# Learner Guide: Building a Cloud Operations Agent with Claude

A hands-on demo of how an AI **agent** works. You ask a question in plain English;
Claude looks up AWS Health events by calling our own Python functions, explains the
impact, recommends fixes, and can write a management report.

Everything runs on **sample data**. No real AWS account is touched.

**Who this is for:** beginners to agentic AI and to Python. Read Part 1 to understand,
Part 2 to run it, Part 3 to study the code, Part 4 to experiment.

---

## Part 1: Understand it

### 1.1 What is an agent?

A chatbot answers from what it already knows. An **agent** can also *do things*
(look up data, call systems) and decide *for itself* which steps to take.

Claude cannot read your files or call anything by itself. It can only produce text.
So the trick is:

1. Claude replies **"please run this tool for me"** instead of a final answer.
2. **Our Python code** runs the tool and sends the result back.
3. Claude reads the result and either asks for another tool or writes the answer.

The code that repeats this is the **agent loop**. That loop, a model and a set of
tools are the whole idea behind almost every agent framework.

### 1.2 Architecture

```
┌────────────────────────────────────────────────────────────────┐
│ INTERFACES (how you talk to it)                                │
│  terminal: agent.py     web page: server.py + web/index.html   │
│  reports:  report.py                                           │
└───────────────────────────┬────────────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────────────┐
│ AGENT LOOP (agent.py → run_agent)                              │
│  keeps the conversation (messages) and repeats:                │
│  send → Claude replies → run tools if asked → send results     │
└──────────┬─────────────────────────────────────┬───────────────┘
           │ messages + system prompt + tool list│ tool requests
           ▼                                     ▼
┌──────────────────────────┐        ┌──────────────────────────────┐
│ CLAUDE (the brain)       │        │ TOOLS (our Python functions) │
│ reasons, picks tools,    │        │  tools.py                    │
│ writes the answer        │        │  tool_definitions.py (menu)  │
│ prompts.py = its rules   │        └───────────────┬──────────────┘
└──────────────────────────┘                        ▼
                                    ┌──────────────────────────────┐
                                    │ DATA (data/*.json)           │
                                    └──────────────────────────────┘
```

### 1.3 The flow, step by step

Question: *"What is affecting production right now?"*

1. `messages = [your question]`
2. Send `messages`, the system prompt and the tool menu to Claude.
3. Claude replies with a **tool request** (`stop_reason = "tool_use"`), e.g.
   `list_health_events(status="open")`.
4. **Our code** runs that function and wraps the output as a `tool_result`.
5. Append Claude's request **and** the result to `messages`, then go to step 2.
6. Claude keeps asking for tools (`get_event_details`, `get_affected_resources`,
   `get_account_info`, `get_remediation_playbook` ...) until it has enough.
7. Claude writes the final answer (`stop_reason = "end_turn"`). The loop returns it.

> **Claude never touches the data.** It only *asks*. Our code does the work.
> **Claude has no memory between calls.** The `messages` list *is* the memory,
> and the whole list is resent every round.

### 1.4 Key concepts

| Concept | Meaning | Where to see it |
|---|---|---|
| **System prompt** | Standing instructions: role, rules, output format | `prompts.py` |
| **Tool definition** | A description telling Claude what a tool does and what inputs it takes | `tool_definitions.py` |
| **Tool use** | Claude requests a function call; our code executes it | `agent.py` lines 41-59 |
| **`stop_reason`** | Why Claude stopped: `tool_use` (needs a tool), `end_turn` (finished), `max_tokens` (cut off) | `agent.py` |
| **Agent loop** | Send, check for tool requests, run them, repeat | `agent.py` |
| **Grounding** | Telling Claude to use only tool data and list unknowns reduces invented facts | `prompts.py` rules |
| **Domain knowledge as data** | The remediation playbook makes advice consistent | `data/remediation_playbook.json` |
| **Safety limit** | `MAX_STEPS` stops a runaway loop from spending money | `agent.py` |

---

## Part 2: Run it

### 2.1 Prerequisites
- **Python 3.12** (3.10+ should work).
- Access to Claude. This demo was built for **Claude Platform on AWS**
  (key, workspace ID and region from the AWS console). Short-lived keys last 12 hours.
- Windows PowerShell commands are shown; on macOS or Linux use
  `source .venv/bin/activate` and `python`.

### 2.2 Setup (once)

