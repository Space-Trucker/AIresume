"""Real price history for the tests that need real market behavior (GT-2, GT-3, GT-5).

This environment can reach PyPI and GitHub but not market-data vendors, so the data comes from files
that public Python projects ship for their own tests and examples. Each source is pinned (a wheel by
version, a GitHub file by commit) and checked against a SHA-256 before anything is read from it.
Nothing downloaded is executed: only CSV text is read. Files are cached in
``trading/goal/.data-cache`` (ignored by git), not committed.

* S&P 500 index, daily, 1999-2018, from ``arch`` 8.0.0 (``arch/data/sp500``);
* Alphabet (GOOG), daily, 2004-2013, and EUR/USD, hourly, 2017-2018, from ``backtesting`` 0.6.6;
* Microsoft (MSFT), daily, 1986-2017, from ``pmdarima`` 2.1.1;
* Oracle (ORCL) 1995-2014, NVIDIA (NVDA) 1999-2014 and Yahoo (YHOO) 1996-2014, daily, split-adjusted,
  from the example data of ``backtrader`` (github.com/mementum/backtrader, ``datas/``).
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import os
import tarfile
import urllib.request
import zipfile
from datetime import datetime

from .spec import HERE

CACHE = os.path.join(HERE, ".data-cache")
WHEELS = {"arch": "8.0.0", "backtesting": "0.6.6", "pmdarima": "2.1.1"}
MEMBERS = {
    "sp500": ("arch", "arch/data/sp500/sp500.csv.gz"),
    "goog": ("backtesting", "backtesting/test/GOOG.csv"),
    "eurusd_h1": ("backtesting", "backtesting/test/EURUSD.csv"),
    "msft": ("pmdarima", "pmdarima/datasets/data/msft.tar.gz"),
}
# files fetched from a pinned GitHub commit: name -> (path in the repository, SHA-256)
GITHUB_REPO, GITHUB_COMMIT = "mementum/backtrader", "b853d7c90b6721476eb5a5ea3135224e33db1f14"
GITHUB_FILES = {
    "orcl": ("datas/orcl-1995-2014.txt", "352b9e0985969d2eb27bfbf65049da3c68fd2a5eebc2d43bec7ccfe553521253"),
    "nvda": ("datas/nvda-1999-2014.txt", "d16ee01711b8a39085a2c3a5d9840bb0ef43091a9e2909e5c819c3020a3ac28f"),
    "yhoo": ("datas/yhoo-1996-2014.txt", "3d75e5763360a2807f821a31448b6d74f7ca1117d538f2e4984ef19b315a6c6d"),
}


def _wheel(package: str) -> bytes:
    version = WHEELS[package]
    path = os.path.join(CACHE, f"{package}-{version}.whl")
    if os.path.exists(path):
        return open(path, "rb").read()
    with urllib.request.urlopen(f"https://pypi.org/pypi/{package}/{version}/json", timeout=60) as r:
        meta = json.load(r)
    files = [f for f in meta["urls"] if f["filename"].endswith(".whl")]
    # any wheel of the release carries the same data files; prefer a pure-Python or Linux x86-64 one
    files.sort(key=lambda f: ("none-any" not in f["filename"], "manylinux" not in f["filename"]
                              or "x86_64" not in f["filename"], f["filename"]))
    f = files[0]
    with urllib.request.urlopen(f["url"], timeout=120) as r:
        data = r.read()
    if hashlib.sha256(data).hexdigest() != f["digests"]["sha256"]:
        raise RuntimeError(f"{f['filename']}: SHA-256 does not match PyPI")
    os.makedirs(CACHE, exist_ok=True)
    with open(path, "wb") as out:
        out.write(data)
    return data


def _github(name: str) -> bytes:
    member, digest = GITHUB_FILES[name]
    url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_COMMIT}/{member}"
    with urllib.request.urlopen(url, timeout=120) as r:
        raw = r.read()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise RuntimeError(f"{member}: SHA-256 does not match the pinned value")
    return raw


def _csv_text(name: str) -> str:
    path = os.path.join(CACHE, f"{name}.csv")
    if os.path.exists(path):
        return open(path).read()
    if name in GITHUB_FILES:
        text = _github(name).decode("utf-8")
        os.makedirs(CACHE, exist_ok=True)
        with open(path, "w") as out:
            out.write(text)
        return text
    package, member = MEMBERS[name]
    raw = zipfile.ZipFile(io.BytesIO(_wheel(package))).read(member)
    if member.endswith(".csv.gz"):
        raw = gzip.decompress(raw)
    elif member.endswith(".tar.gz"):
        with tarfile.open(fileobj=io.BytesIO(raw)) as t:
            raw = next(t.extractfile(m).read() for m in t.getmembers() if m.isfile() and m.name.endswith(".csv"))
    text = raw.decode("utf-8")
    os.makedirs(CACHE, exist_ok=True)
    with open(path, "w") as out:
        out.write(text)
    return text


def bars(name: str) -> list[dict]:
    """Rows with date (datetime), open, high, low, close, oldest first."""
    rows = []
    for row in csv.DictReader(io.StringIO(_csv_text(name))):
        key = row.get("Date") or row.get("") or next(iter(row.values()))
        for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
            try:
                when = datetime.strptime(key, fmt)
                break
            except ValueError:
                continue
        else:
            continue
        try:
            o, h, lo, c = (float(row[k]) for k in ("Open", "High", "Low", "Close"))
        except (KeyError, ValueError):
            continue
        if min(o, h, lo, c) <= 0:
            continue
        rows.append({"date": when, "open": o, "high": h, "low": lo, "close": c})
    rows.sort(key=lambda r: r["date"])
    return rows


def available() -> tuple[bool, str]:
    try:
        bars("sp500")
        return True, "ok"
    except Exception as e:  # noqa: BLE001 - offline or blocked
        return False, f"{type(e).__name__}: {e}"
