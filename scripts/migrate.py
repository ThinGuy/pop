#!/usr/bin/env python3
"""
Migration script for transitioning from monolithic PoP to modular structure.

This script helps with the migration from the original pop.py script to the new
modular structure. It will:

1. Create a backup of the original script
2. Set up the modular structure
3. Create a compatibility wrapper
4. Install the package in development mode
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Migrate from monolithic pop.py to modular structure"
    )
    
    parser.add_argument(
        "--original", default="pop.py",
        help="Path to original pop.py script (default: pop.py)"
    )
    
    parser.add_argument(
        "--backup", action="store_true",
        help="Create a backup of the original script"
    )
    
    parser.add_argument(
        "--no-install", action="store_true",
        help="Skip installation of the package"
    )
    
    parser.add_argument(
        "--virtualenv", action="store_true",
        help="Create and use a virtual environment"
    )
    
    return parser.parse_args()


def backup_original(original_path, backup=True):
    """Create a backup of the original script"""
    print(f"Checking original script: {original_path}")
    
    if not os.path.exists(original_path):
        print(f"Error: Original script not found at {original_path}")
        return False
    
    if backup:
        backup_path = f"{original_path}.bak"
        print(f"Creating backup: {backup_path}")
        shutil.copy2(original_path, backup_path)
    
    return True


def setup_modular_structure():
    """Set up the modular directory structure"""
    print("Setting up modular directory structure...")
    
    # Create main structure using the create_structure.py script
    structure_script = "scripts/create_structure.py"
    
    if os.path.exists(structure_script):
        subprocess.run([sys.executable, structure_script], check=True)
    else:
        print(f"Error: Structure creation script not found at {structure_script}")
        print("You'll need to create the directory structure manually.")
    
    return True


def create_compatibility_wrapper(original_path):
    """Create compatibility wrapper script"""
    print(f"Creating compatibility wrapper at {original_path}...")
    
    wrapper_content = """#!/usr/bin/env python3
# Ubuntu Pro on Premises (PoP) - Compatibility Wrapper
# Revision: 5.0.0
#
# This is a compatibility wrapper for the new modular structure.
# It preserves backward compatibility with existing command-line usage
# while using the new modular code structure.

import sys
from pop.main import main

if __name__ == "__main__":
    # Simply pass control to the main module
    main()
"""
    
    with open(original_path, 'w') as f:
        f.write(wrapper_content)
    
    # Make the script executable
    os.chmod(original_path, 0o755)
    
    return True


def install_package(use_virtualenv=False):
    """Install the package in development mode"""
    print("Installing package in development mode...")
    
    if use_virtualenv:
        print("Creating virtual environment...")
        if not os.path.exists("venv"):
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        
        # Determine activation script based on platform
        if sys.platform.startswith('win'):
            activate_script = os.path.join("venv", "Scripts", "activate")
        else:
            activate_script = os.path.join("venv", "bin", "activate")
        
        # Create installation script
        with open("install_dev.sh", 'w') as f:
            f.write(f"""#!/bin/bash
source {activate_script}
pip install -e .
""")
        
        os.chmod("install_dev.sh", 0o755)
        print("Created installation script: install_dev.sh")
        print("Run this script to complete installation")
    else:
        # Direct installation
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)
            print("Package installed successfully")
        except subprocess.CalledProcessError:
            print("Warning: Failed to install package. You may need to run with sudo or use --virtualenv")
    
    return True


def main():
    """Main function"""
    args = parse_args()
    
    # Ensure we're in the repository root
    repo_root = Path(__file__).resolve().parent.parent
    os.chdir(repo_root)
    
    # Backup original script
    if not backup_original(args.original, args.backup):
        return 1
    
    # Set up modular structure
    if not setup_modular_structure():
        return 1
    
    # Create compatibility wrapper
    if not create_compatibility_wrapper(args.original):
        return 1
    
    # Install package
    if not args.no_install:
        if not install_package(args.virtualenv):
            return 1
    
    print("\nMigration completed successfully!")
    print("\nNext steps:")
    print("1. Implement the remaining modules as needed")
    print("2. Test the compatibility wrapper")
    print("3. Update documentation to reflect the new structure")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
