"""
apt-mirror configuration for Ubuntu Pro on Premises (PoP)
"""

import os
import re
import logging
import subprocess
import datetime
from typing import Dict, List, Any, Optional

from pop.utils.system import run_command


def configure_apt_mirror(paths: Dict[str, str]) -> bool:
    """
    Configure apt-mirror for use with PoP
    
    Args:
        paths: Dictionary of system paths
        
    Returns:
        True if successful, False otherwise
    """
    logging.info("Configuring apt-mirror for PoP")
    
    try:
        # Create mirror directories if they don't exist
        mirror_dirs = [
            "/var/spool/apt-mirror/mirror",
            "/var/spool/apt-mirror/skel",
            "/var/spool/apt-mirror/var"
        ]
        
        for directory in mirror_dirs:
            os.makedirs(directory, exist_ok=True)
        
        # Set correct permissions
        run_command(["chown", "-R", "apt-mirror:apt-mirror", "/var/spool/apt-mirror"])
        
        # Create symlink to mirror list if it doesn't exist
        apt_mirror_conf = "/etc/apt/mirror.list"
        if not os.path.exists(apt_mirror_conf) or not os.path.islink(apt_mirror_conf):
            # Remove existing file if it exists
            if os.path.exists(apt_mirror_conf):
                os.remove(apt_mirror_conf)
            # Create symlink
            os.symlink(paths["pop_apt_mirror_list"], apt_mirror_conf)
        
        logging.info("apt-mirror configured successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to configure apt-mirror: {e}")
        return False


def run_apt_mirror_command(mirror_list_path: Optional[str] = None, 
                         verbose: bool = False) -> Dict[str, Any]:
    """
    Run apt-mirror command
    
    Args:
        mirror_list_path: Path to mirror list file (default: use system default)
        verbose: Enable verbose output
        
    Returns:
        Dictionary with execution results
    """
    logging.info("Running apt-mirror")
    
    command = ["apt-mirror"]
    if verbose:
        command.append("-v")
    if mirror_list_path:
        command.append(mirror_list_path)
    
    result = {
        "success": False,
        "download_size": "0",
        "download_count": 0,
        "cleanup_size": "0",
        "cleanup_files": 0,
        "cleanup_dirs": 0,
        "output": "",
        "error": ""
    }
    
    try:
        # Run apt-mirror
        process = subprocess.run(
            command, 
            capture_output=True,
            text=True
        )
        
        result["output"] = process.stdout
        result["error"] = process.stderr
        result["success"] = process.returncode == 0
        
        if not result["success"]:
            logging.error(f"apt-mirror failed with exit code {process.returncode}")
            logging.error(result["error"])
            return result
        
        # Parse output for statistics
        output = process.stdout
        
        # Look for download size
        size_match = re.search(r'([0-9.]+) ([KMG]iB) will be downloaded into archive', output)
        if size_match:
            size = f"{size_match.group(1)} {size_match.group(2)}"
            result["download_size"] = size
            logging.info(f"Downloaded {size} of packages")
        
        # Look for download count
        count_match = re.search(r'([0-9,]+) packages', output)
        if count_match:
            count = count_match.group(1).replace(',', '')
            result["download_count"] = int(count)
        
        # Look for cleanup info
        cleanup_match = re.search(r'([0-9.]+) ([KMG]iB)? in ([0-9,]+) files and ([0-9,]+) directories can be freed', output)
        if cleanup_match:
            cleanup_size = f"{cleanup_match.group(1)} {cleanup_match.group(2) or 'bytes'}"
            cleanup_files = cleanup_match.group(3).replace(',', '')
            cleanup_dirs = cleanup_match.group(4).replace(',', '')
            
            result["cleanup_size"] = cleanup_size
            result["cleanup_files"] = int(cleanup_files)
            result["cleanup_dirs"] = int(cleanup_dirs)
            
            logging.info(f"{cleanup_size} in {cleanup_files} files and {cleanup_dirs} directories can be freed")
            logging.info("Run /var/spool/apt-mirror/var/clean.sh to free space")
        
        logging.info("apt-mirror completed successfully")
        return result
    except Exception as e:
        logging.error(f"Failed to run apt-mirror: {e}")
        result["error"] = str(e)
        return result


def run_apt_mirror_cleanup() -> bool:
    """
    Run apt-mirror cleanup script
    
    Returns:
        True if successful, False otherwise
    """
    logging.info("Running apt-mirror cleanup")
    
    cleanup_script = "/var/spool/apt-mirror/var/clean.sh"
    if not os.path.exists(cleanup_script):
        logging.warning(f"Cleanup script not found: {cleanup_script}")
        return False
    
    try:
        result = run_command([cleanup_script], capture_output=True)
        logging.info("Cleanup completed successfully")
        logging.debug(result)
        return True
    except Exception as e:
        logging.error(f"Failed to run cleanup: {e}")
        return False


