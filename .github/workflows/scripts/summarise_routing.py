#!/usr/bin/env python3
"""Summarise skillscope routing runs for a human reviewer.

skillscope's own report lists every case. This one answers "what should I
change?": it groups misroutes by the pair of skills involved, says which
description to look at, flags prompts that routed differently across repeat
runs, and, given a baseline, lists only what changed.

    python3 .github/workflows/scripts/summarise_routing.py RUN.json [RUN.json ...] \
        [--baseline BASE.json ...] [--output summary.md]

RUN.json files are skillscope's routing reports from .skillscope/runs/. Pass
several runs of the same room to see flaky prompts; pass the runs from main as
--baseline to see what a pull request changed.
"""

import argparse
import glob
import json
import os
import sys
from collections import Counter, defaultdict

NONE = "(no skill)"


def load_runs(paths):
    """Return (meta of the first run, {case id: [case from each run]})."""
    by_id = defaultdict(list)
    meta = {}
    for path in paths:
        with open(path, encoding="utf-8") as f:
            summary = json.load(f)
        if "cases" not in summary:
            sys.exit(f"{path}: not a skillscope routing report (no 'cases')")
        meta = meta or summary.get("meta") or {}
        for case in summary["cases"]:
            by_id[case["id"]].append(case)
    return meta, by_id


def load_notes():
    """Map case id to the `note` written in the skills' evals.json files."""
    notes = {}
    for path in glob.glob("site/plugins/*/skills/*/evals/evals.json"):
        with open(path, encoding="utf-8") as f:
            for case in json.load(f).get("evaluations", []):
                if case.get("note"):
                    notes[case["id"]] = case["note"]
    return notes


def outcome(runs):
    """Collapse one case's repeat runs into its most common result.

    Returns (expected, observed, graded runs, correct runs). Errored runs say
    nothing about routing, so they are left out of both counts.
    """
    graded = [c for c in runs if c["verdict"] != "error"]
    if not graded:
        return runs[0]["expect"], None, 0, 0
    observed = Counter(c["observed"] for c in graded).most_common(1)[0][0]
    return runs[0]["expect"], observed, len(graded), sum(c["passed"] for c in graded)


