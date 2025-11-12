import math, os, statistics

def softmax(xs):
    m = max(xs) if xs else 0.0
    exps = [math.exp(x - m) for x in xs]; s = sum(exps) or 1.0
    return [e/s for e in exps]

def fitness(state):
    cc = max(state.compute_cost_usd, 1e-9)
    trust_mult = 0.8 + (state.trust_score/1000.0)*0.4
    return (state.agdp_usd/cc) * trust_mult  # ≈ CRI pondéré Trust

def thermostat_adjust(env_vars, cohort_states):
    target_cri = float(env_vars.get("DE_TARGET_CRI","1.30"))
    target_p95_net = float(env_vars.get("DE_TARGET_P95_NET","0.0"))
    price_up = float(env_vars.get("DE_PRICE_STEP_UP","0.10"))
    cov_down = float(env_vars.get("DE_COVERAGE_STEP_DOWN","0.10"))
    cov_floor = float(env_vars.get("DE_COVERAGE_FLOOR","0.30"))
    nets = [s.agent_net_usd for s in cohort_states]
    cris = [s.cri for s in cohort_states if s.cri is not None]
    p95_net = sorted(nets)[int(0.95*len(nets))-1] if len(nets)>=2 else (nets[0] if nets else 0.0)
    p50_cri = statistics.median(cris) if cris else 0.0
    actions = []
    if p50_cri < target_cri: actions.append(("PRICE_PER_POINT","up",price_up))
    if p95_net <= target_p95_net: actions.append(("COVERAGE","down",cov_down,cov_floor))
    return actions, {"p95_net":p95_net, "p50_cri":p50_cri}

def apply_thermostat(env, actions):
    changed={}
    if not actions: return changed
    if any(a[0]=="PRICE_PER_POINT" for a in actions):
        old = float(env.get("PRICE_PER_POINT","150"))
        new = round(old*(1+next(v for k,d,v in actions if k=="PRICE_PER_POINT")),2)
        os.environ["PRICE_PER_POINT"]=str(new); changed["PRICE_PER_POINT"]=(old,new)
    for a in actions:
        if a[0]=="COVERAGE":
            _,_,step,floor = a
            old = float(env.get("COVERAGE","0.70"))
            new = max(floor, round(old*(1-step),2))
            os.environ["COVERAGE"]=str(new); changed["COVERAGE"]=(old,new)
    return changed

def allocate_tokens(fits, total, amin, amax):
    if not fits: return []
    w = softmax(fits)
    raw = [max(amin, min(amax, round(total*wi))) for wi in w]
    diff = total - sum(raw); i=0
    while diff != 0 and raw:
        step = 1 if diff>0 else -1
        if (step>0 and raw[i] < amax) or (step<0 and raw[i] > amin):
            raw[i]+=step; diff-=step
        i=(i+1)%len(raw)
    return raw
