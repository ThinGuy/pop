"""
TLS certificate configuration for Ubuntu Pro on Premises (PoP)
"""

import os
import logging
import shutil
from typing import Dict, Optional

from pop.utils.system import run_command


def configure_tls_certificates(paths: Dict[str, str], tls_cert: str, tls_key: str) -> bool:
    """
    Configure TLS certificates for the mirror server
    
    Args:
        paths: Dictionary of system paths
        tls_cert: Path to TLS certificate
        tls_key: Path to TLS private key
        
    Returns:
        True if successful, False otherwise
    """
    if not tls_cert or not tls_key:
        logging.warning("TLS certificate or key not provided")
        return False
    
    try:
        # Create TLS directory if needed
        os.makedirs(paths["pop_tls_dir"], exist_ok=True)
        
        # Copy certificates to the proper location
        cert_path = os.path.join(paths["pop_tls_dir"], "pop-cert.pem")
        key_path = os.path.join(paths["pop_tls_dir"], "pop-key.pem")
        
        # Verify source files exist
        if not os.path.exists(tls_cert):
            logging.error(f"TLS certificate file not found: {tls_cert}")
            return False
            
        if not os.path.exists(tls_key):
            logging.error(f"TLS key file not found: {tls_key}")
            return False
        
        # Copy files
        shutil.copy2(tls_cert, cert_path)
        shutil.copy2(tls_key, key_path)
        
        # Set appropriate permissions
        os.chmod(cert_path, 0o644)
        os.chmod(key_path, 0o600)
        
        # Update nginx configuration to use SSL
        nginx_conf_path = paths["pop_nginx_conf"]
        nginx_conf_dir = os.path.dirname(nginx_conf_path)
        os.makedirs(nginx_conf_dir, exist_ok=True)
        
        # Read existing conf if it exists
        if os.path.exists(nginx_conf_path):
            with open(nginx_conf_path, 'r') as f:
                nginx_conf = f.read()
            
            # Check if already configured for SSL
            if "ssl_certificate" in nginx_conf:
                # Already configured
                logging.info("Nginx already configured for SSL")
                return True
        
        # Create new SSL-enabled configuration
        with open(nginx_conf_path, 'w') as f:
            f.write(f"""server {{
    listen 80;
    server_name _;
    
    # Redirect HTTP to HTTPS
    location / {{
        return 301 https://$host$request_uri;
    }}
}}

server {{
    listen 443 ssl;
    server_name _;
    
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
        
        os.symlink(nginx_conf_path, nginx_sites_enabled)
        
        # Reload nginx
        run_command(["systemctl", "reload", "nginx"])
        
        logging.info("TLS certificates configured successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to configure TLS certificates: {e}")
        return False


def verify_tls_certificates(paths: Dict[str, str]) -> Dict[str, str]:
    """
    Verify TLS certificates installed in the system
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        Dictionary with certificate information
    """
    cert_info = {
        "installed": False,
        "cert_path": "",
        "expires": "Unknown",
        "issuer": "Unknown",
        "subject": "Unknown"
    }
    
    # Check if certificates exist
    cert_path = os.path.join(paths["pop_tls_dir"], "pop-cert.pem")
    key_path = os.path.join(paths["pop_tls_dir"], "pop-key.pem")
    
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        return cert_info
    
    cert_info["installed"] = True
    cert_info["cert_path"] = cert_path
    
    # Get certificate details with openssl
    try:
        # Get expiration
        expires = run_command(
            ["openssl", "x509", "-in", cert_path, "-enddate", "-noout"],
            capture_output=True
        )
        if expires:
            cert_info["expires"] = expires.replace("notAfter=", "").strip()
        
        # Get issuer
        issuer = run_command(
            ["openssl", "x509", "-in", cert_path, "-issuer", "-noout"],
            capture_output=True
        )
        if issuer:
            cert_info["issuer"] = issuer.replace("issuer=", "").strip()
        
        # Get subject
        subject = run_command(
            ["openssl", "x509", "-in", cert_path, "-subject", "-noout"],
            capture_output=True
        )
        if subject:
            cert_info["subject"] = subject.replace("subject=", "").strip()
    except Exception as e:
        logging.error(f"Failed to get TLS certificate details: {e}")
    
    return cert_info


def generate_self_signed_certificate(paths: Dict[str, str], common_name: Optional[str] = None) -> bool:
    """
    Generate a self-signed TLS certificate
    
    Args:
        paths: Dictionary of system paths
        common_name: Common name for the certificate (default: system hostname)
        
    Returns:
        True if successful, False otherwise
    """
    import socket
    
    # If common name not provided, use system hostname
    if not common_name:
        common_name = socket.gethostname()
    
    # Ensure TLS directory exists
    os.makedirs(paths["pop_tls_dir"], exist_ok=True)
    
    # Certificate paths
    cert_path = os.path.join(paths["pop_tls_dir"], "pop-cert.pem")
    key_path = os.path.join(paths["pop_tls_dir"], "pop-key.pem")
    
    try:
        # Generate private key
        run_command([
            "openssl", "genrsa", 
            "-out", key_path, 
            "2048"
        ])
        
        # Set proper permissions on private key
        os.chmod(key_path, 0o600)
        
        # Generate certificate
        run_command([
            "openssl", "req", 
            "-new", "-x509", 
            "-key", key_path, 
            "-out", cert_path, 
            "-days", "3650",
            "-subj", f"/CN={common_name}"
        ])
        
        logging.info(f"Generated self-signed certificate for {common_name}")
        return True
    except Exception as e:
        logging.error(f"Failed to generate self-signed certificate: {e}")
        return False
