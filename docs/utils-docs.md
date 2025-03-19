# Utility Modules

This document explains the utility modules in the PoP system.

## Overview

The utility modules provide common functionality used throughout the PoP system, including:

- System-level utilities
- Logging configuration
- Package management

These modules encapsulate reusable functionality to avoid code duplication and ensure consistent behavior across the system.

## Modules

### `system.py`

The `system.py` module provides system-level utilities.

#### Key Functions

- `check_sudo()`: Checks if script is running with sudo/root privileges
- `get_current_lts()`: Gets the current LTS release codename
- `get_system_fqdn_or_ip()`: Gets the system's FQDN or IP address
- `create_directories(paths)`: Creates required directories for PoP
- `run_command(cmd, capture_output, check, shell)`: Runs a system command with proper error handling

#### System Utilities Features

The system utilities include:

- Privilege checking for security
- System information retrieval
- Directory structure creation
- Command execution with error handling
- System path management

### `logger.py`

The `logger.py` module handles logging configuration.

#### Key Functions

- `setup_logging(verbose, log_file)`: Configures logging for the PoP application

#### Logging Features

The logging configuration includes:

- Console output for interactive use
- File output for record keeping
- Verbosity control
- Timestamp and severity level formatting
- Error tracking and diagnostic information

### `package.py`

The `package.py` module manages package installation and verification.

#### Key Functions

- `install_prerequisites(offline_repo)`: Installs required packages
- `download_pro_packages(paths)`: Downloads packages for offline installation
- `get_package_version(package)`: Gets installed version of a package
- `verify_package_installation(packages)`: Verifies that packages are installed

#### Package Management Features

The package management includes:

- Prerequisite installation
- Package caching for offline use
- Version checking
- Installation verification
- Repository management

## Usage Examples

### Running Commands

```python
from pop.utils.system import run_command

# Run a command with output capture
output = run_command(["apt-get", "update"], capture_output=True)
print(output)

# Run a command with error handling
try:
    run_command(["apt-get", "install", "-y", "nginx"], check=True)
    print("Nginx installed successfully")
except Exception as e:
    print(f"Failed to install Nginx: {e}")
```

### Setting Up Logging

```python
from pop.utils.logger import setup_logging

# Basic logging to console
setup_logging(verbose=False)

# Verbose logging to console and file
setup_logging(verbose=True, log_file="/srv/pop/pop.log")

# Use logging
import logging
logging.info("This is an informational message")
logging.debug("This is a debug message")
logging.warning("This is a warning message")
logging.error("This is an error message")
```

### Managing Packages

```python
from pop.utils.package import install_prerequisites, verify_package_installation

# Install prerequisites
install_prerequisites()

# Verify installation
required_packages = ["nginx", "apt-mirror", "jq"]
if verify_package_installation(required_packages):
    print("All required packages are installed")
else:
    print("Some packages are missing")
```

## Common Utilities

### System Checks

The system utilities provide various checks to ensure proper operation:

```python
from pop.utils.system import check_sudo, get_current_lts, get_system_fqdn_or_ip

# Check for sudo privileges
check_sudo()  # Exits if not running as root

# Get current LTS release
lts = get_current_lts()
print(f"Current LTS: {lts}")

# Get system FQDN or IP
host = get_system_fqdn_or_ip()
print(f"System host: {host}")
```

### Directory Management

The system utilities also handle directory creation and permissions:

```python
from pop.utils.system import create_directories

# Create required directories
paths = {
    "pop_dir": "/srv/pop",
    "pop_debs_dir": "/srv/pop/debs",
    "pop_gpg_dir": "/srv/pop/etc/apt/trusted.gpg.d",
    # Other paths...
}
create_directories(paths)
```

### Logging Levels

The logging module supports different verbosity levels:

- **ERROR**: Only show error messages
- **WARNING**: Show warnings and errors
- **INFO**: Show informational messages, warnings, and errors (default)
- **DEBUG**: Show all messages including debug information (verbose mode)

Example:

```python
import logging
from pop.utils.logger import setup_logging

# Enable verbose logging
setup_logging(verbose=True)

# Log messages at different levels
logging.debug("Detailed information for debugging")
logging.info("General information about operation")
logging.warning("Something unexpected but not critical")
logging.error("A serious problem occurred")
```

### Package Prerequisites

The package management utilities ensure all required packages are installed:

```
wget wget2 curl vim gawk apt-mirror apache2 nginx nginx-extras jq postgresql postgresql-contrib
```

Additional tools installed:

- **yq**: YAML processing tool (installed via snap)
- **snap-proxy-server**: Snap package proxy (installed via snap)
- **Pro packages**: Contracts and resource management (from PPA)
