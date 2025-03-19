"""
System utilities for Ubuntu Pro on Premises (PoP)
"""

import os
import sys
import subprocess
import logging
import shutil
from typing import Dict, List, Optional


def check_sudo():
    """
    Check if script is running with sudo/root privileges
    
    Raises:
        SystemExit: If not running with sudo
    """
    if os.geteuid() != 0:
        logging.error("This script must be run with sudo privileges")
        sys.exit(1)
    logging.info("Running with sudo privileges")


def get_current_lts() -> str:
    """
    Get the current LTS release codename
    
    Returns:
        str: LTS release codename (e.g., 'jammy')
    """
    # Default fallback value
    DEFAULT_RELEASE = "jammy"
    
    try:
        lts = subprocess.check_output(
            ["ubuntu-distro-info", "-c", "--lts"], 
            text=True
        ).strip()
        return lts.lower()
    except (subprocess.SubprocessError, FileNotFoundError):
        logging.warning(f"Could not determine current LTS, using default: {DEFAULT_RELEASE}")
        return DEFAULT_RELEASE


def get_system_fqdn_or_ip() -> str:
    """
    Get the system's FQDN or IP address for use as default mirror host
    
    Returns:
        str: FQDN, primary IP, or 'localhost' if neither is available
    """
    try:
        # First try to get FQDN using hostname -f
        fqdn = subprocess.check_output(["hostname", "-f"], text=True).strip()
        if fqdn and not fqdn.startswith("localhost"):
            return fqdn
    except subprocess.SubprocessError:
        pass
    
    # If FQDN not available, try to get the primary IP address
    try:
        # Get all IP addresses and pick the first non-localhost one
        ip_output = subprocess.check_output(
            ["hostname", "-I"], text=True
        ).strip().split()
        
        for ip in ip_output:
            if not ip.startswith("127."):
                return ip
    except subprocess.SubprocessError:
        pass
    
    # Fallback to localhost if nothing else works
    return "localhost"


def create_directories(paths: Dict[str, str]) -> None:
    """
    Create required directories for PoP
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        None
    """
    logging.info("Creating required directories")
    
    # Create main directories
    for directory in [
        paths["pop_dir"],
        f"{paths['pop_dir']}/debs/partial",
        f"{paths['pop_dir']}/etc/apt/auth.conf.d", 
        f"{paths['pop_dir']}/etc/apt/trusted.gpg.d"
    ]:
        os.makedirs(directory, exist_ok=True)
    
    # Set up logging
    log_file = paths["pop_log"]
    if os.path.exists(log_file):
        # Backup existing log
        shutil.move(log_file, f"{log_file}.last")
    
    # Create empty log file
    with open(log_file, 'w') as f:
        pass
    
    logging.info("Directory structure created successfully")
    
    # Set permissions for apt cache
    debs_partial = f"{paths['pop_dir']}/debs/partial"
    try:
        subprocess.run(["chown", "-R", "_apt:root", debs_partial], check=True)
        subprocess.run(["chmod", "-R", "700", debs_partial], check=True)
        logging.info("Set permissions on apt cache directory")
    except subprocess.SubprocessError as e:
        logging.warning(f"Could not set permissions on apt cache directory: {e}")


def run_command(cmd: List[str], capture_output: bool = False, 
                check: bool = True, shell: bool = False) -> Optional[str]:
    """
    Run a system command with proper error handling
    
    Args:
        cmd: Command to run as a list of strings
        capture_output: Whether to capture and return command output
        check: Whether to check command return code
        shell: Whether to run command in shell
        
    Returns:
        Command output if capture_output is True, None otherwise
        
    Raises:
        SystemExit: If command fails and check is True
    """
    try:
        if shell and isinstance(cmd, list):
            cmd = " ".join(cmd)
            
        logging.debug(f"Running command: {cmd}")
        
        if capture_output:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=check,
                shell=shell
            )
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=check, shell=shell)
            return None
            
    except subprocess.SubprocessError as e:
        logging.error(f"Command failed: {e}")
        if check:
            logging.error(f"Error output: {getattr(e, 'stderr', 'No stderr available')}")
            sys.exit(1)
        return None
