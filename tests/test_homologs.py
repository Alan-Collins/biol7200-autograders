import unittest
from pathlib import Path
from tempfile import mkdtemp
import shutil
import subprocess
import time
import re

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
    (0, 0, 0, 0): [7]
}

PENALTIES = {
    1: 5, # Don't check sequence ID matches
    2: 0, # Don't use `break` to stop checking hits
    3: 0, # Don't check feature orientation matches hit orientation
    4: 10, # Don't keep only unique lines
    5: 5, # Don't check all combinations of start and stop
    6: 5, # Don't sort before uniq
    7: 40 # Catastrophic failure
}

ISSUES = {
    1: "Didn't check sequence ID matches",
    2: "Didn't use `break` to stop checking hits",
    3: "Didn't check feature orientation matches hit orientation",
    4: "Didn't keep only unique lines",
    5: "Didn't check all combinations of start and stop",
    6: "Didn't sort before uniq",
    7: "Didn't identify any homologs for any species"
}

SPECIES_LIST = [
    "Escherichia_coli_K12",
    "Pseudomonas_aeruginosa_UCBPP-PA14",
    "Vibrio_cholerae_N16961",
    "Wolbachia"
]

LEADERBOARD_NULL = 999_999_999

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
        cls.run_time = LEADERBOARD_NULL
        cls.zero_exit = True
        shutil.copy(SCRIPT_PATH, cls.dir)
        Path(f"{cls.dir}/{SOLUTION_SCRIPT}").chmod(0o777)
        pattern = re.compile(r"\#\![ ]?/(?:usr/(?=bin(?:/env)?))?bin/(?:(?<=usr/bin/)env )?bash")
        cls.shebang = True
        with open(SCRIPT_PATH) as f:
            first_line = f.readline()
        if not re.match(pattern, first_line):
            cls.shebang = False
        cls.stderrs = []
        start = time.perf_counter()
        for assembly in [
            "Escherichia_coli_K12.fna",
            "Pseudomonas_aeruginosa_UCBPP-PA14.fna",
            "Vibrio_cholerae_N16961.fna",
            "Wolbachia.fna"
        ]:
            basename = assembly.replace(".fna", "")
            bed = basename + ".bed"
            outfile = basename + ".txt"
            cls.outfiles[basename] = Path(f"{cls.dir}/{outfile}")
            command = [
                f"./{SOLUTION_SCRIPT}",
                "HK_domain.faa",
                assembly,
                bed,
                outfile
            ]
            try:
                result = subprocess.run(
                    command,
                    text=True,
                    capture_output=True,
                    cwd=cls.dir
                )
            except Exception as e:
                cls.stderrs = [e]
                cls.stderr_trimmed = e
                return cls
            cls.results[basename] = result
            if result.returncode != 0 or result.stderr.strip() != "":
                cls.zero_exit = False
                cls.stderrs.append(result.stderr)
            if cls.outfiles[basename].exists():
                with open(cls.outfiles[basename]) as f:
                    lines = len([i for i in f])
            else:
                lines = 0
            cls.counts[basename] = lines
        end = time.perf_counter()
        cls.run_time = int(end-start)
        cls.stderr_trimmed = []
        if len(cls.stderrs) != 0:
            for line in cls.stderrs[0].splitlines():
                if line in cls.stderr_trimmed:
                    continue
                cls.stderr_trimmed.append(line)
        cls.stderr_trimmed = "\n".join(cls.stderr_trimmed)
        

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
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.shebang:
            self.fail(
                "Your script is either lacking a shebang or the shebang is not correct."
            )
        if not self.zero_exit or len(self.stderrs) != 0:
            self.fail(
                "Your script exited an error:\n"
                f"{self.stderr_trimmed}"
                )
        print("Your script ran successfully.")

    @leaderboard(column_name="run time", sort_order="asc")
    def test_run_time_leaderboard(self, set_leaderboard_value=None):
        """Set script run time for leaderboard"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.shebang:
            self.fail(
                "Your script is either lacking a shebang or the shebang is not correct."
            )
        if not self.zero_exit or len(self.stderrs) != 0:
            self.fail(
                "Your script exited an error:\n"
                f"{self.stderr_trimmed}"
                )
        counts = tuple(self.counts[species] for species in SPECIES_LIST)
        if EXPECTED_OUTPUTS.get(counts, None) != "correct":
            self.fail()
        else:
            set_leaderboard_value(self.run_time)


    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_run_time(self):
        """Check script run time for leaderboard"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.shebang:
            self.fail(
                "Your script is either lacking a shebang or the shebang is not correct."
            )
        if not self.zero_exit or len(self.stderrs) != 0:
            self.fail(
                "Your script exited an error:\n"
                f"{self.stderr_trimmed}"
                )
        print(f"Your script took {self.run_time}s to run on all four species.")
        counts = tuple(self.counts[species] for species in SPECIES_LIST)
        if EXPECTED_OUTPUTS.get(counts, None) != "correct":
            self.fail("Only submissions that identify the correct number of homologs are added to the leaderboard.")


    @partial_credit(40)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_result_correct(self, set_score=None):
        """Check script identifies correct number of homologs"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.zero_exit or len(self.stderrs) != 0:
            self.fail(
                "Your script exited an error:\n"
                f"{self.stderr_trimmed}"
                )
        
        counts = tuple(
            self.counts[species] for species in [
                "Escherichia_coli_K12",
                "Pseudomonas_aeruginosa_UCBPP-PA14",
                "Vibrio_cholerae_N16961",
                "Wolbachia"
            ]
        )
        print("The number of identified homologs was:")
        for species, count in self.counts.items():
            print(f"{species+':':<35} {count}")
        if counts not in EXPECTED_OUTPUTS:
            print(
                "Your script has issues that could not be diagnosed automatically by the autograder."
            )
            set_score(0)
            self.fail()
        result = EXPECTED_OUTPUTS[counts]
        if result == "correct":
            print("Your script identified the correct number of homologs for each organism.")
            set_score(40)
        else:
            penalty = sum([PENALTIES[i] for i in result])
            set_score(40 - penalty)
            self.fail(
                f"Your script has at least {len(result)} issues "
                "that prevent it from identifying the correct number of homologs"
            )


    @visibility("after_due_date")
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_result_correct_tas(self):
        """Indicate identified issues"""
        if not self.submitted:
            self.fail("No script was submitted")
        if not self.zero_exit:
            self.fail("Your script exited with a non-zero exit code.")
        print("The number of identified homologs was:")
        expected = {
            "Escherichia_coli_K12": 27,
            "Pseudomonas_aeruginosa_UCBPP-PA14": 38,
            "Vibrio_cholerae_N16961": 34,
            "Wolbachia": 2
        }
        print(f"{'assembly:':<35}\t{'found':<10}\texpected")
        for species, count in self.counts.items():
            ex = expected[species]
            print(f"{species+':':<35}\t{count:<10}\t{ex}")
        counts = tuple(self.counts[species] for species in SPECIES_LIST)
        if counts not in EXPECTED_OUTPUTS:
            self.fail("The script has issues that could not be diagnosed automatically by the autograder.")
        result = EXPECTED_OUTPUTS[counts]
        
        if result == "correct":
            print("\nThe script identified the correct number of homologs for each organism.")
        else:
            print("\nThe issues with the script likely include:")
            for iss in result:
                print(ISSUES[iss])
            if len(self.stderrs) != 0:
                error = self.stderr_trimmed
            else:
                error = ""
            self.fail(error)
