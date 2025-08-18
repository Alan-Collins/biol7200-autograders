import unittest
from pathlib import Path
import re
import subprocess

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import PointCounter

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "triangle.py"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"

Q_NUM = 1

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
        with open(cls.submission) as fin:
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
            cls.func_bodies = []
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
                        cls.func_bodies.append("\n".join(func_lines))
                        func_lines = []
                        func_found = False
                if line.startswith("def"):
                    cls.def_lines.append(line)
                    cls.func_names.append(line.split()[1].split("(")[0])
                    func_found = True
                elif line.startswith("#") or line.startswith("import") or line.strip() == "":
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
        for fname, f in zip(self.func_names, self.func_bodies):
            try:
                eval(f)
            except Exception as e:
                self.fail(
                    f"There was an issue processing your function {fname}:\n"
                    "{e}"
                )
        
        print(f"Script parsed successfully and {len(self.func_names)} functions were found.")
    
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
    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_odd_numbers(self):
        """Check your script works for odd height triangles"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.shebang:
            self.fail(
                f"Your script does not begin with a correct shebang."
            )
        tests = [
            (["X", "5"],"X\nXX\nXXX\nXX\nX\n"),
            (["#", "3"],"#\n##\n#\n"),
            (["&", "1"],"&\n"),
        ]
        for input, expected in tests:
            command = [self.submission] + input
            result = subprocess.run(
                command,
                text=True,
                capture_output=True
            )
            if result.returncode != 0:
                self.fail(
                    "Your script returned a non-zero exit code"
                )
            out_chars = set("".join(result.stdout.split()))
            if len(out_chars) != 1:
                self.fail(
                    "Your script should produce a triangle composed only of the specified character.\n"
                    f"Instead, your script output including {len(out_chars)} different characters: {out_chars}\n"
                )
            if result.stdout != expected:
                self.fail(
                    "Your script's output did not match the expected output for an odd height triangle."
                    f"Yours:\n{result.stdout}\nExpected:{expected}"
                )
        print("Your script produced odd height triangles that match the expected output")
        

    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_even_numbers(self):
        """Check your script works for even height triangles"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.shebang:
            self.fail(
                f"Your script does not begin with a correct shebang."
            )
        tests = [
            (["X", "6"],"X\nXX\nXXX\nXXX\nXX\nX\n"),
            (["#", "4"],"#\n##\n##\n#\n"),
            (["&", "2"],"&\n&\n"),
        ]
        for input, expected in tests:
            command = [self.submission] + input
            result = subprocess.run(
                command,
                text=True,
                capture_output=True
            )
            if result.returncode != 0:
                self.fail(
                    "Your script returned a non-zero exit code"
                )
            out_chars = set("".join(result.stdout.split()))
            if len(out_chars) != 1:
                self.fail(
                    "Your script should produce a triangle composed only of the specified character.\n"
                    f"Instead, your script output including {len(out_chars)} different characters: {out_chars}\n"
                )
            if result.stdout != expected:
                self.fail(
                    "Your script's output did not match the expected output for an odd height triangle."
                    f"Yours:\n{result.stdout}\nExpected:{expected}"
                )
        print("Your script produced odd height triangles that match the expected output")


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
        for fname, f in zip(self.func_names, self.func_bodies):
            try:
                eval(f)
            except Exception as e:
                self.fail(
                    f"There was an issue processing your function {fname}:\n"
                    f"{e}"
                )
            docstring = eval(f"{fname}.__doc__")
            if not docstring:
                self.fail(
                    f"No docstring found for your function {fname}"
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
        for fname, f in zip(self.func_names, self.func_bodies):
            try:
                eval(f)
            except Exception as e:
                self.fail(
                    f"There was an issue processing your function {fname}:\n"
                    f"{e}"
                )
            annots = eval(f"{fname}.__annotations__")
            if not annots:
                self.fail(
                    f"No annotations found for your function {fname}"
                )
        print("looks like annotations were used. The quality of your annotations will be assessed manually.")
