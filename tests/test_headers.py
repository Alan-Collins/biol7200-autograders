import unittest
import subprocess
import tempfile
import re
from pathlib import Path
import shutil

from gradescope_utils.autograder_utils.decorators import weight, number, partial_credit
from gradescope_utils.autograder_utils.files import check_submitted_files

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "change_headers.sh"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"

INPUT_SEQUENCE = """>contig.1\nATCG\nGCTA\n>contig.2\nAAAA\nTTTT\n>contig.3\nCCCC\nGGGG\n"""

Q_NUM = 5
POINT_NUM = (i for i in range(1000))

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.submitted = True
        cls._dir = Path(tempfile.mkdtemp())
        if not Path(SCRIPT_PATH).exists():
            cls.submitted = False
            return cls
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
        if not self.submitted:
            self.fail("No script was submitted")
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
        if not self.submitted:
            self.fail("No script was submitted")
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
        if not self.submitted:
            self.fail("No script was submitted")
        if self._exit !=  0:
            self.fail(
                f"{SOLUTION_SCRIPT} returned a non-zero exit code. Something went wrong."
            )
        print("Your script ran successfully.")

    @weight(1)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    def test_no_err(self):
        """Check script produces no stderr"""
        if not self.submitted:
            self.fail("No script was submitted")
        if len(self._stderr.strip()) != 0:
            self.fail(
                f"{SOLUTION_SCRIPT} produced messages in the stderr indicating an issue."
                    "If you wrote to the stderr, remove those messages and resubmit."
            )
        print("Your script produced no errors.")

    @weight(2)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    def test_infile_unchanged(self):
        """Check input file unchanged"""
        if not self.submitted:
            self.fail("No script was submitted")
        with open(self._infile) as f:
            contents = f.read()
        if contents != INPUT_SEQUENCE:
            self.fail(
                "The input file was changed by your script. "
                "All modified data should be written to the output file without changing the input file."        
            )
        print("The input file was not modified")

    @partial_credit(2)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    def test_outfile_exists(self, set_score=None):
        """Check output file created correctly"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self._outfile.exists:
            self.fail(
                "Your script did not create the specified output file."
            )
        with open(self._outfile) as f:
            num_lines = len(f.readlines())
        if num_lines == 0:
            self.fail("Your script produced an empty output file.")
        with open(self._outfile) as f:
            contents = f.read()
        if contents == INPUT_SEQUENCE:
            print(
                "Your script created an output file, but did not change the test data. "
                "Make sure not to hard code anything. "
                "The test data is not the same as what you were provided (but is still valid FASTA)"
            )
            set_score(1)
        else:
            print("Your script produced the expected output file with modifications to the input.")
            set_score(2)
    
    @weight(2)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    def test_whitespace_in_headers(self):
        """Check whitespace in headers"""
        if not self.submitted:
            self.fail("No script was submitted")
        with open(self._outfile) as f:
            head = f.readline()
        pattern = re.compile(r"^\S*\s+\S*contig")
        if re.match(pattern, head):
            self.fail(
                "You have introduced whitespace into the header lines. "
                "whitespace marks the end of a FASTA header so you shouldn't be adding whitespace."
            )
        print("You didn't add whitespace to the headers. Whitespace characters mark the end of the header "
              "so adding whitespace while simply renaming headers would be a mistake.")
    
    @weight(4)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    def test_header_format_correct(self):
        """Check header formatting"""
        if not self.submitted:
            self.fail("No script was submitted")
        with open(self._outfile) as f:
            head = f.readline()
        pattern = re.compile(r"^[^>]")
        if re.match(pattern, head):
            self.fail(
                "Your script's output file is not valid FASTA format. "
                f"The first character in a header line should be '>', not '{head[0]}'. "
                "The '>' character is what indicates that a line is a header."
            )
        if head.strip() == ">contig.1":
            self.fail("Your script did not change the headers of the test data")
        pattern = re.compile(r"^>sample_123.*contig")
        if not re.match(pattern, head):
            self.fail(
                "Your header does not appear to include the test file name in the header"
            )
        print("The headers in your output file look like they are correctly formatted")

    @weight(4)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    def test_ext_not_in_header(self):
        """Check file extension not in header"""
        if not self.submitted:
            self.fail("No script was submitted")
        with open(self._outfile) as f:
            head = f.readline()
        if head.strip() == ">contig.1":
            self.fail("Your script did not change the headers of the test data")
        pattern = re.compile(r"^>sample_123.*contig")
        if not re.match(pattern, head):
            self.fail(
                "Your header does not appear to include the test file name in the header"
            )
        pattern = re.compile(r"^.*\.fna.*$")
        if re.match(pattern, head):
            self.fail(f"Your script has added the file extension to the header lines.")
        print("You removed file extensions from the header.")

    @weight(4)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
    def test_sequence_lines_unchanged(self):
        """Check sequence lines unchanged"""
        if not self.submitted:
            self.fail("No script was submitted")
        with open(self._outfile) as f:
            seq = f.readlines()[1].strip()
        expected = INPUT_SEQUENCE.split()[1]
        if seq != expected:
            self.fail(
                "Your script's output file includes modifications to sequence lines. "
                "Only header lines should be modified."
            )
        print("You did not change the sequence lines.")
