"""
Contract data management for Ubuntu Pro on Premises (PoP)
"""

import json
import logging
import tempfile
import subprocess
from typing import Dict, Any

from pop.utils.system import run_command


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
            command = f"cat {token_file.name} | /usr/bin/pro-airgapped | yq -o=json"
            result = run_command(["sh", "-c", command], capture_output=True, shell=True)
            
            # Save the contract data
            with open(paths["pop_json"], 'w') as json_file:
                json_file.write(result)
            
            logging.info(f"Contract data saved to {paths['pop_json']}")
            return json.loads(result)
    except Exception as e:
        logging.error(f"Failed to pull contract data: {e}")
        raise


def extract_account_info(contract_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract account information from contract data
    
    Args:
        contract_data: Contract data as returned by pull_contract_data
        
    Returns:
        Dictionary containing account information
    """
    for token, info in contract_data.items():
        contract_info = info.get("contractInfo", {})
        return {
            "name": contract_info.get("name", "Unknown"),
            "id": contract_info.get("id", "Unknown"),
            "created_at": contract_info.get("createdAt", "Unknown"),
            "effective_from": contract_info.get("effectiveFrom", "Unknown"),
            "effective_to": contract_info.get("effectiveTo", "Unknown"),
        }
    return {
        "name": "Unknown",
        "id": "Unknown",
        "created_at": "Unknown",
        "effective_from": "Unknown",
        "effective_to": "Unknown",
    }


def extract_entitlements(contract_data: Dict[str, Any]) -> list:
    """
    Extract entitlements from contract data
    
    Args:
        contract_data: Contract data as returned by pull_contract_data
        
    Returns:
        List of dictionaries containing entitlement information
    """
    entitlements = []
    for token, info in contract_data.items():
        contract_info = info.get("contractInfo", {})
        for entitlement in contract_info.get("resourceEntitlements", []):
            entitlements.append({
                "type": entitlement.get("type", "Unknown"),
                "entitled": entitlement.get("entitled", False),
                "suites": entitlement.get("directives", {}).get("suites", []),
            })
    return entitlements


def map_entitlement_to_repo_path(entitlement_name: str) -> str:
    """
    Map API entitlement names to actual repository paths
    
    Handles the discrepancy between get-resource-token's
    "esm-infra" naming and actual repository paths like "infra"
    
    Args:
        entitlement_name: Entitlement name from API
        
    Returns:
        Repository path
    """
    # Strip "esm-" prefix if present
    if entitlement_name.startswith("esm-"):
        return entitlement_name[4:]
    return entitlement_name
