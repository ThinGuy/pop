# Service Modules

This document explains the service management modules in the PoP system.

## Overview

The service modules handle various system services required for PoP operation, including:

- TLS certificate management
- Cron job configuration for regular updates
- Snap proxy server configuration

These modules ensure that the PoP system has all necessary services properly configured and running.

## Modules

### `tls.py`

The `tls.py` module handles TLS certificate management.

#### Key Functions

- `configure_tls_certificates(paths, tls_cert, tls_key)`: Configures TLS certificates for the mirror server
- `verify_tls_certificates(paths)`: Verifies TLS certificates installed in the system
- `generate_self_signed_certificate(paths, common_name)`: Generates a self-signed TLS certificate

#### TLS Configuration Features

The TLS configuration includes:

- Certificate and key installation
- Permission management for security
- Server configuration updates (Nginx)
- Support for custom certificates or self-signed certificates

### `cron.py`

The `cron.py` module manages cron jobs for regular updates.

#### Key Functions

- `setup_cron_for_mirror(paths, schedule)`: Configures cron job for regular mirror updates
- `verify_cron_job(paths)`: Verifies that cron job is installed and active
- `update_cron_schedule(paths, schedule)`: Updates the schedule of the mirror update cron job
- `get_last_run_time()`: Gets the time of the last cron job run

#### Cron Configuration Features

The cron configuration includes:

- Scheduled mirror updates (default: every 12 hours)
- Log file for update history
- System integration through `/etc/cron.d/`
- Status monitoring capabilities

### `snap_proxy.py`

The `snap_proxy.py` module configures the snap proxy server for offline snap package management.

#### Key Functions

- `configure_snap_proxy(paths, token)`: Configures snap-proxy-server for offline use
- `check_snap_proxy_status()`: Checks the status of snap proxy server
- `configure_snap_client(mirror_host, port)`: Configures snap client to use proxy
- `unconfigure_snap_client()`: Removes snap proxy configuration
- `update_snap_proxy_token(token)`: Updates the token for snap proxy

#### Snap Proxy Features

The snap proxy configuration includes:

- Database initialization for snap package storage
- Systemd service creation for reliable operation
- Client configuration for snap consumers
- Token management for authentication

## Usage Examples

### Configuring TLS Certificates

```python
from pop.services.tls import configure_tls_certificates, generate_self_signed_certificate

# Generate self-signed certificate
generate_self_signed_certificate(paths, "pop.example.com")

# Or use custom certificates
cert_path = "/path/to/certificate.pem"
key_path = "/path/to/key.pem"
configure_tls_certificates(paths, cert_path, key_path)
```

### Setting Up Cron Jobs

```python
from pop.services.cron import setup_cron_for_mirror

# Set up cron job with default schedule (every 12 hours)
setup_cron_for_mirror(paths)

# Or with custom schedule
setup_cron_for_mirror(paths, "0 */6 * * *")  # Every 6 hours
```

### Configuring Snap Proxy

```python
from pop.services.snap_proxy import configure_snap_proxy, configure_snap_client

# Configure snap proxy server
configure_snap_proxy(paths, token)

# Configure client to use the proxy
configure_snap_client("pop.example.com", 8000)
```

## Service Management

### TLS Certificate Management

TLS certificates are essential for secure communication. The `tls.py` module provides:

1. **Custom Certificate Support**: Use your own certificates
2. **Self-Signed Certificate Generation**: For testing or internal use
3. **Verification Tools**: Ensure certificates are properly installed
4. **Integration with Web Servers**: Automatically configures servers to use TLS

#### Certificate Paths

Certificates are stored in the TLS directory:

```
/srv/pop/etc/ssl/
├── pop-cert.pem       # Certificate file
└── pop-key.pem        # Private key file
```

### Cron Job Management

Regular updates are critical for keeping the mirror synchronized. The `cron.py` module provides:

1. **Scheduled Updates**: Configure when updates occur
2. **Logging**: Track update history
3. **Status Monitoring**: Check when the last update ran
4. **System Integration**: Uses standard cron mechanisms

#### Cron Configuration

The cron job is configured in the system's cron.d directory:

```
# /etc/cron.d/pop-mirror
0 */12 * * * apt-mirror /usr/bin/apt-mirror > /var/spool/apt-mirror/var/cron.log
```

### Snap Proxy Management

For environments that need snap packages, a snap proxy is essential. The `snap_proxy.py` module provides:

1. **Proxy Server Setup**: Configure the snap-proxy-server
2. **Client Configuration**: Set up systems to use the proxy
3. **Token Management**: Keep authentication up to date
4. **Service Management**: Ensure the proxy runs reliably

#### Snap Proxy Service

The snap proxy runs as a systemd service:

```
# /etc/systemd/system/snap-proxy.service
[Unit]
Description=Snap Proxy Server
After=network.target postgresql.service

[Service]
Type=simple
ExecStart=/snap/bin/snap-proxy-server
Restart=on-failure
WorkingDirectory=/srv/pop/snap-proxy

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

### TLS Certificate Issues

- Check certificate validity: `openssl x509 -in /srv/pop/etc/ssl/pop-cert.pem -text -noout`
- Verify key permissions: Should be 0600 (read/write for owner only)
- Check server configuration for proper certificate paths

### Cron Job Issues

- Verify cron service is running: `systemctl status cron`
- Check log file: `/var/spool/apt-mirror/var/cron.log`
- Manually run: `/usr/bin/apt-mirror`

### Snap Proxy Issues

- Check service status: `systemctl status snap-proxy`
- Verify database initialization: `snap-proxy status`
- Test connectivity: `curl http://localhost:8000/v2/snaps`
