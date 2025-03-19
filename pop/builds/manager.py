"""
Build template management for Ubuntu Pro on Premises (PoP)
"""

import os
import logging
import datetime
from typing import Dict, List, Any

from pop.builds.vm import create_vm_template, validate_vm_template
from pop.builds.container import create_container_template, validate_container_template
from pop.builds.snap import create_snap_template, validate_snap_template


def create_build_templates(paths: Dict[str, str], resources: Dict[str, str],
                          release: str, architectures: List[str], 
                          build_types: List[str]) -> Dict[str, Any]:
    """
    Create build templates for specified build types
    
    Args:
        paths: Dictionary of system paths
        resources: Dictionary mapping entitlement types to resource tokens
        release: Ubuntu release codename (e.g., 'jammy')
        architectures: List of architectures to support
        build_types: List of build types to create
        
    Returns:
        Dictionary with build results
    """
    logging.info(f"Creating build templates for: {', '.join(build_types)}")
    
    # Create builds directory
    builds_dir = paths["pop_builds_dir"]
    os.makedirs(builds_dir, exist_ok=True)
    
    results = {
        "builds_dir": builds_dir,
        "build_types": build_types,
        "results": {}
    }
    
    # Process each requested build type
    for build_type in build_types:
        if build_type == "vm":
            # Create VM templates
            vm_result = create_vm_template(builds_dir, paths, release, architectures)
            results["results"]["vm"] = vm_result
        elif build_type == "container":
            # Create container templates
            container_result = create_container_template(builds_dir, paths, release, architectures)
            results["results"]["container"] = container_result
        elif build_type == "snap":
            # Create snap templates
            snap_result = create_snap_template(builds_dir, paths, release, architectures)
            results["results"]["snap"] = snap_result
        else:
            logging.warning(f"Unknown build type: {build_type}")
            results["results"][build_type] = {
                "status": "error",
                "message": f"Unknown build type: {build_type}"
            }
    
    # Create top-level README
    create_builds_readme(builds_dir, build_types, release, architectures)
    
    logging.info(f"Build template creation completed in {builds_dir}")
    return results


def create_builds_readme(builds_dir: str, build_types: List[str], 
                        release: str, architectures: List[str]) -> str:
    """
    Create top-level README for builds directory
    
    Args:
        builds_dir: Directory to store build files
        build_types: List of build types included
        release: Ubuntu release codename
        architectures: List of architectures supported
        
    Returns:
        Path to created README
    """
    readme_path = os.path.join(builds_dir, "README.md")
    
    with open(readme_path, 'w') as f:
        f.write(f"""# PoP Build Files

This directory contains files for building different types of systems with 
Ubuntu Pro on Premises (PoP) integration.

## Available Build Types

{', '.join(build_types)}

## Common Files

Each build directory contains:

- APT repository configuration
- Authentication files
- GPG keys
- Build templates specific to the build type
- README with usage instructions

## Configuration

- Ubuntu Release: {release}
- Architectures: {', '.join(architectures)}
- Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

For assistance, contact your Canonical representative.
""")
    
    return readme_path


def validate_build_templates(paths: Dict[str, str], build_types: List[str]) -> Dict[str, bool]:
    """
    Validate build templates
    
    Args:
        paths: Dictionary of system paths
        build_types: List of build types to validate
        
    Returns:
        Dictionary mapping build types to validation results
    """
    builds_dir = paths["pop_builds_dir"]
    results = {}
    
    for build_type in build_types:
        if build_type == "vm":
            vm_dir = os.path.join(builds_dir, "vm")
            results["vm"] = validate_vm_template(vm_dir)
        elif build_type == "container":
            container_dir = os.path.join(builds_dir, "container")
            results["container"] = validate_container_template(container_dir)
        elif build_type == "snap":
            snap_dir = os.path.join(builds_dir, "snap")
            results["snap"] = validate_snap_template(snap_dir)
        else:
            results[build_type] = False
    
    return results


def list_available_templates(paths: Dict[str, str]) -> Dict[str, List[str]]:
    """
    List available build templates
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        Dictionary mapping build types to available templates
    """
    builds_dir = paths["pop_builds_dir"]
    results = {
        "vm": [],
        "container": [],
        "snap": []
    }
    
    if not os.path.exists(builds_dir):
        return results
    
    # Check for VM templates
    vm_dir = os.path.join(builds_dir, "vm")
    if os.path.exists(vm_dir):
        # Look for README.md, cloud-init.yaml, etc.
        vm_files = os.listdir(vm_dir)
        results["vm"] = [f for f in vm_files if os.path.isfile(os.path.join(vm_dir, f))]
    
    # Check for container templates
    container_dir = os.path.join(builds_dir, "container")
    if os.path.exists(container_dir):
        # Look for Dockerfile, docker-compose.yml, etc.
        container_files = os.listdir(container_dir)
        results["container"] = [f for f in container_files if os.path.isfile(os.path.join(container_dir, f))]
    
    # Check for snap templates
    snap_dir = os.path.join(builds_dir, "snap")
    if os.path.exists(snap_dir):
        # Look for snap directory with snapcraft.yaml
        if os.path.exists(os.path.join(snap_dir, "snap")):
            snap_files = os.listdir(os.path.join(snap_dir, "snap"))
            if "snapcraft.yaml" in snap_files:
                results["snap"].append("snapcraft.yaml")
        
        # Look for other files
        snap_files = os.listdir(snap_dir)
        root_files = [f for f in snap_files if os.path.isfile(os.path.join(snap_dir, f))]
        results["snap"].extend(root_files)
    
    return results
