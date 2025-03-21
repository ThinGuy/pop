# Ubuntu Pro on Premises (PoP)

![Ubuntu Pro](img/Ubuntu-Pro-Logo-Light.jpg)

**PoP** is a secure, air-gapped solution designed to deliver **Ubuntu Pro** services in isolated environments. It enables enterprises to bring the full power of Ubuntu Pro to networks without direct internet access, ensuring critical security updates and certified packages are available.

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
- **Production Mode**: Configure services to start automatically at boot

## New Modular Architecture

PoP has been redesigned with a modular architecture for improved maintainability, testability, and extensibility. The codebase is organized into logical modules:

```
pop/
├── config/     # Configuration handling
├── core/       # Contract and auth management
├── mirror/     # Repository configuration
├── web/        # Web UI and server configuration
├── builds/     # Build template generation
├── services/   # Service management
└── utils/      # Common utilities
```

This architecture allows for easier development, better testing, and simplified extension with new features.

## Requirements

- Ubuntu 20.04 LTS (Focal) or later
- Valid Ubuntu Pro token
- Administrative (sudo) privileges
- Minimum 20GB of free disk space (more recommended for package mirroring)
- 4GB RAM or more

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ThinGuy/pop.git
cd pop

# Install the package
sudo pip install -e .

# Run PoP with your token
sudo pop --token YOUR_TOKEN
```

### Advanced Installation

```bash
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

## Usage Examples

### Basic PoP Server Setup

```bash
sudo pop --token YOUR_TOKEN
```

### Mirror for Multiple Architectures

```bash
sudo pop --token YOUR_TOKEN --arch amd64,arm64,s390x
```

### Create Build Templates

```bash
sudo pop --token YOUR_TOKEN --create-build-map
```

### Reconfigure with New Token

```bash
sudo pop --token NEW_TOKEN --reconfigure
```

### Use Local Mirror Hostname

```bash
sudo pop --token YOUR_TOKEN --mirror-host pop.example.com
```

### Estimate Mirror Size

```bash
sudo pop --token YOUR_TOKEN --estimate-size
```

### Complete Air-Gapped Solution

```bash
sudo pop \
  --token YOUR_TOKEN \
  --generate-web-ui \
  --create-build-map \
  --mirror-host air-gap.internal \
  --estimate-size
```

### Production Deployment

```bash
sudo pop \
  --token YOUR_TOKEN \
  --generate-web-ui \
  --setup-apache \
  --production \
  --run-apt-mirror
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `--token` | Ubuntu Pro token (required) | None |
| `--dir` | Base installation directory | `/srv/pop` |
| `--release` | Ubuntu release codename | Current LTS |
| `--arch` | Comma-separated list of architectures | `amd64` |
| `--entitlements` | Comma-separated list of entitlements | `infra,apps,fips,fips-updates,fips-preview,cis,usg` |
| `--include-source` | Include source packages in the mirror | False |
| `--mirror-host` | Override hostname for repository URLs | System hostname or IP |
| `--mirror-port` | Port for the local mirror server | `80` |
| `--contract-port` | Port for the contracts server | `8484` |
| `--tls-cert` | Path to custom TLS certificate | None |
| `--tls-key` | Path to custom TLS key | None |
| `--offline-repo` | PPA for air-gapped Pro packages | `ppa:yellow/ua-airgapped` |
| `--create-build-map` | Create templates for VMs, containers, etc. | False |
| `--build-types` | Types of build templates to create | `vm,container,snap` |
| `--generate-web-ui` | Create web dashboard for monitoring | False |
| `--reconfigure` | Update contract token without reinstalling | False |
| `--estimate-size` | Estimate mirror size before downloading | False |
| `--production` | Configure services to start at boot | False |
| `--verbose` | Enable detailed logging | False |

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Installation Guide](docs/INSTALLATION.md)
- [User Guide](docs/USER_GUIDE.md)
- [Module Documentation](docs/README.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- [Migration Guide](docs/MIGRATION.md) (from monolithic to modular)
- [Development Guide](docs/DEVELOPMENT.md)
- [Systemd Services](docs/SYSTEMD.md)

## Web Dashboard

When enabled with `--generate-web-ui`, PoP creates a web interface accessible at:

```
http://your-server-ip/
```

The dashboard provides:

- **Overview**: Mirror status, entitlement counts, and disk usage
- **Entitlements**: List of available Ubuntu Pro entitlements
- **Mirror Status**: Repository details and synchronization information

## FIPS Compliance

For environments requiring FIPS-validated cryptographic modules:

1. Include the `fips` entitlement:
   ```bash
   sudo pop --token YOUR_TOKEN --entitlements infra,apps,fips,fips-updates
   ```

2. Use the VM build templates which include the required `fips=1` kernel parameter:
   ```bash
   sudo pop --token YOUR_TOKEN --create-build-map --build-types vm
   ```

## Production Deployment

For production environments, PoP can configure systemd services to ensure all components start automatically at boot time:

1. Configure with production flag:
   ```bash
   sudo pop --token YOUR_TOKEN --setup-apache --generate-web-ui --production
   ```

2. This creates and enables:
   - Contract server service (`pop-contracts`)
   - Web server services (Apache and/or Nginx)
   - Mirror update timer (`pop-mirror.timer`)

3. Manage services with standard systemd commands:
   ```bash
   sudo systemctl status pop-contracts
   sudo systemctl status apache2
   sudo systemctl status nginx
   sudo systemctl status pop-mirror.timer
   ```

See [Systemd Services](docs/SYSTEMD.md) for detailed documentation.

## Client Configuration

### Configure Ubuntu clients to use PoP

1. **Add the repository**:

```bash
echo "deb http://pop-server/mirror/esm.ubuntu.com/infra/ubuntu jammy main" | sudo tee /etc/apt/sources.list.d/ubuntu-pop.list
```

2. **Add the authentication**:

```bash
# Copy from PoP server
sudo scp pop-server:/srv/pop/etc/apt/auth.conf.d/91ubuntu-pro /etc/apt/auth.conf.d/
sudo scp -r pop-server:/srv/pop/etc/apt/trusted.gpg.d/* /etc/apt/trusted.gpg.d/
```

3. **Update package lists**:

```bash
sudo apt update
```

## Contributing

Contributions are welcome! Please see [DEVELOPMENT.md](docs/DEVELOPMENT.md) for guidelines on contributing to the project.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The Ubuntu Pro team at Canonical
- Contributors to the air-gapped Ubuntu Pro technologies
