from pydantic import BaseModel
from typing import List, Optional, Dict

class ViewerCreate(BaseModel):
    handle: str  # Changed from name to handle

class CreatorCreate(BaseModel):
    handle: str  # No change needed

class VideoCreate(BaseModel):
    creator_handle: str  # Changed from creator_id to creator_handle
    title: str
    phash: Optional[str] = None
    c2pa_status: Optional[str] = None  # Added to match the creation logic

class SessionStart(BaseModel):
    viewer_handle: str  # Changed from viewer_id to viewer_handle

class SessionEventIn(BaseModel):
    session_id: int
    video_id: int
    viewer_handle: str  # Changed from viewer_id to viewer_handle
    seconds_watched: int
    interactions: int = 0
    donation_amount: float = 0.0

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

