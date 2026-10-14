#!/usr/bin/env bash
# T-E2E-01: the whole system end to end, in separate processes.
#
#   git history ──ingest──▶ deployment ◀── scion-server ×2 ◀── scion-cache ◀── scion-daemon ◀── scn
#
# It ingests a git repository (with verification), serves it from two servers, a regional cache and
# a node daemon, then exercises what the article describes: clones through the tiers (a second clone
# makes no cache request), a sparse checkout, directory permissions, server-side queries and grep,
# review with semantic rules, concurrent landings without a merge queue, post-merge testing with the
# deploy gate, a superfan reading telemetry and logs, failover when a server dies, and a backup taken
# while everything runs, restored and verified.
#
# Usage: examples/demo.sh        (KEEP=1 keeps the work directory; PYTHON=... picks the interpreter)
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
PY=${PYTHON:-python3}
W=$(mktemp -d "${TMPDIR:-/tmp}/scion-e2e.XXXXXX")
PIDS=()
STARTED=$(date +%s)

cleanup() {
  for p in "${PIDS[@]:-}"; do [ -n "$p" ] && kill "$p" 2>/dev/null || true; done
  wait 2>/dev/null || true
  if [ -n "${KEEP:-}" ]; then echo "work directory kept: $W"; else rm -rf "$W"; fi
}
trap cleanup EXIT

