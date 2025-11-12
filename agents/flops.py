"""
FLOPs computation with real data support.
"""
import os
import csv
import json
import numpy as np


def load_real_data(path="data/events.csv"):
    """
    Load real data from CSV file.
    Expected columns: event_id, timestamp, features_json, label
    Returns: (X, y) as numpy arrays, or None if file not found
    """
    if not os.path.exists(path):
        return None

    X, y = [], []
    with open(path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            feats = json.loads(row["features_json"])
            X.append([float(v) for v in feats.values()])
            y.append(int(row["label"]))

    X = np.array(X, dtype=float)
    y = np.array(y, dtype=int)
    return X, y


def train_logreg_count_flops_real(price_per_point=150.0, seed=42, epochs=30, lr=0.2):
    """
    Train logistic regression on REAL data and count FLOPs.
    Returns dict with baseline_acc, acc, improvement, flops, value_eur.
    Returns None if no real data available (fallback to synthetic).
    """
    data = load_real_data()
    if data is None:
        return None

    X, y = data
    n, d = X.shape

    # Baseline = majority class
    majority = 1 if y.mean() >= 0.5 else 0
    baseline_acc = float((y == majority).mean())

    # Train logistic regression
    np.random.seed(seed)
    w = np.zeros(d)
    flops = 0

    for _ in range(epochs):
        # Forward pass
        z = X @ w
        flops += 2 * n * d

        # Sigmoid (clip to avoid overflow)
        z = np.clip(z, -500, 500)
        p = 1 / (1 + np.exp(-z))

        # Gradient
        err = p - y
        grad = X.T @ err / n
        flops += 2 * n * d

        # Update
        w -= lr * grad
        flops += 2 * d

    # Final accuracy
    z_final = np.clip(X @ w, -500, 500)
    predictions = (1 / (1 + np.exp(-z_final))) >= 0.5
    acc = float((predictions == y).mean())

    # Improvement
    improvement = max(0.0, acc - baseline_acc)

    # Value in EUR
    value_eur = price_per_point * (improvement * 100.0)

    return {
        "baseline_acc": baseline_acc,
        "acc": acc,
        "improvement": improvement,
        "flops": flops,
        "value_eur": value_eur,
        "n_samples": n,
        "n_features": d
    }


def train_logreg_count_flops(n=200, d=4, price_per_point=150.0, seed=42, epochs=30, lr=0.2):
    """
    Fallback: synthetic data logistic regression with FLOPs counting.
    """
    np.random.seed(seed)

    # Generate synthetic data
    X = np.random.randn(n, d)
    true_w = np.random.randn(d)
    probs = 1 / (1 + np.exp(-(X @ true_w)))
    y = (probs + 0.1 * np.random.randn(n) > 0.5).astype(int)

    # Baseline = majority
    majority = 1 if y.mean() >= 0.5 else 0
    baseline_acc = float((y == majority).mean())

    # Train
    w = np.zeros(d)
    flops = 0

    for _ in range(epochs):
        z = np.clip(X @ w, -500, 500)
        flops += 2 * n * d
        p = 1 / (1 + np.exp(-z))
        err = p - y
        grad = X.T @ err / n
        flops += 2 * n * d
        w -= lr * grad
        flops += 2 * d

    z_final = np.clip(X @ w, -500, 500)
    predictions = (1 / (1 + np.exp(-z_final))) >= 0.5
    acc = float((predictions == y).mean())
    improvement = max(0.0, acc - baseline_acc)

    return {
        "baseline_acc": baseline_acc,
        "acc": acc,
        "improvement": improvement,
        "flops": flops,
        "n_samples": n,
        "n_features": d
    }
