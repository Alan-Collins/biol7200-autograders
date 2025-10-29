import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import shutil
import os
import sys
import inspect

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import (
    PointCounter,
    check_class_method,
    check_method_output
)
import data as test_data

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "map_consensus.py"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"
DATA_DIR = "/autograder/biol7200-autograders/data/"

Q_NUM = 1

POINT_NUM = PointCounter(0)

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.submitted = False
        
        if "__init__.py" in os.listdir(SUBMISSION_PATH):
            cls.format = "package"
            os.mkdir(f"{SUBMISSION_PATH}magnumopus")
            for file in os.listdir(SUBMISSION_PATH):
                if file.endswith(".py"):
                    if file == "map_consensus.py":
                        Path(f"{SUBMISSION_PATH}map_consensus.py").chmod(0o777)
                        continue
                    shutil.move(f"{SUBMISSION_PATH}{file}", f"{SUBMISSION_PATH}magnumopus")
        elif "magnumopus.py" in os.listdir(SUBMISSION_PATH):
            cls.format = "module"
        else:
            return cls
        
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
    @visibility("on_fail")
    def test_line_endings(self):
        """Check unix line endings"""
        if not self.submitted:
            self.fail("No script was submitted")
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

    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("on_fail")
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

    @weight(1)
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

    @weight(1)
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

    @weight(1)
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

    @weight(1)
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

    @weight(1)
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
    def test_consensus_method_exists(self):
        """Does the SAM class have a 'consensus' method"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "consensus")
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_best_consensus_method_exists(self):
        """Does the SAM class have a 'best_consensus' method"""
        self.basic_fail()
        self.check_class_method(self.sam_class, "best_consensus")
        print("yes")
