from sqlalchemy.orm import Session
from .models import LedgerEntry

def post(db: Session, account: str, debit: float, credit: float, ref_type: str, ref_id: int):
    db.add(LedgerEntry(account=account, debit=debit, credit=credit, ref_type=ref_type, ref_id=ref_id))
    db.commit()