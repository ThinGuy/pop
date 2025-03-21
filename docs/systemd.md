# Systemd Services

This document explains how to configure and manage systemd services for PoP in production environments.

## Overview

For production deployments, PoP can configure systemd services to ensure that all required components start automatically at boot time. These services include:

- **Contracts Server**: Serves Ubuntu Pro contract data
- **Web Servers**: Apache and/or Nginx for serving repositories and web UI
- **Mirror Timer**: Automatic periodic updates of the mirror

## Using Systemd Services

### Basic Configuration

To configure systemd services for production, use the `--production` flag when running PoP:

```bash
sudo pop --token YOUR_TOKEN --production
```

This will:

1. Create a systemd service for the contracts server
2. Enable and start Apache and/or Nginx (if configured)
3. Create a systemd timer for periodic mirror updates

### Checking Service Status

After configuration, you can check the status of each service:

```bash
# Check contract server status
sudo systemctl status pop-contracts

# Check Apache status
sudo systemctl status apache2

# Check Nginx status
sudo systemctl status nginx

# Check mirror update timer
sudo systemctl status pop-mirror.timer
```

### Managing Services

You can manage the services using standard systemd commands:

```bash
# Stop a service
sudo systemctl stop pop-contracts

# Start a service
sudo systemctl start pop-contracts

# Restart a service
sudo systemctl restart pop-contracts

# Disable a service (prevent from starting at boot)
sudo systemctl disable pop-contracts

# Enable a service (ensure it starts at boot)
sudo systemctl enable pop-contracts
```

## Service Details

### Contracts Server

The contracts server service (`pop-contracts.service`) is responsible for serving Ubuntu Pro contract data:

- **Service Name**: `pop-contracts`
- **Binary**: `/usr/bin/contracts-airgapped`
- **Default Port**: 8484
- **Behavior**: Starts automatically at boot, restarts on failure

To view logs for the contracts server:

```bash
sudo journalctl -u pop-contracts
```

### Web Servers

PoP can configure both Apache and Nginx to start at boot:

#### Apache

- **Service Name**: `apache2`
- **Configuration**: `/srv/pop/etc/apache2/sites-available/pop.conf`
- **Purpose**: Serves mirrored repositories

#### Nginx

- **Service Name**: `nginx`
- **Configuration**: `/srv/pop/etc/nginx/sites-available/pop`
- **Purpose**: Serves web UI dashboard

### Mirror Update Timer

The mirror update timer (`pop-mirror.timer`) triggers periodic updates of the mirror:

- **Service Name**: `pop-mirror`
- **Timer Name**: `pop-mirror.timer`
- **Default Schedule**: Twice daily at 00:00 and 12:00
- **Behavior**: Runs apt-mirror to synchronize repositories

To view the timer status:

```bash
sudo systemctl list-timers pop-mirror.timer
```

To view logs for mirror updates:

```bash
sudo journalctl -u pop-mirror
```

## Customizing Service Configuration

### Changing Contract Server Port

To use a different port for the contracts server:

```bash
sudo pop --token YOUR_TOKEN --production --contract-port 9000
```

### Changing Mirror Update Schedule

The systemd timer uses a different format than cron jobs. To customize the update schedule, you can edit the timer file:

```bash
sudo vi /etc/systemd/system/pop-mirror.timer
```

And modify the `OnCalendar` line with a systemd time specification:

```
[Timer]
OnCalendar=*-*-* 0,12:00:00
```

After editing, reload the configuration:

```bash
sudo systemctl daemon-reload
sudo systemctl restart pop-mirror.timer
```

## Troubleshooting

### Service Won't Start

If a service fails to start:

1. Check the status for error messages:
   ```bash
   sudo systemctl status pop-contracts
   ```

2. View the journal logs:
   ```bash
   sudo journalctl -u pop-contracts
   ```

3. Verify the service file:
   ```bash
   sudo cat /etc/systemd/system/pop-contracts.service
   ```

### Startup Errors

If services fail to start at boot:

1. Check if the contract service is enabled:
   ```bash
   sudo systemctl is-enabled pop-contracts
   ```

2. Ensure the working directory exists:
   ```bash
   sudo ls -la /srv/pop
   ```

3. Verify the binaries are installed:
   ```bash
   which contracts-airgapped
   ```

### Timer Not Running

If the mirror updates are not happening:

1. Check if the timer is active:
   ```bash
   sudo systemctl list-timers
   ```

2. Verify the timer is enabled:
   ```bash
   sudo systemctl is-enabled pop-mirror.timer
   ```

3. Try triggering the service manually:
   ```bash
   sudo systemctl start pop-mirror
   ```

## Manual Configuration

If you need to configure services manually:

1. Create the contract service file:
   ```bash
   sudo vi /etc/systemd/system/pop-contracts.service
   ```

2. Add the content:
   ```
   [Unit]
   Description=Ubuntu Pro on Premises Contracts Server
   After=network.target
   Wants=network-online.target

   [Service]
   Type=simple
   ExecStart=/usr/bin/contracts-airgapped --listen-port=8484
   WorkingDirectory=/srv/pop
   Restart=on-failure
   RestartSec=5
   StandardOutput=journal
   StandardError=journal

   [Install]
   WantedBy=multi-user.target
   ```

3. Reload systemd and enable the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable pop-contracts
   sudo systemctl start pop-contracts
   ```
