#!/usr/bin/env python3
"""Compute real human working hours from Claude Code session transcripts.

Signal: timestamps of messages the human actually produced (typed prompts,
slash commands). Consecutive messages closer than --gap minutes chain into
one activity interval; larger gaps close it, so pauses and idle days fall
out automatically. Intervals from all given sources are merged onto one
timeline (union), so time spent driving several sessions in parallel is
counted once — that union is the "real hours" figure.

Sources are given as working-directory paths (e.g. /home/gm-is/gm-is-613)
or as NAME=PATH pairs to control the label in the report. Paths are
resolved to transcript directories under ~/.claude/projects/.

Limitation: reading/thinking without typing for longer than --gap counts
as a pause. Tune --gap if reality differs.
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

PROJECTS_DIR = os.path.expanduser("~/.claude/projects")


def encode_workdir(path):
    """Encode a working-directory path the way ~/.claude/projects does."""
    return re.sub(r"[/._]", "-", os.path.abspath(path).rstrip("/"))


def resolve_source(arg):
    """Return (label, transcript_dir) for a PATH or NAME=PATH argument."""
    if "=" in arg and not os.path.isdir(arg):
        label, path = arg.split("=", 1)
    else:
        label, path = os.path.basename(os.path.abspath(arg).rstrip("/")), arg
    if os.path.isdir(path) and os.path.dirname(os.path.abspath(path)) == PROJECTS_DIR:
        return label, os.path.abspath(path)
    return label, os.path.join(PROJECTS_DIR, encode_workdir(path))


def is_human_message(obj):
    if obj.get("type") != "user" or obj.get("isSidechain"):
        return False
    origin = obj.get("origin")
    if isinstance(origin, dict):
        return origin.get("kind") == "human"
    # Older/command entries carry no origin; typed slash commands arrive as
    # string content starting with a <command-...> tag.
    content = obj.get("message", {}).get("content")
    return isinstance(content, str) and content.lstrip().startswith("<command-")


def human_timestamps(transcript_dir, since, until):
    stamps = []
    for fn in glob.glob(os.path.join(transcript_dir, "*.jsonl")):
        with open(fn, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not is_human_message(obj):
                    continue
                ts = obj.get("timestamp")
                if not ts:
                    continue
                try:
                    t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                except ValueError:
                    continue
                if since and t < since:
                    continue
                if until and t > until:
                    continue
                stamps.append(t)
    return sorted(stamps)


def to_intervals(stamps, gap, floor):
    """Chain timestamps into activity intervals."""
    intervals = []
    for t in stamps:
        if intervals and t - intervals[-1][1] <= gap:
            intervals[-1][1] = t
        else:
            intervals.append([t, t])
    return [(a, max(b, a + floor)) for a, b in intervals]


def merge(intervals):
    merged = []
    for a, b in sorted(intervals):
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return merged


def total_hours(intervals):
    return sum((b - a).total_seconds() for a, b in intervals) / 3600


def parse_when(s, end=False):
    if not s:
        return None
    t = datetime.fromisoformat(s)
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    if end and len(s) == 10:  # bare date as --until means end of that day
        t += timedelta(days=1)
    return t


def main():
    ap = argparse.ArgumentParser(
        description="Compute real human working hours from Claude Code transcripts.")
    ap.add_argument("sources", nargs="+", metavar="PATH|NAME=PATH",
                    help="working dirs (or transcript dirs) to scan")
    ap.add_argument("--gap", type=float, default=15,
                    help="minutes of silence that closes an interval (default 15)")
    ap.add_argument("--floor", type=float, default=2,
                    help="minimum minutes credited per interval (default 2)")
    ap.add_argument("--since", help="ISO date/datetime lower bound (UTC if naive)")
    ap.add_argument("--until", help="ISO date/datetime upper bound (UTC if naive)")
    ap.add_argument("--detailed", action="store_true",
                    help="include the per-source table")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args()

    gap = timedelta(minutes=args.gap)
    floor = timedelta(minutes=args.floor)
    since = parse_when(args.since)
    until = parse_when(args.until, end=True)

    per_source, everything = [], []
    for arg in args.sources:
        label, tdir = resolve_source(arg)
        if not os.path.isdir(tdir):
            print(f"warning: no transcripts for {label} ({tdir})", file=sys.stderr)
            per_source.append({"label": label, "messages": 0, "hours": 0.0})
            continue
        stamps = human_timestamps(tdir, since, until)
        ivs = to_intervals(stamps, gap, floor)
        everything.extend(ivs)
        per_source.append({"label": label, "messages": len(stamps),
                           "hours": round(total_hours(ivs), 2)})

    union = merge(everything)
    real = round(total_hours(union), 2)
    period = (union[0][0].isoformat(), union[-1][1].isoformat()) if union else (None, None)

    if args.as_json:
        print(json.dumps({"real_hours": real, "period": period,
                          "gap_minutes": args.gap, "sources": per_source}, indent=2))
        return

    print(f"Real hours (union, parallel deduplicated): {real} h")
    if union:
        print(f"Period: {period[0]} .. {period[1]}")
    print(f"Gap threshold: {args.gap} min; interval floor: {args.floor} min")
    if args.detailed:
        print()
        print("| source | human messages | active hours |")
        print("|---|---|---|")
        for s in per_source:
            print(f"| {s['label']} | {s['messages']} | {s['hours']} |")
        print()
        print("Note: per-source hours do not sum to the union — overlapping "
              "parallel work is counted once only in the union.")


if __name__ == "__main__":
    main()
