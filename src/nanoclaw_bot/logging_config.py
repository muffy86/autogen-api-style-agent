import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_dir: Path | None = None) -> Path:
    """Configure logging with rotating file handler.
    
    Returns the log file path.
    """
    if log_dir is None:
        log_dir = Path.home() / ".nanoclaw"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "bot.log"
    
    # Rotating file handler: 5MB per file, keep 3 backups
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5_000_000, backupCount=3
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    ))
    
    # Configure root nanoclaw_bot logger
    logger = logging.getLogger("nanoclaw_bot")
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return log_file
