"""Run this file to try every function in tools.py. No AI involved."""
import json

import tools


def show(title, result):
    print(f"\n=== {title} ===")
    print(json.dumps(result, indent=2))


def short(events):
    """Print events as one short line each, to keep the output readable."""
    return [f'{e["statusCode"]:9} {e["service"]:20} {e["eventTypeCode"]}' for e in events]


show("1. All events", short(tools.list_health_events()))
show("2. Open events only", short(tools.list_health_events(status="open")))
show("3. Scheduled changes only", short(tools.list_health_events(category="scheduledChange")))
show("4. Lambda events only", short(tools.list_health_events(service="lambda")))

ec2_arn = tools.list_health_events(service="EC2")[0]["arn"]
show("5. Details of the EC2 event", tools.get_event_details(ec2_arn))
show("6. Resources affected by the EC2 event", tools.get_affected_resources(ec2_arn))
show("7. Account 111111111111", tools.get_account_info("111111111111"))
show("8. Events touching account 333333333333", short(tools.get_events_for_account("333333333333")))
show("9. Bad ARN (error handling)", tools.get_event_details("not-a-real-arn"))
