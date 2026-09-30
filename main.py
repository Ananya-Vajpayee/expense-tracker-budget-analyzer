"""Entry point: python main.py <command>  (run without args for the menu)."""
import sys

from src.cli import run
from src.logger_config import setup_logging

if __name__ == "__main__":
    setup_logging()
    sys.exit(run())
