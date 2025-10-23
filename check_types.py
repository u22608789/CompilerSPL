#!/usr/bin/env python3
"""
Utility script to run the SPL type checker on a source file.

Usage:
    python check_types.py <file.spl>

Example:
    python check_types.py examples/rich.spl
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from spl.parser import Parser
from spl.type_checker import TypeChecker


def main():
    if len(sys.argv) != 2:
        print("Usage: python check_types.py <file.spl>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)
    
    # Read source file
    with open(filepath, 'r') as f:
        source = f.read()
    
    print(f"Type checking: {filepath}")
    print("=" * 60)
    
    try:
        # Parse the program
        parser = Parser(source)
        ast = parser.parse()
        print("✓ Parsing successful\n")
        
        # Type check the program
        checker = TypeChecker()
        is_correct = checker.check_program(ast)
        
        print()
        checker.print_errors()
        
        # Exit with appropriate code
        sys.exit(0 if is_correct else 1)
        
    except SyntaxError as e:
        print(f"✗ Syntax Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()