```powershell
# 1. Create a private library folder for this project
python -m venv .venv

# 2. Install the libraries
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. Create your settings file from the template, then edit it
Copy-Item .env.example .env
```

Open `.env` and fill in your key, workspace ID and region. **Never share `.env`**;
it is already listed in `.gitignore`. The full setup walk-through, with a table of
where to find each value, is in [README.md](README.md).

> Using the direct Anthropic API instead? Change `AnthropicAWS` to `Anthropic` in
> `agent.py` and `check_setup.py`, and put `ANTHROPIC_API_KEY=...` in `.env`.

### 2.3 Check that it works

```powershell
.\.venv\Scripts\python.exe check_setup.py
```
Expected: `Claude says: <a short greeting>`.

### 2.4 Use it

| What | Command |
|---|---|
| Ask the agent (terminal) | `.\.venv\Scripts\python.exe agent.py "What is affecting production right now?"` |
| Generate a management report | `.\.venv\Scripts\python.exe report.py` (saved to `reports/`) |
| Web page | `.\.venv\Scripts\python.exe server.py`, then open http://127.0.0.1:8000 |
| Test the data functions (no AI) | `.\.venv\Scripts\python.exe test_tools.py` |

Questions to try:
- `"Which events affect the dev sandbox account?"`
- `"Do any upcoming events cause database downtime? Who owns them?"`
- `"Review all open and upcoming events and tell me what needs attention, in priority order."`

> Use `.\.venv\Scripts\python.exe`, not plain `python`. Only the venv has the libraries.
> You will see `[step N] Claude calls ...` lines. That is the agent loop working.

### 2.5 Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `ModuleNotFoundError: No module named 'dotenv'` | You used plain `python`. Use `.\.venv\Scripts\python.exe`. |
| `Missing ANTHROPIC_AWS_API_KEY` | `.env` is missing or still has the placeholder. |
| Authentication error | Short-lived key expired. Generate a new one, update `.env`, restart. |
| Outbound web identity federation disabled | One-time AWS account setup is needed (`aws iam enable-outbound-web-identity-federation`). |
| Answer ends mid-sentence | `stop_reason` was `max_tokens`. Raise `max_tokens` in `agent.py`. |
| "Stopped: reached the step limit" | The loop hit `MAX_STEPS`. Simplify the question or raise the limit. |
| Web page won't load | Is `server.py` running? Port 8000 busy? |

---

## Part 3: Study the code

### 3.1 File map (read in this order)

| # | File | What it teaches |
|---|---|---|
| 1 | `data/*.json` | Realistic AWS Health data: events, affected resources, descriptions, account context, playbook |
| 2 | `tools.py` | Plain functions that read the data (no AI) |
| 3 | `test_tools.py` | Trying the functions on their own |
| 4 | `check_setup.py` | The smallest possible Claude call |
| 5 | `stage3_summary.py` | One Claude call where **we** paste the data into the prompt |
| 6 | `tool_definitions.py` | The tool menu Claude sees |
| 7 | **`agent.py`** | **The agent loop. Read this one slowly.** |
| 8 | `prompts.py` | System prompts: analyst and management report |
| 9 | `report.py` | Same agent, different prompt, saved as Markdown and HTML |
| 10 | `server.py`, `web/index.html` | A local web page in front of the agent |


### 3.2 The data files

| File | Content |
|---|---|
| `health_events.json` | 6 events: EC2 retirement, RDS maintenance, Lambda outage, exposed key, runtime deprecation, one closed event |
| `affected_entities.json` | The specific resources and accounts hit by each event |
| `event_descriptions.json` | AWS-style description text per event |
| `accounts.json` | **Our own business context**: owner, environment, criticality. AWS does not know your prod from your dev. |
| `remediation_playbook.json` | Standard fix steps per event type |

The data is deliberately tricky: the same EC2 event hits production *and* dev
resources; the exposed key has a harmless-looking status but is the most urgent item;
one event is closed and should be ignored. Good agents rank these correctly.

### 3.3 The tools (`tools.py`)

| Function | Answers |
|---|---|
| `list_health_events(status, category, service)` | What events exist? |
| `get_event_details(event_arn)` | What exactly is this event? |
| `get_affected_resources(event_arn)` | Which resources and accounts are hit? |
| `get_account_info(account_id)` | Who owns this account and how critical is it? |
| `get_events_for_account(account_id)` | What affects this account? |
| `get_remediation_playbook(event_type_code)` | What are our standard fix steps? |