def get_mirror_stats() -> Dict[str, Any]:
    """
    Get statistics about the mirror
    
    Returns:
        Dictionary with mirror statistics
    """
    logging.info("Getting mirror statistics")
    
    mirror_path = "/var/spool/apt-mirror/mirror"
    stats = {
        "status": "Not available",
        "last_update": "Never",
        "total_size": "0 B",
        "total_size_bytes": 0,
        "total_files": 0,
        "total_dirs": 0,
        "repositories": []
    }
    
    if not os.path.exists(mirror_path):
        logging.warning(f"Mirror directory does not exist: {mirror_path}")
        return stats
    
    try:
        # Get last update time
        last_update = datetime.datetime.fromtimestamp(
            os.path.getmtime(mirror_path)
        ).strftime("%Y-%m-%d %H:%M:%S")
        stats["last_update"] = last_update
        
        # Get total size
        du_result = subprocess.check_output(
            ["du", "-sb", mirror_path], 
            text=True
        ).strip().split()[0]
        
        total_size_bytes = int(du_result)
        stats["total_size_bytes"] = total_size_bytes
        
        # Make human readable
        if total_size_bytes < 1024:
            stats["total_size"] = f"{total_size_bytes} B"
        elif total_size_bytes < 1024*1024:
            stats["total_size"] = f"{total_size_bytes/1024:.2f} KB"
        elif total_size_bytes < 1024*1024*1024:
            stats["total_size"] = f"{total_size_bytes/1024/1024:.2f} MB"
        else:
            stats["total_size"] = f"{total_size_bytes/1024/1024/1024:.2f} GB"
        
        # Count files and directories
        file_count = int(subprocess.check_output(
            ["find", mirror_path, "-type", "f", "-not", "-path", "*/\.*", "|", "wc", "-l"],
            shell=True,
            text=True
        ).strip())
        stats["total_files"] = file_count
        
        dir_count = int(subprocess.check_output(
            ["find", mirror_path, "-type", "d", "-not", "-path", "*/\.*", "|", "wc", "-l"],
            shell=True,
            text=True
        ).strip())
        stats["total_dirs"] = dir_count
        
        # Get repositories
        repos = []
        for root, dirs, files in os.walk(mirror_path, topdown=True):
            # Limit depth - only get top-level directories
            if root.count(os.sep) - mirror_path.count(os.sep) > 1:
                continue
                
            for dirname in dirs:
                if dirname not in ["dists", "pool"]:  # Skip common repo subdirs
                    repo_path = os.path.join(root, dirname)
                    repos.append({
                        "name": dirname,
                        "path": repo_path.replace(mirror_path + "/", ""),
                    })
                    
        stats["repositories"] = repos
        stats["status"] = "Available"
        
        return stats
    except Exception as e:
        logging.error(f"Failed to get mirror statistics: {e}")
        return stats


def verify_mirror_contents(mirror_list_path: str) -> Dict[str, Any]:
    """
    Verify mirror contents against mirror list
    
    Args:
        mirror_list_path: Path to mirror list file
        
    Returns:
        Dictionary with verification results
    """
    logging.info("Verifying mirror contents")
    
    result = {
        "verified": False,
        "missing_repos": [],
        "total_repos": 0,
        "available_repos": 0
    }
    
    try:
        # Read mirror list
        with open(mirror_list_path, 'r') as f:
            mirror_list = f.read()
        
        # Extract repository URLs
        repo_lines = []
        for line in mirror_list.splitlines():
            if line.startswith("deb ") or line.startswith("deb-src "):
                repo_lines.append(line)
        
        result["total_repos"] = len(repo_lines)
        
        # Get mirror stats
        stats = get_mirror_stats()
        
        # Check if each repository exists
        for repo_line in repo_lines:
            parts = repo_line.split()
            if len(parts) >= 3:
                repo_url = parts[1]
                
                # Extract domain and path
                if "://" in repo_url:
                    domain = repo_url.split("://")[1].split("/")[0]
                    path = "/".join(repo_url.split("://")[1].split("/")[1:])
                else:
                    domain = repo_url.split("/")[0]
                    path = "/".join(repo_url.split("/")[1:])
                
                # Check if repository exists in mirror
                repo_exists = False
                for repo in stats["repositories"]:
                    if domain in repo["path"]:
                        repo_exists = True
                        break
                
                if not repo_exists:
                    result["missing_repos"].append(repo_url)
                else:
                    result["available_repos"] += 1
        
        result["verified"] = result["available_repos"] == result["total_repos"]
        
        return result
    except Exception as e:
        logging.error(f"Failed to verify mirror contents: {e}")
        result["error"] = str(e)
        return result
