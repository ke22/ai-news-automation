#!/usr/bin/env python
"""
Simple runner script for AI news automation
Usage: python run.py [collect|process|publish|analyze]
"""

import sys
import os
import subprocess


def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py [collect|process|publish|analyze]")
        sys.exit(1)

    script_name = sys.argv[1]
    script_map = {
        "collect": "scripts/collect.py",
        "process": "scripts/process.py",
        "publish": "scripts/publish.py",
        "analyze": "scripts/analyze.py",
    }

    if script_name not in script_map:
        print(f"Unknown script: {script_name}")
        print("Available scripts:", list(script_map.keys()))
        sys.exit(1)

    script_path = script_map[script_name]

    # Execute the script using subprocess
    result = subprocess.run([sys.executable, script_path], cwd=os.getcwd())
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
