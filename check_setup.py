"""Stage 0 check: confirms Python, the anthropic library and your AWS key work."""
import os

from dotenv import load_dotenv  # reads the .env file into environment variables
from anthropic import AnthropicAWS

load_dotenv()

# The client reads these three values from the environment automatically.
for name in ("ANTHROPIC_AWS_API_KEY", "ANTHROPIC_AWS_WORKSPACE_ID", "AWS_REGION"):
    value = os.getenv(name, "")
    if not value or "paste-your" in value:
        print(f"Missing {name}. Open .env and fill it in.")
        raise SystemExit(1)

client = AnthropicAWS()  # uses the key, workspace ID and region from .env
reply = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=50,
    messages=[{"role": "user", "content": "Say hello in five words."}],
)
print("Claude says:", reply.content[0].text)
