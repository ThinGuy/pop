# User Guide

This document provides guidance on using the Ubuntu Pro on Premises (PoP) system after installation.

## Overview

PoP creates an air-gapped Ubuntu Pro environment with the following components:

- **Mirror Server**: Local copy of Ubuntu Pro repositories
- **Web Dashboard**: Interface for monitoring system status
- **Build Templates**: Resources for creating VMs, containers, and snaps
- **Service Configuration**: Background services for automation

This guide walks you through how to use these components effectively.

## Getting Started

### Accessing the Web Dashboard

If you enabled the web UI during installation, you can access it using your web browser:

```
http://your-server-hostname/
```

The dashboard provides:

- Overview of system status
- List of enabled entitlements
- Mirror statistics

### Viewing Configuration

To see your current PoP configuration:

```bash
cat /srv/pop/pop.rc
```

This file contains all the settings used during installation, including:

- Ubuntu Pro token
- Release and architectures
- Entitlements
- Paths to configuration files

## Managing the Mirror

### Running Manual Updates

To manually update the mirror:

```bash
sudo apt-mirror
```

Or with a specific mirror list:

```bash
sudo apt-mirror /srv/pop/etc/mirror.list
```

### Checking Mirror Status

To check the mirror status:

```bash
du -sh /var/spool/apt-mirror/mirror
find /var/spool/apt-mirror/mirror -type f | wc -l
```

### Cleaning Up Old Packages

To clean up old packages and free up space:

```bash
sudo /var/spool/apt-mirror/var/clean.sh
```

### Managing Cron Updates

If you enabled cron updates during installation, they will run automatically according to the specified schedule (default: every 12 hours).

To modify the schedule:

```bash
sudo vi /etc/cron.d/pop-mirror
```

To disable cron updates:

```bash
sudo rm /etc/cron.d/pop-mirror
```

To re-enable cron updates:

```bash
sudo pop --token YOUR_TOKEN --setup-cron --reconfigure
```

## Using Build Templates

### VM Templates

VM templates are located in `/srv/pop/builds/vm/`. They include:

- GRUB configuration with FIPS mode enabled
- Cloud-init configuration for Ubuntu Pro
- Repository configuration

To use VM templates:

1. Copy the templates to your VM build environment
2. Follow the instructions in the README.md file

Example for cloud-init:

```bash
# Create a VM with cloud-init
cloud-localds -v cloud-init.img /srv/pop/builds/vm/cloud-init.yaml
```

### Container Templates

Container templates are located in `/srv/pop/builds/container/`. They include:

- Dockerfile for Ubuntu Pro containers
- Docker Compose configuration
- Build scripts

To build a container:

```bash
cd /srv/pop/builds/container
./build.sh
```

To customize the container, edit the Dockerfile:

```bash
vi /srv/pop/builds/container/Dockerfile
```

### Snap Templates

Snap templates are located in `/srv/pop/builds/snap/`. They include:

- Snapcraft configuration
- Build scripts
- Snap hooks

To build a snap package:

```bash
cd /srv/pop/builds/snap
./build.sh
```

To customize the snap, edit the snapcraft.yaml:

```bash
vi /srv/pop/builds/snap/snap/snapcraft.yaml
```

## Client Configuration

### Configuring Ubuntu Clients

To configure an Ubuntu client to use your PoP mirror:

1. Create a sources.list.d entry:
   ```bash
   cat > /etc/apt/sources.list.d/pop.list << 'EOF'
   deb http://your-server-hostname/esm-infra/ jammy main
   deb http://your-server-hostname/esm-apps/ jammy main
   # Add other repositories as needed
   EOF
   ```

2. Copy authentication files:
   ```bash
   sudo mkdir -p /etc/apt/auth.conf.d
   sudo mkdir -p /etc/apt/trusted.gpg.d
   sudo scp your-server-hostname:/srv/pop/etc/apt/auth.conf.d/91ubuntu-pro /etc/apt/auth.conf.d/
   sudo scp your-server-hostname:/srv/pop/etc/apt/trusted.gpg.d/* /etc/apt/trusted.gpg.d/
   ```

3. Update the package lists:
   ```bash
   sudo apt update
   ```

### Using Pro Client with PoP

To use the Ubuntu Pro client with PoP:

1. Install the Pro client:
   ```bash
   sudo apt install ubuntu-pro-client
   ```

2. Attach to Ubuntu Pro (optional):
   ```bash
   sudo pro attach --skip-auto-attach YOUR_TOKEN
   ```

3. Check available services:
   ```bash
   sudo pro status
   ```

4. Enable services:
   ```bash
   sudo pro enable esm-infra
   sudo pro enable fips
   ```

## Web Server Management

### Apache Configuration

If you enabled Apache during installation, it serves the mirrored repositories at:

```
http://your-server-hostname/esm-infra/
http://your-server-hostname/esm-apps/
# etc.
```

To customize Apache configuration:

```bash
sudo vi /srv/pop/etc/apache2/sites-available/pop.conf
sudo systemctl reload apache2
```

### Nginx Configuration

If you enabled the web UI, Nginx serves it at:

```
http://your-server-hostname/
```

To customize Nginx configuration:

