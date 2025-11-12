"""
Real LLM compute tracking via Anthropic API.
"""
import os


def llm_job(prompt: str, model="claude-3-haiku-20240307"):
    """
    Execute LLM job with real Anthropic API call.
    Returns dict with tokens, flops, and text response.

    FLOPs estimation: ~6 * layers * d_model^2 * tokens
    For Sonnet-class models (rough approximation):
    - layers: 48
    - d_model: 4096
    """
    try:
        from anthropic import Anthropic
    except ImportError:
        # Fallback if anthropic SDK not installed
        return {
            "tokens": 0,
            "flops": 0,
            "text": "[ERROR: anthropic SDK not installed]",
            "error": "SDK_MISSING"
        }

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {
            "tokens": 0,
            "flops": 0,
            "text": "[ERROR: ANTHROPIC_API_KEY not set]",
            "error": "NO_API_KEY"
        }

    try:
        client = Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=model,
            max_tokens=512,
            system="You are an expert data cleaner and analyst.",
            messages=[{"role": "user", "content": prompt}]
        )

        toks_in = msg.usage.input_tokens
        toks_out = msg.usage.output_tokens
        tokens = toks_in + toks_out

        # FLOPs estimation (order of magnitude)
        layers, d_model = 48, 4096
        flops = int(6 * layers * (d_model ** 2) * tokens)

        # Extract text
        text = msg.content[0].text if msg.content else ""

        return {
            "tokens": tokens,
            "tokens_in": toks_in,
            "tokens_out": toks_out,
            "flops": flops,
            "text": text,
            "model": model
        }

    except Exception as e:
        return {
            "tokens": 0,
            "flops": 0,
            "text": f"[ERROR: {str(e)}]",
            "error": str(e)
        }
