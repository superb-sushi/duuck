
from pydantic import BaseModel
from typing import Optional, List, Dict

# ---------- Users ----------
class UserCreate(BaseModel):
    handle: Optional[str] = None
    weekly_budget: float = 0.0
    kyc_level: str = "none"
    device_attested: bool = False
    risk_tier: str = "normal"
    reserve_pct: float = 0.1

class UserOut(BaseModel):
    id: int
    handle: Optional[str] = None
    weekly_budget: float
    kyc_level: str
    device_attested: bool
    risk_tier: str
    reserve_pct: float

# ---------- Videos ----------
class VideoCreate(BaseModel):
    creator_id: int
    title: str
    kind: str = "post"

# ---------- APR ----------
class APRIn(BaseModel):
    window: str              # YYYYMMDDHH
    session_id: int
    video_id: int
    seconds_watched: int
    interactions: int
    nonce: str               # client-generated
    device_hash: Optional[str] = None

# ---------- Paid Requests (livestream) ----------
class PaidRequestCreate(BaseModel):
    viewer_id: int
    creator_id: int
    title: str
    description: Optional[str] = None
    amount: float
    deadline_iso: Optional[str] = None

class PaidRequestAction(BaseModel):
    request_id: int

class PaidRequestDeliver(BaseModel):
    request_id: int
    video_id: int

# ---------- Bounties ----------
class BountyCreate(BaseModel):
    title: str
    description: Optional[str] = None
    cutoff_dt_iso: Optional[str] = None

class BountyOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    pool_amount: float

class BountySubmissionCreate(BaseModel):
    bounty_id: int
    creator_id: int
    video_id: int

class BountyFollow(BaseModel):
    bounty_id: int
    user_id: int
