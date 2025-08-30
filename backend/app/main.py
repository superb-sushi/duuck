
import hashlib
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from contextlib import asynccontextmanager

from .db import Base, engine, get_db
from . import models, schemas
from .ledger import post as ledger_post
from .risk import viewer_ok, creator_reserve_pct
from engine.merkle import merkle_root, merkle_proofs, verify_proof, commit_from_meta

PLATFORM_FEE_RATE = 0.05  # 5%

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- APR: Attested Playback Receipts --------------------
def _is_duplicate_commitment(db: Session, window: str, commitment: str) -> bool:
    return db.query(models.APRCommitment).filter_by(window=window, commitment=commitment).first() is not None

@app.post("/apr/commit")
def apr_commit(apr: schemas.APRIn, db: Session = Depends(get_db)):
    ses = db.get(models.Session, apr.session_id)
    if not ses:
        raise HTTPException(status_code=404, detail="session not found")
    if not viewer_ok(db, ses.viewer_id):
        raise HTTPException(status_code=400, detail="viewer/session failed basic checks")

    meta = {
        "session_id": apr.session_id,
        "video_id": apr.video_id,
        "seconds_watched": apr.seconds_watched,
        "interactions": apr.interactions,
        "nonce": apr.nonce,
        "device_hash": apr.device_hash or "",
    }
    commitment = commit_from_meta(meta)
    if _is_duplicate_commitment(db, apr.window, commitment):
        return {"commitment": commitment, "status": "duplicate_ignored"}
    db.add(models.APRCommitment(window=apr.window, commitment=commitment, meta=meta))
    db.commit()
    return {"commitment": commitment, "status": "recorded"}

@app.post("/apr/publish_root")
def apr_publish_root(window: str, db: Session = Depends(get_db)):
    commits = db.query(models.APRCommitment).filter_by(window=window).all()
    leaves = [c.commitment for c in commits]
    root = merkle_root(leaves)
    mr = db.query(models.MerkleRoot).filter_by(window=window).first()
    if not mr:
        mr = models.MerkleRoot(window=window, root=root, leaves_count=len(leaves))
        db.add(mr)
    else:
        mr.root = root
        mr.leaves_count = len(leaves)
    db.commit()
    return {"window": window, "root": root, "count": len(leaves)}

@app.get("/apr/proofs")
def apr_proofs(window: str, db: Session = Depends(get_db)):
    commits = db.query(models.APRCommitment).filter_by(window=window).all()
    leaves = [c.commitment for c in commits]
    proofs = merkle_proofs(leaves)
    out = []
    for c, p in zip(commits, proofs):
        out.append({"commitment": c.commitment, "meta": c.meta, "proof": p})
    mr = db.query(models.MerkleRoot).filter_by(window=window).first()
    return {"window": window, "root": mr.root if mr else "", "proofs": out}

# -------------------- FairSplit (bounties) --------------------
def _receipt_weight(meta: dict) -> float:
    return min(60, int(meta.get("seconds_watched",0))) + 2.0 * min(10, int(meta.get("interactions",0)))

@app.post("/fairsplit/preview")
def fairsplit_preview(window: str, bounty_id: int, db: Session = Depends(get_db)):
    mr = db.query(models.MerkleRoot).filter_by(window=window).first()
    if not mr or not mr.root:
        raise HTTPException(status_code=404, detail="No merkle root for window")
    commits = db.query(models.APRCommitment).filter_by(window=window).all()
    by_video = {}
    for c in commits:
        by_video[c.meta["video_id"]] = by_video.get(c.meta["video_id"], 0.0) + _receipt_weight(c.meta)
    total = sum(by_video.values()) or 1.0
    bounty = db.get(models.Bounty, bounty_id)
    pool = float(bounty.pool_amount if bounty else 0.0)
    alloc = {vid: round(pool * (w/total), 2) for vid, w in by_video.items()}
    return {"window": window, "root": mr.root, "pool": pool, "weights": by_video, "alloc": alloc}

