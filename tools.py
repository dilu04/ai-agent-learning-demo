"""Stage 2: data functions the agent will use as tools.

Every function reads the sample JSON files in data/ and returns plain Python
dicts and lists. In Stage 7 we will replace the data loading with real AWS
Health API calls, and nothing else in the project has to change.
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def _load(name):
    """Read one JSON file from the data folder and return its contents."""
    with open(DATA_DIR / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)


def list_health_events(status=None, category=None, service=None):
    """List Health events. Each filter is optional; leave it out to skip it.

    status:   "open", "upcoming" or "closed"
    category: "issue", "scheduledChange" or "accountNotification"
    service:  for example "EC2", "RDS", "LAMBDA"
    """
    events = _load("health_events")
    if status:
        events = [e for e in events if e["statusCode"] == status]
    if category:
        events = [e for e in events if e["eventTypeCategory"] == category]
    if service:
        events = [e for e in events if e["service"].lower() == service.lower()]
    return events


def get_event_details(event_arn):
    """Return one event together with its human-readable description."""
    for event in _load("health_events"):
        if event["arn"] == event_arn:
            details = dict(event)  # copy, so we don't change the original
            for d in _load("event_descriptions"):
                if d["eventArn"] == event_arn:
                    details["description"] = d["latestDescription"]
            return details
    return {"error": f"No event found with ARN {event_arn}"}


def get_affected_resources(event_arn):
    """Return the resources hit by an event, each with its account's context."""
    accounts = {a["accountId"]: a for a in _load("accounts")}
    results = []
    for entity in _load("affected_entities"):
        if entity["eventArn"] == event_arn:
            item = dict(entity)
            account = accounts.get(entity["awsAccountId"], {})
            item["accountName"] = account.get("name")
            item["environment"] = account.get("environment")
            item["criticality"] = account.get("criticality")
            results.append(item)
    return results


def get_account_info(account_id):
    """Return business context for one AWS account (owner, environment, criticality)."""
    for account in _load("accounts"):
        if account["accountId"] == account_id:
            return account
    return {"error": f"No account found with ID {account_id}"}


def get_remediation_playbook(event_type_code):
    """Return our team's standard remediation steps for an event type."""
    for entry in _load("remediation_playbook"):
        if entry["eventTypeCode"] == event_type_code:
            return entry
    return {"error": f"No playbook for {event_type_code}. Use general best practice and say so."}


def get_events_for_account(account_id):
    """Return every event that affects at least one resource in this account."""
    arns = {e["eventArn"] for e in _load("affected_entities")
            if e["awsAccountId"] == account_id}
    return [e for e in _load("health_events") if e["arn"] in arns]
