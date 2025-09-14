import unittest
from pathlib import Path
import re
from tempfile import mkdtemp
import shutil
import subprocess
import warnings
warnings.filterwarnings("ignore")

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import PointCounter

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "regexes.txt"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"
DATA_DIR = "/autograder/biol7200-autograders/data/"

Q_NUM = 1

SUBQ_COUNTER = PointCounter(0)

POINT_NUM = PointCounter(0)

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.answers = {}
        submission = Path(SCRIPT_PATH)
        if not submission.exists():
            return cls
        with open(submission) as f:
            for line in f:
                if line.strip() == "":
                    continue
                q_num = line.strip()[0]
                command = line.strip()[1:].strip()
                if not re.match(r"\d", q_num):
                    continue
                cls.answers[int(q_num)] = command
        return cls

    
    @weight(0)
    @number(f"{Q_NUM}.{SUBQ_COUNTER}.{POINT_NUM}")
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
    @number(f"{Q_NUM}.{SUBQ_COUNTER}.{POINT_NUM.next()}")
    def test_line_endings(self):
        """Check unix line endings"""
        if not Path(SCRIPT_PATH).exists():
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
        print("Your script uses Unix line endings: '\\n'")
    

    @weight(1)
    @number(f"{Q_NUM}.{SUBQ_COUNTER.next()}.{POINT_NUM.reset(1)}")
    def test_used_regex_1(self):
        """Check used a regex"""
        command = self.answers.get(1)
        if not command:
            self.fail("Could not find command. Make sure you follow the submission instructions")
        if not "sed" in command:
            self.fail("You must use sed for this question.")
        if not any([flag in command for flag in ["-E", "-r", "--regexp-extended"]]):
            self.fail("You must use the sed regex mode to complete this question.")
        # Try to grab the regex from the sed command
        regex_found = False
        for _, script in re.findall(r"([\"\'])(.+?)\1", command):
            search_string = re.match(r".*?s(.)(.*?)\1", script)
            if not search_string:
                continue
            regex = search_string.group(2)
            try:
                re.compile(regex)
                regex_found = True
            except re.error:
                continue
        if not regex_found:
            self.fail("You must use a regex to complete this question.")
        print(f'Looks like you used a regex')

    @weight(4)
    @number(f"{Q_NUM}.{SUBQ_COUNTER}.{POINT_NUM.next()}")
    def test_correct_output_1(self):
        "Check output is correct"
        command = self.answers.get(1)
        if not command:
            self.fail("Could not find command. Make sure you follow the submission instructions")
        if not "sed" in command:
            self.fail("You must use sed for this question.")
        # set up temp dir and test command
        dir = mkdtemp()
        shutil.copy(f"{DATA_DIR}HK_domain.faa", dir)
        result = subprocess.run(
            command,
            shell=True,
            cwd=dir,
            text=True,
            capture_output=True
        )
        if result.returncode != 0:
            self.fail(
                "Your command returned a non-zero exit code.\n"
                f"command run: {result.args}\n"
                f"Error: {result.stderr}"
            )
        # Check output
        with open(f"{DATA_DIR}HK_domain.faa") as f:
            original = [i for i in f]
        outfile = Path(f"{dir}/out_1.fna")
        if not outfile.exists():
            self.fail("Your command did not produce the expected output file.")
        with open(outfile) as f:
            new = [i for i in f]
        
        # Check no lines added or removed
        self.assertEqual(
            len(original),
            len(new),
            "Your command should produce a file with the same number of lines as the input."
        )
        # Check header lines in the same place
        for a, b in zip(original, new):
            if a.startswith(">") != b.startswith(">"):
                self.fail("Your command changed the order or location of lines.")
        # Check non-header lines unchanged
        for a, b in zip(original, new):
            if a.startswith(">"):
                continue
            if a != b:
                self.fail("your command made changes to non-header lines.")
        # Check headers correctly formatted
        header_regex = re.compile(r">[a-z]{3}[A-Z]_[0-9]+-[0-9]+")
        for line in new:
            if not line.startswith(">"):
                continue
            if not re.match(header_regex, line):
                self.fail("The headers in your output do not match the expected format.")
        print("Your output looks good.")

    @weight(1)
    @number(f"{Q_NUM}.{SUBQ_COUNTER.next()}.{POINT_NUM.reset(1)}")
    def test_used_regex_2(self):
        """Check used a regex"""
        command = self.answers.get(2)
        if not command:
            self.fail("Could not find command. Make sure you follow the submission instructions")
        if not "sed" in command:
            self.fail("You must use sed for this question.")
        if not any([flag in command for flag in ["-E", "-r", "--regexp-extended"]]):
            self.fail("You must use a regex to complete this question.")
        # Try to grab the regex from the sed command
        regex_found = False
        for _, script in re.findall(r"([\"\'])(.+?)\1", command):
            search_string = re.match(r".*?s(.)(.*?)\1", script)
            if not search_string:
                continue
            regex = search_string.group(2)
            try:
                re.compile(regex)
                regex_found = True
            except re.error:
                continue
        if not regex_found:
            self.fail("You must use a regex to complete this question.")
        print(f'Looks like you used a regex')

    @weight(4)
    @number(f"{Q_NUM}.{SUBQ_COUNTER}.{POINT_NUM.next()}")
    def test_correct_output_2(self):
        "Check output is correct"
        command = self.answers.get(2)
        if not command:
            self.fail("Could not find command. Make sure you follow the submission instructions")
        if not "sed" in command:
            self.fail("You must use sed for this question.")
        # set up temp dir and test command
        dir = mkdtemp()
        shutil.copy(f"{DATA_DIR}HK_domain.faa", dir)
        result = subprocess.run(
            command,
            shell=True,
            cwd=dir,
            text=True,
            capture_output=True
        )
        if result.returncode != 0:
            self.fail(
                "Your command returned a non-zero exit code.\n"
                f"command run: {result.args}\n"
                f"Error: {result.stderr}"
            )
        # Check output
        with open(f"{DATA_DIR}HK_domain.faa") as f:
            original = [i for i in f]
        outfile = Path(f"{dir}/out_2.fna")
        if not outfile.exists():
            self.fail("Your command did not produce the expected output file.")
        with open(outfile) as f:
            new = [i for i in f]
        
        # Check no lines added or removed
        self.assertEqual(
            len(original),
            len(new),
            "Your command should produce a file with the same number of lines as the input."
        )
        # Check header lines in the same place
        for a, b in zip(original, new):
            if a.startswith(">") != b.startswith(">"):
                self.fail("Your command changed the order or location of lines.")
        # Check non-header lines unchanged
        for a, b in zip(original, new):
            if a.startswith(">"):
                continue
            if a != b:
                self.fail("your command made changes to non-header lines.")
        # Check headers correctly formatted
        header_regex = re.compile(r">[A-Z][a-z]{2}[A-Z]_[0-9]+-[0-9]+")
        for line in new:
            if not line.startswith(">"):
                continue
            if not re.match(header_regex, line):
                self.fail("The headers in your output do not match the expected format.")
        print("Your output looks good.")


    @weight(1)
    @number(f"{Q_NUM}.{SUBQ_COUNTER.next()}.{POINT_NUM.reset(1)}")
    def test_used_regex_3(self):
        """Check used a regex"""
        command = self.answers.get(3)
        if not command:
            self.fail("Could not find command. Make sure you follow the submission instructions")
        if not "sed" in command:
            self.fail("You must use sed for this question.")
        if not any([flag in command for flag in ["-E", "-r", "--regexp-extended"]]):
            self.fail("You must use a regex to complete this question.")
        # Try to grab the regex from the sed command
        regex_found = False
        case_convert_found = False
        for _, script in re.findall(r"([\"\'])(.+?)\1", command):
            regex_parts = re.match(r".*?s(.)(.*?)\1(.*?)\1", script)
            if not regex_parts:
                continue
            search_string = regex_parts.group(2)
            try:
                re.compile(search_string)
                regex_found = True
            except re.error:
                pass
            replace_string = regex_parts.group(3)
            if r"\u" in replace_string or r"\U" in replace_string:
                case_convert_found = True
        if not regex_found:
            self.fail("You must use a regex to complete this question.")
        
        if not case_convert_found:
            self.fail("Make sure you match the specified text and modify it as directed.")
        print(f'Looks like you used a regex and processed the matched text')

    @weight(4)
    @number(f"{Q_NUM}.{SUBQ_COUNTER}.{POINT_NUM.next()}")
    def test_correct_output_3(self):
        "Check output is correct"
        command = self.answers.get(3)
        if not command:
            self.fail("Could not find command. Make sure you follow the submission instructions")
        if not "sed" in command:
            self.fail("You must use sed for this question.")
        # set up temp dir and test command
        dir = mkdtemp()
        shutil.copy(f"{DATA_DIR}HK_domain.faa", dir)
        result = subprocess.run(
            command,
            shell=True,
            cwd=dir,
            text=True,
            capture_output=True
        )
        if result.returncode != 0:
            self.fail(
                "Your command returned a non-zero exit code.\n"
                f"command run: {result.args}\n"
                f"Error: {result.stderr}"
            )
        # Check output
        with open(f"{DATA_DIR}HK_domain.faa") as f:
            original = [i for i in f]
        outfile = Path(f"{dir}/out_3.fna")
        if not outfile.exists():
            self.fail("Your command did not produce the expected output file.")
        with open(outfile) as f:
            new = [i for i in f]
        
        # Check no lines added or removed
        self.assertEqual(
            len(original),
            len(new),
            "Your command should produce a file with the same number of lines as the input."
        )
        # Check header lines in the same place
        for a, b in zip(original, new):
            if a.startswith(">") != b.startswith(">"):
                self.fail("Your command changed the order or location of lines.")
        # Check non-header lines unchanged
        for a, b in zip(original, new):
            if a.startswith(">"):
                continue
            if a != b:
                self.fail("your command made changes to non-header lines.")
        # Check headers correctly formatted
        header_regex = re.compile(r">[A-Z][a-z]{2}[A-Z]_[0-9]+-[0-9]+")
        for line in new:
            if not line.startswith(">"):
                continue
            if not re.match(header_regex, line):
                self.fail("The headers in your output do not match the expected format.")
        if r"\u" not in command and r"\U" not in command:
            self.fail("You do not convert the case of the matched string.")
        print("Your output looks good.")

    @weight(2)
    @number(f"{Q_NUM}.{SUBQ_COUNTER.next()}.{POINT_NUM.reset(1)}")
    def test_correct_leaf_number(self):
        """Check the correct number of leaves was found"""
        command = self.answers.get(4)
        if not command:
            self.fail("Could not find command. Make sure you follow the submission instructions")
        # set up temp dir and test command
        dir = mkdtemp()
        shutil.copy(f"{DATA_DIR}Tree_of_life.nwk", dir)
        result = subprocess.run(
            command.replace("ggrep", "grep"),
            shell=True,
            cwd=dir,
            text=True,
            capture_output=True
        )
        if result.returncode != 0:
            self.fail(
                "Your command returned a non-zero exit code.\n"
                f"command run: {result.args}\n"
                f"Error: {result.stderr}"
            )
        # Check output
        outfile = Path(f"{dir}/out_4.txt")
        if not outfile.exists():
            self.fail("Your command did not produce the expected output file.")
        with open(outfile) as f:
            line_count = len([i for i in f])
        if line_count > 191:
            self.fail("Your command returned too many leaf names.")
        elif line_count < 191:
            self.fail("your command returned too few leaf names.")
        print("Your command returned the correct number of leaf names.")
    
    @weight(3)
    @number(f"{Q_NUM}.{SUBQ_COUNTER}.{POINT_NUM.next()}")
    def test_correct_leaf_names(self):
        """Check the correct leaf names"""
        command = self.answers.get(4)
        if not command:
            self.fail("Could not find command. Make sure you follow the submission instructions")
        # set up temp dir and test command
        dir = mkdtemp()
        shutil.copy(f"{DATA_DIR}Tree_of_life.nwk", dir)
        result = subprocess.run(
            command.replace("ggrep", "grep"),
            shell=True,
            cwd=dir,
            text=True,
            capture_output=True
        )
        if result.returncode != 0:
            self.fail(
                "Your command returned a non-zero exit code.\n"
                f"command run: {result.args}\n"
                f"Error: {result.stderr}"
            )
        # Check output
        outfile = Path(f"{dir}/out_4.txt")
        if not outfile.exists():
            self.fail("Your command did not produce the expected output file.")
        with open(outfile) as f:
            leaves = [l.strip() for l in f]
        
        with open(f"{DATA_DIR}Tree_of_life.nwk") as f:
            tree = f.read()
        leaf_regex = re.compile(r"(?<=\(|,)[^(),:]+(?=[:,)])")
        true_leaves = [i for i in re.findall(leaf_regex, tree)]
        diffs = set(leaves).difference(true_leaves)
        sims = set(leaves).intersection(true_leaves)
        if diffs != set():
            self.fail(
                f"{len(diffs)} of the leaf names found by your command differ from the expected names. "
                f"{len(sims)} leaf names are correct"
            )
        print("Your leaf names match the expected values.")
    
    @weight(5)
    @number(f"{Q_NUM}.{SUBQ_COUNTER.next()}.{POINT_NUM.reset(1)}")
    def test_correct_brlen_sum(self):
        """Check the sum of branch lengths is correct"""
        command = self.answers.get(5)
        if not command:
            self.fail("Could not find command. Make sure you follow the submission instructions")
        # set up temp dir and test command
        dir = mkdtemp()
        shutil.copy(f"{DATA_DIR}Tree_of_life.nwk", dir)
        result = subprocess.run(
            command.replace("ggrep", "grep"),
            shell=True,
            cwd=dir,
            text=True,
            capture_output=True
        )
        if result.returncode != 0:
            self.fail(
                "Your command returned a non-zero exit code.\n"
                f"command run: {result.args}\n"
                f"Error: {result.stderr}"
            )
        # Check output
        outfile = Path(f"{dir}/out_5.txt")
        if not outfile.exists():
            self.fail("Your command did not produce the expected output file.")
        with open(outfile) as f:
            brlen_str = f.read().strip()
        try:
            brlen = float(brlen_str)
        except:
            self.fail("The output of your command is not a number.")
        if brlen != 45.54:
            self.fail("Your command returned the wrong value.")
        print("Your command returned the correct value.")

    @weight(4)
    @number(f"{Q_NUM}.{SUBQ_COUNTER.next()}.{POINT_NUM.reset(1)}")
    def test_count_genes(self):
        """Check number of gene files determined is correct"""
        command = self.answers.get(6)
        if not command:
            self.fail("Could not find command. Make sure you follow the submission instructions")
        # check command uses find with a regex
        if not command.strip().startswith("find "):
            self.fail("Your command should use find to identify the gene files.")
        if not "-regex " in command:
            self.fail("Your command should use a regex to identify gene files.")
        if "-E " in command:
            print(
                "The -E flag is found on Mac's version of find, but not the GNU version found on Linux, "
                "which used in this autograder. Use '-regextype egrep instead of -E.\n"
                "For the purposes of this course, consider installing findutils from conda-forge to use the GNU find."
                )
            command = command.replace("-E ", "-regextype egrep ")
        # set up temp dir and test command
        dir = mkdtemp()
        shutil.copytree(f"{DATA_DIR}find_data", f"{dir}/find_data")
        Path.mkdir(Path(f"{dir}/data"))
        Path(f"{dir}/data/find_data").symlink_to(Path(f"{dir}/find_data"))
        result = subprocess.run(
            command,
            shell=True,
            cwd=dir,
            text=True,
            capture_output=True
        )
        if result.returncode != 0 or result.stderr.strip() != "":
            self.fail(
                "Your command failed.\n"
                f"command run: {result.args}\n"
                f"Error: {result.stderr}"
            )
        # Check output
        outfile = Path(f"{dir}/out_6.txt")
        if not outfile.exists():
            self.fail("Your command did not produce the expected output file.")
        with open(outfile) as f:
            gene_count = f.read().strip()
        try:
            gene_count = int(gene_count)
        except:
            self.fail("The output of your command is not a number.")
        if gene_count != 4334:
            if 4332 < gene_count < 4336:
                self.fail("You're off by one. Perhaps your regex is too permissive and is catching a file in the test environment.")
            self.fail(f"Your command returned the wrong value: {gene_count}.")
        print("Your command returned the correct value.")
    
    @weight(4)
    @number(f"{Q_NUM}.{SUBQ_COUNTER.next()}.{POINT_NUM.reset(1)}")
    def test_count_proteins(self):
        """Check number of protein files determined is correct"""
        command = self.answers.get(7)
        if not command:
            self.fail("Could not find command. Make sure you follow the submission instructions")
        # check command uses find with a regex
        if not command.strip().startswith("find "):
            self.fail("Your command should use find to identify the gene files.")
        if not "-regex " in command:
            self.fail("Your command should use a regex to identify gene files.")
        if "-E " in command:
            print(
                "The -E flag is found on Mac's version of find, but not the GNU version found on Linux, "
                "which used in this autograder. Use '-regextype egrep instead of -E.\n"
                "For the purposes of this course, consider installing findutils from conda-forge to use the GNU find."
                )
            command = command.replace("-E ", "-regextype egrep ")
        # set up temp dir and test command
        dir = mkdtemp()
        shutil.copytree(f"{DATA_DIR}find_data", f"{dir}/find_data")
        Path.mkdir(Path(f"{dir}/data"))
        Path(f"{dir}/data/find_data").symlink_to(Path(f"{dir}/find_data"))
        result = subprocess.run(
            command,
            shell=True,
            cwd=dir,
            text=True,
            capture_output=True
        )
        if result.returncode != 0 or result.stderr.strip() != "":
            self.fail(
                "Your command failed.\n"
                f"command run: {result.args}\n"
                f"Error: {result.stderr}"
            )
        # Check output
        outfile = Path(f"{dir}/out_7.txt")
        if not outfile.exists():
            self.fail("Your command did not produce the expected output file.")
        with open(outfile) as f:
            gene_count = f.read().strip()
        try:
            gene_count = int(gene_count)
        except:
            self.fail("The output of your command is not a number.")
        if gene_count != 3992:
            if 3990 < gene_count < 3994:
                self.fail("You're off by one. Perhaps your regex is too permissive and is catching a file in the test environment.")
            self.fail(f"Your command returned the wrong value: {gene_count}.")
        print("Your command returned the correct value.")
    
    @weight(2)
    @number(f"{Q_NUM}.{SUBQ_COUNTER.next()}.{POINT_NUM.reset(1)}")
    def test_count_file_cps(self):
        """Check gene and protein files were copied correctly"""
        command = self.answers.get(8)
        if not command:
            self.fail("Could not find command. Make sure you follow the submission instructions")
        # check command uses find with a regex
        if not command.strip().startswith("find "):
            self.fail("Your solution should use find to identify the gene files.")
        if not "-regex " in command:
            self.fail("Your solution should use a regex to identify gene files.")
        if "-E " in command:
            print(
                "The -E flag is found on Mac's version of find, but not the GNU version found on Linux, "
                "which used in this autograder. Use '-regextype egrep instead of -E.\n"
                "For the purposes of this course, consider installing findutils from conda-forge to use the GNU find."
                )
            command = command.replace("-E ", "-regextype egrep ")
        if not re.match(r".+[^\\](?:;|&&).+", command):
            self.fail("Your solution should be composed of two bash commands.")
        # set up temp dir and test command
        dir = mkdtemp()
        shutil.copytree(f"{DATA_DIR}find_data", f"{dir}/find_data")
        Path.mkdir(Path(f"{dir}/data"))
        shutil.copytree(f"{DATA_DIR}find_data", f"{dir}/data/find_data")
        gene_dir = Path(f"{dir}/genes")
        protein_dir = Path(f"{dir}/proteins")
        Path.mkdir(gene_dir)
        Path.mkdir(protein_dir)
        result = subprocess.run(
            command,
            shell=True,
            cwd=dir,
            text=True,
            capture_output=True
        )
        if result.returncode != 0 or result.stderr.strip() != "" and not "are the same file" in result.stderr.strip():
            self.fail(
                "Your command failed.\n"
                f"command run: {result.args}\n"
                f"Error: {result.stderr}"
            )
        # Check output
        gene_files = [file.name for file in gene_dir.iterdir()]
        protein_files = [file.name for file in protein_dir.iterdir()]
        if len(gene_files) != 4334:
            self.fail(
                "Your command copied the wrong number of files to the genes directory.\n"
                f"you copied {len(gene_files)}"
                )
        if len(protein_files) != 3992:
            self.fail(
                "Your command copied the wrong number of files to the proteins directory.\n"
                f"you copied {len(protein_files)}"
                )
        gene_regex = re.compile(r"[a-z]{3}[A-Z]")
        protein_regex = re.compile(r"[A-Z][a-z]{2}[A-Z]")
        for f in gene_files:
            if not re.match(gene_regex, str(f)):
                self.fail("files that do not match the expected name format were found in the output genes directory")
        for f in protein_files:
            if not re.match(protein_regex, str(f)):
                self.fail("files that do not match the expected name format were found in the output proteins directory")

        print("Your command copied the files as expected.")
    