import os, csv, json, numpy as np

def load_real_data(path="data/events.csv"):
    if not os.path.exists(path): return None
    X, y = [], []
    with open(path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            feats = json.loads(row["features_json"])
            X.append([float(v) for v in feats.values()])
            y.append(int(row["label"]))
    X = np.array(X, dtype=float); y = np.array(y, dtype=int)
    return X, y

def train_logreg_count_flops(X, y, epochs=30, lr=0.2):
    n, d = X.shape
    maj = 1 if y.mean() >= 0.5 else 0
    baseline = float((y == maj).mean())
    w = np.zeros(d); flops=0
    for _ in range(epochs):
        z = np.clip(X @ w, -500, 500); flops += 2*n*d
        p = 1/(1+np.exp(-z))
        err = p - y
        grad = X.T @ err / n; flops += 2*n*d
        w -= lr*grad; flops += 2*d
    z_final = np.clip(X@w, -500, 500)
    acc = float(((1/(1+np.exp(-z_final))>=0.5) == y).mean())
    imp = max(0.0, acc - baseline)
    return {"baseline_acc":baseline,"acc":acc,"improvement":imp,"flops":flops}

def real_or_synth(price_per_point=150.0, seed=42, epochs=30, lr=0.2):
    data = load_real_data()
    if data is None:
        rng = np.random.default_rng(seed)
        n, d = 5000, 50
        true_w = rng.normal(0,1,d); X = rng.normal(0,1,(n,d))
        y = (X@true_w + rng.normal(0,1.5,n) > 0).astype(int)
    else:
        X, y = data
    r = train_logreg_count_flops(X, y, epochs=epochs, lr=lr)
    value_eur = price_per_point * (r["improvement"]*100.0)
    r["value_eur"] = value_eur
    return r
