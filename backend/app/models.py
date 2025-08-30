
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

# ---------------- Core user/creator/viewer model ----------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    # optional display handle for creators
    handle = Column(String, unique=True, nullable=True)
    weekly_budget = Column(Float, default=0.0)
    kyc_level = Column(String, default="none")  # none|basic|full
    device_attested = Column(Boolean, default=False)
    risk_tier = Column(String, default="normal")  # low|normal|high
    reserve_pct = Column(Float, default=0.1)      # default reserve used if creator
    created_at = Column(DateTime, default=datetime.utcnow)

# ---------------- Videos ----------------
class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    kind = Column(String, default="post")  # "post" or "live"
    phash = Column(String, nullable=True)
    c2pa_status = Column(String, default="unknown")
    created_at = Column(DateTime, default=datetime.utcnow)

# ---------------- Sessions & events (for APR and AML review) ----------------
class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    viewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

class SessionEvent(Base):
    __tablename__ = "session_events"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    seconds_watched = Column(Integer, default=0)
    interactions = Column(Integer, default=0)
    donation_amount = Column(Float, default=0.0)
    target = Column(Integer, default=0)
    status = Column(String, default="approved")  # approved/under_review/rejected
    created_at = Column(DateTime, default=datetime.utcnow)

# ---------------- Ledger ----------------
class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id = Column(Integer, primary_key=True)
    account = Column(String)   # escrow, platform_pool, escrow_reserve, creator_payable
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    ref_type = Column(String)  # e.g., fairsplit_fee, paid_request_payout
    ref_id = Column(Integer)   # related object id
    ts = Column(DateTime, default=datetime.utcnow)

# ---------------- APR receipts & Merkle snapshots ----------------
class APRCommitment(Base):
    __tablename__ = "apr_commitments"
    id = Column(Integer, primary_key=True)
    window = Column(String, index=True)  # YYYYMMDDHH
    commitment = Column(String)          # sha256 hex
    meta = Column(JSON)                  # {session_id, video_id, seconds_watched, interactions, nonce, device_hash}
    created_at = Column(DateTime, default=datetime.utcnow)

class MerkleRoot(Base):
    __tablename__ = "merkle_roots"
    id = Column(Integer, primary_key=True)
    window = Column(String, unique=True)
    root = Column(String)
    leaves_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

# ---------------- Bounty core ----------------
class Bounty(Base):
    __tablename__ = "bounties"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="open")  # open/closed/ended
    cutoff_dt = Column(DateTime, nullable=True)
    pool_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class BountySubmission(Base):
    __tablename__ = "bounty_submissions"
    id = Column(Integer, primary_key=True)
    bounty_id = Column(Integer, ForeignKey("bounties.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id"))
    submitted_at = Column(DateTime, default=datetime.utcnow)

class BountyVote(Base):
    __tablename__ = "bounty_votes"
    id = Column(Integer, primary_key=True)
    bounty_id = Column(Integer, ForeignKey("bounties.id"))
    submission_id = Column(Integer, ForeignKey("bounty_submissions.id"))
    viewer_id = Column(Integer, ForeignKey("users.id"))

class BountyFollow(Base):
    __tablename__ = "bounty_follows"
    id = Column(Integer, primary_key=True)
    bounty_id = Column(Integer, ForeignKey("bounties.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

class Donation(Base):
    __tablename__ = "donations"
    id = Column(Integer, primary_key=True)
    bounty_id = Column(Integer, ForeignKey("bounties.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ---------------- Paid livestream requests ----------------
class PaidRequest(Base):
    __tablename__ = "paid_requests"
    id = Column(Integer, primary_key=True)
    viewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending/accepted/delivered/approved/rejected/disputed/refunded
    deadline = Column(DateTime, nullable=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=True)  # proof attachment
    created_at = Column(DateTime, default=datetime.utcnow)

class LivestreamTask(Base):
    __tablename__ = "livestream_tasks"
    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    request_id = Column(Integer, ForeignKey("paid_requests.id"), nullable=True)
    title = Column(String, nullable=False)
    status = Column(String, default="scheduled")  # scheduled/live/completed/cancelled
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
