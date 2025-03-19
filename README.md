# Ubuntu Pro on Premises Appliance (PoPA)

![Ubuntu Pro](img/Ubuntu-Pro-Logo-Light.jpg)

**PoPA** is a secure, air-gapped solution designed to deliver **Ubuntu Pro** services in isolated environments. It enables enterprises to bring the full power of Ubuntu Pro to networks without direct internet access, ensuring critical security updates and certified packages are available.

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

## Requirements

- Ubuntu 20.04 LTS (Focal) or later
- Valid Ubuntu Pro token
- Administrative (sudo) privileges
- Minimum 20GB of free disk space (more recommended for package mirroring)
- 4GB RAM or more

## Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/popa.git
cd popa

# Run the installer with your Ubuntu Pro token
sudo ./popa.py --token YOUR_TOKEN
```

### Advanced Installation

```bash
# Full installation with custom settings
sudo ./popa.py \
  --token YOUR_TOKEN \
  --dir /path/to/popa \
  --release jammy \
  --arch amd64,arm64 \
  --entitlements infra,apps,fips,cis \
  --include-source \
  --mirror-host popa.internal \
  --mirror-port 80 \
  --generate-web-ui \
  --estimate-size \
  --verbose
```

## Usage Examples

### Basic PoPA Server Setup

```bash
sudo ./popa.py --token YOUR_TOKEN
```

### Mirror for Multiple Architectures

```bash
sudo ./popa.py --token YOUR_TOKEN --arch amd64,arm64,s390x
```

### Create Build Templates

```bash
sudo ./popa.py --token YOUR_TOKEN --create-build-map
```

### Reconfigure with New Token

```bash
sudo ./popa.py --token NEW_TOKEN --reconfigure
```

### Use Local Mirror Hostname

```bash
sudo ./popa.py --token YOUR_TOKEN --mirror-host popa.example.com
```

### Estimate Mirror Size

```bash
sudo ./popa.py --token YOUR_TOKEN --estimate-size
```

### Complete Air-Gapped Solution

```bash
sudo ./popa.py \
  --token YOUR_TOKEN \
  --generate-web-ui \
  --create-build-map \
  --mirror-host air-gap.internal \
  --estimate-size
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `--token` | Ubuntu Pro token (required) | None |
| `--dir` | Base installation directory | `/srv/popa` |
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
| `--verbose` | Enable detailed logging | False |

## Web Dashboard

When enabled with `--generate-web-ui`, PoPA creates a web interface accessible at:

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
   sudo ./popa.py --token YOUR_TOKEN --entitlements infra,apps,fips,fips-updates
   ```

2. Use the VM build templates which include the required `fips=1` kernel parameter:
   ```bash
   sudo ./popa.py --token YOUR_TOKEN --create-build-map --build-types vm
   ```

## Directory Structure

```
/srv/popa/                   # Default installation directory
├── debs/                    # Cached package files
├── etc/
│   ├── apt/
│   │   ├── auth.conf.d/     # APT authentication files
│   │   └── trusted.gpg.d/   # GPG keys for repositories
│   ├── mirror.list          # APT mirror configuration
│   ├── nginx/               # Web server configuration
│   └── ssl/                 # TLS certificates (if used)
├── builds/                  # Build templates
│   ├── vm/                  # VM deployment files with FIPS config
│   ├── container/           # Container build files
│   └── snap/                # Snap package templates
├── www/                     # Web dashboard files
├── snap-proxy/              # Snap proxy configuration
├── popa.json                # Contract information
├── popa_resources.json      # Resource tokens
├── popa.log                 # Operation logs
└── popa.rc                  # Runtime configuration
```

## Client Configuration

### Configure Ubuntu clients to use PoPA

1. **Add the repository**:

```bash
echo "deb http://popa-server/mirror/esm.ubuntu.com/infra/ubuntu jammy main" | sudo tee /etc/apt/sources.list.d/ubuntu-popa.list
```

2. **Add the authentication**:

```bash
# Copy from PoPA server
sudo scp popa-server:/srv/popa/etc/apt/auth.conf.d/91ubuntu-pro /etc/apt/auth.conf.d/
sudo scp -r popa-server:/srv/popa/etc/apt/trusted.gpg.d/* /etc/apt/trusted.gpg.d/
```

3. **Update package lists**:

```bash
sudo apt update
```

## Building with PoPA Templates

### Virtual Machine Images with FIPS Support

```bash
cd /srv/popa/builds/vm
# Follow instructions in README.md to include FIPS kernel parameter
```

### Container Images

```bash
cd /srv/popa/builds/container
docker build -t popa-enabled-container .
```

### Snap Packages

```bash
cd /srv/popa/builds/snap
snapcraft
```

## Troubleshooting

### Repository Access Issues

Check authentication file permissions:

```bash
sudo chmod 600 /etc/apt/auth.conf.d/91ubuntu-pro
```

### Mirror Sync Problems

Run apt-mirror manually:

```bash
sudo apt-mirror /srv/popa/etc/mirror.list
```

### Web Dashboard Not Accessible

Ensure nginx is running and configured:

```bash
sudo systemctl status nginx
sudo nginx -t
```

### Reconfiguration Issues

If reconfiguration fails, verify your installation directory:

```bash
sudo ls -la /srv/popa
# Check if directory exists and has correct permissions
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The Ubuntu Pro team at Canonical
- Contributors to the air-gapped Ubuntu Pro technologies
