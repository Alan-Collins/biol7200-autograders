import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import shutil
import tempfile
import os
import sys
import subprocess
import re

from gradescope_utils.autograder_utils.decorators import weight, number, visibility, partial_credit
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import (
    PointCounter,
    FastaSeq,
    recursive_type_str
)
import data as test_data

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "map_consensus.py"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"
DATA_DIR = "/autograder/biol7200-autograders/data/"

Q_NUM = PointCounter(1)

POINT_NUM = PointCounter(0)

MAPCON_EXPECTED = FastaSeq.from_fasta((
    ">Fusibacter_paucivorans_consensus\n"
    "AGAGTTTGATCCTGGCTCAGGATGAACGCTGGCGGCGTGCCTAACACATGCAAGTTGAGCGATTTACTTC"
    "GGTAAAGAGCGGCGGACGGGTGAGTAACGCGTGGGTAACCTACCCTGTACACACGGATAACATACCGAAA"
    "GGTATGCTAATACGGGATAATATATTTGAGAGGCATCTCTTGAATATCAAAGGTGAGCCAGTACAGGATG"
    "GACCCGCGTCTGATTAGCTAGTTGGTAAGGTAACGGCTTACCAAGGCGACGATCAGTAGCCGACCTGAGA"
    "GGGTGATCGGCCACATTGGAACTGAGACACGGTCCAAACTCCTACGGGAGGCAGCAGTGGGGAATATTGC"
    "ACAATGGGCGAAAGCCTGATGCAGCAACGCCGCGTGAGTGATGAAGGCCTTCGGGTCGTAAAACTCTGTC"
    "CTCAAGGAAGATAATGACGGTACTTGAGGAGGAAGCCCCGGCTAACTACGTGCCAGCAGCCGCGGTAATA"
    "CGTAGGGGGCTAGCGTTATCCGGATTTACTGGGCGTAAAGGGTGCGTAGGCGGTCTTTCAAGTCAGGAGT"
    "GAAAGGCTACGGCTCAACCGTAGTAAGCTCTTGAAACTGGGAGACTTGAGTGCAGGAGAGGAGAGTGGAA"
    "TTCCTAGTGTAGCGGTGAAATGCGTAGATATTAGGAGGAACACCAGTTGCGAAGGCGGCTCTCTGGACTG"
    "TAACTGACGCTGAGGCACGAAAGCGTGGGGAGCAAACAGGATTAGATACCCTGGTAGTCCACGCTGTAAA"
    "CGATGAGTACTAGGTGTCGGGGGTTNCCCNTCGGTGCCGCAGCTAACGCATTAAGTACTCCGCCTGGGAA"
    "GTACGCTCGCAAGAGTGAAACTCAAAGGAATTGACGGGGACCCGCACAAGTAGCGGAGCATGTGGTTTAA"
    "TTCGAAGCAACGCGAAGAACCTTACCTAAGCTTGACATCCCAATGACATCTCCTTAATCGGAGAGTTCCC"
    "TTCGGGGACATTGGTGACAGGTGGTGCATGGTTGTCGTCAGCTCGTGTCGTGAGATGTTGGGTTAAGTCC"
    "CGCAACGAGCGCAACCCTTGTCTTTAGTTGCCATCATTAAGTTGGGCACTCTAGAGAGACTGCCAGGGAT"
    "AACCTGGAGGAAGGTGGGGATGACGTCAAATCATCATGCCCCTTATGCTTAGGGCTACACACGTGCTACA"
    "ATGGGTAGTACAGAGGGTTGCCAAGCCGTAAGGTGGAGCTAATCCCTTAAAGCTACTCTCAGTTCGGATT"
    "GTAGGCTGAAACTCGCCTACATGAAGCTGGAGTTACTAGTAATCGCAGATCAGAATGCTGCGGTGAATGC"
    "GTTCCCGGGTCTTGTACACACCGCCCGTCACACCACGGGAGTTGGAGACGCCCGAAGCCGATTATCTAAC"
    "CTTTTGGAAGAAGTCGTCGAAGGTGGAATCAATAACTGGGGTGAAGTCGTAACAAGGTAGCCGTATCGGA"
    "AGGTGCGGCTGGATCACCTCCTT"
))

