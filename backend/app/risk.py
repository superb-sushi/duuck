from sqlalchemy.orm import Session
# from .models import Viewer, Creator

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