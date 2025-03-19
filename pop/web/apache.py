"""
Apache configuration for Ubuntu Pro on Premises (PoP)
"""

import os
import logging
import shutil
from typing import Dict, Optional

from pop.utils.system import run_command


def setup_apache_for_mirror(paths: Dict[str, str], mirror_host: str) -> bool:
    """
    Configure Apache to serve the mirrored repositories
    
    Args:
        paths: Dictionary of system paths
        mirror_host: Host name for mirror server
        
    Returns:
        True if successful, False otherwise
    """
    logging.info("Setting up Apache for serving mirrored repositories")
    
    try:
        # Create Apache configuration directory if needed
        apache_conf_dir = os.path.dirname(paths["pop_apache_conf"])
        os.makedirs(apache_conf_dir, exist_ok=True)
        
        # Create links to mirror directories
        mirror_path = "/var/spool/apt-mirror/mirror"
        apache_links = {
            # Pro repositories
            "esm-infra": "esm.ubuntu.com/infra/ubuntu",
            "esm-apps": "esm.ubuntu.com/apps/ubuntu",
            "fips": "esm.ubuntu.com/fips/ubuntu",
            "fips-updates": "esm.ubuntu.com/fips-updates/ubuntu",
            "cis": "esm.ubuntu.com/cis/ubuntu",
            "usg": "esm.ubuntu.com/usg/ubuntu",
            # Standard repositories
            "ubuntu": "archive.ubuntu.com/ubuntu",
            "ubuntu-ports": "ports.ubuntu.com/ubuntu-ports"
        }
        
        # Create symlinks in /var/www/html for each repository
        for link_name, repo_path in apache_links.items():
            full_mirror_path = os.path.join(mirror_path, repo_path)
            www_link_path = f"/var/www/html/{link_name}"
            
            # Check if the source directory exists before creating the symlink
            if os.path.exists(full_mirror_path):
                # Remove existing link if it exists
                if os.path.exists(www_link_path):
                    if os.path.islink(www_link_path):
                        os.unlink(www_link_path)
                    else:
                        # It's a directory, remove it
                        shutil.rmtree(www_link_path)
                
                # Create the symlink
                os.symlink(full_mirror_path, www_link_path)
                logging.info(f"Created symlink: {www_link_path} -> {full_mirror_path}")
        
        # Create Apache configuration
        apache_conf = f"""<VirtualHost *:80>
    ServerName {mirror_host}
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/html

    ErrorLog ${{APACHE_LOG_DIR}}/error.log
    CustomLog ${{APACHE_LOG_DIR}}/access.log combined

    <Directory /var/www/html>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>
</VirtualHost>
"""
        
        # Write Apache configuration
        with open(paths["pop_apache_conf"], 'w') as f:
            f.write(apache_conf)
        
        # Create symlink to enable the site
        enabled_link = paths["pop_apache_conf"].replace('sites-available', 'sites-enabled')
        enabled_link = enabled_link.replace('.conf', '')
        
        if os.path.exists(enabled_link):
            os.unlink(enabled_link)
        
        os.symlink(paths["pop_apache_conf"], enabled_link)
        
        # Enable required Apache modules
        run_command(["a2enmod", "autoindex"])
        
        # Restart Apache
        run_command(["systemctl", "restart", "apache2"])
        
        logging.info("Apache configured successfully to serve mirrored repositories")
        return True
    except Exception as e:
        logging.error(f"Failed to set up Apache for mirror: {e}")
        return False


def check_apache_status() -> bool:
    """
    Check if Apache is running
    
    Returns:
        True if running, False otherwise
    """
    try:
        status = run_command(
            ["systemctl", "is-active", "apache2"],
            capture_output=True
        )
        return status.strip() == "active"
    except Exception:
        return False


def configure_apache_ssl(paths: Dict[str, str], cert_path: str, key_path: str) -> bool:
    """
    Configure SSL for Apache
    
    Args:
        paths: Dictionary of system paths
        cert_path: Path to SSL certificate
        key_path: Path to SSL private key
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure SSL module is enabled
        run_command(["a2enmod", "ssl"])
        
        # Read existing config
        with open(paths["pop_apache_conf"], 'r') as f:
            config = f.read()
        
        # Check if SSL is already configured
        if "<VirtualHost *:443>" in config:
            logging.info("Apache SSL already configured")
            return True
        
        # Create new config with SSL
        ssl_config = f"""<VirtualHost *:80>
    ServerName {{{mirror_host}}}
    Redirect permanent / https://{{{mirror_host}}}/
</VirtualHost>

<VirtualHost *:443>
    ServerName {{{mirror_host}}}
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/html

    ErrorLog ${{APACHE_LOG_DIR}}/error.log
    CustomLog ${{APACHE_LOG_DIR}}/access.log combined

    SSLEngine on
    SSLCertificateFile {cert_path}
    SSLCertificateKeyFile {key_path}
    SSLProtocol all -SSLv2 -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite HIGH:!aNULL:!MD5:!RC4

    <Directory /var/www/html>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>
</VirtualHost>
"""
        
        # Write new config
        with open(paths["pop_apache_conf"], 'w') as f:
            f.write(ssl_config)
        
        # Restart Apache
        run_command(["systemctl", "restart", "apache2"])
        
        logging.info("Apache SSL configured successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to configure Apache SSL: {e}")
        return False


def get_apache_vhost_info(paths: Dict[str, str]) -> Dict[str, str]:
    """
    Get information about Apache virtual hosts
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        Dictionary with virtual host information
    """
    info = {
        "status": "unknown",
        "config_path": paths["pop_apache_conf"],
        "enabled": False,
        "ssl": False
    }
    
    if not os.path.exists(paths["pop_apache_conf"]):
        info["status"] = "not_configured"
        return info
    
    # Check if site is enabled
    enabled_link = paths["pop_apache_conf"].replace('sites-available', 'sites-enabled')
    enabled_link = enabled_link.replace('.conf', '')
    
    if os.path.exists(enabled_link):
        info["enabled"] = True
    
    # Check for SSL configuration
    try:
        with open(paths["pop_apache_conf"], 'r') as f:
            config = f.read()
        
        if "<VirtualHost *:443>" in config:
            info["ssl"] = True
        
        info["status"] = "configured"
    except Exception:
        info["status"] = "error"
    
    return info
