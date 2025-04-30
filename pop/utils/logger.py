#!/usr/bin/env python3
# Ubuntu Pro on Premises (PoP) - logger.py
# Revision: 5.0.0

"""
Logging configuration for Ubuntu Pro on Premises (PoP)
"""

import logging
import os
from typing import Optional


def setup_logging(verbose: bool = False, log_file: Optional[str] = "/srv/pop/pop.log"):
    """
    Configure logging for the PoP application.
    
    Args:
        verbose: Enable debug logging if True
        log_file: Path to log file (optional)
        
    Returns:
        None
    """
    # Set up log level based on verbosity
    log_level = logging.DEBUG if verbose else logging.INFO

    # Configure basic logging to console
    console_format = logging.Formatter('[%(levelname)s] %(message)s')
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.propagate = False

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # If log file is provided, add file handler
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_format = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        file_handler.setFormatter(file_format)
        
        # Add handler to root logger
        logger.addHandler(file_handler)
        
        logger.debug(f"Logging configured. Log file: {log_file}")
    else:
        logger.debug("Logging configured for console output only")
