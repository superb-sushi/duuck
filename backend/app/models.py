from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

# Association table for many-to-many relationship between Bounties and Creators
bounty_creators = Table(
    "bounty_creators",
    Base.metadata,
    Column("bounty_id", Integer, ForeignKey("bounties.id"), primary_key=True),
    Column("creator_handle", String, ForeignKey("users.handle"), primary_key=True)  # Changed from viewer_handle to creator_handle
)

class User(Base):
    __tablename__ = "users"
    handle = Column(String, primary_key=True)
    wallet = Column(Float, default=0.0)
    total_donations = Column(Float, default=0.0)
    time_spent_on_app = Column(Integer, default=0)
    account_age_days = Column(Integer, default=0)
    total_interactions = Column(Integer, default=0)  # Total interactions represent the user's interactions with other content

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True)
    creator_handle = Column(String, ForeignKey("users.handle"))
    title = Column(String)
<<<<<<< HEAD
    phash = Column(String, nullable=True)  # mock perceptual hash
=======
    phash = Column(String)
    length = Column(Integer)
    views = Column(Integer, default=0)
    votes = Column(Integer, default=0)
    likes = Column(Integer, default=0)
>>>>>>> 9b4395d28ee7a19e1f5eb93fb2d95a578d4d905f
    creator = relationship("User")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    viewer_handle = Column(String, ForeignKey("users.handle"))  # Changed from viewer_id to viewer_handle
    started_at = Column(DateTime, default=datetime.now)
    ended_at = Column(DateTime, nullable=True)
    viewer = relationship("User")

class SessionEvent(Base):
    __tablename__ = "session_events"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    video_id = Column(Integer, ForeignKey("videos.id"))
    viewer_handle = Column(String, ForeignKey("users.handle"))  # Added viewer_handle for direct reference
    seconds_watched = Column(Integer)
    interactions = Column(Integer, default=0)  # likes/comments simplified
    donation_amount = Column(Float, default=0.0)
    target = Column(Integer, nullable=False, default=0)  # Added default value for target
    status = Column(String, default="pending")  # pending|approved|rejected|under_review

class Bounty(Base):
    __tablename__ = "bounties"
    id = Column(Integer, primary_key=True)
    description = Column(String)
    creator_handle = Column(String, ForeignKey("users.handle"))  # Updated from creator_id
    prize_pool = Column(Float, default=0.0)
    cutoff_date = Column(DateTime)
    judging_start = Column(DateTime)
    judging_end = Column(DateTime)
    is_closed = Column(Boolean, default=False)
<<<<<<< HEAD
=======
    following = Column(Boolean, default=False)
    submissions = relationship("BountySubmission", backref="bounty")
>>>>>>> 9b4395d28ee7a19e1f5eb93fb2d95a578d4d905f

class BountyContribution(Base):
    __tablename__ = "bounty_contributions"
    id = Column(Integer, primary_key=True)
    bounty_id = Column(Integer, ForeignKey("bounties.id"))
    viewer_handle = Column(String, ForeignKey("users.handle"))  # Updated from viewer_id
    amount = Column(Float)

class BountySubmission(Base):
    __tablename__ = "bounty_submissions"
    id = Column(Integer, primary_key=True)
    bounty_id = Column(Integer, ForeignKey("bounties.id"))
    creator_handle = Column(String, ForeignKey("users.handle"))  # Updated from creator_id
    video_id = Column(Integer, ForeignKey("videos.id"))
    submitted_at = Column(DateTime, default=datetime.utcnow)
<<<<<<< HEAD
=======
    video = relationship("Video")
>>>>>>> 9b4395d28ee7a19e1f5eb93fb2d95a578d4d905f

class BountyVote(Base):
    __tablename__ = "bounty_votes"
    id = Column(Integer, primary_key=True)
    bounty_id = Column(Integer, ForeignKey("bounties.id"))
    submission_id = Column(Integer, ForeignKey("bounty_submissions.id"))
    viewer_handle = Column(String, ForeignKey("users.handle"))  # Updated from viewer_id

class BountyFollow(Base):
    __tablename__ = "bounty_follows"
    id = Column(Integer, primary_key=True)
    bounty_id = Column(Integer, ForeignKey("bounties.id"))
    user_handle = Column(String, ForeignKey("users.handle"))  # Updated from user_id