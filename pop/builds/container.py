"""
Container build template management for Ubuntu Pro on Premises (PoP)
"""

import os
import logging
import shutil
import datetime
from typing import Dict, List, Any


def create_container_template(builds_dir: str, paths: Dict[str, str], 
                            release: str, architectures: List[str]) -> Dict[str, Any]:
    """
    Create container build templates
    
    Args:
        builds_dir: Directory to store build files
        paths: Dictionary of system paths
        release: Ubuntu release codename (e.g., 'jammy')
        architectures: List of architectures to support
        
    Returns:
        Dictionary with build information
    """
    logging.info("Creating container build templates")
    
    container_dir = os.path.join(builds_dir, "container")
    os.makedirs(container_dir, exist_ok=True)
    
    # Files to copy from the repository
    files = [
        {"src": paths["pop_apt_mirror_list"], "dst": "etc/apt/sources.list.d/pop.list"},
        {"src": paths["pop_apt_auth_file"], "dst": "etc/apt/auth.conf.d/91ubuntu-pro"},
        {"src": paths["pop_gpg_dir"], "dst": "etc/apt/trusted.gpg.d/"},
    ]
    
    # Create subdirectories for file structure
    for file_info in files:
        dst_path = os.path.join(container_dir, file_info["dst"])
        dst_dir = os.path.dirname(dst_path)
        os.makedirs(dst_dir, exist_ok=True)
    
    # Copy files
    for file_info in files:
        src_path = file_info["src"]
        dst_path = os.path.join(container_dir, file_info["dst"])
        
        if os.path.isdir(src_path):
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)
            
        logging.debug(f"Copied {src_path} to {dst_path}")
    
    # Create Dockerfile template
    dockerfile_path = os.path.join(container_dir, "Dockerfile")
    with open(dockerfile_path, 'w') as f:
        f.write(f"""# Dockerfile for Ubuntu Pro container with PoP integration
# Generated: {datetime.datetime.now().isoformat()}
# For Ubuntu {release.capitalize()}

FROM ubuntu:{release}

# Add PoP repository files
COPY etc/apt/sources.list.d/pop.list /etc/apt/sources.list.d/
COPY etc/apt/auth.conf.d/91ubuntu-pro /etc/apt/auth.conf.d/
COPY etc/apt/trusted.gpg.d/ /etc/apt/trusted.gpg.d/

# Install Ubuntu Pro client
RUN apt-get update && \\
    apt-get install -y ubuntu-pro-client && \\
    apt-get clean

# Your application setup here
# ...

# Runtime configuration
CMD ["/bin/bash"]
""")
    
    # Create docker-compose.yml template
    compose_path = os.path.join(container_dir, "docker-compose.yml")
    with open(compose_path, 'w') as f:
        f.write(f"""# Docker Compose for Ubuntu Pro container with PoP integration
# Generated: {datetime.datetime.now().isoformat()}
# For Ubuntu {release.capitalize()}

version: '3'

services:
  app:
    build: .
    container_name: pop-{release}
    volumes:
      - ./data:/data
    environment:
      - TZ=UTC
    restart: unless-stopped
""")
    
    # Create build script
    build_script_path = os.path.join(container_dir, "build.sh")
    with open(build_script_path, 'w') as f:
        f.write(f"""#!/bin/bash
# Build script for Ubuntu Pro container
# Generated: {datetime.datetime.now().isoformat()}
# For Ubuntu {release.capitalize()}

set -e

# Build the container image
docker build -t pop-ubuntu:{release} .

echo "Container image built successfully: pop-ubuntu:{release}"
echo "To run the container: docker run -it pop-ubuntu:{release}"
""")
    
    # Make the build script executable
    os.chmod(build_script_path, 0o755)
    
    # Create README.md with instructions
    readme_path = os.path.join(container_dir, "README.md")
    with open(readme_path, 'w') as f:
        f.write(f"""# PoP Container Build Files

This directory contains files needed to build a container with Ubuntu Pro on Premises (PoP) integration.

## Contents

- Configuration files for apt repositories
- Authentication files for Ubuntu Pro repositories
- GPG keys for repository validation
- Dockerfile for container build
- Docker Compose configuration
- Build script

## Usage

1. Copy these files to your container build environment
2. Run the build script:
   ```bash
   ./build.sh
   ```
3. Or build manually:
   ```bash
   docker build -t pop-ubuntu:{release} .
   ```
4. Run the container:
   ```bash
   docker run -it pop-ubuntu:{release}
   ```

## Customization

Modify the Dockerfile to include your application and dependencies:

```dockerfile
# After the Ubuntu Pro client installation
RUN apt-get update && \\
    apt-get install -y your-package1 your-package2 && \\
    apt-get clean

# Add your application files
COPY app/ /app/

# Set working directory
WORKDIR /app

# Expose ports if needed
EXPOSE 8080

# Command to run your application
CMD ["./your-application"]
```

## Notes

- These files were generated for Ubuntu {release.capitalize()}
- Configured for architectures: {', '.join(architectures)}
- Generated on {datetime.datetime.now().strftime('%Y-%m-%d')}

For more information, see the PoP documentation.
""")
    
    return {
        "dir": container_dir,
        "files": [
            dockerfile_path,
            compose_path,
            build_script_path,
            readme_path
        ],
        "status": "success"
    }