MAPCON_IGNORE_DELS = FastaSeq.from_fasta((
    ">Fusibacter_paucivorans_consensus\n"
    "AGAGTTTGATCCTGGCTCAGGATGAACGCTGGCGGCGTGCCTAACACATGCAAGTTGAGCGATTTACTTC"
    "GGTAAAGAGCGGCGGNNNNNTNCGTNANNNAAGAGCGGCGGACGGGTGAGTAACGCGTGGGTAACCTACC"
    "CTGTACACACGGATAACATACCGAAAGGTATGCTAATACGGGATAATATATTTGAGAGGCATCTCTTGAA"
    "TATCAAAGGTGAGCCAGTACAGGATGGACCCGCGTCTGATTAGCTAGTTGGTAAGGTAACGGCTTACCAA"
    "GGCGACGATCAGTAGCCGACCTGAGAGGGTGATCGGCCACATTGGAACTGAGACACGGTCCAAACTCCTA"
    "CGGGAGGCAGCAGTGGGGAATATTGCACAATGGGCGAAAGCCTGATGCAGCAACGCCGCGTGAGTGATGA"
    "AGGCCTTCGGGTCGTAAAACTCTGTCCTCAAGGAAGANNATAATGACGGTACTTGAGGAGGAAGCCCCGG"
    "CTAACTACGTGCCAGCAGCCGCGGTAATACGTAGGGGGCTAGCGTTATCCGGATTTACTGGGCGTAAAGG"
    "GTGCGTAGGCGGTCTTTCAAGTCAGGAGTGAAAGGCTACGGCTCAACCGTAGTAAGCTCTTGAAACTGGG"
    "AGACTTGAGTGCAGGAGAGGAGAGTGGAATTCCTAGTGTAGCGGTGAAATGCGTAGATATTAGGAGGAAC"
    "ACCAGTTGCGAAGGCGGCTCTCTGGACTGTAACTGACGCTGAGGCACGAAAGCGTGGGGAGCAAACAGGA"
    "TTAGATACCCTGGTAGTCCACGCTGTAAACGATGAGTACTAGGTGTCGGGGGTTNCCCNTCGGTGCCGCA"
    "GCTAACGCATTAAGTACTCCGCCTGGGAAGTACGCTCGCAAGAGTGAAACTCAAAGGAATTGACGGGGAC"
    "CCGCACAAGTAGCGGAGCATGTGGTTTAATTCGAAGCAACGCGAAGAACCTTACCTAAGCTTGACATCCC"
    "AATGACATCTCCTTAATCGGAGAGTTCCCTTCGGGGACATTGGTGACAGGTGGTGCATGGTTGTCGTCAG"
    "CTCGTGTCGTGAGATGTTGGGTTAAGTCCCGCAACGAGCGCAACCCTTGTCTTTAGTTGCCATCATTAAG"
    "TTGGGCACTCTAGAGAGACTGCCAGGGATAACCTGGAGGAAGGTGGGGATGACGTCAAATCATCATGCCC"
    "CTTATGCTTAGGGCTACACACGTGCTACAATGGGTAGTACAGAGGGTTGCCAAGCCGTAAGGTGGAGCTA"
    "ATCCCCTTAAAGCTACTCTCAGTTCGGATTGTAGGCTGAAACTCGCCTACATGAAGCTGGAGTTACTAGT"
    "AATCGCAGATCAGAATGCTGCGGTGAATGCGTTCCCGGGTCTTGTACACACCGCCCGTCACACCACGGGA"
    "GTTGGAGACGCCCGAAGCCGATTATCTAACCTTTTTTGGAAGAAGTCGTCGAAGGTGGAATCAATAACTG"
    "GGGTGAAGTCGTAACAAGGTAGCCGTATCGGAAGGTGCGGCTGGATCACCTCCTT"
))

SAM_CON_EXPECTED = FastaSeq.from_fasta((
    ">Fusibacter_paucivorans\n"
    "AGAGTTTGATCCTGGCTCAGGATGAACGCTGGCGGCGTGCCTAACACATGCAAGTTGAGCGATTTACTTC"
    "GGTAAAGAGCGGCGGACGGGTGAGTAACGCGTGGGTAACCTACCCTGTACACACGGATAACATACCGAAA"
    "GGTATGCTAATACGGGATAATATATTTGAGAGGCATCTCTTNAATATCAAAGGTGAGCCAGTACAGGATG"
    "GACCCGCGTCTGATTAGCTAGTTGGTAAGGTAACGGCTTACCAAGGCGACGATCAGTAGCCGACCTGAGA"
    "GGGTGATCGGCCACATTGGAACTGAGACACGGTCCAAACTCCTACGGGAGGCAGCAGTGGGGAATATTGC"
    "ACAATGGGCGAAAGCCTGATGCAGCAACGCCGCGTGAGTGATGAAGGCCTTCGGGTCGTAAAACTCTGTC"
    "CTCAAGGAAGATAATGACGGTACTTGAGGAGGAAGCCCCGGCTAACTACGTGCCAGCAGCCGCGGTAATA"
    "CGTAGGGGGCTAGCGTTATCCGGATTTACTGGGCGTAAAGGGTGCGTAGGCGGTCTTTCAAGTCAGGAGT"
    "GAAAGGCTACGGCTCAACCGTAGTAAGCTCTTGAAACTGGGAGACTTGAGTGCAGGAGAGGAGAGTGGAA"
    "TTCCTAGTGTAGCGGTGAAATGCGTAGATATTAGGAGGAACACCAGTTGCGAAGGCGGCTCTCTGGACTG"
    "TAACTGACGCTGAGGCACGAAAGCGTGGGGAGCAAACAGGATTAGATACCCTGGTAGTCCACGCTGTAAA"
    "CGATGAGTACTAGGTGTCGGGGGTNNCCCCCTTCGGTGCCGCAGCTAACGCATTAAGTACTCCGCCTGGG"
    "AAGTACGCTCGCAAGAGTGAAACTCAAAGGAATTGACGGGGACCCGCACAAGTAGCGGAGCATGTGGTTT"
    "AATTCGAAGCAACGCGAAGAACCTTACCTAAGCTTGACATCCCAATGACATCTCCTTAATCGGAGAGTTC"
    "CCTTCGGGGNNNNTGGTGACAGGTGGTGCATGGTTGTCGTCAGCTCGTGTCGTGAGATGTTGGGTTAAGT"
    "CCCGCAACGAGCGCAACCCTTGTCTTTAGTTGCCATCATTAAGTTGGGCACTCTAGAGAGACTGCCAGGG"
    "ATAACCTGGAGGAAGGTGGGGATGACGTCAAATCATCATGCCCCTTATGCTTAGGGCTACACACGTGCTA"
    "CAATGGGTAGTACAGAGGGTTGCCAAGCCGTAAGGTGGAGCTAATCCCTTAAAGCTACTCTCAGTTCGGA"
    "TTGTAGGCTGAAACTCGCCTACATGAAGCTGGAGTTACTAGTAATCGCAGATCAGAATGCTGCGGTGAAT"
    "GCGTTCCCGGGTCTTGTACACACCGCCCGTCACACCACGGGAGTTGGAGACGCCCGAAGCCGATTATCTA"
    "ACCTTNTGGAAGAAGTCGTCGAAGGTGGAATCAATAACTGGGGTGAAGTCGTAACAAGGTAGCCGTATCG"
    "GAAGGTGCGGCTGGATCACCTCCTT"
))

