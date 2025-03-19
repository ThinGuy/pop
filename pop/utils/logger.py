#!/usr/bin/env python3
# Ubuntu Pro on Premises (PoP) - logger.py
# Revision: 5.0.0

"""
Logging configuration for Ubuntu Pro on Premises (PoP)
"""

import logging
import os
from typing import Optional


def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> None:
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
    console_format = '[%(levelname)s] %(message)s'
    logging.basicConfig(level=log_level, format=console_format)
    
    # If log file is provided, add file handler
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)
        
        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        
        logging.debug(f"Logging configured. Log file: {log_file}")
    else:
        logging.debug("Logging configured for console output only")
