"""Antique's review pages (FR-RV-08/09, ADR-17).

Server-rendered HTML with plain forms: no client-side code. Signing in gives a session cookie
(HttpOnly, SameSite=Strict, Secure over TLS); every form carries the session's CSRF token. The
actions call the same Antique code paths as the RPCs, with the same permission checks. Line
comments are shown inline in the diff (D-04).
"""
from __future__ import annotations

import difflib
import hashlib
import hmac
import html
import secrets
import threading
import time
from urllib.parse import parse_qs, quote

from .antique import Retryable
from .iam import PermissionDenied
from .objects import is_binary
from .repo import MergeConflict, NotFound

SESSION_SECONDS = 12 * 3600
COOKIE = "scion_session"

CSS = """
:root{--bg:#fbfaf7;--fg:#1f1e1c;--muted:#6b675f;--line:#e4e0d6;--accent:#b4541a;--ok:#2f7a3d;--bad:#a8322a;
--add:#e6f4ea;--del:#fbe9e7;--note:#fff6dd}
@media (prefers-color-scheme:dark){:root{--bg:#191817;--fg:#ecebe6;--muted:#a29d92;--line:#34322e;--accent:#e08a4d;
--ok:#6cc27c;--bad:#ef7b70;--add:#1e3324;--del:#3a2220;--note:#3a3320}}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0 auto;max-width:1040px;padding:24px 16px}
a{color:var(--accent)} table{border-collapse:collapse;width:100%} td,th{border-bottom:1px solid var(--line);padding:4px 8px;
text-align:left;vertical-align:top} .muted{color:var(--muted)} .ok{color:var(--ok)} .bad{color:var(--bad)}
pre,code,.diff td{font:13px/1.4 ui-monospace,monospace} .diff{margin:8px 0 20px} .diff td.n{color:var(--muted);width:3em;
text-align:right;user-select:none} .diff tr.add{background:var(--add)} .diff tr.del{background:var(--del)}
.diff tr.note td{background:var(--note);font:14px/1.4 system-ui,sans-serif} form.inline{display:inline}
textarea,input[type=text],input[type=password]{width:100%;box-sizing:border-box;font:inherit} button{font:inherit}
"""


