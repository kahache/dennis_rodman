"""
tests/ package — Rodman Historic Feats test suite.
Adds backend/ to sys.path so all modules resolve without installation.
"""
import os
import sys

_TESTS_DIR  = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_TESTS_DIR, "..", "backend"))

if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)
