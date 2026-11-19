"""Test configuration: use an in-memory database and make `app`/`ml` importable."""
import os
import sys
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