def validate_container_template(container_dir: str) -> bool:
    """
    Validate container template files
    
    Args:
        container_dir: Container template directory
        
    Returns:
        True if valid, False otherwise
    """
    # Required files
    required_files = [
        "Dockerfile",
        "docker-compose.yml",
        "build.sh",
        "README.md",
        "etc/apt/sources.list.d/pop.list",
        "etc/apt/auth.conf.d/91ubuntu-pro"
    ]
    
    # Check if all required files exist
    for file_path in required_files:
        full_path = os.path.join(container_dir, file_path)
        if not os.path.exists(full_path):
            logging.warning(f"Missing required file: {file_path}")
            return False
    
    # Check if GPG keys directory is not empty
    gpg_dir = os.path.join(container_dir, "etc/apt/trusted.gpg.d")
    if not os.path.exists(gpg_dir) or not os.listdir(gpg_dir):
        logging.warning("GPG keys directory is empty or missing")
        return False
    
    return True


def create_multiarch_dockerfile(container_dir: str, release: str, architectures: List[str]) -> str:
    """
    Create a multi-architecture Dockerfile
    
    Args:
        container_dir: Container template directory
        release: Ubuntu release codename
        architectures: List of architectures
        
    Returns:
        Path to created Dockerfile
    """
    multiarch_path = os.path.join(container_dir, "Dockerfile.multiarch")
    
    # Only include supported architectures for containers
    supported_container_archs = [arch for arch in architectures 
                              if arch in ["amd64", "arm64", "ppc64el", "s390x"]]
    
    if not supported_container_archs:
        # Default to amd64 if no supported architectures
        supported_container_archs = ["amd64"]
    
    with open(multiarch_path, 'w') as f:
        f.write(f"""# Multi-architecture Dockerfile for Ubuntu Pro container with PoP integration
# Generated: {datetime.datetime.now().isoformat()}
# For Ubuntu {release.capitalize()} on {', '.join(supported_container_archs)}

# Use buildx and platform-specific base images
FROM --platform=$TARGETPLATFORM ubuntu:{release}

# Add PoP repository files
COPY etc/apt/sources.list.d/pop.list /etc/apt/sources.list.d/
COPY etc/apt/auth.conf.d/91ubuntu-pro /etc/apt/auth.conf.d/
COPY etc/apt/trusted.gpg.d/ /etc/apt/trusted.gpg.d/

# Install Ubuntu Pro client
RUN apt-get update && \\
    apt-get install -y ubuntu-pro-client && \\
    apt-get clean

# Your application setup here
# ...

# Runtime configuration
CMD ["/bin/bash"]
""")
    
    # Create build script for multi-arch
    script_path = os.path.join(container_dir, "build-multiarch.sh")
    with open(script_path, 'w') as f:
        f.write(f"""#!/bin/bash
# Multi-architecture build script for Ubuntu Pro container
# Generated: {datetime.datetime.now().isoformat()}
# For Ubuntu {release.capitalize()} on {', '.join(supported_container_archs)}

set -e

# Create buildx builder if it doesn't exist
if ! docker buildx inspect pop-builder &>/dev/null; then
  echo "Creating buildx builder instance..."
  docker buildx create --name pop-builder --use
fi

# Build for multiple architectures
docker buildx build --platform={','.join([f'linux/{arch}' for arch in supported_container_archs])} \\
  -t pop-ubuntu:{release} \\
  -f Dockerfile.multiarch \\
  --push \\
  .

echo "Multi-architecture container image built successfully: pop-ubuntu:{release}"
echo "Supported architectures: {', '.join(supported_container_archs)}"
""")
    
    # Make the build script executable
    os.chmod(script_path, 0o755)
    
    return multiarch_path