step() { printf '\n== %s\n' "$*"; }
fail() { echo "E2E FAILED: $*" >&2; for f in "$W"/logs/*.log; do echo "--- $f"; tail -20 "$f"; done >&2; exit 1; }
ok() { echo "   ok: $*"; }
port() { $PY -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])'; }
admin() { $PY -m scion scion-admin "$@"; }
json_get() { $PY -c "import json, sys; d = json.load(sys.stdin); print($1)"; }
stat_of() {  # stat_of URL EXPR: evaluate EXPR on the component's /stats as `s`
  $PY - "$1" "$2" <<'EOF'
import sys
from scion.rpc import RpcClient
s = RpcClient(sys.argv[1], retries=0).get_json("/stats")
print(eval(sys.argv[2]))
EOF
}
wait_up() {
  $PY - "$1" <<'EOF' || fail "$1 did not come up"
import sys, time
from scion.rpc import RpcClient
deadline = time.time() + 20
while time.time() < deadline:
    try:
        RpcClient(sys.argv[1], retries=0, timeout=2).get_json("/healthz")
        sys.exit(0)
    except Exception:
        time.sleep(0.1)
sys.exit(1)
EOF
}
start() {  # start NAME COMMAND...: a background process with its own log
  local name=$1; shift
  "$@" >"$W/logs/$name.log" 2>&1 &
  PIDS+=($!)
  eval "PID_${name//-/_}=$!"
}

mkdir -p "$W/logs"
DEP="$W/deployment"
SOCK="$W/d.sock"
P1=$(port); P2=$(port); PC=$(port)
S1="http://127.0.0.1:$P1"; S2="http://127.0.0.1:$P2"; CACHE="http://127.0.0.1:$PC"; DAEMON="unix:$SOCK"
SERVERS="$S1,$S2"
scn() { local user=$1; shift; $PY -m scion scn --server "$SERVERS" --repo monorepo --user "$user" "$@"; }

step "1. a git repository with history: branches, a merge, a rename, an executable and a symlink"
G="$W/git"
mkdir -p "$G/src" "$G/docs" "$G/secrets" "$G/tools"
export GIT_AUTHOR_NAME=Dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=Dev GIT_COMMITTER_EMAIL=dev@example.com
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
git -C "$G" init -q -b main
printf 'def handler(x):\n    return x + 1\n' > "$G/src/app.py"
printf '# Project\n' > "$G/docs/README.md"
printf 'API_KEY = "s3cr3t-NEEDLE"\n' > "$G/secrets/keys.py"
printf '#!/bin/sh\necho build\n' > "$G/tools/build.sh"; chmod +x "$G/tools/build.sh"
ln -s docs/README.md "$G/README.md"
git -C "$G" add -A && git -C "$G" commit -qm "initial import"
git -C "$G" checkout -qb feature
printf 'def helper():\n    return "NEEDLE"\n' > "$G/src/helper.py"
git -C "$G" add -A && git -C "$G" commit -qm "add a helper"
git -C "$G" checkout -q main
printf 'def handler(x):\n    # add one\n    return x + 1\n' > "$G/src/app.py"
git -C "$G" commit -qam "comment the handler"
git -C "$G" merge -q --no-edit feature
git -C "$G" mv src/helper.py src/helpers.py && git -C "$G" commit -qm "rename the helper"
ok "$(git -C "$G" rev-list --count main) commits"

step "2. a deployment: groups, admins, a restricted directory and a protected main"
admin init --root "$DEP" >/dev/null
cat > "$DEP/deployment.json" <<'EOF'
{"groups": {"sec-team": ["sam"], "dev": ["alice", "bob", "carol"]}, "admins": ["root"]}
EOF
admin create-repo --root "$DEP" monorepo >/dev/null
cat > "$DEP/repos/monorepo/policy.json" <<'EOF'
{"read": ["*"], "write": ["*"],
 "paths": [{"prefix": "secrets", "read": ["sec-team"], "write": ["sec-team"]}],
 "protected_refs": {"main": ["antique"]}}
EOF
admin repos --root "$DEP" | grep -qx monorepo || fail "repository not created"
ok "repository monorepo with secrets/ readable by sec-team only"

step "3. ingest the git history, verified file by file (FR-MG-*)"
admin ingest --root "$DEP" --repo monorepo --git "$G" --rev main --ref main --verify > "$W/ingest.json" \
  || fail "ingestion or verification failed"
$PY - "$W/ingest.json" <<'EOF' || fail "unexpected ingestion result"
import json, sys
text = open(sys.argv[1]).read()
stats, end = json.JSONDecoder().raw_decode(text)
verify = json.loads(text[end:])
assert stats["commits"] == 5 and verify["ok"] and verify["mismatches"] == [], (stats, verify)
print(f"   ok: {stats['commits']} commits ingested; {verify['files']} files match git")
EOF
admin derive --root "$DEP" --repo monorepo blame >/dev/null

step "4. two servers, a regional cache and a node daemon, each its own process"
start server1 $PY -m scion scion-server --root "$DEP" --listen "127.0.0.1:$P1"
start server2 $PY -m scion scion-server --root "$DEP" --listen "127.0.0.1:$P2"
wait_up "$S1"; wait_up "$S2"
start cache $PY -m scion scion-cache --listen "127.0.0.1:$PC" --upstream "$S1" --upstream "$S2"
wait_up "$CACHE"
start daemon $PY -m scion scion-daemon --socket "$SOCK" --store "$W/node" --upstream "$CACHE"
wait_up "$DAEMON"
ok "server $S1, server $S2, cache $CACHE, daemon $DAEMON"

step "5. metadata queries with no checkout: log, blame, git lookups, grep (FR-QRY-*, FR-MG-06, FR-SR-02)"
scn alice log -n 3 | head -3
scn alice blame src/app.py | grep -q "add one" || fail "blame"
GIT_TIP=$(git -C "$G" rev-parse main)
scn alice api git_lookup git="$GIT_TIP" | json_get 'd["cs"]' > "$W/tip"
[ "$(scn alice api resolve rev=main | json_get 'd')" = "$(cat "$W/tip")" ] || fail "git_lookup"
scn alice grep NEEDLE | grep -q "src/helpers.py" || fail "grep finds the public match"
if scn alice grep NEEDLE | grep -q secrets; then fail "grep showed alice a restricted file"; fi
scn sam grep NEEDLE | grep -q "secrets/keys.py" || fail "grep shows sam the restricted file"
ok "history, blame, ingested-commit lookups and permission-filtered grep"

step "6. clones through the tiers: the second clone on the node is served by the daemon (NFR-02)"
counts() {  # public misses at the daemon, restricted pass-throughs at the daemon, requests to the cache
  echo "$(stat_of "$DAEMON" 's["cache"]["misses"]') $(stat_of "$DAEMON" 's["cache"]["restricted_passthrough"]')" \
       "$(stat_of "$CACHE" 's["counters"].get("rpc.get_objects", 0)')"
}
scn alice clone "$W/alice" --objects "$DAEMON" >/dev/null
[ -x "$W/alice/tools/build.sh" ] && [ -L "$W/alice/README.md" ] || fail "modes and symlinks"
[ ! -e "$W/alice/secrets/keys.py" ] || fail "alice's clone contains a restricted file"
read -r M0 R0 C0 <<<"$(counts)"
scn bob clone "$W/bob" --objects "$DAEMON" >/dev/null
read -r M1 R1 C1 <<<"$(counts)"
[ "$M1" = "$M0" ] || fail "the second clone missed $((M1 - M0)) public objects at the daemon"
# Restricted objects are never cached (ADR-06): the restricted secrets/ tree still goes up to the
# server, which re-authorizes it for bob and denies it. Nothing else reaches the cache.
[ $((C1 - C0)) -le $((R1 - R0)) ] || fail "the second clone made $((C1 - C0)) cache requests for public objects"
scn carol clone "$W/carol" --objects "$DAEMON" --sparse docs >/dev/null
[ -f "$W/carol/docs/README.md" ] && [ ! -e "$W/carol/src" ] || fail "sparse checkout"
ok "bob's clone: every public object from the daemon; $((C1 - C0)) request reached the cache, for the restricted tree"
ok "a sparse clone for carol; daemon hit rate $(stat_of "$DAEMON" 's["cache"]["hit_rate"]')"

step "7. review with semantic rules, then land (FR-RV-*, FR-LD-*)"
printf 'def handler(x):\n    # add one\n    return x + 2\n' > "$W/alice/src/app.py"
(cd "$W/alice" && $PY -m scion scn commit -m "handler adds two" >/dev/null)
(cd "$W/alice" && $PY -m scion scn review create --title "handler adds two" >/dev/null)
if (cd "$W/alice" && $PY -m scion scn review land 1 >/dev/null 2>&1); then fail "landed a logic change without approval"; fi
scn alice review approve 1 >/dev/null   # recorded, but an author's approval never counts
if (cd "$W/alice" && $PY -m scion scn review land 1 >/dev/null 2>&1); then fail "self-approval counted"; fi
scn bob review approve 1 >/dev/null
(cd "$W/alice" && $PY -m scion scn review land 1 >/dev/null) || fail "approved change did not land"
scn bob cat src/app.py | grep -q "x + 2" || fail "main does not have the landed change"
ok "self-approval did not count; bob's did; the change landed with one compare-and-swap"

step "8. six agents land concurrently on two servers, with no merge queue (FR-LD-02/03)"
AGENTS=()
for i in 1 2 3 4 5 6; do
  (
    printf 'note %s\n' "$i" > "$W/note$i.md"
    head=$(scn "agent$i" api commit --parent main -m "agent $i notes" --file "docs/agent$i.md=$W/note$i.md" | json_get 'd["id"]')
    cr=$(scn "agent$i" api antique.create title="agent $i" head="$head" | json_get 'd["id"]')
    scn "agent$i" api antique.land id="$cr" > "$W/land$i.json"   # documentation needs no approval
  ) &
  AGENTS+=($!)
done
for a in "${AGENTS[@]}"; do wait "$a" || fail "a concurrent landing failed"; done
for i in 1 2 3 4 5 6; do scn bob cat "docs/agent$i.md" | grep -q "note $i" || fail "agent $i's change is missing"; done
ok "all six landed; main has every change"

step "9. post-merge testing and the deploy gate (FR-PM-*)"
$PY -m scion scion-postmerge --server "$SERVERS" --repo monorepo --workdir "$W/postmerge" --objects "$DAEMON" \
  --cmd "test -f src/app.py" --once > "$W/logs/postmerge.log" 2>&1 || fail "post-merge worker"
GATE=$(scn bob gate)
echo "   deploy gate: $GATE"
[ "$(echo "$GATE" | cut -c1-64)" = "$(scn bob api resolve rev=main | json_get 'd')" ] || fail "the gate is not at the tested tip"
ok "every landing tested; the gate is at the tip"

step "10. a superfan watches the daemon's telemetry and logs (FR-OP-03…05/08)"
$PY -m scion scion-superfan --url "$DAEMON" --profile daemon --polls 3 --interval 0.3 --json \
  --rule "requests_per_s >= 0 info" > "$W/superfan.jsonl" 2>"$W/logs/superfan.log" || fail "superfan"
$PY - "$W/superfan.jsonl" <<'EOF' || fail "no superfan findings"
import json, sys
findings = [json.loads(line) for line in open(sys.argv[1]) if line.strip()]
assert any(f["kind"] == "threshold" and f["component"] == "scion-daemon" for f in findings), findings
print(f"   ok: {len(findings)} finding(s), e.g. {findings[0]['message']}")
EOF

step "11. a server dies: clients and the cache fail over (NFR-09)"
kill "$PID_server1"; wait "$PID_server1" 2>/dev/null || true
scn alice log -n 1 >/dev/null || fail "the client did not fail over"
printf 'after failover\n' > "$W/after.md"
head=$(scn alice api commit --parent main -m "after failover" --file "docs/after.md=$W/after.md" | json_get 'd["id"]')
cr=$(scn alice api antique.create title="after failover" head="$head" | json_get 'd["id"]')
scn alice api antique.land id="$cr" >/dev/null || fail "landing after failover"
scn dave clone "$W/dave" --objects "$DAEMON" >/dev/null || fail "clone after failover"
[ -f "$W/dave/docs/after.md" ] || fail "the new file did not reach the clone"
ok "queries, landing and a clone through the cache with one server down"

step "12. backup while the system runs, then restore and verify (FR-AD-06, NFR-13)"
admin backup --root "$DEP" --out "$W/backup" | tail -2
admin restore --backup "$W/backup" --root "$W/restored" --deep > "$W/restore.json" || fail "restore"
admin verify --root "$W/restored" --deep | json_get 'd["ok"]' | grep -qx True || fail "verify"
ok "restored deployment verified: every ref's tree and every changeset's blobs present and intact"

step "13. the audit log verifies, with the security-relevant actions recorded (FR-IAM-10)"
scn root audit --verify
scn root audit --limit 200 | awk '{print $5}' | sort | uniq -c | sort -rn | head -8

echo
echo "E2E OK in $(( $(date +%s) - STARTED )) s"
