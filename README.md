# Ubuntu Pro on Premises (PoP)

[![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-20.04%2B-orange)](https://ubuntu.com/)
[![Security](https://img.shields.io/badge/Security-FIPS%20Ready-brightgreen)](https://ubuntu.com/security)


![Ubuntu Pro](img/Ubuntu-Pro-Logo-Light.jpg)

**PoP** is a secure, air-gapped solution designed to deliver **Ubuntu Pro** services in isolated environments. It enables enterprises to bring the full power of Ubuntu Pro to networks without direct internet access, ensuring critical security updates and certified packages are available.

## About This Project

This repository contains a modular implementation of the PoP tooling, designed for better maintainability and extensibility. The code has been refactored from a monolithic script into a well-organized Python package.

## Features

- **Air-gapped Ubuntu Pro**: Deploy Ubuntu Pro services without internet connectivity
- **Resource Token Management**: Efficient handling of Ubuntu Pro entitlements
- **Security Package Mirroring**: Offline access to ESM (Extended Security Maintenance) packages
- **Automated Configuration**: Simple deployment with minimal manual intervention
- **Web Dashboard**: Monitor entitlements, repository status, and system health
- **Build Templates**: Ready-to-use templates for VMs, containers, and snaps
- **Snap Proxy Integration**: Offline snap package management
- **Reconfiguration Support**: Update contract tokens without reinstallation
- **FIPS Compliance**: Built-in FIPS mode for VM deployments
- **Size Estimation**: Preview mirror size before downloading

## Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/ThinGuy/pop.git
cd pop

# Install the package
sudo pip install -e .

# Run PoP with your Ubuntu Pro token
sudo pop --token YOUR_TOKEN
```

### Advanced Installation

```bash
# Install with all dependencies
sudo pip install -e '.[dev,test]'

# Full installation with custom settings
sudo pop \
  --token YOUR_TOKEN \
  --dir /path/to/pop \
  --release jammy \
  --arch amd64,arm64 \
  --entitlements infra,apps,fips,cis \
  --include-source \
  --mirror-host pop.internal \
  --mirror-port 80 \
  --generate-web-ui \
  --estimate-size \
  --verbose
```

## Project Structure

The project has been organized into the following modules:

```
pop/
├── __init__.py              # Package initialization
├── main.py                  # Main entry point and CLI handling
├── config/                  # Configuration management
│   ├── __init__.py
│   ├── args.py              # Argument parsing
│   ├── paths.py             # Path management
│   └── validator.py         # Config validation
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
│   └── snap.py              # Snap build templates
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

## Development

### Setting Up a Development Environment

```bash
# Clone the repository
git clone https://github.com/ThinGuy/pop.git
cd pop

# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e '.[dev]'
```

### Running Tests

```bash
# Run unit tests
pytest

# Run with coverage
pytest --cov=pop tests/
```

### Code Style

This project follows PEP 8 style guidelines. You can check your code with:

```bash
# Check style
flake8 pop

# Format code
black pop
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The Ubuntu Pro team at Canonical
- Contributors to the air-gapped Ubuntu Pro technologies****
