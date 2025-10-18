import unittest
from pathlib import Path
import shutil
import tempfile
import sys
import inspect
import os
import subprocess

from gradescope_utils.autograder_utils.decorators import weight, number, visibility, partial_credit
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import PointCounter, FastaSeq, Seq, recursive_type_str

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_DIR = "magnumopus"
SOLUTION_SCRIPT = "amplicon_align.py"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"
PACKAGE_PATH = f"{SUBMISSION_PATH}{SOLUTION_DIR}"
DATA_DIR = "/autograder/biol7200-autograders/data/"

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
            seq1 = "CTTCTCGTCGGTCTCGTGGTTCGGGAAC"
            seq2 = "CTTTCATCCACTTCGTTGCCCGGGAAC"
            cls.needleman_wunsch_result = magnumopus.needleman_wunsch(seq1, seq2, 1, -1, -1)
            cls.needleman_wunsch_ran = True
        except Exception as e:
            cls.needleman_wunsch_ran = False
            cls.needleman_wunsch_error = e
        
        # Store help message of amplicon_align.py
        if "amplicon_align.py" not in os.listdir(SUBMISSION_PATH):
            cls.amplicon_align_ran = False
            cls.amplicon_align_error = "File not found"
            return cls

        Path(f"{SUBMISSION_PATH}amplicon_align.py").chmod(0o777)
        
        command = [f"{SUBMISSION_PATH}amplicon_align.py", "-h"]
                   
        cls.aa_help_result = subprocess.run(
            command,
            text=True,
            capture_output=True
        )

        # Run amplicon_align.py
        command = [
            f"{SUBMISSION_PATH}amplicon_align.py",
            "-1", "Pseudomonas_aeruginosa_PAO1.fna",
            "-2", "Pseudomonas_protegens_CHA0.fna",
            "-p", "rpoD.fna",
            "-m", "2000",
            "--match", "1",
            "--mismatch=-1",
            "--gap=-1"
        ]
                   
        cls.aa_result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            cwd=cls.dir
        )

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
            print(self.ispcr_error)
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
            print(self.needleman_wunsch_error)



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
            self.fail(f"ispcr failed with the error: {self.ispcr_error}")
        print("ispcr ran")
    
    @weight(20)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_ispcr_output(self):
        """Check ispcr output correct"""
        if not self.submitted:
            self.fail("magnumopus was not submitted.")
        if not self.imported:
            self.fail(f"magnumopus could not be imported due to an error:\n{self.error}")
        if not self.ispcr_ran:
            self.fail(f"ispcr failed with the error: {self.ispcr_error}")
        # Check return type matches expected str
        if isinstance(self.ispcr_result, str):
            print("ispcr return type matches expectation")
        else:
            actual = recursive_type_str(self.ispcr_result)
            self.fail(
                "ispcr return type is wrong.\n"
                "Expected: str\n"
                f"Found: {actual}"
            )
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
            self.fail(f"needleman_wunsch failed with the error: {self.needleman_wunsch_error}")
        print("needleman_wunsch ran")

    
    @partial_credit(50)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_nw_output(self, set_score=None):
        """Check needleman-wunsch output correct"""
        if not self.submitted:
            self.fail("magnumopus was not submitted.")
        if not self.imported:
            self.fail(f"magnumopus could not be imported due to an error:\n{self.error}")
        if not self.needleman_wunsch_ran:
            self.fail(f"needleman_wunsch failed with the error: {self.error}")
        score = 50
        # Check return type matches expected str
        expected_return_type = "tuple[tuple[str,str],int]"
        actual_return_type = recursive_type_str(self.needleman_wunsch_result)
        if actual_return_type == expected_return_type:
            print("needleman_wunsch return type matches expectation")
        else:
            self.fail(
                "needleman_wunsch return type is wrong.\n"
                f"Expected: {expected_return_type}\n"
                f"Found: {actual_return_type}"
            )
        if self.needleman_wunsch_result[0] not in POSSIBLE_ALNS and self.needleman_wunsch_result[0][::-1] not in POSSIBLE_ALNS:
            print(
                "needleman_wunsch output does not match expected output.\n"
                f"Your output was:\n{self.needleman_wunsch_result}"
            )
            # Now diagnose why the output doesn't match
            # First check if one or both sequences were not reversed
            s1 = Seq("s1", self.needleman_wunsch_result[0][0])
            s2 = Seq("s2", self.needleman_wunsch_result[0][0])
            first = (s1.reverse(), s2)
            second = (s1, s2.reverse())
            both = (s1.reverse(), s2.reverse())
            if first in POSSIBLE_ALNS or second in POSSIBLE_ALNS:
                score -= 5
            elif both in POSSIBLE_ALNS:
                score -= 5

            # Next check if they reverse complemented instead of reversing
            first = (s1.complement(), s2)
            second = (s1, s2.complement())
            both = (s1.complement(), s2.complement())
            if first in POSSIBLE_ALNS or second in POSSIBLE_ALNS:
                score -= 5
            elif both in POSSIBLE_ALNS:
                score -= 5


            # Otherwise we'll need to diagnose this issue manually
            if score == 50:
                print("The autograder cannot automatically determine the issue(s) with your script. Your score will be adjusted during grading once we diagnose the issue(s).")
                score = 0
            else:
                # next check the alignment score
                if self.needleman_wunsch_result[1] != 11:
                    score -= 5
            

        else:
            print("needleman_wunsch output matches expected output")
        set_score(score)

    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("hidden")
    def test_nw_output_TAs(self):
        """Describe issues the autograder could diagnose for TAs"""
        if not self.submitted:
            self.fail("magnumopus was not submitted.")
        if not self.imported:
            self.fail(f"magnumopus could not be imported due to an error:\n{self.error}")
        if not self.needleman_wunsch_ran:
            self.fail(f"needleman_wunsch failed with the error: {self.error}")
        # Check return type matches expected str
        expected_return_type = "tuple[tuple[str,str],int]"
        actual_return_type = recursive_type_str(self.needleman_wunsch_result)
        if actual_return_type == expected_return_type:
            print("needleman_wunsch return type matches expectation")
        else:
            self.fail(
                "needleman_wunsch return type is wrong.\n"
                f"Expected: {expected_return_type}\n"
                f"Found: {actual_return_type}"
            )
        if self.needleman_wunsch_result[0] not in POSSIBLE_ALNS and self.needleman_wunsch_result[0][::-1] not in POSSIBLE_ALNS:
            print(
                "needleman_wunsch output does not match expected output.\n"
                f"Your output was:\n{self.needleman_wunsch_result}"
            )
            # Now diagnose why the output doesn't match
            # First check if one or both sequences were not reversed
            s1 = Seq("s1", self.needleman_wunsch_result[0][0])
            s2 = Seq("s2", self.needleman_wunsch_result[0][0])
            first = (s1.reverse(), s2)
            second = (s1, s2.reverse())
            both = (s1.reverse(), s2.reverse())
            if first in POSSIBLE_ALNS or second in POSSIBLE_ALNS:
                print("(-5) One of your sequences is backwards")
            elif both in POSSIBLE_ALNS:
                print("(-5) Both of your sequences are backwards")
            
            # Next check if they reverse complemented instead of reversing
            first = (s1.complement(), s2)
            second = (s1, s2.complement())
            both = (s1.complement(), s2.complement())
            if first in POSSIBLE_ALNS or second in POSSIBLE_ALNS:
                print("(-5) One of your sequences is reverse complemented when it should have just been reversed")
            elif both in POSSIBLE_ALNS:
                print("(-5) Both of your sequences are reverse complemented when they should have just been reversed")
            
            # Next check if they complemented but didn't reverse
            first = (s1.reverse_complement(), s2)
            second = (s1, s2.reverse_complement())
            both = (s1.reverse_complement(), s2.reverse_complement())
            if first in POSSIBLE_ALNS or second in POSSIBLE_ALNS:
                print("(-10) One of your sequences is complemented but should have been reversed")
            elif both in POSSIBLE_ALNS:
                print("(-10) Both of your sequences are complemented but should have been reversed")
            
            if self.needleman_wunsch_result[1] != 11:
                print(f"(-5) Alignment score doesn't match expected. Expected 11, got {self.needleman_wunsch_result[1]}")


        else:    
            print("needleman_wunsch output matches expected output")
