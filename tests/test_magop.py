import unittest
from pathlib import Path
import shutil
import tempfile
import subprocess
import tempfile
import os
import re


from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import PointCounter

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "magop.py"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"
DATA_DIR = "/autograder/biol7200-autograders/data/"

Q_NUM = 1

POINT_NUM = PointCounter(0)

ALL_DATA_EXPECTED = "\n".join([
    # expected trees
    "((Pseudomonas_syringae_pv_tomato_str_DC3000_NC_004578.1:1.72,Pseudomonas_protegens_CHA0_NZ_LS999205.1:0.28):0.39,Pseudomonas_putida_NBRC_14164_NC_021505.1:0.61,((((((((ERR11767307:12.39,Fusibacter_paucivorans:15.61):8.01,(Leptospira_borgpetersenii:-0.02,SRR13255634:0.02):25.74):2.92,((SRR30750791:4.01,SRR28858832:5.99):2.38,Bacillus_subtilis:9.12):12.33):2.14,((Synechococcus_elongatus:21.69,SRR27732368:23.31):10.53,((SRR24886915:10.61,Methanococcus_aeolicus:9.39):24.69,(Sulfolobus_islandicus:15.04,ERR12954019:12.96):22.81):22.72):3.61):1.67,(Mycoplasma_pneumoniae:21.26,SRR25626983:21.74):14.46):3.58,((Wolbachia_NZ_CP046925.1:3.97,Wolbachia_pipientis:9.03):15.77,SRR24105535:17.73):9.02):7.87,((Vibrio_cholerae_strain_N16961_NZ_CP028827.1:0.00,ERR13716760:0.00):10.21,(Escherichia_coli:0.00,Escherichia_coli_str._K-12_substr._MG1655_NC_000913.3:0.00):9.79):10.31):8.90,(Pseudomonas_oleovorans_GD04132_NZ_CP104579.1:0.89,(SRR21376282:0.00,(Pseudomonas_aeruginosa_UCBPP-PA14_NC_008463.1:0.00,Pseudomonas_aeruginosa_PAO1_NC_002516.2:0.00):0.00):6.11):2.13):1.75):0.00;",
    # No reorient
    "(((SRR27732368:23.23,Synechococcus_elongatus:21.77):9.06,(((SRR24886915:10.65,Methanococcus_aeolicus:9.35):24.41,(ERR12954019:13.13,Sulfolobus_islandicus:14.87):23.09):10.96,Pseudomonas_oleovorans_GD04132_NZ_CP104579.1:101.29):11.94):2.00,(SRR25626983:21.68,Mycoplasma_pneumoniae:21.32):14.06,(((((SRR30750791:4.19,SRR28858832:5.81):2.44,Bacillus_subtilis:9.06):12.30,(ERR11767307:12.53,Fusibacter_paucivorans:15.47):7.20):3.12,(SRR13255634:-0.02,Leptospira_borgpetersenii:0.02):26.38):1.91,((SRR24105535:17.90,(Wolbachia_pipientis:8.92,Wolbachia_NZ_CP046925.1:4.08):15.60):9.25,(((SRR21376282:0.00,(Pseudomonas_aeruginosa_UCBPP-PA14_NC_008463.1:0.00,Pseudomonas_aeruginosa_PAO1_NC_002516.2:0.00):0.00):5.97,(Pseudomonas_syringae_pv_tomato_str_DC3000_NC_004578.1:1.58,(Pseudomonas_putida_NBRC_14164_NC_021505.1:0.52,Pseudomonas_protegens_CHA0_NZ_LS999205.1:0.48):0.42):4.53):9.63,((ERR13716760:0.00,Vibrio_cholerae_strain_N16961_NZ_CP028827.1:0.00):10.21,(Escherichia_coli:-0.02,Escherichia_coli_str._K-12_substr._MG1655_NC_000913.3:0.02):9.79):8.74):8.12):3.32):2.27):0.00;",
    ""
])

