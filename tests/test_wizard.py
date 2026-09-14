import unittest
import subprocess
from pathlib import Path
from gradescope_utils.autograder_utils.decorators import weight, number
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import PointCounter

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "wizard.sh"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"

Q_NUM = 3
POINT_NUM = PointCounter(0)

class TestFiles(unittest.TestCase):
    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM}")
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

class TestVariables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.submitted = True
        if not Path(SCRIPT_PATH).exists():
            cls.submitted = False
            return cls
    
    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_wizard_set(self):
        """Check wizard variable is set"""
        if not self.submitted:
            self.fail("No script was submitted")
        command = f'source {SCRIPT_PATH}; if [[ -z "$wizard" ]]; then exit 1; else exit 0; fi'
        result = subprocess.call(command, shell=True, executable="/bin/bash", text=True)
        if result != 0:
            self.fail('The wizard variable is not set properly in your script')
        print('The wizard variable is set')

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_wizard_value_correct(self):
        """Check wizard variable has the right value"""
        if not self.submitted:
            self.fail("No script was submitted")
        command = f'source {SCRIPT_PATH}; echo "$wizard"'
        result = subprocess.run(command, shell=True, executable="/bin/bash", text=True, capture_output=True).stdout.strip()
        expected = "Gandalf the Grey"
        self.assertEqual(
            result,
            expected,
            f'The value assigned to the wizard variable is not correct. We expected {expected}, but found "{result}"')
        print('The wizard variable has the correct value')


class TestAliases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.submitted = True
        if not Path(SCRIPT_PATH).exists():
            cls.submitted = False
            return cls
    
    
    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_view_wizard_set(self):
        """Check view_wizard alias is set"""
        if not self.submitted:
            self.fail("No script was submitted")
        command = f'source {SCRIPT_PATH}; if alias view_wizard >/dev/null 2>&1; then exit 0; else exit 1; fi'
        result = subprocess.call(command, shell=True, executable="/bin/bash", text=True)
        if result != 0:
            self.fail('The view_wizard alias is not set properly in your script')
        print('The view_wizard alias is set')

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_view_wizard_alias_correct(self):
        """Check view_wizard alias works as expected"""
        if not self.submitted:
            self.fail("No script was submitted")
        command = f'source {SCRIPT_PATH}; if alias view_wizard >/dev/null 2>&1; then grep -Po "(?<=view_wizard=).+" {SCRIPT_PATH}; exit 0; else exit 1; fi'
        alias = subprocess.run(command, capture_output=True, shell=True, executable="/bin/bash", text=True).stdout.strip('"\n ').replace("'", "")
        if len(alias) == 0:
            self.fail("We were not able to process your alias. Please notify Professor Collins so he can diagnose the issue")
        # get wizard value
        command = f'source {SCRIPT_PATH}; echo "$wizard"'
        wizard = subprocess.run(command, shell=True, executable="/bin/bash", text=True, capture_output=True).stdout.strip()
        # get alias output
        result = subprocess.run(f"source {SCRIPT_PATH}; {alias}", capture_output=True, shell=True, executable="/bin/bash", text=True).stdout.strip()
        self.assertEqual(
            result,
            wizard,
            f'The view_wizard alias is not set properly in your script. We expected running the alias to produce your wizard variable contents: {wizard}, but it produced "{result} for your alias "{alias}"')
        print('The wizard alias works as expected')
