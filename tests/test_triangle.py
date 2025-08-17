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
            cls.code = fin.read()
        # check shebang
        pattern = re.compile(r"\#\![ ]?/usr/bin/env python3")
        with open(SCRIPT_PATH) as f:
            first_line = f.readline()
        if re.match(pattern, first_line):
            cls.shebang = True
        else:
            cls.shebang = False
        try:
            func_found = False
            func_body = []
            indent = None
            func_lines = []
            cls.def_lines = []
            cls.func_names = []
            cls.baseline_code = []
            for line in cls.code.splitlines():
                if func_found:
                    if not indent:
                        # If the function starts with a de-indented comment can't get indent amount
                        if len(line.split("#")[0].strip()) == 0:
                            continue
                        indent = re.match(r"^\s*", line)[0]
                    # Add appropriately indented lines and blank lines
                    # If the line is neither it indicates the end of the function body
                    if line.startswith(indent) or len(line.split("#")[0].strip()) == 0:
                        func_lines.append(line)
                        continue
                    else:
                        func_body.append("\n".join(func_lines))
                        func_lines = []
                        func_found = False
                if line.startswith("def"):
                    cls.def_lines.append(line)
                    cls.func_names.append(line.split()[1].split("(")[0])
                    func_found = True
                elif line.startswith("#") or line.startswith("import"):
                    continue
                else:
                    cls.baseline_code.append(line)


            cls.imported = True
        except Exception as e:
            cls.parse_exception = e
            cls.imported = False
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


    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("on_fail")
    def test_parsed(self):
        """Check your script could be parsed"""
        if not self.imported:
            self.fail(
                "Couldn't import your script due to the following error.\n"
                "Please bring this issue to the attention of Dr. Collins as this may be an"
                "issue with his autograder code..."
                f"{self.parse_exception}"
            )
        else:
            print(f"Script parsed successfully and {len(self.func_names)} functions were found.")
    
    # check base line code just functions and single call

    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("on_fail")
    def test_single_baseline_line(self):
        """Check your script uses functions for all code except one call"""
        if not self.imported:
            self.fail(
                "Couldn't import your script."
            )
        if len(self.baseline_code) == 1:
            print(
                "Only one line of code found on the baseline:\n"
                f"{self.baseline_code[0]}"  
            )
        else:
            print("found multiple lines of code on the baseline:\n")
            for line in self.baseline_code:
                print(line)
            self.fail("")
            

    # run script and check triangles

    # interrogate docstrings

    # check type hints
