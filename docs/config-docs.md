# Configuration Modules

This document explains the configuration modules in the PoP system.

## Overview

The configuration modules handle all aspects of configuring the PoP application:

- Command-line argument parsing
- Path management
- Configuration file handling

## Modules

### `args.py`

The `args.py` module is responsible for defining and parsing command-line arguments.

#### Key Functions

- `parse_arguments()`: Parses command-line arguments and returns a namespace
- `_process_arguments()`: Validates and processes parsed arguments

#### Supported Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--token` | Ubuntu Pro contract token | (required) |
| `--dir` | Base directory for PoP installation | `/srv/pop` |
| `--release` | Ubuntu release codename | Current LTS |
| `--arch` | Architectures to support | `amd64` |
| `--entitlements` | Entitlements to mirror | `infra,apps,fips,fips-updates,fips-preview,cis,usg` |
| `--include-source` | Include source packages | False |
| `--create-build-map` | Create build templates | False |
| `--mirror-host` | Mirror hostname/IP | System hostname |
| `--estimate-size` | Estimate mirror size | False |
| `--generate-web-ui` | Generate web dashboard | False |
| `--reconfigure` | Reconfigure with new token | False |
| `--run-apt-mirror` | Run apt-mirror | False |
| `--verbose` | Verbose output | False |

For a complete list of arguments, run `pop.py --help`.

### `paths.py`

The `paths.py` module manages system paths and configuration files.

#### Key Functions

- `setup_paths(args)`: Sets up and returns paths based on configuration
- `save_configuration(args, paths)`: Saves configuration to RC file
- `load_configuration(rc_file)`: Loads configuration from RC file

#### Path Structure

The module creates a consistent directory structure with paths like:

```
/srv/pop/
├── etc/
│   ├── apt/
│   │   ├── auth.conf.d/         # APT authentication files
│   │   └── trusted.gpg.d/       # GPG keys
│   ├── mirror.list              # apt-mirror configuration
│   ├── nginx/                   # Nginx configuration
│   └── ssl/                     # TLS certificates
├── debs/                        # Cached packages
├── builds/                      # Build templates
├── www/                         # Web UI files
├── pop.json                     # Contract data
├── pop_resources.json           # Resource tokens
└── pop.rc                       # Runtime configuration
```

## Configuration File Format

The `pop.rc` configuration file uses a simple key-value format:

```
# PoP Configuration - Created 2023-03-15T10:30:45.123456
POP_TOKEN=<token>
POP_DIR=/srv/pop
POP_RELEASE=jammy
POP_ARCHITECTURES=amd64,arm64
POP_ENTITLEMENTS=infra,apps,fips
POP_GPG_DIR=/srv/pop/etc/apt/trusted.gpg.d
# Additional configuration...
```

## Usage Examples

### Creating paths

```python
from pop.config.args import parse_arguments
from pop.config.paths import setup_paths

# Parse arguments
args = parse_arguments()

# Set up paths
paths = setup_paths(args)
```

### Saving configuration

```python
from pop.config.paths import save_configuration

# Save configuration
save_configuration(args, paths)
```

### Loading configuration

```python
from pop.config.paths import load_configuration

# Load configuration
config = load_configuration("/srv/pop/pop.rc")
```
