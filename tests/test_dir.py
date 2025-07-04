import unittest
import subprocess
import re
from pathlib import Path

from gradescope_utils.autograder_utils.decorators import weight
from gradescope_utils.autograder_utils.files import check_submitted_files

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "dir_script.sh"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"

TEST_PATH = "/test/childdir"

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run(
            ["bash", f"{SCRIPT_PATH}", f"{TEST_PATH}"],
            text=True,
            capture_output=True
        )
        cls._path = Path(TEST_PATH)
        cls._stdout = result.stdout
        cls._stderr = result.stderr
        cls._exit = result.returncode

    @classmethod
    def tearDownClass(cls):
        if cls._path.exists():
            for dir in cls._path.parents:
                dir.rmdir()

    @weight(0)
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
    
    @weight(2)
    def test_no_err(self):
        self.assertEqual(
            self._exit,
            0,
            f"{SOLUTION_SCRIPT} returned a non-zero exit code. Something went wrong."
        )
        self.assertEqual(
            len(self._stderr.strip()),
            0,
            f"{SOLUTION_SCRIPT} produced messages in the stderr indicating an issue."
                "If you wrote to the stderr, remove those messages and resubmit."
        )
    
    @weight(2)
    def test_taking_cli(self):
        found = False # look for use of commandline inputs
        pattern = re.compile(r"^[^#]*([ =]\$\d+|\bgetopts)([ #]|$)")
        with open(SCRIPT_PATH) as fin:
            for line in fin:
                if re.match(pattern, line):
                    found = True
        
        self.assertTrue(
            found,
            f'Your script does not appear to use command line arguments.'
        )

    @weight(2)
    def test_mkdir(self):
        self.assertTrue(
            self._path.exists(),
            "Your script did not create the directory specified as commandline input."
        )

    @weight(2)
    def test_cd(self):
        found = False # look for use of commandline inputs
        pattern = re.compile(r"^[^#]*cd ")
        with open(SCRIPT_PATH) as fin:
            for line in fin:
                if re.match(pattern, line):
                    found = True
        
        self.assertTrue(
            found,
            'Your script does not appear to change its working directory.'
        )

    @weight(1)
    def test_stdout_has_path(self):
        self.assertTrue(
            TEST_PATH in self._stdout,
            "Your script does not print the absolute path of the new working directory to stdout"
        )
    
    @weight(1)
    def test_stdout_is_only_path(self):
        if not TEST_PATH in self._stdout:
            self.fail("Your script's stdout does not include the new working directory")
        
        self.assertTrue(
            TEST_PATH == self._stdout.strip(),
            "Your script should only print the absolute path of the new working directory to stdout."
                "There should be nothing else written to the stdout."
        )