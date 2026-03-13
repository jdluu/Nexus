"""Pytest configuration and global fixtures.

This module configures the testing environment and ensures the project root
is included in the Python path for correct module resolution.
"""

import sys
from pathlib import Path

# Incorporate the project root into the system path for module imports.
sys.path.insert(0, str(Path(__file__).parent.parent))
