import unittest
from pathlib import Path
from tempfile import mkdtemp
import shutil
import subprocess
import re

from gradescope_utils.autograder_utils.decorators import (
    weight,
    number,
    visibility,
)
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import PointCounter

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "get_homolog_seqs.py"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"
DATA_DIR = "/autograder/biol7200-autograders/data/"

Q_NUM = 3

POINT_NUM = PointCounter(0)


class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = mkdtemp()
        cls.input_files = [
            "Vibrio_cholerae_N16961.fna",
            "Vibrio_cholerae_N16961.bed",
            "Vc_blastout.txt"
        ]
        for file in cls.input_files:
            shutil.copy(f"{DATA_DIR}{file}", f"{cls.dir}/")
        cls.submitted = True
        cls.outfile = Path(f"{cls.dir}/Vc_student_out.fna")
        if not Path(SCRIPT_PATH).exists():
            cls.submitted = False
            return cls
        else:
            pattern = re.compile(r"\#\![ ]?/usr/bin/env python3")
            with open(SCRIPT_PATH) as f:
                first_line = f.readline()
            if re.match(pattern, first_line):
                cls.shebang = True
            else:
                cls.shebang = False
        cls.zero_exit = False
        shutil.copy(SCRIPT_PATH, cls.dir)
        Path(f"{cls.dir}/{SOLUTION_SCRIPT}").chmod(0o777)
        assembly =  Path(f"{cls.dir}/Vibrio_cholerae_N16961.fna")
        bed = Path(f"{cls.dir}/Vibrio_cholerae_N16961.bed")
        blast = Path(f"{cls.dir}/Vc_blastout.txt")
        command = [
            f"./{SOLUTION_SCRIPT}",
            blast,
            bed,
            assembly,
            cls.outfile
        ]
        cls.result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            cwd=cls.dir
        )
        if cls.result.returncode == 0:
            cls.zero_exit = True


    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir)

    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM}")
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
    
    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("on_fail")
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

    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("on_fail")
    def test_shebang_correct(self):
        """Check shebang correct"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.shebang:
            self.fail(
                f"Your script does not begin with a correct shebang."
            )
        print("Your script begins with a correct shebang.")

    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_exit_codes(self):
        """Check script ran without error"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.zero_exit:
            self.fail("Your script exited with a non-zero exit code.")
        print("Your script ran successfully.")
