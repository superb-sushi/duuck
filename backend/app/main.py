import joblib
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from .db import Base, engine, get_db
from . import models, schemas
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from .models import Bounty, BountyContribution, BountySubmission, BountyVote, User, BountyFollow
from .schemas import BountyCreate, BountyOut, UserCreate
from .ideaModeration import find_similar_idea,moderate_idea

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
            # Example: Add initial users
            if not db.query(models.User).first():
                users = [
                    models.User(handle="user1", wallet=100.0, total_donations=10.0, time_spent_on_app=120, account_age_days=365, total_interactions=50),
                    models.User(handle="user2", wallet=200.0, total_donations=20.0, time_spent_on_app=240, account_age_days=730, total_interactions=100),
                    models.User(handle="user3", wallet=300.0, total_donations=30.0, time_spent_on_app=360, account_age_days=1095, total_interactions=150),
                    models.User(handle="user4", wallet=400.0, total_donations=40.0, time_spent_on_app=480, account_age_days=1460, total_interactions=200),
                    models.User(handle="user5", wallet=500.0, total_donations=50.0, time_spent_on_app=600, account_age_days=1825, total_interactions=250),
                    models.User(handle="user6", wallet=600.0, total_donations=60.0, time_spent_on_app=720, account_age_days=2190, total_interactions=300),
                ]
                db.add_all(users)

            # Example: Add initial videos
            if not db.query(models.Video).first():
                videos = [
                    models.Video(creator_handle="user1", title="Video 1", phash="hash1"),
                    models.Video(creator_handle="user2", title="Video 2", phash="hash2"),
                    models.Video(creator_handle="user3", title="Video 3", phash="hash3"),
                    models.Video(creator_handle="user4", title="Video 4", phash="hash4"),
                    models.Video(creator_handle="user1", title="Video 5", phash="hash5"),
                ]
                db.add_all(videos)

            # Example: Add initial bounties
            if not db.query(models.Bounty).first():
                bounties = [
                    models.Bounty(description="Solve problem 1", creator_handle="user5", prize_pool=50.0, cutoff_date=datetime(2025, 8, 21), judging_start=datetime(2025, 8, 22), judging_end=datetime(2025, 8, 29), is_closed=True),
                    models.Bounty(description="Solve problem 2", creator_handle="user6", prize_pool=100.0, cutoff_date=datetime(2025, 9, 2), judging_start=datetime(2025, 9, 3), judging_end=datetime(2025, 9, 7), is_closed=False),
                ]
                db.add_all(bounties)

            db.commit()
        except SQLAlchemyError as e:
            print(f"Error during startup data initialization: {e}")

    yield

    # Cleanup logic
    with Session(engine) as db:
        try:
            # Example cleanup: Remove test data (if needed)
            db.query(models.Bounty).delete()
            db.query(models.Video).delete()
            db.query(models.User).delete()
            db.commit()
        except SQLAlchemyError as e:
            print(f"Error during cleanup: {e}")

app = FastAPI(title="Duuck API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000/main.lynx.bundle"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/user/create")
def create_user(user_handle: str, db: Session = Depends(get_db)):
    new_user = User(
        user_handle=user_handle,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/video/create")
def create_video(v: schemas.VideoCreate, db: Session = Depends(get_db)):
    vid = models.Video(creator_id=v.creator_id, title=v.title, phash=v.phash, c2pa_status=v.c2pa_status)
    db.add(vid); db.commit(); db.refresh(vid)
    return {"id": vid.id}


@app.post("/session/start")
def session_start(s: schemas.SessionStart, db: Session = Depends(get_db)):
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
    ses.ended_at = datetime.now(); db.commit()
    return {"session_id": session_id}

@app.get("/bounty")
def get_top_bounties(db: Session = Depends(get_db)):
    """
    Endpoint to fetch top bounty ideas.
    """
    bounties = db.query(models.Bounty).all()  # Default sorting by donations assumed
    return bounties

@app.post("/bounty/create", response_model=BountyOut)
def create_bounty(bounty: BountyCreate, db: Session = Depends(get_db)):
    # Get the user who is creating the bounty
    user = db.get(User, bounty.creator_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if bounty.prize_pool < 10.0:
        raise HTTPException(status_code=400, detail="Invalid prize pool. Prize pool must be at least 10.0")
    if user.weekly_budget < bounty.prize_pool:
        raise HTTPException(status_code=400, detail="Insufficient weekly budget to fund prize pool")
    response = moderate_idea(bounty.description)
    if not response.get("is_safe"):
        raise HTTPException(status_code=400, detail="Inappropriate content detected")
    bounty.description = response.get("summary")
    response = find_similar_idea(bounty.description, [b.description for b in db.query(Bounty).all()])
    if len(response.get("similar")) != 0:
        raise HTTPException(status_code=400, detail="Similar bounty already exists: " + "; ".join(response.get("similar")))
    # Deduct prize pool from user's weekly_budget
    user.weekly_budget -= bounty.prize_pool
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
    viewer = db.get(User, viewer_id)
    if not viewer:
        raise HTTPException(status_code=404, detail="User not found")
    if viewer.weekly_budget < amount:
        raise HTTPException(status_code=400, detail="Insufficient weekly budget to contribute")
    # Deduct contribution from viewer's weekly_budget
    viewer.weekly_budget -= amount
    contribution = BountyContribution(bounty_id=bounty_id, viewer_id=viewer_id, amount=amount)
    bounty.prize_pool += amount
    db.add(contribution)
    db.commit()
    return {"success": True, "new_prize_pool": bounty.prize_pool}

@app.post("/bounty/{bounty_id}/submit")
def submit_bounty(bounty_id: int, creator_id: int, video_id: int, db: Session = Depends(get_db)):
    bounty = db.get(Bounty, bounty_id)
    if not bounty or bounty.is_closed or datetime.now() > bounty.cutoff_date:
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
    # if not bounty or not (bounty.judging_start <= datetime.now() <= bounty.judging_end):
    #     raise HTTPException(status_code=400, detail="Not in judging period")
   
    # Check if viewer has submitted to this bounty
    user_submission = db.query(BountySubmission).filter_by(bounty_id=bounty_id, creator_id=viewer_id).first()
    if user_submission:
        raise HTTPException(status_code=403, detail="Submitters cannot vote on this bounty.")

    # Check if viewer has already voted for any submission in this bounty
    any_vote = db.query(BountyVote).filter_by(bounty_id=bounty_id, viewer_id=viewer_id).first()
    if any_vote:
        raise HTTPException(status_code=400, detail="User has already voted for a submission in this bounty.")

    vote = BountyVote(bounty_id=bounty_id, submission_id=submission_id, viewer_id=viewer_id)
    db.add(vote)
    db.commit()
    return {"success": True}

@app.post("/bounty/{bounty_id}/distribute")
def distribute_bounty(bounty_id: int, db: Session = Depends(get_db)):
    bounty = db.get(Bounty, bounty_id)
    if not bounty or datetime.now() < bounty.judging_end or bounty.is_closed:
        raise HTTPException(status_code=400, detail="Judging not finished or bounty already closed")
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
            # Add prize to winner's weekly_budget
            winner = db.get(User, submission.creator_id)
            if winner:
                winner.weekly_budget += prize
            winners.append({
                "submission_id": sid,
                "creator_id": submission.creator_id,
                "video_id": submission.video_id,
                "prize": prize
            })
    bounty.is_closed = True
    db.commit()
    return {
        "success": True,
        "winners": winners
    }

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
