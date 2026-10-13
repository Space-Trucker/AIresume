"""Scion: agent-scale source control.

A from-scratch implementation of the system described in "Redesigning source control at
Anthropic": server-side changesets with derived data, a want-only object protocol served by
daemon → cache → server tiers, sparse and virtual checkouts, directory-level IAM, and the Antique
code review / landing system.  See README.md and docs/FEATURES.md.
"""

__version__ = "0.1.0"
