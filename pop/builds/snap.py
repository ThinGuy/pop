"""
Snap build template management for Ubuntu Pro on Premises (PoP)
"""

import os
import logging
import shutil
import datetime
from typing import Dict, List, Any


def create_snap_template(builds_dir: str, paths: Dict[str, str], 
                       release: str, architectures: List[str]) -> Dict[str, Any]:
    """
    Create snap package build templates
    
    Args:
        builds_dir: Directory to store build files
        paths: Dictionary of system paths
        release: Ubuntu release codename (e.g., 'jammy')
        architectures: List of architectures to support
        
    Returns:
        Dictionary with build information
    """
    logging.info("Creating snap build templates")
    
    snap_dir = os.path.join(builds_dir, "snap")
    os.makedirs(snap_dir, exist_ok=True)
    
    # Files to copy from the repository
    files = [
        {"src": paths["pop_apt_mirror_list"], "dst": "etc/apt/sources.list.d/pop.list"},
        {"src": paths["pop_apt_auth_file"], "dst": "etc/apt/auth.conf.d/91ubuntu-pro"},
        {"src": paths["pop_gpg_dir"], "dst": "etc/apt/trusted.gpg.d/"},
    ]
    
    # Create subdirectories for file structure
    for file_info in files:
        dst_path = os.path.join(snap_dir, file_info["dst"])
        dst_dir = os.path.dirname(dst_path)
        os.makedirs(dst_dir, exist_ok=True)
    
    # Copy files
    for file_info in files:
        src_path = file_info["src"]
        dst_path = os.path.join(snap_dir, file_info["dst"])
        
        if os.path.isdir(src_path):
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)
            
        logging.debug(f"Copied {src_path} to {dst_path}")
    
    # Map Ubuntu release to core base
    core_mapping = {
        "focal": "core20",
        "jammy": "core22",
        "noble": "core24"
    }
    
    # Default to core22 if release not in mapping
    core_base = core_mapping.get(release, "core22")
    
    # Create snapcraft.yaml template
    snapcraft_path = os.path.join(snap_dir, "snap/snapcraft.yaml")
    os.makedirs(os.path.dirname(snapcraft_path), exist_ok=True)
    
    with open(snapcraft_path, 'w') as f:
        f.write(f"""name: my-pop-enabled-app  # Change this to your app name
version: '0.1'  # Your app version
summary: An application with PoP integration
description: |
  This is a snap application with Ubuntu Pro on Premises integration.
  
  This template provides a base configuration for building snaps with 
  Ubuntu Pro on Premises (PoP) integration, allowing secure access to 
  Ubuntu Pro services in air-gapped environments.

base: {core_base}
confinement: strict
grade: stable

parts:
  my-part:  # Change this to your app's part name
    plugin: nil
    stage-packages:
      - ubuntu-pro-client
    override-build: |
      snapcraftctl build
      # Copy PoP configuration files
      mkdir -p $SNAPCRAFT_PART_INSTALL/etc/apt/sources.list.d/
      mkdir -p $SNAPCRAFT_PART_INSTALL/etc/apt/auth.conf.d/
      mkdir -p $SNAPCRAFT_PART_INSTALL/etc/apt/trusted.gpg.d/
      cp -r etc/apt/sources.list.d/pop.list $SNAPCRAFT_PART_INSTALL/etc/apt/sources.list.d/
      cp -r etc/apt/auth.conf.d/91ubuntu-pro $SNAPCRAFT_PART_INSTALL/etc/apt/auth.conf.d/
      cp -r etc/apt/trusted.gpg.d/* $SNAPCRAFT_PART_INSTALL/etc/apt/trusted.gpg.d/

apps:
  my-app:  # Change this to your app name
    command: bin/my-command
    plugs:
      - network
      - network-bind
""")
    
    # Create build script
    build_script_path = os.path.join(snap_dir, "build.sh")
    with open(build_script_path, 'w') as f:
        f.write(f"""#!/bin/bash
# Build script for Ubuntu Pro snap
# Generated: {datetime.datetime.now().isoformat()}
# For Ubuntu {release.capitalize()} with {core_base}

set -e

# Build the snap package
snapcraft

echo "Snap package built successfully"
echo "To install: sudo snap install my-pop-enabled-app_0.1_*.snap --dangerous"
""")
    
    # Make the build script executable
    os.chmod(build_script_path, 0o755)
    
    # Create hooks directory and pre-refresh hook
    hooks_dir = os.path.join(snap_dir, "snap/hooks")
    os.makedirs(hooks_dir, exist_ok=True)
    
    pre_refresh_path = os.path.join(hooks_dir, "pre-refresh")
    with open(pre_refresh_path, 'w') as f:
        f.write("""#!/bin/sh
# Pre-refresh hook for Ubuntu Pro snap
# This hook runs before the snap is refreshed

# Ensure Pro configuration is preserved
if [ -f "$SNAP_DATA/etc/ubuntu-pro/ubuntu-pro.cfg" ]; then
    cp "$SNAP_DATA/etc/ubuntu-pro/ubuntu-pro.cfg" "$SNAP_COMMON/ubuntu-pro.cfg.backup"
fi

exit 0
""")
    
    # Make the hook executable
    os.chmod(pre_refresh_path, 0o755)
    
    # Create post-refresh hook
    post_refresh_path = os.path.join(hooks_dir, "post-refresh")
    with open(post_refresh_path, 'w') as f:
        f.write("""#!/bin/sh
# Post-refresh hook for Ubuntu Pro snap
# This hook runs after the snap is refreshed

# Restore Pro configuration if backup exists
if [ -f "$SNAP_COMMON/ubuntu-pro.cfg.backup" ]; then
    mkdir -p "$SNAP_DATA/etc/ubuntu-pro"
    cp "$SNAP_COMMON/ubuntu-pro.cfg.backup" "$SNAP_DATA/etc/ubuntu-pro/ubuntu-pro.cfg"
fi

exit 0
""")
    
    # Make the hook executable
    os.chmod(post_refresh_path, 0o755)
    
    # Create README.md with instructions
    readme_path = os.path.join(snap_dir, "README.md")
    with open(readme_path, 'w') as f:
        f.write(f"""# PoP Snap Build Files

This directory contains files needed to build a snap package with Ubuntu Pro on Premises (PoP) integration.

## Contents

- Configuration files for apt repositories
- Authentication files for Ubuntu Pro repositories
- GPG keys for repository validation
- snapcraft.yaml for snap packaging
- Build script
- Snap hooks for lifecycle management

## Usage

1. Copy these files to your snap build environment
2. Modify the snapcraft.yaml to include your application:
   - Change the name, version, and description
   - Add your application's build configuration
   - Update the apps section with your commands
3. Run the build script:
   ```bash
   ./build.sh
   ```
4. Or build manually with snapcraft:
   ```bash
   snapcraft
   ```

## Customization

Modify the snapcraft.yaml to include your application's parts and dependencies:

```yaml
parts:
  my-app:
    plugin: python  # Use appropriate plugin for your app
    source: .
    python-packages:
      - requests
      - pyyaml
    stage-packages:
      - ubuntu-pro-client
      - your-package1
      - your-package2
    override-build: |
      snapcraftctl build
      # Copy PoP configuration files
      mkdir -p $SNAPCRAFT_PART_INSTALL/etc/apt/sources.list.d/
      mkdir -p $SNAPCRAFT_PART_INSTALL/etc/apt/auth.conf.d/
      mkdir -p $SNAPCRAFT_PART_INSTALL/etc/apt/trusted.gpg.d/
      cp -r etc/apt/sources.list.d/pop.list $SNAPCRAFT_PART_INSTALL/etc/apt/sources.list.d/
      cp -r etc/apt/auth.conf.d/91ubuntu-pro $SNAPCRAFT_PART_INSTALL/etc/apt/auth.conf.d/
      cp -r etc/apt/trusted.gpg.d/* $SNAPCRAFT_PART_INSTALL/etc/apt/trusted.gpg.d/
```

## Hooks

The template includes lifecycle hooks:

- `pre-refresh`: Runs before the snap is refreshed/updated
- `post-refresh`: Runs after the snap is refreshed/updated

These hooks help preserve Ubuntu Pro configuration during updates.

## Notes

- These files were generated for Ubuntu {release.capitalize()} with {core_base}
- Configured for architectures: {', '.join(architectures)}
- Generated on {datetime.datetime.now().strftime('%Y-%m-%d')}

For more information, see the PoP documentation.
""")
    
    return {
        "dir": snap_dir,
        "files": [
            snapcraft_path,
            build_script_path,
            pre_refresh_path,
            post_refresh_path,
            readme_path
        ],
        "status": "success"
    }


