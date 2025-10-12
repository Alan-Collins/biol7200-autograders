import unittest
from pathlib import Path
import re
import subprocess
import ast

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import PointCounter

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "pair_parens.py"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"

Q_NUM = 2

POINT_NUM = PointCounter(0)

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.submission = Path(SCRIPT_PATH)
        if not cls.submission.exists():
            cls.submitted = False
            return cls
        cls.submission.chmod(0o777)
        cls.submitted = True
        cls.code = cls.submission.read_text()
        # check shebang
        pattern = re.compile(r"\#\![ ]?/usr/bin/env python3")
        with open(SCRIPT_PATH) as f:
            first_line = f.readline()
        if re.match(pattern, first_line):
            cls.shebang = True
        else:
            cls.shebang = False
        try:
            cls.tree = ast.parse(cls.code)
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
    @visibility("on_fail")
    def test_parsed(self):
        """Check your script could be parsed"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.imported:
            self.fail(
                "Couldn't parse your script due to the following error.\n"
                "Please bring this issue to the attention of Dr. Collins as this may be an"
                "issue with his autograder code..."
                f"{self.parse_exception}"
            )
        
        print(f"Script parsed successfully.")
    
    # check base line code just functions and single call

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_single_baseline_line(self):
        """Check your script uses functions for all code except one call"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.imported:
            self.fail(
                "Couldn't parse your script."
            )
        body = list(self.tree.body)
        # remove module docstring if present (first node a string Expr)
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            body = body[1:]
        # count nodes that are not imports or function defs
        baseline_code = [n for n in body if not isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef))]
        if len(baseline_code) == 1:
            print(
                "Only one line of code found on the baseline:\n"
                f"{ast.unparse(baseline_code[0])}"
            )
        else:
            print("found multiple lines of code on the baseline:\n")
            for line in baseline_code:
                print(ast.unparse(line))
            self.fail("")


    # run script and check triangles
    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_paired(self):
        """Check your script works for paired parentheses"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.shebang:
            self.fail(
                f"Your script does not begin with a correct shebang."
            )
        tests = [
            ("()", "PAIRED"),
            ("()()()", "PAIRED"),
            ("(()())", "PAIRED"),
            ("((()))", "PAIRED"),
            ("(()())", "PAIRED"),
            ("((())())", "PAIRED")
        ]
        for input, expected in tests:
            command = [self.submission, input]
            result = subprocess.run(
                command,
                text=True,
                capture_output=True
            )
            if result.returncode != 0:
                self.fail(
                    "Your script returned a non-zero exit code\n"
                    f"The stderr was {result.stderr}"
                )
            if result.stdout.strip() != expected:
                self.fail(
                    "Your script's output did not match the expected output for paired parentheses."
                )
        print("Your script correctly identified paired parentheses")
        

    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_unpaired(self):
        """Check your script works for paired parentheses"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.shebang:
            self.fail(
                f"Your script does not begin with a correct shebang."
            )
        tests = [
            (")", "NOT PAIRED"),
            (")(", "NOT PAIRED"),
            ("()()(", "NOT PAIRED"),
            (")((())", "NOT PAIRED"),
            ("))((", "NOT PAIRED"),
            ("())(", "NOT PAIRED"),
            # ("())(()", "NOT PAIRED")  ##### Uncomment after assignment is done
        ]
        for input, expected in tests:
            command = [self.submission, input]
            result = subprocess.run(
                command,
                text=True,
                capture_output=True
            )
            if result.returncode != 0:
                self.fail(
                    "Your script returned a non-zero exit code\n"
                    f"The stderr was {result.stderr}"
                )
            if result.stdout.strip() != expected:
                self.fail(
                    "Your script's output did not match the expected output for unpaired parentheses."
                )
        print("Your script correctly identified unpaired parentheses")


    # interrogate docstrings
    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_docstrings_used(self):
        """Check your functions have docstrings"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.shebang:
            self.fail(
                f"Your script does not begin with a correct shebang."
            )
        funcs = [n for n in self.tree.body if isinstance(n, (ast.FunctionDef))]
        for f in funcs:
            docstring = ast.get_docstring(f)
            if not docstring or not docstring.strip():
                self.fail(
                    f"No docstring found for your function {f.name}"
                )
        print("looks like docstrings were used. The quality of your docstrings will be assessed manually.")

    # check type hints
    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_typehints_used(self):
        """Check your functions have typehints"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.shebang:
            self.fail(
                f"Your script does not begin with a correct shebang."
            )
        funcs = [n for n in self.tree.body if isinstance(n, (ast.FunctionDef))]
        for f in funcs:
            if not f.returns:
                self.fail(f"Missing return type annotation for {f.name}")
            params = f.args.args
            params.extend(f.args.posonlyargs)
            params.extend(f.args.kwonlyargs)

            for a in params:
                if not a.annotation:
                    self.fail(
                        f"No annotation found for your function {f.name}'s param {a.arg}"
                    )
        print("looks like annotations were used. The quality of your annotations will be assessed manually.")
