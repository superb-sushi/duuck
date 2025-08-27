from pydantic import BaseModel
from typing import List, Optional, Dict

class ViewerCreate(BaseModel):
    name: str
    weekly_budget: float = 0.0

class CreatorCreate(BaseModel):
    handle: str

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