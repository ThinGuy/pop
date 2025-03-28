"""
Command-line argument handling for Ubuntu Pro on Premises (PoP)
"""

import argparse
import sys
import logging
import subprocess
from typing import Dict, List

# Define constants
DEFAULT_RELEASE = "jammy"  # Current LTS by default
DEFAULT_ARCHITECTURES = ["amd64"]
DEFAULT_CONTRACT_PORT = 8484
SUPPORTED_ARCHITECTURES = ["amd64", "arm64", "i386", "ppc64el", "s390x", "riscv64"]
SUPPORTED_RELEASES = ["trusty", "xenial", "bionic", "focal", "jammy", "noble"]  # ESM + Active LTS
BUILD_TYPES = ["vm", "container", "snap"]


def get_current_lts() -> str:
    """Get the current LTS release codename"""
    try:
        lts = subprocess.check_output(
            ["ubuntu-distro-info", "-c", "--lts"], 
            text=True
        ).strip()
        return lts.lower()
    except (subprocess.SubprocessError, FileNotFoundError):
        logging.warning(f"Could not determine current LTS, using default: {DEFAULT_RELEASE}")
        return DEFAULT_RELEASE


def get_system_fqdn_or_ip() -> str:
    """Get the system's FQDN or IP address for use as default mirror host"""
    try:
        # First try to get FQDN using hostname -f
        fqdn = subprocess.check_output(["hostname", "-f"], text=True).strip()
        if fqdn and not fqdn.startswith("localhost"):
            return fqdn
    except subprocess.SubprocessError:
        pass
    
    # If FQDN not available, try to get the primary IP address
    try:
        # Get all IP addresses and pick the first non-localhost one
        ip_output = subprocess.check_output(
            ["hostname", "-I"], text=True
        ).strip().split()
        
        for ip in ip_output:
            if not ip.startswith("127."):
                return ip
    except subprocess.SubprocessError:
        pass
    
    # Fallback to localhost if nothing else works
    return "localhost"


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    # Get system FQDN or IP as default for mirror host
    default_mirror_host = get_system_fqdn_or_ip()
    
    parser = argparse.ArgumentParser(
        description="Ubuntu Pro on Premises (PoP) Configuration",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("--token", required=True, 
                        help="Ubuntu Pro contract token")
    
    parser.add_argument("--dir", dest="pop_dir", default="/srv/pop",
                        help="Base directory for PoP installation")
    
    parser.add_argument("--release", choices=SUPPORTED_RELEASES, default=get_current_lts(),
                        help="Ubuntu release to configure")
    
    parser.add_argument("--arch", dest="architectures", 
                        default=",".join(DEFAULT_ARCHITECTURES),
                        help="Comma-separated list of architectures to support")
    
    parser.add_argument("--entitlements",
                        default="infra,apps,fips,fips-updates,fips-preview,cis,usg",
                        help="Comma-separated list of entitlements to mirror")
                        
    parser.add_argument("--include-source", action="store_true",
                        help="Include source packages in the mirror")
    
    parser.add_argument("--offline-repo", dest="offline_repo",
                        default="ppa:yellow/ua-airgapped",
                        help="PPA for air-gapped Pro packages")
    
    parser.add_argument("--create-build-map", action="store_true",
                        help="Create file map for VM, container, and snap builds")
                        
    parser.add_argument("--build-types", 
                        default=",".join(BUILD_TYPES),
                        help=f"Build types to support in file map (comma-separated: {', '.join(BUILD_TYPES)})")
    
    parser.add_argument("--mirror-host", dest="mirror_host",
                        default=default_mirror_host,
                        help="Host FQDN/IP for the local mirror (overrides default URLs)")
    
    parser.add_argument("--mirror-port", dest="mirror_port", type=int, default=80,
                        help="Port for the local mirror server")
    
    parser.add_argument("--contract-port", dest="contract_port", type=int, default=DEFAULT_CONTRACT_PORT,
                        help="Port for the contracts server")
    
    parser.add_argument("--tls-cert", dest="tls_cert",
                        help="Path to custom TLS certificate")
    
    parser.add_argument("--tls-key", dest="tls_key",
                        help="Path to custom TLS key")
    
    parser.add_argument("--estimate-size", action="store_true",
                        help="Estimate mirror size before downloading")
    
    parser.add_argument("--generate-web-ui", action="store_true",
                        help="Generate a web UI for monitoring PoP status")
    
    parser.add_argument("--reconfigure", action="store_true",
                        help="Reconfigure PoP with new contract token without reinstalling")
    
    parser.add_argument("--mirror-standard-repos", action="store_true",
                        help="Mirror standard Ubuntu repositories in addition to Pro repositories")
                        
    parser.add_argument("--mirror-components", 
                        default="main,restricted,universe,multiverse",
                        help="Components to mirror for standard repositories")
                        
    parser.add_argument("--mirror-pockets",
                        default="release,updates,backports,security",
                        help="Pockets to mirror (e.g., release,updates,backports,security)")
                        
    parser.add_argument("--setup-apache", action="store_true",
                        help="Configure Apache to serve mirrored repositories")
                        
    parser.add_argument("--setup-cron", action="store_true",
                        help="Set up cron job for regular mirror updates")
                        
    parser.add_argument("--cron-schedule", default="0 */12 * * *",
                        help="Cron schedule for mirror updates (default: every 12 hours)")
                        
    parser.add_argument("--run-apt-mirror", action="store_true",
                        help="Run apt-mirror to start the initial mirror download")
    
    parser.add_argument("--production", action="store_true",
                        help="Configure services to start at boot for production use")
    
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Process and validate arguments
    args = _process_arguments(args)
    
    return args


def _process_arguments(args: argparse.Namespace) -> argparse.Namespace:
    """Process and validate parsed arguments"""
    # Convert comma-separated values to lists
    args.architectures = args.architectures.split(",")
    args.entitlements = args.entitlements.split(",")
    args.mirror_components = args.mirror_components.split(",")
    args.mirror_pockets = args.mirror_pockets.split(",")
    
    if hasattr(args, 'build_types'):
        args.build_types = args.build_types.split(",")
    
    # Validate architectures
    for arch in args.architectures:
        if arch not in SUPPORTED_ARCHITECTURES and arch != "source":
            logging.error(f"Unsupported architecture: {arch}")
            logging.error(f"Supported architectures: {', '.join(SUPPORTED_ARCHITECTURES)} and 'source'")
            sys.exit(1)
    
    # Add source if requested
    if args.include_source and "source" not in args.architectures:
        args.architectures.append("source")
    
    # Validate build types if creating build map
    if args.create_build_map:
        for build_type in args.build_types:
            if build_type not in BUILD_TYPES:
                logging.error(f"Unsupported build type: {build_type}")
                logging.error(f"Supported build types: {', '.join(BUILD_TYPES)}")
                sys.exit(1)
    
    return args
