#!/usr/bin/env bash
# End-to-end demo with real processes: scion-server -> scion-cache -> scion-daemon -> scn.
#
#   ./examples/demo.sh [path-to-a-git-repo]
#
# It ingests a git repository (default: the repository containing this folder), starts the
# three tiers, does a sparse checkout through the daemon's Unix socket, commits on the server,
# reviews and lands the change with Antique, and shows history, blame, search and tier stats.
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
GIT_SRC="${1:-$(cd "$HERE/.." && pwd)}"
WORK="$(mktemp -d /tmp/scion-demo.XXXXXX)"
export PYTHONPATH="$HERE"
PY="${PYTHON:-python3}"
scion() { "$PY" -m scion "$@"; }
PIDS=()
cleanup() { for p in "${PIDS[@]}"; do kill "$p" 2>/dev/null || true; done; wait 2>/dev/null || true; }
trap cleanup EXIT

# Plain HTTP GET without any proxy (curl and urllib honor proxy variables, even for localhost).
get() { "$PY" -c 'import http.client,sys,urllib.parse as u; p=u.urlparse(sys.argv[1]); c=http.client.HTTPConnection(p.hostname,p.port,timeout=2); c.request("GET",p.path); r=c.getresponse(); sys.stdout.write(r.read().decode()); sys.exit(r.status!=200)' "$1"; }
port() { "$PY" -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1])'; }
SERVER_PORT=$(port); CACHE_PORT=$(port)
SERVER="http://127.0.0.1:$SERVER_PORT"; CACHE="http://127.0.0.1:$CACHE_PORT"
SOCK="$WORK/daemon.sock"

cat > "$WORK/policy.json" <<'EOF'
{
  "admins": ["admin"],
  "protected_refs": {"main": ["antique", "admin"]},
  "review": {"rules": [{"prefix": "", "logic": {"approvals": 1}, "comment_only": {"approvals": 0}, "docs": {"approvals": 0}}]}
}
EOF

echo "== ingesting $GIT_SRC"
scion scion-admin ingest --repo "$WORK/repo" --policy "$WORK/policy.json" --git "$GIT_SRC" --rev HEAD --ref main --verify
scion scion-admin snapshot --repo "$WORK/repo" --rev main --out "$WORK/snapshots" >/dev/null

echo "== starting scion-server, scion-cache, scion-daemon"
scion scion-server --repo "$WORK/repo" --policy "$WORK/policy.json" --listen "127.0.0.1:$SERVER_PORT" & PIDS+=($!)
scion scion-cache --listen "127.0.0.1:$CACHE_PORT" --upstream "$SERVER" & PIDS+=($!)
scion scion-daemon --socket "$SOCK" --upstream "$CACHE" --store "$WORK/daemon-store" --snapshot-dir "$WORK/snapshots" & PIDS+=($!)
for _ in $(seq 100); do [ -S "$SOCK" ] && get "$SERVER/healthz" >/dev/null 2>&1 && break; sleep 0.1; done

echo "== sparse checkout through the daemon socket"
FIRST_DIR=$(scion scn --server "$SERVER" ls | awk '$1=="d"{print $2; exit}')
if [ -n "$FIRST_DIR" ]; then SPARSE=(--sparse "$FIRST_DIR"); else SPARSE=(); fi
scion scn --server "$SERVER" --user dev clone "$WORK/wc" --objects "unix:$SOCK" "${SPARSE[@]}"
cd "$WORK/wc"
scion scn log --oneline -n 5

echo "== edit, commit on the server (nothing to push), review, land"
mkdir -p notes && echo "Hello from Scion" > notes/hello.md
scion scn add notes
scion scn commit -m "Add a note"
scion scn review create --title "Add a note" >/dev/null
scion scn review land 1
scion scn --server "$SERVER" log --oneline -n 3 -r main

echo "== history, blame, search (all answered by the server)"
scion scn history notes/hello.md
scion scn blame notes/hello.md
scion scn search hello
scion scn review landing --cs "$(scion scn --server "$SERVER" api resolve rev=main | tr -d '"')"

echo "== tier stats"
get "$CACHE/stats" | "$PY" -c 'import json,sys; s=json.load(sys.stdin)["cache"]; print("cache:", {k: s[k] for k in ("hits","misses","hit_rate")})'
echo "demo workspace: $WORK"
