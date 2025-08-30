import hashlib
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from .db import Base, engine, get_db
from . import models, schemas
from .ledger import post as ledger_post
from .risk import viewer_ok, creator_reserve_pct
from engine.fae import allocate
from engine.merkle import merkle_root, merkle_proofs, verify_proof
import joblib
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

# Load the fraud detection model
fraud_model = joblib.load("models/fraud_detection_model.pkl")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to load initial data and clean up resources.
    """
    with Session(engine) as db:
        try:
            # Example: Add initial viewers
            if not db.query(models.Viewer).first():
                viewers = [
                    models.Viewer(handle="viewer1", kyc_level="basic", device_attested=True),
                    models.Viewer(handle="viewer2", kyc_level="basic", device_attested=True),
                ]
                db.add_all(viewers)

            # Example: Add initial creators
            if not db.query(models.Creator).first():
                creators = [
                    models.Creator(handle="creator1", risk_tier="low", reserve_pct=0.1),
                    models.Creator(handle="creator2", risk_tier="medium", reserve_pct=0.2),
                ]
                db.add_all(creators)

            # Example: Add initial videos
            if not db.query(models.Video).first():
                videos = [
                    models.Video(creator_handle="creator1", title="Video 1", phash="hash1"),
                    models.Video(creator_handle="creator2", title="Video 2", phash="hash2"),
                ]
                db.add_all(videos)

            # Example: Add initial bounties
            if not db.query(models.Bounty).first():
                bounties = [
                    models.Bounty(title="Bounty 1", description="Solve problem 1", user_creator_handle="viewer1", total_donations=50),
                    models.Bounty(title="Bounty 2", description="Solve problem 2", user_creator_handle="viewer2", total_donations=100),
                ]
                db.add_all(bounties)

            # Example: Add initial sessions and session events
            if not db.query(models.Session).first():
                session = models.Session(viewer_handle="viewer1")
                db.add(session)
                db.commit()
                db.refresh(session)

                session_event = models.SessionEvent(
                    session_id=session.id,
                    video_id=1,
                    viewer_handle="viewer1",
                    seconds_watched=120,
                    interactions=5,
                    donation_amount=10,
                    target=0,
                    status="approved"
                )
                db.add(session_event)

            db.commit()
        except SQLAlchemyError as e:
            print(f"Error during startup data initialization: {e}")

    yield

    # Cleanup logic
    with Session(engine) as db:
        try:
            # Example cleanup: Remove test data (if needed)
            db.query(models.SessionEvent).delete()
            db.query(models.Session).delete()
            db.query(models.Bounty).delete()
            db.query(models.Video).delete()
            db.query(models.Creator).delete()
            db.query(models.Viewer).delete()
            db.commit()
        except SQLAlchemyError as e:
            print(f"Error during cleanup: {e}")

app = FastAPI(title="Duuck API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/viewer/create")
def create_viewer(v: schemas.ViewerCreate, db: Session = Depends(get_db)):
    viewer = models.Viewer(handle=v.handle, kyc_level="basic", device_attested=True)
    db.add(viewer); db.commit(); db.refresh(viewer)
    return {"status": "success"}

@app.post("/creator/create")
def create_creator(c: schemas.CreatorCreate, db: Session = Depends(get_db)):
    cr = models.Creator(handle=c.handle, risk_tier="low", reserve_pct=0.1)
    db.add(cr); db.commit(); db.refresh(cr)
    return {"status": "success"}

@app.post("/video/create")
def create_video(v: schemas.VideoCreate, db: Session = Depends(get_db)):
    vid = models.Video(creator_handle=v.creator_handle, title=v.title, phash=v.phash, c2pa_status=v.c2pa_status)
    db.add(vid); db.commit(); db.refresh(vid)
    return {"status": "success"}

@app.post("/session/start")
def session_start(s: schemas.SessionStart, db: Session = Depends(get_db)):
    if not viewer_ok(db, s.viewer_handle):
        return {"error": "viewer not allowed"}
    ses = models.Session(viewer_handle=s.viewer_handle)
    db.add(ses); db.commit(); db.refresh(ses)
    return {"session_id": ses.id}

@app.post("/session/event")
def session_event(ev: schemas.SessionEventIn, db: Session = Depends(get_db)):
    video = db.get(models.Video, ev.video_id)
    e = models.SessionEvent(
        session_id=ev.session_id,
        video_id=ev.video_id,
        seconds_watched=ev.seconds_watched,
        interactions=ev.interactions,
        donation_amount=ev.donation_amount,
        status="pending"
    )
    db.add(e)
    db.commit()

    # Use the fraud detection model to check for suspicious donations
    features = [
        ev.seconds_watched,
        ev.interactions,
        db.get(models.Viewer, db.get(models.Session, ev.session_id).viewer_handle).total_interactions,
        ev.donation_amount,
        db.get(models.Viewer, db.get(models.Session, ev.session_id).viewer_handle).total_donations,
        db.get(models.Viewer, db.get(models.Session, ev.session_id).viewer_handle).time_spent_on_app,
        db.get(models.Viewer, db.get(models.Session, ev.session_id).viewer_handle).account_age_days
    ]
    is_suspicious = fraud_model.predict([features])[0]  # Assuming the model returns a boolean

    if is_suspicious:
        e.status = "under_review"
        db.commit()
        return {"event_id": e.id, "status": "under_review"}

    ledger_post(db, account="escrow", debit=ev.donation_amount, credit=0.0, ref_type="donation", ref_id=e.id)
    return {"event_id": e.id, "status": "approved"}

@app.post("/session/close")
def session_close(session_id: int, platform_match_pool: float = 0.5, db: Session = Depends(get_db)):
    ses = db.get(models.Session, session_id)
    ses.ended_at = datetime.utcnow(); db.commit()
    viewer = db.get(models.Viewer, ses.viewer_handle)
    events = db.query(models.SessionEvent).filter_by(session_id=session_id).all()
    evt_payload = []
    for e in events:
        vid = db.get(models.Video, e.video_id)
        evt_payload.append({
            "video_id": vid.id,
            "creator_id": vid.creator_id,
            "donation_amount": e.donation_amount,
        })
    allocs = allocate(evt_payload, platform_match_pool=platform_match_pool, K=25)
    breakdown = []
    total = 0.0
    for a in allocs:
        amount = round(a["amount"], 2)
        total += amount
        resv = creator_reserve_pct(db, a["creator_handle"]) * amount
        # ledger: move from escrow to creator payable (with reserve to platform_pool for safety)
        ledger_post(db, account="escrow", debit=0.0, credit=amount, ref_type="allocation", ref_id=session_id)
        ledger_post(db, account="creator_payable", debit=amount - resv, credit=0.0, ref_type="allocation", ref_id=session_id)
        ledger_post(db, account="platform_pool", debit=resv, credit=0.0, ref_type="reserve", ref_id=session_id)
        db.add(models.Allocation(session_id=session_id, creator_handle=a["creator_handle"], weight=a["weight"], amount=amount, components=a["components"]))
        breakdown.append({
            "creator_id": a["creator_id"],
            "video_id": a["video_id"],
            "amount": amount,
            "weight": round(a["weight"], 4),
            "explain": a["components"],
        })
    db.commit()
    return {"session_id": session_id, "breakdown": breakdown, "total_spent": round(total, 2)}

# --------- APR + Merkle‑FairSplit (Innovation) ---------

@app.post("/apr/commit")
def apr_commit(apr: schemas.APRIn, db: Session = Depends(get_db)):
    payload = f"{apr.session_id}|{apr.video_id}|{apr.seconds_watched}|{apr.nonce}".encode()
    digest = hashlib.sha256(payload).hexdigest()
    db.add(models.APRCommitment(window=apr.window, commitment=digest, meta={"session_id": apr.session_id, "video_id": apr.video_id}))
    db.commit()
    return {"commitment": digest}

@app.post("/apr/publish_root")
def apr_publish_root(window: str, db: Session = Depends(get_db)):
    commits = db.query(models.APRCommitment).filter_by(window=window).all()
    leaves = [c.commitment for c in commits]
    root = merkle_root(leaves)
    mr = db.query(models.MerkleRoot).filter_by(window=window).first()
    if not mr:
        mr = models.MerkleRoot(window=window, root=root, leaves_count=len(leaves))
        db.add(mr)
    else:
        mr.root = root; mr.leaves_count = len(leaves)
    db.commit()
    return {"window": window, "root": root, "count": len(leaves)}

@app.get("/apr/proofs")
def apr_proofs(window: str, db: Session = Depends(get_db)):
    commits = db.query(models.APRCommitment).filter_by(window=window).all()
    leaves = [c.commitment for c in commits]
    proofs = merkle_proofs(leaves)
    out = []
    for i, c in enumerate(commits):
        out.append({"commitment": c.commitment, "proof": proofs[i]})
    return {"window": window, "root": merkle_root(leaves), "proofs": out}

@app.post("/apr/verify")
def apr_verify(window: str, commitment: str, proof: list, db: Session = Depends(get_db)):
    mr = db.query(models.MerkleRoot).filter_by(window=window).first()
    if not mr:
        return {"ok": False, "error": "no root"}
    ok = verify_proof(commitment, proof, mr.root)
    return {"ok": ok, "root": mr.root}

@app.get("/bounty")
def get_top_bounties(db: Session = Depends(get_db)):
    """
    Endpoint to fetch top bounty ideas.
    """
    bounties = db.query(models.Bounty).all()  # Default sorting by donations assumed
    return bounties

@app.post("/bounty/{bounty_id}/follow")
def follow_bounty(bounty_id: int, user_handle: str, db: Session = Depends(get_db)):
    """
    Endpoint to allow a user to follow a bounty.
    """
    bounty = db.get(models.Bounty, bounty_id)
    if not bounty:
        raise HTTPException(status_code=404, detail="Bounty not found")

    # Check if the user is already following the bounty
    existing_follow = db.query(models.BountyFollow).filter_by(bounty_id=bounty_id, user_handle=user_handle).first()
    if existing_follow:
        raise HTTPException(status_code=400, detail="User already following this bounty")

    follow = models.BountyFollow(bounty_id=bounty_id, user_handle=user_handle)
    db.add(follow)
    db.commit()
    return {"message": "Bounty followed successfully"}

@app.post("/bounty/create")
def create_bounty(b: schemas.BountyCreate, db: Session = Depends(get_db)):
    """
    Endpoint to create a new bounty with an initial donation.
    """
    if b.initial_donation < 10:  # Example minimum donation validation
        raise HTTPException(status_code=400, detail="Minimum donation is 10 units")

    bounty = models.Bounty(title=b.title, description=b.description, creator_handle=b.creator_handle, total_donations=b.initial_donation)
    db.add(bounty)
    db.commit()
    db.refresh(bounty)

    # Record the initial donation
    donation = models.Donation(bounty_id=bounty.id, user_handle=b.creator_handle, amount=b.initial_donation)
    db.add(donation)
    db.commit()

    return {"id": bounty.id, "message": "Bounty created successfully"}

@app.get("/bounty/similar")
def get_similar_bounties(title: str, tags: list[str], db: Session = Depends(get_db)):
    """
    Endpoint to suggest similar existing bounty ideas based on title and tags.
    """
    # Example fuzzy search logic (to be replaced with actual implementation)
    similar_bounties = db.query(models.Bounty).filter(models.Bounty.title.contains(title)).all()
    return similar_bounties

@app.post("/video/submit")
def submit_video(v: schemas.VideoSubmission, db: Session = Depends(get_db)):
    """
    Endpoint to tag a video submission to a bounty.
    """
    bounty = db.get(models.Bounty, v.bounty_id)
    if not bounty:
        raise HTTPException(status_code=404, detail="Bounty not found")

    if bounty.status != "open":
        raise HTTPException(status_code=400, detail="Bounty is not open for submissions")

    # Add the creator to the bounty's competing creators if not already added
    creator = db.get(models.Creator, v.creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    if creator not in bounty.competing_creators:
        bounty.competing_creators.append(creator)

    video = models.Video(creator_handle=v.creator_handle, title=v.title, bounty_id=v.bounty_id)
    db.add(video)
    db.commit()
    db.refresh(video)
    return {"id": video.id, "message": "Video submitted successfully"}

@app.post("/bounty/{bounty_id}/vote")
def vote_for_submission(bounty_id: int, v: schemas.VoteCreate, db: Session = Depends(get_db)):
    """
    Endpoint to cast a vote for a submission.
    """
    bounty = db.get(models.Bounty, bounty_id)
    if not bounty:
        raise HTTPException(status_code=404, detail="Bounty not found")

    if bounty.status != "voting":
        raise HTTPException(status_code=400, detail="Voting is not active for this bounty")

    # Prevent multiple votes by the same user unless allowed by stretch goals
    existing_vote = db.query(models.Vote).filter_by(bounty_id=bounty_id, user_handle=v.user_handle).first()
    if existing_vote:
        raise HTTPException(status_code=400, detail="User has already voted for this bounty")

    vote = models.Vote(bounty_id=bounty_id, user_handle=v.user_handle, video_id=v.video_id)
    db.add(vote)
    db.commit()
    return {"message": "Vote cast successfully"}

@app.get("/bounty/{bounty_id}/winners")
def reveal_winners(bounty_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to reveal the top 3 winning videos after the bounty ends.
    """
    bounty = db.get(models.Bounty, bounty_id)
    if not bounty:
        raise HTTPException(status_code=404, detail="Bounty not found")

    if bounty.status != "ended":
        raise HTTPException(status_code=400, detail="Bounty has not ended yet")

    # Query top 3 videos based on votes
    winners = (
        db.query(models.Video, db.func.count(models.Vote.id).label("vote_count"))
        .join(models.Vote, models.Video.id == models.Vote.video_id)
        .filter(models.Vote.bounty_id == bounty_id)
        .group_by(models.Video.id)
        .order_by(db.func.count(models.Vote.id).desc())
        .limit(3)
        .all()
    )

    return {"bounty_id": bounty_id, "winners": [{"video_id": w.Video.id, "vote_count": w.vote_count} for w in winners]}