def validate_snap_template(snap_dir: str) -> bool:
    """
    Validate snap template files
    
    Args:
        snap_dir: Snap template directory
        
    Returns:
        True if valid, False otherwise
    """
    # Required files
    required_files = [
        "snap/snapcraft.yaml",
        "build.sh",
        "README.md",
        "etc/apt/sources.list.d/pop.list",
        "etc/apt/auth.conf.d/91ubuntu-pro"
    ]
    
    # Check if all required files exist
    for file_path in required_files:
        full_path = os.path.join(snap_dir, file_path)
        if not os.path.exists(full_path):
            logging.warning(f"Missing required file: {file_path}")
            return False
    
    # Check if GPG keys directory is not empty
    gpg_dir = os.path.join(snap_dir, "etc/apt/trusted.gpg.d")
    if not os.path.exists(gpg_dir) or not os.listdir(gpg_dir):
        logging.warning("GPG keys directory is empty or missing")
        return False
    
    # Check if hook files exist
    hooks_dir = os.path.join(snap_dir, "snap/hooks")
    if not os.path.exists(os.path.join(hooks_dir, "pre-refresh")) or \
       not os.path.exists(os.path.join(hooks_dir, "post-refresh")):
        logging.warning("Missing hook files")
        return False
    
    return True


def create_multiarch_snap_config(snap_dir: str, architectures: List[str]) -> str:
    """
    Create multi-architecture snap configuration
    
    Args:
        snap_dir: Snap template directory
        architectures: List of architectures
        
    Returns:
        Path to created configuration
    """
    # Only include supported architectures for snaps
    supported_snap_archs = [arch for arch in architectures 
                          if arch in ["amd64", "arm64", "armhf", "i386", "ppc64el", "s390x"]]
    
    if not supported_snap_archs:
        # Default to amd64 if no supported architectures
        supported_snap_archs = ["amd64"]
    
    multiarch_path = os.path.join(snap_dir, "snap/snapcraft-multiarch.yaml")
    
    # Read existing snapcraft.yaml
    with open(os.path.join(snap_dir, "snap/snapcraft.yaml"), 'r') as f:
        content = f.read()
    
    # Add architectures field
    modified_content = content.replace(
        "grade: stable",
        f"grade: stable\narchitectures: [{', '.join(supported_snap_archs)}]"
    )
    
    # Write multiarch snapcraft.yaml
    with open(multiarch_path, 'w') as f:
        f.write(modified_content)
    
    # Create build script for multi-arch
    script_path = os.path.join(snap_dir, "build-multiarch.sh")
    with open(script_path, 'w') as f:
        f.write(f"""#!/bin/bash
# Multi-architecture build script for Ubuntu Pro snap
# Generated: {datetime.datetime.now().isoformat()}
# For architectures: {', '.join(supported_snap_archs)}

set -e

# Build with multiarch configuration
snapcraft --use-lxd --target-arch={supported_snap_archs[0]} --file snap/snapcraft-multiarch.yaml

# For additional architectures, use:
{' '.join([f'# snapcraft --use-lxd --target-arch={arch} --file snap/snapcraft-multiarch.yaml' for arch in supported_snap_archs[1:]])}

echo "Snap package built successfully for {supported_snap_archs[0]}"
echo "To build for other architectures, uncomment the additional commands"
""")
    
    # Make the build script executable
    os.chmod(script_path, 0o755)
    
    return multiarch_path
