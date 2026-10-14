#!/usr/bin/env python3
"""The documentation checks of the test plan (10 §10.4).

T-DOC-02, always:
* every requirement ID referenced anywhere in docs/design is defined once in 03;
* every Must requirement has a feature (04) and every requirement a row in 11;
* every test ID cited in 11 is defined in 10's test table;
* every test in 10's table exists in tests/ (as test_T_XXX_NN, or cited in a test's docstring),
  except the documentation checks, the end-to-end demo and the pilot, which live outside the suite,
  and the tests of requirements still planned for a milestone (designed before they are written);
* every test named test_T_XXX_NN in tests/ is in the plan.
With --release, every requirement must also be built (I) or partial with a reason (P), and every
test must exist.

T-DOC-01, with --mmdc: every ```mermaid block in docs/design renders (mermaid-cli; pass
--puppeteer-config where a sandboxed browser needs one).

    python3 scripts/check_docs.py [--release] [--mmdc PATH [--puppeteer-config FILE]]
"""
from __future__ import annotations

import argparse
import collections
import glob
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESIGN = os.path.join(HERE, "docs", "design")
TESTS = os.path.join(HERE, "tests")

REQ = re.compile(r"\b(FR-[A-Z]+|NFR)-(\d+)((?:/\d+)*)(?:…(\d+))?")
TEST = re.compile(r"\bT-([A-Z0-9]+)-(\d+)((?:/\d+)*)(?:…(\d+))?")
TEST_FN = re.compile(r"def test_T_([A-Z0-9]+)_(\d+)(?:_|\()")
OUTSIDE_SUITE = ("T-DOC-", "T-E2E-", "T-PILOT-")


def read(name: str) -> str:
    with open(os.path.join(DESIGN, name), encoding="utf-8") as f:
        return f.read()


def expand(pattern: re.Pattern, text: str, prefix: str = "") -> set[str]:
    """IDs with ranges written as FR-X-01/03 and FR-X-01…05 expanded."""
    out = set()
    for m in pattern.finditer(text):
        area, first, slashes, last = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        nums = [first] + [int(x) for x in slashes.split("/") if x]
        if last:
            nums += list(range(first, int(last) + 1))
        out |= {f"{prefix}{area}-{n:02d}" for n in nums}
    return out


def check_requirements(release: bool) -> int:
    problems = 0
    defined: dict[str, str] = {}
    for line in read("03-requirements.md").splitlines():
        m = re.match(r"\| (FR-[A-Z]+-\d+|NFR-\d+) \| .*?\| ([MSC]) \|", line)
        if m:
            if m.group(1) in defined:
                print("DUPLICATE definition", m.group(1))
                problems += 1
            defined[m.group(1)] = m.group(2)
    fr = {k: v for k, v in defined.items() if k.startswith("FR")}

    def resolve(text: str) -> set[str]:
        ids = expand(REQ, text)
        for m in re.finditer(r"\bFR-([A-Z]+)-\*", text):
            ids |= {k for k in defined if k.startswith(f"FR-{m.group(1)}-")}
        return ids

    for f in sorted(os.listdir(DESIGN)):
        if f.endswith(".md") and f != "03-requirements.md":
            for i in sorted(resolve(read(f)) - set(defined)):
                print(f"UNDEFINED {i} referenced in {f}")
                problems += 1
    features = resolve(read("04-feature-list.md"))
    for k, p in fr.items():
        if p == "M" and k not in features:
            print(f"MUST without a feature: {k}")
            problems += 1
    status: dict[str, str] = {}
    for line in read("11-traceability.md").splitlines():
        m = re.match(r"\| (FR-[A-Z]+-\d+|NFR-\d+) \|(.*)", line)
        if m:
            cells = [c.strip() for c in m.group(2).split("|")]
            st = cells[4] if m.group(1).startswith("FR") else cells[0]
            if m.group(1) in status:
                print("DUPLICATE trace row", m.group(1))
                problems += 1
            status[m.group(1)] = st
    for k in defined:
        if k not in status:
            print(f"NOT TRACED in 11: {k}")
            problems += 1
        elif release and status[k] not in ("I", "P"):
            print(f"NOT BUILT at release: {k} is {status[k]!r}")
            problems += 1
    uc = resolve(read("05-use-cases.md"))
    counts = collections.Counter(status.get(k) for k in defined)
    print(f"requirements: {len(fr)} FR, {len(defined) - len(fr)} NFR; status {dict(counts)}; "
          f"FR without a use case: {', '.join(sorted(k for k in fr if k not in uc)) or 'none'}")
    return problems


