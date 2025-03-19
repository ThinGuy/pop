"""
Authentication file management for Ubuntu Pro on Premises (PoP)
"""

import os
import logging
from typing import Dict

from pop.core.contracts import map_entitlement_to_repo_path


def create_auth_file(paths: Dict[str, str], resources: Dict[str, str]) -> None:
    """
    Create authentication file for apt
    
    Args:
        paths: Dictionary of system paths
        resources: Dictionary mapping entitlement types to resource tokens
        
    Returns:
        None
        
    Raises:
        Exception: If auth file creation fails
    """
    logging.info("Creating apt authentication file")
    
    try:
        # Create auth file
        auth_file_path = paths["pop_apt_auth_file"]
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(auth_file_path), exist_ok=True)
        
        with open(auth_file_path, 'w') as auth_file:
            for resource, password in resources.items():
                # Map the resource name (handles esm-infra -> infra conversion)
                repo_path = map_entitlement_to_repo_path(resource)
                
                if repo_path == "anbox-cloud":
                    repo_url = f"archive.anbox-cloud.io/stable/"
                else:
                    repo_url = f"esm.ubuntu.com/{repo_path}/ubuntu/"
                
                auth_file.write(f"machine {repo_url} login bearer password {password}  # ubuntu-pro-client\n")
        
        # Set permissions
        os.chmod(auth_file_path, 0o600)
        logging.info(f"Auth file created at {auth_file_path}")
    except Exception as e:
        logging.error(f"Failed to create auth file: {e}")
        raise


def verify_auth_file(paths: Dict[str, str]) -> bool:
    """
    Verify that authentication file exists and has correct permissions
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        True if file exists and has correct permissions, False otherwise
    """
    auth_file_path = paths["pop_apt_auth_file"]
    
    if not os.path.exists(auth_file_path):
        logging.warning(f"Authentication file does not exist: {auth_file_path}")
        return False
    
    # Check permissions
    file_perms = os.stat(auth_file_path).st_mode & 0o777
    if file_perms != 0o600:
        logging.warning(f"Authentication file has incorrect permissions: {oct(file_perms)}")
        return False
    
    return True


def update_auth_file(paths: Dict[str, str], resources: Dict[str, str]) -> None:
    """
    Update authentication file with new resource tokens
    
    Args:
        paths: Dictionary of system paths
        resources: Dictionary mapping entitlement types to resource tokens
        
    Returns:
        None
    """
    # The simplest way to update is to recreate the file
    create_auth_file(paths, resources)
    logging.info("Authentication file updated")
