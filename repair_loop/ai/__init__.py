"""Optional AI enhancement layer.

This package must never be required by the local-first core engine. It is disabled
unless a future integration explicitly detects an API key and opts in.
"""

import os


def is_enabled() -> bool:
    return bool(os.environ.get("REPAIRLOOP_API_KEY"))
