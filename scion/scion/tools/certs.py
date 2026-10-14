"""Development certificates for TLS and mutual TLS between tiers (ADR-14).

Shells out to the ``openssl`` command-line tool, which must be installed; Scion itself only uses
Python's ``ssl`` module. Production deployments use their own PKI: a certificate per server and
cache (with the hosts they are reached by) and a client certificate whose common name is the
service principal for each cache (``scion-cache``) and daemon (``scion-daemon``).
"""
from __future__ import annotations

import os
import subprocess

EC = ["-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:prime256v1", "-nodes"]


def _run(args: list[str], cwd: str) -> None:
    subprocess.run(["openssl", *args], cwd=cwd, check=True, capture_output=True)


def make_ca(directory: str, name: str = "ca", subject: str = "Scion Development CA") -> str:
    """Create ``<name>.pem`` and ``<name>.key``; returns the certificate's path."""
    os.makedirs(directory, exist_ok=True)
    _run(["req", "-x509", *EC, "-keyout", f"{name}.key", "-out", f"{name}.pem", "-days", "3650",
          "-subj", f"/CN={subject}",
          "-addext", "basicConstraints=critical,CA:TRUE",
          "-addext", "keyUsage=critical,keyCertSign,cRLSign",
          "-addext", "subjectKeyIdentifier=hash"], directory)
    return os.path.join(directory, f"{name}.pem")


def make_cert(directory: str, name: str, common_name: str, ca: str = "ca",
              hosts: tuple[str, ...] = ("localhost", "127.0.0.1")) -> tuple[str, str]:
    """Create ``<name>.pem``/``<name>.key`` signed by ``<ca>``, usable as a server certificate for
    ``hosts`` and as a client certificate naming ``common_name``. Returns (cert, key)."""
    sans = ",".join(f"IP:{h}" if h.replace(".", "").isdigit() or ":" in h else f"DNS:{h}" for h in hosts)
    ext = os.path.join(directory, f"{name}.ext")
    with open(ext, "w") as f:
        f.write("basicConstraints=critical,CA:FALSE\n"
                "keyUsage=critical,digitalSignature,keyEncipherment\n"
                "extendedKeyUsage=serverAuth,clientAuth\n"
                "subjectKeyIdentifier=hash\n"
                "authorityKeyIdentifier=keyid,issuer\n"
                f"subjectAltName={sans}\n")
    _run(["req", *EC, "-keyout", f"{name}.key", "-out", f"{name}.csr", "-subj", f"/CN={common_name}"], directory)
    _run(["x509", "-req", "-in", f"{name}.csr", "-CA", f"{ca}.pem", "-CAkey", f"{ca}.key", "-CAcreateserial",
          "-out", f"{name}.pem", "-days", "825", "-extfile", ext], directory)
    os.unlink(os.path.join(directory, f"{name}.csr"))
    os.unlink(ext)
    return os.path.join(directory, f"{name}.pem"), os.path.join(directory, f"{name}.key")


def make_dev_pki(directory: str) -> dict:
    """A CA plus certificates for a server, a cache and a daemon."""
    make_ca(directory)
    out = {"ca": os.path.join(directory, "ca.pem")}
    for name, cn in (("server", "scion-server"), ("cache", "scion-cache"), ("daemon", "scion-daemon")):
        out[name] = make_cert(directory, name, cn)
    return out