@app.post("/fairsplit/settle")
def fairsplit_settle(window: str, bounty_id: int, top_n: int = 3, db: Session = Depends(get_db)):
    prev = fairsplit_preview(window, bounty_id, db)
    alloc = prev["alloc"]
    top = sorted(alloc.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    pool = prev["pool"]
    denom = sum(v for _, v in top) or 1.0
    payouts = [(vid, round(pool * (v/denom), 2)) for vid, v in top]

    results = []
    for vid, amt in payouts:
        video = db.get(models.Video, vid)
        if not video:
            continue
        creator_id = video.creator_id
        fee = round(PLATFORM_FEE_RATE * amt, 2)
        reserve_pct = creator_reserve_pct(db, creator_id)
        reserve = round(reserve_pct * (amt - fee), 2)
        net = round(amt - fee - reserve, 2)

        # Fee
        ledger_post(db, account="escrow", credit=fee, debit=0.0, ref_type="fairsplit_fee", ref_id=vid)
        ledger_post(db, account="platform_pool", debit=fee, credit=0.0, ref_type="fairsplit_fee", ref_id=vid)
        # Reserve
        if reserve > 0:
            ledger_post(db, account="escrow", credit=reserve, debit=0.0, ref_type="fairsplit_reserve", ref_id=vid)
            ledger_post(db, account="escrow_reserve", debit=reserve, credit=0.0, ref_type="fairsplit_reserve", ref_id=vid)
        # Net payout
        ledger_post(db, account="escrow", credit=net, debit=0.0, ref_type="fairsplit_payout", ref_id=vid)
        ledger_post(db, account="creator_payable", debit=net, credit=0.0, ref_type="fairsplit_payout", ref_id=vid)

        results.append({"video_id": vid, "gross": amt, "fee": fee, "reserve": reserve, "net_to_creator": net})

    return {"bounty_id": bounty_id, "window": window, "root": prev["root"], "payouts": results}

@app.post("/payout/release_reserve")
def payout_release_reserve(creator_id: int, amount: float, db: Session = Depends(get_db)):
    ledger_post(db, account="escrow_reserve", credit=amount, debit=0.0, ref_type="reserve_release", ref_id=creator_id)
    ledger_post(db, account="creator_payable", debit=amount, credit=0.0, ref_type="reserve_release", ref_id=creator_id)
    return {"creator_id": creator_id, "released": amount}

# -------------------- Paid Requests (livestream) --------------------
@app.post("/live/request")
def live_request_create(req: schemas.PaidRequestCreate, db: Session = Depends(get_db)):
    pr = models.PaidRequest(
        viewer_id=req.viewer_id,
        creator_id=req.creator_id,
        title=req.title,
        description=req.description,
        amount=req.amount,
        deadline=datetime.fromisoformat(req.deadline_iso) if req.deadline_iso else None,
    )
    db.add(pr); db.commit(); db.refresh(pr)
    ledger_post(db, account="escrow", debit=float(req.amount), credit=0.0, ref_type="paid_request", ref_id=pr.id)
    return {"request_id": pr.id, "status": pr.status}

@app.post("/live/request/accept")
def live_request_accept(act: schemas.PaidRequestAction, db: Session = Depends(get_db)):
    pr = db.get(models.PaidRequest, act.request_id)
    if not pr: raise HTTPException(status_code=404, detail="request not found")
    if pr.status != "pending": raise HTTPException(status_code=400, detail="cannot accept")
    pr.status = "accepted"; db.commit()
    task = models.LivestreamTask(creator_id=pr.creator_id, request_id=pr.id, title=pr.title, status="scheduled")
    db.add(task); db.commit()
    return {"request_id": pr.id, "status": pr.status, "task_id": task.id}

@app.post("/live/request/deliver")
def live_request_deliver(pay: schemas.PaidRequestDeliver, db: Session = Depends(get_db)):
    pr = db.get(models.PaidRequest, pay.request_id)
    if not pr: raise HTTPException(status_code=404, detail="request not found")
    if pr.status not in ["accepted","pending"]: raise HTTPException(status_code=400, detail="cannot deliver")
    pr.video_id = pay.video_id
    pr.status = "delivered"
    db.commit()
    return {"request_id": pr.id, "status": pr.status, "video_id": pr.video_id}

@app.post("/live/request/approve")
def live_request_approve(act: schemas.PaidRequestAction, db: Session = Depends(get_db)):
    pr = db.get(models.PaidRequest, act.request_id)
    if not pr: raise HTTPException(status_code=404, detail="request not found")
    if pr.status != "delivered": raise HTTPException(status_code=400, detail="cannot approve")
    pr.status = "approved"; db.commit()

    fee = round(PLATFORM_FEE_RATE * pr.amount, 2)
    reserve_pct = creator_reserve_pct(db, pr.creator_id)
    reserve = round(reserve_pct * (pr.amount - fee), 2)
    net = round(pr.amount - fee - reserve, 2)

    ledger_post(db, account="escrow", credit=fee, debit=0.0, ref_type="paid_request_fee", ref_id=pr.id)
    ledger_post(db, account="platform_pool", debit=fee, credit=0.0, ref_type="paid_request_fee", ref_id=pr.id)

    if reserve > 0:
        ledger_post(db, account="escrow", credit=reserve, debit=0.0, ref_type="paid_request_reserve", ref_id=pr.id)
        ledger_post(db, account="escrow_reserve", debit=reserve, credit=0.0, ref_type="paid_request_reserve", ref_id=pr.id)

    ledger_post(db, account="escrow", credit=net, debit=0.0, ref_type="paid_request_payout", ref_id=pr.id)
    ledger_post(db, account="creator_payable", debit=net, credit=0.0, ref_type="paid_request_payout", ref_id=pr.id)

    return {"request_id": pr.id, "status": pr.status, "gross": pr.amount, "fee": fee, "reserve": reserve, "net_to_creator": net}

# -------------------- Admin / AML helpers --------------------
@app.get("/admin/suspicious-donations")
def get_suspicious_donations(db: Session = Depends(get_db)):
    suspicious_events = db.query(models.SessionEvent).filter_by(status="under_review").all()
    return suspicious_events

@app.post("/admin/review-donation")
def review_donation(donation_id: int, action: str, db: Session = Depends(get_db)):
    donation = db.get(models.SessionEvent, donation_id)
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if action not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    donation.status = "approved" if action == "approve" else "rejected"
    db.commit()
    return {"message": f"Donation {action}d successfully"}
