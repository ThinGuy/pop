"""
Mirror size estimation for Ubuntu Pro on Premises (PoP)
"""

import io
import gzip
import logging
import requests
from typing import Dict, List, Any

from pop.core.contracts import map_entitlement_to_repo_path


def estimate_mirror_size(paths: Dict[str, str], resources: Dict[str, str], 
                        release: str, architectures: List[str], 
                        entitlements_list: List[str]) -> Dict[str, Any]:
    """
    Estimate the size of the mirror based on package lists
    
    Args:
        paths: Dictionary of system paths
        resources: Dictionary mapping entitlement types to resource tokens
        release: Ubuntu release codename (e.g., 'jammy')
        architectures: List of architectures to support
        entitlements_list: List of entitlements to include
        
    Returns:
        Dictionary with size information
    """
    logging.info("Estimating mirror size. This may take a few minutes...")
    
    try:
        # Read contract data
        import json
        with open(paths["pop_json"], 'r') as file:
            contract_data = json.load(file)
        
        total_size = 0
        total_packages = 0
        
        # Track repos that will be included
        included_repos = []
        
        # Process entitlements
        for token, info in contract_data.items():
            for entitlement in info.get("contractInfo", {}).get("resourceEntitlements", []):
                ent_type = entitlement.get("type")
                apt_url = entitlement.get("directives", {}).get("aptURL")
                suites = entitlement.get("directives", {}).get("suites", [])
                entitled = entitlement.get("entitled", False)
                
                # Map the entitlement name (handles esm-infra -> infra conversion)
                repo_path = map_entitlement_to_repo_path(ent_type)
                
                # Skip if not entitled, missing URL, or not in our entitlements list
                if not entitled or not apt_url or repo_path not in entitlements_list:
                    continue
                
                # Get token for this entitlement
                resource_token = resources.get(ent_type)
                if not resource_token:
                    logging.warning(f"No token found for entitlement {ent_type}")
                    continue
                
                # Ensure URL format
                if repo_path == "anbox-cloud":
                    if not apt_url.endswith('/'):
                        apt_url += "/"
                else:
                    if not apt_url.endswith('/ubuntu/'):
                        if apt_url.endswith('/'):
                            apt_url += "ubuntu/"
                        else:
                            apt_url += "/ubuntu/"
                
                # Process each suite (release) that matches our target
                for suite in suites:
                    if release in suite:
                        # For each architecture
                        for arch in architectures:
                            if arch == "source":
                                # Source packages format
                                package_path = f"{apt_url}dists/{suite}/main/source/Sources.gz"
                                included_repos.append(f"deb-src {apt_url} {suite} main")
                            else:
                                # Binary packages format
                                package_path = f"{apt_url}dists/{suite}/main/binary-{arch}/Packages.gz"
                                included_repos.append(f"deb [arch={arch}] {apt_url} {suite} main")
                            
                            try:
                                # Set up authentication for requests
                                auth = requests.auth.HTTPBasicAuth('bearer', resource_token)
                                headers = {'User-Agent': 'PoP/1.0'}
                                
                                # Get the package list
                                response = requests.get(package_path, auth=auth, headers=headers, timeout=30)
                                
                                if response.status_code == 200:
                                    # Decompress gzip data
                                    with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                                        package_data = f.read().decode('utf-8')
                                    
                                    # Parse package data to get size information
                                    packages = []
                                    current_package = {}
                                    
                                    for line in package_data.splitlines():
                                        if not line.strip():
                                            if current_package:
                                                packages.append(current_package)
                                                current_package = {}
                                            continue
                                        
                                        if ':' in line:
                                            key, value = line.split(':', 1)
                                            current_package[key.strip()] = value.strip()
                                    
                                    # Add the last package if present
                                    if current_package:
                                        packages.append(current_package)
                                    
                                    # Sum up sizes
                                    repo_size = sum(int(pkg.get('Size', 0)) for pkg in packages)
                                    repo_packages = len(packages)
                                    
                                    total_size += repo_size
                                    total_packages += repo_packages
                                    
                                    logging.debug(f"Found {repo_packages} packages ({repo_size/1024/1024:.2f} MB) in {suite}/{arch}")
                                else:
                                    logging.debug(f"Could not access {package_path}: {response.status_code}")
                            except Exception as e:
                                logging.debug(f"Error estimating size for {package_path}: {e}")
        
        # Convert to human-readable size
        if total_size < 1024*1024:
            readable_size = f"{total_size/1024:.2f} KB"
        elif total_size < 1024*1024*1024:
            readable_size = f"{total_size/1024/1024:.2f} MB"
        else:
            readable_size = f"{total_size/1024/1024/1024:.2f} GB"
        
        return {
            "bytes": total_size,
            "readable": readable_size,
            "packages": total_packages,
            "included_repos": included_repos
        }
    except Exception as e:
        logging.error(f"Failed to estimate mirror size: {e}")
        return {
            "bytes": 0,
            "readable": "Unknown",
            "packages": 0,
            "included_repos": []
        }


def get_mirror_disk_usage(mirror_path: str = "/var/spool/apt-mirror/mirror") -> Dict[str, Any]:
    """
    Get disk usage statistics for the mirror
    
    Args:
        mirror_path: Path to mirror directory
        
    Returns:
        Dictionary with disk usage information
    """
    import os
    import subprocess
    
    stats = {
        "total_size_bytes": 0,
        "total_size_readable": "0 B",
        "total_files": 0,
        "total_dirs": 0
    }
    
    if not os.path.exists(mirror_path):
        return stats
        
    try:
        # Get total size
        du_result = subprocess.check_output(
            ["du", "-sb", mirror_path], 
            text=True
        ).strip().split()[0]
        
        stats["total_size_bytes"] = int(du_result)
        
        # Make human readable
        size_bytes = stats["total_size_bytes"]
        if size_bytes < 1024:
            stats["total_size_readable"] = f"{size_bytes} B"
        elif size_bytes < 1024*1024:
            stats["total_size_readable"] = f"{size_bytes/1024:.2f} KB"
        elif size_bytes < 1024*1024*1024:
            stats["total_size_readable"] = f"{size_bytes/1024/1024:.2f} MB"
        else:
            stats["total_size_readable"] = f"{size_bytes/1024/1024/1024:.2f} GB"
            
        # Count files and directories
        file_count = subprocess.check_output(
            ["find", mirror_path, "-type", "f", "|", "wc", "-l"],
            shell=True,
            text=True
        ).strip()
        stats["total_files"] = int(file_count)
        
        dir_count = subprocess.check_output(
            ["find", mirror_path, "-type", "d", "|", "wc", "-l"],
            shell=True,
            text=True
        ).strip()
        stats["total_dirs"] = int(dir_count)
        
        return stats
    except Exception as e:
        logging.error(f"Failed to get mirror disk usage: {e}")
        return stats
