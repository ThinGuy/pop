"""
GPG key management for Ubuntu Pro on Premises (PoP)
"""

import os
import logging
import subprocess
from typing import Dict, Any

from pop.utils.system import run_command


def download_gpg_keys(paths: Dict[str, str], contract_data: Dict[str, Any]) -> None:
    """
    Download GPG keys for repositories
    
    Args:
        paths: Dictionary of system paths
        contract_data: Contract data from contracts.py
        
    Returns:
        None
        
    Raises:
        Exception: If key download fails
    """
    logging.info("Downloading GPG keys for repositories")
    
    try:
        # Create GPG directory if it doesn't exist
        os.makedirs(paths["pop_gpg_dir"], exist_ok=True)
        
        # Extract GPG keys
        gpg_keys = {}
        for token, info in contract_data.items():
            for entitlement in info.get("contractInfo", {}).get("resourceEntitlements", []):
                ent_type = entitlement.get("type")
                apt_key = entitlement.get("directives", {}).get("aptKey")
                
                if ent_type and apt_key:
                    gpg_keys[ent_type] = apt_key
        
        # Download keys
        for ent_type, key_id in gpg_keys.items():
            key_name = f"ubuntu-{ent_type}.gpg"
            key_path = os.path.join(paths["pop_gpg_dir"], key_name)
            key_url = f"https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x{key_id}"
            
            # Download and convert key
            logging.info(f"Downloading GPG key for {ent_type}")
            run_command(
                ["sh", "-c", f"wget -qO- '{key_url}' | gpg --dearmor > '{key_path}'"],
                shell=True
            )
            
            # Set appropriate permissions
            os.chmod(key_path, 0o644)
            
            logging.info(f"Downloaded GPG key for {ent_type} to {key_path}")
        
        logging.info(f"Downloaded {len(gpg_keys)} GPG keys")
    except Exception as e:
        logging.error(f"Failed to download GPG keys: {e}")
        raise


def verify_gpg_keys(paths: Dict[str, str], entitlements: list) -> bool:
    """
    Verify that GPG keys exist for specified entitlements
    
    Args:
        paths: Dictionary of system paths
        entitlements: List of entitlement types
        
    Returns:
        True if all keys exist, False otherwise
    """
    missing = []
    
    for entitlement in entitlements:
        key_name = f"ubuntu-{entitlement}.gpg"
        key_path = os.path.join(paths["pop_gpg_dir"], key_name)
        
        if not os.path.exists(key_path):
            missing.append(entitlement)
    
    if missing:
        logging.warning(f"Missing GPG keys for entitlements: {', '.join(missing)}")
        return False
    
    return True


def add_keyring_to_apt(key_path: str) -> bool:
    """
    Add a keyring to apt's trusted keyrings
    
    Args:
        key_path: Path to keyring file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        apt_trusted_dir = "/etc/apt/trusted.gpg.d/"
        target_path = os.path.join(apt_trusted_dir, os.path.basename(key_path))
        
        # Copy key to apt trusted directory
        if os.path.exists(key_path):
            if not os.path.exists(apt_trusted_dir):
                os.makedirs(apt_trusted_dir, exist_ok=True)
                
            run_command(["cp", "-f", key_path, target_path])
            os.chmod(target_path, 0o644)
            
            logging.info(f"Added keyring to apt: {target_path}")
            return True
        else:
            logging.warning(f"Keyring file does not exist: {key_path}")
            return False
    except Exception as e:
        logging.error(f"Failed to add keyring to apt: {e}")
        return False