class ReviewUI:
    def __init__(self, service):
        self.service = service  # ScionService: deployment, identity, antique(repo)
        self._sessions: dict[str, dict] = {}
        self._lock = threading.Lock()

    # -- sessions ---------------------------------------------------------------------------------
    def _credential(self, user: str) -> str | None:
        """A digest of the user's stored token: a session lasts only while it is unchanged, so
        removing or rotating a token ends the user's sessions at their next request, as it refuses
        their RPCs (FR-IAM-01)."""
        stored = self.service.identity.tokens.get(user)
        return None if stored is None else hashlib.sha256(stored.encode()).hexdigest()

    def _session(self, headers) -> dict | None:
        raw = headers.get("Cookie") or ""
        for part in raw.split(";"):
            k, _, v = part.strip().partition("=")
            if k == COOKIE:
                with self._lock:
                    s = self._sessions.get(v)
                    if s and s["expires"] > time.time() and s["credential"] == self._credential(s["user"]):
                        return s
                    self._sessions.pop(v, None)
        return None

    def _new_session(self, user: str) -> tuple[str, dict]:
        sid = secrets.token_urlsafe(32)
        s = {"user": user, "csrf": secrets.token_urlsafe(32), "expires": time.time() + SESSION_SECONDS,
             "credential": self._credential(user)}
        with self._lock:
            now = time.time()
            for k in [k for k, v in self._sessions.items() if v["expires"] <= now]:
                del self._sessions[k]
            self._sessions[sid] = s
        return sid, s

    def _cookie(self, sid: str, secure: bool, max_age: int = SESSION_SECONDS) -> str:
        return (f"{COOKIE}={sid}; Path=/antique; Max-Age={max_age}; HttpOnly; SameSite=Strict"
                + ("; Secure" if secure else ""))

    # -- responses ------------------------------------------------------------------------------------
    @staticmethod
    def _page(title: str, body: str, user: str | None = None, csrf: str | None = None) -> bytes:
        who = ""
        if user:
            who = (f"<p class=muted>Signed in as <b>{html.escape(user)}</b> · "
                   f"<form class=inline method=post action=/antique/logout><input type=hidden name=csrf "
                   f"value='{html.escape(csrf or '')}'><button>Sign out</button></form></p>")
        return (f"<!doctype html><html lang=en><head><meta charset=utf-8>"
                f"<meta name=viewport content='width=device-width,initial-scale=1'><title>{html.escape(title)}</title>"
                f"<style>{CSS}</style></head><body>{who}{body}</body></html>").encode()

    @staticmethod
    def _headers(extra=None) -> dict:
        h = {"Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; "
                                        "frame-ancestors 'none'",
             "X-Content-Type-Options": "nosniff", "Referrer-Policy": "same-origin", "Cache-Control": "no-store"}
        h.update(extra or {})
        return h

    def _html(self, status: int, title: str, body: str, session=None, extra=None):
        return (status, "text/html; charset=utf-8",
                self._page(title, body, session and session["user"], session and session["csrf"]), self._headers(extra))

    @staticmethod
    def _redirect(location: str, extra=None):
        return 303, "text/plain", b"", {"Location": location, "Cache-Control": "no-store", **(extra or {})}

    # -- dispatch ------------------------------------------------------------------------------------
    def handle(self, method: str, path: str, query: dict, headers, body: bytes, secure: bool):
        parts = [p for p in path.split("/") if p]
        if not parts or parts[0] != "antique":
            return None
        try:
            if parts == ["antique", "login"]:
                return self._login(method, body, secure)
            session = self._session(headers)
            if session is None:
                if method == "GET":
                    return self._redirect("/antique/login")
                return self._html(401, "Sign in", "<p>Please <a href=/antique/login>sign in</a>.</p>")
            if method == "POST":
                form = parse_qs(body.decode("utf-8", "replace"), keep_blank_values=True)
                csrf = (form.get("csrf") or [""])[0]
                if not hmac.compare_digest(csrf.encode(), session["csrf"].encode()):
                    return self._html(403, "Forbidden", "<p class=bad>Invalid form token. Reload the page.</p>", session)
                if parts == ["antique", "logout"]:
                    with self._lock:
                        self._sessions = {k: v for k, v in self._sessions.items() if v is not session}
                    return self._redirect("/antique/login", {"Set-Cookie": self._cookie("", secure, 0)})
                if len(parts) == 5 and parts[2] == "cr" and parts[4] in ("approve", "comment", "land"):
                    return self._action(session, parts[1], int(parts[3]), parts[4], form)
                return None
            if parts == ["antique"]:
                return self._index(session, (query.get("repo") or [None])[0], (query.get("state") or ["open"])[0])
            if len(parts) == 4 and parts[2] == "cr":
                return self._cr_page(session, parts[1], int(parts[3]))
            return None
        except MergeConflict:
            return self._redirect(path.rsplit("/", 1)[0])  # the CR page shows the conflicts
        except (PermissionDenied, NotFound, ValueError, Retryable) as e:
            status = (403 if isinstance(e, PermissionDenied) else 404 if isinstance(e, NotFound)
                      else 503 if isinstance(e, Retryable) else 400)
            return self._html(status, "Error", f"<p class=bad>{html.escape(str(e))}</p><p><a href=/antique>Back</a></p>",
                              self._session(headers))

    # -- pages ------------------------------------------------------------------------------------------
    def _login(self, method: str, body: bytes, secure: bool):
        tokens = self.service.identity.tokens_required
        if method == "POST":
            form = parse_qs(body.decode("utf-8", "replace"))
            user = (form.get("user") or [""])[0].strip()
            token = (form.get("token") or [""])[0]
            if user and (not tokens or self.service.identity.check_token(user, token)):
                sid, _ = self._new_session(user)
                return self._redirect("/antique", {"Set-Cookie": self._cookie(sid, secure)})
            return self._html(401, "Sign in", "<p class=bad>Unknown user or wrong token.</p>" + self._login_form(tokens))
        return self._html(200, "Sign in", "<h1>Antique</h1>" + self._login_form(tokens))

    @staticmethod
    def _login_form(tokens: bool) -> str:
        token = "<p><label>Token<input type=password name=token></label></p>" if tokens else ""
        return (f"<form method=post action=/antique/login><p><label>User<input type=text name=user></label></p>"
                f"{token}<button>Sign in</button></form>")

    def _repo(self, session, name: str):
        repo = self.service.deployment.repo(name)
        if not repo.policy.can_read_repo(session["user"]):
            raise PermissionDenied(f"{session['user']} may not read repository {repo.name}")
        return repo

    def _index(self, session, repo_name, state):
        names = [r["name"] for r in self.service.readable_repos(session["user"])]
        repo_name = repo_name or (names[0] if names else None)
        tabs = " · ".join(f"<a href='/antique?repo={quote(n)}&state={quote(state)}'>{html.escape(n)}</a>" for n in names)
        if repo_name is None:
            return self._html(200, "Antique", f"<h1>Antique</h1><p>No repositories.</p>", session)
        self._repo(session, repo_name)
        a = self.service.antique(repo_name)
        rows = []
        for cr in a.list(state if state != "all" else None, limit=200):
            rows.append(f"<tr><td><a href='/antique/{quote(repo_name)}/cr/{cr['id']}'>#{cr['id']}</a></td>"
                        f"<td>{html.escape(cr['title'])}</td><td>{html.escape(cr['author'])}</td>"
                        f"<td>{html.escape(cr['state'])}</td><td><code>{cr['head'][:12]}</code></td></tr>")
        states = " · ".join(f"<a href='/antique?repo={quote(repo_name)}&state={s}'>{s}</a>"
                            for s in ("open", "landing", "conflict", "landed", "abandoned", "all"))
        body = (f"<h1>Antique</h1><p class=muted>{tabs}</p><h2>{html.escape(repo_name)}: {html.escape(state)}</h2>"
                f"<p class=muted>{states}</p><table><tr><th>CR</th><th>Title</th><th>Author</th><th>State</th>"
                f"<th>Head</th></tr>{''.join(rows) or '<tr><td colspan=5>None.</td></tr>'}</table>")
        return self._html(200, f"Antique: {repo_name}", body, session)

    def _cr_page(self, session, repo_name: str, cr_id: int):
        repo = self._repo(session, repo_name)
        a = self.service.antique(repo_name)
        user, csrf = session["user"], html.escape(session["csrf"])
        cr = a.view(a.get(cr_id), user)
        hidden = f"<input type=hidden name=csrf value='{csrf}'>"
        seen = f"<input type=hidden name=rev value='{cr['revision']}'>"  # the revision this page shows
        action = f"/antique/{quote(repo_name)}/cr/{cr_id}"
        out = [f"<p><a href='/antique?repo={quote(repo_name)}'>&larr; all change requests</a></p>",
               f"<h1>#{cr['id']} {html.escape(cr['title'])}</h1>",
               f"<p class=muted>{html.escape(cr['author'])} · <b>{html.escape(cr['state'])}</b> · target "
               f"<code>{html.escape(cr['target'])}</code> · revision {cr['revision']} · head <code>{cr['head'][:12]}</code></p>",
               f"<p>{html.escape(cr['description'])}</p>"]
        req = cr.get("requirements")
        if req:
            out.append("<h2>Approval requirements</h2><table><tr><th>Scope</th><th>Category</th><th>Needs</th>"
                       "<th>Has</th><th></th></tr>")
            for g in req["groups"]:
                need = f"{g['need']['approvals']} approval(s)" + (
                    f", {g['need']['owner_approvals']} from {html.escape(', '.join(g['owners']))}"
                    if g["need"]["owner_approvals"] else "")
                have = f"{g['have']['approvals']} ({g['have']['owner_approvals']} owner)"
                mark = "<span class=ok>✓</span>" if g["satisfied"] else "<span class=bad>✗</span>"
                out.append(f"<tr><td><code>/{html.escape(g['prefix'])}</code></td><td>{g['category']}</td>"
                           f"<td>{need}</td><td>{have}</td><td>{mark}</td></tr>")
            out.append("</table>")
        if cr.get("conflict"):
            hidden_paths = cr["conflict"].get("hidden", 0)
            out.append("<h2 class=bad>Conflicts</h2><ul>" + "".join(
                f"<li><code>{html.escape(c['path'])}</code>: {html.escape(c['reason'])}</li>"
                for c in cr["conflict"]["conflicts"]) + (
                f"<li>{hidden_paths} in files you can't read</li>" if hidden_paths else "") + "</ul>")
        out.append("<h2>Approvals</h2><ul>" + ("".join(
            f"<li>{html.escape(x['user'])} (revision {x['rev']})</li>" for x in cr["approvals"]) or "<li>None yet.</li>")
            + "</ul>")
        if cr["state"] in ("open", "conflict"):
            out.append(f"<p><form class=inline method=post action='{action}/approve'>{hidden}{seen}"
                       f"<button>Approve revision {cr['revision']}</button></form> "
                       f"<form class=inline method=post action='{action}/land'>{hidden}{seen}<button>Land</button></form></p>")
        general = [c for c in cr["comments"] if not c["path"]]
        out.append("<h2>Comments</h2>" + ("".join(self._comment(c) for c in general) or "<p class=muted>None.</p>"))
        out.append(f"<form method=post action='{action}/comment'>{hidden}<p><textarea name=body rows=3 required></textarea></p>"
                   f"<p><label>Path (optional)<input type=text name=path></label></p>"
                   f"<p><label>Line (optional)<input type=text name=line inputmode=numeric></label></p>"
                   f"<button>Comment</button></form>")
        out.append("<h2>Diff</h2>" + self._diff(repo, a, cr, user))
        return self._html(200, f"CR {cr_id}", "".join(out), session)

    @staticmethod
    def _comment(c) -> str:
        where = f" on <code>{html.escape(c['path'])}:{c['line']}</code>" if c["path"] and c["line"] else (
            f" on <code>{html.escape(c['path'])}</code>" if c["path"] else "")
        return (f"<p><b>{html.escape(c['user'])}</b>{where} <span class=muted>(revision {c['rev']})</span><br>"
                f"{html.escape(c['body'])}</p>")

    def _diff(self, repo, a, cr, user) -> str:
        if cr["state"] == "landed":  # everything the landing added: beneath its bottom changeset
            stack = a.landing_stack(cr["landed_cs"]) or [cr["landed_cs"]]
            base = repo.get_changeset(stack[-1]).first_parent
        else:
            base = a.base_of(cr)
        notes: dict[str, dict[int, list]] = {}
        loose: dict[str, list] = {}
        for c in cr["comments"]:
            if c["path"] and c["line"]:
                notes.setdefault(c["path"], {}).setdefault(c["line"], []).append(c)
            elif c["path"]:
                loose.setdefault(c["path"], []).append(c)
        parts = []
        for f in repo.diff(base, cr["head"], user=user):
            path = f["path"]
            old = repo.read_blob(f["old"]["id"]) if f["old"] else b""
            new = repo.read_blob(f["new"]["id"]) if f["new"] else b""
            parts.append(f"<h3><code>{html.escape(path)}</code> <span class=muted>{f['status']}</span></h3>")
            parts.extend(self._comment(c) for c in loose.get(path, []))
            if is_binary(old) or is_binary(new):
                parts.append("<p class=muted>Binary file.</p>")
                continue
            parts.append(self._file_table(old.decode("utf-8", "replace").splitlines(),
                                          new.decode("utf-8", "replace").splitlines(), notes.get(path, {})))
        return "".join(parts) or "<p class=muted>No changes visible to you.</p>"

    def _file_table(self, old: list[str], new: list[str], notes: dict[int, list]) -> str:
        rows = []
        shown_notes = set()

        def note_rows(line_no):
            if line_no in notes and line_no not in shown_notes:
                shown_notes.add(line_no)
                for c in notes[line_no]:
                    rows.append(f"<tr class=note><td></td><td></td><td>{self._comment(c)}</td></tr>")

        for group in difflib.SequenceMatcher(None, old, new, autojunk=False).get_grouped_opcodes(3):
            rows.append("<tr><td class=n>…</td><td class=n>…</td><td></td></tr>")
            for tag, i1, i2, j1, j2 in group:
                if tag == "equal":
                    for k in range(i2 - i1):
                        rows.append(f"<tr><td class=n>{i1 + k + 1}</td><td class=n>{j1 + k + 1}</td>"
                                    f"<td>&nbsp;{html.escape(old[i1 + k])}</td></tr>")
                        note_rows(j1 + k + 1)
                    continue
                for k in range(i1, i2):
                    rows.append(f"<tr class=del><td class=n>{k + 1}</td><td class=n></td><td>-{html.escape(old[k])}</td></tr>")
                for k in range(j1, j2):
                    rows.append(f"<tr class=add><td class=n></td><td class=n>{k + 1}</td><td>+{html.escape(new[k])}</td></tr>")
                    note_rows(k + 1)
        leftover = [c for line, cs in sorted(notes.items()) if line not in shown_notes for c in cs]
        table = f"<table class=diff>{''.join(rows)}</table>"
        return table + "".join(self._comment(c) for c in leftover)

    # -- actions --------------------------------------------------------------------------------------
    def _action(self, session, repo_name: str, cr_id: int, what: str, form: dict):
        repo = self._repo(session, repo_name)
        a = self.service.antique(repo_name)
        user = session["user"]
        rev = (form.get("rev") or [""])[0].strip()
        rev = int(rev) if rev else None  # the revision the page showed: acting on a newer one is refused
        if what == "approve":
            a.approve(user, cr_id, rev)
        elif what == "comment":
            body = (form.get("body") or [""])[0]
            path = (form.get("path") or [""])[0].strip() or None
            line = (form.get("line") or [""])[0].strip()
            if path is not None and not repo.policy.can_read(user, path):
                raise PermissionDenied(f"{user} may not read {path}")
            a.comment(user, cr_id, body, path, int(line) if line else None)
        else:
            a.land(user, cr_id, rev=rev)
        return self._redirect(f"/antique/{quote(repo_name)}/cr/{cr_id}")
