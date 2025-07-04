import unittest
import subprocess
from gradescope_utils.autograder_utils.decorators import weight
from gradescope_utils.autograder_utils.files import check_submitted_files

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "q2.sh"

class TestFiles(unittest.TestCase):
    @weight(2)
    def test_submitted_files(self):
        """Check submitted files"""
        missing_files = check_submitted_files([f'{SOLUTION_SCRIPT}'])
        for path in missing_files:
            print(f'Missing {path}')
        self.assertEqual(len(missing_files), 0, 'Missing script, follow instructions carefully')
        print('Script submitted successfully')

class TestVariables(unittest.TestCase):
    @weight(2)
    def test_wizard_set(self):
        """check wizard variable is set"""
        command = f'source {SUBMISSION_PATH}{SOLUTION_SCRIPT}; if [[ -z "$wizard" ]]; then exit 1; else exit 0; fi'
        result = subprocess.call(command, shell=True, executable="/bin/bash", text=True)
        self.assertEqual(result, 0, 'The wizard variable is not set properly in your script')
        print('The wizard variable is set')

    @weight(2)
    def test_wizard_value_correct(self):
        """check wizard variable has the right value"""
        command = f'source {SUBMISSION_PATH}{SOLUTION_SCRIPT}; echo "$wizard"; if [[ "$wizard" == "Gandalf the Grey" ]]; then exit 0; else exit 1; fi'
        result = subprocess.run(command, shell=True, executable="/bin/bash", text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, f'The value assigned to the wizard variable is not correct. We expected "Gandalf the Grey", but found "{result.stdout}"')
        print('The wizard variable has the correct value')


class TestAliases(unittest.TestCase):
    @weight(2)
    def test_view_wizard_set(self):
        """check view_wizard alias is set"""
        command = f'source {SUBMISSION_PATH}{SOLUTION_SCRIPT}; if alias view_wizard >/dev/null 2>&1; then exit 0; else exit 1; fi'
        result = subprocess.call(command, shell=True, executable="/bin/bash", text=True)
        self.assertEqual(result, 0, 'The view_wizard alias is not set properly in your script')
        print('The view_wizard alias is set')

    @weight(2)
    def test_view_wizard_alias_correct(self):
        """check view_wizard alias works as expected"""
        command = f'source {SUBMISSION_PATH}{SOLUTION_SCRIPT}; if alias view_wizard >/dev/null 2>&1; then grep -Po "(?<=view_wizard=).+" {SUBMISSION_PATH}{SOLUTION_SCRIPT}; exit 0; else exit 1; fi'
        alias = subprocess.run(command, capture_output=True, shell=True, executable="/bin/bash", text=True).stdout.strip('"\'\n ')
        if len(alias) == 0:
            self.fail("We were not able to process your alias. Please notify Professor Collins so he can diagnose the issue")
        result = subprocess.run(f"source {SUBMISSION_PATH}{SOLUTION_SCRIPT}; {alias}", capture_output=True, shell=True, executable="/bin/bash", text=True).stdout.strip()
        self.assertEqual(result, 'Gandalf the Grey', f'The view_wizard alias is not set properly in your script. We expected running the alias to produce "Gandalf the Grey", but it produced "{result} for your alias "{alias}"')
        print('The wizard alias works as expected')
