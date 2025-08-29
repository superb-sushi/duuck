# Fair Allocation Engine: Shapley-style approximation with quadratic matching

from typing import List, Dict
import random
import math

# event: {video_id, creator_id, donation_amount}
def allocate(events: List[Dict], viewer_budget: float, platform_match_pool: float = 0.0, K: int = 25):
    if not events:
        return []

    videos = list(range(len(events)))

    def S(subset_idx):
        # simple surrogate: sqrt(sum boosts)
        if not subset_idx:
            return 0.0
        sum_b = sum(events[i]["donation_amount"] for i in subset_idx)
        return math.sqrt(max(0.0, sum_b))

    shapley = [0.0] * len(events)
    for _ in range(K):
        perm = videos[:]
        random.shuffle(perm)
        acc = []
        prev = 0.0
        for v in perm:
            acc.append(v)
            cur = S(acc)
            shapley[v] += (cur - prev)
            prev = cur

    # normalize
    total = sum(shapley)
    if total <= 0:
        weights = [1.0 / len(events)] * len(events)
    else:
        weights = [s / total for s in shapley]

    # quadratic matching: distribute some pool proportionally to sqrt of small weights
    if platform_match_pool > 0:
        sqrtw = [math.sqrt(w) for w in weights]
        sw = sum(sqrtw)
        match = [platform_match_pool * (s / sw) if sw > 0 else 0 for s in sqrtw]
    else:
        match = [0.0] * len(events)

    # final dollar allocation: viewer_budget * weights + match
    allocations = [viewer_budget * w + m for w, m in zip(weights, match)]

    return [
        {
            "video_id": events[i]["video_id"],
            "creator_id": events[i]["creator_id"],
            "weight": weights[i],
            "amount": allocations[i],
            "components": {
                "donation": events[i]["donation_amount"],
            },
        }
        for i in range(len(events))
    ]