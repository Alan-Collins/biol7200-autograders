import unittest
from pathlib import Path
import re
from tempfile import mkdtemp
import shutil
import subprocess

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import PointCounter


SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "find_perfect_matches.sh"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"
DATA_DIR = "/autograder/biol7200-autograders/data/"

Q_NUM = 4

POINT_NUM = PointCounter(0)