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

class BountyCreate(BaseModel):
    title: str
    description: Optional[str] = None
    initial_donation: float
    competing_creators: List[str] = []  # Changed to list of creator handles

class VoteCreate(BaseModel):
    bounty_id: int
    viewer_handle: str  # Changed from user_id to viewer_handle
    video_id: int

class BountyFollow(BaseModel):
    bounty_id: int
    viewer_handle: str  # Changed from user_id to viewer_handle

class Donation(BaseModel):
    bounty_id: int
    viewer_handle: str  # Changed from user_id to viewer_handle
    amount: float

class VideoSubmission(BaseModel):
    bounty_id: int
    creator_handle: str  # Changed from creator_id to creator_handle
    title: str