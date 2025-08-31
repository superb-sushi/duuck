from fastapi import Query
import joblib
import os
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


# Delete and recreate the database file at startup
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "duuck.db")
if os.path.exists(db_path):
    os.remove(db_path)
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
                    # Bounty creators (do not create videos)
                    models.User(handle="PixelPilot", wallet=153.0, total_donations=12.5, time_spent_on_app=98, account_age_days=120, total_interactions=67),
                    models.User(handle="FrameFrenzy", wallet=95.0, total_donations=22.0, time_spent_on_app=80, account_age_days=45, total_interactions=101),
                    models.User(handle="ClipCrafter", wallet=480.0, total_donations=33.0, time_spent_on_app=175, account_age_days=160, total_interactions=278),
                    models.User(handle="MontageMaven", wallet=510.0, total_donations=61.0, time_spent_on_app=140, account_age_days=170, total_interactions=175),
                    models.User(handle="VFXValkyrie", wallet=777.0, total_donations=95.0, time_spent_on_app=180, account_age_days=180, total_interactions=388),
                    models.User(handle="ViralVisionary", wallet=410.0, total_donations=55.0, time_spent_on_app=150, account_age_days=180, total_interactions=189),
                    models.User(handle="RenderRogue", wallet=199.0, total_donations=29.5, time_spent_on_app=50, account_age_days=20, total_interactions=84),
                    # Video creators (no more than 2 videos each)
                    models.User(handle="EditEagle", wallet=620.0, total_donations=47.0, time_spent_on_app=60, account_age_days=30, total_interactions=222),
                    models.User(handle="JumpCutJedi", wallet=305.0, total_donations=19.0, time_spent_on_app=90, account_age_days=80, total_interactions=110),
                    models.User(handle="CodeCrusader", wallet=287.5, total_donations=8.0, time_spent_on_app=110, account_age_days=90, total_interactions=143),
                    models.User(handle="MontageMaster", wallet=210.0, total_donations=15.0, time_spent_on_app=70, account_age_days=60, total_interactions=99),
                    models.User(handle="VFXVirtuoso", wallet=330.0, total_donations=25.0, time_spent_on_app=120, account_age_days=100, total_interactions=150),
                    models.User(handle="PetPrankster", wallet=180.0, total_donations=10.0, time_spent_on_app=40, account_age_days=20, total_interactions=55),
                    models.User(handle="SoundSensei", wallet=260.0, total_donations=18.0, time_spent_on_app=80, account_age_days=70, total_interactions=88),
                    models.User(handle="MaskMagician", wallet=145.0, total_donations=7.0, time_spent_on_app=35, account_age_days=15, total_interactions=40),
                    models.User(handle="TransitionTiger", wallet=175.0, total_donations=12.0, time_spent_on_app=60, account_age_days=25, total_interactions=60),
                ]
                db.add_all(users)
                db.commit()

            if not db.query(models.Video).first():
                videos = [
                    models.Video(creator_handle="EditEagle", title="Speedrun Editing: 60s Transformation", phash="hash5", length=60, views=120, votes=15, likes=40),
                    models.Video(creator_handle="EditEagle", title="30 Second Color Grading Tip", phash="hash13", length=30, views=80, votes=10, likes=25),
                    models.Video(creator_handle="JumpCutJedi", title="Jump Cut Masterclass", phash="hash7", length=54, views=200, votes=22, likes=60),
                    models.Video(creator_handle="JumpCutJedi", title="Whip Pan Transition Demo", phash="hash15", length=25, views=95, votes=8, likes=30),
                    models.Video(creator_handle="CodeCrusader", title="Python Animation Challenge", phash="hash2", length=92, views=150, votes=18, likes=50),
                    models.Video(creator_handle="CodeCrusader", title="Keyboard Macro Setup Fast", phash="hash18", length=44, views=60, votes=5, likes=20),
                    models.Video(creator_handle="MontageMaster", title="Travel Vlog: 10 Countries in 5 Minutes", phash="hash8", length=120, views=300, votes=30, likes=100),
                    models.Video(creator_handle="MontageMaster", title="Mountain Hike Timelapse", phash="hash19", length=80, views=110, votes=12, likes=35),
                    models.Video(creator_handle="VFXVirtuoso", title="VFX Lightning Tutorial", phash="hash10", length=66, views=170, votes=20, likes=55),
                    models.Video(creator_handle="VFXVirtuoso", title="Particle Explosion Demo", phash="hash20", length=70, views=90, votes=7, likes=28),
                    models.Video(creator_handle="PetPrankster", title="Best Cat Fails 2025", phash="hash4", length=48, views=250, votes=35, likes=120),
                    models.Video(creator_handle="PetPrankster", title="Snappy Pet Intro Sequence", phash="hash17", length=36, views=60, votes=6, likes=18),
                    models.Video(creator_handle="SoundSensei", title="Sound Design Basics in 50s", phash="hash16", length=50, views=130, votes=14, likes=45),
                    models.Video(creator_handle="SoundSensei", title="Quick Foley Demo", phash="hash21", length=40, views=55, votes=4, likes=15),
                    models.Video(creator_handle="MaskMagician", title="Quick Masking Trick", phash="hash14", length=28, views=40, votes=3, likes=10),
                    models.Video(creator_handle="MaskMagician", title="Layer Reveal Animation", phash="hash22", length=32, views=35, votes=2, likes=8),
                    models.Video(creator_handle="TransitionTiger", title="Whip Pan Transition Demo", phash="hash15", length=25, views=75, votes=9, likes=22),
                    models.Video(creator_handle="TransitionTiger", title="Spin Cut Example", phash="hash23", length=29, views=50, votes=5, likes=14),
                ]
                db.add_all(videos)
                db.commit()

            if not db.query(models.Bounty).first():
                bounties = [
                    models.Bounty(description="Create a montage of drone footage with at least 3 different locations.", creator_handle="PixelPilot", prize_pool=75.0, cutoff_date=datetime(2025, 9, 10), judging_start=datetime(2025, 9, 11), judging_end=datetime(2025, 9, 18), is_closed=False, following=False),
                    models.Bounty(description="Edit a video showing a creative use of slow motion in sports.", creator_handle="FrameFrenzy", prize_pool=60.0, cutoff_date=datetime(2025, 9, 15), judging_start=datetime(2025, 9, 16), judging_end=datetime(2025, 9, 22), is_closed=False, following=False),
                    models.Bounty(description="Produce a tutorial for beginners on setting up a home video studio.", creator_handle="ClipCrafter", prize_pool=80.0, cutoff_date=datetime(2025, 9, 20), judging_start=datetime(2025, 9, 21), judging_end=datetime(2025, 9, 28), is_closed=False, following=False),
                    models.Bounty(description="Make a travel vlog covering at least 5 countries in under 5 minutes.", creator_handle="MontageMaven", prize_pool=120.0, cutoff_date=datetime(2025, 9, 25), judging_start=datetime(2025, 9, 26), judging_end=datetime(2025, 10, 2), is_closed=False, following=False),
                    models.Bounty(description="Show off your best VFX lightning effect in a short clip.", creator_handle="VFXValkyrie", prize_pool=90.0, cutoff_date=datetime(2025, 9, 30), judging_start=datetime(2025, 10, 1), judging_end=datetime(2025, 10, 7), is_closed=False, following=False),
                    models.Bounty(description="Create a compilation of funny pet fails with creative editing.", creator_handle="ViralVisionary", prize_pool=55.0, cutoff_date=datetime(2025, 9, 12), judging_start=datetime(2025, 9, 13), judging_end=datetime(2025, 9, 19), is_closed=False, following=False),
                    models.Bounty(description="Explain a technical concept visually using animation or graphics.", creator_handle="RenderRogue", prize_pool=70.0, cutoff_date=datetime(2025, 9, 18), judging_start=datetime(2025, 9, 19), judging_end=datetime(2025, 9, 25), is_closed=False, following=False),
                ]
                db.add_all(bounties)
                db.commit()

                # Re-query committed objects for correct IDs
                users = db.query(models.User).all()
                videos = db.query(models.Video).all()
                bounties = db.query(models.Bounty).all()
                video_map = {v.title: v for v in videos}
                bounty_map = {b.description: b for b in bounties}
                user_map = {u.handle: u for u in users}
                submissions = [
                    # Drone montage bounty (using existing videos)
                    models.BountySubmission(bounty_id=bounty_map["Create a montage of drone footage with at least 3 different locations."].id, creator_handle=user_map["EditEagle"].handle, video_id=video_map["Speedrun Editing: 60s Transformation"].id),
                    models.BountySubmission(bounty_id=bounty_map["Create a montage of drone footage with at least 3 different locations."].id, creator_handle=user_map["MontageMaster"].handle, video_id=video_map["Travel Vlog: 10 Countries in 5 Minutes"].id),
                    # Slow motion sports bounty
                    models.BountySubmission(bounty_id=bounty_map["Edit a video showing a creative use of slow motion in sports."].id, creator_handle=user_map["JumpCutJedi"].handle, video_id=video_map["Jump Cut Masterclass"].id),
                    models.BountySubmission(bounty_id=bounty_map["Edit a video showing a creative use of slow motion in sports."].id, creator_handle=user_map["TransitionTiger"].handle, video_id=video_map["Whip Pan Transition Demo"].id),
                    # Home studio bounty
                    models.BountySubmission(bounty_id=bounty_map["Produce a tutorial for beginners on setting up a home video studio."].id, creator_handle=user_map["CodeCrusader"].handle, video_id=video_map["Python Animation Challenge"].id),
                    models.BountySubmission(bounty_id=bounty_map["Produce a tutorial for beginners on setting up a home video studio."].id, creator_handle=user_map["SoundSensei"].handle, video_id=video_map["Sound Design Basics in 50s"].id),
                    # Travel vlog bounty
                    models.BountySubmission(bounty_id=bounty_map["Make a travel vlog covering at least 5 countries in under 5 minutes."].id, creator_handle=user_map["MontageMaster"].handle, video_id=video_map["Mountain Hike Timelapse"].id),
                    # VFX lightning bounty
                    models.BountySubmission(bounty_id=bounty_map["Show off your best VFX lightning effect in a short clip."].id, creator_handle=user_map["VFXVirtuoso"].handle, video_id=video_map["VFX Lightning Tutorial"].id),
                    models.BountySubmission(bounty_id=bounty_map["Show off your best VFX lightning effect in a short clip."].id, creator_handle=user_map["VFXVirtuoso"].handle, video_id=video_map["Particle Explosion Demo"].id),
                    # Pet fails bounty
                    models.BountySubmission(bounty_id=bounty_map["Create a compilation of funny pet fails with creative editing."].id, creator_handle=user_map["PetPrankster"].handle, video_id=video_map["Best Cat Fails 2025"].id),
                    models.BountySubmission(bounty_id=bounty_map["Create a compilation of funny pet fails with creative editing."].id, creator_handle=user_map["PetPrankster"].handle, video_id=video_map["Snappy Pet Intro Sequence"].id),
                    # Technical animation bounty
                    models.BountySubmission(bounty_id=bounty_map["Explain a technical concept visually using animation or graphics."].id, creator_handle=user_map["CodeCrusader"].handle, video_id=video_map["Keyboard Macro Setup Fast"].id),
                    models.BountySubmission(bounty_id=bounty_map["Explain a technical concept visually using animation or graphics."].id, creator_handle=user_map["MaskMagician"].handle, video_id=video_map["Quick Masking Trick"].id),
                ]
                db.add_all(submissions)
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

