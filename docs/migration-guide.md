# Migration Guide

This document guides you through migrating from the monolithic PoP script to the modular structure.

## Why Migrate?

The modular structure offers several advantages over the monolithic script:

- **Improved maintainability**: Each module has a single responsibility
- **Better testability**: Modules can be tested in isolation
- **Easier collaboration**: Multiple developers can work on different modules
- **Enhanced extensibility**: New features can be added without modifying existing code
- **Documentation**: Better organization of code and documentation

## Migration Process

### Automated Migration

The easiest way to migrate is to use the provided migration script:

1. Clone the repository (if you haven't already):
   ```bash
   git clone https://github.com/ThinGuy/pop.git
   cd pop
   ```

2. Run the migration script:
   ```bash
   python scripts/migrate.py
   ```

3. The script will:
   - Back up the original script
   - Create the modular structure
   - Create a compatibility wrapper
   - Install the package in development mode

### Manual Migration

If you prefer to migrate manually:

1. Back up the original script:
   ```bash
   cp pop.py pop.py.bak
   ```

2. Create the modular structure:
   ```bash
   mkdir -p pop/{config,core,mirror,web,services,builds,utils}/
   touch pop/__init__.py
   touch pop/{config,core,mirror,web,services,builds,utils}/__init__.py
   ```

3. Set up package installation:
   ```bash
   # Create setup.py
   cat > setup.py << 'EOF'
   from setuptools import setup, find_packages
   setup(
       name="pop-appliance",
       version="5.0.0",
       description="Ubuntu Pro on Premises",
       packages=find_packages(),
       install_requires=["requests", "pyyaml"],
       entry_points={"console_scripts": ["pop=pop.main:main"]},
   )
   EOF
   ```

4. Create a compatibility wrapper:
   ```bash
   # Replace pop.py with wrapper
   cat > pop.py << 'EOF'
   #!/usr/bin/env python3
   from pop.main import main
   if __name__ == "__main__":
       main()
   EOF
   chmod +x pop.py
   ```

5. Install in development mode:
   ```bash
   pip install -e .
   ```

6. Copy module implementations from the repository or create your own.

## Testing the Migration

### Verify the Compatibility Wrapper

Run the compatibility wrapper with `--help` to verify it works:

```bash
./pop.py --help
```

You should see the same help output as before.

### Test Basic Functionality

Test basic functionality with a minimal command:

```bash
sudo ./pop.py --token YOUR_TOKEN --dir /tmp/pop_test --verbose
```

### Run with Previous Settings

If you've previously run PoP, you can use the same settings:

```bash
source /srv/pop/pop.rc  # Adjust path if needed
sudo ./pop.py --token $POP_TOKEN --dir $POP_DIR --reconfigure
```

## Troubleshooting Migration

### ImportError or ModuleNotFoundError

**Symptom**: Error importing modules when running the compatibility wrapper.

**Solution**:
```bash
# Verify package installation
pip list | grep pop-appliance
# Install package if needed
pip install -e .
```

### Permission Issues

**Symptom**: Permission errors when running the script.

**Solution**:
```bash
# Make the wrapper executable
chmod +x pop.py
# Run with sudo
sudo ./pop.py [options]
```

### Missing Implementations

**Symptom**: AttributeError or ImportError for specific modules.

**Solution**:
```bash
# Check module implementation
ls -la pop/modulename/
# Copy missing implementation from repository
cp /path/to/repo/pop/modulename/filename.py pop/modulename/
```

## Reverting the Migration

If you need to revert to the monolithic script:

```bash
# Restore the original script
cp pop.py.bak pop.py
chmod +x pop.py
```

## Development with the Modular Structure

### Running Individual Modules

You can test individual modules:

```python
# Example: Test the mirror estimator
# File: test_estimator.py
from pop.config.args import parse_arguments
from pop.config.paths import setup_paths
from pop.core.contracts import pull_contract_data
from pop.core.resources import generate_resource_tokens
from pop.mirror.estimator import estimate_mirror_size

# Parse minimal arguments
args = parse_arguments(['--token', 'YOUR_TOKEN', '--dir', '/tmp/pop_test'])
paths = setup_paths(args)
contract_data = pull_contract_data(args.token, paths)
resources = generate_resource_tokens(args.token, paths)

# Estimate mirror size
size_info = estimate_mirror_size(
    paths, resources, args.release, args.architectures, args.entitlements
)
print(f"Estimated size: {size_info['readable']}")
```

### Adding New Features

To add a new feature:

1. Identify the appropriate module
2. Implement the feature in that module
3. Update the main module to use the new feature
4. Add tests for the new feature
5. Update documentation

For example, to add a new repository type:

```python
# Add to mirror/repository.py
def add_custom_repository(paths, repo_url, repo_key):
    """Add a custom repository to mirror list"""
    # Implementation...

# Update main.py to use the new function
if args.custom_repo:
    add_custom_repository(paths, args.custom_repo_url, args.custom_repo_key)
```

### Creating Tests

Create tests for new features:

```python
# File: tests/test_repository.py
import unittest
from unittest.mock import patch, MagicMock
from pop.mirror.repository import add_custom_repository

class TestRepository(unittest.TestCase):
    def test_add_custom_repository(self):
        # Setup
        paths = {"pop_apt_mirror_list": "/tmp/mirror.list"}
        repo_url = "http://example.com/repo"
        repo_key = "ABCDEF1234"
        
        # Mock file operations
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            # Call the function
            result = add_custom_repository(paths, repo_url, repo_key)
            
            # Assertions
            self.assertTrue(result)
            mock_file.assert_called_with("/tmp/mirror.list", 'a')
            handle = mock_file()
            handle.write.assert_called()

if __name__ == '__main__':
    unittest.main()
```

## Continuous Integration

Set up CI to ensure code quality:

```yaml
# File: .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov
        pip install -e .
    - name: Test with pytest
      run: |
        pytest tests/ --cov=pop
```

## Documentation

Keep documentation updated as you develop:

```bash
# Generate documentation
mkdir -p docs
# Update module documentation
vim docs/MODULE_NAME.md
```

Remember to update the main README.md with any significant changes.
