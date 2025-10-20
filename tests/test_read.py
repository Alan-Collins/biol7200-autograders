import unittest
import shutil
import os
import sys
import inspect

from gradescope_utils.autograder_utils.decorators import weight, number, visibility

from utils import (
    PointCounter,
    check_attribute_value,
    check_class_attribute,
    check_class_method,
    check_method_output
)
import data as test_data

SUBMISSION_PATH = "/autograder/submission/"

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
            from magnumopus.sam import Read
            cls.read_class = Read
            cls.imported = True
        
        except Exception as e:
            cls.imported = False
            cls.error = e
        
        try:
            _ = Read(test_data.TEST_READ_F_MAPPED)
            cls.can_instance = True
        except:
            cls.can_instance = False

    def basic_fail(self):
        if not self.submitted:
            self.fail("Your submission is lacking a magnumopus.py file or an __init__.py file and can't be processed.")
        if not self.imported:
            self.fail(f"Unable to import magnumopus.sam.Read")
        if not self.can_instance:
            self.fail("Unable to create an instance of your Read class")


    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM}")
    @visibility("visible")
    def test_submitted_files(self):
        """Check submitted files"""
        if not self.submitted:
            self.fail("Your submission is lacking a magnumopus.py file or an __init__.py file and can't be processed.")
        else:
            print(f"magnumopus {self.format} submitted successfully")

    
    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_magop_import(self):
        """Check magnumopus import"""
        if not self.imported:
            # Something about importing isn't working.
            try:
                sys.path.append(SUBMISSION_PATH)
                import magnumopus
            except Exception as e:
                self.fail(
                    f"Unable to import your magnumopus {self.format} due to error:\n{e}"
                )
        print(f"magnumopus {self.format} imported successfully")

    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_sam_import(self):
        """Check magnumopus.sam import"""
        if not self.imported:
            # Something about importing isn't working.
            try:
                sys.path.append(SUBMISSION_PATH)
                import magnumopus.sam
            except Exception as e:
                self.fail(
                    f"Unable to import your magnumopus.sam due to error:\n{e}"
                )
        print(f"magnumopus.sam imported successfully")

    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_read_import(self):
        """Check magnumopus import"""
        if not self.imported:
            # Something about importing isn't working.
            try:
                sys.path.append(SUBMISSION_PATH)
                import magnumopus.sam.Read
            except Exception as e:
                self.fail(
                    f"Unable to import magnumopus.sam.Read due to error:\n{e}"
                )
        print(f"magnumopus.sam.Read imported successfully")


    def test_read_is_a_class(self):
        """Is Read a class"""
        if not self.imported:
            self.fail(f"Unable to import magnumopus.sam.Read")
        if not inspect.isclass(self.read_class):
            self.fail(f"Read is not a class, but an instance of {self.read_class.__class__.__name__}")

    def test_read_class_can_be_instantiated(self):
        """Can the Read class be instantiated from a SAM entry"""
        try:
            _ = self.read_class(test_data.TEST_READ_F_MAPPED)
        except Exception as e:
            self.fail(f"Your Read class __init__ method does not create an instance of the class when given a SAM entry:\n{e}")
    
    def test_is_mapped_attr_exists(self):
        """Is the 'is_mapped' attribute defined"""
        self.basic_fail()
        read_instance = self.read_class(test_data.TEST_READ_F_MAPPED)
        check_class_attribute(read_instance, "is_mapped")

    def test_is_forward_attr_exists(self):
        """Is the 'is_forward' attribute defined"""
        self.basic_fail()
        read_instance = self.read_class(test_data.TEST_READ_F_MAPPED)
        check_class_attribute(read_instance, "is_forward")

    def test_is_reverse_attr_exists(self):
        """Is the 'is_reverse' attribute defined"""
        self.basic_fail()
        read_instance = self.read_class(test_data.TEST_READ_F_MAPPED)
        check_class_attribute(read_instance, "is_reverse")

    def test_is_primary_attr_exists(self):
        """Is the 'is_primary' attribute defined"""
        self.basic_fail()
        read_instance = self.read_class(test_data.TEST_READ_F_MAPPED)
        check_class_attribute(read_instance, "is_primary")

    def test_init_method_implemented(self):
        """Is there a callable __init__ method defined"""
        self.basic_fail()
        check_class_method(self.read_class, "__init__")

    def test_base_at_pos_method_implemented(self):
        """Is there a callable base_at_pos method defined"""
        self.basic_fail()
        check_class_method(self.read_class, "base_at_pos")
    
    def test_qual_at_pos_method_implemented(self):
        """Is there a callable qual_at_pos method defined"""
        self.basic_fail()
        check_class_method(self.read_class, "qual_at_pos")

    def test_mapped_seq_method_implemented(self):
        """Is there a callable mapped_seq method defined"""
        self.basic_fail()
        check_class_method(self.read_class, "mapped_seq")
