# Cloud Operations Agent (AWS Health demo)

A small, beginner-friendly AI agent built with Claude. Ask a question in plain English
and it investigates **sample** AWS Health events, explains the impact, recommends fixes
and can write a management report. It uses fake data only: no real AWS account is touched.

New to agents? After you get it running, read **[LEARNER_GUIDE.md](LEARNER_GUIDE.md)**.
It explains the architecture, the agent loop and the code, and has exercises.

## What you need
- **Windows with PowerShell** (macOS/Linux users: see the note at the end of step 2).
- **Python 3.10 or newer** (built with 3.12). Check with `python --version`. Install it from python.org and tick **"Add python.exe to PATH"**.
- **Claude Platform on AWS access:** an API key, a workspace ID and a region.

## Quick start

### 1. Get the project
Copy this folder to your computer (or clone the repository), then open PowerShell **inside the folder**.

### 2. Install
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
The first command creates a private library folder (`.venv`) for this project. The second installs the libraries into it.

> macOS/Linux: use `python3 -m venv .venv`, then `.venv/bin/python -m pip install -r requirements.txt`, and replace `.\.venv\Scripts\python.exe` with `.venv/bin/python` in every command below.

### 3. Create your `.env` file (your secret settings)
The program reads your credentials from a file named **`.env`**. It is deliberately **not** included in the project, because it holds a secret. A template is provided: **[`.env.example`](.env.example)**.

```powershell
Copy-Item .env.example .env
```
Open `.env` in any text editor (Notepad is fine) and replace the three placeholders:

| Setting | What to put | Where to find it |
|---|---|---|
| `ANTHROPIC_AWS_API_KEY` | Your API key | AWS Console → Claude Platform on AWS → API keys → Generate a key |
| `ANTHROPIC_AWS_WORKSPACE_ID` | Starts with `wrkspc_` | The Claude Platform on AWS area of the AWS Console |
| `AWS_REGION` | e.g. `us-west-2` | The region your workspace was created in |

Rules for `.env`:
- No quotes and no spaces around `=` (correct: `AWS_REGION=us-west-2`).
- **Never share it, email it, paste it into a chat, or commit it to git.** The included `.gitignore` already excludes it.
- Short-lived keys last 12 hours. If you later see an authentication error, generate a new key, paste it into `.env`, and restart the program.
- Keys made at console.anthropic.com do **not** work with Claude Platform on AWS.
- Using the direct Anthropic API instead? In `agent.py` and `check_setup.py` change `AnthropicAWS` to `Anthropic`, and put `ANTHROPIC_API_KEY=...` in `.env`.

### 4. Check the setup
```powershell
.\.venv\Scripts\python.exe check_setup.py
```
You should see `Claude says: ...` followed by a short greeting. If you get an error, see **Troubleshooting** below.

### 5. Use the agent
```powershell
# Ask a question
.\.venv\Scripts\python.exe agent.py "What is affecting production right now?"

# Generate a management report (saved in the reports folder)
.\.venv\Scripts\python.exe report.py

# Open the local web page, then browse to http://127.0.0.1:8000
.\.venv\Scripts\python.exe server.py
```
Always use `.\.venv\Scripts\python.exe` (not plain `python`): only the `.venv` has the libraries installed.

## Project layout

| Path | Purpose |
|---|---|
| `agent.py` | **The agent loop**, the heart of the project |
| `tools.py`, `tool_definitions.py` | The functions Claude can ask us to run, and the menu describing them |
| `prompts.py` | Claude's instructions (analyst and management-report prompts) |
| `report.py` | Writes the management report (Markdown + HTML) |
| `server.py`, `web/index.html` | Local web page |
| `check_setup.py`, `test_tools.py`, `stage3_summary.py` | Setup check, tool tests, a first one-shot Claude call |
| `data/` | The sample AWS Health data |
| `.env.example` | Template for your secret settings (copy to `.env`) |
| `requirements.txt` | The libraries to install |
| `LEARNER_GUIDE.md` | The learning guide |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'dotenv'` | You used plain `python`. Use `.\.venv\Scripts\python.exe`. |
| `Missing ANTHROPIC_AWS_API_KEY ...` | `.env` is missing, in the wrong folder, or still has the placeholder text. |
| Authentication or 401/403 error | Key expired (12 hours) or copied incompletely. Generate a new one and update `.env`. |
| Permission error mentioning `CallWithBearerToken` | Your AWS identity needs the `aws-external-anthropic:CallWithBearerToken` permission. |
| "Outbound web identity federation is disabled" | A one-time AWS account setting is needed (`aws iam enable-outbound-web-identity-federation`). Ask your AWS administrator. |
| Wrong region or workspace error | `AWS_REGION` must match the region your workspace lives in. |
| `python` not recognised | Python is not installed or not on PATH. Reinstall and tick "Add python.exe to PATH". |

## Important notes
- **Sample data only.** The clock is pinned to 2026-11-10 09:00 UTC in `prompts.py` because the data is set on that date.
- **Costs:** every question uses your Claude credits. Set a spend limit or an AWS Budget alert.
- **Keep the web page local.** `server.py` listens on `127.0.0.1` only and has no login. Do not expose it to a network.
- **Check the output.** AI answers can vary between runs. Verify before acting on them.
