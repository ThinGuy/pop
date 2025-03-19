"""
Cron job management for Ubuntu Pro on Premises (PoP)
"""

import os
import logging
import shutil
import datetime
from typing import Dict, Optional

from pop.utils.system import run_command


def setup_cron_for_mirror(paths: Dict[str, str], schedule: str = "0 */12 * * *") -> bool:
    """
    Configure cron job for regular mirror updates
    
    Args:
        paths: Dictionary of system paths
        schedule: Cron schedule expression (default: every 12 hours)
        
    Returns:
        True if successful, False otherwise
    """
    logging.info("Setting up cron job for mirror updates")
    
    try:
        # Create cron directory if needed
        cron_dir = os.path.dirname(paths["pop_cron_file"])
        os.makedirs(cron_dir, exist_ok=True)
        
        # Create cron job file
        cron_content = f"""# PoP mirror update cron job
# Created by PoP Configuration Script - {datetime.datetime.now().isoformat()}
{schedule} apt-mirror /usr/bin/apt-mirror > /var/spool/apt-mirror/var/cron.log
"""
        
        with open(paths["pop_cron_file"], 'w') as f:
            f.write(cron_content)
        
        # Set proper permissions
        os.chmod(paths["pop_cron_file"], 0o644)
        
        # Install cron job by copying to system cron.d directory
        system_cron_path = "/etc/cron.d/pop-mirror"
        shutil.copy2(paths["pop_cron_file"], system_cron_path)
        
        logging.info(f"Cron job set up with schedule: {schedule}")
        return True
    except Exception as e:
        logging.error(f"Failed to set up cron job: {e}")
        return False


def verify_cron_job(paths: Dict[str, str]) -> bool:
    """
    Verify that cron job is installed and active
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        True if job is active, False otherwise
    """
    # Check if our cron file exists
    system_cron_path = "/etc/cron.d/pop-mirror"
    if not os.path.exists(system_cron_path):
        logging.warning(f"Cron job not found: {system_cron_path}")
        return False
    
    # Check if cron service is running
    try:
        cron_status = run_command(
            ["systemctl", "is-active", "cron"],
            capture_output=True
        )
        
        if cron_status.strip() != "active":
            logging.warning("Cron service is not active")
            return False
            
        logging.info("Cron job is active")
        return True
    except Exception as e:
        logging.error(f"Failed to verify cron job: {e}")
        return False


def update_cron_schedule(paths: Dict[str, str], schedule: str) -> bool:
    """
    Update the schedule of the mirror update cron job
    
    Args:
        paths: Dictionary of system paths
        schedule: New cron schedule expression
        
    Returns:
        True if successful, False otherwise
    """
    # Simply use setup function to override existing job
    return setup_cron_for_mirror(paths, schedule)


def get_last_run_time() -> Optional[str]:
    """
    Get the time of the last cron job run
    
    Returns:
        Timestamp of last run, or None if unable to determine
    """
    cron_log = "/var/spool/apt-mirror/var/cron.log"
    
    if not os.path.exists(cron_log):
        return None
        
    try:
        # Get last modification time of log file
        last_mod = os.path.getmtime(cron_log)
        last_time = datetime.datetime.fromtimestamp(last_mod).isoformat()
        return last_time
    except Exception as e:
        logging.error(f"Failed to get last run time: {e}")
        return None
