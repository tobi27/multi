import os, requests

def stripe_capture(amount_eur: float, description: str):
    key = os.getenv("STRIPE_SECRET_TEST")
    if not key or amount_eur <= 0: return None
    amount = int(round(amount_eur*100))
    r = requests.post(
        "https://api.stripe.com/v1/payment_intents",
        auth=(key, ""),
        data={"amount": amount, "currency":"eur", "payment_method_types[]":"card", "description": description, "confirm":"false"},
        timeout=10
    )
    try:
        return r.json().get("id")
    except Exception:
        return None
