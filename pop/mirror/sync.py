"""
Mirror synchronization functionality for Ubuntu Pro on Premises (PoP)
"""

import os
import re
import logging
import subprocess
from typing import Dict, Optional

from pop.utils.system import run_command


def run_apt_mirror(paths: Dict[str, str]) -> bool:
    """
    Run apt-mirror to start the initial mirror download
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        True if successful, False otherwise
    """
    logging.info("Running apt-mirror for initial repository download")
    
    try:
        # Run apt-mirror with the generated mirror list
        result = run_command(
            ["apt-mirror", paths["pop_apt_mirror_list"]],
            capture_output=True
        )
        
        # Extract information from output
        output = result
        
        # Look for download size
        size_match = re.search(r'([0-9.]+) ([KMG]iB) will be downloaded into archive', output)
        if size_match:
            size = f"{size_match.group(1)} {size_match.group(2)}"
            logging.info(f"Downloaded {size} of packages")
        
        # Look for cleanup info
        cleanup_match = re.search(r'([0-9.]+) ([KMG]iB)? in ([0-9]+) files and ([0-9]+) directories can be freed', output)
        if cleanup_match:
            cleanup_size = f"{cleanup_match.group(1)} {cleanup_match.group(2) or 'bytes'}"
            cleanup_files = cleanup_match.group(3)
            cleanup_dirs = cleanup_match.group(4)
            logging.info(f"{cleanup_size} in {cleanup_files} files and {cleanup_dirs} directories can be freed")
            logging.info("Run /var/spool/apt-mirror/var/clean.sh to free space")
        
        logging.info("apt-mirror completed successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to run apt-mirror: {e}")
        return False


def verify_mirror(paths: Dict[str, str]) -> Dict[str, str]:
    """
    Verify mirror structure and get statistics
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        Dictionary with mirror statistics
    """
    mirror_path = "/var/spool/apt-mirror/mirror"
    stats = {
        "status": "Not available",
        "last_update": "Never",
        "total_size": "0 GB",
        "total_files": "0"
    }
    
    if not os.path.exists(mirror_path):
        logging.warning(f"Mirror directory does not exist: {mirror_path}")
        return stats
    
    # Get last update time
    try:
        last_update = run_command(
            ["stat", "-c", "%y", mirror_path], 
            capture_output=True
        )
        stats["last_update"] = last_update.strip()
    except:
        pass
        
    # Get total size
    try:
        total_size = run_command(
            ["du", "-sh", mirror_path], 
            capture_output=True
        ).split()[0]
        stats["total_size"] = total_size
    except:
        pass
        
    # Get total files
    try:
        total_files = run_command(
            ["find", mirror_path, "-type", "f", "|", "wc", "-l"], 
            capture_output=True,
            shell=True
        )
        stats["total_files"] = total_files.strip()
    except:
        pass
    
    stats["status"] = "Available"
    return stats


def run_mirror_cleanup(paths: Dict[str, str]) -> bool:
    """
    Run apt-mirror cleanup script to free space
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        True if successful, False otherwise
    """
    logging.info("Running apt-mirror cleanup")
    cleanup_script = "/var/spool/apt-mirror/var/clean.sh"
    
    if not os.path.exists(cleanup_script):
        logging.warning(f"Cleanup script not found: {cleanup_script}")
        return False
    
    try:
        result = run_command([cleanup_script], capture_output=True)
        logging.info("Cleanup completed successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to run cleanup: {e}")
        return False
