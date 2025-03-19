# Core Modules

This document explains the core modules in the PoP system.

## Overview

The core modules provide the essential functionality for PoP, handling:

- Contract data fetching and processing
- Resource token management
- Authentication file creation
- GPG key management

## Modules

### `contracts.py`

The `contracts.py` module handles contract data.

#### Key Functions

- `pull_contract_data(token, paths)`: Fetches contract data using pro-airgapped
- `extract_account_info(contract_data)`: Extracts account information
- `extract_entitlements(contract_data)`: Extracts entitlement information
- `map_entitlement_to_repo_path(entitlement_name)`: Maps API entitlement names to repository paths

#### Contract Data Structure

```json
{
  "token": {
    "contractInfo": {
      "name": "Ubuntu Pro Contract",
      "id": "contract-id",
      "createdAt": "2023-01-01T00:00:00Z",
      "effectiveFrom": "2023-01-01T00:00:00Z",
      "effectiveTo": "2024-01-01T00:00:00Z",
      "resourceEntitlements": [
        {
          "type": "esm-infra",
          "entitled": true,
          "directives": {
            "aptURL": "https://esm.ubuntu.com/infra/ubuntu/",
            "aptKey": "key-id",
            "suites": ["jammy", "jammy-updates"]
          }
        }
      ]
    }
  }
}
```

### `resources.py`

The `resources.py` module manages resource tokens.

#### Key Functions

- `generate_resource_tokens(token, paths)`: Generates resource tokens
- `load_resource_tokens(paths)`: Loads resource tokens from file
- `validate_entitlements(resources, requested_entitlements)`: Validates requested entitlements

#### Resource Token Structure

```json
{
  "esm-infra": "token-value-1",
  "esm-apps": "token-value-2",
  "fips": "token-value-3"
}
```

### `auth.py`

The `auth.py` module handles authentication file creation.

#### Key Functions

- `create_auth_file(paths, resources)`: Creates authentication file for apt
- `verify_auth_file(paths)`: Verifies that authentication file exists and has correct permissions
- `update_auth_file(paths, resources)`: Updates authentication file with new resource tokens

#### Auth File Format

```
machine esm.ubuntu.com/infra/ubuntu/ login bearer password TOKEN_VALUE  # ubuntu-pro-client
machine esm.ubuntu.com/apps/ubuntu/ login bearer password TOKEN_VALUE  # ubuntu-pro-client
```

### `gpg.py`

The `gpg.py` module handles GPG key management.

#### Key Functions

- `download_gpg_keys(paths, contract_data)`: Downloads GPG keys for repositories
- `verify_gpg_keys(paths, entitlements)`: Verifies that GPG keys exist for entitlements
- `add_keyring_to_apt(key_path)`: Adds a keyring to apt's trusted keyrings

## Usage Examples

### Pulling contract data

```python
from pop.core.contracts import pull_contract_data

# Pull contract data
contract_data = pull_contract_data(token, paths)
```

### Generating resource tokens

```python
from pop.core.resources import generate_resource_tokens

# Generate resource tokens
resources = generate_resource_tokens(token, paths)
```

### Creating authentication file

```python
from pop.core.auth import create_auth_file

# Create authentication file
create_auth_file(paths, resources)
```

### Downloading GPG keys

```python
from pop.core.gpg import download_gpg_keys

# Download GPG keys
download_gpg_keys(paths, contract_data)
```
