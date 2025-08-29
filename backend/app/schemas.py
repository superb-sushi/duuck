from pydantic import BaseModel
from typing import List, Optional, Dict

class ViewerCreate(BaseModel):
    name: str

class CreatorCreate(BaseModel):
    handle: str

class VideoCreate(BaseModel):
    creator_id: int
    title: str
    phash: Optional[str] = None

class SessionStart(BaseModel):
    viewer_id: int

class SessionEventIn(BaseModel):
    session_id: int
    video_id: int
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
    competing_creators: List[int] = []  # List of creator IDs joining the bounty

class VoteCreate(BaseModel):
    bounty_id: int
    user_id: int
    video_id: int

class BountyFollow(BaseModel):
    bounty_id: int
    user_id: int

class Donation(BaseModel):
    bounty_id: int
    user_id: int
    amount: float

class VideoSubmission(BaseModel):
    bounty_id: int
    creator_id: int
    title: str