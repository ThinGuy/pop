"""
Build template management for Ubuntu Pro on Premises (PoP)
"""

import os
import logging
import datetime
from typing import Dict, List, Any

from pop.builds.vm import create_vm_template, validate_vm_template
# Import additional build modules as they're implemented:
# from pop.builds.container import create_container_template, validate_container_template
# from pop.builds.snap import create_snap_template, validate_snap_template


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
            # Create container templates (when implemented)
            results["results"]["container"] = {
                "status": "not_implemented",
                "message": "Container templates not yet implemented"
            }
            logging.warning("Container build templates not yet implemented")
        elif build_type == "snap":
            # Create snap templates (when implemented)
            results["results"]["snap"] = {
                "status": "not_implemented",
                "message": "Snap templates not yet implemented"
            }
            logging.warning("Snap build templates not yet implemented")
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
            # Validate container templates (when implemented)
            results["container"] = False
        elif build_type == "snap":
            # Validate snap templates (when implemented)
            results["snap"] = False
        else:
            results[build_type] = False
    
    return results
