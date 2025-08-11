import unittest
import sys
from pathlib import Path
import re

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import PointCounter

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "triangle.py"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"

Q_NUM = 1

POINT_NUM = PointCounter(0)

sys.path.append(SUBMISSION_PATH)


class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        soln = Path(SCRIPT_PATH)
        if not soln.exists():
            cls.submitted = False
            return cls
        with open(soln) as fin:
            code = fin.read()
        # check shebang
        pattern = re.compile(r"\#\![ ]?/usr/bin/env python3")
        with open(SCRIPT_PATH) as f:
            first_line = f.readline()
        if re.match(pattern, first_line):
            cls.shebang = True
        else:
            cls.shebang = False

        # check base line code just functions and single call


        # run script and check triangles

        try:
            import triangle

            # interrogate docstrings

            # check type hints
        except:
            cls.imported = False
            cls.docstrings = False
            cls.typehints = False
            return cls

        
        
        


        


    @classmethod
    def tearDownClass(cls):
        pass

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
