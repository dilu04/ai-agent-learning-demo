"""Stage 6: generate a management report and save it as Markdown and HTML."""
from pathlib import Path

import markdown  # converts Markdown text to HTML

from agent import run_agent
from prompts import build_report_prompt, current_time

REPORTS_DIR = Path(__file__).parent / "reports"

HTML_TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AWS Health Report</title>
<style>
  body {{ font-family: Segoe UI, Arial, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; color: #1f2933; }}
  h1 {{ border-bottom: 3px solid #ff9900; padding-bottom: .3rem; }}
  h2 {{ margin-top: 2rem; color: #232f3e; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
  th, td {{ border: 1px solid #cbd2d9; padding: .5rem .7rem; text-align: left; vertical-align: top; }}
  th {{ background: #232f3e; color: #fff; }}
  tr:nth-child(even) td {{ background: #f5f7fa; }}
</style></head><body>
{body}
</body></html>"""


def generate_report():
    question = "Review all open and upcoming AWS Health events and write the management report."
    report_md = run_agent(question, system_prompt=build_report_prompt())

    REPORTS_DIR.mkdir(exist_ok=True)
    stamp = current_time()[:10]  # the date, e.g. 2026-11-10
    md_path = REPORTS_DIR / f"health-report-{stamp}.md"
    html_path = REPORTS_DIR / f"health-report-{stamp}.html"

    md_path.write_text(report_md, encoding="utf-8")
    body = markdown.markdown(report_md, extensions=["tables"])
    html_path.write_text(HTML_TEMPLATE.format(body=body), encoding="utf-8")
    return md_path, html_path


if __name__ == "__main__":
    md_path, html_path = generate_report()
    print(f"\nSaved:\n  {md_path}\n  {html_path}")
