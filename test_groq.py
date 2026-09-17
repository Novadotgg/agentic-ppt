"""Quick Groq API key + model validation test. Run with: python test_groq.py"""
import urllib.request
import json
import sys

# ── Paste your key here OR pass as first arg ──────────────────────────────────
KEY = sys.argv[1] if len(sys.argv) > 1 else ""

if not KEY:
    print("Usage: python test_groq.py gsk_YOUR_KEY_HERE")
    sys.exit(1)

KEY = KEY.strip()
print(f"Testing key: {KEY[:12]}...{KEY[-4:]}")

headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

# 1. List models (lightweight, no tokens consumed)
print("\n[1] Checking /v1/models ...")
req = urllib.request.Request("https://api.groq.com/openai/v1/models", headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        models = sorted(m["id"] for m in data.get("data", []))
        print(f"    Key is VALID. {len(models)} models available.")
        llama = [m for m in models if "llama" in m]
        print(f"    Llama models: {llama}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"    HTTP {e.code} {e.reason}: {body}")
    sys.exit(1)
except Exception as e:
    print(f"    Error: {type(e).__name__}: {e}")
    sys.exit(1)

# 2. Send a minimal chat completion (1 token output)
print("\n[2] Sending minimal chat completion ...")
payload = json.dumps({
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "Say hi."}],
    "max_tokens": 5,
}).encode()

req2 = urllib.request.Request(
    "https://api.groq.com/openai/v1/chat/completions",
    data=payload,
    headers=headers,
    method="POST",
)
try:
    with urllib.request.urlopen(req2, timeout=20) as resp:
        data = json.loads(resp.read())
        reply = data["choices"][0]["message"]["content"]
        print(f"    Model replied: {reply!r}")
        print("\n[OK] Everything works. The key and model are valid.")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"    HTTP {e.code} {e.reason}")
    print(f"    Body: {body}")
except Exception as e:
    print(f"    Error: {type(e).__name__}: {e}")
