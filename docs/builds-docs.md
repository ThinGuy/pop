# Build Modules

This document explains the build template modules in the PoP system.

## Overview

The build modules generate templates for various deployment targets, including:

- Virtual machines (VMs)
- Containers (Docker)
- Snap packages

These templates provide pre-configured files needed to build systems with Ubuntu Pro integration in air-gapped environments.

## Modules

### `manager.py`

The `manager.py` module orchestrates build template creation across different formats.

#### Key Functions

- `create_build_templates(paths, resources, release, architectures, build_types)`: Creates templates for specified build types
- `validate_build_templates(paths, build_types)`: Validates existing build templates
- `list_available_templates(paths)`: Lists available templates in the builds directory

### `vm.py`

The `vm.py` module generates templates for virtual machines.

#### Key Functions

- `create_vm_template(builds_dir, paths, release, architectures)`: Creates VM build templates
- `create_fips_startup_script(vm_dir, release)`: Creates a script to enable FIPS mode
- `validate_vm_template(vm_dir)`: Validates VM template files

#### VM Templates

VM templates include:

- Cloud-init configuration for Ubuntu Pro integration
- GRUB configuration with FIPS mode enabled
- APT repository configuration
- Authentication files for Ubuntu Pro repositories
- GPG keys for repository validation

### `container.py`

The `container.py` module generates templates for containers (Docker).

#### Key Functions

- `create_container_template(builds_dir, paths, release, architectures)`: Creates container build templates
- `create_multiarch_dockerfile(container_dir, release, architectures)`: Creates multi-architecture Dockerfile
- `validate_container_template(container_dir)`: Validates container template files

#### Container Templates

Container templates include:

- Dockerfile for building Ubuntu Pro containers
- Docker Compose configuration
- Build scripts for single and multi-architecture builds
- APT repository configuration
- Authentication files for Ubuntu Pro repositories
- GPG keys for repository validation

### `snap.py`

The `snap.py` module generates templates for snap packages.

#### Key Functions

- `create_snap_template(builds_dir, paths, release, architectures)`: Creates snap package build templates
- `create_multiarch_snap_config(snap_dir, architectures)`: Creates multi-architecture snap configuration
- `validate_snap_template(snap_dir)`: Validates snap template files

#### Snap Templates

Snap templates include:

- Snapcraft.yaml configuration for snap packaging
- Build scripts for single and multi-architecture builds
- Snap hooks for lifecycle management (pre-refresh, post-refresh)
- APT repository configuration
- Authentication files for Ubuntu Pro repositories
- GPG keys for repository validation

## Usage Examples

### Creating Build Templates

```python
from pop.config.args import parse_arguments
from pop.config.paths import setup_paths
from pop.core.contracts import pull_contract_data
from pop.core.resources import generate_resource_tokens
from pop.builds.manager import create_build_templates

# Parse arguments
args = parse_arguments()
paths = setup_paths(args)

# Get contract data and resources
contract_data = pull_contract_data(args.token, paths)
resources = generate_resource_tokens(args.token, paths)

# Create build templates
build_results = create_build_templates(
    paths, resources, args.release, args.architectures, ["vm", "container", "snap"]
)

# Check results
for build_type, result in build_results["results"].items():
    print(f"{build_type}: {result['status']}")
```

### Validating Templates

```python
from pop.builds.manager import validate_build_templates

# Validate templates
validation_results = validate_build_templates(paths, ["vm", "container", "snap"])

for build_type, is_valid in validation_results.items():
    print(f"{build_type}: {'Valid' if is_valid else 'Invalid'}")
```

### Building from Templates

Each template directory contains a build.sh script that can be used to build the system:

```bash
# Building a container
cd /srv/pop/builds/container
./build.sh

# Building a snap package
cd /srv/pop/builds/snap
./build.sh

# Building a multi-architecture container
cd /srv/pop/builds/container
./build-multiarch.sh
```

## Directory Structure

```
/srv/pop/builds/
├── README.md                    # Top-level README
├── vm/                          # VM templates
│   ├── cloud-init.yaml         # Cloud-init configuration
│   ├── grub.cfg                # GRUB configuration with FIPS mode
│   ├── README.md               # VM-specific instructions
│   └── etc/                    # APT configuration
├── container/                   # Container templates
│   ├── Dockerfile              # Dockerfile for Ubuntu Pro
│   ├── docker-compose.yml      # Docker Compose configuration
│   ├── build.sh                # Build script
│   ├── README.md               # Container-specific instructions
│   └── etc/                    # APT configuration
└── snap/                        # Snap templates
    ├── snap/                   # Snap configuration directory
    │   ├── snapcraft.yaml      # Snapcraft configuration
    │   └── hooks/              # Snap lifecycle hooks
    ├── build.sh                # Build script
    ├── README.md               # Snap-specific instructions
    └── etc/                    # APT configuration
```
