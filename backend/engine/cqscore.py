# CQScore: content quality + originality + safety (mock)
# For demo: logistic transform of seconds watched and interactions; originality bonus if c2pa verified
from sqlalchemy.orm import Session
from math import exp
from app.models import Video # Changed import path due to error - Daniel

def compute(seconds_watched: int, interactions: int, video: Video) -> float:
    # Normalize seconds_watched into [0,1] roughly assuming 0-60s clips
    x = min(seconds_watched, 60) / 60.0
    inter = min(interactions, 10) / 10.0
    base = 1 / (1 + exp(-6 * (x - 0.5)))  # sigmoid centered at 0.5
    bonus = 0.1 * inter
    provenance = 0.15 if (video.c2pa_status == "verified") else 0.0
    return max(0.0, min(1.0, base + bonus + provenance))