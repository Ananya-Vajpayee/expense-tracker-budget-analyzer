"""Central logging setup (writes to logs/app.log)."""
import logging
from pathlib import Path


def setup_logging(log_file: str = "logs/app.log", level=logging.INFO) -> None:
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
