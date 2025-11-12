"""
Real payment flow tracking via Stripe API (test mode).
"""
import os


def stripe_capture(amount_eur: float, description: str):
    """
    Create a PaymentIntent in Stripe test mode to track revenue.
    Returns the PaymentIntent object or error dict.

    Note: This creates an intent in test mode (no real money).
    The intent ID serves as proof of the transaction flow.
    """
    stripe_key = os.getenv("STRIPE_SECRET_TEST")

    if not stripe_key:
        return {
            "error": "NO_STRIPE_KEY",
            "message": "STRIPE_SECRET_TEST env var not set",
            "amount_eur": amount_eur,
            "description": description
        }

    if amount_eur <= 0:
        return {
            "error": "INVALID_AMOUNT",
            "message": "Amount must be positive",
            "amount_eur": amount_eur
        }

    try:
        import requests

        # Convert EUR to cents
        amount_cents = int(round(amount_eur * 100))

        # Create PaymentIntent
        response = requests.post(
            "https://api.stripe.com/v1/payment_intents",
            auth=(stripe_key, ""),
            data={
                "amount": amount_cents,
                "currency": "eur",
                "payment_method_types[]": "card",
                "description": description,
                "confirm": "false"
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "intent_id": data.get("id"),
                "amount_eur": amount_eur,
                "amount_cents": amount_cents,
                "currency": "eur",
                "description": description,
                "status": data.get("status"),
                "created": data.get("created")
            }
        else:
            return {
                "error": "STRIPE_API_ERROR",
                "status_code": response.status_code,
                "message": response.text[:200],
                "amount_eur": amount_eur
            }

    except ImportError:
        return {
            "error": "REQUESTS_NOT_INSTALLED",
            "message": "requests library not available",
            "amount_eur": amount_eur
        }
    except Exception as e:
        return {
            "error": "EXCEPTION",
            "message": str(e),
            "amount_eur": amount_eur
        }


def stripe_capture_safe(amount_eur: float, description: str):
    """
    Safe wrapper that doesn't raise exceptions.
    Returns (success: bool, result: dict).
    """
    result = stripe_capture(amount_eur, description)

    if result.get("success"):
        return True, result
    else:
        return False, result
