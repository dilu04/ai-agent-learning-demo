"""Stage 4, part 2: the agent loop.

Claude decides which tools to call. Our code runs them and sends the results back,
repeating until Claude gives a final answer.
"""
import json
import sys

from dotenv import load_dotenv
from anthropic import AnthropicAWS

from prompts import build_system_prompt
from tool_definitions import TOOL_DEFINITIONS, TOOL_FUNCTIONS

load_dotenv()
client = AnthropicAWS()

MAX_STEPS = 15  # safety limit so a mistake can never loop (and spend money) forever


def run_agent(question, system_prompt=None, on_tool_call=None):
    # Use the default analyst prompt unless the caller supplies another one.
    system_prompt = system_prompt or build_system_prompt()
    # The conversation so far. This list is the agent's memory.
    messages = [{"role": "user", "content": question}]

    for step in range(MAX_STEPS):
        # 1. Send the conversation and the tool list to Claude.
        response = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=6000,
            system=system_prompt,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        # 2. Final answer? Return the text.
        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        # 3. Otherwise Claude asked for one or more tools.
        # Remember Claude's request in the conversation.
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"[step {step + 1}] Claude calls {block.name}({json.dumps(block.input)})")
                if on_tool_call:  # lets a caller (like the web page) collect the tool calls
                    on_tool_call(step + 1, block.name, block.input)
                try:
                    result = TOOL_FUNCTIONS[block.name](**block.input)  # run OUR function
                except Exception as error:  # report the problem to Claude instead of crashing
                    result = {"error": str(error)}
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,  # links the result to the request
                    "content": json.dumps(result),
                })

        # 4. Send the results back as a user message, then loop again.
        messages.append({"role": "user", "content": tool_results})

    return "Stopped: reached the step limit without a final answer."


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What is affecting production right now?"
    print(f"Question: {question}\n")
    print("\n" + run_agent(question))
