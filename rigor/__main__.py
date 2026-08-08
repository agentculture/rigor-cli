"""Entry point for ``python -m rigor``."""

from __future__ import annotations

import sys

from rigor.cli import main

if __name__ == "__main__":
    sys.exit(main())
