from pydantic import BaseModel
from typing import List, Optional, Dict

class ViewerCreate(BaseModel):
    name: str
    weekly_budget: float = 0.0

class CreatorCreate(BaseModel):
    handle: str

class UserCreate(BaseModel):
    weekly_budget: float = 0.0
    kyc_level: str = "none"  # none|basic|full
    device_attested: bool = False
    risk_tier: str = "low"  # low|med|high
    reserve_pct: float = 0.1


class VideoCreate(BaseModel):
    creator_id: int
    title: str
    phash: Optional[str] = None
    c2pa_status: str = "unknown"

class SessionStart(BaseModel):
    viewer_id: int

class SessionEventIn(BaseModel):
    session_id: int
    video_id: int
    seconds_watched: int
    interactions: int = 0
    boost_amount: float = 0.0

class BoostIn(BaseModel):
    viewer_id: int
    video_id: int
    amount: float

class APRIn(BaseModel):
    window: str
    session_id: int
    video_id: int
    seconds_watched: int
    nonce: str

class AllocationOut(BaseModel):
    session_id: int
    breakdown: List[Dict]
    total_spent: float

class BountyCreate(BaseModel):
    creator_id: int
    description: str
    cutoff_date: str  # ISO format
    judging_start: str
    judging_end: str
    prize_pool: float

class BountyOut(BaseModel):
    id: int
    creator_id: int
    description: str
    prize_pool: float
    cutoff_date: str
    judging_start: str
    judging_end: str
    is_closed: bool

class UserOut(BaseModel):
    id: int
    weekly_budget: float
    kyc_level: str
    device_attested: bool
    risk_tier: str
    reserve_pct: float

class BountyFollow(BaseModel):
    bounty_id: int
    user_id: int

