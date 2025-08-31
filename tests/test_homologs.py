import unittest
from pathlib import Path
import re
from tempfile import mkdtemp
import shutil
import subprocess

from gradescope_utils.autograder_utils.decorators import weight, number, visibility

from utils import PointCounter

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "git_repo.txt"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"
DATA_DIR = "/autograder/biol7200-autograders/data/"

Q_NUM = 3

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
            cls.homolog_file = Path(f"{cls.dir}/{repo_name}/find_homologs.sh")
            cls.homolog_file.chmod(0o777)
            cls.repo_cloned = True
        except:
            cls.repo_cloned = False
            cls.homolog_file = Path("/not_submitted")
        
        cls.input_files = [
            "HK_domain.faa",
            "Escherichia_coli_K12.fna",
            "Pseudomonas_aeruginosa_UCBPP-PA14.fna",
            "Vibrio_cholerae_N16961.fna",
            "Wolbachia.fna"
        ]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir)

    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("on_fail")
    def test_submitted_files(self):
        """Check submitted files"""
        if not self.homolog_file.exists():
            self.fail(
                "Unable to get the identify_homologs.sh script from a git repo. "
                "follow the instructions carefully."
            )
        print(f"identify_homologs.sh script submitted successfully")
    

    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_runs(self):
        """Check script runs without error"""
        if not self.homolog_file.exists():
            self.fail(
                "Unable to get the identify_homologs.sh script from a git repo. "
                "follow the instructions carefully."
            )
        dir = mkdtemp()
        for file in self.input_files:
            shutil.copy(f"{DATA_DIR}{file}", f"{dir}/")
        command = [
            self.homolog_file,
            f"{dir}/HK_domain.faa",
            f"{dir}/Wolbachia.fna",
            f"{dir}/out.txt"
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            cwd=dir,
            text=True
        )
        if result.returncode != 0:
            self.fail("Your script exited with a non-zero exit code.")

        task_regex = re.compile(r"^[^\#]*tblastn-fast")
        with open(self.homolog_file) as f:
            for line in f:
                if re.match(task_regex, line):
                    print(
                        "You appear to be using -task tblastn-fast. "
                        "Note that you will get fewer matches that meet our criteria with "
                        "that setting. It also won't speed things up much."
                    )

        print(f"Your script executed successfully")

    
    @weight(15)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_produces_expected_outputs(self):
        """Check script produces expected outputs"""
        if not self.homolog_file.exists():
            self.fail(
                "Unable to get the identify_homologs.sh script from a git repo. "
                "follow the instructions carefully."
            )
        dir = mkdtemp()
        for file in self.input_files:
            shutil.copy(f"{DATA_DIR}{file}", f"{dir}/")
        for assembly in [
            "Escherichia_coli_K12.fna",
            "Pseudomonas_aeruginosa_UCBPP-PA14.fna",
            "Vibrio_cholerae_N16961.fna",
            "Wolbachia.fna"
        ]:
            try:
                command = [
                    self.homolog_file,
                    f"{dir}/HK_domain.faa",
                    f"{dir}/{assembly}",
                    f"{dir}/out.txt"
                ]
                result = subprocess.run(
                    command,
                    capture_output=True,
                    cwd=dir,
                    text=True
                )
                if result.returncode != 0:
                    self.fail("Your script exited with a non-zero exit code.")
                try:
                    output_numbers = re.findall(r"(?<!\S)\d+(?!\S)", result.stdout)
                    if len(output_numbers) > 1:
                        self.fail(
                            "Your script's stdout appears to contain more than one number. "
                            "The stdout should only contain the number of matches"
                        )
                    count = int(output_numbers[0])
                except Exception as e:
                    self.fail(
                        "Unable to interpret the stdout as a number. "
                        "The stdout should contain the number of matches"
                    )
            except Exception as e:
                self.fail(
                    f"Error running your script:\n{e}"
                )
            with open(f"{dir}/out.txt") as f:
                lines = [i for i in f]
                if len(lines) < 2:
                    self.fail("Your script produces an output file lacking hits")
            
            if count != len(lines):
                self.fail("Your script's stdout and output file disagree about how many hits there are.")

        print(f"Your script produces outputs of the correct format.")

    
    @weight(20)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("after_due_date")
    def test_gets_right_number(self):
        """Check script identifies correct number of matches"""
        if not self.homolog_file.exists():
            self.fail(
                "Unable to get the identify_homologs.sh script from a git repo. "
                "follow the instructions carefully."
            )
        dir = mkdtemp()
        for file in self.input_files:
            shutil.copy(f"{DATA_DIR}{file}", f"{dir}/")
        all_results = {}
        for assembly in [
            "Escherichia_coli_K12.fna",
            "Pseudomonas_aeruginosa_UCBPP-PA14.fna",
            "Vibrio_cholerae_N16961.fna",
            "Wolbachia.fna"
        ]:
            try:
                command = [
                    self.homolog_file,
                    f"{dir}/HK_domain.faa",
                    f"{dir}/{assembly}",
                    f"{dir}/{assembly[:-4]}_out.txt"
                ]
                result = subprocess.run(
                    command,
                    capture_output=True,
                    cwd=dir,
                    text=True
                )
                all_results[assembly] = result
                if result.returncode != 0:
                    self.fail("Your script exited with a non-zero exit code.")
                try:
                    output_numbers = re.findall(r"(?<!\S)\d+(?!\S)", result.stdout)
                    if len(output_numbers) > 1:
                        self.fail(
                            "Your script's stdout appears to contain more than one number. "
                            "The stdout should only contain the number of matches"
                        )
                    count = int(output_numbers[0])
                except:
                    self.fail(
                        "Unable to interpret the stdout as a number. "
                        "The stdout should contain the number of matches"
                    )
                with open(f"{dir}/{assembly[:-4]}_out.txt") as f:
                    lines = [i for i in f]
                    if len(lines) < 2:
                        self.fail("Your script produces an output file lacking hits")
                
                if count != len(lines):
                    self.fail("Your script's stdout and output file disagree about how many hits there are.")
            except Exception as e:
                self.fail(
                    f"Error running your script:\n{e}"
                )
        
        tblastn_expected = {
            "Escherichia_coli_K12.fna": 116,
            "Vibrio_cholerae_N16961.fna": 125,
            "Pseudomonas_aeruginosa_UCBPP-PA14.fna": 250,
            "Wolbachia.fna": 5
        }

        tblastn_fast_expected = {
            "Escherichia_coli_K12.fna": 102,
            "Vibrio_cholerae_N16961.fna": 107,
            "Pseudomonas_aeruginosa_UCBPP-PA14.fna": 196,
            "Wolbachia.fna": 4
        }

        task_regex = re.compile(r"^[^\#]*tblastn-fast")
        task = "slow"
        with open(self.homolog_file) as f:
            for line in f:
                if re.match(task_regex, line):
                    task = "fast"
        
        fail = False
        print(f"Performance using -task {'tblastn' if task == 'slow' else 'tblastn-fast'}")
        for ass, result in all_results.items():
            if task == "fast":
                expected = tblastn_fast_expected[ass]
            else:
                expected = tblastn_expected[ass]
            count = int(re.findall(r"(?<!\S)\d+(?!\S)", result.stdout)[0])
            if count != expected:
                fail = True
            print(f"Yours: {count} expected: {expected} for {ass}")

        if fail:
            self.fail("Your script identifies the wrong number of matches.")        

        print("Your script identifies the correct number of matches.")
