# app/core/logging.py

import logging
import sys

def init_logging() -> None:
    """
    Configure root logger to output INFO+ messages to stdout
    with a timestamped format.
    """
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    # remove any existing handlers, then add ours
    if root.handlers:
        root.handlers.clear()
    root.addHandler(handler)
