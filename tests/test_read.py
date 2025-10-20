import unittest
import shutil
import os
import sys

from gradescope_utils.autograder_utils.decorators import weight, number, visibility

from utils import PointCounter

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


    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
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
