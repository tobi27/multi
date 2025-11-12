import os
from anthropic import Anthropic

def llm_job(prompt:str, model:str="claude-3-haiku-20240307", token_cap:int|None=None):
    api = os.getenv("ANTHROPIC_API_KEY")
    if not api: return None
    max_tokens = 512 if token_cap is None else max(64, min(512, token_cap//2))
    client = Anthropic(api_key=api)
    msg = client.messages.create(
        model=model,
        system="You clean and normalize tabular data to a strict schema.",
        max_tokens=max_tokens,
        messages=[{"role":"user","content":prompt}]
    )
    usage = getattr(msg, "usage", None)
    tokens = (usage.input_tokens if usage else 0) + (usage.output_tokens if usage else 0)
    L, d = 48, 4096
    flops = int(6 * L * (d**2) * max(tokens,1))
    return {"text": msg.content[0].text, "tokens": tokens, "flops": flops, "usage_id": getattr(msg,"id", None)}
