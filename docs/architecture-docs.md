# PoP Architecture Overview

This document provides an overview of the modular architecture of the Ubuntu Pro on Premises (PoP) system.

## Architecture Overview

PoP has been structured as a modular Python package to improve maintainability, testability, and extensibility. The codebase is organized into logically separated modules, each with well-defined responsibilities.

```
pop/
├── __init__.py              # Package initialization
├── main.py                  # Main entry point and CLI handling
├── config/                  # Configuration management
│   ├── __init__.py
│   ├── args.py              # Argument parsing
│   └── paths.py             # Path management
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── contracts.py         # Contract handling
│   ├── auth.py              # Authentication file management
│   ├── gpg.py               # GPG key management
│   └── resources.py         # Resource token management
├── mirror/                  # Mirror management
│   ├── __init__.py
│   ├── apt_mirror.py        # apt-mirror configuration
│   ├── estimator.py         # Mirror size estimation
│   ├── repository.py        # Repository management
│   └── sync.py              # Mirror synchronization
├── web/                     # Web UI and servers
│   ├── __init__.py
│   ├── dashboard.py         # Web UI generator
│   ├── apache.py            # Apache configuration
│   └── nginx.py             # Nginx configuration
├── builds/                  # Build templates
│   ├── __init__.py
│   ├── vm.py                # VM build templates
│   ├── container.py         # Container build templates
│   ├── snap.py              # Snap build templates
│   └── manager.py           # Build management
├── services/                # Service management
│   ├── __init__.py
│   ├── cron.py              # Cron job management
│   ├── tls.py               # TLS configuration
│   └── snap_proxy.py        # Snap proxy configuration
└── utils/                   # Utilities
    ├── __init__.py
    ├── system.py            # System utilities
    ├── logger.py            # Logging utilities
    └── package.py           # Package management utilities
```

## Component Responsibilities

### Main Entry Point

The `main.py` module serves as the central orchestrator for the entire application. It:

1. Parses command-line arguments
2. Sets up logging
3. Coordinates the execution of operations based on user input
4. Reports results back to the user

### Configuration (config/)

The configuration modules handle all aspects of configuring the PoP application:

- `args.py`: Command-line argument definition and parsing
- `paths.py`: Manages system paths and configuration file handling

### Core Functionality (core/)

The core modules provide the essential functionality for PoP:

- `contracts.py`: Contract data handling and processing
- `resources.py`: Resource token management
- `auth.py`: Authentication file creation and management
- `gpg.py`: GPG key management

### Mirror Management (mirror/)

Mirror modules handle repository configuration and synchronization:

- `repository.py`: Repository configuration
- `estimator.py`: Mirror size estimation
- `sync.py`: Mirror synchronization with apt-mirror

### Web UI and Servers (web/)

Web-related modules manage the web dashboard and server configurations:

- `dashboard.py`: Web UI generation
- `apache.py`: Apache server configuration
- `nginx.py`: Nginx server configuration

### Build Templates (builds/)

Build template modules generate templates for various deployment targets:

- `vm.py`: VM deployment templates
- `container.py`: Container deployment templates
- `snap.py`: Snap package templates
- `manager.py`: Unified build management

### Service Management (services/)

Service modules handle various system services:

- `cron.py`: Cron job configuration
- `tls.py`: TLS certificate management
- `snap_proxy.py`: Snap proxy server configuration

### Utilities (utils/)

Utility modules provide common functionality:

- `system.py`: System-level utilities
- `logger.py`: Logging configuration
- `package.py`: Package management utilities

## Component Interaction

1. The main entry point (`main.py`) orchestrates the overall flow
2. Configuration modules parse user input and set up paths
3. Core modules handle Pro contract data and authentication
4. Mirror modules configure and synchronize repositories
5. Web and service modules configure necessary services
6. Build modules generate deployment templates

## Compatibility

For backward compatibility, a wrapper script (`pop.py`) is provided in the repository root. This script simply delegates to the modular implementation while maintaining the same command-line interface.
