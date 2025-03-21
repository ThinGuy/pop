#!/usr/bin/env python3
# Ubuntu Pro on Premises (PoP) - Main Entry Point
# Revision: 5.0.0

import os
import sys
import logging
import datetime

# Import modules
from pop.config.args import parse_arguments
from pop.config.paths import setup_paths, save_configuration
from pop.utils.system import check_sudo, create_directories
from pop.utils.logger import setup_logging
from pop.utils.package import install_prerequisites, download_pro_packages
from pop.core.contracts import pull_contract_data
from pop.core.resources import generate_resource_tokens
from pop.core.auth import create_auth_file
from pop.core.gpg import download_gpg_keys
from pop.mirror.estimator import estimate_mirror_size
from pop.mirror.repository import create_mirror_list
from pop.mirror.sync import run_apt_mirror
from pop.web.apache import setup_apache_for_mirror
from pop.web.dashboard import generate_web_ui
from pop.web.nginx import configure_nginx
from pop.services.cron import setup_cron_for_mirror
from pop.services.tls import configure_tls_certificates
from pop.services.snap_proxy import configure_snap_proxy
from pop.services.systemd import configure_production_services
from pop.builds.manager import create_build_templates


def display_banner():
    """Display welcome banner"""
    banner = """
    ┌───────────────────────────────────────────────┐
    │ Ubuntu Pro on Premises (PoP) Setup            │
    └───────────────────────────────────────────────┘
    """
    print(banner)


def display_completion_message(args, paths, is_reconfiguring, size_info=None, apt_mirror_result=None):
    """Display completion message"""
    mode = "Reconfiguration" if is_reconfiguring else "Configuration"
    
    completion_message = f"""
    ┌───────────────────────────────────────────────┐
    │ PoP {mode.lower()} complete!                       │
    │                                               │
    │ Configuration: {paths['pop_rc_file']}
    │ Mirror List:   {paths['pop_apt_mirror_list']}
    │ Auth File:     {paths['pop_apt_auth_file']}
    """
    
    if hasattr(args, 'create_build_map') and args.create_build_map:
        completion_message += f"""│                                               │
    │ Build files:   {paths['pop_builds_dir']}
    """
    
    if hasattr(args, 'generate_web_ui') and args.generate_web_ui and not is_reconfiguring:
        completion_message += f"""│                                               │
    │ Web UI:        http://{args.mirror_host}/
    """
    
    if hasattr(args, 'configure_snap_proxy') and args.configure_snap_proxy and not is_reconfiguring:
        completion_message += f"""│                                               │
    │ Snap Proxy:    http://{args.mirror_host}:8000/
    """
    
    if size_info:
        completion_message += f"""│                                               │
    │ Estimated Size: {size_info['readable']} ({size_info['packages']:,} packages)
    """
    
    if hasattr(args, 'setup_apache') and args.setup_apache:
        completion_message += f"""│                                               │
    │ Repository URL: http://{args.mirror_host}/
    """
    
    if hasattr(args, 'production') and args.production:
        completion_message += f"""│                                               │
    │ Services:      Configured to start at boot
    │ Contracts:     systemctl status pop-contracts
    │ Mirror Updates: systemctl status pop-mirror.timer
    """
    
    if apt_mirror_result is not None:
        status = "successful" if apt_mirror_result else "failed"
        completion_message += f"""│                                               │
    │ Initial mirror: {status}
    """
    
    next_steps = "Run apt-mirror to update packages" if is_reconfiguring else "Run apt-mirror to download packages"
    if hasattr(args, 'run_apt_mirror') and args.run_apt_mirror:
        next_steps = "Repository mirroring completed"
    
    completion_message += f"""│                                               │
    │ Next Steps:                                   │
    │ 1. {next_steps}        │
    │ 2. Configure clients to use this repository   │
    └───────────────────────────────────────────────┘
    """
    
    print(completion_message)


