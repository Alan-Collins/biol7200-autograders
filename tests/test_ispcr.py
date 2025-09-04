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

from utils import PointCounter

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_DIR = "ispcr"
SOLUTION_SCRIPT = "ispcr.py"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"
PACKAGE_PATH = f"{SUBMISSION_PATH}{SOLUTION_DIR}"
DATA_DIR = "/autograder/biol7200-autograders/data/"

Q2_INPUT = [
    ['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '46920', '46938', '0.005', '32.4', '19'],
    ['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '47211', '47192', '0.45', '26.1', '20'],
    ['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '144156', '144174', '0.005', '32.4', '19'],
    ['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '144447', '144428', '0.45', '26.1', '20'],
    ['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '149622', '149640', '0.005', '32.4', '19'],
    ['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '149913', '149894', '0.45', '26.1', '20'],
    ['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '401483', '401501', '0.005', '32.4', '19'],
    ['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '401774', '401755', '0.45', '26.1', '20'],
    ['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '2321911', '2321930', '0.45', '26.1', '20'],
    ['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '2322202', '2322184', '0.005', '32.4', '19'],
    ['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '2683111', '2683130', '0.45', '26.1', '20'],
    ['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '2683402', '2683384', '0.005', '32.4', '19'],
    ['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '2688655', '2688674', '0.45', '26.1', '20'],
    ['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '2688946', '2688928', '0.005', '32.4', '19'],
    ['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '2694199', '2694218', '0.45', '26.1', '20'],
    ['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '2694490', '2694472', '0.005', '32.4', '19'],
    ['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '2771804', '2771823', '0.45', '26.1', '20'],
    ['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '2772095', '2772077', '0.005', '32.4', '19'],
    ['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '2945147', '2945166', '0.45', '26.1', '20'],
    ['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '2945438', '2945420', '0.005', '32.4', '19']
]

Q3_INPUT = [
    (['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '46920', '46938', '0.005', '32.4', '19'], ['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '47211', '47192', '0.45', '26.1', '20']),
    (['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '144156', '144174', '0.005', '32.4', '19'], ['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '144447', '144428', '0.45', '26.1', '20']),
    (['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '149622', '149640', '0.005', '32.4', '19'], ['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '149913', '149894', '0.45', '26.1', '20']),
    (['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '401483', '401501', '0.005', '32.4', '19'], ['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '401774', '401755', '0.45', '26.1', '20']),
    (['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '2321911', '2321930', '0.45', '26.1', '20'], ['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '2322202', '2322184', '0.005', '32.4', '19']),
    (['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '2683111', '2683130', '0.45', '26.1', '20'], ['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '2683402', '2683384', '0.005', '32.4', '19']),
    (['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '2688655', '2688674', '0.45', '26.1', '20'], ['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '2688946', '2688928', '0.005', '32.4', '19']),
    (['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '2694199', '2694218', '0.45', '26.1', '20'], ['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '2694490', '2694472', '0.005', '32.4', '19']),
    (['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '2771804', '2771823', '0.45', '26.1', '20'], ['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '2772095', '2772077', '0.005', '32.4', '19']),
    (['806R', 'NZ_CP028827.1', '85.000', '20', '3', '0', '1', '20', '2945147', '2945166', '0.45', '26.1', '20'], ['515F', 'NZ_CP028827.1', '89.474', '19', '2', '0', '1', '19', '2945438', '2945420', '0.005', '32.4', '19']),
]

Q3_OUTPUT = """>NZ_CP028827.1:46939-47191 Vibrio cholerae strain N16961 chromosome 1, complete sequence
TACGGAGGGTGCAAGCGTTAATCGGAATTACTGGGCGTAAAGCGCATGCAGGTGGTTTGTTAAGTCAGATGTGAAAGCCCTGGGCTCAACCTAGGAATCGCATTTGAAACTGACAAGCTAGAGTACTGTAGAGGGGGGTAGAATTTCAGGTGTAGCGGTGAAATGCGTAGAGATCTGAAGGAATACCGGTGGCGAAGGCGGCCCCCTGGACAGATACTGACACTCAGATGCGAAAGCGTGGGGAGCAAACAGG
>NZ_CP028827.1:144175-144427 Vibrio cholerae strain N16961 chromosome 1, complete sequence
TACGGAGGGTGCAAGCGTTAATCGGAATTACTGGGCGTAAAGCGCATGCAGGTGGTTTGTTAAGTCAGATGTGAAAGCCCTGGGCTCAACCTAGGAATCGCATTTGAAACTGACAAGCTAGAGTACTGTAGAGGGGGGTAGAATTTCAGGTGTAGCGGTGAAATGCGTAGAGATCTGAAGGAATACCGGTGGCGAAGGCGGCCCCCTGGACAGATACTGACACTCAGATGCGAAAGCGTGGGGAGCAAACAGG
>NZ_CP028827.1:149641-149893 Vibrio cholerae strain N16961 chromosome 1, complete sequence
TACGGAGGGTGCAAGCGTTAATCGGAATTACTGGGCGTAAAGCGCATGCAGGTGGTTTGTTAAGTCAGATGTGAAAGCCCTGGGCTCAACCTAGGAATCGCATTTGAAACTGACAAGCTAGAGTACTGTAGAGGGGGGTAGAATTTCAGGTGTAGCGGTGAAATGCGTAGAGATCTGAAGGAATACCGGTGGCGAAGGCGGCCCCCTGGACAGATACTGACACTCAGATGCGAAAGCGTGGGGAGCAAACAGG
>NZ_CP028827.1:401502-401754 Vibrio cholerae strain N16961 chromosome 1, complete sequence
TACGGAGGGTGCAAGCGTTAATCGGAATTACTGGGCGTAAAGCGCATGCAGGTGGTTTGTTAAGTCAGATGTGAAAGCCCTGGGCTCAACCTAGGAATCGCATTTGAAACTGACAAGCTAGAGTACTGTAGAGGGGGGTAGAATTTCAGGTGTAGCGGTGAAATGCGTAGAGATCTGAAGGAATACCGGTGGCGAAGGCGGCCCCCTGGACAGATACTGACACTCAGATGCGAAAGCGTGGGGAGCAAACAGG
>NZ_CP028827.1:2321931-2322183 Vibrio cholerae strain N16961 chromosome 1, complete sequence
CCTGTTTGCTCCCCACGCTTTCGCATCTGAGTGTCAGTATCTGTCCAGGGGGCCGCCTTCGCCACCGGTATTCCTTCAGATCTCTACGCATTTCACCGCTACACCTGAAATTCTACCCCCCTCTACAGTACTCTAGCTTGTCAGTTTCAAATGCGATTCCTAGGTTGAGCCCAGGGCTTTCACATCTGACTTAACAAACCACCTGCATGCGCTTTACGCCCAGTAATTCCGATTAACGCTTGCACCCTCCGTA
>NZ_CP028827.1:2683131-2683383 Vibrio cholerae strain N16961 chromosome 1, complete sequence
CCTGTTTGCTCCCCACGCTTTCGCATCTGAGTGTCAGTATCTGTCCAGGGGGCCGCCTTCGCCACCGGTATTCCTTCAGATCTCTACGCATTTCACCGCTACACCTGAAATTCTACCCCCCTCTACAGTACTCTAGCTTGTCAGTTTCAAATGCGATTCCTAGGTTGAGCCCAGGGCTTTCACATCTGACTTAACAAACCACCTGCATGCGCTTTACGCCCAGTAATTCCGATTAACGCTTGCACCCTCCGTA
>NZ_CP028827.1:2688675-2688927 Vibrio cholerae strain N16961 chromosome 1, complete sequence
CCTGTTTGCTCCCCACGCTTTCGCATCTGAGTGTCAGTATCTGTCCAGGGGGCCGCCTTCGCCACCGGTATTCCTTCAGATCTCTACGCATTTCACCGCTACACCTGAAATTCTACCCCCCTCTACAGTACTCTAGCTTGTCAGTTTCAAATGCGATTCCTAGGTTGAGCCCAGGGCTTTCACATCTGACTTAACAAACCACCTGCATGCGCTTTACGCCCAGTAATTCCGATTAACGCTTGCACCCTCCGTA
>NZ_CP028827.1:2694219-2694471 Vibrio cholerae strain N16961 chromosome 1, complete sequence
CCTGTTTGCTCCCCACGCTTTCGCATCTGAGTGTCAGTATCTGTCCAGGGGGCCGCCTTCGCCACCGGTATTCCTTCAGATCTCTACGCATTTCACCGCTACACCTGAAATTCTACCCCCCTCTACAGTACTCTAGCTTGTCAGTTTCAAATGCGATTCCTAGGTTGAGCCCAGGGCTTTCACATCTGACTTAACAAACCACCTGCATGCGCTTTACGCCCAGTAATTCCGATTAACGCTTGCACCCTCCGTA
>NZ_CP028827.1:2771824-2772076 Vibrio cholerae strain N16961 chromosome 1, complete sequence
CCTGTTTGCTCCCCACGCTTTCGCATCTGAGTGTCAGTATCTGTCCAGGGGGCCGCCTTCGCCACCGGTATTCCTTCAGATCTCTACGCATTTCACCGCTACACCTGAAATTCTACCCCCCTCTACAGTACTCTAGCTTGTCAGTTTCAAATGCGATTCCTAGGTTGAGCCCAGGGCTTTCACATCTGACTTAACAAACCACCTGCATGCGCTTTACGCCCAGTAATTCCGATTAACGCTTGCACCCTCCGTA
>NZ_CP028827.1:2945167-2945419 Vibrio cholerae strain N16961 chromosome 1, complete sequence
CCTGTTTGCTCCCCACGCTTTCGCATCTGAGTGTCAGTATCTGTCCAGGGGGCCGCCTTCGCCACCGGTATTCCTTCAGATCTCTACGCATTTCACCGCTACACCTGAAATTCTACCCCCCTCTACAGTACTCTAGCTTGTCAGTTTCAAATGCGATTCCTAGGTTGAGCCCAGGGCTTTCACATCTGACTTAACAAACCACCTGCATGCGCTTTACGCCCAGTAATTCCGATTAACGCTTGCACCCTCCGTA
"""

Q_NUM = PointCounter(0)

POINT_NUM = PointCounter(0)

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not Path(SCRIPT_PATH).exists():
            cls.submitted = False
            return cls
        
        if "__init__.py" in os.listdir:
            cls.format = "package"
            os.mkdir(f"{SUBMISSION_PATH}ispcr")
            for file in os.listdir():
                if file.endswith(".py"):
                    shutil.move(f"{SUBMISSION_PATH}{file}", f"{SUBMISSION_PATH}ispcr")
        else:
            cls.format = "module"
        cls.input_files = [
            "Vibrio_cholerae_N16961.fna",
            "general_16S_515f_806r.fna"
        ]
        for file in cls.input_files:
            shutil.copy(f"{DATA_DIR}{file}", f"{cls.dir}/")
        cls.submitted = True
        
        

        try: # import the package
            sys.path.append(SUBMISSION_PATH)
            import ispcr
            cls.pkg = ispcr
            cls.imported = True
        
        except Exception as e:
            cls.imported = False
            cls.error = e
        
        try: # run step 1
            if not hasattr(ispcr, "step_one"):
                raise("ispcr has no function 'step_one'")
            if not inspect.isfunction(ispcr.step_one):
                raise("ispcr.step_one is not a function")
            cls.step_one_result = ispcr.step_one(
                primer_file=f"{DATA_DIR}/general_16S_515f_806r.fna",
                assembly_file=f"{DATA_DIR}/Vibrio_cholerae_N16961.fna"
            )
            cls.step_one_ran = True
        except Exception as e:
            cls.step_one_ran = False
            cls.error = e
        
        try: # run step 2
            if not hasattr(ispcr, "step_two"):
                raise("ispcr has no function 'step_two'")
            if not inspect.isfunction(ispcr.step_two):
                raise("ispcr.step_two is not a function")
            cls.step_two_result = ispcr.step_two(
                sorted_hits=Q2_INPUT,
                max_amplicon_size=1000
            )
            cls.step_two_ran = True
        except Exception as e:
            cls.step_two_ran = False
            cls.error = e
        
        try: # run step 3
            if not hasattr(ispcr, "step_three"):
                raise("ispcr has no function 'step_three'")
            if not inspect.isfunction(ispcr.step_three):
                raise("ispcr.step_three is not a function")
            cls.step_three_result = ispcr.step_three(
                hit_pairs=Q3_INPUT,
                assembly_file=f"{DATA_DIR}/Vibrio_cholerae_N16961.fna"
            )
            cls.step_three_ran = True
        except Exception as e:
            cls.step_three_ran = False
            cls.error = e


    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM}")
    @visibility("hidden")
    def test_check_outputs(self):
        """secretly check student outputs"""
        if self.step_one_ran:
            print("step one output:")
            for thing in self.step_one_result:
                print(thing)
        if self.step_two_ran:
            print("step two output:")
            for thing in self.step_two_result:
                print(thing)
        if self.step_three_ran:
            print("step three output:")
            print(self.step_three_result)


    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("on_fail")
    def test_submitted_files(self):
        """Check submitted files"""
        missing_files = check_submitted_files([f'{SOLUTION_SCRIPT}', f'{SOLUTION_DIR}'])
        for path in missing_files:
            print(f'Missing {path}')
        self.assertEqual(
            len(missing_files),
            1,
            f'Missing your ispcr package or module, follow instructions carefully'
        )
        print(f'ispcr submitted successfully')
        print(f"Your submission was determined to be a {self.format}")

    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_import(self):
        """Check ispcr can be imported"""
        if not self.submitted:
            self.fail("ispcr was not submitted.")
        if not self.imported:
            self.fail(f"ispcr could not be imported due to an error:\n{self.error}")
        print("ispcr was imported successfully")
    

    @weight(0)
    @number(f"{Q_NUM.next()}.{POINT_NUM.reset(1)}")
    @visibility("visible")
    def test_step_one_runs(self):
        """Check step_one runs"""
        if not self.submitted:
            self.fail("ispcr was not submitted.")
        if not self.imported:
            self.fail(f"ispcr could not be imported due to an error:\n{self.error}")
        if not self.step_one_ran:
            self.fail(f"Step one failed with the error: {self.error}")
        print("step_one ran")
    
    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_step_one_output(self):
        """Check step_one output correct"""
        if not self.submitted:
            self.fail("ispcr was not submitted.")
        if not self.imported:
            self.fail(f"ispcr could not be imported due to an error:\n{self.error}")
        if not self.step_one_ran:
            self.fail(f"Step one failed with the error: {self.error}")
        # Check return type matches expected list[list[str]]
        if (
            isinstance(self.step_one_result, list) and
            isinstance(self.step_one_result[0], list) and
            isinstance(self.step_one_result[0][0], str)
        ):
            print("step_one return type matches expectation")
        else:
            self.fail("step_one return type is wrong")
        if self.step_one_result != Q2_INPUT:
            self.fail("step_one output does not match expected output")
        print("step_one output matches expected output")
        
        




    @weight(0)
    @number(f"{Q_NUM.next()}.{POINT_NUM.reset(1)}")
    @visibility("visible")
    def test_step_two_runs(self):
        """Check step_two runs"""
        if not self.submitted:
            self.fail("ispcr was not submitted.")
        if not self.imported:
            self.fail(f"ispcr could not be imported due to an error:\n{self.error}")
        if not self.step_two_ran:
            self.fail(f"Step two failed with the error: {self.error}")
        print("step_two ran")


    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_step_two_output(self):
        """Check step_two output correct"""
        if not self.submitted:
            self.fail("ispcr was not submitted.")
        if not self.imported:
            self.fail(f"ispcr could not be imported due to an error:\n{self.error}")
        if not self.step_two_ran:
            self.fail(f"Step two failed with the error: {self.error}")
        # Check return type matches expected list[list[str]]
        if (
            isinstance(self.step_two_result, list) and
            isinstance(self.step_two_result[0], tuple) and
            isinstance(self.step_two_result[0][0], list) and
            isinstance(self.step_two_result[0][0][0], str)
        ):
            print("step_two return type matches expectation")
        else:
            self.fail("step_two return type is wrong")
        if self.step_two_result != Q3_INPUT:
            self.fail("step_two output does not match expected output")
        print("step_two output matches expected output")




    @weight(0)
    @number(f"{Q_NUM.next()}.{POINT_NUM.reset(1)}")
    @visibility("visible")
    def test_step_two_runs(self):
        """Check step_two runs"""
        if not self.submitted:
            self.fail("ispcr was not submitted.")
        if not self.imported:
            self.fail(f"ispcr could not be imported due to an error:\n{self.error}")
        if not self.step_three_ran:
            self.fail(f"Step three failed with the error: {self.error}")
        print("step_two ran")

    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_step_three_output(self):
        """Check step_three output correct"""
        if not self.submitted:
            self.fail("ispcr was not submitted.")
        if not self.imported:
            self.fail(f"ispcr could not be imported due to an error:\n{self.error}")
        if not self.step_three_ran:
            self.fail(f"Step three failed with the error: {self.error}")
        # Check return type matches expected list[list[str]]
        if (isinstance(self.step_three_result, str)):
            print("step_three return type matches expectation")
        else:
            self.fail("step_three return type is wrong")
        if self.step_three_result != Q3_OUTPUT:
            self.fail("step_three output does not match expected output")
        print("step_three output matches expected output")
