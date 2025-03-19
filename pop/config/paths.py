"""
Path management for Ubuntu Pro on Premises (PoP)
"""

import os
import datetime
import logging
from typing import Dict, Any


def setup_paths(args) -> Dict[str, str]:
    """
    Set up and return paths based on configuration
    
    Args:
        args: Command-line arguments
    
    Returns:
        Dictionary of system paths
    """
    pop_dir = args.pop_dir
    
    # Define all paths relative to the base directory
    paths = {
        "pop_dir": pop_dir,
        "pop_gpg_dir": f"{pop_dir}/etc/apt/trusted.gpg.d",
        "pop_json": f"{pop_dir}/pop.json",
        "pop_resources_json": f"{pop_dir}/pop_resources.json",  
        "pop_apt_mirror_list": f"{pop_dir}/etc/mirror.list",
        "pop_apt_auth_file": f"{pop_dir}/etc/apt/auth.conf.d/91ubuntu-pro",
        "pop_rc_file": f"{pop_dir}/pop.rc",
        "pop_log": f"{pop_dir}/pop.log",
        "pop_debs_dir": f"{pop_dir}/debs",
        "pop_builds_dir": f"{pop_dir}/builds",
        "pop_www_dir": f"{pop_dir}/www",
        "pop_nginx_conf": f"{pop_dir}/etc/nginx/sites-available/pop",
        "pop_apache_conf": f"{pop_dir}/etc/apache2/sites-available/pop.conf",
        "pop_snap_proxy_dir": f"{pop_dir}/snap-proxy",
        "pop_tls_dir": f"{pop_dir}/etc/ssl",
        "pop_cron_file": f"{pop_dir}/etc/cron.d/pop-mirror",
        "pop_mirror_dir": "/var/spool/apt-mirror",
    }
    
    # Create TLS directory if using custom certs
    if hasattr(args, 'tls_cert') and args.tls_cert or hasattr(args, 'tls_key') and args.tls_key:
        os.makedirs(f"{paths['pop_tls_dir']}", exist_ok=True)
    
    return paths


def save_configuration(args, paths) -> None:
    """
    Save configuration to RC file
    
    Args:
        args: Command-line arguments
        paths: Dictionary of system paths
    
    Returns:
        None
    """
    rc_file = paths["pop_rc_file"]
    
    try:
        with open(rc_file, 'w') as f:
            f.write(f"# PoP Configuration - Created {datetime.datetime.now().isoformat()}\n")
            f.write(f"POP_TOKEN={args.token}\n")
            f.write(f"POP_DIR={args.pop_dir}\n")
            f.write(f"POP_RELEASE={args.release}\n")
            f.write(f"POP_ARCHITECTURES={','.join(args.architectures)}\n")
            f.write(f"POP_ENTITLEMENTS={','.join(args.entitlements)}\n")
            f.write(f"POP_GPG_DIR={paths['pop_gpg_dir']}\n")
            f.write(f"POP_JSON={paths['pop_json']}\n")
            f.write(f"POP_RESOURCES_JSON={paths['pop_resources_json']}\n")
            f.write(f"POP_APT_MIRROR_LIST={paths['pop_apt_mirror_list']}\n")
            f.write(f"POP_APT_AUTH_FILE={paths['pop_apt_auth_file']}\n")
            f.write(f"POP_LOG={paths['pop_log']}\n")
            f.write(f"POP_OFFLINE_REPO={args.offline_repo}\n")
            f.write(f"POP_MIRROR_HOST={args.mirror_host}\n")
            f.write(f"POP_MIRROR_PORT={args.mirror_port}\n")
            
            # Add contract port if specified
            if hasattr(args, 'contract_port'):
                f.write(f"POP_CONTRACT_PORT={args.contract_port}\n")
                
            # Add mirroring options if specified
            if hasattr(args, 'mirror_standard_repos') and args.mirror_standard_repos:
                f.write(f"POP_MIRROR_STANDARD_REPOS=True\n")
                f.write(f"POP_MIRROR_COMPONENTS={','.join(args.mirror_components)}\n")
                f.write(f"POP_MIRROR_POCKETS={','.join(args.mirror_pockets)}\n")
                
            # Add reconfigured timestamp if this is a reconfiguration
            if getattr(args, 'reconfigure', False):
                f.write(f"POP_RECONFIGURED={datetime.datetime.now().isoformat()}\n")
        
        # Secure permissions for token storage
        os.chmod(rc_file, 0o600)
        logging.info(f"Configuration saved to {rc_file}")
    except Exception as e:
        logging.error(f"Failed to save configuration: {e}")


def load_configuration(rc_file: str) -> Dict[str, Any]:
    """
    Load configuration from RC file
    
    Args:
        rc_file: Path to RC file
    
    Returns:
        Dictionary of configuration values
    """
    config = {}
    
    try:
        if not os.path.exists(rc_file):
            logging.warning(f"Configuration file {rc_file} not found")
            return config
            
        with open(rc_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key] = value
                    
        logging.info(f"Configuration loaded from {rc_file}")
        return config
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        return {}
