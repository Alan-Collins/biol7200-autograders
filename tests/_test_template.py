import unittest

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "<script name>"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"

Q_NUM = 4

class PointCounter():
    def __init__(self, start=0):
        self._setup(start)
    
    def _setup(self, start=0):
        self._counter = (i for i in range(start, 1000))
    
    def __iter__(self):
        return self._counter
    
    def __next__(self):
        try:
            return next(self._counter)
        except:
            raise StopIteration
    
    def reset(self, start=0) -> int:
        self._setup(start)
        return next(self._counter)

POINT_NUM = PointCounter(0)

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

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
