# Simple Merkle tree utilities for APR commitments (sha256 hex strings)

import hashlib
from typing import List, Tuple

def _h(x: bytes) -> bytes:
    return hashlib.sha256(x).digest()

def merkle_root(leaves_hex: List[str]) -> str:
    if not leaves_hex:
        return ""
    level = [bytes.fromhex(hx) for hx in leaves_hex]
    if len(level) == 1:
        return level[0].hex()
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i+1] if i+1 < len(level) else left
            nxt.append(_h(left + right))
        level = nxt
    return level[0].hex()

def merkle_proofs(leaves_hex: List[str]) -> List[List[Tuple[str, str]]]:
    # Returns for each leaf an array of (sibling_hex, position) where position in {"L","R"}
    if not leaves_hex:
        return []
    layers = [[bytes.fromhex(hx) for hx in leaves_hex]]
    while len(layers[-1]) > 1:
        cur = layers[-1]
        nxt = []
        for i in range(0, len(cur), 2):
            left = cur[i]
            right = cur[i+1] if i+1 < len(cur) else left
            nxt.append(_h(left + right))
        layers.append(nxt)
    proofs = [[] for _ in leaves_hex]
    for depth in range(len(layers) - 1):
        cur = layers[depth]
        for i in range(len(cur)):
            sib_i = i + 1 if i % 2 == 0 else i - 1
            sib = cur[sib_i] if sib_i < len(cur) else cur[i]
            pos = "R" if i % 2 == 0 else "L"
            proofs[i].append((sib.hex(), pos))
    return proofs

def verify_proof(leaf_hex: str, proof: List[Tuple[str, str]], root_hex: str) -> bool:
    node = bytes.fromhex(leaf_hex)
    for sib_hex, pos in proof:
        sib = bytes.fromhex(sib_hex)
        node = _h(node + sib) if pos == "R" else _h(sib + node)
    return node.hex() == root_hex