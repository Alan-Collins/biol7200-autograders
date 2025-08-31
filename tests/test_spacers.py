import unittest
from pathlib import Path
import re
from tempfile import mkdtemp
import shutil
import subprocess

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import PointCounter, BlastResult

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "find_perfect_matches.sh"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"
DATA_DIR = "/autograder/biol7200-autograders/data/"

Q_NUM = 4

POINT_NUM = PointCounter(0)

EXPECTED_SPACERS = """\
>other_contig:1/8
ATTATGCGGACCCTTGGCGGCATCCTGATGAA
>other_contig:2/8
TGCATGTACCTCCAGTGGTTCGGGTATCTGCT
>other_contig:3/8
GATTCGACCGTCAGACCACGGCGACGCACAGC
>other_contig:4/8
TTCCACCACGTTGCCGAGCGCCATGACCTTGTA
>other_contig:5/8
GCAGTGATCAGCCTGGCCGGCGACCAGGTGAA
>other_contig:6/8
AACCACGGCCCCTTTGCCGAACTGCTCGACCA
>other_contig:7/8
TTATCGTGTTCTGCACGATTTGATGCGATGCT
>other_contig:8/8
ACCGTCTTCCTCGCGCAAGTCGTATTCGGGTA
>orig_array:1/9
AGGTCGAGGTGGGCTCGGCGGCGATGATCGAT
>orig_array:2/9
GGTACGTGGTTTCGACCAACAGCACTGCCCAA
>orig_array:3/9
TAAAGGAGATTGCCATGCTGATCAAACTTCCC
>orig_array:4/9
GTCAGGGTCGTGCATGACTCCGATGTGGTGGC
>orig_array:5/9
CGTCCAGAACGTCACACGCTCGCCGTCGATGT
>orig_array:6/9
AACCGGAGCCTTCGGGCCGCGTTGGGATCCAC
>orig_array:7/9
TTGACTGCTGGGGCCTGACGCTCATCGCGCGG
>orig_array:8/9
GCGACCCTGGCCAGGGCGGCGTCGCGCTCTGC
>orig_array:9/9
TTGAGCACAACCGGCTGAGCCAGCTGGTTGTC
>same_contig:1/8
TGTCGTTGTCCACGGTTGGTCCTCCGGGGGTC
>same_contig:2/8
CACTTACCAGTTCGGATGCGCAGGACCGCATT
>same_contig:3/8
CCCTCGACGGCGCGCATCAGGGTGCCGAAGCT
>same_contig:4/8
CAGGTGCCCCAGCATCAGGCGATTGATGTTGT
>same_contig:5/8
TAGATTCTGCTGTGATGATGCCGCCCCAGATC
>same_contig:6/8
GAGTATCGCCACCCCAATGGAGAGAGCCATAC
>same_contig:7/8
GCGGACGTCTGGTAGTTGTCGCCGCGACTCTT
>same_contig:8/8
AGGCAGCGCCCCTCTTCCTGGAGCCGCTGCTG
"""

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = mkdtemp()
        cls.input_files = [
            "CRISPR_1f.fna",
            "ERR430992.fna"
        ]
        for file in cls.input_files:
            shutil.copy(f"{DATA_DIR}{file}", f"{cls.dir}/")
        
        if not Path(SCRIPT_PATH).exists():
            cls.submitted = False
            return cls
        cls.submitted = True
        shutil.copy(SCRIPT_PATH, cls.dir)
        cls.outfile = Path(f"{cls.dir}/spacers.fna")
        Path(f"{cls.dir}/{SOLUTION_SCRIPT}").chmod(0o777)
        command = [
            f"./{SOLUTION_SCRIPT}",
            "CRISPR_1f.fna",
            "ERR430992.fna",
            cls.outfile
        ]
        cls.result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            cwd=cls.dir
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir)

    
    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM}")
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
    def test_no_error(self):
        """Check script ran successfully"""
        if not self.submitted:
            self.fail("No script was submitted.")
        if self.result.returncode != 0:
            self.fail("Your script returned a non-zero exitcode.")
        print("Your script ran successfully.")
    
    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_outfile_exists(self):
        """Check script produced an output file"""
        if not self.submitted:
            self.fail("No script was submitted.")
        if self.result.returncode != 0:
            self.fail("Your script returned a non-zero exitcode.")
        if not self.outfile.exists():
            print([i for i in Path(self.dir).iterdir()])
            print(self.result)
            self.fail("Your script did not produce an output file.")
        print("Your script produced a file.")

    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_fasta_output(self):
        """Check output file is fasta"""
        if not self.submitted:
            self.fail("No script was submitted.")
        if self.result.returncode != 0:
            self.fail("Your script returned a non-zero exitcode.")
        if not self.outfile.exists():
            self.fail("Your script did not produce an output file.")
        with open(self.outfile) as f:
            first = next(f)
            if not first.startswith(">"):
                self.fail("Your script does not produce valid fasta output")
            nseqs = 1
            for line in f:
                if line.startswith(">"):
                    nseqs += 1
                    continue
                for base in line.strip():
                    if base not in {"A", "T", "C", "G", "N"}:
                        self.fail("Your output file contains invalid sequence.")
        if nseqs == 1:
            self.fail("your output file contains only one sequence.")
        print("Your output file looks like fasta sequences.")
    
    @weight(0)
    @visibility("hidden")
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    def test_compare_to_expected(self):
        """Compare output to actual spacer sequences"""
        if not self.submitted:
            self.fail("No script was submitted.")
        if self.result.returncode != 0:
            self.fail("Your script returned a non-zero exitcode.")
        if not self.outfile.exists():
            self.fail("Your script did not produce an output file.")
        
        expected_file = Path(f"{self.dir}/expected.fna")
        with open(expected_file, 'w') as f:
            f.write(EXPECTED_SPACERS)
        # BLAST expected against student results
        # Sort by subject hits
        # keep best hit for each subject based on length and pident
        command = (
            f"blastn -query {expected_file} -subject {self.outfile} "
            "-task blastn-short -outfmt '6 std qlen slen' "
            "| sort -k2,2 -k4,4nr -k3,3nr | awk '!a[$2]++'"
        )
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            cwd=self.dir,
            capture_output=True
        )
        if result.returncode != 0:
            self.fail(
                "Couldn't compare output to expected results.\n"
                f"Error:\n{result.stderr}"
            )
        if len(result.stdout.strip()) == 0:
            self.fail("No matches found between expected spacers and output.")
        expected_count = {
            "other_contig": 8,
            "orig_array": 9,
            "same_contig": 8
        }
        n = 0
        for array, count in expected_count.items():
            n += 1
            # Assess ability to extract the 100% match array
            this_array_count = 0
            this_array_spacers_seen = set()
            this_array_hits = []
            for line in result.stdout.split("\n")[:-1]:
                cols = line.split()
                if array not in cols[0]:
                    continue
                this_array_count += 1
                spacer_num = int(cols[0].split(":")[1][0])
                this_array_spacers_seen.add(spacer_num)
                this_array_hits.append(BlastResult.from_outfmt_str("std qlen slen", line))
            if (
                this_array_count == count
                and all(
                    [i in this_array_spacers_seen for i in range(1, count+1)]
                )
            ):
                print(f"Array {n} found")
            elif this_array_count == 0:
                print(f"Array {n} not found")
            else:
                print(f"Array {n} has issues")
            
            # Assess original array hits
            orig_issues = set()
            for hit in this_array_hits:
                if hit.is_perfect_match():
                    continue
                if hit.qlen != hit.slen:
                    if hit.qlen == hit.slen+1 or hit.qlen == hit.slen-1:
                        orig_issues.add("off by one error.")
                    else:
                        orig_issues.add("spacers of the wrong length found.")
            if len(orig_issues) == 0:
                print(f"Array {n} spacers are correct")
            else:
                issue_str = "\n".join([f"Array {n} issues:"] + [i for i in orig_issues])
                print(issue_str)

        print(f"Expected vs result BLAST output (outfmt '6 std qlen slen'):\n{result.stdout}")
        
