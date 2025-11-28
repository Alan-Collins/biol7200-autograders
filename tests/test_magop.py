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
    # Preferring gaps in traceback
    "((Pseudomonas_syringae_pv_tomato_str_DC3000_NC_004578.1:1.72,Pseudomonas_protegens_CHA0_NZ_LS999205.1:0.28):0.35,Pseudomonas_putida_NBRC_14164_NC_021505.1:0.65,((((((((SRR30750791:3.73,SRR28858832:6.27):2.64,Bacillus_subtilis:8.86):11.38,(ERR11767307:12.19,Fusibacter_paucivorans:15.81):8.87):3.09,(((SRR27732368:23.21,Synechococcus_elongatus:21.79):11.00,((SRR24886915:10.63,Methanococcus_aeolicus:9.37):25.03,(ERR12954019:13.56,Sulfolobus_islandicus:14.44):22.47):24.75):1.20,(SRR13255634:0.02,Leptospira_borgpetersenii:-0.02):28.55):1.50):2.71,(SRR25626983:22.51,Mycoplasma_pneumoniae:21.49):15.36):2.91,(SRR24105535:18.03,(Wolbachia_NZ_CP046925.1:3.95,Wolbachia_pipientis:9.05):15.47):9.01):8.16,((ERR13716760:0.00,Vibrio_cholerae_strain_N16961_NZ_CP028827.1:0.00):10.40,(Escherichia_coli_str._K-12_substr._MG1655_NC_000913.3:0.00,Escherichia_coli:0.00):9.60):10.73):9.15,((SRR21376282:0.00,(Pseudomonas_aeruginosa_UCBPP-PA14_NC_008463.1:0.00,Pseudomonas_aeruginosa_PAO1_NC_002516.2:0.00):0.00):6.15,Pseudomonas_oleovorans_GD04132_NZ_CP104579.1:0.85):2.14):1.74):0.00;",
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
    # distance = num_mismatches / len_alignment
    "((((Wolbachia_pipientis:0.03534124046564102,Wolbachia_NZ_CP046925.1:0.015639154240489006):0.0925878956913948,(((Escherichia_coli:0.0,Escherichia_coli_str._K-12_substr._MG1655_NC_000913.3:0.0):0.03738344833254814,Vibrio_cholerae_strain_N16961_NZ_CP028827.1:0.04074155166745186):0.03454092890024185,(((Pseudomonas_syringae_pv_tomato_str_DC3000_NC_004578.1:0.006461316719651222,(Pseudomonas_putida_NBRC_14164_NC_021505.1:0.0020134293008595705,Pseudomonas_protegens_CHA0_NZ_LS999205.1:0.0019391401438042521):0.0014438217040151358):0.007907647639513016,Pseudomonas_oleovorans_GD04132_NZ_CP104579.1:0.00978943333029747):0.006725793704390526,(Pseudomonas_aeruginosa_UCBPP-PA14_NC_008463.1:0.0,Pseudomonas_aeruginosa_PAO1_NC_002516.2:0.0):0.018630018457770348):0.042924150824546814):0.03495058789849281):0.010688744485378265,((Synechococcus_elongatus:0.11096963286399841,Mycoplasma_pneumoniae:0.13156768679618835):0.011511477641761303,(Sulfolobus_islandicus:0.1409788727760315,Methanococcus_aeolicus:0.12796053290367126):0.08921836316585541):0.0038778483867645264):0.0018465183675289154,Bacillus_subtilis:0.0867706835269928,(Fusibacter_paucivorans:0.08718350529670715,Leptospira_borgpetersenii:0.0953260064125061):0.010154064744710922):0.0;",
    "((((Wolbachia_pipientis:0.04,Wolbachia_NZ_CP046925.1:0.02):0.09,(((Escherichia_coli:0.00,Escherichia_coli_str._K-12_substr._MG1655_NC_000913.3:0.00):0.04,Vibrio_cholerae_strain_N16961_NZ_CP028827.1:0.04):0.03,(((Pseudomonas_syringae_pv_tomato_str_DC3000_NC_004578.1:0.01,(Pseudomonas_putida_NBRC_14164_NC_021505.1:0.00,Pseudomonas_protegens_CHA0_NZ_LS999205.1:0.00):0.00):0.01,Pseudomonas_oleovorans_GD04132_NZ_CP104579.1:0.01):0.01,(Pseudomonas_aeruginosa_UCBPP-PA14_NC_008463.1:0.00,Pseudomonas_aeruginosa_PAO1_NC_002516.2:0.00):0.02):0.04):0.03):0.01,((Synechococcus_elongatus:0.11,Mycoplasma_pneumoniae:0.13):0.01,(Sulfolobus_islandicus:0.14,Methanococcus_aeolicus:0.13):0.09):0.00):0.00,Bacillus_subtilis:0.09,(Fusibacter_paucivorans:0.09,Leptospira_borgpetersenii:0.10):0.01):0.00;",
    # Including primers in amplicons
    "((((Synechococcus_elongatus:30.80,(Sulfolobus_islandicus:40.44,Methanococcus_aeolicus:34.56):22.70):3.45,Mycoplasma_pneumoniae:38.80):1.25,(Leptospira_borgpetersenii:26.44,Fusibacter_paucivorans:22.56):3.06):0.48,Bacillus_subtilis:22.61,((Wolbachia_pipientis:9.07,Wolbachia_NZ_CP046925.1:3.93):24.43,((Vibrio_cholerae_strain_N16961_NZ_CP028827.1:10.50,(Escherichia_coli_str._K-12_substr._MG1655_NC_000913.3:0.00,Escherichia_coli:0.00):9.50):8.82,(((Pseudomonas_syringae_pv_tomato_str_DC3000_NC_004578.1:1.65,(Pseudomonas_putida_NBRC_14164_NC_021505.1:0.50,Pseudomonas_protegens_CHA0_NZ_LS999205.1:0.50):0.35):2.06,Pseudomonas_oleovorans_GD04132_NZ_CP104579.1:2.44):1.75,(Pseudomonas_aeruginosa_UCBPP-PA14_NC_008463.1:0.00,Pseudomonas_aeruginosa_PAO1_NC_002516.2:0.00):4.75):11.12):9.29):3.14);",
    ""
])

