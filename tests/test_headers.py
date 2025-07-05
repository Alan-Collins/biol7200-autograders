import unittest
import subprocess
import tempfile
import re
from pathlib import Path
import shutil

from gradescope_utils.autograder_utils.decorators import weight, number
from gradescope_utils.autograder_utils.files import check_submitted_files

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "change_headers.sh"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"

INPUT_SEQUENCE = """>contig.1\nATCG\nGCTA\n>contig.2\nAAAA\nTTTT\n>contig.3\nCCCC\nGGGG\n"""

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
    @number("5.1")
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
    @number("5.2")
    def test_zero_exit(self):
        """Check script runs successfully"""
        if self._exit !=  0:
            self.fail(
                f"{SOLUTION_SCRIPT} returned a non-zero exit code. Something went wrong."
            )
        print("Your script ran successfully.")

    @weight(1)
    @number("5.3")
    def test_no_err(self):
        """Check script produces no stderr"""
        if len(self._stderr.strip()) != 0:
            self.fail(
                f"{SOLUTION_SCRIPT} produced messages in the stderr indicating an issue."
                    "If you wrote to the stderr, remove those messages and resubmit."
            )
        print("Your script produced no errors.")

    @weight(5)
    @number("5.4")
    def test_infile_unchanged(self):
        """Check input file unchanged"""
        with open(self._infile) as f:
            contents = f.read()
        if contents != INPUT_SEQUENCE:
            self.fail(
                "The input file was changed by your script. "
                "All modified data should be written to the output file without changing the input file."        
            )
        print("The input file was not modified")

    @weight(5)
    @number("5.5")
    def test_outfile_exists(self):
        """Check output file created"""
        if not self._outfile.exists:
            self.fail(
                "Your script did not create the specified output file."
            )
        print("Your script produced the expected output file.")
    
    @weight(3)
    @number("5.6")
    def test_whitespace_in_headers(self):
        """Check whitespace in headers"""
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
    
    @weight(5)
    @number("5.7")
    def test_header_format_correct(self):
        """Check header formatting"""
        with open(self._outfile) as f:
            head = f.readline()
        pattern = re.compile(r"^[^>]")
        if re.match(pattern, head):
            self.fail(
                "Your script's output file is not valid FASTA format. "
                f"The first character in a header line should be '>', not '{head[0]}'. "
                "The '>' character is what indicates that a line is a header."
            )
        print("The headers in your output file look like they are correctly formatted")

    @weight(5)
    @number("5.8")
    def test_ext_not_in_header(self):
        """Check file extension not in header"""
        with open(self._outfile) as f:
            head = f.readline()
        pattern = re.compile(r"^.*\.fna.*$")
        if re.match(pattern, head):
            self.fail(f"Your script has added the file extension to the header lines.")
        print("You removed file extensions from the header.")

    @weight(5)
    @number("5.9")
    def test_sequence_lines_unchanged(self):
        """Check sequence lines unchanged"""
        with open(self._outfile) as f:
            seq = f.readlines()[1].strip()
        expected = INPUT_SEQUENCE.split()[1]
        if seq != expected:
            self.fail(
                "Your script's output file includes modifications to sequence lines. "
                "Only header lines should be modified."
            )
        print("You did not change the sequence lines.")