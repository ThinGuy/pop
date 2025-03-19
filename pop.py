#!/usr/bin/env python3
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
