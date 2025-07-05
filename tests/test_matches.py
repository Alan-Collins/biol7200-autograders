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

TEST_DATA_PATH = Path("/autograder/biol7200-autograders/data/q6")
QUERY_FILE = "query.fna"
MATCH_ASSEMBLY_FILE = "match_assembly.fna"
NO_MATCH_ASSEMBLY_FILE = "no_match_assembly.fna"
QUERY_PATH = TEST_DATA_PATH / QUERY_FILE
MATCH_ASSEMBLY_PATH = TEST_DATA_PATH / MATCH_ASSEMBLY_FILE
NO_MATCH_ASSEMBLY_PATH = TEST_DATA_PATH / NO_MATCH_ASSEMBLY_FILE

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir = Path(tempfile.mkdtemp())
        cls._q = shutil.copy(QUERY_PATH, cls._dir / QUERY_FILE)
        cls._no_match = shutil.copy(NO_MATCH_ASSEMBLY_PATH, cls._dir / NO_MATCH_ASSEMBLY_FILE)
        cls._match = shutil.copy(MATCH_ASSEMBLY_PATH, cls._dir / MATCH_ASSEMBLY_FILE)
        cls._match_out = cls._dir / "match_out.txt"
        cls._no_match_out = cls._dir / "no_match_out.txt"
        result = subprocess.run(
            ["bash", f"{SCRIPT_PATH}", f"{cls._q}", f"{cls._match}", f"{cls._match_out}"],
            cwd=cls._dir,
            text=True,
            capture_output=True
        )
        cls._match_stdout = result.stdout
        cls._match_stderr = result.stderr
        cls._match_exit = result.returncode
        result = subprocess.run(
            ["bash", f"{SCRIPT_PATH}", f"{cls._q}", f"{cls._no_match}", f"{cls._no_match_out}"],
            cwd=cls._dir,
            text=True,
            capture_output=True
        )
        cls._no_match_stdout = result.stdout
        cls._no_match_stderr = result.stderr
        cls._no_match_exit = result.returncode

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
        if len(missing_files) > 0:
            self.fail(
                f'Missing script {SOLUTION_SCRIPT}, follow instructions carefully'
            )
        print(f'{SOLUTION_SCRIPT} script submitted successfully')
    
    @weight(1)
    @number("6.2")
    def test_zero_exit(self):
        """Check script runs successfully"""
        if self._match_exit !=  0:
            self.fail(
                f"{SOLUTION_SCRIPT} returned a non-zero exit code. Something went wrong."
            )
        print("Your script ran successfully.")

    @weight(1)
    @number("5.3")
    def test_no_err(self):
        """Check script produces no stderr"""
        if len(self._match_stderr.strip()) != 0 or len(self._no_match_stderr.strip()) != 0:
            self.fail(
                f"{SOLUTION_SCRIPT} produced messages in the stderr indicating an issue."
                    "If you wrote to the stderr, remove those messages and resubmit."
            )
        print("Your script produced no errors.")

    @weight(1)
    @number("5.4")
    def test_infile_unchanged(self):
        """Check input file unchanged"""
        match_eq = subprocess.call(["cmp", "-s", self._match, MATCH_ASSEMBLY_PATH])
        no_match_eq = subprocess.call(["cmp", "-s", self._no_match, NO_MATCH_ASSEMBLY_PATH])
        query_eq = subprocess.call(["cmp", "-s", self._q, QUERY_PATH])
        if not all([i == 0 for i in [match_eq, no_match_eq, query_eq]]):
            self.fail(
                "One or more input file was changed by your script. "
                "Your script should analyse the input files but should not make changes to them."        
            )
        print("The input files were not modified")

    @weight(1)
    @number("5.5")
    def test_outfile_exists(self):
        """Check output file created"""
        if not all([
            self._match_out.exists,
            self._no_match_out.exists            
        ]):
            self.fail(
                "Your script did not create the specified output file."
            )
        print("Your script produced the expected output file.")