MAPCON_SYN_EXPECTED = FastaSeq.from_fasta((
    ">Synechococcus_elongatus_consensus\n"
    "ATTTGAGAGTTTGATCCTGGCTCAGGATGAACGCTGCTTCGGGGACATTGGTGACAGGTGGTGCATGGTT"
    "GTCGTCAGCTCGTGTCGTGAGATGTTGGGTTAAGTCCCGCAACGAGCGCAACCCTTGTCTTTAGTTGCCA"
    "TCATTAAGTTGGGCACTCTAGAGAGACTGCCAGGGATAACCTGGAGG"
))

MAPCON_METH_EXPECTED = FastaSeq.from_fasta((
    ">Methanococcus_aeolicus_consensus\n"
))

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = Path(tempfile.mkdtemp())
        cls.submitted = False
        
        if "__init__.py" in os.listdir(SUBMISSION_PATH):
            cls.format = "package"
            os.mkdir(f"{SUBMISSION_PATH}magnumopus")
            for file in os.listdir(SUBMISSION_PATH):
                if file.endswith(".py"):
                    if file == "map_consensus.py":
                        Path(f"{SCRIPT_PATH}").chmod(0o777)
                        continue
                    shutil.move(f"{SUBMISSION_PATH}{file}", f"{SUBMISSION_PATH}magnumopus")
        elif "magnumopus.py" in os.listdir(SUBMISSION_PATH):
            cls.format = "module"
        else:
            return cls
        
        cls.input_dirs = [
            "reads",
            "refs"
        ]
        for dir in cls.input_dirs:
            shutil.copytree(f"{DATA_DIR}{dir}", f"{cls.dir}/{dir}")
        
        cls.submitted = True
        try: # import the package
            sys.path.append(SUBMISSION_PATH)
            import magnumopus
            import magnumopus.sam
            from magnumopus.sam import SAM
            cls.sam_class = SAM
            cls.imported = True
        
        except Exception as e:
            cls.imported = False
            cls.error = e
        
        try:
            with patch("builtins.open", mock_open(read_data=test_data.MINIMAL_SAM)):
                _ = SAM.from_sam("fakepath")
                cls.can_instance = True
        except Exception as e:
            cls.can_instance = False
            cls.error = e

        cls.map_consensus_ran = False
        cls.map_consensus_error = ""
        # Store help message of map_consensus.py
        if not Path(f"{SCRIPT_PATH}").exists():
            cls.map_consensus_error = "File not found"
            return cls

        Path(f"{SCRIPT_PATH}").chmod(0o777)

        pattern = re.compile(r"\#\![ ]?/usr/bin/env python3")
        with open(f"{SCRIPT_PATH}") as f:
            first_line = f.readline()
        if re.match(pattern, first_line):
            cls.shebang = True
        else:
            cls.map_consensus_error = "Missing or invalid shebang"
            return cls
        
        command = [f"{SCRIPT_PATH}", "-h"]
                   
        cls.mapcon_help_result = subprocess.run(
            command,
            text=True,
            capture_output=True
        )
        cls.map_consensus_ran = True

        # Run map_consensus.py
        command = [
            f"{SCRIPT_PATH}",
            "-1", "reads/ERR11767307_1.fastq",
            "-2", "reads/ERR11767307_2.fastq",
            "-r", "refs/16S.fna"
        ]
                   
        cls.mapcon_result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            cwd=cls.dir
        )

        # specify off-target seq
        command = [
            f"{SCRIPT_PATH}",
            "-1", "reads/ERR11767307_1.fastq",
            "-2", "reads/ERR11767307_2.fastq",
            "-r", "refs/16S.fna",
            "-s", "Synechococcus_elongatus"
        ]
                   
        cls.mapcon_syn_result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            cwd=cls.dir
        )

        # specify blank seq
        command = [
            f"{SCRIPT_PATH}",
            "-1", "reads/ERR11767307_1.fastq",
            "-2", "reads/ERR11767307_2.fastq",
            "-r", "refs/16S.fna",
            "-s", "Methanococcus_aeolicus"
        ]
                   
        cls.mapcon_meth_result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            cwd=cls.dir
        )

    
    def basic_fail(self):
        if not self.submitted:
            self.fail("Your submission is lacking a magnumopus.py file or an __init__.py file and can't be processed.")
        if not self.imported:
            self.fail(f"Unable to import magnumopus.sam.SAM: {self.error}")
        if not self.can_instance:
            self.fail(f"Unable to create an instance of your SAM class: {self.error}")
    
    def check_class_method(self, cls, meth):
        """Check class for a method and print a clear message if absent

        Args:
            meth (str): The method of which to assess the existence callable-ity
        """
        # Figure out if message should say a or an for this method
        a_an = "an" if meth[0] in {"a", "e", "i", "o" "u"} else "a"
        if not hasattr(cls, meth):
            self.fail(f"Your {cls.__name__} class does not have {a_an} {meth} method.")
        else:
            if not callable(eval(f"cls.{meth}")):
                self.fail(f"Your {cls.__name__} class does have {a_an} {meth} attribute, but it is not callable")

    def check_method_output(self, instance, method, expected, tested_data, args=(), kwargs=None, comparison=None):
        """Compare an output of a class method to an expected value

        Args:
            instance (Object): The instance you want to assess
            method (str): The method whose return value should be compared
            args (tuple[any]): The arguments to provide to the method when called
            kwargs (dict[str, any]): The keyword arguments to provide to the method when called
            expected (any): The expected value
            tested_data (str): the nature of the tested data
            comparison (callable): a function to compare the results. will be called with (result, expected) and should return bool
        """
        if kwargs == None:
            kwargs = {}
        a_an = "an" if tested_data[0] in {"a", "e", "i", "o", "u"} else "a"
        try:
            value = eval(f"instance.{method}(*args, **kwargs)")
        except Exception as e:
            self.fail(f"Your {instance.__class__.__name__}.{method} for {a_an} {tested_data}, when it was run with input {args}. The error was {e}")
        expected_ret_type = recursive_type_str(expected)
        self.check_method_return_type(instance, method, tested_data, args, kwargs, expected_ret_type)
        try:
            if comparison is not None:
                assert comparison(value, expected)
            else:
                assert value == expected
        except:
            self.fail(f"Your {instance.__class__.__name__}.{method} returned {repr(value)} for {a_an} {tested_data}, when it should have returned {repr(expected)}.")


    def check_method_return_type(self, instance, method, tested_data, args=(), kwargs=None, expected_type=None):
        """Compare an return type of a class method to an expected return type

        Args:
            instance (Object): The instance you want to assess
            method (str): The method whose return value should be compared
            args (tuple[any]): The arguments to provide to the method when called
            kwargs (dict[str, any]): The keyword arguments to provide to the method when called
            tested_data (str): the nature of the tested data
            expected_type (str): The expected return type
        """
        if kwargs == None:
            kwargs = {}
        a_an = "an" if tested_data[0] in {"a", "e", "i", "o", "u"} else "a"
        try:
            value = eval(f"instance.{method}(*args, **kwargs)")
        except Exception as e:
            self.fail(f"Your {instance.__class__.__name__}.{method} for {a_an} {tested_data}, when it was run with input {args}. The error was {e}")
        return_type = recursive_type_str(value) 
        if return_type != expected_type:
            self.fail(f"Your {instance.__class__.__name__}.{method} return type is {return_type}, when it should have been {expected_type}.")

    
    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_magop_import(self):
        """Check magnumopus import"""
        if not self.imported:
            # Something about importing isn't working.
            try:
                import magnumopus
            except Exception as e:
                self.fail(
                    f"Unable to import your magnumopus package due to error:\n{e}"
                )
        print(f"magnumopus package imported successfully")

    
    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_sam_import(self):
        """Check magnumopus.sam import"""
        if not self.imported:
            # Something about importing isn't working.
            try:
                import magnumopus.sam
            except Exception as e:
                self.fail(
                    f"Unable to import your magnumopus.sam due to error:\n{e}"
                )
        print(f"magnumopus.sam imported successfully")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_sam_class_import(self):
        """Check SAM import"""
        if not self.imported:
            # Something about importing isn't working.
            try:
                import magnumopus.sam.SAM
            except Exception as e:
                self.fail(
                    f"Unable to import magnumopus.sam.SAM due to error:\n{e}"
                )
        print(f"magnumopus.sam.SAM imported successfully")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.MINIMAL_SAM))
    def test_sam_class_can_be_instantiated(self):
        """Can the Read class be instantiated from a SAM entry"""
        try:
            _ = self.sam_class.from_sam("patch_data")
        except Exception as e:
            self.fail(f"Your SAM class from_sam classmethod does not create an instance of the class when given a SAM entry:\n{e}")
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_from_sam_method_exists(self):
        """Does the SAM class have a 'from_sam' classmethod"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "from_sam")
        method = self.sam_class.from_sam
        bound_to = getattr(method, '__self__', None)
        if not isinstance(bound_to, type):
            # must be bound to a class
            self.fail("from_sam is not a classmethod")
        name = method.__name__
        for cls in bound_to.__mro__:
            descriptor = vars(cls).get(name)
            if descriptor is not None:
                if not isinstance(descriptor, classmethod):
                    self.fail("from_sam is not a classmethod")
                print("yes")
                return
        self.fail("from_sam is not a classmethod of SAM or any class in its mro")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.MINIMAL_SAM))
    def test_from_sam_method_creates_instance(self):
        """Does the SAM.from_sam method return a SAM instance"""
        self.basic_fail()
        inst = self.sam_class.from_sam("fakepath")
        if not isinstance(inst, self.sam_class):
            self.fail(
                "SAM.from_sam does not return an instance of SAM, but of "
                f"{inst.__class__.__name__}"
            )
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_reads_at_pos_method_exists(self):
        """Does the SAM class have a 'reads_at_pos' method"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "reads_at_pos")
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_pileup_at_pos_method_exists(self):
        """Does the SAM class have a 'pileup_at_pos' method"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "pileup_at_pos")
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.INDELS_SAM))
    def test_pileup_at_pos_method_basic(self):
        """Does the 'pileup_at_pos' method behave as expected"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "pileup_at_pos")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="pileup_at_pos",
            expected=(['G', 'G', 'G', 'G'], ['F', 'F', 'F', 'F']),
            args=("Bacillus_subtilis", 402),
            tested_data="a position corresponding to normally mapped bases"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.SECONDARY_CONSENSUS_SAM))
    def test_pileup_at_pos_method_secondary(self):
        """Does the 'pileup_at_pos' method handle secondary mappings as expected"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "pileup_at_pos")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="pileup_at_pos",
            expected=(['C'], ['F']),
            args=("Bacillus_subtilis", 5),
            tested_data="a position with bases from secondary mapping reads"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.SUPPLEMENTAL_CONSENSUS_SAM))
    def test_pileup_at_pos_method_supplemental(self):
        """Does the 'pileup_at_pos' method handle supplemental mappings as expected"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "pileup_at_pos")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="pileup_at_pos",
            expected=(['C'], ['F']),
            args=("Bacillus_subtilis", 5),
            tested_data="a position with bases from supplemental mapping reads"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.INDELS_SAM))
    def test_pileup_at_pos_method_handles_deletions(self):
        """Does the 'pileup_at_pos' method handle deletions as expected"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "pileup_at_pos")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="pileup_at_pos",
            expected=(['T', 'T', 'T', 'T'], ['F', 'F', 'F', 'F']),
            args=("Bacillus_subtilis", 476),
            tested_data="a position corresponding to normally mapped bases"
        )
        self.check_method_output(
            instance=inst,
            method="pileup_at_pos",
            expected=(['', '', '', ''], ['', '', '', '']),
            args=("Bacillus_subtilis", 477),
            tested_data="a position corresponding to a deleted base"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.INDELS_SAM))
    def test_pileup_at_pos_method_handles_insertions(self):
        """Does the 'pileup_at_pos' method handle insertions as expected"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "pileup_at_pos")
        inst = self.sam_class.from_sam("fakepath")
        # base before insertion
        self.check_method_output(
            instance=inst,
            method="pileup_at_pos",
            expected=(['A', 'A', 'A', 'A'], [':', 'F', 'F', 'F']),
            args=("Bacillus_subtilis", 460),
            tested_data="a position corresponding to normally mapped bases",
            comparison=lambda x, y: set(x[0]) == set(y[0]) and  set(x[1]) == set(y[1])
        )
        # insertion base
        self.check_method_output(
            instance=inst,
            method="pileup_at_pos",
            expected=(['CATATGTGT', 'CATATGTGT', 'CATATGTGT', 'CATATGTGT'], ['FF:FFFFFF', 'FFFF:FFFF', 'FFFFFFFFF', 'FFFFFFFFF']),
            args=("Bacillus_subtilis", 461),
            tested_data="a position corresponding to inserted bases",
            comparison=lambda x, y: set(x[0]) == set(y[0]) and  set(x[1]) == set(y[1])
        )
        # base after insertion
        self.check_method_output(
            instance=inst,
            method="pileup_at_pos",
            expected=(['A', 'A', 'A', 'A'], ['F', ':', 'F', 'F']),
            args=("Bacillus_subtilis", 462),
            tested_data="a position corresponding to normally mapped bases",
            comparison=lambda x, y: set(x[0]) == set(y[0]) and  set(x[1]) == set(y[1])
        )
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_consensus_at_pos_method_exists(self):
        """Does the SAM class have a 'consensus_at_pos' method"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus_at_pos")
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.INDELS_SAM))
    def test_consensus_at_pos_method_basic(self):
        """Does the 'consensus_at_pos' method behave as expected"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus_at_pos")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="consensus_at_pos",
            expected="G",
            args=("Bacillus_subtilis", 402),
            tested_data="a position corresponding to normally mapped bases"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.SECONDARY_CONSENSUS_SAM))
    def test_consensus_at_pos_method_secondary(self):
        """Does the 'consensus_at_pos' method handle secondary mappings as expected"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus_at_pos")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="consensus_at_pos",
            expected="C",
            args=("Bacillus_subtilis", 5),
            tested_data="a position with bases from secondary mapping reads"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.SUPPLEMENTAL_CONSENSUS_SAM))
    def test_consensus_at_pos_method_supplemental(self):
        """Does the 'consensus_at_pos' method handle supplemental mappings as expected"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus_at_pos")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="consensus_at_pos",
            expected="C",
            args=("Bacillus_subtilis", 5),
            tested_data="a position with bases from supplemental mapping reads"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.INDELS_SAM))
    def test_consensus_at_pos_method_handles_deletions(self):
        """Does the 'consensus_at_pos' method handle deletions as expected"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus_at_pos")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="consensus_at_pos",
            expected="T",
            args=("Bacillus_subtilis", 476),
            tested_data="a position corresponding to normally mapped bases"
        )
        self.check_method_output(
            instance=inst,
            method="consensus_at_pos",
            expected="",
            args=("Bacillus_subtilis", 477),
            tested_data="a position corresponding to a deleted base"
        )
        print("yes")

    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.INDELS_SAM))
    def test_consensus_at_pos_method_handles_insertions(self):
        """Does the 'consensus_at_pos' method handle insertions as expected"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus_at_pos")
        inst = self.sam_class.from_sam("fakepath")
        # base before insertion
        self.check_method_output(
            instance=inst,
            method="consensus_at_pos",
            expected="A",
            args=("Bacillus_subtilis", 460),
            tested_data="a position corresponding to normally mapped bases"
            )
        # insertion base
        self.check_method_output(
            instance=inst,
            method="consensus_at_pos",
            expected="CATATGTGT",
            args=("Bacillus_subtilis", 461),
            tested_data="a position corresponding to inserted bases"
        )
        # base after insertion
        self.check_method_output(
            instance=inst,
            method="consensus_at_pos",
            expected="A",
            args=("Bacillus_subtilis", 462),
            tested_data="a position corresponding to normally mapped bases"
        )
        print("yes")

    
    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.MINORITY_CONFLICTING_BASES_SAM))
    def test_consensus_at_pos_method_handles_minor_disagree(self):
        """Does the 'consensus_at_pos' method handle a minority of reads disagreeing with the majority base call as expected"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus_at_pos")
        inst = self.sam_class.from_sam("fakepath")
        # base before insertion
        self.check_method_output(
            instance=inst,
            method="consensus_at_pos",
            expected="C",
            args=("Bacillus_subtilis", 4),
            tested_data="a position where a minority of reads disagree with the majority base call"
            )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.MAJORITY_CONFLICTING_BASES_SAM))
    def test_consensus_at_pos_method_handles_major_disagree(self):
        """Does the 'consensus_at_pos' method handle a majority of reads disagreeing about the base call as expected"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus_at_pos")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="consensus_at_pos",
            expected="N",
            args=("Bacillus_subtilis", 8),
            tested_data="a position where a majority of reads disagree with the majority base call"
            )
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_consensus_method_exists(self):
        """Does the SAM class have a 'consensus' method"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus")
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.SIMPLE_CONSENSUS_SAM))
    def test_consensus_method_basic(self):
        """Does the 'consensus' method behave as expected for a simple input"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="consensus",
            expected="CAGCCGCGGTAATCCGGAGGTGGCAAGCGTTATCCGGAATTATTGGGCGTAAAGCGCGCGTAGGCGGTTTTTTAAGTCTGATGTGAAAGCCCACGGCTCAACCGTGGAGGGTCATTGGAAACTGGAAAACTTGAGTGCAGAAGAGGAAAG",
            args=("Bacillus_subtilis",),
            tested_data="a sequence to which reads mapped with no indels or clipping"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.SIMPLE_CONSENSUS_SAM))
    def test_consensus_method_fake_seq(self):
        """Does the 'consensus' method behave as expected for a sequence that doesn't exist"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="consensus",
            expected="",
            args=("Not_a_real_seq",),
            tested_data="a sequence to which no reads were mapped"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.SOFT_CLIP_CONSENSUS_SAM))
    def test_consensus_method_soft_clip(self):
        """Does the 'consensus' method behave as expected with soft clipping"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="consensus",
            expected="CAGCCGCGGTAATCCGGAGGTGGCAAGCGTTATCCGGAATTATTGGGCGTAAAGCGCGCGTAGGCGGTTTTTTAAGTCTGATGTGAAAGCCCACGGCTCAACCGTGGAGGGTCATTGGAAACTGGAAAACTTGAGTGCAGAAGAGGAAAG",
            args=("Bacillus_subtilis",),
            tested_data="a sequence to which reads mapped with soft clipping"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.DELETION_CONSENSUS_SAM))
    def test_consensus_method_deletion(self):
        """Does the 'consensus' method behave as expected with a deletion in the reads"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="consensus",
            expected="CAGCCGCGGTAATCCGGAGGTGGCAAGCGTTATCCTATTGGGCGTAAAGCGCGCGTAGGCGGTTTTTTAAGTCTGATGTGAAAGCCCACGGCTCAACCGTGGAGGGTCATTGGAAACTGGAAAACTTGAGTGCAGAAGAGGAAAG",
            args=("Bacillus_subtilis",),
            tested_data="a sequence to which reads mapped with a deletion"
        )
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.INSERTION_CONSENSUS_SAM))
    def test_consensus_method_insertion(self):
        """Does the 'consensus' method behave as expected with an insertion in the reads"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="consensus",
            expected="CAGCCGCGGTAATCCGGAGGTGGCAAGCGTTATCCGGAATAAAAATATTGGGCGTAAAGCGCGCGTAGGCGGTTTTTTAAGTCTGATGTGAAAGCCCACGGCTCAACCGTGGAGGGTCATTGGAAACTGGAAAACTTGAGTGCAGAAGAGGAAAG",
            args=("Bacillus_subtilis",),
            tested_data="a sequence to which reads mapped with an insertion"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.MINORITY_CONFLICTING_BASES_SAM))
    def test_consensus_method_minor_disagree(self):
        """Does the 'consensus' method behave as expected when a minority of reads disagree about base calls"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="consensus",
            expected="CAGCCGCGGTAATCCGGAGG",
            args=("Bacillus_subtilis",),
            tested_data="a sequence to which reads mapped with a minority of reads disagreeing about base calls"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.MAJORITY_CONFLICTING_BASES_SAM))
    def test_consensus_method_major_disagree(self):
        """Does the 'consensus' method behave as expected when a majority of reads disagree about base calls"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="consensus",
            expected="CAGCCGCNNNNNTCCGGAGG",
            args=("Bacillus_subtilis",),
            tested_data="a sequence to which reads mapped with a majority of reads disagreeing about base calls"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_best_consensus_method_exists(self):
        """Does the SAM class have a 'best_consensus' method"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "best_consensus")
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.SIMPLE_CONSENSUS_SAM))
    def test_best_consensus_method_basic(self):
        """Does the 'best_consensus' method behave as expected for a simple input"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "best_consensus")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="best_consensus",
            expected="CAGCCGCGGTAATCCGGAGGTGGCAAGCGTTATCCGGAATTATTGGGCGTAAAGCGCGCGTAGGCGGTTTTTTAAGTCTGATGTGAAAGCCCACGGCTCAACCGTGGAGGGTCATTGGAAACTGGAAAACTTGAGTGCAGAAGAGGAAAG",
            tested_data="a SAM file with reads all mapped to a single reference"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.MAJORITY_READS_ONE_REF_SAM))
    def test_best_consensus_method_two_ref(self):
        """Does the 'best_consensus' method behave as expected for an input with reads mapped to two references"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "best_consensus")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="best_consensus",
            expected="CAGCCGCGGTAATCCGGAGGTGGCAAGCGTTATCCGGAATTATTGGGCGTAAAGCGCGCGTAGGCGGTTTTTTAAGTCTGATGTGAAAGCCCACGGCTCAACCGTGGAGGGTCATTGGAAACTGGAAAACTTGAGTGCAGAAGAGGAAAG",
            tested_data="a SAM file with a minority of reads mapped to a second, longer reference"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.MIN_READS_BUT_MAJ_BASES_ONE_REF_SAM))
    def test_best_consensus_method_minority_reads_majority_bases(self):
        """Does the 'best_consensus' method behave as expected when the minority of reads, but majority of bases map to a reference"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "best_consensus")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="best_consensus",
            expected="ATCAAACATCATAATTTTTATGGAGAGTTTGATCCTGGCTCAGGATGAACGCTGGCGGCGTGCCTAATACATGCAAGTCGAGCGAACGGACGAGAAGCTT",
            tested_data="a SAM file with a minority of reads mapped to a second, longer reference"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.MAJORITY_SECONDARY_SAM))
    def test_best_consensus_method_majority_secondary(self):
        """Does the 'best_consensus' method behave as expected when majority of reads and mapped bases are part of secondary mappings"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "best_consensus")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="best_consensus",
            expected="CAGCCGCGGTAATCCGGAGGTGGCAAGCGTTATCCGGAATTATTGGGCGTAAAGCGCGCGTAGGCGGTTTTTTAA",
            tested_data="a SAM file where the majority of mapped reads and bases are part of secondary mappings"
        )
        print("yes")

    @weight(2)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @patch("builtins.open", mock_open(read_data=test_data.MAJORITY_SUPPLEMENTAL_SAM))
    def test_best_consensus_method_majority_supplemental(self):
        """Does the 'best_consensus' method behave as expected when majority of reads and mapped bases are part of supplemental mappings"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "best_consensus")
        inst = self.sam_class.from_sam("fakepath")
        self.check_method_output(
            instance=inst,
            method="best_consensus",
            expected="CAGCCGCGGTAATCCGGAGGTGGCAAGCGTTATCCGGAATTATTGGGCGTAAAGCGCGCGTAGGCGGTTTTTTAA",
            tested_data="a SAM file where the majority of mapped reads and bases are part of supplemental mappings"
        )
        print("yes")

    
    @weight(0)
    @number(f"{Q_NUM.next()}.{POINT_NUM.reset()}")
    @visibility("on_fail")
    def test_map_consensus_submitted(self):
        """Was map_consensus.py submitted and does it run"""
        if not self.map_consensus_ran:
            self.fail(f"map_consensus.py could not be run: {self.map_consensus_error}")
        if self.mapcon_help_result.stderr.strip() != "":
            self.fail(
                "map_consensus.py failed with the following error when run with -h:\n"
                f"{self.mapcon_help_result.stderr}"
                )
        else:
            print("map_consensus.py ran without error when run with -h")

        if self.mapcon_result.stderr.strip() != "":
            self.fail(
                "map_consensus.py failed with the following error when run with test inputs:\n"
                f"{self.mapcon_result.stderr}"
                )
        else:
            print("map_consensus.py ran without error when run with test inputs")
    
        print("map_consensus.py was submitted and seems to run")

    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_line_endings(self):
        """Check unix line endings"""
        if not Path(f"{SCRIPT_PATH}").exists():
            self.fail("No map_consensus.py script was submitted")
        with open(SCRIPT_PATH) as f:
            f.readline()
            newlines = f.newlines
        if newlines != "\n":
            self.fail(
                "Your script does not use unix line endings. "
                "That might interfere with the functionality of autograder tests. "
                f"Please change your line endings to the unix \\n instead of your current {repr(newlines)}"
            )
        print(f"Unix line endings used")
    

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_map_consensus_help_matches_expectation(self):
        """Is map_consensus.py help message correct"""
        if not self.map_consensus_ran:
            self.fail(f"map_consensus.py could not be run: {self.map_consensus_error}")
        opts = set(re.findall(r"\B-+\w+", self.mapcon_help_result.stdout))
        print(
            f"Found the following command line options:\n"
            f"{", ".join(sorted(opts))}"
            )
        expected = {"-1", "-2", "-r", "-s"}
        missing = expected.difference(opts)
        if len(missing) != 0:
            self.fail("your map_consensus.py script is missing options which were specified as required parts of the CLI.")
        print("All expected command line options were found.")

    
    @partial_credit(40)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_map_consensus_output_matches_expectation(self, set_score=None):
        """Is map_consensus.py output correct"""
        if not self.map_consensus_ran:
            self.fail(f"map_consensus.py could not be run: {self.map_consensus_error}")
        print(f"Your script's output is:\n{self.mapcon_result.stdout}")
        print("Comparing your output against the expectation with no -s specified")
        score = 40
        try:
            result = FastaSeq.from_fasta(self.mapcon_result.stdout.strip())
        except Exception as e:
            self.fail(f"Could not parse your script's stdout as FASTA sequence: {e}")
        
        if result == MAPCON_EXPECTED:
            print("output matches expected output")
        
        else:        
            if result == SAM_CON_EXPECTED:
                self.fail("Don't use `samtools consensus` to get the consensus")

            if result == MAPCON_IGNORE_DELS:
                self.fail("Don't ignore reads indicating a deletion. We are trying to determine the sequence in the DNA the reads came from so a deletion in the reads tells us useful information about that DNA sequence.")
            
            if result.num_seqs != 1:
                self.fail("Your output includes multiple sequences")

            if len(result) != 1493:
                print(f"Your output is the wrong length. Expected 1493. Found {len(result)}")
                
                rlen = len(result)

                match rlen:
                    case 1528:
                        print("You are not considering deletions correctly")
                        score -= 5
                    case 1495:
                        print("You are not determining the majority base call to decide the consensus")
                        score -= 5
                    case 1529:
                        print("You are not considering deletions correctly or determining the majority base call to decide the consensus")
                        score -= 10
                    case _:
                        self.fail(
                            "Your output cannot be diagnosed automatically. "
                            "Please report this issue so the autograder can be improved. "
                            "Otherwise, your score will be manually adjusted during grading."
                        )
            else:
                print("Your output is the correct length, but does not match the expected sequence")
                if "N" not in result.seqs[0].seq:
                    score -= 5
                    print("You are not handling cases where there is no majority base call")
                

                if result.seqs[0].reverse_complement() == MAPCON_EXPECTED:
                    print(
                        "Your output is correct but is the reverse complement of the expected output. "
                        "Did you intend to reverse the sequence relative to the mapping reference?"
                    )
                else:
                    print("Unable to automatically diagnose the issue with your sequence")
                    score -= 5
        print()
        print("Comparing your output with specified -s inputs")
        try:
            result = FastaSeq.from_fasta(self.mapcon_syn_result.stdout)
            print(f"Your script's output is:\n{self.mapcon_syn_result.stdout}")
            if result == MAPCON_SYN_EXPECTED:
                print("Your output matches the expectation for a sequence other than the best.")
            else:
                print(f"Your output does not match the expectation for a sequence other than the best. Expected\n{MAPCON_SYN_EXPECTED}")
                score -= 5
        except Exception as e:
            print(f"Could not parse your script's stdout as FASTA sequence: {e}")
            score -= 5

        print()
        try:
            result = FastaSeq.from_fasta(self.mapcon_meth_result.stdout.strip())
            print(f"Your script's output is:\n{self.mapcon_meth_result.stdout}")
            if result == MAPCON_METH_EXPECTED:
                print("Your output matches the expectation for a sequence with no reads mapped to it.")
            else:
                print(f"Your output does not match the expectation for a sequence with no reads mapped to it. Expected\n{MAPCON_METH_EXPECTED}")
                score -= 5
        except Exception as e:
            print(f"Could not parse your script's stdout as FASTA sequence: {e}")
            score -= 5

        
        set_score(max(score, 0))
