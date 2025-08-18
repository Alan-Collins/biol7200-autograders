import unittest
from pathlib import Path
from tempfile import mkdtemp
import shutil
import subprocess
import re
import ast

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
        cls.code = Path(f"{cls.dir}/{SOLUTION_SCRIPT}").read_text()
        try:
            cls.tree = ast.parse(cls.code)
            cls.baseline_code = []
            cls.func_bodies = []
            cls.def_lines = []
            cls.func_names = []
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
                    func_lines.append(line)
                    cls.def_lines.append(line)
                    cls.func_names.append(line.split()[1].split("(")[0])
                    func_found = True
                elif line.startswith("#") or line.startswith("import") or line.strip() == "":
                    continue
                else:
                    cls.baseline_code.append(line)
            cls.imported = True
        except:
            cls.imported = False
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
