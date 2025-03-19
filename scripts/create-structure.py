#!/usr/bin/env python3
"""
Create the directory structure for the modular PoP implementation.
"""

import os
import sys

def create_directory_structure():
    """Create the package directory structure"""
    print("Creating directory structure...")
    
    # Main package directory
    os.makedirs("pop", exist_ok=True)
    
    # Module directories
    modules = ["config", "core", "mirror", "web", "services", "builds", "utils"]
    for module in modules:
        os.makedirs(f"pop/{module}", exist_ok=True)
    
    # Template directories
    os.makedirs("pop/templates/web", exist_ok=True)
    os.makedirs("pop/templates/builds", exist_ok=True)
    
    # Create __init__.py files
    with open("pop/__init__.py", "w") as f:
        f.write('"""Ubuntu Pro on Premises (PoP) - Air-gapped solution for Ubuntu Pro services"""\n\n')
        f.write('__version__ = "5.0.0"\n')
    
    for module in modules:
        with open(f"pop/{module}/__init__.py", "w") as f:
            f.write(f'"""{module.capitalize()} module for Ubuntu Pro on Premises (PoP)"""\n')
    
    print("Directory structure created successfully!")

if __name__ == "__main__":
    create_directory_structure()
