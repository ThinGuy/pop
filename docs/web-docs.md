# Web Modules

This document explains the web-related modules in the PoP system.

## Overview

The web modules handle the web interface and server configurations, including:

- Web UI dashboard generation
- Apache server configuration
- Nginx server configuration

These modules provide a consistent interface for monitoring and managing PoP in a web browser.

## Modules

### `dashboard.py`

The `dashboard.py` module generates the web UI dashboard.

#### Key Functions

- `generate_web_ui(paths, resources, contract_data, release, architectures)`: Generates the web UI dashboard
- `get_mirror_stats(paths, release, architectures)`: Gets statistics about the mirror
- `create_dashboard_css(www_dir)`: Creates CSS styles for the dashboard
- `create_dashboard_js(www_dir)`: Creates JavaScript for the dashboard
- `create_nginx_config(paths)`: Creates Nginx configuration for the web UI
- `update_dashboard_data(paths, contract_data)`: Updates dashboard data without regenerating the entire UI

#### Web UI Features

The web UI dashboard includes:

- Overview of PoP status
- Account information
- Entitlements list with status
- Mirror statistics
- Responsive design using CSS

### `apache.py`

The `apache.py` module configures Apache to serve the mirrored repositories.

#### Key Functions

- `setup_apache_for_mirror(paths, mirror_host)`: Configures Apache to serve mirrored repositories
- `check_apache_status()`: Checks if Apache is running
- `configure_apache_ssl(paths, cert_path, key_path)`: Configures SSL for Apache
- `get_apache_vhost_info(paths)`: Gets information about Apache virtual hosts

#### Apache Configuration Features

The Apache configuration includes:

- Virtual host setup for mirror serving
- Directory aliases for Ubuntu Pro repositories
- Autoindex for repository browsing
- SSL configuration (optional)

### `nginx.py`

The `nginx.py` module configures Nginx to serve the web UI and mirrored repositories.

#### Key Functions

- `configure_nginx(paths, mirror_host)`: Configures Nginx to serve the web UI and mirrored repositories
- `configure_nginx_ssl(paths, mirror_host, cert_path, key_path)`: Configures Nginx with SSL support
- `verify_nginx_configuration(paths)`: Verifies Nginx configuration
- `disable_nginx_site(paths)`: Disables Nginx site

#### Nginx Configuration Features

The Nginx configuration includes:

- Server block for web UI
- Location directives for mirrored repositories
- SSL configuration (optional)
- HTTP to HTTPS redirection (with SSL)

## Usage Examples

### Generating Web UI

```python
from pop.config.args import parse_arguments
from pop.config.paths import setup_paths
from pop.core.contracts import pull_contract_data
from pop.core.resources import generate_resource_tokens
from pop.web.dashboard import generate_web_ui

# Parse arguments
args = parse_arguments()
paths = setup_paths(args)

# Get contract data and resources
contract_data = pull_contract_data(args.token, paths)
resources = generate_resource_tokens(args.token, paths)

# Generate web UI
generate_web_ui(
    paths, resources, contract_data, args.release, args.architectures
)
```

### Configuring Nginx with SSL

```python
from pop.web.nginx import configure_nginx_ssl

# Configure Nginx with SSL
cert_path = "/srv/pop/etc/ssl/pop-cert.pem"
key_path = "/srv/pop/etc/ssl/pop-key.pem"
configure_nginx_ssl(paths, "pop.example.com", cert_path, key_path)
```

### Setting Up Apache

```python
from pop.web.apache import setup_apache_for_mirror

# Set up Apache
setup_apache_for_mirror(paths, "pop.example.com")
```

## Web UI Structure

The web UI is organized into tabs:

### Overview Tab

The Overview tab displays key statistics and account information:

- Active entitlements count
- Total mirror size
- Total files count
- Last update time
- Account details (name, ID, effective dates)

### Entitlements Tab

The Entitlements tab lists all entitlements with their status:

- Type (e.g., infra, apps, fips)
- Status (entitled or not entitled)
- Supported suites (e.g., jammy, jammy-updates)

### Mirror Status Tab

The Mirror Status tab shows detailed mirror information:

- Last update time
- Total size
- Total files
- Release
- Architectures

## Server Configuration

### Apache vs. Nginx

Both Apache and Nginx are supported for serving the PoP content:

- **Apache**: Better for serving repository content due to extensive module support
- **Nginx**: Better for serving the web UI due to performance and simplicity

You can use both servers simultaneously, with Apache serving repositories and Nginx serving the web UI.

### SSL Configuration

SSL/TLS support is available for both servers:

- Self-signed certificates can be generated
- Custom certificates can be provided
- HTTP to HTTPS redirection is configured automatically
