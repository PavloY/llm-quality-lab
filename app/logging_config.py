import logging
import sys
import time
from contextlib import contextmanager


def setup_logging(level: int = logging.INFO) -> None:
    """Configure structured logging for the application."""
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger("app")
    root.setLevel(level)
    if not root.handlers:
        root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    return logging.getLogger(name)


@contextmanager
def log_timing(logger: logging.Logger, event: str, **extra):
    """Context manager that logs event with latency_ms on exit.

    Usage:
        with log_timing(logger, "retriever_search", collection="docs"):
            results = retriever.retrieve(query)
    """
    start = time.perf_counter()
    yield
    latency_ms = round((time.perf_counter() - start) * 1000, 1)
    parts = [f"{event} latency_ms={latency_ms}"]
    for k, v in extra.items():
        parts.append(f"{k}={v}")
    logger.info(" ".join(parts))
