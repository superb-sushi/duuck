
import hashlib
from typing import List, Tuple, Dict

def _h(x: bytes) -> bytes:
    return hashlib.sha256(x).digest()

def commit_from_meta(meta: Dict) -> str:
    parts = [
        str(meta.get("session_id","")),
        str(meta.get("video_id","")),
        str(meta.get("seconds_watched","")),
        str(meta.get("interactions","")),
        str(meta.get("nonce","")),
        str(meta.get("device_hash","")),
    ]
    payload = "|".join(parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def merkle_root(leaves_hex: List[str]) -> str:
    if not leaves_hex:
        return ""
    level = [bytes.fromhex(hx) for hx in leaves_hex]
    if len(level) == 1:
        return level[0].hex()
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            a = level[i]
            b = level[i+1] if i+1 < len(level) else level[i]
            nxt.append(_h(a + b))
        level = nxt
    return level[0].hex()

def merkle_proofs(leaves_hex: List[str]) -> List[List[Tuple[str, str]]]:
    if not leaves_hex:
        return []
    # Build layers with duplication of last when odd
    layers = [[bytes.fromhex(hx) for hx in leaves_hex]]
    while len(layers[-1]) > 1:
        cur = layers[-1]
        nxt = []
        for i in range(0, len(cur), 2):
            a = cur[i]
            b = cur[i+1] if i+1 < len(cur) else cur[i]
            nxt.append(_h(a + b))
        layers.append(nxt)

    n = len(leaves_hex)
    proofs: List[List[Tuple[str, str]]] = [[] for _ in range(n)]
    # Track positions per original leaf
    positions = list(range(n))
    for depth in range(len(layers) - 1):
        cur = layers[depth]
        # For each original leaf, compute its sibling at this depth using its current position
        new_positions = [0] * n
        for k in range(n):
            i = positions[k]
            sib_i = i + 1 if i % 2 == 0 else i - 1
            if sib_i >= len(cur):
                sib_i = i  # duplicate last
            sib = cur[sib_i]
            pos = 'R' if i % 2 == 0 else 'L'
            proofs[k].append((sib.hex(), pos))
            new_positions[k] = i // 2
        positions = new_positions
    return proofs

def verify_proof(leaf_hex: str, proof: List[Tuple[str, str]], root_hex: str) -> bool:
    node = bytes.fromhex(leaf_hex)
    for sib_hex, pos in proof:
        sib = bytes.fromhex(sib_hex)
        node = _h(node + sib) if pos == "R" else _h(sib + node)
    return node.hex() == root_hex
