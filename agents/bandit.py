import math, os, random
class UCB:
    def __init__(self, beta: float=None):
        self.beta = float(beta or os.getenv("UCB_BETA","0.5"))
        self.n, self.mean = {}, {}
    def update(self, arm: str, reward: float):
        c = self.n.get(arm,0)+1; m = self.mean.get(arm,0.0)
        m = m + (reward - m)/c
        self.n[arm]=c; self.mean[arm]=m
    def score(self, arm: str, t: int):
        n_i = self.n.get(arm,0); mu = self.mean.get(arm,0.0)
        bonus = 0.0 if n_i==0 else self.beta*math.sqrt(2*math.log(max(t,1))/n_i)
        return (10.0 if n_i==0 else mu) + bonus

def gen_variants(base_prompt_len=200, base_epochs=30):
    rate = float(os.getenv("VARIATION_RATE","0.15"))
    def jitter(v, rate, lo, hi):
        dv = max(1, int(v*rate))
        return max(lo, min(hi, v + (dv if random.random()<0.5 else -dv)))
    return {
        "arm_A": {"prompt_len": base_prompt_len, "epochs": base_epochs},
        "arm_B": {"prompt_len": jitter(base_prompt_len, rate, 40, 2000), "epochs": base_epochs},
        "arm_C": {"prompt_len": base_prompt_len, "epochs": jitter(base_epochs, rate, 5, 100)},
        "arm_D": {"prompt_len": jitter(base_prompt_len, rate, 40, 2000), "epochs": jitter(base_epochs, rate, 5, 100)}
    }
