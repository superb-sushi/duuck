from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
from .db import Base, engine, get_db
from . import models, schemas
from .ledger import post as ledger_post
from .risk import viewer_ok, creator_reserve_pct
# Changed the 3 imports below too - Daniel
from engine.cqscore import compute as cq_compute
from engine.fae import allocate
from engine.merkle import merkle_root, merkle_proofs, verify_proof

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Duuck API")

@app.post("/viewer/create")
def create_viewer(v: schemas.ViewerCreate, db: Session = Depends(get_db)):
    viewer = models.Viewer(name=v.name, weekly_budget=v.weekly_budget, kyc_level="basic", device_attested=True)
    db.add(viewer); db.commit(); db.refresh(viewer)
    return {"id": viewer.id}

@app.post("/creator/create")
def create_creator(c: schemas.CreatorCreate, db: Session = Depends(get_db)):
    cr = models.Creator(handle=c.handle, risk_tier="low", reserve_pct=0.1)
    db.add(cr); db.commit(); db.refresh(cr)
    return {"id": cr.id}

@app.post("/video/create")
def create_video(v: schemas.VideoCreate, db: Session = Depends(get_db)):
    vid = models.Video(creator_id=v.creator_id, title=v.title, phash=v.phash, c2pa_status=v.c2pa_status)
    db.add(vid); db.commit(); db.refresh(vid)
    return {"id": vid.id}

@app.post("/session/start")
def session_start(s: schemas.SessionStart, db: Session = Depends(get_db)):
    if not viewer_ok(db, s.viewer_id):
        return {"error": "viewer not allowed"}
    ses = models.Session(viewer_id=s.viewer_id)
    db.add(ses); db.commit(); db.refresh(ses)
    return {"session_id": ses.id}

@app.post("/session/event")
def session_event(ev: schemas.SessionEventIn, db: Session = Depends(get_db)):
    video = db.get(models.Video, ev.video_id)
    cq = cq_compute(ev.seconds_watched, ev.interactions, video)
    e = models.SessionEvent(session_id=ev.session_id, video_id=ev.video_id, seconds_watched=ev.seconds_watched, interactions=ev.interactions, boost_amount=ev.boost_amount, cqscore=cq)
    db.add(e); db.commit()
    if ev.boost_amount and ev.boost_amount > 0:
        db.add(models.Boost(viewer_id=db.get(models.Session, ev.session_id).viewer_id, video_id=ev.video_id, amount=ev.boost_amount))
        db.commit()
    ledger_post(db, account="escrow", debit=ev.boost_amount, credit=0.0, ref_type="boost", ref_id=e.id)
    return {"event_id": e.id, "cqscore": cq}

@app.post("/session/close")
def session_close(session_id: int, platform_match_pool: float = 0.5, db: Session = Depends(get_db)):
    ses = db.get(models.Session, session_id)
    ses.ended_at = datetime.utcnow(); db.commit()
    viewer = db.get(models.Viewer, ses.viewer_id)
    events = db.query(models.SessionEvent).filter_by(session_id=session_id).all()
    evt_payload = []
    for e in events:
        vid = db.get(models.Video, e.video_id)
        evt_payload.append({
            "video_id": vid.id,
            "creator_id": vid.creator_id,
            "cqscore": e.cqscore,
            "boost_amount": e.boost_amount,
        })
    allocs = allocate(evt_payload, viewer.weekly_budget/7.0, platform_match_pool=platform_match_pool, K=25)
    breakdown = []
    total = 0.0
    for a in allocs:
        amount = round(a["amount"], 2)
        total += amount
        resv = creator_reserve_pct(db, a["creator_id"]) * amount
        # ledger: move from escrow to creator payable (with reserve to platform_pool for safety)
        ledger_post(db, account="escrow", debit=0.0, credit=amount, ref_type="allocation", ref_id=session_id)
        ledger_post(db, account="creator_payable", debit=amount - resv, credit=0.0, ref_type="allocation", ref_id=session_id)
        ledger_post(db, account="platform_pool", debit=resv, credit=0.0, ref_type="reserve", ref_id=session_id)
        db.add(models.Allocation(session_id=session_id, creator_id=a["creator_id"], weight=a["weight"], amount=amount, components=a["components"]))
        breakdown.append({
            "creator_id": a["creator_id"],
            "video_id": a["video_id"],
            "amount": amount,
            "weight": round(a["weight"], 4),
            "explain": a["components"],
        })
    db.commit()
    return {"session_id": session_id, "breakdown": breakdown, "total_spent": round(total, 2)}

# --------- APR + Merkle‑FairSplit (Innovation) ---------

@app.post("/apr/commit")
def apr_commit(apr: schemas.APRIn, db: Session = Depends(get_db)):
    payload = f"{apr.session_id}|{apr.video_id}|{apr.seconds_watched}|{apr.nonce}".encode()
    digest = hashlib.sha256(payload).hexdigest()
    db.add(models.APRCommitment(window=apr.window, commitment=digest, meta={"session_id": apr.session_id, "video_id": apr.video_id}))
    db.commit()
    return {"commitment": digest}

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
        mr.root = root; mr.leaves_count = len(leaves)
    db.commit()
    return {"window": window, "root": root, "count": len(leaves)}

@app.get("/apr/proofs")
def apr_proofs(window: str, db: Session = Depends(get_db)):
    commits = db.query(models.APRCommitment).filter_by(window=window).all()
    leaves = [c.commitment for c in commits]
    proofs = merkle_proofs(leaves)
    out = []
    for i, c in enumerate(commits):
        out.append({"commitment": c.commitment, "proof": proofs[i]})
    return {"window": window, "root": merkle_root(leaves), "proofs": out}

@app.post("/apr/verify")
def apr_verify(window: str, commitment: str, proof: list, db: Session = Depends(get_db)):
    mr = db.query(models.MerkleRoot).filter_by(window=window).first()
    if not mr:
        return {"ok": False, "error": "no root"}
    ok = verify_proof(commitment, proof, mr.root)
    return {"ok": ok, "root": mr.root}