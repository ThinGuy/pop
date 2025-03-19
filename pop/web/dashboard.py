"""
Web dashboard generation for Ubuntu Pro on Premises (PoP)
"""

import os
import logging
import datetime
import subprocess
from typing import Dict, List, Any, Optional

from pop.core.contracts import extract_account_info, extract_entitlements
from pop.mirror.sync import verify_mirror


def generate_web_ui(paths: Dict[str, str], resources: Dict[str, str], 
                   contract_data: Dict[str, Any], release: str, 
                   architectures: List[str]) -> bool:
    """
    Generate web UI for monitoring PoP status
    
    Args:
        paths: Dictionary of system paths
        resources: Dictionary mapping entitlement types to resource tokens
        contract_data: Contract data from contracts.py
        release: Ubuntu release codename (e.g., 'jammy')
        architectures: List of architectures supported
        
    Returns:
        True if successful, False otherwise
    """
    logging.info("Generating web UI for PoP monitoring")
    
    try:
        # Create www directory
        www_dir = paths["pop_www_dir"]
        os.makedirs(www_dir, exist_ok=True)
        os.makedirs(f"{www_dir}/css", exist_ok=True)
        os.makedirs(f"{www_dir}/js", exist_ok=True)
        
        # Get contract info
        account_info = extract_account_info(contract_data)
        entitlements = extract_entitlements(contract_data)
        
        # Get mirror stats
        mirror_stats = get_mirror_stats(paths, release, architectures)
        
        # Generate entitlements table rows separately to avoid f-string errors
        entitlements_rows = ""
        for ent in entitlements:
            status_badge = '<span class="badge badge-success">Entitled</span>' if ent['entitled'] else '<span class="badge badge-danger">Not Entitled</span>'
            entitlements_rows += f"""
            <tr>
                <td>{ent['type']}</td>
                <td>{status_badge}</td>
                <td>{', '.join(ent['suites'])}</td>
            </tr>
            """
        
        # Create CSS file
        create_dashboard_css(www_dir)
        
        # Create JavaScript file
        create_dashboard_js(www_dir)
        
        # Create main HTML file
        with open(f"{www_dir}/index.html", 'w') as html_file:
            html_file.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ubuntu Pro on Premises</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="https://assets.ubuntu.com/v1/vanilla-framework-version-3.8.0.min.css" />
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>Ubuntu Pro on Premises (PoP)</h1>
        </div>
    </header>

    <main class="container" style="padding-top: 1.5rem;">
        <ul class="tabs">
            <li><a href="#" class="active" data-tab="overview">Overview</a></li>
            <li><a href="#" data-tab="entitlements">Entitlements</a></li>
            <li><a href="#" data-tab="mirror">Mirror Status</a></li>
        </ul>

        <div id="overview" class="tab-content">
            <div class="grid">
                <div class="stat-card">
                    <h3>{len([e for e in entitlements if e['entitled']])}</h3>
                    <p>Active Entitlements</p>
                </div>
                <div class="stat-card">
                    <h3>{mirror_stats['total_size']}</h3>
                    <p>Total Mirror Size</p>
                </div>
                <div class="stat-card">
                    <h3>{mirror_stats['total_files']}</h3>
                    <p>Total Files</p>
                </div>
                <div class="stat-card">
                    <h3>{mirror_stats['last_update']}</h3>
                    <p>Last Updated</p>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Account Information</h2>
                </div>
                <div class="card-body">
                    <table class="table">
                        <tr>
                            <th>Account Name</th>
                            <td>{account_info['name'] if account_info else 'Unknown'}</td>
                        </tr>
                        <tr>
                            <th>Account ID</th>
                            <td>{account_info['id'] if account_info else 'Unknown'}</td>
                        </tr>
                        <tr>
                            <th>Created At</th>
                            <td>{account_info['created_at'] if account_info else 'Unknown'}</td>
                        </tr>
                        <tr>
                            <th>Effective From</th>
                            <td>{account_info['effective_from'] if account_info else 'Unknown'}</td>
                        </tr>
                        <tr>
                            <th>Effective To</th>
                            <td>{account_info['effective_to'] if account_info else 'Unknown'}</td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>

        <div id="entitlements" class="tab-content" style="display: none;">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Entitlements</h2>
                </div>
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Status</th>
                                <th>Suites</th>
                            </tr>
                        </thead>
                        <tbody>
                            {entitlements_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="mirror" class="tab-content" style="display: none;">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Mirror Status</h2>
                </div>
                <div class="card-body">
                    <table class="table">
                        <tr>
                            <th>Last Update</th>
                            <td>{mirror_stats['last_update']}</td>
                        </tr>
                        <tr>
                            <th>Total Size</th>
                            <td>{mirror_stats['total_size']}</td>
                        </tr>
                        <tr>
                            <th>Total Files</th>
                            <td>{mirror_stats['total_files']}</td>
                        </tr>
                        <tr>
                            <th>Release</th>
                            <td>{mirror_stats['release']}</td>
                        </tr>
                        <tr>
                            <th>Architectures</th>
                            <td>{', '.join(mirror_stats['architectures'])}</td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>
    </main>

    <footer class="footer">
        <div class="container">
            <p>© {datetime.datetime.now().year} Canonical Ltd. Ubuntu and Canonical are registered trademarks of Canonical Ltd.</p>
        </div>
    </footer>

    <script src="js/dashboard.js"></script>
</body>
</html>
            """)
        
        # Create nginx configuration
        create_nginx_config(paths)
        
        logging.info(f"Web UI generated at {www_dir}")
        return True
    except Exception as e:
        logging.error(f"Failed to generate web UI: {e}")
        return False


def get_mirror_stats(paths: Dict[str, str], release: str, architectures: List[str]) -> Dict[str, Any]:
    """
    Get statistics about the mirror
    
    Args:
        paths: Dictionary of system paths
        release: Ubuntu release codename
        architectures: List of architectures supported
        
    Returns:
        Dictionary with mirror statistics
    """
    mirror_stats = {
        "last_update": "Never",
        "total_size": "0 GB",
        "total_files": 0,
        "architectures": architectures,
        "release": release
    }
    
    # Try to get actual mirror stats if available
    mirror_path = "/var/spool/apt-mirror/mirror"
    if os.path.exists(mirror_path):
        # Get last update time
        try:
            last_update = subprocess.check_output(
                ["stat", "-c", "%y", mirror_path], 
                text=True
            ).strip()
            mirror_stats["last_update"] = last_update
        except subprocess.SubprocessError:
            pass
            
        # Get total size
        try:
            total_size = subprocess.check_output(
                ["du", "-sh", mirror_path], 
                text=True
            ).split()[0]
            mirror_stats["total_size"] = total_size
        except subprocess.SubprocessError:
            pass
            
        # Get total files
        try:
            total_files = subprocess.check_output(
                ["find", mirror_path, "-type", "f", "|", "wc", "-l"], 
                shell=True, 
                text=True
            ).strip()
            mirror_stats["total_files"] = total_files
        except subprocess.SubprocessError:
            pass
    
    return mirror_stats


def create_dashboard_css(www_dir: str) -> str:
    """
    Create CSS file for dashboard
    
    Args:
        www_dir: Directory to store web files
        
    Returns:
        Path to created CSS file
    """
    css_path = os.path.join(www_dir, "css/style.css")
    
    with open(css_path, 'w') as css_file:
        css_file.write("""
:root {
    --color-primary: #0066cc;
    --color-secondary: #f2f2f2;
    --color-success: #38b44a;
    --color-warning: #f99b11;
    --color-danger: #c7162b;
    --color-text: #111111;
    --color-muted: #666666;
    --color-bg: #ffffff;
    --color-bg-alt: #f7f7f7;
    --color-border: #cdcdcd;
    --font-family: "Ubuntu", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: var(--font-family);
    color: var(--color-text);
    background-color: var(--color-bg);
    line-height: 1.5;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

.header {
    background-color: #772953;
    color: white;
    padding: 1rem 0;
}

.header h1 {
    font-size: 1.5rem;
    font-weight: 300;
}

.card {
    background-color: var(--color-bg);
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    margin-bottom: 1.5rem;
    overflow: hidden;
}

.card-header {
    background-color: var(--color-secondary);
    padding: 1rem;
    border-bottom: 1px solid var(--color-border);
}

.card-title {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 400;
}

.card-body {
    padding: 1rem;
}

.table {
    width: 100%;
    border-collapse: collapse;
}

.table th, .table td {
    text-align: left;
    padding: 0.75rem;
    border-bottom: 1px solid var(--color-border);
}

.table th {
    font-weight: 500;
    background-color: var(--color-secondary);
}

.table-striped tbody tr:nth-of-type(odd) {
    background-color: var(--color-bg-alt);
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.875rem;
    font-weight: 500;
}

.badge-success {
    background-color: var(--color-success);
    color: white;
}

.badge-danger {
    background-color: var(--color-danger);
    color: white;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1.5rem;
}

.stat-card {
    background-color: var(--color-bg);
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    padding: 1.5rem;
    text-align: center;
}

.stat-card h3 {
    font-size: 2rem;
    font-weight: 300;
    margin-bottom: 0.5rem;
}

.stat-card p {
    color: var(--color-muted);
    font-size: 0.875rem;
    margin: 0;
}

.footer {
    text-align: center;
    padding: 2rem 0;
    color: var(--color-muted);
}

.tabs {
    display: flex;
    list-style: none;
    border-bottom: 1px solid var(--color-border);
    margin-bottom: 1.5rem;
}

.tabs li a {
    display: block;
    padding: 0.5rem 1rem;
    text-decoration: none;
    color: var(--color-muted);
    border-bottom: 2px solid transparent;
}

.tabs li a.active {
    color: var(--color-primary);
    border-bottom-color: var(--color-primary);
}

@media (max-width: 768px) {
    .grid {
        grid-template-columns: 1fr;
    }
}
        """)
    
    return css_path


def create_dashboard_js(www_dir: str) -> str:
    """
    Create JavaScript file for dashboard
    
    Args:
        www_dir: Directory to store web files
        
    Returns:
        Path to created JavaScript file
    """
    js_path = os.path.join(www_dir, "js/dashboard.js")
    
    with open(js_path, 'w') as js_file:
        js_file.write("""
// Simple tab switching
document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('.tabs li a');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Hide all tab content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.style.display = 'none';
            });
            
            // Show the selected tab content
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).style.display = 'block';
        });
    });
});
        """)
    
    return js_path


def create_nginx_config(paths: Dict[str, str]) -> bool:
    """
    Create Nginx configuration for web UI
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create nginx configuration directory if needed
        nginx_conf_dir = os.path.dirname(paths["pop_nginx_conf"])
        os.makedirs(nginx_conf_dir, exist_ok=True)
        
        with open(paths["pop_nginx_conf"], 'w') as nginx_file:
            nginx_file.write(f"""server {{
    listen 80;
    server_name _;

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
        
        # Reload nginx
        subprocess.run(["systemctl", "reload", "nginx"], check=True)
        
        return True
    except Exception as e:
        logging.error(f"Failed to create Nginx configuration: {e}")
        return False


def update_dashboard_data(paths: Dict[str, str], contract_data: Dict[str, Any]) -> bool:
    """
    Update dashboard data without regenerating entire UI
    
    Args:
        paths: Dictionary of system paths
        contract_data: Contract data from contracts.py
        
    Returns:
        True if successful, False otherwise
    """
    # This would implement a data update API for dashboard
    # Not fully implemented yet
    logging.info("Dashboard data update not implemented yet")
    return False
