"""
Systemd service management for Ubuntu Pro on Premises (PoP)
"""

import os
import logging
from typing import Dict, List, Optional

from pop.utils.system import run_command


def create_contract_service(paths: Dict[str, str], contract_port: int = 8484) -> bool:
    """
    Create and enable systemd service for contracts server
    
    Args:
        paths: Dictionary of system paths
        contract_port: Port for the contracts server
        
    Returns:
        True if successful, False otherwise
    """
    logging.info("Creating systemd service for contracts server")
    
    try:
        # Create service file
        service_path = "/etc/systemd/system/pop-contracts.service"
        service_content = f"""[Unit]
Description=Ubuntu Pro on Premises Contracts Server
After=network.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/contracts-airgapped --listen-port={contract_port}
WorkingDirectory={paths["pop_dir"]}
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
        
        with open(service_path, 'w') as f:
            f.write(service_content)
        
        # Reload systemd daemon
        run_command(["systemctl", "daemon-reload"])
        
        # Enable and start service
        run_command(["systemctl", "enable", "pop-contracts"])
        run_command(["systemctl", "start", "pop-contracts"])
        
        logging.info("Contracts server service created and started")
        return True
    except Exception as e:
        logging.error(f"Failed to create contracts server service: {e}")
        return False


def create_mirror_service(paths: Dict[str, str], server_type: str = "apache") -> bool:
    """
    Create and enable systemd service for mirror server
    
    Args:
        paths: Dictionary of system paths
        server_type: Type of server (apache or nginx)
        
    Returns:
        True if successful, False otherwise
    """
    logging.info(f"Configuring {server_type} to start at boot")
    
    try:
        if server_type.lower() == "apache":
            # Enable and start Apache
            run_command(["systemctl", "enable", "apache2"])
            run_command(["systemctl", "start", "apache2"])
        elif server_type.lower() == "nginx":
            # Enable and start Nginx
            run_command(["systemctl", "enable", "nginx"])
            run_command(["systemctl", "start", "nginx"])
        else:
            logging.error(f"Unknown server type: {server_type}")
            return False
        
        logging.info(f"{server_type.capitalize()} server enabled and started")
        return True
    except Exception as e:
        logging.error(f"Failed to configure {server_type} service: {e}")
        return False


def create_apt_mirror_timer(paths: Dict[str, str], schedule: str = "*-*-* 0,12:00:00") -> bool:
    """
    Create and enable systemd timer for apt-mirror updates
    
    Args:
        paths: Dictionary of system paths
        schedule: Schedule in systemd time format (default: twice daily at 00:00 and 12:00)
        
    Returns:
        True if successful, False otherwise
    """
    logging.info("Creating systemd timer for apt-mirror updates")
    
    try:
        # Create service file
        service_path = "/etc/systemd/system/pop-mirror.service"
        service_content = f"""[Unit]
Description=Ubuntu Pro on Premises Mirror Update
After=network.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/bin/apt-mirror {paths["pop_apt_mirror_list"]}
WorkingDirectory={paths["pop_dir"]}
StandardOutput=journal
StandardError=journal
"""
        
        with open(service_path, 'w') as f:
            f.write(service_content)
        
        # Create timer file
        timer_path = "/etc/systemd/system/pop-mirror.timer"
        timer_content = f"""[Unit]
Description=Ubuntu Pro on Premises Mirror Update Timer

[Timer]
OnCalendar={schedule}
Persistent=true

[Install]
WantedBy=timers.target
"""
        
        with open(timer_path, 'w') as f:
            f.write(timer_content)
        
        # Reload systemd daemon
        run_command(["systemctl", "daemon-reload"])
        
        # Enable and start timer
        run_command(["systemctl", "enable", "pop-mirror.timer"])
        run_command(["systemctl", "start", "pop-mirror.timer"])
        
        logging.info("apt-mirror timer created and started")
        return True
    except Exception as e:
        logging.error(f"Failed to create apt-mirror timer: {e}")
        return False


def configure_production_services(paths: Dict[str, str], 
                                contract_port: int = 8484,
                                server_types: List[str] = ["apache", "nginx"]) -> Dict[str, bool]:
    """
    Configure all services for production use
    
    Args:
        paths: Dictionary of system paths
        contract_port: Port for the contracts server
        server_types: List of server types to enable
        
    Returns:
        Dictionary with service status
    """
    logging.info("Configuring services for production use")
    
    results = {
        "contracts": False,
        "mirror_timer": False,
        "servers": {}
    }
    
    # Create contract server service
    results["contracts"] = create_contract_service(paths, contract_port)
    
    # Create apt-mirror timer
    results["mirror_timer"] = create_apt_mirror_timer(paths)
    
    # Configure web servers
    for server_type in server_types:
        results["servers"][server_type] = create_mirror_service(paths, server_type)
    
    # Check if all services were configured successfully
    all_success = results["contracts"] and results["mirror_timer"]
    for server, status in results["servers"].items():
        all_success = all_success and status
    
    if all_success:
        logging.info("All services configured successfully for production use")
    else:
        logging.warning("Some services failed to configure")
        
    return results


def check_service_status(service_name: str) -> Dict[str, Any]:
    """
    Check status of a systemd service
    
    Args:
        service_name: Name of the service
        
    Returns:
        Dictionary with service status information
    """
    status = {
        "exists": False,
        "enabled": False,
        "active": False,
        "status": "unknown",
        "error": None
    }
    
    try:
        # Check if service exists
        result = run_command(
            ["systemctl", "list-unit-files", f"{service_name}.service"],
            capture_output=True
        )
        
        if f"{service_name}.service" in result:
            status["exists"] = True
        else:
            return status
        
        # Check if service is enabled
        result = run_command(
            ["systemctl", "is-enabled", service_name],
            capture_output=True
        )
        
        if "enabled" in result:
            status["enabled"] = True
        
        # Check if service is active
        result = run_command(
            ["systemctl", "is-active", service_name],
            capture_output=True
        )
        
        if "active" in result:
            status["active"] = True
            status["status"] = "running"
        else:
            status["status"] = result.strip()
        
        return status
    except Exception as e:
        status["error"] = str(e)
        return status
