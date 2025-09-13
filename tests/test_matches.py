import unittest
import subprocess
import re
import tempfile
import shutil
from pathlib import Path

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import PointCounter, BlastResult

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

Q_NUM = 6
POINT_NUM = PointCounter(0)

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.submitted = True
        cls.was_run = False
        cls._dir = Path(tempfile.mkdtemp())
        if not Path(SCRIPT_PATH).exists():
            cls.submitted = False
            return cls
        outfmt_pattern = re.compile(r"-outfmt[ ]*?(?:([\'\" ]?)[ ]*6[ ]*\1|([\'\"])[ ]*6[ ]*(.*?)\2)")
        with open(SCRIPT_PATH) as f:
            lines = []
            for line in f:
                # skip commented lines
                if line.strip().startswith("#"):
                    continue
                lines.append(line.rstrip().strip("\\"))
        contents = "".join(lines)
        cls._all_outfmts = re.findall(outfmt_pattern, contents)
        cls._outfmt_count = len(cls._all_outfmts)
        outfmt_match = re.search(outfmt_pattern, contents)
        if outfmt_match is None:
            cls._outfmt = None
            return cls
        cls._outfmt = outfmt_match.group(3)
        cls._qcov_hsp_perc = re.search(r"-qcov_hsp_perc[ ]+100", contents) is not None
        cls._perc_identity = re.search(r"-perc_identity[ ]+100", contents) is not None
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
        cls.was_run = True
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
    @number(f"{Q_NUM}.{POINT_NUM}")
    def test_submitted_files(self):
        """Check submitted files"""
        if not self.submitted:
            self.fail("No script was submitted")
        missing_files = check_submitted_files([f'{SOLUTION_SCRIPT}'])
        for path in missing_files:
            print(f'Missing {path}')
        if len(missing_files) > 0:
            self.fail(
                f'Missing script {SOLUTION_SCRIPT}, follow instructions carefully'
            )
        print(f'{SOLUTION_SCRIPT} script submitted successfully')
    
    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_line_endings(self):
        """Check unix line endings"""
        if not self.submitted:
            self.fail("No script was submitted")
        with open(SCRIPT_PATH) as f:
            f.readline()
            newlines = f.newlines
        if newlines != "\n":
            self.fail(
                "Your script does not use unix line endings. "
                "That might interfere with the functionality of autograder tests. "
                f"Please change your line endings to the unix \\n instead of your current {repr(newlines)}"
            )
        print("Your script uses Unix line endings: '\\n'")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
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
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
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
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_zero_exit(self):
        """Check script runs successfully"""
        if not self.was_run:
            self.fail("Your script had issues and so was not run.")
        if self._match_exit !=  0:
            self.fail(
                f"{SOLUTION_SCRIPT} returned a non-zero exit code. Something went wrong."
            )
        print("Your script ran successfully.")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_no_err(self):
        """Check script produces no stderr"""
        if not self.was_run:
            self.fail("Your script had issues and so was not run.")
        if len(self._match_stderr.strip()) != 0 or len(self._no_match_stderr.strip()) != 0:
            self.fail(
                f"{SOLUTION_SCRIPT} produced messages in the stderr indicating an issue."
                    "If you wrote to the stderr, remove those messages and resubmit.\n"
                    f"{self._match_stderr or self._no_match_stderr}"
            )
        print("Your script produced no errors.")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_infile_unchanged(self):
        """Check input file unchanged"""
        if not self.was_run:
            self.fail("Your script had issues and so was not run.")
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
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_outfile_exists(self):
        """Check output file created"""
        if not self.was_run:
            self.fail("Your script had issues and so was not run.")
        if not all([
            self._match_out.exists,
            self._no_match_out.exists            
        ]):
            self.fail(
                "Your script did not create the specified output file."
            )

        with open(self._match_out) as f:
            num_lines = len(f.readlines())
        if num_lines == 0:
            self.fail("Your script produced an empty output file.")

        print("Your script produced the expected output file.")

    @weight(4)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_task_blastn_short(self):
        """Check task used"""
        with open(SCRIPT_PATH) as f:
            found = False
            for line in f:
                if line.strip().startswith("#"):
                    continue
                if re.match(".*blastn-short.*", line):
                    found = True
        if not found:
            self.fail("The instructions specified you must use a -task option. Check the assignment document.")

        print("Your script uses -task as instructed.")

    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_can_determine_perf(self):
        """Check you include data for identifying perfect hits"""
        if not self._outfmt:
            self.fail(
                "Your script does not include any specification of the outfmt. Consult the BLAST section of the assignment document if unsure."
            )
        if not self._outfmt_count > 0:
            self.fail(
                "Your script does not include any specification of the outfmt. Consult the BLAST section of the assignment document if unsure."
            )
        if self._outfmt_count > 1 and len(set(self._all_outfmts)) > 1:
            self.fail(
                "Your script is running blast multiple times with (what look like) different outfmt specifications. For the sake of my sanity in writing these autograder checks please just run BLAST once in your script."
            )
        br = BlastResult.from_outfmt_str(self._outfmt)
        if not br.can_verify_perfect_match(self._qcov_hsp_perc, self._perc_identity):
            self.fail(
                "You do not use BLAST settings that can allow you to identify perfect hits.\nIf you are convinced this automated check is wrong, you can ask me or a TA to confirm."
            )

        print("Your script uses BLAST settings that allow you to identify perfect hits.")

    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_attempts_filtering(self):
        """Check your script filters hits"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.was_run:
            self.fail("Your script had issues and so was not run.")
        with open(SCRIPT_PATH) as fin:
            contents = fin.read()
        if not "awk" in contents or not "==" in contents:
            self.fail(
                "It looks like your script does not include a step to filter BLAST hits"
            )
        
        print("Your script includes filtering of hits")

    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_file_match_number(self):
        """Check correct number of matches in output file"""
        if not self.was_run:
            self.fail("Your script had issues and so was not run.")
        if not self._match_out.exists():
            self.fail(
                "Your script did not create the specified output file."
            )

        with open(self._match_out) as f:
            num_lines = len(f.readlines())
        if num_lines == 0:
            self.fail("Your script produced an empty output file.")
        
        if num_lines != 10:
            self.fail("Your script's output file contains the wrong number of matches.")

        with open(self._no_match_out) as f:
            num_lines = len(f.readlines())
        if num_lines != 0:
            self.fail("Your script's output file contains the wrong number of matches.")

        print("Your script produced an output file containing the expected number of matches.")

    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_stdout_match_number(self):
        """Check correct number of matches in stdout"""
        if not self.was_run:
            self.fail("Your script had issues and so was not run.")
        match_numbers = re.findall(r"\b\d+\b", self._match_stdout)
        no_match_numbers = re.findall(r"\b\d+\b", self._no_match_stdout)

        if len(match_numbers) > 1 or len(no_match_numbers) > 1:
            self.fail(
                "Your script produces stdout with too many numbers for this simple autograder to interpret.\n"
                "It should only print the number of perfect hits identified to stdout."
            )
        if len(match_numbers) == 0 or len(no_match_numbers) == 0:
            self.fail(
                "No numbers were found in your script's stdout"
            )

        if int(match_numbers[0]) != 10 or int(no_match_numbers[0]) != 0:
            self.fail("Your script prints the wrong number of matches to the stdout.")
        print("Your script printed the expected number of hits to stdout.")

    @weight(0)
    @visibility("hidden")
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_see_match_hits(self):
        """View hits for file that should have matches"""
        print(f"outfmt specification: {self._outfmt}")
        with open(self._match_out) as f:
            print(f.read())
    
    @weight(0)
    @visibility("hidden")
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_see_no_match_hits(self):
        """View hits for file that shouldn't have matches"""
        print(f"outfmt specification: {self._outfmt}")
        with open(self._no_match_out) as f:
            print(f.read())
