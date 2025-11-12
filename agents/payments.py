import os, requests

def stripe_capture(amount_usd: float, description: str):
    key = os.getenv("STRIPE_SECRET_TEST")
    if not key or amount_usd <= 0:
        print(f"[STRIPE] Skipped: key={bool(key)}, amount={amount_usd}")
        return None
    amount = int(round(amount_usd*100))
    print(f"[STRIPE] Requesting PaymentIntent: ${amount_usd} ({amount} cents)")

    r = requests.post(
        "https://api.stripe.com/v1/payment_intents",
        auth=(key, ""),
        data={"amount": amount, "currency":"usd", "payment_method_types[]":"card", "description": description, "confirm":"false"},
        timeout=10
    )

    print(f"[STRIPE] Status: {r.status_code}")

    if r.status_code != 200:
        print(f"[STRIPE] Error response: {r.text[:500]}")
        return None

    try:
        data = r.json()
        intent_id = data.get("id")
        print(f"[STRIPE] Success: {intent_id}")
        return intent_id
    except Exception as e:
        print(f"[STRIPE] Parse error: {e}")
        return None
