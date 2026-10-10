"""Đảm bảo repo root luôn nằm trong sys.path khi chạy pytest."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
