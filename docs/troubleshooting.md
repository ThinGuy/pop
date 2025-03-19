# Troubleshooting Guide

This document provides guidance for troubleshooting common issues with the PoP system.

## Common Issues

### Installation Issues

#### Issue: Missing Dependencies

**Symptoms:**
- Error messages about missing packages
- ImportError when running PoP

**Solution:**
1. Ensure all dependencies are installed:
   ```bash
   sudo apt-get update
   sudo apt-get install wget curl vim gawk apt-mirror apache2 nginx jq postgresql postgresql-contrib
   sudo snap install yq --stable
   sudo snap install snap-proxy-server
   ```

2. Make sure the PPA for air-gapped packages is added:
   ```bash
   sudo add-apt-repository -y -u ppa:yellow/ua-airgapped
   ```

#### Issue: Permission Denied

**Symptoms:**
- "Permission denied" errors
- Unable to create or access directories

**Solution:**
1. Ensure the script is run with sudo:
   ```bash
   sudo ./pop.py [options]
   ```

2. Check directory permissions:
   ```bash
   sudo chown -R $(whoami):$(whoami) /srv/pop
   sudo chmod -R 755 /srv/pop
   ```

### Contract and Token Issues

#### Issue: Invalid Token

**Symptoms:**
- "Failed to pull contract data" error
- Error message about unauthorized access

**Solution:**
1. Verify the token is correct:
   ```bash
   sudo pro token | grep "Contract token"
   ```

2. Try regenerating the token:
   ```bash
   sudo pro detach
   sudo pro attach [your-token]
   ```

#### Issue: Missing Entitlements

**Symptoms:**
- Warning about missing entitlements
- Error when creating mirror list

**Solution:**
1. Check available entitlements:
   ```bash
   sudo pro status --format json | jq '.services'
   ```

2. Ensure you're requesting entitlements that are in your contract:
   ```bash
   sudo ./pop.py --token YOUR_TOKEN --entitlements infra,apps
   ```

### Mirror Issues

#### Issue: Mirror Download Fails

**Symptoms:**
- apt-mirror exits with an error
- "Failed to run apt-mirror" message

**Solution:**
1. Check network connectivity:
   ```bash
   ping esm.ubuntu.com
   ```

2. Verify the mirror list:
   ```bash
   cat /srv/pop/etc/mirror.list
   ```

3. Run apt-mirror manually with verbose output:
   ```bash
   sudo apt-mirror -v /srv/pop/etc/mirror.list
   ```

#### Issue: Insufficient Disk Space

**Symptoms:**
- apt-mirror fails with "No space left on device"
- Incomplete mirror

**Solution:**
1. Check available disk space:
   ```bash
   df -h
   ```

2. Run the cleanup script to free space:
   ```bash
   sudo /var/spool/apt-mirror/var/clean.sh
   ```

3. Consider using a different drive with more space:
   ```bash
   sudo ./pop.py --dir /path/to/larger/drive/pop
   ```

### Web UI Issues

#### Issue: Web UI Not Accessible

**Symptoms:**
- Unable to access web UI at http://your-server-ip/
- "Connection refused" error

**Solution:**
1. Check if Nginx is running:
   ```bash
   sudo systemctl status nginx
   ```

2. Verify the Nginx configuration:
   ```bash
   sudo nginx -t
   ```

3. Ensure the configuration is linked correctly:
   ```bash
   ls -l /etc/nginx/sites-enabled/
   ```

4. If using Apache instead:
   ```bash
   sudo systemctl status apache2
   sudo apache2ctl -t
   ```

### TLS Certificate Issues

#### Issue: SSL Certificate Errors

**Symptoms:**
- Browser warnings about invalid certificate
- "SSL handshake failed" errors

**Solution:**
1. Check certificate validity:
   ```bash
   sudo openssl x509 -in /srv/pop/etc/ssl/pop-cert.pem -text -noout
   ```

2. Verify key permissions:
   ```bash
   sudo ls -l /srv/pop/etc/ssl/pop-key.pem
   # Should be -rw------- (0600)
   ```

3. Regenerate self-signed certificate:
   ```bash
   sudo openssl genrsa -out /srv/pop/etc/ssl/pop-key.pem 2048
   sudo openssl req -new -x509 -key /srv/pop/etc/ssl/pop-key.pem -out /srv/pop/etc/ssl/pop-cert.pem -days 3650 -subj "/CN=your-server-name"
   sudo chmod 600 /srv/pop/etc/ssl/pop-key.pem
   sudo chmod 644 /srv/pop/etc/ssl/pop-cert.pem
   ```

### Service Issues

#### Issue: Snap Proxy Not Working

**Symptoms:**
- Unable to download snaps
- Errors about unable to connect to snap store

**Solution:**
1. Check snap proxy status:
   ```bash
   sudo systemctl status snap-proxy
   ```

2. Restart snap proxy:
   ```bash
   sudo systemctl restart snap-proxy
   ```

3. Verify snap client configuration:
   ```bash
   snap get system proxy
   ```

## Debugging Techniques

### Enabling Verbose Logging

Run PoP with the `--verbose` flag to get detailed logging:

```bash
sudo ./pop.py --token YOUR_TOKEN --verbose
```

### Checking Log Files

Check various log files for more information:

```bash
# PoP log
cat /srv/pop/pop.log

# apt-mirror log
cat /var/spool/apt-mirror/var/cron.log

# Nginx error log
cat /var/log/nginx/error.log

# Apache error log
cat /var/log/apache2/error.log
```

### Run Components Individually

You can test individual components of the system:

```python
# Example script to test mirror list creation
from pop.config.args import parse_arguments
from pop.config.paths import setup_paths
from pop.core.contracts import pull_contract_data
from pop.core.resources import generate_resource_tokens
from pop.mirror.repository import create_mirror_list

# Parse arguments
args = parse_arguments()
paths = setup_paths(args)
contract_data = pull_contract_data(args.token, paths)
resources = generate_resource_tokens(args.token, paths)

# Create mirror list
create_mirror_list(
    paths, resources, args.release, args.architectures, 
    args.entitlements, args.mirror_host
)
```

## Restoring from Backup

If you need to restore from a backup:

1. Restore the RC file:
   ```bash
   sudo cp /srv/pop/pop.rc.bak /srv/pop/pop.rc
   ```

2. Restore the original script (if using monolithic version):
   ```bash
   sudo cp pop.py.bak pop.py
   ```

3. Reconfigure with existing settings:
   ```bash
   source /srv/pop/pop.rc
   sudo ./pop.py --token $POP_TOKEN --dir $POP_DIR --reconfigure
   ```

## Getting Help

If you're unable to resolve an issue, gather the following information before seeking help:

1. PoP version:
   ```bash
   ./pop.py --version
   ```

2. System information:
   ```bash
   lsb_release -a
   uname -a
   ```

3. Log files (with sensitive information redacted):
   ```bash
   sudo cat /srv/pop/pop.log
   ```

4. Configuration files (with sensitive information redacted):
   ```bash
   sudo cat /srv/pop/pop.rc
   sudo cat /srv/pop/etc/mirror.list
   ```
