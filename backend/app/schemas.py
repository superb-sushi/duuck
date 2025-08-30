from pydantic import BaseModel
from typing import List, Optional, Dict

class UserCreate(BaseModel):
    handle: str  # No change needed

class VideoCreate(BaseModel):
    creator_handle: str  # Updated from creator_id
    title: str
    phash: Optional[str] = None
    views: int = 0
    votes: int = 0
    likes: int = 0
    duration: int = 0  # duration replaces length

class SessionStart(BaseModel):
    viewer_handle: str  # Changed from viewer_id to viewer_handle

class SessionEventIn(BaseModel):
    session_id: int
    video_id: int
    viewer_handle: str  # Changed from viewer_id to viewer_handle
    seconds_watched: int
    interactions: int = 0
    donation_amount: float = 0.0

class BountyCreate(BaseModel):
    creator_handle: str
    description: str
    cutoff_date: str  # ISO format
    judging_start: str
    judging_end: str
    prize_pool: float

class BountyOut(BaseModel):
    id: int
    creator_handle: str
    description: str
    prize_pool: float
    cutoff_date: str
    judging_start: str
    judging_end: str
    is_closed: bool
    current_videos: List[Dict] = []
    following: bool = False


class BountyFollow(BaseModel):
    bounty_id: int
    user_handle: str

