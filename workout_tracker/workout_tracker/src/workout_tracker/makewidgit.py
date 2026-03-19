#!/usr/bin/env python3
"""Legacy alias for the correctly spelled makewidget.py script."""

import os
import runpy
from pathlib import Path

if __name__ == "__main__":
    target = Path(__file__).with_name("makewidget.py")
    runpy.run_path(str(target), run_name="__main__")
