import unittest
from pathlib import Path
from tempfile import mkdtemp
import shutil
import subprocess
import re

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import PointCounter

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "pretty_align.py"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"

Q_NUM = 1

POINT_NUM = PointCounter(0)

SEQS_UNWRAPPED = """\
>seq1
AACTACCTGTCAGTCGCAATCTTTATACCCTATCTTATGTCTACTTGTCT
>seq2
TACTTAAGATCAGTCGCAATCTTTATGGCCTATCTTCGGTCTACTTGTCT
"""

SEQS_WRAPPED = """\
>seq1
AACTACCTGTCAGTCGCAATCTTTA
TACCCTATCTTATGTCTACTTGTCT
>seq2
TACTTAAGATCAGTCGCAATCTTTA
TGGCCTATCTTCGGTCTACTTGTCT
"""

EXPECTED = """\
AACTACCTGTCAGTCGCAATCTTTATACCCTATCTTATGTCTACTTGTCT
 |||     |||||||||||||||||  ||||||||  ||||||||||||
TACTTAAGATCAGTCGCAATCTTTATGGCCTATCTTCGGTCTACTTGTCT
"""

HIDDEN_SEQS_UNWRAPPED = """\
>seq1
TTCAGTATCGAGAACCTGTTCCCGAATTAACAGAGACCCCCGCCGTCGCC
>seq2
TTCAATGTCGTGAATGTGTTCCCGAATTAATACCGTCCCCCGCCGTCGCT
"""

HIDDEN_SEQS_WRAPPED = """\
>seq1
TTCAGTATCGAGAACCTGTTCCCGA
ATTAACAGAGACCCCCGCCGTCGCC
>seq2
TTCAATGTCGTGAATGTGTTCCCGA
ATTAATACCGTCCCCCGCCGTCGCT
"""

