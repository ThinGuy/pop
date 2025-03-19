"""
Nginx configuration for Ubuntu Pro on Premises (PoP)
"""

import os
import logging
import shutil
from typing import Dict, Optional, Any

from pop.utils.system import run_command


def configure_nginx(paths: Dict[str, str], mirror_host: str) -> bool:
    """
    Configure Nginx to serve the web UI and mirrored repositories
    
    Args:
        paths: Dictionary of system paths
        mirror_host: Host name for mirror server
        
    Returns:
        True if successful, False otherwise
    """
    logging.info("Configuring Nginx for web UI and mirror")
    
    try:
        # Create Nginx configuration directory if needed
        nginx_conf_dir = os.path.dirname(paths["pop_nginx_conf"])
        os.makedirs(nginx_conf_dir, exist_ok=True)
        
        # Create Nginx configuration file
        with open(paths["pop_nginx_conf"], 'w') as f:
            f.write(f"""server {{
    listen 80;
    server_name {mirror_host};

    root {paths["pop_www_dir"]};
    index index.html;

    location / {{
        try_files $uri $uri/ =404;
    }}

    # Serve apt-mirror content
    location /mirror/ {{
        alias /var/spool/apt-mirror/mirror/;
        autoindex on;
    }}
}}
""")
        
        # Create symlink to enable the site
        nginx_sites_enabled = "/etc/nginx/sites-enabled/pop"
        if os.path.exists(nginx_sites_enabled):
            os.unlink(nginx_sites_enabled)
        
        os.symlink(paths["pop_nginx_conf"], nginx_sites_enabled)
        
        # Reload Nginx
        run_command(["systemctl", "reload", "nginx"])
        
        logging.info("Nginx configured successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to configure Nginx: {e}")
        return False


def configure_nginx_ssl(paths: Dict[str, str], mirror_host: str, cert_path: str, key_path: str) -> bool:
    """
    Configure Nginx with SSL support
    
    Args:
        paths: Dictionary of system paths
        mirror_host: Host name for mirror server
        cert_path: Path to SSL certificate
        key_path: Path to SSL key
        
    Returns:
        True if successful, False otherwise
    """
    logging.info("Configuring Nginx with SSL support")
    
    try:
        # Create Nginx configuration directory if needed
        nginx_conf_dir = os.path.dirname(paths["pop_nginx_conf"])
        os.makedirs(nginx_conf_dir, exist_ok=True)
        
        # Create Nginx configuration file with SSL support
        with open(paths["pop_nginx_conf"], 'w') as f:
            f.write(f"""server {{
    listen 80;
    server_name {mirror_host};
    
    # Redirect HTTP to HTTPS
    location / {{
        return 301 https://$host$request_uri;
    }}
}}

server {{
    listen 443 ssl;
    server_name {mirror_host};
    
    ssl_certificate {cert_path};
    ssl_certificate_key {key_path};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    root {paths["pop_www_dir"]};
    index index.html;
    
    location / {{
        try_files $uri $uri/ =404;
    }}
    
    # Serve apt-mirror content
    location /mirror/ {{
        alias /var/spool/apt-mirror/mirror/;
        autoindex on;
    }}
}}
""")
        
        # Create symlink to enable the site
        nginx_sites_enabled = "/etc/nginx/sites-enabled/pop"
        if os.path.exists(nginx_sites_enabled):
            os.unlink(nginx_sites_enabled)
        
        os.symlink(paths["pop_nginx_conf"], nginx_sites_enabled)
        
        # Reload Nginx
        run_command(["systemctl", "reload", "nginx"])
        
        logging.info("Nginx configured with SSL successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to configure Nginx with SSL: {e}")
        return False


def verify_nginx_configuration(paths: Dict[str, str]) -> Dict[str, Any]:
    """
    Verify Nginx configuration
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        Dictionary with configuration status
    """
    status = {
        "configured": False,
        "enabled": False,
        "ssl": False,
        "valid": False,
        "running": False
    }
    
    # Check if configuration file exists
    if not os.path.exists(paths["pop_nginx_conf"]):
        return status
    
    status["configured"] = True
    
    # Check if site is enabled
    nginx_sites_enabled = "/etc/nginx/sites-enabled/pop"
    if os.path.exists(nginx_sites_enabled) and os.path.islink(nginx_sites_enabled):
        status["enabled"] = True
    
    # Check if SSL is configured
    try:
        with open(paths["pop_nginx_conf"], 'r') as f:
            content = f.read()
            if "ssl_certificate" in content:
                status["ssl"] = True
    except:
        pass
    
    # Check if configuration is valid
    try:
        run_command(["nginx", "-t"], capture_output=True)
        status["valid"] = True
    except:
        pass
    
    # Check if Nginx is running
    try:
        result = run_command(["systemctl", "is-active", "nginx"], capture_output=True)
        if result.strip() == "active":
            status["running"] = True
    except:
        pass
    
    return status


def disable_nginx_site(paths: Dict[str, str]) -> bool:
    """
    Disable Nginx site
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        True if successful, False otherwise
    """
    logging.info("Disabling Nginx site")
    
    try:
        # Remove symlink from sites-enabled
        nginx_sites_enabled = "/etc/nginx/sites-enabled/pop"
        if os.path.exists(nginx_sites_enabled):
            os.unlink(nginx_sites_enabled)
        
        # Reload Nginx
        run_command(["systemctl", "reload", "nginx"])
        
        logging.info("Nginx site disabled successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to disable Nginx site: {e}")
        return False
