#!/usr/bin/env bash
# The migration pilot on CPython (M4, WP-M4.1; T-PILOT-01).
#
# CPython's history is ingested in order and verified file by file at checkpoints on its main line;
# a scion-server process serves it to CI with no client (log, file history, blame, ancestry, git
# lookups, file reads) while it grows; storage, memory and the latency of every query are recorded
# at each checkpoint. It stops at the end of the history or before the disk budget runs out (R-20).
#
#   examples/pilot.sh [WORKDIR]
#
# PILOT_GIT=path uses an existing clone (bare is fine) instead of cloning from GitHub;
# PILOT_CHECKPOINTS (default 10), PILOT_DISK_GB (default 12) and PILOT_MAINLINE (only the first N
# main-line commits) shape the run. The checks at the end are T-PILOT-01.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python3}
W=${1:-$(mktemp -d /tmp/scion-pilot-XXXXXX)}
mkdir -p "$W"
G=${PILOT_GIT:-$W/cpython.git}
if [ ! -d "$G" ]; then
  echo "cloning CPython into $G"
  git clone -q --bare https://github.com/python/cpython.git "$G"
fi
echo "pilot in $W: $(git -C "$G" rev-list --count main) commits, $(git -C "$G" rev-list --first-parent --count main) on the main line"
$PY -m scion.tools.pilot --git "$G" --root "$W/deployment" --checkpoints "${PILOT_CHECKPOINTS:-10}" \
  --disk-budget-gb "${PILOT_DISK_GB:-12}" ${PILOT_MAINLINE:+--mainline "$PILOT_MAINLINE"} \
  --summary "$W/summary.json" | tee "$W/checkpoints.jsonl"

$PY - "$W/summary.json" <<'EOF'
import json, math, sys
s = json.load(open(sys.argv[1]))
cps = s["checkpoints"]
assert cps, "no checkpoint was reached"
bad = [c["checkpoint"] for c in cps if not c["verified"] or c["mismatches"]]
assert not bad, f"verification failed at checkpoints {bad}"  # FR-MG-05: every file, every checkpoint
for c in cps:  # NFR-06: ancestry over the whole history in O(log n) steps
    assert c["is_ancestor_steps"] <= 2 * math.ceil(math.log2(max(c["commits"], 2))) + 2, c
first, last = cps[0], cps[-1]
growth = last["commits"] / first["commits"]
print(f"T-PILOT-01: {len(cps)} checkpoints, {first['commits']:,} to {last['commits']:,} commits (x{growth:.1f}), "
      f"all verified ({last['files']:,} files at the last)")
print("  checkpoint    commits   objects   objects MB   meta MB   commits/s   ingest RSS MB   server RSS MB")
for c in cps:
    print(f"  {c['checkpoint']:>10} {c['commits']:>10,} {c['objects']:>9,} {c['objects_mb']:>12,.1f} {c['meta_mb']:>9,.1f} "
          f"{c['commits_per_s'] or 0:>11,.1f} {c['ingest_peak_rss_mb']:>15,.1f} {c['server_peak_rss_mb']:>15,.1f}")
print("  query (median ms; first call in brackets)      first checkpoint        last checkpoint")
for q in last["queries"]:
    a, b = first["queries"].get(q), last["queries"][q]
    left = f"{a['ms']:8.2f} [{a['first_ms']:9.2f}]" if a else " " * 20
    print(f"  {q:44} {left}   {b['ms']:8.2f} [{b['first_ms']:9.2f}]")
# NFR-03/05: answering a query does not grow with the history's size; lookups by key stay flat
for q in ("git_lookup", "is_ancestor_first_tip", "fp_ancestor_half", "log_50"):
    a, b = first["queries"][q]["ms"], last["queries"][q]["ms"]
    assert b <= 5 * a + 20, f"{q}: {a} ms at {first['commits']:,} commits, {b} ms at {last['commits']:,}"
# FR-MG-04: ingestion memory stays bounded as the history grows
assert last["ingest_peak_rss_mb"] <= 4 * first["ingest_peak_rss_mb"] + 200, (first, last)
print("T-PILOT-01 passed" + (f" (stopped: {s['stopped']})" if s["stopped"] else ""))
EOF
