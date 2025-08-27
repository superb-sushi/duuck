from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class Viewer(Base):
    __tablename__ = "viewers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    weekly_budget = Column(Float, default=0.0)
    kyc_level = Column(String, default="none")  # none|basic|full
    device_attested = Column(Boolean, default=False)

class Creator(Base):
    __tablename__ = "creators"
    id = Column(Integer, primary_key=True)
    handle = Column(String, unique=True)
    risk_tier = Column(String, default="low")  # low|med|high
    reserve_pct = Column(Float, default=0.1)

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey("creators.id"))
    title = Column(String)
    phash = Column(String, nullable=True)  # mock perceptual hash
    c2pa_status = Column(String, default="unknown")  # unknown|verified|failed
    creator = relationship("Creator")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    viewer_id = Column(Integer, ForeignKey("viewers.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    viewer = relationship("Viewer")

class SessionEvent(Base):
    __tablename__ = "session_events"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    video_id = Column(Integer, ForeignKey("videos.id"))
    seconds_watched = Column(Integer)
    interactions = Column(Integer, default=0)  # likes/comments simplified
    boost_amount = Column(Float, default=0.0)
    cqscore = Column(Float, default=0.0)

class Boost(Base):
    __tablename__ = "boosts"
    id = Column(Integer, primary_key=True)
    viewer_id = Column(Integer, ForeignKey("viewers.id"))
    video_id = Column(Integer, ForeignKey("videos.id"))
    amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class Allocation(Base):
    __tablename__ = "allocations"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    creator_id = Column(Integer, ForeignKey("creators.id"))
    weight = Column(Float)
    amount = Column(Float)
    components = Column(JSON)  # explanation parts

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