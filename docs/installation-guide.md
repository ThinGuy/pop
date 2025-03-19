# Installation Guide

This document provides detailed instructions for installing and configuring the Ubuntu Pro on Premises (PoP) system.

## System Requirements

### Minimum Requirements

- Ubuntu 20.04 LTS (Focal) or newer
- 4 GB of RAM
- 20 GB of free disk space
- Valid Ubuntu Pro token
- Root/sudo access

### Recommended Requirements

- Ubuntu 22.04 LTS (Jammy)
- 8 GB of RAM or more
- 100+ GB of free disk space (for full repository mirroring)
- 2 or more CPU cores
- Valid Ubuntu Pro token with all required entitlements
- Root/sudo access

## Pre-Installation Steps

### Verify System Resources

Check available disk space:

```bash
df -h
```

Check system memory:

```bash
free -h
```

### Obtain Ubuntu Pro Token

If you don't already have an Ubuntu Pro token:

1. Visit [ubuntu.com/pro](https://ubuntu.com/pro) to obtain a subscription
2. Generate a token in your Canonical account dashboard
3. Make note of the token - you'll need it during installation

To view your current token on an attached system:

```bash
sudo pro token
```

### Prepare the System

Update your system:

```bash
sudo apt update
sudo apt upgrade -y
```

## Installation Methods

### Method 1: Direct Installation (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/ThinGuy/pop.git
   cd pop
   ```

2. Install the package:
   ```bash
   sudo pip install -e .
   ```

3. Run the installation:
   ```bash
   sudo pop --token YOUR_TOKEN [options]
   ```

### Method 2: Using the Script Directly

1. Clone the repository:
   ```bash
   git clone https://github.com/ThinGuy/pop.git
   cd pop
   ```

2. Make the script executable:
   ```bash
   chmod +x pop.py
   ```

3. Run the script:
   ```bash
   sudo ./pop.py --token YOUR_TOKEN [options]
   ```

### Method 3: Installation from Release Package

1. Download the latest release package:
   ```bash
   wget https://github.com/ThinGuy/pop/releases/download/v5.0.0/pop-appliance-5.0.0.tar.gz
   ```

2. Extract the package:
   ```bash
   tar -xzf pop-appliance-5.0.0.tar.gz
   cd pop-appliance-5.0.0
   ```

3. Install the package:
   ```bash
   sudo pip install .
   ```

4. Run the installation:
   ```bash
   sudo pop --token YOUR_TOKEN [options]
   ```

## Configuration Options

PoP offers many configuration options to customize your installation:

### Basic Options

- `--token YOUR_TOKEN`: Ubuntu Pro token (required)
- `--dir /path/to/pop`: Base directory for PoP installation (default: `/srv/pop`)
- `--release jammy`: Ubuntu release to configure (default: current LTS)
- `--arch amd64,arm64`: Architectures to support (default: `amd64`)
- `--verbose`: Enable verbose output

### Entitlement Options

- `--entitlements infra,apps,fips`: Entitlements to mirror (default: all available)
- `--include-source`: Include source packages in the mirror

### Mirror Options

- `--mirror-host pop.example.com`: Host for the local mirror (default: system hostname)
- `--mirror-port 80`: Port for the local mirror (default: 80)
- `--estimate-size`: Estimate mirror size before downloading
- `--run-apt-mirror`: Run apt-mirror to start the initial mirror download
- `--mirror-standard-repos`: Mirror standard Ubuntu repositories
- `--mirror-components main,restricted,universe,multiverse`: Components to mirror
- `--mirror-pockets release,updates,backports,security`: Pockets to mirror

### Server Options

- `--setup-apache`: Configure Apache to serve mirrored repositories
- `--setup-cron`: Set up cron job for regular mirror updates
- `--cron-schedule "0 */12 * * *"`: Cron schedule for mirror updates

### Web UI Options

- `--generate-web-ui`: Generate a web UI for monitoring PoP status

### TLS Options

- `--tls-cert /path/to/cert.pem`: Path to custom TLS certificate
- `--tls-key /path/to/key.pem`: Path to custom TLS key

### Build Options

- `--create-build-map`: Create file map for VM, container, and snap builds
- `--build-types vm,container,snap`: Build types to support

### Reconfiguration Options

- `--reconfigure`: Reconfigure PoP with new contract token without reinstalling

## Installation Examples

### Basic Installation

```bash
sudo pop --token YOUR_TOKEN
```

This will install PoP with default settings.

### Complete Installation with Web UI and Builds

```bash
sudo pop --token YOUR_TOKEN \
  --release jammy \
  --arch amd64,arm64 \
  --entitlements infra,apps,fips,cis \
  --include-source \
  --mirror-host pop.example.com \
  --setup-apache \
  --setup-cron \
  --generate-web-ui \
  --create-build-map \
  --run-apt-mirror \
  --verbose
```

This will create a complete PoP installation with all features.

### Installation for FIPS Compliance

```bash
sudo pop --token YOUR_TOKEN \
  --entitlements fips,fips-updates \
  --create-build-map \
  --build-types vm \
  --verbose
```

This will create an installation focused on FIPS compliance.

### Minimal Mirror Only

```bash
sudo pop --token YOUR_TOKEN \
  --entitlements infra \
  --arch amd64 \
  --setup-apache \
  --verbose
```

This will create a minimal mirror with only ESM Infra for amd64.

## Post-Installation Steps

### Verify Installation

Check that the installation was successful:

```bash
ls -la /srv/pop
cat /srv/pop/pop.rc
```

### Access Web UI

If you enabled the web UI, access it at:

```
http://your-server-hostname/
```

### Check Mirror Status

Check the mirror status:

```bash
ls -la /var/spool/apt-mirror/mirror
```

### Configure Clients

Configure client systems to use the mirror:

1. Copy the repository configuration:
   ```bash
   sudo scp /srv/pop/etc/apt/sources.list.d/pop.list client:/etc/apt/sources.list.d/
   ```

2. Copy the authentication files:
   ```bash
   sudo scp -r /srv/pop/etc/apt/auth.conf.d/* client:/etc/apt/auth.conf.d/
   sudo scp -r /srv/pop/etc/apt/trusted.gpg.d/* client:/etc/apt/trusted.gpg.d/
   ```

3. Update the client:
   ```bash
   sudo apt update
   ```

## Upgrading

### Upgrading PoP Code

To upgrade the PoP code to a newer version:

1. Pull the latest changes:
   ```bash
   cd pop
   git pull
   ```

2. Reinstall the package:
   ```bash
   sudo pip install -e .
   ```

### Reconfiguring with a New Token

To reconfigure PoP with a new token:

```bash
sudo pop --token NEW_TOKEN --reconfigure
```

## Troubleshooting Installation

### Common Installation Issues

#### Permission Denied

**Symptom:** "Permission denied" errors during installation

**Solution:** Run the script with sudo:
```bash
sudo ./pop.py --token YOUR_TOKEN
```

#### Package Installation Failures

**Symptom:** "Failed to install prerequisites" error

**Solution:** Check network connectivity and try installing packages manually:
```bash
sudo apt-get update
sudo apt-get install -y wget curl apt-mirror
```

#### Token Issues

**Symptom:** "Failed to pull contract data" error

**Solution:** Verify your token is valid:
```bash
sudo pro attach YOUR_TOKEN
sudo pro detach
```

#### Disk Space Issues

**Symptom:** "No space left on device" error during mirroring

**Solution:** Free up disk space or specify a different directory:
```bash
sudo pop --token YOUR_TOKEN --dir /path/with/more/space
```

### Getting Help

If you encounter an issue that you can't resolve, gather the following information:

1. PoP version:
   ```bash
   pop --version
   ```

2. Logs:
   ```bash
   cat /srv/pop/pop.log
   ```

3. System information:
   ```bash
   lsb_release -a
   uname -a
   df -h
   ```

Then contact your Canonical representative or file an issue on GitHub with this information.
