"""
Pytest configuration file.
This file is automatically loaded by pytest and adds the project root to sys.path
so that imports work correctly.
"""
import sys
import os
from pathlib import Path

# Get the project root directory (parent of tests directory)
project_root = Path(__file__).parent.parent

# Add project root to Python path if not already there
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