def planned_tests() -> set[str]:
    """Tests cited in 11 only by requirements that are not built yet (status neither I nor P)."""
    built, planned = set(), set()
    for line in read("11-traceability.md").splitlines():
        m = re.match(r"\| (FR-[A-Z]+-\d+) \|(.*)", line)
        if m:
            cells = [c.strip() for c in m.group(2).split("|")]
            (built if cells[4] in ("I", "P") else planned).update(expand(TEST, cells[3], "T-"))
    return planned - built


def check_tests(release: bool) -> int:
    problems = 0
    plan = read("10-test-plan.md")
    defined = set()
    for line in plan.splitlines():
        m = re.match(r"\| (T-[A-Z0-9]+-\d+) \|", line)
        if m:
            if m.group(1) in defined:
                print("DUPLICATE test definition", m.group(1))
                problems += 1
            defined.add(m.group(1))
    cited = expand(TEST, read("11-traceability.md"), "T-")
    for t in sorted(cited - defined):
        print(f"UNDEFINED test {t} cited in 11")
        problems += 1
    in_suite, named = set(), set()
    for path in glob.glob(os.path.join(TESTS, "test_*.py")):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        named |= {f"T-{a}-{int(n):02d}" for a, n in TEST_FN.findall(text)}
        in_suite |= expand(TEST, text, "T-")
    in_suite |= named
    planned = set() if release else planned_tests()
    for t in sorted(defined - in_suite):
        if t in planned:
            print(f"planned, not written yet: {t}")
        elif not t.startswith(OUTSIDE_SUITE):
            print(f"NO TEST in tests/ for {t}")
            problems += 1
    for t in sorted(named - defined):
        print(f"TEST {t} in tests/ is not in the plan (10)")
        problems += 1
    print(f"tests: {len(defined)} in the plan, {len(cited)} cited in 11, {len(named)} named in tests/")
    return problems


def check_diagrams(mmdc: str, config: str | None) -> int:
    failed = total = 0
    for path in sorted(glob.glob(os.path.join(DESIGN, "*.md"))):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for m in re.finditer(r"```mermaid\n(.*?)```", text, re.S):
            total += 1
            with tempfile.TemporaryDirectory() as d:
                src, out = os.path.join(d, "d.mmd"), os.path.join(d, "d.svg")
                with open(src, "w", encoding="utf-8") as f:
                    f.write(m.group(1))
                cmd = [mmdc, "-i", src, "-o", out] + (["-p", config] if config else [])
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                ok = r.returncode == 0 and os.path.exists(out)
                if ok:
                    with open(out, encoding="utf-8") as f:
                        ok = "<svg" in f.read()
            if not ok:
                failed += 1
                line = text[:m.start()].count("\n") + 1
                print(f"DIAGRAM FAILS {os.path.basename(path)}:{line}: {(r.stderr or r.stdout).strip()[:300]}")
    print(f"diagrams: {total - failed}/{total} rendered")
    return failed


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--release", action="store_true", help="every requirement must be I or P")
    p.add_argument("--mmdc", help="mermaid-cli executable: also render every diagram (T-DOC-01)")
    p.add_argument("--puppeteer-config")
    a = p.parse_args()
    problems = check_requirements(a.release) + check_tests(a.release)
    if a.mmdc:
        problems += check_diagrams(a.mmdc, a.puppeteer_config)
    print(f"problems: {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
