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

    
    @weight(1)
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

    @weight(1)
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

    @weight(1)
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


    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_read_is_a_class(self):
        """Is Read a class"""
        if not self.imported:
            self.fail(f"Unable to import magnumopus.sam.Read")
        if not inspect.isclass(self.read_class):
            self.fail(f"Read is not a class, but an instance of {self.read_class.__class__.__name__}")
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_read_class_can_be_instantiated(self):
        """Can the Read class be instantiated from a SAM entry"""
        try:
            _ = self.read_class(test_data.TEST_READ_F_MAPPED)
        except Exception as e:
            self.fail(f"Your Read class __init__ method does not create an instance of the class when given a SAM entry:\n{e}")
        print("yes")
    
    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_is_mapped_attr_exists(self):
        """Is the 'is_mapped' attribute defined"""
        self.basic_fail()
        read_instance = self.read_class(test_data.TEST_READ_F_MAPPED)
        check_class_attribute(read_instance, "is_mapped")
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_is_forward_attr_exists(self):
        """Is the 'is_forward' attribute defined"""
        self.basic_fail()
        read_instance = self.read_class(test_data.TEST_READ_F_MAPPED)
        check_class_attribute(read_instance, "is_forward")
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_is_reverse_attr_exists(self):
        """Is the 'is_reverse' attribute defined"""
        self.basic_fail()
        read_instance = self.read_class(test_data.TEST_READ_F_MAPPED)
        check_class_attribute(read_instance, "is_reverse")
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_is_primary_attr_exists(self):
        """Is the 'is_primary' attribute defined"""
        self.basic_fail()
        read_instance = self.read_class(test_data.TEST_READ_F_MAPPED)
        check_class_attribute(read_instance, "is_primary")
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_init_method_implemented(self):
        """Is there a callable __init__ method defined"""
        self.basic_fail()
        check_class_method(self.read_class, "__init__")
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_base_at_pos_method_implemented(self):
        """Is there a callable base_at_pos method defined"""
        self.basic_fail()
        check_class_method(self.read_class, "base_at_pos")
        print("yes")
    
    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_qual_at_pos_method_implemented(self):
        """Is there a callable qual_at_pos method defined"""
        self.basic_fail()
        check_class_method(self.read_class, "qual_at_pos")
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_mapped_seq_method_implemented(self):
        """Is there a callable mapped_seq method defined"""
        self.basic_fail()
        check_class_method(self.read_class, "mapped_seq")
        print("yes")


    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_is_forward_with_forward(self):
        """Is the is_forward attribute set properly"""
        self.basic_fail()
        check_attribute_value(
            instance=self.read_class(test_data.TEST_READ_F_MAPPED),
            attr="is_forward",
            expected=True,
            tested_data="forward-mapped read"
        )
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_is_reverse_with_forward(self):
        """Is the is_reverse attribute set properly"""
        self.basic_fail()
        check_attribute_value(
            instance=self.read_class(test_data.TEST_READ_F_MAPPED),
            attr="is_reverse",
            expected=False,
            tested_data="forward-mapped read"
        )
        print("yes")
    
    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_is_forward_with_reverse(self):
        """Is the is_forward attribute set properly"""
        self.basic_fail()
        check_attribute_value(
            instance=self.read_class(test_data.TEST_READ_R_MAPPED),
            attr="is_forward",
            expected=False,
            tested_data="reverse-mapped read"
        )
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_is_reverse_with_reverse(self):
        """Is the is_reverse attribute set properly"""
        self.basic_fail()
        check_attribute_value(
            instance=self.read_class(test_data.TEST_READ_R_MAPPED),
            attr="is_reverse",
            expected=True,
            tested_data="reverse-mapped read"
        )
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_is_mapped_with_mapped(self):
        """Is the is_mapped attribute set properly"""
        self.basic_fail()
        check_attribute_value(
            instance=self.read_class(test_data.TEST_READ_F_MAPPED),
            attr="is_mapped",
            expected=True,
            tested_data="mapped read"
        )
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_is_mapped_with_unmapped(self):
        """Is the is_mapped attribute set properly"""
        self.basic_fail()
        check_attribute_value(
            instance=self.read_class(test_data.TEST_READ_UNMAPPED),
            attr="is_mapped",
            expected=False,
            tested_data="unmapped read"
        )
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_is_primary_with_primary(self):
        """Is the is_primary attribute set properly"""
        self.basic_fail()
        check_attribute_value(
            instance=self.read_class(test_data.TEST_READ_F_MAPPED),
            attr="is_primary",
            expected=True,
            tested_data="primary read mapping"
        )
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_is_primary_with_secondary(self):
        """Is the is_primary attribute set properly"""
        self.basic_fail()
        check_attribute_value(
            instance=self.read_class(test_data.TEST_READ_F_SECONDARY),
            attr="is_primary",
            expected=False,
            tested_data="secondary read mapping"
        )
        print("yes")

    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_is_primary_with_supplemental(self):
        """Is the is_primary attribute set properly"""
        self.basic_fail()
        check_attribute_value(
            instance=self.read_class(test_data.TEST_READ_F_SUPPLEMENTAL),
            attr="is_primary",
            expected=False,
            tested_data="supplemental read mapping"
        )
        print("yes")


    @weight(1)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_init_creates_instance(self):
        """Does the Read.__init__ return an instance of Read"""
        self.basic_fail()
        if not isinstance(self.read_class(test_data.TEST_READ_F_MAPPED), self.read_class):
            self.fail(f"Your Read class __init__ method does not create an instance of the class when given a SAM entry")
        print("yes")
    
    @weight(3)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_just_M_read_at_pos(self):
        """Does the base_at_pos method return the right base when the read doesn't map to the first reference base"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_CIGAR_M_ONLY_NON_1_POS),
            method="base_at_pos",
            args=(13,), # comma specifies this is a single element tuple. Just here to satisfy syntax rules
            expected="G",
            tested_data="read with only M in CIGAR, but that doesn't map to the start of the reference"
        )
        print("yes")
    
    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_del_read_at_pos(self):
        """Does the base_at_pos method return the right base when there is a deletion in the read at the requested location"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_CIGAR_D_12),
            method="base_at_pos",
            args=(13,),
            expected="",
            tested_data="read with deletion at requested location"
        )
        print("yes")
    
    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_upstream_del_read_at_pos(self):
        """Does the base_at_pos method return the right base when there is a deletion in the read before the requested location"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_CIGAR_D_12),
            method="base_at_pos",
            args=(14,),
            expected="G",
            tested_data="read with deletion before requested location"
        )
        print("yes")

    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_ins_read_at_pos(self):
        """Does the base_at_pos method return the right base when there is an insertion in the read at the requested location"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_CIGAR_I_10),
            method="base_at_pos",
            args=(10,),
            expected="GC",
            tested_data="read with insertion at requested location"
        )
        print("yes")

    @weight(5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_upstream_ins_read_at_pos_internal_pos(self):
        """Does the base_at_pos method return the right base when there is an insertion in the read before the requested location"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_CIGAR_I_10),
            method="base_at_pos",
            args=(14,),
            expected="G",
            tested_data="read with insertion before (i.e., 5') requested location"
        )
        print("yes")

    @weight(3)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_upstream_ins_read_at_pos_beyond_read(self):
        """Does the base_at_pos method return the right base when there is an insertion in the read that reduces the mapped length to less than the read length"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_CIGAR_I_10),
            method="base_at_pos",
            args=(150,),
            expected="",
            tested_data="read with insertion before (i.e., 5') requested location when position equal to read POS + read SEQ length requested"
        )
        print("yes")
    
    @weight(3)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_downstream_del_read_at_pos(self):
        """Is the base_at_pos method impacted if there is a deletion in the read after the requested location"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_CIGAR_D_12),
            method="base_at_pos",
            args=(10,),
            expected="G",
            tested_data="read with deletion after (i.e., 3') requested location"
        )
        print("yes")

    @weight(3)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_mapped_right_of_requested_pos_read_at_pos(self):
        """Does base_at_pos return an empty string for reads that map to the right of requested location"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_F_MAPPED),
            method="base_at_pos",
            args=(10,),
            expected="",
            tested_data="read maps to the right of requested location"
        )
        print("yes")

    @weight(3)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_first_base_in_read_read_at_pos(self):
        """Does base_at_pos return an the right base for the first position in the read"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_F_MAPPED),
            method="base_at_pos",
            args=(16,),
            expected="G",
            tested_data="requested is the first base in the read"
        )
        print("yes")
    
    @weight(3)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_mapped_left_of_requested_pos_read_at_pos(self):
        """Does base_at_pos return an empty string for reads that map to the left of requested location"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_F_MAPPED),
            method="base_at_pos",
            args=(167,),
            expected="",
            tested_data="read maps to the left of requested location"
        )
        print("yes")

    @weight(3)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_last_base_in_read_read_at_pos(self):
        """Does base_at_pos return the right read when the requested pos is the last base in the read"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_F_MAPPED),
            method="base_at_pos",
            args=(166,),
            expected="C",
            tested_data="requested is the last base in the read"
        )
        print("yes")

    @weight(3)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_unmapped_read_pos_read_at_pos(self):
        """Does the base_at_pos method return an empty string for unmapped reads"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_UNMAPPED),
            method="base_at_pos",
            args=(10,),
            expected="",
            tested_data="unmapped read"
        )
        print("yes")

    @weight(3)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_soft_clipped_upstream_read_at_pos(self):
        """Does the base_at_pos method correctly handle soft clipping"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_SOFT_CLIP),
            method="base_at_pos",
            args=(13,),
            expected="G",
            tested_data="read with soft clipping before requested location"
        )
        print("yes")
    
    @weight(3)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_hard_clipped_upstream_read_at_pos(self):
        """Does the base_at_pos method correctly handle hard clipping"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_HARD_CLIP),
            method="base_at_pos",
            args=(13,),
            expected="G",
            tested_data="read with hard clipping before requested location"
        )
        print("yes")

    @weight(3)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_internally_mapped_read_at_pos(self):
        """Does the base_at_pos method return the right base for a position in the middle of the reference"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_CIGAR_M_ONLY_NON_1_POS),
            method="base_at_pos",
            args=(50,),
            expected="C",
            tested_data="read with only M in CIGAR, that maps to somewhere in the middle of the reference"
        )
        print("yes")

    @weight(4)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_internally_mapped_mapped_seq(self):
        """Does the mapped_seq method return the right sequence for a read mapped to the middle of the reference"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_CIGAR_M_ONLY_NON_1_POS),
            method="mapped_seq",
            expected="CAGCAGCCGCGGTAATACGAAGGGTGCAAGCGTTAATCGGAATTACTGGGCGTAAAGCGCGCGTAGGTGGTTCAGCAAGTTGGATGTGAAATCCCCGGGCTCAACCTGGGAACTGCATCCAAAACTACTGAGCTAGAGTACGGTAGAGGGT",
            tested_data="read with only M in CIGAR, that maps to somewhere in the middle of the reference"
        )
        print("yes")

    @weight(4)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_deletion_mapped_seq(self):
        """Does the mapped_seq method handle deletions correctly"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_CIGAR_D_12),
            method="mapped_seq",
            expected="GTGCCAGCAGCC-GCGGTAATACGAAGGGTGCAAGCGTTAATCGGAATTACTNGGCGTAAAGCGCGCGTAGGTGGTTCAGCAAGTTGGATGTGAAATCCCCGGGCTCAACCTGGGAACTGCATCCAAAACTACTGAGCTAGAGTACGGTAG",
            tested_data="read with a deletion relative to the reference"
        )
        print("yes")
    
    @weight(4)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_insertion_mapped_seq(self):
        """Does the mapped_seq method handle insertions correctly"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_CIGAR_I_10),
            method="mapped_seq",
            expected="GTGCCAGCAGCCGCGGTAATACGAAGGGTGCAAGCGTTAATCGGAATTACTNGGCGTAAAGCGCGCGTAGGTGGTTCAGCAAGTTGGATGTGAAATCCCCGGGCTCAACCTGGGAACTGCATCCAAAACTACTGAGCTAGAGTACGGTAG",
            tested_data="read with an insertion relative to the reference"
        )
        print("yes")

    @weight(4)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_soft_clipped_mapped_seq(self):
        """Does the mapped_seq method handle soft clipping correctly"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_SOFT_CLIP),
            method="mapped_seq",
            expected="GTGCCAGCAGCCGCGGTAATACGAAGGGTGCAAGCGTTAATCGGAATTACTGGGCGTAAAGCGCGCGTAGGTGGTTCAGCAAGTTGGATGTGAAATCCCCGGGCTCAACCTGGGAACTGCATCCAAAACTACTG",
            tested_data="read with an insertion relative to the reference"
        )
        print("yes")

    @weight(4)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_hard_clipped_mapped_seq(self):
        """Does the mapped_seq method handle hard clipping correctly"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_HARD_CLIP),
            method="mapped_seq",
            expected="GTGCCAGCAGCCGCGGTAATACGAAGGGTGCAAGCGTTAATCGGAATTACTGGGCGTAAAGCGCGCGTAGGTGGTTCAGCAAGTTGGATGTGAAATCCCCGGGCTCAACCTGGGAACTGCATCCAAAACTACTG",
            tested_data="read with an insertion relative to the reference"
        )
        print("yes")

    @weight(4)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_unmapped_mapped_seq(self):
        """Does the mapped_seq method handle unmapped reads correctly"""
        self.basic_fail()
        check_method_output(
            instance=self.read_class(test_data.TEST_READ_UNMAPPED),
            method="mapped_seq",
            expected="",
            tested_data="unmapped read"
        )
        print("yes")