def main():
    """Main execution flow"""
    display_banner()
    
    # Check for sudo privileges
    check_sudo()
    
    # Parse arguments
    args = parse_arguments()
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Set up paths
    paths = setup_paths(args)
    
    # Display configuration information
    logging.info(f"Setting up PoP with token: {args.token[:5]}...{args.token[-5:]}")
    logging.info(f"Target release: {args.release}")
    logging.info(f"Target architectures: {', '.join(args.architectures)}")
    logging.info(f"Target entitlements: {', '.join(args.entitlements)}")
    logging.info(f"Using mirror host: {args.mirror_host}")
    
    # Check if reconfiguring
    is_reconfiguring = args.reconfigure if hasattr(args, 'reconfigure') else False
    if is_reconfiguring:
        if not os.path.exists(paths["pop_dir"]):
            logging.error(f"Cannot reconfigure: {paths['pop_dir']} does not exist")
            sys.exit(1)
        logging.info("Reconfiguring PoP with new contract token")
    
    # Create directories if needed
    if not is_reconfiguring:
        create_directories(paths)
        
    # Install prerequisites if not reconfiguring
    if not is_reconfiguring:
        install_prerequisites(args.offline_repo)
        download_pro_packages(paths)
    
    # Always pull new contract data
    contract_data = pull_contract_data(args.token, paths)
    resources = generate_resource_tokens(args.token, paths)
    create_auth_file(paths, resources)
    download_gpg_keys(paths, contract_data)
    
    # Estimate mirror size if requested
    size_info = None
    if hasattr(args, 'estimate_size') and args.estimate_size:
        size_info = estimate_mirror_size(paths, resources, args.release, 
                                        args.architectures, args.entitlements)
        print("\nMirror Size Estimate:")
        print(f"  Total size:      {size_info['readable']}")
        print(f"  Total packages:  {size_info['packages']:,}")
        print("\nRepositories to be mirrored:")
        for repo in size_info['included_repos']:
            print(f"  {repo}")
        print("\nContinue with mirror setup? (y/n)")
        response = input().strip().lower()
        if response != 'y':
            print("Setup aborted by user.")
            sys.exit(0)
    
    # Create mirror list with mirror host if specified
    mirror_components = args.mirror_components if hasattr(args, 'mirror_components') else None
    mirror_pockets = args.mirror_pockets if hasattr(args, 'mirror_pockets') else None
    mirror_standard_repos = args.mirror_standard_repos if hasattr(args, 'mirror_standard_repos') else False
    
    create_mirror_list(
        paths, resources, args.release, args.architectures, args.entitlements, 
        args.mirror_host, args.mirror_port, mirror_standard_repos, 
        mirror_components, mirror_pockets
    )
    
    # Configure snap-proxy if requested and not reconfiguring
    if hasattr(args, 'configure_snap_proxy') and args.configure_snap_proxy and not is_reconfiguring:
        configure_snap_proxy(paths, args.token)
    
    # Configure TLS if certificates provided
    if hasattr(args, 'tls_cert') and args.tls_cert and hasattr(args, 'tls_key') and args.tls_key:
        configure_tls_certificates(paths, args.tls_cert, args.tls_key)
    
    # Configure Apache if requested
    if hasattr(args, 'setup_apache') and args.setup_apache:
        setup_apache_for_mirror(paths, args.mirror_host)
    
    # Configure Nginx if web UI is requested
    if hasattr(args, 'generate_web_ui') and args.generate_web_ui:
        configure_nginx(paths, args.mirror_host)
    
    # Configure cron job if requested
    if hasattr(args, 'setup_cron') and args.setup_cron:
        cron_schedule = args.cron_schedule if hasattr(args, 'cron_schedule') else "0 */12 * * *"
        setup_cron_for_mirror(paths, cron_schedule)
    
    # Save configuration
    save_configuration(args, paths)
    
    # Create build map if requested
    if hasattr(args, 'create_build_map') and args.create_build_map:
        build_types = args.build_types if hasattr(args, 'build_types') else ["vm", "container", "snap"]
        create_build_templates(paths, resources, args.release, args.architectures, build_types)
    
    # Generate web UI if requested and not reconfiguring
    if hasattr(args, 'generate_web_ui') and args.generate_web_ui and not is_reconfiguring:
        generate_web_ui(paths, resources, contract_data, args.release, args.architectures)
    
    # Configure production services if requested
    if hasattr(args, 'production') and args.production:
        # Determine which servers to enable
        server_types = []
        if hasattr(args, 'setup_apache') and args.setup_apache:
            server_types.append("apache")
        if hasattr(args, 'generate_web_ui') and args.generate_web_ui:
            server_types.append("nginx")
            
        # Get contract port if specified
        contract_port = args.contract_port if hasattr(args, 'contract_port') else 8484
        
        # Configure services
        configure_production_services(paths, contract_port, server_types)
    
    # Run apt-mirror if requested
    apt_mirror_result = None
    if hasattr(args, 'run_apt_mirror') and args.run_apt_mirror:
        apt_mirror_result = run_apt_mirror(paths)
    
    # Display completion message
    display_completion_message(args, paths, is_reconfiguring, size_info, apt_mirror_result)


if __name__ == "__main__":
    main()
