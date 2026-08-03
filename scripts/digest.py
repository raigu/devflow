#!/usr/bin/env python3
"""Produce compact per-session digests of Claude Code transcripts.

Input sources are working-directory paths (or NAME=PATH pairs), the
same convention as worktime.py. For every session found, one small
markdown digest is written to --out: a header (source, session, time
span, message and interruption counts) plus one line per HUMAN
message — timestamp and text, truncated to --max-chars. Assistant
output and tool results are never included, so digests stay a small
fraction of the raw transcript and are safe to hand to helper agents.

Sessions with no human messages in range are skipped. Exits non-zero
when a source has no transcripts at all.
"""

import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from worktime import resolve_source, is_human_message, parse_when  # noqa: E402

INTERRUPT_RE = re.compile(r"\[Request interrupted")


def message_text(obj):
    content = obj.get("message", {}).get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(b.get("text", "") for b in content
                        if isinstance(b, dict) and b.get("type") == "text")
    return ""


def digest_session(path, since, until, max_chars):
    lines, interrupts, first, last = [], 0, None, None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if INTERRUPT_RE.search(str(obj.get("message", {}).get("content", ""))[:200]):
                interrupts += 1
            if not is_human_message(obj):
                continue
            ts = obj.get("timestamp", "")
            if since and ts and ts < since:
                continue
            if until and ts and ts > until:
                continue
            text = " ".join(message_text(obj).split())
            if not text:
                continue
            if len(text) > max_chars:
                text = text[:max_chars] + " …"
            stamp = ts[:16].replace("T", " ") if ts else "?"
            lines.append(f"- {stamp} {text}")
            first, last = first or stamp, stamp
    return lines, interrupts, first, last


def main():
    ap = argparse.ArgumentParser(
        description="Produce compact per-session digests of Claude Code transcripts.")
    ap.add_argument("sources", nargs="+", metavar="PATH|NAME=PATH")
    ap.add_argument("--out", required=True, help="directory for digest files")
    ap.add_argument("--since", help="ISO date lower bound")
    ap.add_argument("--until", help="ISO date upper bound")
    ap.add_argument("--max-chars", type=int, default=300,
                    help="truncate each message to this length (default 300)")
    args = ap.parse_args()

    # Validate bounds early; comparison itself is done on ISO strings.
    parse_when(args.since)
    parse_when(args.until)
    os.makedirs(args.out, exist_ok=True)

    written, errors = 0, []
    for arg in args.sources:
        label, tdir = resolve_source(arg)
        files = glob.glob(os.path.join(tdir, "*.jsonl"))
        if not os.path.isdir(tdir) or not files:
            errors.append(f"no transcripts for {label} ({tdir})")
            continue
        for fn in sorted(files):
            stem = os.path.splitext(os.path.basename(fn))[0]
            lines, interrupts, first, last = digest_session(
                fn, args.since, args.until, args.max_chars)
            if not lines:
                continue
            out = os.path.join(args.out, f"{label}--{stem}.md")
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(f"# {label} / {stem}\n"
                         f"{first} .. {last} | {len(lines)} human messages"
                         f" | {interrupts} interruptions\n\n")
                fh.write("\n".join(lines) + "\n")
            written += 1

    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    if errors:
        sys.exit(2)
    if not written:
        sys.exit("error: no sessions with human messages in the given range")
    print(f"{written} digest file(s) written to {args.out}")


if __name__ == "__main__":
    main()
