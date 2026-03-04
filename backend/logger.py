import logging
import sys

# Configure logging format
# Example: 2024-03-04 23:45:01,123 | INFO | backend.main | Received registration request for John
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

def setup_logger(name: str):
    """
    Sets up a logger with a standard format and console output.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers if the logger is already setup
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
        
    return logger