READ_REFS_EXPECTED = "\n".join([
    # Expected
    "(((SRR27732368:24.29,Synechococcus_elongatus:20.71):9.14,((SRR24886915:10.12,Methanococcus_aeolicus:9.88):23.37,(ERR12954019:14.17,Sulfolobus_islandicus:13.83):24.13):24.11):2.45,((SRR25626983:22.35,Mycoplasma_pneumoniae:20.65):15.45,((SRR24105535:17.85,Wolbachia_pipientis:24.15):9.70,(SRR21376282:16.97,(ERR13716760:10.94,Escherichia_coli:9.06):10.53):6.30):2.42):1.70,((((SRR30750791:4.23,SRR28858832:5.77):3.22,Bacillus_subtilis:8.28):12.59,(ERR11767307:12.56,Fusibacter_paucivorans:15.44):6.91):2.42,(SRR13255634:-0.03,Leptospira_borgpetersenii:0.03):27.08):1.80):0.00;",
    # sorted by sample name
    "((((((Synechococcus_elongatus:20.74,SRR27732368:24.26):8.34,((Sulfolobus_islandicus:13.79,ERR12954019:14.21):22.34,(SRR24886915:6.86,Methanococcus_aeolicus:13.14):25.16):24.66):3.05,(SRR13255634:0.01,Leptospira_borgpetersenii:-0.01):26.39):2.01,(((SRR30750791:4.23,SRR28858832:5.77):3.22,Bacillus_subtilis:8.28):12.64,(Fusibacter_paucivorans:15.41,ERR11767307:12.59):6.86):2.33):2.82,(SRR25626983:23.48,Mycoplasma_pneumoniae:19.52):16.77):1.10,(SRR21376282:16.97,(Escherichia_coli:9.06,ERR13716760:10.94):10.53):6.81,(Wolbachia_pipientis:24.17,SRR24105535:17.83):9.19):0.00;",
    # Including primers in amplicons
    "(((((Synechococcus_elongatus:21.33,SRR27732368:24.67):10.01,((Sulfolobus_islandicus:14.67,ERR12954019:14.33):26.34,(SRR24886915:10.15,Methanococcus_aeolicus:9.85):24.16):23.12):2.11,(SRR13255634:0.02,Leptospira_borgpetersenii:-0.02):28.52):2.06,(((SRR30750791:4.23,SRR28858832:5.77):3.17,Bacillus_subtilis:8.33):12.59,(Fusibacter_paucivorans:15.38,ERR11767307:12.62):6.91):3.15):1.92,(SRR25626983:22.35,Mycoplasma_pneumoniae:21.65):16.61,((Wolbachia_pipientis:22.19,SRR24105535:18.81):11.29,(SRR21376282:16.99,(Escherichia_coli:9.10,ERR13716760:10.90):10.51):6.59):2.08);",
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

        if scores[2] < 0.002:
            self.fail("Your tree indicates you are preferring gaps during your NW traceback.\nWhile this alignment does perform a correct tracebak, gaps are generally considered worse than mismatches so you should prefer diagonals in your traceback.")

        self.fail("Your tree can't be automatically diagnosed. That means you have made an uncommon error. Try viewing your amplicons, checking that your NW settings are 1, -1, -1, and eyeballing the tree. Those are common place where mistakes are made. Additionally, if your branch lengths in a tree that passes the autograder don't match those in the expected tree then that might be related to the same issue. Some issues only impact the topology with certain data, but still have small inputs elsewhere.")

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

        self.fail("Your tree can't be automatically diagnosed. That means you have made an uncommon error. Try viewing your amplicons, checking that your NW settings are 1, -1, -1, and eyeballing the tree. Those are common place where mistakes are made. Additionally, if your branch lengths in a tree that passes the autograder don't match those in the expected tree then that might be related to the same issue. Some issues only impact the topology with certain data, but still have small inputs elsewhere.")

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

        if scores[2] == 0 or scores[3] == 0:
            self.fail("Your tree indicates you divide your distance by the alignment length. Just use the sum of mismatches and gaps as the distance.")

        if scores[4] == 0:
            self.fail("Your tree indicates you are including the primers in your isPCR amplicons.")

        self.fail("Your tree can't be automatically diagnosed. That means you have made an uncommon error. Try viewing your amplicons, checking that your NW settings are 1, -1, -1, and eyeballing the tree. Those are common place where mistakes are made. Additionally, if your branch lengths in a tree that passes the autograder don't match those in the expected tree then that might be related to the same issue. Some issues only impact the topology with certain data, but still have small inputs elsewhere.")

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

        if scores[1] == 0:
            self.fail("Your Needleman-Wunsch implementation uses a while loop with a condition like `while i>0 or j>0`. It should be `and` not `or`")

        if scores[2] == 0:
            self.fail("Your tree indicates you are including the primers in your isPCR amplicons.")

        self.fail("Your tree can't be automatically diagnosed. That means you have made an uncommon error. Try viewing your amplicons, checking that your NW settings are 1, -1, -1, and eyeballing the tree. Those are common place where mistakes are made. Additionally, if your branch lengths in a tree that passes the autograder don't match those in the expected tree then that might be related to the same issue. Some issues only impact the topology with certain data, but still have small inputs elsewhere.")
