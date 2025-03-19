# Mirror Modules

This document explains the mirror management modules in the PoP system.

## Overview

The mirror modules handle repository configuration and synchronization, including:

- Repository configuration
- Mirror size estimation
- Mirror synchronization

## Modules

### `repository.py`

The `repository.py` module configures repositories for mirroring.

#### Key Functions

- `create_mirror_list(paths, resources, release, architectures, entitlements, ...)`: Creates mirror list with embedded credentials
- `verify_mirror_list(paths)`: Verifies that mirror list exists and is valid

#### Mirror List Format

```
############# config ##################
#
# Created by PoP Configuration Script
# 2023-03-15T10:30:45.123456
#
set base_path    /var/spool/apt-mirror
set mirror_path  $base_path/mirror
set skel_path    $base_path/skel
set var_path     $base_path/var
set defaultarch  amd64
set run_postmirror 0
set nthreads     20
set _tilde 0
set auth_no_challenge 1
#
############# end config ##############

deb [arch=amd64,arm64] https://bearer:TOKEN@esm.ubuntu.com/infra/ubuntu/ jammy main

deb-src https://bearer:TOKEN@esm.ubuntu.com/infra/ubuntu/ jammy main

clean https://esm.ubuntu.com/infra/ubuntu/
```

### `estimator.py`

The `estimator.py` module estimates mirror size.

#### Key Functions

- `estimate_mirror_size(paths, resources, release, architectures, entitlements_list)`: Estimates the size of the mirror
- `get_mirror_disk_usage(mirror_path)`: Gets disk usage statistics for the mirror

#### Size Estimation Output

```json
{
  "bytes": 10737418240,
  "readable": "10.00 GB",
  "packages": 5000,
  "included_repos": [
    "deb [arch=amd64] https://esm.ubuntu.com/infra/ubuntu/ jammy main",
    "deb-src https://esm.ubuntu.com/infra/ubuntu/ jammy main"
  ]
}
```

### `sync.py`

The `sync.py` module handles mirror synchronization.

#### Key Functions

- `run_apt_mirror(paths)`: Runs apt-mirror to start the initial mirror download
- `verify_mirror(paths)`: Verifies mirror structure and gets statistics
- `run_mirror_cleanup(paths)`: Runs apt-mirror cleanup script to free space

#### Mirror Structure

```
/var/spool/apt-mirror/
├── mirror/
│   ├── esm.ubuntu.com/
│   │   ├── infra/
│   │   │   └── ubuntu/
│   │   ├── apps/
│   │   │   └── ubuntu/
│   │   └── ...
│   └── archive.ubuntu.com/
│       └── ubuntu/
├── skel/
└── var/
    ├── clean.sh
    └── cron.log
```

## Usage Examples

### Creating mirror list

```python
from pop.mirror.repository import create_mirror_list

# Create mirror list
create_mirror_list(
    paths, resources, "jammy", ["amd64", "arm64"], 
    ["infra", "apps"], mirror_host="localhost"
)
```

### Estimating mirror size

```python
from pop.mirror.estimator import estimate_mirror_size

# Estimate mirror size
size_info = estimate_mirror_size(
    paths, resources, "jammy", ["amd64"], ["infra", "apps"]
)

print(f"Estimated size: {size_info['readable']}")
print(f"Packages: {size_info['packages']}")
```

### Running apt-mirror

```python
from pop.mirror.sync import run_apt_mirror

# Run apt-mirror
result = run_apt_mirror(paths)

if result:
    print("Mirror synchronization successful")
else:
    print("Mirror synchronization failed")
```
