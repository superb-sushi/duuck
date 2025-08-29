from sqlalchemy.orm import Session
from .models import Viewer, Creator, Video, SessionEvent

# Extremely simplified demo logic
def viewer_ok(db: Session, viewer_id: int) -> bool:
    v = db.get(Viewer, viewer_id)
    if not v:
        return False
    # require at least basic KYC for boosts > $50 (not enforced here, demo)
    return True

def creator_reserve_pct(db: Session, creator_id: int) -> float:
    c = db.get(Creator, creator_id)
    if not c:
        return 0.1
    return c.reserve_pct if c.risk_tier != "high" else max(0.25, c.reserve_pct)

def is_suspicious_donator(db: Session, viewer_id: int) -> bool:
    viewer = db.get(Viewer, viewer_id)
    if not viewer:
        return False

    # Check if the viewer is new
    if viewer.kyc_level == "none":
        return True

    # Check if the viewer only donates without interacting with other content
    donation_events = db.query(SessionEvent).filter_by(viewer_id=viewer_id).count()
    interaction_events = db.query(SessionEvent).filter(SessionEvent.viewer_id == viewer_id, SessionEvent.interactions > 0).count()

    return donation_events > 0 and interaction_events == 0

def is_suspicious_creator(db: Session, creator_id: int) -> bool:
    creator = db.get(Creator, creator_id)
    if not creator:
        return False

    # Check if the creator is new and receiving large donations
    if creator.risk_tier == "high":
        return True

    donation_events = db.query(SessionEvent).filter_by(creator_id=creator_id).count()
    return donation_events > 10 and creator.reserve_pct < 0.2

def has_data_discrepancies(db: Session, creator_id: int) -> bool:
    creator = db.get(Creator, creator_id)
    if not creator:
        return False

    # Check discrepancies in follower count and donations
    followers = db.query(Viewer).filter_by(creator_id=creator_id).count()
    donation_events = db.query(SessionEvent).filter_by(creator_id=creator_id).count()

    return followers < 10 and donation_events > 100