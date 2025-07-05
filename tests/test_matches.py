import unittest
import subprocess
import re
import tempfile
import shutil
from pathlib import Path

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "find_perfect_matches.sh"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir = Path(tempfile.mkdtemp())
        cls._infile = cls._dir / "sample_123.fna"
        cls._outfile = cls._dir / "output.fna"
        with open(cls._infile, 'w') as f:
            f.write(INPUT_SEQUENCE)
        result = subprocess.run(
            ["bash", f"{SCRIPT_PATH}", f"{cls._infile.name}", f"{cls._outfile.name}"],
            cwd=cls._dir,
            text=True,
            capture_output=True
        )
        cls._stdout = result.stdout
        cls._stderr = result.stderr
        cls._exit = result.returncode

    @classmethod
    def tearDownClass(cls):
        if cls._dir.exists():
            shutil.rmtree(cls._dir)

    @weight(0)
    @number("6.1")
    def test_submitted_files(self):
        """Check submitted files"""
        missing_files = check_submitted_files([f'{SOLUTION_SCRIPT}'])
        for path in missing_files:
            print(f'Missing {path}')
        self.assertEqual(
            len(missing_files),
            0,
            f'Missing script {SOLUTION_SCRIPT}, follow instructions carefully'
        )
        print(f'{SOLUTION_SCRIPT} script submitted successfully')