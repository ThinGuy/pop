"""
VM build template management for Ubuntu Pro on Premises (PoP)
"""

import os
import logging
import shutil
import datetime
from typing import Dict, List, Any

def create_vm_template(builds_dir: str, paths: Dict[str, str], 
                     release: str, architectures: List[str]) -> Dict[str, Any]:
    """
    Create virtual machine build templates
    
    Args:
        builds_dir: Directory to store build files
        paths: Dictionary of system paths
        release: Ubuntu release codename (e.g., 'jammy')
        architectures: List of architectures to support
        
    Returns:
        Dictionary with build information
    """
    logging.info("Creating VM build templates")
    
    vm_dir = os.path.join(builds_dir, "vm")
    os.makedirs(vm_dir, exist_ok=True)
    
    # Files to copy from the repository
    files = [
        {"src": paths["pop_apt_mirror_list"], "dst": "etc/apt/sources.list.d/pop.list"},
        {"src": paths["pop_apt_auth_file"], "dst": "etc/apt/auth.conf.d/91ubuntu-pro"},
        {"src": paths["pop_gpg_dir"], "dst": "etc/apt/trusted.gpg.d/"},
    ]
    
    # Create subdirectories for file structure
    for file_info in files:
        dst_path = os.path.join(vm_dir, file_info["dst"])
        dst_dir = os.path.dirname(dst_path)
        os.makedirs(dst_dir, exist_ok=True)
    
    # Copy files
    for file_info in files:
        src_path = file_info["src"]
        dst_path = os.path.join(vm_dir, file_info["dst"])
        
        if os.path.isdir(src_path):
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)
            
        logging.debug(f"Copied {src_path} to {dst_path}")
    
    # Create cloud-init.yaml template
    cloud_init_path = os.path.join(vm_dir, "cloud-init.yaml")
    with open(cloud_init_path, 'w') as f:
        f.write(f"""# Cloud-init configuration for PoP VM
# Generated: {datetime.datetime.now().isoformat()}
# For Ubuntu {release.capitalize()}

apt:
  sources_list: |
    # Managed by PoP
    deb http://archive.ubuntu.com/ubuntu/ {release} main restricted universe multiverse
    deb http://archive.ubuntu.com/ubuntu/ {release}-updates main restricted universe multiverse
    deb http://archive.ubuntu.com/ubuntu/ {release}-security main restricted universe multiverse

packages:
  - ubuntu-pro-client

runcmd:
  - [pro, attach, --no-auto-enable, "$POP_TOKEN"]
""")
    
    # Create grub.cfg for FIPS
    grub_path = os.path.join(vm_dir, "grub.cfg")
    with open(grub_path, 'w') as f:
        f.write(f"""# GRUB configuration for PoP VM with FIPS enabled
# Generated: {datetime.datetime.now().isoformat()}
# For Ubuntu {release.capitalize()}

GRUB_CMDLINE_LINUX="$GRUB_CMDLINE_LINUX fips=1"
GRUB_TERMINAL="console"
GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR="Ubuntu Pro"
GRUB_DEFAULT=0
""")
    
    # Create README.md with instructions
    readme_path = os.path.join(vm_dir, "README.md")
    with open(readme_path, 'w') as f:
        f.write(f"""# PoP VM Build Files

This directory contains files needed to build a virtual machine with Ubuntu Pro on Premises (PoP) integration.

## Contents

- Configuration files for apt repositories
- Authentication files for Ubuntu Pro repositories
- GPG keys for repository validation
- Template for VM build (cloud-init.yaml)
- GRUB configuration with FIPS mode enabled

## FIPS Mode

This VM template includes FIPS mode enabled by default via the kernel parameter `fips=1`. This ensures that the system will use only FIPS-validated cryptographic modules when FIPS packages are installed.

## Usage

1. Copy these files to your VM build environment
2. Include the grub.cfg settings in your VM's GRUB configuration
3. Use the cloud-init.yaml as a starting point for your cloud-init configuration
4. Build your VM with PoP integration

## Notes

- These files were generated for Ubuntu {release.capitalize()}
- Configured for architectures: {', '.join(architectures)}
- Generated on {datetime.datetime.now().strftime('%Y-%m-%d')}

For more information, see the PoP documentation.
""")
    
    return {
        "dir": vm_dir,
        "files": [
            cloud_init_path,
            grub_path,
            readme_path
        ],
        "status": "success"
    }


def create_fips_startup_script(vm_dir: str, release: str) -> str:
    """
    Create FIPS startup script for VM
    
    Args:
        vm_dir: Directory to store build files
        release: Ubuntu release codename (e.g., 'jammy')
        
    Returns:
        Path to created script
    """
    script_path = os.path.join(vm_dir, "enable-fips.sh")
    
    with open(script_path, 'w') as f:
        f.write(f"""#!/bin/bash
# FIPS enablement script for Ubuntu {release.capitalize()}
# Generated: {datetime.datetime.now().isoformat()}

set -e

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root" >&2
    exit 1
fi

# Attach to Ubuntu Pro if not already attached
if ! pro status | grep -q "This machine is attached"; then
    echo "Attaching to Ubuntu Pro..."
    pro attach --no-auto-enable $POP_TOKEN
fi

# Enable FIPS
echo "Enabling FIPS..."
pro enable fips

# Update GRUB configuration
echo "Updating GRUB configuration..."
cat > /etc/default/grub.d/99-fips.cfg << EOF
GRUB_CMDLINE_LINUX="$GRUB_CMDLINE_LINUX fips=1"
EOF

# Update GRUB
update-grub

echo "FIPS configuration complete. Please reboot your system."
""")
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    return script_path


def validate_vm_template(vm_dir: str) -> bool:
    """
    Validate VM template files
    
    Args:
        vm_dir: VM template directory
        
    Returns:
        True if valid, False otherwise
    """
    # Required files
    required_files = [
        "cloud-init.yaml",
        "grub.cfg",
        "README.md",
        "etc/apt/sources.list.d/pop.list",
        "etc/apt/auth.conf.d/91ubuntu-pro"
    ]
    
    # Check if all required files exist
    for file_path in required_files:
        full_path = os.path.join(vm_dir, file_path)
        if not os.path.exists(full_path):
            logging.warning(f"Missing required file: {file_path}")
            return False
    
    # Check if GPG keys directory is not empty
    gpg_dir = os.path.join(vm_dir, "etc/apt/trusted.gpg.d")
    if not os.path.exists(gpg_dir) or not os.listdir(gpg_dir):
        logging.warning("GPG keys directory is empty or missing")
        return False
    
    return True