ASS_ONLY_EXPECTED = "\n".join([
    # Expected
    "(Pseudomonas_syringae_pv_tomato_str_DC3000_NC_004578.1:1.44,(Pseudomonas_putida_NBRC_14164_NC_021505.1:0.69,Pseudomonas_protegens_CHA0_NZ_LS999205.1:0.31):0.56,((Wolbachia_NZ_CP046925.1:37.92,(Vibrio_cholerae_strain_N16961_NZ_CP028827.1:9.29,Escherichia_coli_str._K-12_substr._MG1655_NC_000913.3:10.71):11.08):7.88,(Pseudomonas_oleovorans_GD04132_NZ_CP104579.1:0.94,(Pseudomonas_aeruginosa_UCBPP-PA14_NC_008463.1:0.00,Pseudomonas_aeruginosa_PAO1_NC_002516.2:0.00):6.06):2.12):1.69):0.00;",
    # No reorient
    "(Pseudomonas_syringae_pv_tomato_str_DC3000_NC_004578.1:1.34,(Pseudomonas_putida_NBRC_14164_NC_021505.1:0.59,Pseudomonas_protegens_CHA0_NZ_LS999205.1:0.41):0.66,(((Wolbachia_NZ_CP046925.1:27.79,Pseudomonas_oleovorans_GD04132_NZ_CP104579.1:123.21):8.68,(Vibrio_cholerae_strain_N16961_NZ_CP028827.1:9.29,Escherichia_coli_str._K-12_substr._MG1655_NC_000913.3:10.71):9.57):8.33,(Pseudomonas_aeruginosa_UCBPP-PA14_NC_008463.1:0.00,Pseudomonas_aeruginosa_PAO1_NC_002516.2:0.00):7.04):3.41):0.00;",
    ""
])

ASS_REFS_EXPECTED = "\n".join([
    # Expected
    "((((Wolbachia_pipientis:9.07,Wolbachia_NZ_CP046925.1:3.93):24.25,(((Escherichia_coli:0.00,Escherichia_coli_str._K-12_substr._MG1655_NC_000913.3:0.00):9.50,Vibrio_cholerae_strain_N16961_NZ_CP028827.1:10.50):8.82,(((Pseudomonas_syringae_pv_tomato_str_DC3000_NC_004578.1:1.65,(Pseudomonas_putida_NBRC_14164_NC_021505.1:0.50,Pseudomonas_protegens_CHA0_NZ_LS999205.1:0.50):0.35):2.06,Pseudomonas_oleovorans_GD04132_NZ_CP104579.1:2.44):1.75,(Pseudomonas_aeruginosa_UCBPP-PA14_NC_008463.1:0.00,Pseudomonas_aeruginosa_PAO1_NC_002516.2:0.00):4.75):11.12):9.47):3.06,Bacillus_subtilis:22.69):0.44,((Synechococcus_elongatus:29.93,Mycoplasma_pneumoniae:35.07):2.86,(Sulfolobus_islandicus:37.06,Methanococcus_aeolicus:33.94):25.39):1.02,(Fusibacter_paucivorans:22.66,Leptospira_borgpetersenii:25.34):2.61):0.00;",
    # No reorient
    "((((Wolbachia_pipientis:8.91,Wolbachia_NZ_CP046925.1:4.09):24.26,(((Escherichia_coli:-0.04,Escherichia_coli_str._K-12_substr._MG1655_NC_000913.3:0.04):9.09,Vibrio_cholerae_strain_N16961_NZ_CP028827.1:10.91):8.57,((Pseudomonas_syringae_pv_tomato_str_DC3000_NC_004578.1:1.58,(Pseudomonas_putida_NBRC_14164_NC_021505.1:0.52,Pseudomonas_protegens_CHA0_NZ_LS999205.1:0.48):0.43):4.36,(Pseudomonas_aeruginosa_UCBPP-PA14_NC_008463.1:0.00,Pseudomonas_aeruginosa_PAO1_NC_002516.2:0.00):6.14):9.80):9.31):3.21,((Synechococcus_elongatus:29.72,((Sulfolobus_islandicus:37.30,Methanococcus_aeolicus:33.70):10.00,Pseudomonas_oleovorans_GD04132_NZ_CP104579.1:100.50):13.28):1.32,Mycoplasma_pneumoniae:34.55):3.41):0.42,Bacillus_subtilis:22.77,(Fusibacter_paucivorans:23.46,Leptospira_borgpetersenii:24.54):2.73):0.00;",
    ""
])