Design choices worth copying:
- Functions return plain dicts and lists, which convert cleanly to JSON text.
- Errors come back as data (`{"error": "..."}`), so Claude can read them and recover.
- Data loading lives in one helper, `_load()`. To use real AWS later, only that
  part changes.

### 3.4 The agent loop (`agent.py`), line by line

```python
messages = [{"role": "user", "content": question}]   # the memory
for step in range(MAX_STEPS):                        # safety limit
    response = client.messages.create(...)           # 1. ask Claude
    if response.stop_reason != "tool_use":           # 2. finished?
        return the text
    messages.append({"role": "assistant", ...})      # 3. remember Claude's request
    for block in response.content:
        if block.type == "tool_use":
            result = TOOL_FUNCTIONS[block.name](**block.input)   # run OUR function
            tool_results.append({... "tool_use_id": block.id ...})
    messages.append({"role": "user", "content": tool_results})   # 4. send results back
```

The line that makes it an agent: `TOOL_FUNCTIONS[block.name](**block.input)`. It looks up
the function Claude named and runs it with the inputs Claude chose.
`tool_use_id` matches each result to its request, which matters when Claude asks for
several tools at once. `try/except` turns a crashing tool into an error message
Claude can read.

### 3.5 Prompts (`prompts.py`)

The system prompt is the main lever on quality. Ours sets:
- a **role** (cloud operations analyst);
- **rules** ("use only tool data", "list unknowns under To verify");
- the **current time** (Claude cannot know it, so we tell it);
- a **fixed report format** and a **severity guide**.

The management report uses the same facts and tools with a different prompt
(plain business language, six fixed sections).

---

## Part 4: Experiments

Try these. Each takes a few minutes and teaches something real.

1. **Watch the memory grow.** In `agent.py`, add `print(len(messages))` at the top of
   the loop. See it increase each round.
2. **Trigger the safety brake.** Set `MAX_STEPS = 2`, ask a big question, read the message.
3. **Break the answer.** Set `max_tokens=200` and observe `stop_reason == "max_tokens"`.
4. **Change the behaviour with words only.** Edit a rule in `prompts.py` (for example
   "write in one paragraph") and compare answers. No code change needed.
5. **Add a tool.** Write `count_events_by_service()` in `tools.py`, add its definition in
   `tool_definitions.py` and its name in `TOOL_FUNCTIONS`. Ask "How many events per service?"
6. **Add your own event.** Edit the JSON files with an event you invent and see how the
   agent handles it. Does it rate severity sensibly?
7. **Remove a rule** (for example "never invent facts") and see whether answers get worse.
8. **Hide a tool.** Delete `get_remediation_playbook` from the menu and see how the
   recommendations change.

---

## Part 5: What this demo does NOT do (read before using it for real)

- **Not connected to real AWS.** Real use needs the AWS Health API via read-only
  `boto3` calls (needs a Business or Enterprise support plan), a read-only IAM role,
  the real clock (`USE_FIXED_NOW = False` in `prompts.py`), and a source for the
  account business context.
- **The clock is pinned** to 2026-11-10 09:00 UTC because the sample data is set then.
- **Results vary between runs.** Severity ratings can differ slightly. Verify output
  before acting on it.
- **No memory between questions** and **no login.** The web page is local-only
  (`127.0.0.1`). Do not expose it to a network without authentication, since it spends
  your API credits and shows account details.
- **Data leaves your machine** to reach Claude. Check your company policy before
  using real data.
- Keys: keep them in `.env`, set spend limits or an AWS Budget alert, and never paste
  keys into chats or commit them.

## Part 6: Where to go next

1. Real AWS Health data (see Part 5).
2. Scheduled weekly reports by email or chat message.
3. A small set of test questions with known correct answers, to catch regressions when
   you change prompts.
4. Authentication, a long-lived credential and a spend limit before sharing.

## Glossary

| Term | Plain meaning |
|---|---|
| **LLM** | The language model (Claude) |
| **Agent** | An LLM that can call tools and decide its own steps |
| **Tool** | A function the agent may ask us to run |
| **Token** | A piece of text (about 3/4 of a word); what you are billed for |
| **System prompt** | Standing instructions sent with every call |
| **ARN** | A unique ID for an AWS resource or event |
| **Health event** | An AWS notice about an issue, scheduled change or account notification |
| **Single-AZ / Multi-AZ** | One data-centre zone vs. a standby copy in another |
| **Venv** | A private folder of libraries for one project |
