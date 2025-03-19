#!/usr/bin/env python3
# Ubuntu Pro on Premises (PoP) - contracts.py

"""
Contract data management for Ubuntu Pro on Premises (PoP)
"""

import json
import logging
import tempfile
import subprocess
from typing import Dict, Any


def pull_contract_data(token: str, paths: Dict[str, str]) -> Dict[str, Any]:
    """
    Pull contract data using pro-airgapped
    
    Args:
        token: Ubuntu Pro contract token
        paths: Dictionary of system paths
        
    Returns:
        Dictionary containing contract data
        
    Raises:
        SystemExit: If contract data retrieval fails
    """
    logging.info("Pulling contract data with pro-airgapped")
    
    try:
        # Create a temporary file for the token
        with tempfile.NamedTemporaryFile(mode='w+') as token_file:
            token_file.write(f"{token}:")
            token_file.flush()
            
            # Run pro-airgapped and pipe to yq for JSON output
            result = subprocess.run(
                ["sh", "-c", f"cat {token_file.name} | /usr/bin/pro-airgapped | yq -o=json"],
                capture_output=True,
