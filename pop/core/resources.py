"""
Resource token management for Ubuntu Pro on Premises (PoP)
"""

import json
import logging
import subprocess
from typing import Dict, Any

from pop.utils.system import run_command


def generate_resource_tokens(token: str, paths: Dict[str, str]) -> Dict[str, str]:
    """
    Generate resource tokens using get-resource-tokens
    
    Args:
        token: Ubuntu Pro contract token
        paths: Dictionary of system paths
        
    Returns:
        Dictionary mapping entitlement types to resource tokens
        
    Raises:
        SystemExit: If token generation fails
    """
    logging.info("Generating resource tokens with get-resource-tokens")
    
    try:
        # Run get-resource-tokens
        result = run_command(
            ["get-resource-tokens", token],
            capture_output=True
        )
        
        # Parse the output
        output_lines = result.strip().split('\n')
        
        resources = {}
        resource_section_started = False
        
        for line in output_lines:
            if "resources:" in line:
                resource_section_started = True
                continue
                
            if resource_section_started and ":" in line and not line.startswith(("server:", "account:")):
                parts = line.strip().split(':', 1)
                if len(parts) == 2 and "contracts.canonical.com" not in line:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    resources[key] = value
        
        # Save to JSON file
        with open(paths["pop_resources_json"], 'w') as json_file:
            json.dump(resources, json_file, indent=4)
            
        logging.info(f"Resource tokens saved to {paths['pop_resources_json']}")
        return resources
    except Exception as e:
        logging.error(f"Failed to generate resource tokens: {e}")
        raise


def load_resource_tokens(paths: Dict[str, str]) -> Dict[str, str]:
    """
    Load resource tokens from file
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        Dictionary mapping entitlement types to resource tokens
    """
    try:
        with open(paths["pop_resources_json"], 'r') as json_file:
            resources = json.load(json_file)
        
        logging.info(f"Resource tokens loaded from {paths['pop_resources_json']}")
        return resources
    except Exception as e:
        logging.warning(f"Failed to load resource tokens: {e}")
        return {}


def validate_entitlements(resources: Dict[str, str], requested_entitlements: list) -> bool:
    """
    Validate that requested entitlements are available
    
    Args:
        resources: Dictionary mapping entitlement types to resource tokens
        requested_entitlements: List of requested entitlement types
        
    Returns:
        True if all requested entitlements are available, False otherwise
    """
    missing = []
    
    for entitlement in requested_entitlements:
        # Handle esm-infra -> infra mapping
        entitlement_key = entitlement
        if not entitlement.startswith("esm-") and f"esm-{entitlement}" in resources:
            entitlement_key = f"esm-{entitlement}"
            
        if entitlement not in resources and entitlement_key not in resources:
            missing.append(entitlement)
    
    if missing:
        logging.warning(f"Missing entitlements: {', '.join(missing)}")
        return False
    
    return True