```bash
sudo vi /srv/pop/etc/nginx/sites-available/pop
sudo systemctl reload nginx
```

### SSL/TLS Configuration

If you enabled SSL/TLS, you can access the web UI and repositories securely:

```
https://your-server-hostname/
```

To update SSL certificates:

```bash
sudo pop --token YOUR_TOKEN --tls-cert /path/to/cert.pem --tls-key /path/to/key.pem --reconfigure
```

## System Maintenance

### Backing Up PoP

To back up your PoP configuration:

```bash
sudo tar -czf pop-backup.tar.gz /srv/pop/etc /srv/pop/*.json /srv/pop/*.rc
```

For a full backup including the mirror:

```bash
sudo tar -czf pop-full-backup.tar.gz /srv/pop /var/spool/apt-mirror
```

### Restoring from Backup

To restore PoP configuration from backup:

```bash
sudo tar -xzf pop-backup.tar.gz -C /
```

### Reconfiguring PoP

To reconfigure PoP with a new token:

```bash
sudo pop --token NEW_TOKEN --reconfigure
```

To add new entitlements:

```bash
sudo pop --token YOUR_TOKEN --entitlements infra,apps,fips,NEW_ENTITLEMENT --reconfigure
```

### Upgrading PoP

To upgrade PoP to a new version:

1. Update the code:
   ```bash
   cd /path/to/pop/repo
   git pull
   ```

2. Install the updated version:
   ```bash
   sudo pip install -e .
   ```

3. Reconfigure if needed:
   ```bash
   sudo pop --token YOUR_TOKEN --reconfigure
   ```

## Monitoring and Troubleshooting

### Checking Logs

To check PoP logs:

```bash
cat /srv/pop/pop.log
```

To check apt-mirror logs:

```bash
cat /var/spool/apt-mirror/var/cron.log
```

To check web server logs:

```bash
# Nginx logs
cat /var/log/nginx/error.log
cat /var/log/nginx/access.log

# Apache logs
cat /var/log/apache2/error.log
cat /var/log/apache2/access.log
```

### Common Issues

#### Mirror Not Updating

**Symptom:** Repository content is not updating

**Solution:**
1. Check apt-mirror is working:
   ```bash
   sudo apt-mirror
   ```
2. Verify cron is running:
   ```bash
   sudo systemctl status cron
   ```
3. Check mirror list:
   ```bash
   cat /srv/pop/etc/mirror.list
   ```

#### Web UI Not Accessible

**Symptom:** Cannot access the web UI

**Solution:**
1. Check Nginx is running:
   ```bash
   sudo systemctl status nginx
   ```
2. Verify configuration:
   ```bash
   sudo nginx -t
   ```
3. Check firewall settings:
   ```bash
   sudo ufw status
   ```

#### Client Cannot Connect

**Symptom:** Client systems cannot connect to the mirror

**Solution:**
1. Verify network connectivity:
   ```bash
   ping your-server-hostname
   ```
2. Check authentication files:
   ```bash
   sudo ls -la /etc/apt/auth.conf.d/
   sudo ls -la /etc/apt/trusted.gpg.d/
   ```
3. Test repository access:
   ```bash
   curl -I http://your-server-hostname/esm-infra/ubuntu/dists/jammy/Release
   ```

### Diagnostics

Run diagnostics to check system health:

```bash
# Check disk space
df -h

# Check services
sudo systemctl status apache2 nginx apt-mirror.timer cron

# Check repository structure
find /var/spool/apt-mirror/mirror -maxdepth 3 -type d | sort

# Check configuration files
find /srv/pop/etc -type f | xargs ls -la
```

## Advanced Usage

### Custom Repository Configuration

To add custom repositories to your PoP mirror:

1. Edit the mirror list:
   ```bash
   sudo vi /srv/pop/etc/mirror.list
   ```

2. Add repository entries:
   ```
   deb http://custom-repo-url/ubuntu jammy main
   ```

3. Update mirror:
   ```bash
   sudo apt-mirror
   ```

### Multi-architecture Support

To add support for additional architectures:

```bash
sudo pop --token YOUR_TOKEN --arch amd64,arm64,s390x --reconfigure
```

### FIPS Compliance

For FIPS-compliant deployments:

1. Ensure FIPS entitlements are enabled:
   ```bash
   sudo pop --token YOUR_TOKEN --entitlements infra,fips,fips-updates --reconfigure
   ```

2. Use the VM templates with FIPS mode enabled:
   ```bash
   cp /srv/pop/builds/vm/grub.cfg /etc/default/grub.d/99-fips.cfg
   update-grub
   ```

3. Install FIPS packages:
   ```bash
   sudo apt install ubuntu-fips
   ```

### Customizing the Web UI

To customize the web UI:

1. Edit the CSS:
   ```bash
   sudo vi /srv/pop/www/css/style.css
   ```

2. Edit the HTML:
   ```bash
   sudo vi /srv/pop/www/index.html
   ```

3. Reload Nginx:
   ```bash
   sudo systemctl reload nginx
   ```

## Getting Help

If you encounter issues that cannot be resolved through this guide:

1. Check the documentation in the `docs/` directory
2. Check the PoP issue tracker on GitHub
3. Contact your Canonical representative
