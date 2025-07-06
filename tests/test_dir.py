import unittest
import subprocess
import re
from pathlib import Path

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "dir_script.sh"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"

TEST_PATH = "/test/childdir"

Q_NUM = 4
POINT_NUM = (i for i in range(1000))

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
            cls._path.rmdir()
            for dir in cls._path.parents:
                if str(dir) == "/":
                    break
                dir.rmdir()

    @weight(0)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
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
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    def test_shebang_present(self):
        """Check script uses shebang"""
        with open(SCRIPT_PATH) as f:
            first_two = f.read()[:2]
        if first_two != "#!":
            self.fail(
                f"Your scripts should always start with a shebang to ensure the correct program executes them."
            )
        print("Your script begins with a shebang.")

    @weight(1)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    def test_shebang_correct(self):
        """Check shebang correct"""
        pattern = re.compile(r"\#\![ ]?/(?:usr/(?=bin/env))?bin/(?:(?<=usr/bin/)env )?bash")
        with open(SCRIPT_PATH) as f:
            first_line = f.readline()
        if not re.match(pattern, first_line):
            self.fail(
                f"Your script does not begin with a correct shebang."
            )
        print("Your script begins with a correct shebang.")
    
    @weight(1)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    def test_zero_exit(self):
        """Check script runs successfully"""
        if self._exit !=  0:
            self.fail(
                f"{SOLUTION_SCRIPT} returned a non-zero exit code. Something went wrong."
            )
        print("Your script ran successfully.")

    @weight(1)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    def test_no_err(self):
        """Check script produces no stderr"""
        if len(self._stderr.strip()) != 0:
            self.fail(
                f"{SOLUTION_SCRIPT} produced messages in the stderr indicating an issue."
                    "If you wrote to the stderr, remove those messages and resubmit."
            )
        print("Your script produced no errors.")
    
    @weight(2)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    def test_taking_cli(self):
        """Check script uses command line inputs"""
        found = False # look for use of commandline inputs
        pattern = re.compile(r"^[^#]*([ =]\$\d+|\bgetopts)([ #]|$)")
        with open(SCRIPT_PATH) as fin:
            for line in fin:
                if re.match(pattern, line):
                    found = True
        
        if not found:
            self.fail(
                f'Your script does not appear to use command line arguments.'
            )
        print("your script uses the provided command line arguments.")

    @weight(1)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    def test_mkdir(self):
        """Check script makes directory"""
        if not self._path.exists():
            self.fail(
                "Your script did not create the directory specified as commandline input."
            )
        print("Your script created the expected directory")

    @weight(1)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    def test_cd(self):
        """Check script changes directory"""
        found = False # look for use of commandline inputs
        pattern = re.compile(r"^[^#]*cd ")
        with open(SCRIPT_PATH) as fin:
            for line in fin:
                if re.match(pattern, line):
                    found = True
        
        if not found:
            self.fail(
                'Your script does not appear to change its working directory.'
            )
        print("Your script changes its working directory.")

    @weight(1)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    def test_stdout_has_path(self):
        """Check script writes path to stdout"""
        found = False # look for use of commandline inputs
        pattern = re.compile(r"^[^#]*pwd")
        with open(SCRIPT_PATH) as fin:
            for line in fin:
                if re.match(pattern, line):
                    found = True
        if not found:
            self.fail(
                "Your script does not print the location of its current working directory."
            )
        
        if TEST_PATH not in self._stdout:
            self.fail(
                "Your script does not print the absolute path of the new working directory to stdout"
            )
        print("Your script prints the path of its current working directory")
    
    @weight(1)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    def test_stdout_is_only_path(self):
        """Check script doesn't print extraneous information to stdout"""
        if not TEST_PATH in self._stdout:
            self.fail("Your script's stdout does not include the new working directory")
        
        if TEST_PATH != self._stdout.strip():
            self.fail(
                "Your script should only print the absolute path of the new working directory to stdout."
                    "There should be nothing else written to the stdout."
            )
        print("The stdout of your script only contains the instructed contents: the path of your scripts working directory.")
    
    @weight(0)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    @visibility("on_fail")
    def test_validating_cli(self):
        """Check script validates inputs"""
        found = False # look for conditional checking cli
        pattern = re.compile(r"if.*\[.*\$\#.*\]")
        with open(SCRIPT_PATH) as fin:
            for line in fin:
                if re.match(pattern, line):
                    found = True
        if found:
            self.fail(
                'It looks like you are validating the number of command line arguments given to your script. '
                "That's not necessary for any of the Bash assignments in this course (but you can do it if you like). "
                'LLMs like to include input validation in their Bash scripts. '
                'If you included it here because you have seen it when talking to an LLM, '
                'then two things:\n'
                '1. Make sure you understand and can write from memory all of the code you submit for assignments.\n'
                "2. We'll cover conditionals like that in an upcoming class. If you don't understand how it works then (see point 1, but also) you should understand it after that class.\n"
            )

    @weight(0)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    @visibility("on_fail")
    def test_named_variables(self):
        """Check script uses named variables"""
        found = False # look for assignment of cli to var
        pattern = re.compile(r"[^=]\$1")
        with open(SCRIPT_PATH) as fin:
            for line in fin:
                if re.match(pattern, line):
                    found = True
        
        if found:
            self.fail(
                'It looks like you are using command line arguments directly. '
                'Consider assigning command line inputs to named variables instead. '
                'Named variables make it much easier for a reader to understand what code is doing.'
            )
