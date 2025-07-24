import unittest
from pathlib import Path
from tempfile import mkdtemp
import shutil
import subprocess
import time

from gradescope_utils.autograder_utils.decorators import (
    weight,
    number,
    visibility,
    leaderboard,
    partial_credit
)
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import PointCounter

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "homolog_identify.sh"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"
DATA_DIR = "/autograder/biol7200-autograders/data/"

Q_NUM = 1

POINT_NUM = PointCounter(0)

EXPECTED_OUTPUTS = {
    # order of homolog counts:
    # "Escherichia_coli_K12.fna"
    # "Pseudomonas_aeruginosa_UCBPP-PA14.fna",
    # "Vibrio_cholerae_N16961.fna",
    # "Wolbachia.fna"
    (27, 38, 34, 2): "correct",
    (27, 38, 25, 2): [1],
    (27, 38, 35, 2): [1, 2],
    (27, 38, 42, 2): [1, 2, 3],
    (115, 179, 125, 5): [4],
    (115, 179, 152, 5): [1, 2, 3, 4],
    (27, 38, 46, 2): [1, 2, 3, 5],
    (115, 179, 167, 5): [1, 2, 3, 4, 5],
    (113, 179, 124, 2): [6],
    (113, 179, 93, 2): [1, 6],
    (113, 179, 108, 2): [1, 3, 6],
    (113, 179, 151, 2): [1, 2, 3, 6],
    (113, 179, 126, 2): [1, 2, 6],
    (113, 179, 167, 2): [1, 2, 3, 5, 6],
    (113, 179, 113, 2): [1, 3, 5, 6],
    (113, 179, 97, 2): [1, 5, 6],
}

PENALTIES = {
    1: 5, # Don't check sequence ID matches
    2: 0, # Don't use `break` to stop checking hits
    3: 0, # Don't check feature orientation matches hit orientation
    4: 10, # Don't keep only unique lines
    5: 5, # Don't check all combinations of start and stop
    6: 5, # Don't sort before uniq
}

ISSUES = {
    1: "Don't check sequence ID matches",
    2: "Don't use `break` to stop checking hits",
    3: "Don't check feature orientation matches hit orientation",
    4: "Don't keep only unique lines",
    5: "Don't check all combinations of start and stop",
    6: "Don't sort before uniq"
}

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = mkdtemp()
        cls.input_files = [
            "HK_domain.faa",
            "Escherichia_coli_K12.fna",
            "Escherichia_coli_K12.bed",
            "Pseudomonas_aeruginosa_UCBPP-PA14.fna",
            "Pseudomonas_aeruginosa_UCBPP-PA14.bed",
            "Vibrio_cholerae_N16961.fna",
            "Vibrio_cholerae_N16961.bed",
            "Wolbachia.fna",
            "Wolbachia.bed"
        ]
        for file in cls.input_files:
            shutil.copy(f"{DATA_DIR}{file}", f"{cls.dir}/")
        
        if not Path(SCRIPT_PATH).exists():
            cls.submitted = False
            return cls
        cls.submitted = True
        cls.outfiles = {}
        cls.results = {}
        cls.counts = {}
        cls.run_time = 999_999_999
        cls.zero_exit = True
        shutil.copy(SCRIPT_PATH, cls.dir)
        Path(f"{cls.dir}/{SOLUTION_SCRIPT}").chmod(0o777)
        start = time.perf_counter()
        for assembly in [
            "Escherichia_coli_K12.fna",
            "Pseudomonas_aeruginosa_UCBPP-PA14.fna",
            "Vibrio_cholerae_N16961.fna",
            "Wolbachia.fna"
        ]:
            bed = assembly.replace(".fna", ".bed")
            outfile = assembly.replace("fna", "txt")
            cls.outfiles[assembly.replace(".fna", "")] = Path(outfile)
            command = [
                f"./{SOLUTION_SCRIPT}",
                "HK_domain.faa",
                assembly,
                bed,
                outfile
            ]
            result = subprocess.run(
                command,
                text=True,
                capture_output=True,
                cwd=cls.dir
            )
            cls.results[assembly.replace(".fna", "")] = result
            if result.returncode != 0:
                cls.zero_exit = False
            with open(outfile) as f:
                lines = len([i for i in f])
            cls.counts[assembly.replace(".fna", "")] = lines
        end = time.perf_counter()
        cls.run_time = int(end-start)

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
    def test_exit_codes(self):
        """Check script ran without error"""
        if not self.zero_exit:
            self.fail("Your script exited with a non-zero exit code.")
        print("Your script ran successfully.")

    @weight(0)
    @leaderboard(column_name="run time", sort_order="asc")
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_run_time(self, set_leaderboard_value=None):
        """Check script run time for leaderboard"""
        if not self.zero_exit:
            self.fail("Your script exited with a non-zero exit code.")
        set_leaderboard_value = self.run_time
        print(f"Your script took {self.run_time}s to run on all four species.")



    @partial_credit(40)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_result_correct(self, set_score=None):
        """Check script identifies correct number of homologs"""
        if not self.zero_exit:
            self.fail("Your script exited with a non-zero exit code.")
        
        counts = tuple(
            self.counts[species] for species in [
                "Escherichia_coli_K12"
                "Pseudomonas_aeruginosa_UCBPP-PA14",
                "Vibrio_cholerae_N16961",
                "Wolbachia"
            ]
        )
        if counts not in EXPECTED_OUTPUTS:
            print(
                "Your script has issues that could not be diagnosed automatically by the autograder."
            )
            self.fail()
        result = EXPECTED_OUTPUTS[counts]
        if result == "correct":
            print("Your script identified the correct number of homologs for each organism.")
            set_score = 40
        else:
            print(
                f"Your script has at least {len(result)} issues "
                "that prevent it from identifying the correct number of homology"
            )
            penalty = sum([PENALTIES[i] for i in result])
            set_score = 40 - penalty
            self.fail()

    @visibility("hidden")
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_result_correct(self):
        """Indicate identified issues to TAs"""
        if not self.zero_exit:
            self.fail("Your script exited with a non-zero exit code.")
        
        counts = tuple(
            self.counts[species] for species in [
                "Escherichia_coli_K12"
                "Pseudomonas_aeruginosa_UCBPP-PA14",
                "Vibrio_cholerae_N16961",
                "Wolbachia"
            ]
        )
        if counts not in EXPECTED_OUTPUTS:
            print(
                "The script has issues that could not be diagnosed automatically by the autograder."
            )
            self.fail()
        result = EXPECTED_OUTPUTS[counts]
        if result == "correct":
            print("The script identified the correct number of homologs for each organism.")

        else:
            for iss in result:
                print(ISSUES[iss])
            self.fail()
