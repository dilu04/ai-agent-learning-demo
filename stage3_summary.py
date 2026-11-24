"""Stage 3: our first real Claude call, with NO tools and NO loop.

We fetch the data ourselves, paste it into the prompt, and ask Claude to
summarise it. Compare this with Stage 4, where Claude fetches the data itself.
"""
import json

from dotenv import load_dotenv
from anthropic import AnthropicAWS

import tools

load_dotenv()
client = AnthropicAWS()

# The system prompt gives Claude its role and rules. It is sent with every call.
SYSTEM_PROMPT = """You are a cloud operations analyst. You explain AWS Health events
to engineers and managers in clear, plain English.

Rules:
- Use only the data you are given. If something is missing, say so; never invent facts.
- Always say which accounts and resources are affected.
- Weigh impact by the account's environment and criticality (production matters more than development).
- Keep the answer under 200 words."""

# 1. WE choose the event and fetch all of its data.
event_arn = tools.list_health_events(service="EC2")[0]["arn"]
event = tools.get_event_details(event_arn)
resources = tools.get_affected_resources(event_arn)

# 2. WE paste that data into the user message.
user_message = f"""Please summarise this AWS Health event.

EVENT:
{json.dumps(event, indent=2)}

AFFECTED RESOURCES:
{json.dumps(resources, indent=2)}"""

# 3. Send it to Claude.
reply = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=800,
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": user_message}],
)

# 4. Show the answer, plus how many tokens we used (tokens = what you pay for).
print(reply.content[0].text)
print("\n--- stats ---")
print("stop_reason:", reply.stop_reason)
print("input tokens:", reply.usage.input_tokens, "| output tokens:", reply.usage.output_tokens)
