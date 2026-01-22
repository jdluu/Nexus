"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

# Add project root to path so we can import nexus
sys.path.insert(0, str(Path(__file__).parent.parent))
