"""Stage 4, part 1: tell Claude which tools exist.

Claude cannot see tools.py. It only sees the descriptions below, so they
must say clearly WHAT each tool does and WHEN to use it.
"""
import tools

# The list we send to Claude with every API call.
TOOL_DEFINITIONS = [
    {
        "name": "list_health_events",
        "description": (
            "List AWS Health events. Use this first to discover what events exist. "
            "All filters are optional; leave them out to get every event."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["open", "upcoming", "closed"],
                    "description": "open = happening now, upcoming = scheduled, closed = resolved",
                },
                "category": {
                    "type": "string",
                    "enum": ["issue", "scheduledChange", "accountNotification"],
                },
                "service": {
                    "type": "string",
                    "description": "AWS service name, for example EC2, RDS or LAMBDA",
                },
            },
        },
    },
    {
        "name": "get_event_details",
        "description": "Get one event's full details and AWS's description text, including recommended actions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_arn": {"type": "string", "description": "The 'arn' field of an event"},
            },
            "required": ["event_arn"],
        },
    },
    {
        "name": "get_affected_resources",
        "description": (
            "Get the resources hit by an event. Each result includes its AWS account and "
            "that account's name, environment and criticality."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "event_arn": {"type": "string", "description": "The 'arn' field of an event"},
            },
            "required": ["event_arn"],
        },
    },
    {
        "name": "get_account_info",
        "description": "Get business context for an AWS account: owner team, email, environment, criticality and business function.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string", "description": "12-digit AWS account ID"},
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "get_remediation_playbook",
        "description": (
            "Get our team's standard remediation steps and urgency rule for an event type. "
            "Use it when recommending actions, and base recommendations on it."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "event_type_code": {
                    "type": "string",
                    "description": "The 'eventTypeCode' field of an event, e.g. AWS_EC2_INSTANCE_RETIREMENT_SCHEDULED",
                },
            },
            "required": ["event_type_code"],
        },
    },
    {
        "name": "get_events_for_account",
        "description": "List every event that affects at least one resource in the given AWS account.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string", "description": "12-digit AWS account ID"},
            },
            "required": ["account_id"],
        },
    },
]

# Maps the name Claude uses to the real Python function.
TOOL_FUNCTIONS = {
    "list_health_events": tools.list_health_events,
    "get_event_details": tools.get_event_details,
    "get_affected_resources": tools.get_affected_resources,
    "get_account_info": tools.get_account_info,
    "get_events_for_account": tools.get_events_for_account,
    "get_remediation_playbook": tools.get_remediation_playbook,
}