def short(text, limit=140):
    text = " ".join(text.split()).replace("|", "\\|")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def render(meta, runs, baseline, notes):
    lines = []
    results = {cid: outcome(cases) for cid, cases in runs.items()}
    graded = {cid: r for cid, r in results.items() if r[2]}
    stable_pass = [cid for cid, r in graded.items() if r[3] == r[2]]
    repeats = max(len(c) for c in runs.values())
    errored = len(results) - len(graded)

    lines.append("## Skill routing")
    lines.append("")
    lines.append(
        f"**{len(stable_pass)} of {len(graded)} prompts routed to the right "
        f"skill** in every run ({meta.get('harness', 'unknown harness')}, "
        f"model `{meta.get('model', 'unknown')}`, {repeats} run"
        f"{'s' if repeats != 1 else ''} per prompt"
        + (f", {errored} errored and not graded" if errored else "")
        + ")."
    )

    if baseline:
        base = {cid: outcome(cases) for cid, cases in baseline.items()}
        broke = [
            cid for cid, r in graded.items()
            if cid in base and base[cid][2] and base[cid][3] == base[cid][2]
            and r[3] < r[2]
        ]
        fixed = [
            cid for cid in stable_pass
            if cid in base and base[cid][2] and base[cid][3] < base[cid][2]
        ]
        lines += ["", "### Compared with the baseline", ""]
        if not broke and not fixed:
            lines.append("No prompt changed result.")
        for label, ids in (("Now failing", broke), ("Now passing", fixed)):
            for cid in ids:
                exp, obs, n, ok = graded[cid]
                _, base_obs, base_n, base_ok = base[cid]
                got = (
                    f"right in {ok} of {n} runs" if ok
                    else f"went to {obs or NONE}"
                )
                was = (
                    f"right in {base_ok} of {base_n}" if base_ok
                    else f"went to {base_obs or NONE}"
                )
                lines.append(
                    f"- **{label}:** `{cid}` (expects {exp or NONE}): "
                    f"{got}; baseline {was}"
                )

    # Group every failing prompt by what kind of description problem it shows.
    overlaps = defaultdict(list)   # (expected, observed) -> case ids
    too_narrow = defaultdict(list)  # expected skill that didn't fire
    too_broad = defaultdict(list)   # skill that fired with nothing expected
    flaky = []
    for cid, (exp, obs, n, ok) in graded.items():
        if 0 < ok < n:
            flaky.append(cid)
        if ok == n:
            continue
        if exp and obs and exp != obs:
            overlaps[(exp, obs)].append(cid)
        elif exp and not obs:
            too_narrow[exp].append(cid)
        elif obs and not exp:
            too_broad[obs].append(cid)

    def case_lines(ids):
        out = []
        for cid in sorted(ids):
            prompt = short(runs[cid][0]["prompt"])
            note = f" _{short(notes[cid], 120)}_" if cid in notes else ""
            out.append(f"  - `{cid}`: \"{prompt}\"{note}")
        return out

    lines += ["", "### What to look at", ""]
    if not (overlaps or too_narrow or too_broad):
        lines.append("Nothing: every graded prompt routed as expected.")
    for (exp, obs), ids in sorted(overlaps.items(), key=lambda kv: -len(kv[1])):
        lines.append(
            f"- **`{obs}` took {len(ids)} prompt{'s' if len(ids) > 1 else ''} "
            f"meant for `{exp}`.** The descriptions overlap: make `{exp}`'s "
            f"claim these more specifically, or narrow `{obs}`'s."
        )
        lines += case_lines(ids)
    for exp, ids in sorted(too_narrow.items()):
        lines.append(
            f"- **`{exp}` didn't fire when it should have.** Its description "
            f"may not mention what these prompts ask about."
        )
        lines += case_lines(ids)
    for obs, ids in sorted(too_broad.items()):
        lines.append(
            f"- **`{obs}` fired on a prompt no skill should take.** Its "
            f"description may be too broad."
        )
        lines += case_lines(ids)
    lines += [
        "",
        "Before changing a description, check the prompt: if a reasonable "
        "person couldn't say which skill it belongs to, fix the test instead.",
    ]

    if flaky:
        lines += [
            "",
            "### Inconsistent across runs",
            "",
            "These prompts routed correctly in some runs only, so a single run "
            "can pass or fail them by chance:",
            "",
        ]
        for cid in sorted(flaky):
            _, _, n, ok = graded[cid]
            lines.append(f"- `{cid}`: right in {ok} of {n} runs")

    per_skill = defaultdict(lambda: [0, 0])
    for exp, _, n, ok in graded.values():
        if exp:
            per_skill[exp][0] += 1
            per_skill[exp][1] += ok == n
    lines += [
        "",
        "<details><summary>Per skill</summary>",
        "",
        "| Skill | Prompts that should fire it | Routed correctly |",
        "| --- | --- | --- |",
    ]
    for skill, (total, ok) in sorted(per_skill.items()):
        lines.append(f"| `{skill}` | {total} | {ok} |")
    lines += ["", "</details>", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("runs", nargs="+", help="skillscope routing JSON")
    parser.add_argument("--baseline", nargs="*", default=[],
                        help="routing JSON from main, to compare against")
    parser.add_argument("--output", help="write markdown here, not stdout")
    args = parser.parse_args()

    meta, runs = load_runs(args.runs)
    _, baseline = load_runs(args.baseline) if args.baseline else ({}, {})
    text = render(meta, runs, baseline, load_notes())
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as f:
            f.write(text + "\n")


if __name__ == "__main__":
    main()
