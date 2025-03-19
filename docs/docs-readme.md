# PoP Documentation

This directory contains documentation for the Ubuntu Pro on Premises (PoP) system.

## Overview

PoP is a secure, air-gapped solution designed to deliver Ubuntu Pro services in isolated environments. It enables enterprises to bring the full power of Ubuntu Pro to networks without direct internet access, ensuring critical security updates and certified packages are available.

## Documentation Index

### Architecture and Design

- [Architecture Overview](ARCHITECTURE.md) - Overview of the modular architecture

### Module Documentation

- [Configuration Modules](CONFIG.md) - Command-line arguments and path management
- [Core Modules](CORE.md) - Contract data and authentication
- [Mirror Modules](MIRROR.md) - Repository configuration and synchronization
- [Web Modules](WEB.md) - Web UI and server configuration
- [Build Modules](BUILDS.md) - Build templates for VMs, containers, and snaps
- [Service Modules](SERVICES.md) - Service management (cron, TLS, snap proxy)
- [Utility Modules](UTILS.md) - Helper functions and utilities

### Guides

- [Installation Guide](INSTALLATION.md) - How to install and set up PoP
- [User Guide](USER_GUIDE.md) - How to use PoP
- [Migration Guide](MIGRATION.md) - Migrating from monolithic to modular structure
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Solutions to common issues
- [Development Guide](DEVELOPMENT.md) - Guide for developers

## Quick Start

For a quick start with PoP, see the main [README.md](../README.md) file in the repository root.

## Contributing to Documentation

Contributions to the documentation are welcome! Please follow these guidelines:

1. Use Markdown for all documentation
2. Follow the existing style and structure
3. Update the documentation index in this file when adding new documents
4. Keep the documentation up to date with code changes

## Building the Documentation

The documentation is primarily in Markdown format and can be viewed directly on GitHub or with any Markdown viewer. 

For a more polished presentation, you can use a documentation generator like MkDocs:

```bash
# Install MkDocs
pip install mkdocs

# Configure MkDocs (if not already done)
mkdocs new .

# Build the documentation
mkdocs build

# Serve the documentation locally
mkdocs serve
```

## License

The documentation is licensed under the same license as the PoP software. See the [LICENSE](../LICENSE) file in the repository root for details.
