import unittest
from pathlib import Path
from tempfile import mkdtemp
import shutil
import subprocess

from gradescope_utils.autograder_utils.decorators import (
    weight,
    number,
    visibility,
)
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import PointCounter

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "homolog_identify.py"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"
DATA_DIR = "/autograder/biol7200-autograders/data/"

Q_NUM = 2

POINT_NUM = PointCounter(0)

SPECIES_LIST = [
    "Escherichia_coli_K12",
    "Pseudomonas_aeruginosa_UCBPP-PA14",
    "Vibrio_cholerae_N16961",
    "Wolbachia"
]


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
        cls.zero_exit = True
        shutil.copy(SCRIPT_PATH, cls.dir)
        Path(f"{cls.dir}/{SOLUTION_SCRIPT}").chmod(0o777)
        for assembly in [
            "Escherichia_coli_K12.fna",
            "Pseudomonas_aeruginosa_UCBPP-PA14.fna",
            "Vibrio_cholerae_N16961.fna",
            "Wolbachia.fna"
        ]:
            basename = assembly.replace(".fna", "")
            bed = basename + ".bed"
            blast = basename + "blast.txt"
            outfile = basename + ".txt"
            cls.outfiles[basename] = Path(f"{cls.dir}/{outfile}")
            blast_command = f"tblastn -query HK_domain.faa -subject {assembly} -outfmt '6 std qlen' > {blast}"
            subprocess.run(
                blast_command,
                text=True,
                capture_output=True,
                shell=True,
                cwd=cls.dir
            )
            command = [
                f"./{SOLUTION_SCRIPT}",
                blast,
                bed,
                outfile
            ]
            result = subprocess.run(
                command,
                text=True,
                capture_output=True,
                cwd=cls.dir
            )
            cls.results[basename] = result
            if result.returncode != 0:
                cls.zero_exit = False
            with open(cls.outfiles[basename]) as f:
                lines = len([i for i in f])
            cls.counts[basename] = lines

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

    @weight(20)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_result_correct(self):
        """Check script identifies correct number of homologs"""
        if not self.zero_exit:
            self.fail("Your script exited with a non-zero exit code.")
        
        counts = tuple(self.counts[species] for species in SPECIES_LIST)
        if counts == (27, 38, 34, 2):
            print("Your script identified the correct number of homologs for each organism.")
        else:
            for species, count in self.counts.items():
                print(f"{species+':':<35} {count}")
            self.fail("Your script identified the wrong number of homologs")
