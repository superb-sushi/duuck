from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
from .db import Base, engine, get_db
from . import models, schemas
from .ledger import post as ledger_post
# from .risk import viewer_ok, creator_reserve_pct
# Changed the 3 imports below too - Daniel
from engine.cqscore import compute as cq_compute
from engine.fae import allocate
from engine.merkle import merkle_root, merkle_proofs, verify_proof

from .models import Bounty, BountyContribution, BountySubmission, BountyVote, User, BountyFollow
from .schemas import BountyCreate, BountyOut,UserOut, UserCreate
from .ideaModeration import find_similar_idea,moderate_idea

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Duuck API")

@app.post("/user/create", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        weekly_budget=user.weekly_budget,
        kyc_level=user.kyc_level,
        device_attested=user.device_attested,
        risk_tier=user.risk_tier,
        reserve_pct=user.reserve_pct
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# @app.post("/viewer/create")
# def create_viewer(v: schemas.ViewerCreate, db: Session = Depends(get_db)):
#     viewer = models.Viewer(name=v.name, weekly_budget=v.weekly_budget, kyc_level="basic", device_attested=True)
#     db.add(viewer); db.commit(); db.refresh(viewer)
#     return {"id": viewer.id}

# @app.post("/creator/create")
# def create_creator(c: schemas.CreatorCreate, db: Session = Depends(get_db)):
#     cr = models.Creator(handle=c.handle, risk_tier="low", reserve_pct=0.1)
#     db.add(cr); db.commit(); db.refresh(cr)
#     return {"id": cr.id}

@app.post("/video/create")
def create_video(v: schemas.VideoCreate, db: Session = Depends(get_db)):
    vid = models.Video(creator_id=v.creator_id, title=v.title, phash=v.phash, c2pa_status=v.c2pa_status)
    db.add(vid); db.commit(); db.refresh(vid)
    return {"id": vid.id}

@app.post("/session/start")
def session_start(s: schemas.SessionStart, db: Session = Depends(get_db)):
    if not viewer_ok(db, s.viewer_id):
        return {"error": "viewer not allowed"}
    ses = models.Session(viewer_id=s.viewer_id)
    db.add(ses); db.commit(); db.refresh(ses)
    return {"session_id": ses.id}

@app.post("/session/event")
def session_event(ev: schemas.SessionEventIn, db: Session = Depends(get_db)):
    video = db.get(models.Video, ev.video_id)
    cq = cq_compute(ev.seconds_watched, ev.interactions, video)
    e = models.SessionEvent(session_id=ev.session_id, video_id=ev.video_id, seconds_watched=ev.seconds_watched, interactions=ev.interactions, boost_amount=ev.boost_amount, cqscore=cq)
    db.add(e); db.commit()
    if ev.boost_amount and ev.boost_amount > 0:
        db.add(models.Boost(viewer_id=db.get(models.Session, ev.session_id).viewer_id, video_id=ev.video_id, amount=ev.boost_amount))
        db.commit()
    ledger_post(db, account="escrow", debit=ev.boost_amount, credit=0.0, ref_type="boost", ref_id=e.id)
    return {"event_id": e.id, "cqscore": cq}

@app.post("/session/close")
def session_close(session_id: int, platform_match_pool: float = 0.5, db: Session = Depends(get_db)):
    ses = db.get(models.Session, session_id)
    ses.ended_at = datetime.utcnow(); db.commit()
    viewer = db.get(models.Viewer, ses.viewer_id)
    events = db.query(models.SessionEvent).filter_by(session_id=session_id).all()
    evt_payload = []
    for e in events:
        vid = db.get(models.Video, e.video_id)
        evt_payload.append({
            "video_id": vid.id,
            "creator_id": vid.creator_id,
            "cqscore": e.cqscore,
            "boost_amount": e.boost_amount,
        })
    allocs = allocate(evt_payload, viewer.weekly_budget/7.0, platform_match_pool=platform_match_pool, K=25)
    breakdown = []
    total = 0.0
    for a in allocs:
        amount = round(a["amount"], 2)
        total += amount
        resv = creator_reserve_pct(db, a["creator_id"]) * amount
        # ledger: move from escrow to creator payable (with reserve to platform_pool for safety)
        ledger_post(db, account="escrow", debit=0.0, credit=amount, ref_type="allocation", ref_id=session_id)
        ledger_post(db, account="creator_payable", debit=amount - resv, credit=0.0, ref_type="allocation", ref_id=session_id)
        ledger_post(db, account="platform_pool", debit=resv, credit=0.0, ref_type="reserve", ref_id=session_id)
        db.add(models.Allocation(session_id=session_id, creator_id=a["creator_id"], weight=a["weight"], amount=amount, components=a["components"]))
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

# --------- Bounties (Innovation) ---------
@app.post("/bounty/create", response_model=BountyOut)
def create_bounty(bounty: BountyCreate, db: Session = Depends(get_db)):
    # User needs at least a minimum amount to create a bounty
    if bounty.prize_pool < 10.0:
        raise HTTPException(status_code=400, detail="Invalid prize pool. Prize pool must be at least 10.0")
    response = moderate_idea(bounty.description)
    if not response.get("is_safe"):
        raise HTTPException(status_code=400, detail="Inappropriate content detected")
    bounty.description = response.get("summary")
    response = find_similar_idea(bounty.description, [b.description for b in db.query(Bounty).all()])
    if len(response.get("similar")) != 0:
        raise HTTPException(status_code=400, detail="Similar bounty already exists: " + "; ".join(response.get("similar")))
    new_bounty = Bounty(
        creator_id=bounty.creator_id,
        description=bounty.description,
        cutoff_date=datetime.fromisoformat(bounty.cutoff_date),
        judging_start=datetime.fromisoformat(bounty.judging_start),
        judging_end=datetime.fromisoformat(bounty.judging_end),
        prize_pool=bounty.prize_pool,
        is_closed=False
    )
    db.add(new_bounty)
    db.commit()
    db.refresh(new_bounty)
    return {
        "id": new_bounty.id,
        "creator_id": new_bounty.creator_id,
        "description": new_bounty.description,
        "prize_pool": new_bounty.prize_pool,
        "cutoff_date": new_bounty.cutoff_date.isoformat(),
        "judging_start": new_bounty.judging_start.isoformat(),
        "judging_end": new_bounty.judging_end.isoformat(),
        "is_closed": new_bounty.is_closed
    }

@app.post("/bounty/{bounty_id}/contribute")
def contribute_bounty(bounty_id: int, viewer_id: int, amount: float, db: Session = Depends(get_db)):
    # Check if viewer has submitted to this bounty
    user_submission = db.query(BountySubmission).filter_by(bounty_id=bounty_id, creator_id=viewer_id).first()
    if user_submission:
        raise HTTPException(status_code=403, detail="Submitters cannot donate to this bounty.")
    bounty = db.get(Bounty, bounty_id)
    if not bounty or bounty.is_closed:
        raise HTTPException(status_code=404, detail="Bounty not found or closed")
    contribution = BountyContribution(bounty_id=bounty_id, viewer_id=viewer_id, amount=amount)
    bounty.prize_pool += amount
    db.add(contribution)
    db.commit()
    return {"success": True, "new_prize_pool": bounty.prize_pool}

@app.post("/bounty/{bounty_id}/submit")
def submit_bounty(bounty_id: int, creator_id: int, video_id: int, db: Session = Depends(get_db)):
    bounty = db.get(Bounty, bounty_id)
    if not bounty or bounty.is_closed or datetime.utcnow() > bounty.cutoff_date:
        raise HTTPException(status_code=400, detail="Bounty closed or cutoff passed")
    
    # Condition 1: User who created the bounty cannot submit
    if bounty.creator_id == creator_id:
        raise HTTPException(status_code=403, detail="Bounty creator cannot submit a video to their own bounty.")
    
    # Condition 2: User who contributed to the bounty cannot submit
    contribution = db.query(BountyContribution).filter_by(bounty_id=bounty_id, viewer_id=creator_id).first()
    if contribution:
        raise HTTPException(status_code=403, detail="Contributors cannot submit a video to this bounty.")

    submission = BountySubmission(bounty_id=bounty_id, creator_id=creator_id, video_id=video_id)
    db.add(submission)
    db.commit()
    return {"success": True}

@app.post("/bounty/{bounty_id}/vote")
def vote_bounty(bounty_id: int, submission_id: int, viewer_id: int, db: Session = Depends(get_db)):
    bounty = db.get(Bounty, bounty_id)
    # if not bounty or not (bounty.judging_start <= datetime.utcnow() <= bounty.judging_end):
    #     raise HTTPException(status_code=400, detail="Not in judging period")
   
    # Check if viewer has submitted to this bounty
    user_submission = db.query(BountySubmission).filter_by(bounty_id=bounty_id, creator_id=viewer_id).first()
    if user_submission:
        raise HTTPException(status_code=403, detail="Submitters cannot vote on this bounty.")

    # Check if viewer has already voted for this submission
    existing_vote = db.query(BountyVote).filter_by(bounty_id=bounty_id, submission_id=submission_id, viewer_id=viewer_id).first()
    if existing_vote:
        raise HTTPException(status_code=400, detail="User has already voted for this submission.")

    vote = BountyVote(bounty_id=bounty_id, submission_id=submission_id, viewer_id=viewer_id)
    db.add(vote)
    db.commit()
    return {"success": True}

@app.post("/bounty/{bounty_id}/distribute")
def distribute_bounty(bounty_id: int, db: Session = Depends(get_db)):
    bounty = db.get(Bounty, bounty_id)
    if not bounty or datetime.utcnow() < bounty.judging_end or bounty.is_closed:
        raise HTTPException(status_code=400, detail="Judging not finished or bounty already closed")
    # Count votes per submission
    votes = db.query(BountyVote.submission_id).filter(BountyVote.bounty_id == bounty_id).all()
    from collections import Counter
    vote_counts = Counter([v[0] for v in votes])
    top_submissions = [sid for sid, _ in vote_counts.most_common(3)]
    # Split prize pool: 50%, 30%, 20%
    # TODO Kaiwen's FAE
    splits = [0.5, 0.3, 0.2]
    for i, sid in enumerate(top_submissions):
        submission = db.get(BountySubmission, sid)
        if submission:
            # Here you would credit the creator (e.g., via ledger)
            pass
    bounty.is_closed = True
    db.commit()
    return {"success": True, "top_submissions": top_submissions}

@app.get("/bounty/{bounty_id}", response_model=BountyOut)
def view_bounty(bounty_id: int, db: Session = Depends(get_db)):
    bounty = db.get(Bounty, bounty_id)
    if not bounty:
        raise HTTPException(status_code=404, detail="Bounty not found")
    return {
        "id": bounty.id,
        "description": bounty.description,
        "prize_pool": bounty.prize_pool,
        "cutoff_date": bounty.cutoff_date.isoformat(),
        "judging_start": bounty.judging_start.isoformat(),
        "judging_end": bounty.judging_end.isoformat(),
        "is_closed": bounty.is_closed
    }

@app.get("/bounty/{bounty_id}/winners")
def view_bounty_winners(bounty_id: int, db: Session = Depends(get_db)):
    bounty = db.get(Bounty, bounty_id)
    if not bounty or not bounty.is_closed:
        raise HTTPException(status_code=400, detail="Bounty not finished or winners not decided yet")
    # Count votes per submission
    votes = db.query(BountyVote.submission_id).filter(BountyVote.bounty_id == bounty_id).all()
    from collections import Counter
    vote_counts = Counter([v[0] for v in votes])
    top_submissions = [sid for sid, _ in vote_counts.most_common(3)]
    splits = [0.5, 0.3, 0.2]
    winners = []
    for i, sid in enumerate(top_submissions):
        submission = db.get(BountySubmission, sid)
        if submission:
            prize = round(bounty.prize_pool * splits[i], 2) if i < len(splits) else 0.0
            winners.append({
                "submission_id": sid,
                "creator_id": submission.creator_id,
                "video_id": submission.video_id,
                "prize": prize
            })
    return {
        "bounty_id": bounty_id,
        "winners": winners
    }

@app.post("/bounty/{bounty_id}/follow")
def follow_bounty(bounty_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to allow a user to follow a bounty.
    """
    bounty = db.get(models.Bounty, bounty_id)
    if not bounty:
        raise HTTPException(status_code=404, detail="Bounty not found")

    # Check if the user is already following the bounty
    existing_follow = db.query(models.BountyFollow).filter_by(bounty_id=bounty_id, user_id=user_id).first()
    if existing_follow:
        raise HTTPException(status_code=400, detail="User already following this bounty")

    follow = models.BountyFollow(bounty_id=bounty_id, user_id=user_id)
    db.add(follow)
    db.commit()
    return {"message": "Bounty followed successfully"}
