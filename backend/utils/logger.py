import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(log_level: str = "INFO", log_file: str = "logs/firewall.log"):
    """
    Configure application logging
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
    """
    
    
    log_dir = Path(log_file).parent
    log_dir.mkdir(exist_ok=True)
    
    
    logger = logging.getLogger("firewall")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    
    logger.handlers.clear()
    
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


logger = setup_logging()


def test_logging():
    """Test all logging levels"""
    print("\nTesting logging system...\n")
    
    logger.debug("This is a DEBUG message (detailed info)")
    logger.info("This is an INFO message (general info)")
    logger.warning("This is a WARNING message (something to watch)")
    logger.error("This is an ERROR message (something went wrong)")
    
    print("\n[✓] Logging test complete!")
    print(f"Check logs/firewall.log for detailed logs\n")

if __name__ == "__main__":
    test_logging()
