from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

# Association table for many-to-many relationship between Bounties and Creators
bounty_creators = Table(
    "bounty_creators",
    Base.metadata,
    Column("bounty_id", Integer, ForeignKey("bounties.id"), primary_key=True),
    Column("creator_handle", String, ForeignKey("creators.handle"), primary_key=True)  # Changed from viewer_handle to creator_handle
)

class Viewer(Base):
    __tablename__ = "viewers"
    handle = Column(String, primary_key=True)  # Changed from id to handle
    kyc_level = Column(String, default="none")  # none|basic|full
    device_attested = Column(Boolean, default=False)
    total_donations = Column(Float, default=0.0)
    time_spent_on_app = Column(Integer, default=0)
    account_age_days = Column(Integer, default=0)
    total_interactions = Column(Integer, default=0)  # Total interactions represent the user's interactions with other content

class Creator(Base):
    __tablename__ = "creators"
    handle = Column(String, primary_key=True)  # Changed from id to handle
    risk_tier = Column(String, default="low")  # low|med|high
    reserve_pct = Column(Float, default=0.1)

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True)
    creator_handle = Column(String, ForeignKey("creators.handle"))  # Changed from creator_id to creator_handle
    title = Column(String)
    phash = Column(String, nullable=True)  # mock perceptual hash
    c2pa_status = Column(String, default="unknown")  # unknown|verified|failed
    creator = relationship("Creator")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    viewer_handle = Column(String, ForeignKey("viewers.handle"))  # Changed from viewer_id to viewer_handle
    started_at = Column(DateTime, default=datetime.now)
    ended_at = Column(DateTime, nullable=True)
    viewer = relationship("Viewer")

class SessionEvent(Base):
    __tablename__ = "session_events"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    video_id = Column(Integer, ForeignKey("videos.id"))
    viewer_handle = Column(String, ForeignKey("viewers.handle"))  # Added viewer_handle for direct reference
    seconds_watched = Column(Integer)
    interactions = Column(Integer, default=0)  # likes/comments simplified
    donation_amount = Column(Float, default=0.0)
    target = Column(Integer, nullable=False, default=0)  # Added default value for target
    status = Column(String, default="pending")  # pending|approved|rejected|under_review

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id = Column(Integer, primary_key=True)
    account = Column(String)  # escrow, creator_payable, platform_pool
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    ref_type = Column(String)
    ref_id = Column(Integer)
    ts = Column(DateTime, default=datetime.utcnow)

class APRCommitment(Base):
    __tablename__ = "apr_commitments"
    id = Column(Integer, primary_key=True)
    window = Column(String)  # e.g., YYYYMMDDHH
    commitment = Column(String)  # hex digest
    meta = Column(JSON)  # {session_id, video_id, viewer_id? (optional)}

class MerkleRoot(Base):
    __tablename__ = "merkle_roots"
    id = Column(Integer, primary_key=True)
    window = Column(String, unique=True)
    root = Column(String)  # hex root
    leaves_count = Column(Integer, default=0)

class Bounty(Base):
    __tablename__ = "bounties"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    user_creator_handle = Column(String, ForeignKey("viewers.handle"))
    status = Column(String, default="open")  # open|voting|ended
    total_donations = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_creator = relationship("Viewer", backref="bounties")  # Updated relationship to Viewer
    competing_creators = relationship("Creator", secondary=bounty_creators, backref="bounties")

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True)
    bounty_id = Column(Integer, ForeignKey("bounties.id"))
    user_handle = Column(String, ForeignKey("viewers.handle"))  # Changed from user_id to user_handle
    video_id = Column(Integer, ForeignKey("videos.id"))

class BountyFollow(Base):
    __tablename__ = "bounty_follows"
    id = Column(Integer, primary_key=True)
    bounty_id = Column(Integer, ForeignKey("bounties.id"))
    user_handle = Column(String, ForeignKey("viewers.handle"))  # Changed from user_id to user_handle

class Donation(Base):
    __tablename__ = "donations"
    id = Column(Integer, primary_key=True)
    bounty_id = Column(Integer, ForeignKey("bounties.id"))
    user_handle = Column(String, ForeignKey("viewers.handle"))  # Changed from user_id to user_handle
    amount = Column(Float, nullable=False)