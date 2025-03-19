"""
Repository configuration for Ubuntu Pro on Premises (PoP)
"""

import os
import logging
import datetime
from typing import Dict, List, Optional

from pop.core.contracts import map_entitlement_to_repo_path


def create_mirror_list(paths: Dict[str, str], resources: Dict[str, str], 
                      release: str, architectures: List[str], entitlements: List[str],
                      mirror_host: Optional[str] = None, mirror_port: Optional[int] = None,
                      mirror_standard_repos: bool = False, 
                      components: Optional[List[str]] = None,
                      pockets: Optional[List[str]] = None) -> None:
    """
    Create mirror list with embedded credentials
    
    Args:
        paths: Dictionary of system paths
        resources: Dictionary mapping entitlement types to resource tokens
        release: Ubuntu release codename (e.g., 'jammy')
        architectures: List of architectures to support
        entitlements: List of entitlements to mirror
        mirror_host: Host for the local mirror (optional)
        mirror_port: Port for the local mirror (optional)
        mirror_standard_repos: Whether to mirror standard Ubuntu repositories
        components: List of components to mirror for standard repositories
        pockets: List of pockets to mirror
        
    Returns:
        None
        
    Raises:
        Exception: If mirror list creation fails
    """
    logging.info(f"Creating mirror list for release {release} with architectures: {', '.join(architectures)}")
    
    try:
        # Create directory if needed
        mirror_list_dir = os.path.dirname(paths["pop_apt_mirror_list"])
        os.makedirs(mirror_list_dir, exist_ok=True)
        
        # Create mirror list
        mirror_list_path = paths["pop_apt_mirror_list"]
        
        with open(mirror_list_path, 'w') as mirror_file:
            # Write header
            header = f"""############# config ##################
#
# Created by PoP Configuration Script
# {datetime.datetime.now().isoformat()}
#
set base_path    /var/spool/apt-mirror
set mirror_path  $base_path/mirror
set skel_path    $base_path/skel
set var_path     $base_path/var
set defaultarch  {architectures[0] if architectures[0] != 'source' else 'amd64'}
set run_postmirror 0
set nthreads     20
set _tilde 0
set auth_no_challenge 1
#
############# end config ##############

"""
            mirror_file.write(header)
            
            # Track entitlements processed
            processed_entitlements = set()
            
            # Process Ubuntu Pro entitlements
            for resource_type, resource_token in resources.items():
                # Map the entitlement name (handles esm-infra -> infra conversion)
                repo_path = map_entitlement_to_repo_path(resource_type)
                
                # Skip if not in our entitlements list
                if repo_path not in entitlements:
                    continue
                
                # Determine repository URL
                if repo_path == "anbox-cloud":
                    apt_url = f"https://archive.anbox-cloud.io/stable/"
                else:
                    apt_url = f"https://esm.ubuntu.com/{repo_path}/ubuntu/"
                
                # Override URL with local mirror host if specified
                if mirror_host:
                    # Extract the path component from the URL
                    url_parts = apt_url.split('/')
                    # Rebuild URL with local mirror host
                    if mirror_port and mirror_port != 80:
                        apt_url = f"http://{mirror_host}:{mirror_port}/{'/'.join(url_parts[3:])}"
                    else:
                        apt_url = f"http://{mirror_host}/{'/'.join(url_parts[3:])}"
                    logging.info(f"Using local mirror URL: {apt_url}")
                
                # Add credentials to URL
                cred_url = apt_url.replace("https://", f"https://bearer:{resource_token}@")
                cred_url = cred_url.replace("http://", f"http://bearer:{resource_token}@")
                
                # Add entry for release
                repo_suite = f"{release}"
                
                # Handle source architecture differently
                if 'source' in architectures:
                    mirror_file.write(f"\ndeb-src {cred_url} {repo_suite} main\n")
                
                # Add binary architectures
                binary_archs = [a for a in architectures if a != 'source']
                if binary_archs:
                    mirror_file.write(f"\ndeb [arch={','.join(binary_archs)}] {cred_url} {repo_suite} main\n")
                
                processed_entitlements.add(repo_path)
                logging.info(f"Added repository for {repo_path} ({repo_suite})")
            
            # Add clean directives for Pro repositories
            for repo_path in processed_entitlements:
                if repo_path == "anbox-cloud":
                    mirror_file.write(f"\nclean https://archive.anbox-cloud.io/stable/\n")
                else:
                    mirror_file.write(f"\nclean https://esm.ubuntu.com/{repo_path}/ubuntu/\n")
            
            # If requested, add standard Ubuntu repositories
            if mirror_standard_repos and components and pockets:
                logging.info(f"Adding standard Ubuntu repositories for {release}")
                components_str = " ".join(components)
                
                # Determine if we need ports.ubuntu.com or archive.ubuntu.com
                use_ports = any(arch in ['arm64', 'armhf', 'ppc64el', 's390x'] for arch in architectures)
                repo_url = "http://ports.ubuntu.com/ubuntu-ports" if use_ports else "http://archive.ubuntu.com/ubuntu"
                
                # Map pocket names to Ubuntu repository names
                pocket_map = {
                    "release": release,
                    "updates": f"{release}-updates",
                    "backports": f"{release}-backports",
                    "security": f"{release}-security"
                }
                
                # Add entries for each pocket
                for pocket in pockets:
                    if pocket in pocket_map:
                        suite = pocket_map[pocket]
                        
                        # Add source if requested
                        if 'source' in architectures:
                            mirror_file.write(f"\ndeb-src {repo_url} {suite} {components_str}\n")
                        
                        # Add binary architectures
                        binary_archs = [a for a in architectures if a != 'source']
                        for arch in binary_archs:
                            mirror_file.write(f"\ndeb [arch={arch}] {repo_url} {suite} {components_str}\n")
                        
                        logging.info(f"Added standard repository: {suite} with components: {components_str}")
                
                # Add clean directive for standard repositories
                mirror_file.write(f"\nclean {repo_url}\n")
        
        # Set permissions
        os.chmod(mirror_list_path, 0o644)
        logging.info(f"Mirror list created at {mirror_list_path} with {len(processed_entitlements)} entitlements")
    except Exception as e:
        logging.error(f"Failed to create mirror list: {e}")
        raise


def verify_mirror_list(paths: Dict[str, str]) -> bool:
    """
    Verify that mirror list exists and is valid
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        True if valid, False otherwise
    """
    mirror_list_path = paths["pop_apt_mirror_list"]
    
    if not os.path.exists(mirror_list_path):
        logging.warning(f"Mirror list does not exist: {mirror_list_path}")
        return False
    
    try:
        with open(mirror_list_path, 'r') as f:
            content = f.read()
            
        # Check for required config settings
        required_configs = [
            "set base_path",
            "set mirror_path",
            "set defaultarch",
            "set auth_no_challenge"
        ]
        
        for config in required_configs:
            if config not in content:
                logging.warning(f"Mirror list missing required config: {config}")
                return False
        
        # Check for repository entries
        if "deb " not in content and "deb-src " not in content:
            logging.warning("Mirror list does not contain any repository entries")
            return False
            
        return True
    except Exception as e:
        logging.error(f"Failed to verify mirror list: {e}")
        return False
