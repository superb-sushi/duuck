import pandas as pd
import numpy as np

np.random.seed(42)

# -----------------------------
# Parameters
# -----------------------------
num_samples = 1000000
fraud_ratio = 0.05   # ~5% fraud
num_fraud = int(num_samples * fraud_ratio)
num_legit = num_samples - num_fraud

# Generate IDs
viewer_ids = [f"viewer_{i}" for i in range(1, num_samples + 1)]
creator_ids = [f"creator_{np.random.randint(1, 50)}" for _ in range(num_samples)]
video_ids = [f"video_{np.random.randint(1, 100)}" for _ in range(num_samples)]

# -----------------------------
# Legitimate accounts (baseline distributions)
# -----------------------------
legit_data = {
    "viewer_id": viewer_ids[:num_legit],
    "creator_id": creator_ids[:num_legit],
    "video_id": video_ids[:num_legit],
    "seconds_watched": np.random.gamma(5, 600, num_legit).astype(int),
    "interactions": np.random.poisson(30, num_legit),
    "total_interactions": np.random.poisson(500, num_legit),
    "donation_amount": np.round(np.random.normal(2, 3, num_legit).clip(0, 500), 2),
    "total_donations": np.round(np.random.normal(50, 100, num_legit).clip(0, 5000), 2),
    "time_spent_on_app": np.random.gamma(5, 20, num_legit).astype(int),
    "account_age_days": np.random.exponential(400, num_legit).astype(int).clip(1, 2000),
    "target": [0] * num_legit
}

# -----------------------------
# Fraudulent accounts (baseline distributions)
# -----------------------------
fraud_data = {
    "viewer_id": viewer_ids[num_legit:],
    "creator_id": creator_ids[num_legit:],
    "video_id": video_ids[num_legit:],
    "seconds_watched": np.random.gamma(2, 200, num_fraud).astype(int),
    "interactions": np.random.poisson(5, num_fraud),
    "total_interactions": np.random.poisson(50, num_fraud),
    "donation_amount": np.round(np.random.normal(40, 40, num_fraud).clip(0, 500), 2),
    "total_donations": np.round(np.random.normal(500, 500, num_fraud).clip(0, 5000), 2),
    "time_spent_on_app": np.random.gamma(2, 10, num_fraud).astype(int),
    "account_age_days": np.random.exponential(100, num_fraud).astype(int).clip(1, 2000),
    "target": [1] * num_fraud
}

# Convert to DataFrames
legit_df = pd.DataFrame(legit_data)
fraud_df = pd.DataFrame(fraud_data)

# -----------------------------
# Add overlapping / confusing cases
# -----------------------------
def inject_overlap(df, label, frac=0.3):
    sample = df.sample(frac=frac, random_state=np.random.randint(10000)).copy()
    if label == 0:
        # Some legit users look suspicious (whales, low engagement)
        sample["donation_amount"] = np.round(np.random.uniform(50, 500, len(sample)), 2)
        sample["total_donations"] = np.round(np.random.uniform(500, 5000, len(sample)), 2)
        sample["interactions"] = np.random.randint(0, 10, len(sample))
        sample["time_spent_on_app"] = np.random.randint(1, 30, len(sample))
    else:
        # Some frauds look clean
        sample["donation_amount"] = np.round(np.random.uniform(0, 20, len(sample)), 2)
        sample["total_donations"] = np.round(np.random.uniform(0, 200, len(sample)), 2)
        sample["interactions"] = np.random.randint(50, 500, len(sample))
        sample["account_age_days"] = np.random.randint(200, 2000, len(sample))
    df.update(sample)
    return df

legit_df = inject_overlap(legit_df, label=0, frac=0.2)
fraud_df = inject_overlap(fraud_df, label=1, frac=0.2)

# -----------------------------
# Combine dataset
# -----------------------------
dataset = pd.concat([legit_df, fraud_df]).sample(frac=1, random_state=42).reset_index(drop=True)

# -----------------------------
# Add label noise (~5%)
# -----------------------------
flip_idx = dataset.sample(frac=0.05, random_state=42).index
dataset.loc[flip_idx, "target"] = 1 - dataset.loc[flip_idx, "target"]

# Save
dataset.to_csv("data/synthetic_fraud_dataset.csv", index=False)
print(f"Synthetic dataset generated: {dataset.shape[0]} rows, {dataset['target'].sum()} fraud cases (after noise)")
