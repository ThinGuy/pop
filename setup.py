#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="pop-appliance",
    version="5.0.0",
    description="Ubuntu Pro on Premises (PoP) Configuration",
    author="ThinGuy",
    author_email="your.email@example.com",
    url="https://github.com/ThinGuy/pop",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "pop=pop.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.6",
)