@app.get("/admin/suspicious-donations")
def get_suspicious_donations(db: Session = Depends(get_db)):
    """
    Fetch all donations marked as under review.
    """
    suspicious_events = db.query(models.SessionEvent).filter_by(status="under_review").all()
    return suspicious_events

@app.get("/admin/viewer/{viewer_handle}")
def get_viewer_profile(viewer_handle: str, db: Session = Depends(get_db)):
    """
    Fetch viewer profile and donation history.
    """
    viewer = db.get(models.Viewer, viewer_handle)
    donations = db.query(models.SessionEvent).filter_by(viewer_handle=viewer_handle).all()
    return {"viewer": viewer, "donations": donations}

@app.get("/admin/creator/{creator_handle}")
def get_creator_profile(creator_handle: str, db: Session = Depends(get_db)):
    """
    Fetch creator profile and associated bounties.
    """
    creator = db.get(models.Creator, creator_handle)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    bounties = db.query(models.Bounty).filter(models.Bounty.competing_creators.contains(creator)).all()
    return {"creator": creator, "bounties": bounties}

@app.post("/admin/donation/{donation_id}/review")
def review_donation(donation_id: int, action: str, db: Session = Depends(get_db)):
    """
    Approve or reject a suspicious donation.
    """
    donation = db.get(models.SessionEvent, donation_id)
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")

    if action not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    donation.status = "approved" if action == "approve" else "rejected"
    db.commit()
    return {"message": f"Donation {action}ed successfully"}
