import logging
import sys

from portfolio_manager.config import log_file_path


def configure_logging():
    log_path = log_file_path()
    root = logging.getLogger()
    if root.handlers:
        return logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | AGENT: %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger(__name__)
