"""Shared test setup. Later milestones add in-process clusters (server → cache → daemon)."""
from __future__ import annotations

import os
import sys
import warnings

warnings.simplefilter("ignore", ResourceWarning)  # per-thread SQLite connections close at exit
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
