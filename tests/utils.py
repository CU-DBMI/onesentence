"""
Utilities for testing.
"""

import subprocess
import sys
import os
from typing import Tuple

def run_cli_command(command: str) -> Tuple[str, str, int]:
    """
    Run a CLI command using subprocess and capture the output and return code.

    Args:
        command (list): The command to run as a list of strings.

    Returns:
        tuple: (str: stdout, str: stderr, int: returncode)
    """

    # Resolve CLI entry points relative to the active Python interpreter so
    # tests work inside a venv without the scripts directory on PATH.
    # Only resolve if the script exists in the venv bin; fall back to PATH otherwise.
    venv_bin = os.path.dirname(sys.executable)
    venv_script = os.path.join(venv_bin, command[0]) if command else None
    resolved = [venv_script] + command[1:] if (venv_script and os.path.isfile(venv_script)) else command

    result = subprocess.run(args=resolved, capture_output=True, text=True, check=False)
    return result.stdout, result.stderr, result.returncode