@app.get("/user/getdefault")
def get_default_user(db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(handle="PixelPilot").first()
    if not user:
        raise HTTPException(status_code=404, detail="Default user PixelPilot not found")
    return {
        "handle": user.handle,
        "wallet": user.wallet,
        "total_donations": user.total_donations,
        "time_spent_on_app": user.time_spent_on_app,
        "account_age_days": user.account_age_days,
        "total_interactions": user.total_interactions
    }

@app.post("/video/create")
def create_video(v: schemas.VideoCreate, db: Session = Depends(get_db)):
    vid = models.Video(creator_handle=v.creator_handle, title=v.title, phash=v.phash, length=v.length)
    db.add(vid); db.commit(); db.refresh(vid)
    return {"id": vid.id}

@app.put("/video/{video_id}")
def update_video(
    video_id: int,
    title: str = Query(None),
    creator_handle: str = Query(None),
    views: int = Query(None),
    length: int = Query(None),
    votes: int = Query(None),
    likes: int = Query(None),
    db: Session = Depends(get_db)
):
    video = db.get(models.Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    updated_fields = {}
    if title is not None:
        video.title = title
        updated_fields["title"] = title
    if creator_handle is not None:
        video.creator_handle = creator_handle
        updated_fields["creator_handle"] = creator_handle
    if views is not None:
        video.views = views
        updated_fields["views"] = views
    if length is not None:
        video.length = length
        updated_fields["length"] = length
    if votes is not None:
        video.votes = votes
        updated_fields["votes"] = votes
    if likes is not None:
        video.likes = likes
        updated_fields["likes"] = likes
    db.commit()
    db.refresh(video)
    return {"id": video.id, **updated_fields}


# Get a video by id
@app.get("/video/{video_id}")
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = db.get(models.Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return {
        "id": video.id,
        "title": video.title,
        "creator_handle": video.creator_handle,
        "views": video.views,
        "length": video.length,
        "votes": video.votes,
        "likes": video.likes
    }

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
        db.get(models.User, db.get(models.Session, ev.session_id).viewer_handle).total_interactions,
        ev.donation_amount,
        db.get(models.User, db.get(models.Session, ev.session_id).viewer_handle).total_donations,
        db.get(models.User, db.get(models.Session, ev.session_id).viewer_handle).time_spent_on_app,
        db.get(models.User, db.get(models.Session, ev.session_id).viewer_handle).account_age_days
    ]
    is_suspicious = fraud_model.predict([features])[0] 

    if is_suspicious:
        e.status = "under_review"
        db.commit()
        return {"event_id": e.id, "status": "under_review"}

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
    result = []
    for bounty in bounties:
        # Use relationship to get all submissions and their videos
        seen_creator_handles = set()
        current_videos = []
        for submission in bounty.submissions:
            v = submission.video
            if v and v.creator_handle not in seen_creator_handles:
                video_data = {
                    "id": v.id,
                    "title": v.title,
                    "creator_handle": v.creator_handle,
                    "views": v.views,
                    "duration": v.length,
                    "votes": v.votes,
                    "likes": v.likes
                }
                current_videos.append(video_data)
                seen_creator_handles.add(v.creator_handle)
        bounty_dict = {
            "id": bounty.id,
            "description": bounty.description,
            "prize_pool": bounty.prize_pool,
            "cutoff_date": bounty.cutoff_date.isoformat(),
            "judging_start": bounty.judging_start.isoformat(),
            "judging_end": bounty.judging_end.isoformat(),
            "is_closed": bounty.is_closed,
            "current_videos": current_videos,
            "following": bounty.following
        }
        result.append(bounty_dict)
    return result

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
        creator_handle=bounty.creator_handle,
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
        "creator_handle": new_bounty.creator_handle,
        "description": new_bounty.description,
        "prize_pool": new_bounty.prize_pool,
        "cutoff_date": new_bounty.cutoff_date.isoformat(),
        "judging_start": new_bounty.judging_start.isoformat(),
        "judging_end": new_bounty.judging_end.isoformat(),
        "is_closed": new_bounty.is_closed
    }

@app.post("/bounty/{bounty_id}/contribute")
def contribute_bounty(bounty_id: int, viewer_handle: str, amount: float, db: Session = Depends(get_db)):
    # Check if viewer has submitted to this bounty
    user_submission = db.query(BountySubmission).filter_by(bounty_id=bounty_id, creator_handle=viewer_handle).first()
    if user_submission:
        raise HTTPException(status_code=403, detail="Submitters cannot donate to this bounty.")
    bounty = db.get(Bounty, bounty_id)
    if not bounty or bounty.is_closed:
        raise HTTPException(status_code=404, detail="Bounty not found or closed")
    contribution = BountyContribution(bounty_id=bounty_id, viewer_handle=viewer_handle, amount=amount)
    bounty.prize_pool += amount
    db.add(contribution)

    # Update viewer's wallet and total_donations
    viewer = db.query(User).filter_by(handle=viewer_handle).first()
    if viewer:
        viewer.wallet -= amount
        viewer.total_donations += amount

    db.commit()
    return {"success": True, "new_prize_pool": bounty.prize_pool}

@app.post("/bounty/{bounty_id}/submit")
def submit_bounty(bounty_id: int, creator_handle: str, video_id: int, db: Session = Depends(get_db)):
    bounty = db.get(Bounty, bounty_id)
    if not bounty or bounty.is_closed or datetime.now() > bounty.cutoff_date:
        raise HTTPException(status_code=400, detail="Bounty closed or cutoff passed")
    
    # Condition 1: User who created the bounty cannot submit
    if bounty.creator_handle == creator_handle:
        raise HTTPException(status_code=403, detail="Bounty creator cannot submit a video to their own bounty.")
    
    # Condition 2: User who contributed to the bounty cannot submit
    contribution = db.query(BountyContribution).filter_by(bounty_id=bounty_id, viewer_handle=creator_handle).first()
    if contribution:
        raise HTTPException(status_code=403, detail="Contributors cannot submit a video to this bounty.")

    submission = BountySubmission(bounty_id=bounty_id, creator_handle=creator_handle, video_id=video_id)
    db.add(submission)
    db.commit()
    return {"success": True}

@app.post("/bounty/{bounty_id}/vote")
def vote_bounty(bounty_id: int, submission_id: int, viewer_handle: str, db: Session = Depends(get_db)):
    bounty = db.get(Bounty, bounty_id)
    # if not bounty or not (bounty.judging_start <= datetime.now() <= bounty.judging_end):
    #     raise HTTPException(status_code=400, detail="Not in judging period")
   
    # Check if viewer has submitted to this bounty
    user_submission = db.query(BountySubmission).filter_by(bounty_id=bounty_id, creator_handle=viewer_handle).first()
    if user_submission:
        raise HTTPException(status_code=403, detail="Submitters cannot vote on this bounty.")

    # Check if viewer has already voted for this submission
    existing_vote = db.query(BountyVote).filter_by(bounty_id=bounty_id, submission_id=submission_id, viewer_handle=viewer_handle).first()
    if existing_vote:
        raise HTTPException(status_code=400, detail="User has already voted for this submission.")

    vote = BountyVote(bounty_id=bounty_id, submission_id=submission_id, viewer_handle=viewer_handle)
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
                "creator_handle": submission.creator_handle,
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
