import unittest
from pathlib import Path
from tempfile import mkdtemp
import shutil
import subprocess

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "git_repo.txt"
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
        try:
            with open(SCRIPT_PATH) as f:
                repo = f.read().strip()
            repo_name = repo.split("/")[-1]
            if repo_name.endswith(".git"):
                repo_name = repo_name[:-4]
            result = subprocess.run(
                ["git", "clone", repo],
                cwd=cls.dir,
                capture_output=True
            )
            if result.returncode != 0:
                raise
            result = subprocess.run(
                ["git", "log"],
                cwd=f"{cls.dir}/{repo_name}",
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise
            cls.git_log = result.stdout
            result = subprocess.run(
                ["git", "log", "--merges"],
                cwd=f"{cls.dir}/{repo_name}",
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise
            cls.merges = result.stdout
            cls.homolog_file = Path(f"{cls.dir}/{repo_name}/find_homologs.sh")
            cls.biol_file = Path(f"{cls.dir}/{repo_name}/BIOL7200")
            cls.repo_cloned = True
        except:
            cls.repo_cloned = False

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
    
    @weight(6)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_repo_cloneable(self):
        """Check repo exists and cloned without error"""
        if not self.repo_cloned:
            self.fail(
                "Unable to clone the repo. Confirm that you provided the right URL, "
                "the repo is public, and that you are able to clone it."
            )
        print("Repo cloned successfully.")

    @weight(6)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_repo_has_commits(self):
        """Check commits were made to repo during development"""
        if not self.repo_cloned:
            self.fail(
                "Unable to clone the repo. Confirm that you provided the right URL, "
                "the repo is public, and that you are able to clone it."
            )
        commit_count = 0
        for line in self.git_log.split("\n"):
            if line.startswith("commit"):
                commit_count += 1
        if commit_count < 4:
            self.fail("Your git repo does not contain enough commits to have completed the assigned steps.")
        print("Your repo has commits that track your activities.")

    @weight(6)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_repo_has_required_files(self):
        """Check repo contains the required files"""
        if not self.repo_cloned:
            self.fail(
                "Unable to clone the repo. Confirm that you provided the right URL, "
                "the repo is public, and that you are able to clone it."
            )
        if not self.biol_file.exists() or not self.homolog_file.exists():
            self.fail("Your repo is missing one or more required files. Check the instructions.")
        print("Repo contains the required files.")
    
    @weight(6)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_repo_has_merge(self):
        """Check repo includes merge of branches"""
        if not self.repo_cloned:
            self.fail(
                "Unable to clone the repo. Confirm that you provided the right URL, "
                "the repo is public, and that you are able to clone it."
            )
        if len(self.merges.strip()) == 0:
            self.fail(
                "No merge can be found in the history of your git repo. "
                "Make sure you followed the instructions as you might have accidentally "
                "fast-forwarded your main branch instead of merged."
            )
        print("Your git repo has a merge.")
    
    @weight(6)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_repo_has_revert(self):
        """Check repo includes a reverted commit"""
        if not self.repo_cloned:
            self.fail(
                "Unable to clone the repo. Confirm that you provided the right URL, "
                "the repo is public, and that you are able to clone it."
            )
        revert_found = False
        for line in self.git_log.split("\n"):
            if "This reverts commit" in line:
                revert_found = True
        if not revert_found:
            self.fail(
                "No reverted commit was identified. "
                "Make sure you leave the default commit message in place when performing the reversion.")
        print("Your git repo has a reverted commit.")
