"""
Package management utilities for Ubuntu Pro on Premises (PoP)
"""

import os
import logging
import subprocess
import shutil
from typing import Dict, List, Optional

from pop.utils.system import run_command


def install_prerequisites(offline_repo: str = "ppa:yellow/ua-airgapped") -> None:
    """
    Install required packages for PoP
    
    Args:
        offline_repo: PPA for air-gapped Pro packages
        
    Returns:
        None
        
    Raises:
        SystemExit: If installation fails
    """
    prereqs = "wget wget2 curl vim gawk apt-mirror apache2 nginx nginx-extras jq postgresql postgresql-contrib"
    
    logging.info(f"Installing prerequisites: {prereqs}")
    
    try:
        # Update package lists
        run_command(["apt-get", "update"])
        
        # Install prerequisites
        run_command(
            ["apt-get", "install", "-yqf", "--reinstall"] + prereqs.split()
        )
        
        # Install yq via snap
        run_command(["snap", "install", "yq", "--stable"])
        
        # Install snap-proxy-server
        run_command(["snap", "install", "snap-proxy-server"])
        
        # Add PPA for air-gapped packages
        run_command(
            ["add-apt-repository", "-y", "-u", offline_repo]
        )
        
        logging.info("Prerequisites installed successfully")
    except Exception as e:
        logging.error(f"Failed to install prerequisites: {e}")
        raise


def download_pro_packages(paths: Dict[str, str]) -> None:
    """
    Download packages for offline installation
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        None
        
    Raises:
        SystemExit: If download fails
    """
    packages = ["contracts-airgapped", "pro-airgapped", "get-resource-tokens"]
    
    logging.info(f"Downloading Ubuntu Pro packages: {', '.join(packages)}")
    
    try:
        # Download only
        run_command([
            "apt-get", "install", "--download-only", "--reinstall",
            "-o", f"Dir::Cache::archives={paths['pop_debs_dir']}",
            "-yqf"
        ] + packages)
        
        # Now install
        run_command([
            "apt-get", "install", "--reinstall", "--autoremove", "--purge",
            "-yqf"
        ] + packages)
        
        # Cleanup
        for item in ["lock", "partial"]:
            path = os.path.join(paths["pop_debs_dir"], item)
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
        
        logging.info("Pro packages downloaded and installed successfully")
    except Exception as e:
        logging.error(f"Failed to download Pro packages: {e}")
        raise


def get_package_version(package: str) -> Optional[str]:
    """
    Get installed version of a package
    
    Args:
        package: Package name
        
    Returns:
        Version string if package is installed, None otherwise
    """
    try:
        version = run_command(
            ["dpkg-query", "-W", "-f=${Version}", package],
            capture_output=True
        )
        return version
    except:
        return None


def verify_package_installation(packages: List[str]) -> bool:
    """
    Verify that packages are installed
    
    Args:
        packages: List of package names to verify
        
    Returns:
        True if all packages are installed, False otherwise
    """
    missing = []
    for package in packages:
        if not get_package_version(package):
            missing.append(package)
    
    if missing:
        logging.warning(f"Missing packages: {', '.join(missing)}")
        return False
    
    return True
