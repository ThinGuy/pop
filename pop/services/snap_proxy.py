"""
Snap proxy configuration for Ubuntu Pro on Premises (PoP)
"""

import os
import logging
from typing import Dict, Optional

from pop.utils.system import run_command


def configure_snap_proxy(paths: Dict[str, str], token: str) -> bool:
    """
    Configure snap-proxy-server for offline use
    
    Args:
        paths: Dictionary of system paths
        token: Ubuntu Pro contract token
        
    Returns:
        True if successful, False otherwise
    """
    logging.info("Configuring snap-proxy-server for offline use")
    
    try:
        # Create snap-proxy directory
        os.makedirs(paths["pop_snap_proxy_dir"], exist_ok=True)
        
        # Initialize snap-proxy database
        run_command(["snap-proxy", "init"])
        
        # Configure snap-proxy with token
        run_command(["snap-proxy", "config", "account-token", token])
        
        # Create a systemd service file for snap-proxy
        service_path = "/etc/systemd/system/snap-proxy.service"
        service_content = f"""[Unit]
Description=Snap Proxy Server
After=network.target postgresql.service

[Service]
Type=simple
ExecStart=/snap/bin/snap-proxy-server
Restart=on-failure
WorkingDirectory={paths["pop_snap_proxy_dir"]}

[Install]
WantedBy=multi-user.target
"""
        with open(service_path, 'w') as service_file:
            service_file.write(service_content)
        
        # Enable and start the service
        run_command(["systemctl", "daemon-reload"])
        run_command(["systemctl", "enable", "snap-proxy"])
        run_command(["systemctl", "start", "snap-proxy"])
        
        logging.info("Snap proxy server configured successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to configure snap-proxy-server: {e}")
        return False


def check_snap_proxy_status() -> Dict[str, str]:
    """
    Check the status of snap proxy server
    
    Returns:
        Dictionary with status information
    """
    status_info = {
        "running": False,
        "enabled": False,
        "port": "8000",
        "version": "Unknown"
    }
    
    try:
        # Check if service is running
        status = run_command(
            ["systemctl", "is-active", "snap-proxy"],
            capture_output=True
        )
        
        if status.strip() == "active":
            status_info["running"] = True
        
        # Check if service is enabled
        enabled = run_command(
            ["systemctl", "is-enabled", "snap-proxy"],
            capture_output=True
        )
        
        if enabled.strip() == "enabled":
            status_info["enabled"] = True
        
        # Get snap proxy version
        version = run_command(
            ["snap", "info", "snap-proxy-server"],
            capture_output=True
        )
        
        for line in version.split("\n"):
            if line.strip().startswith("installed:"):
                status_info["version"] = line.split(":", 1)[1].strip()
                break
        
        return status_info
    except Exception as e:
        logging.error(f"Failed to check snap proxy status: {e}")
        return status_info


def configure_snap_client(mirror_host: str, port: int = 8000) -> bool:
    """
    Configure snap client to use proxy
    
    Args:
        mirror_host: Host name or IP for the mirror server
        port: Port for the snap proxy server
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Set snap proxy
        run_command([
            "snap", "set", "system", 
            f"proxy.http=http://{mirror_host}:{port}"
        ])
        
        run_command([
            "snap", "set", "system", 
            f"proxy.https=http://{mirror_host}:{port}"
        ])
        
        logging.info(f"Snap client configured to use proxy at {mirror_host}:{port}")
        return True
    except Exception as e:
        logging.error(f"Failed to configure snap client: {e}")
        return False


def unconfigure_snap_client() -> bool:
    """
    Remove snap proxy configuration
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Unset snap proxy
        run_command(["snap", "unset", "system", "proxy.http"])
        run_command(["snap", "unset", "system", "proxy.https"])
        
        logging.info("Snap client proxy configuration removed")
        return True
    except Exception as e:
        logging.error(f"Failed to remove snap client configuration: {e}")
        return False


def update_snap_proxy_token(token: str) -> bool:
    """
    Update the token for snap proxy
    
    Args:
        token: New Ubuntu Pro contract token
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Update token
        run_command(["snap-proxy", "config", "account-token", token])
        
        # Restart service
        run_command(["systemctl", "restart", "snap-proxy"])
        
        logging.info("Snap proxy token updated successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to update snap proxy token: {e}")
        return False
