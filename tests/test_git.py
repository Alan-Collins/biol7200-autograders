import unittest
from pathlib import Path
import re
from tempfile import mkdtemp
import shutil
import subprocess

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "git_repo.txt.txt"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"

Q_NUM = 2

class PointCounter():
    def __init__(self, start=0):
        self._setup(start)
    
    def _setup(self, start=0):
        self._counter = start
    
    def reset(self, start=0) -> int:
        self._setup(start)
        return self._counter

    def next(self) -> int:
        self._counter += 1
        return self._counter

    def __hash__(self):
        return hash(self._counter)
    
    def __eq__(self, value):
        return self._counter == value

    def __str__(self):
        return str(self._counter)



POINT_NUM = PointCounter(0)

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = mkdtemp()
        raise NotImplemented

    @classmethod
    def tearDownClass(cls):
        pass

    @weight(0)
    @number(f"{Q_NUM}.{next(POINT_NUM)}")
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
