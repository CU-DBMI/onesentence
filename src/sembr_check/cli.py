"""
CLI for sembr_check
"""

import fire
import sys
from sembr_check.utils import check_file_for_semantic_line_breaks

class SembrCheckCLI:
    def check(self, file_path: str) -> bool:
        """
        Check if each line in the given file contains only one sentence.
        
        Args:
            file_path (str): The path to the file to check.
            
        Returns:
            bool: True if all lines contain only one sentence, False otherwise.
        """
        result = check_file_for_semantic_line_breaks(file_path)
        if result:
            sys.exit(0)
        else:
            sys.exit(1)

def trigger():
    """
    Trigger the CLI to run.
    """
    fire.Fire(SembrCheckCLI)


if __name__ == "__main__":
    """
    Setup the CLI with python-fire for the sembr_check package.

    This allows the function `check` to be ran through the
    command line interface.
    """

    trigger()