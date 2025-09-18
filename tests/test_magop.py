import unittest
from pathlib import Path
import shutil
import tempfile
import sys
import inspect
import os
import subprocess

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import PointCounter, FastaSeq, Seq

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_DIR = "magnumopus"
SOLUTION_SCRIPT = "amplicon_align.py"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"
PACKAGE_PATH = f"{SUBMISSION_PATH}{SOLUTION_DIR}"
DATA_DIR = "/autograder/biol7200-autograders/source/"

ISPCR_OUTPUT = (
    ">Pseudomonas_aeruginosa_PAO1_NC_002516.2:635141-635853 Pseudomonas aeruginosa PAO1, complete genome\n"
    "TCTCGGCGACGGTCAGCTCGACCTCGCTTTCCAGGGCCGCCAGCTTCTGCTGGTTGCGCAGGATGTCGTCGCGCAGGCGCTCGATGGCCTCGGCGTACTT"
    "CGGCTTGCTCTTCAGGACGCTGTCGACCCACTTCTCGTCGGTCTCGTGGTTCGGGAACAGGCGCAGGAAGTCGGCACGCGGCATGCGCGCGTCACGCACG"
    "CAGAGCTGCATGATGGCGCGTTCCTGGGCGCGCACGCCTTCCAGGGCGGAGCGCACGCGGGCGACCAGGGCGTCGAACTGCTTGGGCACCAGCTTGATCG"
    "GCATGAACAGCTCGGCCAGGCCGGTGAGTTCGGCGGTGGCCTGCTTGCTGCCGCGACCGTGCTTCTTCAGGGCCTTCTTGGCCTTGTCGAGCTGCTCGGA"
    "GACCGCGGTGAAACGCAGGCGGGCTTCTTCCGGATCCGGACCGCCGTCGCCTTCGTCGTCGCTGTCGCTGCTGTCGTCGCTTTCTTCTTCCTCGTCGTCC"
    "TTCTCTTTCGAGTCGGCGGAATCGTCCTTCAGGTTGACCGGCTCCACCTCTTCGGCGGGCAGGCTGCCGTCATCGGGATCGATATAGCCGCTGAGGACGT"
    "CGGAGAGGCGACCGCCTTCGGCGACGATGCGATTGTAGTCGGCCAGGATGCTGTCCACCGTGCCCGGGAACTGGGCGATGGCGCTCATCACTTCGCGGAT"
    "GCCTTCCTCGATG"
)

POSSIBLE_ALNS = {
	('CTTCTCGT-CGGTCTCGTGGTTCGGGAAC', 'CTT-TCATCCACT-TCGTTGCCCGGGAAC'),
	('CTTCTCGTC-GGTCTCGTGGTTCGGGAAC', 'CTT-TCATCCACT-TCGTTGCCCGGGAAC'),
	('CTTCTCGTCG-GTCTCGTGGTTCGGGAAC', 'CTT-TCATCCACT-TCGTTGCCCGGGAAC'),
	('CTTCTCGTCGG-TCTCGTGGTTCGGGAAC', 'CTT-TCATCCACT-TCGTTGCCCGGGAAC'),
	('CTTCTCGTCGGTC-TCGTGGTTCGGGAAC', 'CTT-TCATC-CACTTCGTTGCCCGGGAAC'),
	('CTTCTCGTCGGTC-TCGTGGTTCGGGAAC', 'CTT-TCATCC-ACTTCGTTGCCCGGGAAC'),
	('CTTCTCGTCGGTC-TCGTGGTTCGGGAAC', 'CTT-TCATCCA-CTTCGTTGCCCGGGAAC'),
	('CTTCTCGTCGGTCT-CGTGGTTCGGGAAC', 'CTT-TCATC-CACTTCGTTGCCCGGGAAC'),
	('CTTCTCGTCGGTCT-CGTGGTTCGGGAAC', 'CTT-TCATCC-ACTTCGTTGCCCGGGAAC'),
	('CTTCTCGTCGGTCT-CGTGGTTCGGGAAC', 'CTT-TCATCCA-CTTCGTTGCCCGGGAAC')
}

Q_NUM = PointCounter(0)

