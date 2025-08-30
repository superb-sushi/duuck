
from sqlalchemy.orm import Session
from .models import User

# Simple, explicit rules for the demo
def viewer_ok(db: Session, viewer_id: int) -> bool:
    u = db.get(User, viewer_id)
    if not u:
        return False
    # Example constraints: if weekly_budget is 0 and kyc is none, still allow but flag elsewhere
    return True

def creator_reserve_pct(db: Session, creator_id: int) -> float:
    u = db.get(User, creator_id)
    if not u:
        return 0.1
    base = u.reserve_pct or 0.1
    if (u.risk_tier or "").lower() == "high":
        return max(0.25, base)
    return base
