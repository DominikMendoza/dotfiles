#!/usr/bin/env python3
"""Print the devops.hyros.com Log Insights URL for a query read from stdin."""
import argparse
import sys
import urllib.parse
from datetime import datetime, timezone

BASE_URL = "https://devops.hyros.com/tools/log-insights"


def to_utc_iso(parser, value):
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        parser.error(f"not an ISO 8601 date: {value}")
    if moment.tzinfo is None:
        parser.error(f"give {value} an offset or Z, so it is not read as local time")
    moment = moment.astimezone(timezone.utc)
    return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", required=True, help="exact log group, such as HYROS-PROD-AIR-PROCESSING")
    parser.add_argument("--run", required=True, help="id of a finished run, from logs_run")
    parser.add_argument("--window", type=int, help="minutes, ending now")
    parser.add_argument("--from", dest="range_from", help="fixed range start, ISO 8601 with an offset or Z")
    parser.add_argument("--to", dest="range_to", help="fixed range end, ISO 8601 with an offset or Z")
    args = parser.parse_args()

    fixed_range = args.range_from is not None or args.range_to is not None
    if fixed_range and args.window is not None:
        parser.error("pass either --window or --from/--to, not both")
    if fixed_range and (args.range_from is None or args.range_to is None):
        parser.error("a fixed range needs both --from and --to")
    if not fixed_range and args.window is None:
        parser.error("pass --window, or --from and --to")

    query = sys.stdin.read().strip()
    if not query:
        parser.error("pass the query on stdin")

    if fixed_range:
        range_from = to_utc_iso(parser, args.range_from)
        range_to = to_utc_iso(parser, args.range_to)
        source_line = f"SOURCE '{args.group}' START=\"{range_from}\" END=\"{range_to}\""
    else:
        source_line = f"SOURCE '{args.group}' START=-{args.window}m END=0s"

    if not query.startswith("SOURCE "):
        commands = query if query.startswith("|") else f"| {query}"
        query = f"{source_line}\n{commands}"

    if fixed_range:
        params = [("groups", args.group), ("run", args.run), ("q", query), ("from", range_from), ("to", range_to)]
    else:
        params = [("groups", args.group), ("window", str(args.window)), ("run", args.run), ("q", query)]
    print(f"{BASE_URL}?{urllib.parse.urlencode(params, safe='*', quote_via=urllib.parse.quote_plus)}")


if __name__ == "__main__":
    main()