HIDDEN_EXPECTED = """\
TTCAGTATCGAGAACCTGTTCCCGAATTAACAGAGACCCCCGCCGTCGCC
|||| | ||| |||  |||||||||||||| |  | ||||||||||||| 
TTCAATGTCGTGAATGTGTTCCCGAATTAATACCGTCCCCCGCCGTCGCT
"""

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = mkdtemp()
        wrapped = Path(cls.dir) / Path("wrapped.fna")
        unwrapped = Path(cls.dir) / Path("unwrapped.fna")
        wrapped_hidden = Path(cls.dir) / Path("wrapped_hidden.fna")
        unwrapped_hidden = Path(cls.dir) / Path("unwrapped_hidden.fna")
        with open(wrapped.resolve(), 'w') as f:
            f.write(SEQS_WRAPPED)
        with open(unwrapped.resolve(), 'w') as f:
            f.write(SEQS_UNWRAPPED)
        with open(wrapped_hidden.resolve(), 'w') as f:
            f.write(HIDDEN_SEQS_WRAPPED)
        with open(unwrapped_hidden.resolve(), 'w') as f:
            f.write(HIDDEN_SEQS_UNWRAPPED)
        
        cls.submitted = True
        cls.results = {}
        cls.shebang = False
        cls.zero_exit = True
        if not Path(SCRIPT_PATH).exists():
            cls.submitted = False
            return cls
        else:
            pattern = re.compile(r"\#\![ ]?/usr/bin/env python3")
            with open(SCRIPT_PATH) as f:
                first_line = f.readline()
            if re.match(pattern, first_line):
                cls.shebang = True
        cls.zero_exit = False
        shutil.copy(SCRIPT_PATH, cls.dir)
        Path(f"{cls.dir}/{SOLUTION_SCRIPT}").chmod(0o777)
        if not cls.shebang:
            return cls
        wrapped_result = subprocess.run(
            ["./pretty_align.py", f"{wrapped.resolve()}"],
            text=True,
            capture_output=True,
            cwd=cls.dir
        )
        
        if wrapped_result.returncode != 0:
            cls.zero_exit = False
        
        unwrapped_result = subprocess.run(
            ["./pretty_align.py", f"{unwrapped.resolve()}"],
            text=True,
            capture_output=True,
            cwd=cls.dir
        )
        
        if unwrapped_result.returncode != 0:
            cls.zero_exit = False

        hidden_wrapped_result = subprocess.run(
            ["./pretty_align.py", f"{wrapped_hidden.resolve()}"],
            text=True,
            capture_output=True,
            cwd=cls.dir
        )
        
        if hidden_wrapped_result.returncode != 0:
            cls.zero_exit = False
        
        hidden_unwrapped_result = subprocess.run(
            ["./pretty_align.py", f"{unwrapped_hidden.resolve()}"],
            text=True,
            capture_output=True,
            cwd=cls.dir
        )

        if hidden_unwrapped_result.returncode != 0:
            cls.zero_exit = False
        
        cls.results = {
            "wrapped": wrapped_result,
            "unwrapped": unwrapped_result,
            "hidden_wrapped": hidden_wrapped_result,
            "hidden_unwrapped": hidden_unwrapped_result
        }

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir)

    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("on_fail")
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

    @weight(65)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_any_worked(self):
        """Check if submitted script works for any test cases"""
        if not self.submitted:
            self.fail("No script was submitted")
        worked = False
        for category, result in self.results.items():
            if "hidden" in category:
                comparator = HIDDEN_EXPECTED
            else:
                comparator = EXPECTED
            if result.stdout.strip() == comparator.strip() and result.returncode == 0:
                worked = True
        if worked == False:
            self.fail("No outputs match the expected output.")
        else:
            print("Your script works for at least one of the test cases.")

    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
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

    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_shebang_correct(self):
        """Check shebang correct"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.shebang:
            self.fail(
                f"Your script does not begin with a correct shebang."
            )
        print("Your script begins with a correct shebang.")
    
    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_zero_exit(self):
        """Check zero exit"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.shebang:
            self.fail(
                f"Your script does not begin with a correct shebang."
            )
        for category, result in self.results.items():
            if result.returncode != 0:
                if not "un" in category:
                    self.fail(
                        "Your script produced a non-zero exit code "
                        "when provided input sequences which are wrapped "
                        "over multiple lines."
                        )
                else:
                    self.fail(
                        "Your script produced a non-zero exit code "
                        "when provided input sequences which are each "
                        "on a single line like the example provided in "
                        "the assignment."
                        )
        print("Your script produced an exit code of zero for all tests.")

    @weight(10)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_matches_expected_shown(self):
        """Check output matches expected"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.shebang:
            self.fail(
                f"Your script does not begin with a correct shebang."
            )
        one_line_res = self.results["unwrapped"]
        for a, b in zip(one_line_res.stdout.split("\n"), EXPECTED.split("\n")):
            self.assertEqual(
                a, b,
                "Your output does not match the expected output for single-line sequences"
            )
        
        multi_line_res = self.results["wrapped"]
        for a, b in zip(multi_line_res.stdout.split("\n"), EXPECTED.split("\n")):
            self.assertEqual(
                a, b,
                "Your output does not match the expected output for multi-line sequences"
            )
        print("Your output matches the expected output for the first test case.")

    @weight(10)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_matches_expected_hidden(self):
        """Check output matches expected hidden testcase"""
        one_line_res = self.results["hidden_unwrapped"]
        for a, b in zip(one_line_res.stdout.split("\n"), HIDDEN_EXPECTED.split("\n")):
            if a == b:
                continue
            self.fail(
                "Your output does not match the expected output for single-line sequences"
            )
        
        multi_line_res = self.results["hidden_wrapped"]
        for a, b in zip(multi_line_res.stdout.split("\n"), HIDDEN_EXPECTED.split("\n")):
            if a == b:
                continue
            self.fail(
                "Your output does not match the expected output for multi-line sequences"
            )
        print("Your output matches the expected output for the second test case.")

    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("hidden")
    def test_view_output(self):
        """secretly print outputs for grading"""
        one_line_res = self.results["hidden_unwrapped"]
        print("expected for known sequence")
        print(EXPECTED)
        print("student unwrapped output for known sequence")
        print(self.results.get("unwrapped"))
        print("student wrapped output for known sequence")
        print(self.results.get("wrapped"))
        print("\n")
        print("expected for hidden sequence")
        print(HIDDEN_EXPECTED)
        print("student unwrapped output for hidden sequence")
        print(self.results.get("hidden_unwrapped"))
        print("student wrapped output for hidden sequence")
        print(self.results.get("hidden_wrapped"))
