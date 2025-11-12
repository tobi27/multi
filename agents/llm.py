import os
from anthropic import Anthropic

def llm_job(prompt:str, model:str="claude-3-haiku-20240307"):
    api = os.getenv("ANTHROPIC_API_KEY")
    if not api: return None
    client = Anthropic(api_key=api)
    msg = client.messages.create(
        model=model,
        system="You clean and normalize tabular data to a strict schema.",
        max_tokens=512,
        messages=[{"role":"user","content":prompt}]
    )
    usage = getattr(msg, "usage", None)
    tokens = (usage.input_tokens if usage else 0) + (usage.output_tokens if usage else 0)
    L, d = 48, 4096
    flops = int(6 * L * (d**2) * max(tokens,1))
    return {"text": msg.content[0].text, "tokens": tokens, "flops": flops, "usage_id": getattr(msg,"id", None)}