POINT_NUM = PointCounter(0)

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = Path(tempfile.mkdtemp())
        cls.submitted = False
        
        if "__init__.py" in os.listdir(SUBMISSION_PATH):
            cls.format = "package"
            os.mkdir(f"{SUBMISSION_PATH}magnumopus")
            for file in os.listdir(SUBMISSION_PATH):
                if file == "amplicon_align.py":
                    continue
                if file.endswith(".py"):
                    shutil.move(f"{SUBMISSION_PATH}{file}", f"{SUBMISSION_PATH}magnumopus")
        elif "magnumopus.py" in os.listdir(SUBMISSION_PATH):
            cls.format = "module"
        else:
            return cls
        cls.input_files = [
            "Pseudomonas_aeruginosa_PAO1.fna",
            "Pseudomonas_protegens_CHA0.fna",
            "rpoD.fna"
        ]
        for file in cls.input_files:
            shutil.copy(f"{DATA_DIR}{file}", f"{cls.dir}/")
        cls.submitted = True
        try: # import the package
            sys.path.append(SUBMISSION_PATH)
            import magnumopus
            cls.pkg = magnumopus
            cls.imported = True
        
        except Exception as e:
            cls.imported = False
            cls.error = e
        
        try: # run ispcr
            if not hasattr(magnumopus, "ispcr"):
                raise("magnumopus has no function 'ispcr'")
            if not inspect.isfunction(magnumopus.ispcr):
                raise("magnumopus.ispcr is not a function")
            cls.ispcr_result = magnumopus.ispcr(
                primer_file=f"{DATA_DIR}/rpoD.fna",
                assembly_file=f"{DATA_DIR}/Pseudomonas_aeruginosa_PAO1.fna",
                max_amplicon_size=2000
            )
            cls.ispcr_ran = True
        except Exception as e:
            cls.ispcr_ran = False
            cls.ispcr_error = e
        
        try: # run needleman_wunsch
            if not hasattr(magnumopus, "needleman_wunsch"):
                raise("magnumopus has no function 'needleman_wunsch'")
            if not inspect.isfunction(magnumopus.needleman_wunsch):
                raise("magnumopus.needleman_wunsch is not a function")
            cls.needleman_wunsch_result = magnumopus.needleman_wunsch(seq1, seq2, 1, -1, -1)
            cls.needleman_wunsch_ran = True
        except Exception as e:
            cls.needleman_wunsch_ran = False
            cls.error = e
        
        # try: # run step 3
        #     if not hasattr(magnumopus, "step_three"):
        #         raise("magnumopus has no function 'step_three'")
        #     if not inspect.isfunction(magnumopus.step_three):
        #         raise("magnumopus.step_three is not a function")
        #     cls.step_three_result = magnumopus.step_three(
        #         hit_pairs=Q3_INPUT,
        #         assembly_file=f"{DATA_DIR}/Vibrio_cholerae_N16961.fna"
        #     )
        #     cls.step_three_ran = True
        # except Exception as e:
        #     cls.step_three_ran = False
        #     cls.error = e

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir)

    @weight(0)
    @number(f"999.{POINT_NUM}")
    @visibility("hidden")
    def test_check_outputs(self):
        """secretly check student outputs"""
        if self.ispcr_ran:
            print("ispcr output:")
            print(self.ispcr_result)
        else:
            print("ispcr error:")
            self.ispcr_error
        print("\n\n")
        if self.needleman_wunsch_ran:
            print("needleman_wunsch output:")
            print(f"score: {self.needleman_wunsch_result[1]}")
            print("\n".join(self.needleman_wunsch_result[0]))
            if self.needleman_wunsch_result[0] in POSSIBLE_ALNS or self.needleman_wunsch_result[0][::-1] in POSSIBLE_ALNS:
                print("alignment matches expected.")
            else:
                print("alignment was not in the expected set.")
        else:
            print("needleman_wunsch error:")
            self.needleman_wunsch_error



    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_submitted_files(self):
        """Check submitted files"""
        if not self.submitted:
            self.fail(
                f'Missing your magnumopus package or module, follow instructions carefully'
            )
        print(f'magnumopus submitted successfully')
        print(f"Your submission was determined to be a {self.format}")
        if "amplicon_align.py" in os.listdir(SUBMISSION_PATH):
            print("amplicon_align.py submitted successfully.")

    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_import(self):
        """Check magnumopus can be imported"""
        if not self.submitted:
            self.fail("magnumopus was not submitted.")
        if not self.imported:
            self.fail(f"magnumopus could not be imported due to an error:\n{self.error}")
        print("magnumopus was imported successfully")
    
    @weight(0)
    @number(f"{Q_NUM.next()}.{POINT_NUM.reset(1)}")
    @visibility("visible")
    def test_ispcr_runs(self):
        """Check ispcr runs"""
        if not self.submitted:
            self.fail("magnumopus was not submitted.")
        if not self.imported:
            self.fail(f"magnumopus could not be imported due to an error:\n{self.error}")
        if not self.ispcr_ran:
            self.fail(f"ispcr failed with the error: {self.error}")
        print("ispcr ran")
    
    @weight(20)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_ispcr_output(self):
        """Check ispcr output correct"""
        if not self.submitted:
            self.fail("ispcr was not submitted.")
        if not self.imported:
            self.fail(f"ispcr could not be imported due to an error:\n{self.error}")
        if not self.ispcr_ran:
            self.fail(f"Step one failed with the error: {self.error}")
        # Check return type matches expected str
        if isinstance(self.ispcr_result, str):
            print("ispcr return type matches expectation")
        else:
            self.fail("ispcr return type is wrong")
        result = FastaSeq.from_fasta(self.ispcr_result)
        expected = FastaSeq.from_fasta(ISPCR_OUTPUT)
        if result != expected:
            self.fail(
                "ispcr output does not match expected output.\n"
                f"Your output was:\n{self.ispcr_result}"
            )
        print("ispcr output matches expected output")

    @weight(0)
    @number(f"{Q_NUM.next()}.{POINT_NUM.reset(1)}")
    @visibility("visible")
    def test_nw_runs(self):
        """Check needleman_wunsch runs"""
        if not self.submitted:
            self.fail("magnumopus was not submitted.")
        if not self.imported:
            self.fail(f"magnumopus could not be imported due to an error:\n{self.error}")
        if not self.needleman_wunsch_ran:
            self.fail(f"needleman_wunsch failed with the error: {self.error}")
        print("needleman_wunsch ran")
