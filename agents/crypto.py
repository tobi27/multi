import os, json, base64, hashlib

DISABLE = os.getenv("DISABLE_CRYPTO","false").lower()=="true"
try:
    from nacl.signing import SigningKey, VerifyKey
except Exception:
    SigningKey = VerifyKey = None

KEYFILE = ".agent_ed25519.json"

def load_or_create_keys():
    if DISABLE or SigningKey is None: return None, None
    if os.path.exists(KEYFILE):
        with open(KEYFILE,"r") as f: data = json.load(f)
        sk = SigningKey(base64.b64decode(data["sk_b64"]))
        vk = VerifyKey(base64.b64decode(data["vk_b64"]))
        return sk, vk
    sk = SigningKey.generate(); vk = sk.verify_key
    data = {"sk_b64": base64.b64encode(bytes(sk)).decode(), "vk_b64": base64.b64encode(bytes(vk)).decode()}
    with open(KEYFILE,"w") as f: json.dump(data,f)
    return sk, vk

def sha256_hex(obj)->str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()

def sign_ledger(ledger: dict):
    if DISABLE or SigningKey is None: return None, None
    sk, vk = load_or_create_keys()
    if not sk: return None, None
    digest = hashlib.sha256(json.dumps(ledger, sort_keys=True).encode()).digest()
    sig = sk.sign(digest).signature
    import base64 as b64
    return b64.b64encode(sig).decode(), b64.b64encode(bytes(vk)).decode()
