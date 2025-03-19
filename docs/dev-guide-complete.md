# Development Guide

This document provides guidance for developers working on the PoP system.

## Development Environment Setup

### Prerequisites

- Python 3.8 or newer
- Git
- Ubuntu 20.04 LTS or newer (recommended)
- Python development tools

### Setup Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/ThinGuy/pop.git
   cd pop
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   # Or with development dependencies
   pip install -e '.[dev]'
   ```

4. Set up pre-commit hooks (optional):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Project Structure

The project follows a modular structure:

```
pop/
├── __init__.py              # Package initialization
├── main.py                  # Main entry point and CLI handling
├── config/                  # Configuration management
├── core/                    # Core functionality
├── mirror/                  # Mirror management
├── web/                     # Web UI and servers
├── builds/                  # Build templates
├── services/                # Service management
└── utils/                   # Utilities
```

Each module has a specific responsibility and interacts with other modules in well-defined ways.

## Coding Standards

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use 4 spaces for indentation (no tabs)
- Maximum line length of 88 characters (compatible with Black formatter)
- Use proper docstrings in Google or NumPy style for all modules, classes, and functions

### Type Annotations

Use type annotations for function parameters and return values:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Example function with type annotations.
    
    Args:
        param1: String parameter
        param2: Integer parameter
        
    Returns:
        Boolean result
    """
    return param2 > len(param1)
```

### Error Handling

- Use try/except blocks for error handling
- Log errors with appropriate level
- Provide meaningful error messages
- Catch specific exceptions rather than generic ones

Example:

```python
try:
    result = run_command(["apt-mirror", paths["pop_apt_mirror_list"]])
    logging.info("apt-mirror completed successfully")
except subprocess.CalledProcessError as e:
    logging.error(f"apt-mirror failed with exit code {e.returncode}")
    logging.error(f"Error output: {e.stderr}")
    return False
except Exception as e:
    logging.error(f"Unexpected error running apt-mirror: {e}")
    return False
```

## Logging

Use the logging module for all output:

- `logging.debug()`: Detailed debugging information
- `logging.info()`: General information
- `logging.warning()`: Warning messages
- `logging.error()`: Error messages

Do not use `print()` statements in production code.

Example:

```python
import logging

logging.debug("Processing repository: %s", repo_name)
logging.info("Found %d packages in repository", package_count)
logging.warning("Repository %s has no packages", empty_repo)
logging.error("Failed to download repository: %s", failed_repo)
```

## Testing

### Unit Tests

Write unit tests for all modules using the Python `unittest` framework or `pytest`.

Example test:

```python
# tests/test_system.py
import unittest
from unittest.mock import patch
from pop.utils.system import get_current_lts

class TestSystem(unittest.TestCase):
    @patch("pop.utils.system.subprocess.check_output")
    def test_get_current_lts(self, mock_check_output):
        mock_check_output.return_value = "jammy\n"
        self.assertEqual(get_current_lts(), "jammy")
        
        mock_check_output.side_effect = subprocess.SubprocessError()
        self.assertEqual(get_current_lts(), "jammy")  # Default value

if __name__ == "__main__":
    unittest.main()
```

### Running Tests

Run tests using pytest:

```bash
# Run all tests
python -m pytest

# Run tests with coverage report
python -m pytest --cov=pop tests/

# Run tests for a specific module
python -m pytest tests/test_system.py
```

## Documentation

### Docstrings

Use docstrings for all modules, classes, and functions. Follow Google or NumPy style:

```python
def function_with_types_in_docstring(param1, param2):
    """Example function with types documented in the docstring.
    
    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.
    
    Returns:
        bool: The return value. True for success, False otherwise.
    """
    return param1 < len(param2)
```

### Documentation Files

Update markdown documentation files when making changes to the code:

- `README.md`: Main project documentation
- `docs/*.md`: Module-specific documentation

## Git Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make your changes with clear, atomic commits:
   ```bash
   git add .
   git commit -m "Add X feature"
   ```

3. Push your branch:
   ```bash
   git push origin feature/my-feature
   ```

4. Create a pull request against the main branch

## Adding New Features

### Adding a New Module

1. Create the module file in the appropriate directory
2. Add an import in the package's `__init__.py`
3. Update the main module to use the new functionality
4. Add tests for the new module
5. Update documentation

Example for adding a new mirror module:

```python
# pop/mirror/cleanup.py
"""
Mirror cleanup functionality for Ubuntu Pro on Premises (PoP)
"""

def cleanup_mirror(paths):
    """
    Clean up old packages from the mirror
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        True if successful, False otherwise
    """
    # Implementation...
```

Update `pop/mirror/__init__.py`:

```python
"""Mirror management for Ubuntu Pro on Premises (PoP)"""

from pop.mirror.cleanup import cleanup_mirror
```

### Adding a New Command-Line Option

1. Add the option to `parse_arguments()` in `config/args.py`
2. Update the argument processing logic if needed
3. Update the main module to handle the new option
4. Add tests for the new option
5. Update documentation

Example for adding a cleanup option:

```python
# In config/args.py
parser.add_argument("--cleanup-mirror", action="store_true",
                   help="Clean up old packages from the mirror")

# In main.py
if args.cleanup_mirror:
    from pop.mirror.cleanup import cleanup_mirror
    cleanup_mirror(paths)
```

## Building for Distribution

### Source Distribution

Create a source distribution:

```bash
python setup.py sdist
```

### Wheel Distribution

Create a wheel distribution:

```bash
python setup.py bdist_wheel
```

## Releasing

1. Update version number in:
   - `pop/__init__.py`
   - `setup.py`
   - Any other version references

2. Update the changelog

3. Create a release tag:
   ```bash
   git tag -a v5.0.0 -m "Version 5.0.0"
   git push origin v5.0.0
   ```

## Debugging Tips

### Enabling Verbose Logging

Run with the `--verbose` flag:

```bash
./pop.py --verbose [other options]
```

### Debugging Individual Modules

You can debug individual modules by creating a simple test script:

```python
# debug_mirror.py
from pop.config.args import parse_arguments
from pop.config.paths import setup_paths
from pop.mirror.repository import create_mirror_list

# Parse minimal arguments
args = parse_arguments(['--token', 'YOUR_TOKEN', '--verbose'])
paths = setup_paths(args)

# Test function
create_mirror_list(
    paths, {'infra': 'token123'}, 'jammy', ['amd64'], ['infra']
)
```

Run with:

```bash
python -m debug_mirror
```

### Using the Python Debugger

Insert a breakpoint in your code:

```python
import pdb

def some_function():
    # ... code ...
    pdb.set_trace()  # Debugger will stop here
    # ... more code ...
```

Or use Python 3.7+ breakpoint():

```python
def some_function():
    # ... code ...
    breakpoint()  # Debugger will stop here
    # ... more code ...
```

## Performance Profiling

Use the `cProfile` module to profile performance:

```python
import cProfile

cProfile.run('some_function()', 'profile_output')
```

Analyze the results:

```bash
python -m pstats profile_output
```

## Contributing Guidelines

1. **Code Quality**: Ensure your code passes all tests and linting
2. **Documentation**: Update documentation for any changes
3. **Tests**: Add tests for new functionality
4. **Commit Messages**: Use clear, descriptive commit messages
5. **Pull Requests**: Keep PRs focused on a single issue or feature
6. **Review**: Address review comments promptly

## Common Development Tasks

### Adding a New Dependency

1. Add the dependency to `setup.py`:
   ```python
   install_requires=[
       "requests",
       "pyyaml",
       "new-dependency",
   ],
   ```

2. Update the development environment:
   ```bash
   pip install -e .
   ```

### Updating Documentation

1. Update the relevant markdown files in `docs/`
2. Test documentation build if using tools like mkdocs:
   ```bash
   mkdocs build
   mkdocs serve
   ```

### Creating a New Release

1. Update version numbers
2. Update CHANGELOG.md
3. Create distribution packages
4. Tag the release in git
5. Push to repository

## Troubleshooting Development Issues

### Import Errors

If you see import errors during development:

1. Verify your virtual environment is activated
2. Ensure the package is installed in development mode
3. Check for typos in import statements
4. Verify module names and paths

### Permission Issues

For functions that require root privileges:

1. Run the script with sudo during testing
2. Make sure file permissions are correct
3. Use appropriate error handling for permission errors

### Dependencies

If you encounter missing dependencies:

1. Install missing packages: `apt-get install <package>`
2. Update Python dependencies: `pip install -r requirements.txt`
3. Check for conflicting package versions