READ_REFS_EXPECTED = "\n".join([
    # Expected
    "(((SRR27732368:24.29,Synechococcus_elongatus:20.71):9.14,((SRR24886915:10.12,Methanococcus_aeolicus:9.88):23.37,(ERR12954019:14.17,Sulfolobus_islandicus:13.83):24.13):24.11):2.45,((SRR25626983:22.35,Mycoplasma_pneumoniae:20.65):15.45,((SRR24105535:17.85,Wolbachia_pipientis:24.15):9.70,(SRR21376282:16.97,(ERR13716760:10.94,Escherichia_coli:9.06):10.53):6.30):2.42):1.70,((((SRR30750791:4.23,SRR28858832:5.77):3.22,Bacillus_subtilis:8.28):12.59,(ERR11767307:12.56,Fusibacter_paucivorans:15.44):6.91):2.42,(SRR13255634:-0.03,Leptospira_borgpetersenii:0.03):27.08):1.80):0.00;",
    # same again to use the same R script
    "(((SRR27732368:24.29,Synechococcus_elongatus:20.71):9.14,((SRR24886915:10.12,Methanococcus_aeolicus:9.88):23.37,(ERR12954019:14.17,Sulfolobus_islandicus:13.83):24.13):24.11):2.45,((SRR25626983:22.35,Mycoplasma_pneumoniae:20.65):15.45,((SRR24105535:17.85,Wolbachia_pipientis:24.15):9.70,(SRR21376282:16.97,(ERR13716760:10.94,Escherichia_coli:9.06):10.53):6.30):2.42):1.70,((((SRR30750791:4.23,SRR28858832:5.77):3.22,Bacillus_subtilis:8.28):12.59,(ERR11767307:12.56,Fusibacter_paucivorans:15.44):6.91):2.42,(SRR13255634:-0.03,Leptospira_borgpetersenii:0.03):27.08):1.80):0.00;",
    ""
])

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
                    if file == SOLUTION_SCRIPT:
                        Path(f"{SCRIPT_PATH}").chmod(0o777)
                        continue
                    shutil.move(f"{SUBMISSION_PATH}{file}", f"{SUBMISSION_PATH}magnumopus")
        elif "magnumopus.py" in os.listdir(SUBMISSION_PATH):
            cls.format = "module"
        else:
            return cls

        shutil.copytree(f"{DATA_DIR}data", f"{cls.dir}/data")

 
        
        if not Path(SCRIPT_PATH).exists():
            return cls

        cls.submitted = True
        
        cls.magop_ran = False
        cls.magop_error = ""
        # Store help message of magop.py
        if not Path(f"{SCRIPT_PATH}").exists():
            cls.magop_error = "File not found"
            return cls

        Path(f"{SCRIPT_PATH}").chmod(0o777)

        pattern = re.compile(r"\#\![ ]?/usr/bin/env python3")
        with open(f"{SCRIPT_PATH}") as f:
            first_line = f.readline()
        if re.match(pattern, first_line):
            cls.shebang = True
        else:
            cls.magop_error = "Missing or invalid shebang"
            return cls
        
        command = [f"{SCRIPT_PATH}", "-h"]
                   
        try:
            cls.magop_help_result = subprocess.run(
                command,
                text=True,
                capture_output=True
            )
            cls.magop_ran = True
        except Exception as e:
            cls.magop_error = f"Couldn't run magop.py due to an exception: {Exception}"
            return cls

        # Run magop.py will all inputs
        command = " ".join([
            f"{SCRIPT_PATH}",
            "-a", "data/assemblies/*",
            "-p", "data/primers/general_16S_515f_806r.fna",
            "-r", "data/reads/*",
            "-s", "data/refs/V4_plus_5.fna"
        ])
                   
        cls.magop_all_result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            cwd=cls.dir
        )

        # just assemblies
        command = " ".join([
            f"{SCRIPT_PATH}",
            "-a", "data/assemblies/*",
            "-p", "data/primers/general_16S_515f_806r.fna"
        ])
                   
        cls.magop_ass_result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            cwd=cls.dir
        )

        # assemblies and refs
        command = " ".join([
            f"{SCRIPT_PATH}",
            "-a", "data/assemblies/*",
            "-p", "data/primers/general_16S_515f_806r.fna",
            "-s", "data/refs/V4_plus_5.fna"
        ])
                   
        cls.magop_ass_ref_result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            cwd=cls.dir
        )

        # reads and refs
        command = " ".join([
            f"{SCRIPT_PATH}",
            "-p", "data/primers/general_16S_515f_806r.fna",
            "-r", "data/reads/*",
            "-s", "data/refs/V4_plus_5.fna"
        ])
                   
        cls.magop_read_ref_result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            cwd=cls.dir
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir)

    def basic_fail(self):
        """Check submitted files"""
        if not self.submitted:
            self.fail("Your submission is lacking a magnumopus.py file or an __init__.py file and can't be processed.")
        if not self.magop_ran:
            self.fail(f"Your {SOLUTION_SCRIPT} could not be run due to an error: {self.magop_error}")

    def compare_trees(self, ref_trees: str, query_tree: str) -> list[float]:
        with tempfile.NamedTemporaryFile() as ref_file, tempfile.NamedTemporaryFile() as query_file:
            with open(ref_file.name, 'w') as f:
                f.write(ref_trees)
            with open(query_file.name, 'w') as f:
                f.write(query_tree)
            
            command = [
                "./compare_trees.r",
                f"{query_file.name}",
                f"{ref_file.name}"
            ]

            result = subprocess.run(
                command,
                text=True,
                capture_output=True
            )

        if result.stdout.strip() == "":
            self.fail(
                f"Could not process your output tree. Your tree was\n{query_tree}\n"
                f"The error was {result.stderr}"
            )
        
        scores = [float(i) for i in re.findall(r"(?<=\s)(\d\.\d+|\d)(?=(?:\s|$))", result.stdout)]
        
        return scores


    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM}")
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

    @weight(12.5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_all_outputs(self):
        """Assess magop output when given all inputs"""
        self.basic_fail()
        if self.magop_all_result.stderr.strip() != "":
            self.fail(f"Your script produced an error:\n{self.magop_all_result.stderr}")
        print("Comparing your tree to the expected tree...")
        print(f"Your script output\n{self.magop_all_result.stdout}")
        print(f"\nExpected tree is:\n{ALL_DATA_EXPECTED.split()[0]}")
        scores = self.compare_trees(ALL_DATA_EXPECTED, self.magop_all_result.stdout)

        if scores[0] < 0.002:
            print("Your tree closely matches the expected tree")
            return
        if scores[1] < 0.002:
            self.fail("Your tree indicates you forgot to make sure all your amplicons are aligned in the best orientation.")

        self.fail("Your tree can't be automatically diagnosed. That means you have made an uncommon error. Try viewing your amplicons, checking that your NW settings are 1, -1, -1, and eyeballing the tree. Those are common place where mistakes are made.")

    @weight(12.5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_assembly_outputs(self):
        """Assess magop output when given assembly inputs only"""
        self.basic_fail()
        if self.magop_ass_result.stderr.strip() != "":
            self.fail(f"Your script produced an error:\n{self.magop_ass_result.stderr}")
        print("Comparing your tree to the expected tree...")
        print(f"Your script output\n{self.magop_ass_result.stdout}")
        print(f"\nExpected tree is:\n{ASS_ONLY_EXPECTED.split()[0]}")
        scores = self.compare_trees(ASS_ONLY_EXPECTED, self.magop_ass_result.stdout)

        if scores[0] == 0:
            print("Your tree closely matches the expected tree")
            return
        if scores[1] == 0:
            self.fail("Your tree indicates you forgot to make sure all your amplicons are aligned in the best orientation.")

        self.fail("Your tree can't be automatically diagnosed. That means you have made an uncommon error. Try viewing your amplicons, checking that your NW settings are 1, -1, -1, and eyeballing the tree. Those are common place where mistakes are made.")

    @weight(12.5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_assembly_ref_outputs(self):
        """Assess magop output when given assembly and reference sequence inputs"""
        self.basic_fail()
        if self.magop_ass_ref_result.stderr.strip() != "":
            self.fail(f"Your script produced an error:\n{self.magop_ass_ref_result.stderr}")
        print("Comparing your tree to the expected tree...")
        print(f"Your script output\n{self.magop_ass_ref_result.stdout}")
        print(f"\nExpected tree is:\n{ASS_REFS_EXPECTED.split()[0]}")
        scores = self.compare_trees(ASS_REFS_EXPECTED, self.magop_ass_ref_result.stdout)

        if scores[0] == 0:
            print("Your tree closely matches the expected tree")
            return
        if scores[1] == 0:
            self.fail("Your tree indicates you forgot to make sure all your amplicons are aligned in the best orientation.")

        self.fail("Your tree can't be automatically diagnosed. That means you have made an uncommon error. Try viewing your amplicons, checking that your NW settings are 1, -1, -1, and eyeballing the tree. Those are common place where mistakes are made.")

    @weight(12.5)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_read_ref_outputs(self):
        """Assess magop output when given only reads and reference sequence inputs"""
        self.basic_fail()
        if self.magop_read_ref_result.stderr.strip() != "":
            self.fail(f"Your script produced an error:\n{self.magop_read_ref_result.stderr}")
        print("Comparing your tree to the expected tree...")
        print(f"Your script output\n{self.magop_read_ref_result.stdout}")
        print(f"\nExpected tree is:\n{READ_REFS_EXPECTED.split()[0]}")
        scores = self.compare_trees(READ_REFS_EXPECTED, self.magop_read_ref_result.stdout)
        

        if scores[0] == 0:
            print("Your tree closely matches the expected tree")
            return

        self.fail("Your tree can't be automatically diagnosed. That means you have made an uncommon error. Try viewing your amplicons, checking that your NW settings are 1, -1, -1, and eyeballing the tree. Those are common place where mistakes are made.")
