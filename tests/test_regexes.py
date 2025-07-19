import unittest
from pathlib import Path
import re
from tempfile import mkdtemp
import shutil
import subprocess

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "regexes.txt"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"
DATA_DIR = "/autograder/biol7200-autograders/data/"

Q_NUM = 1

class PointCounter():
    def __init__(self, start=0):
        self._setup(start)
    
    def _setup(self, start=0):
        self._counter = (i for i in range(start, 1000))
    
    def __iter__(self):
        return self._counter
    
    def __next__(self):
        try:
            return next(self._counter)
        except:
            raise StopIteration
    
    def reset(self, start=0) -> int:
        self._setup(start)
        return next(self._counter)


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
                q_num = line.strip()[0]
                command = line.strip()[1:].strip()
                if not re.match(r"\d", q_num):
                    continue
                cls.answers[int(q_num)] = command
        return cls

    
    @weight(0)
    @number(f"{Q_NUM}.0.{next(POINT_NUM)}")
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
    

    @weight(1)
    @number(f"{Q_NUM}.1.{POINT_NUM.reset(1)}")
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
        print(command)
        print(re.findall(r"([\"\']).+?\1", command))
        for script in re.findall(r"([\"\']).+?\1", command):
            print(f"found sed script: {script}")
            search_string = re.match(r"s(.)(.*)\1", script)
            if not search_string:
                continue
            regex = search_string.group(2)
            print(f"found regex: {regex}")
            try:
                re.compile(regex)
                regex_found = True
            except re.error:
                continue
        if not regex_found:
            self.fail("You must use a regex to complete this question.")
        print(f'Looks like you used a regex')

    @weight(4)
    @number(f"{Q_NUM}.1.{next(POINT_NUM)}")
    def test_correct_output_1(self):
        "Check output is correct"
        command = self.answers.get(1)
        if not command:
            self.fail("Could not find command. Make sure you follow the submission instructions")
        if not "sed" in command:
            self.fail("You must use sed for this question.")
        # set up temp dir and test command
        dir = mkdtemp()
        shutil.copyfile(f"{DATA_DIR}HK_domain.faa", dir)
        result = subprocess.run(
            command,
            cwd=dir,
            text=True,
            capture_output=True
        )
        if result.returncode != 0:
            self.fail("Your command returned a non-zero exit code.")
        # Check output
        with open(f"{DATA_DIR}HK_domain.faa") as f:
            original = [i for i in f]
        outfile = Path(f"{dir}out_1.fna")
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
    @number(f"{Q_NUM}.2.{POINT_NUM.reset(1)}")
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
        for script in re.findall(r"([\"\']).+?\1", command):
            search_string = re.match(r"s(.)(.*)\1", command)
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
    @number(f"{Q_NUM}.2.{next(POINT_NUM)}")
    def test_correct_output_2(self):
        "Check output is correct"
        command = self.answers.get(2)
        if not command:
            self.fail("Could not find command. Make sure you follow the submission instructions")
        if not "sed" in command:
            self.fail("You must use sed for this question.")
        # set up temp dir and test command
        dir = mkdtemp()
        shutil.copyfile(f"{DATA_DIR}HK_domain.faa", dir)
        result = subprocess.run(
            command,
            cwd=dir,
            text=True,
            capture_output=True
        )
        if result.returncode != 0:
            self.fail("Your command returned a non-zero exit code.")
        # Check output
        with open(f"{DATA_DIR}HK_domain.faa") as f:
            original = [i for i in f]
        outfile = Path(f"{dir}out_1.fna")
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
    @number(f"{Q_NUM}.3.{POINT_NUM.reset(1)}")
    def test_used_regex_3(self):
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
        case_convert_found = False
        for script in re.findall(r"([\"\']).+?\1", command):
            search_string = re.match(r"s(.)(.*)\1", command)
            if not search_string:
                continue
            regex = search_string.group(2)
            try:
                re.compile(regex)
                if r"\u" in regex or r"\U" in regex:
                    case_convert_found = True
                regex_found = True
            except re.error:
                continue
        if not regex_found:
            self.fail("You must use a regex to complete this question.")
        
        if not case_convert_found:
            self.fail("Make sure you match the specified text and modify it as directed.")
        print(f'Looks like you used a regex and processed the matched text')

    @weight(4)
    @number(f"{Q_NUM}.2.{next(POINT_NUM)}")
    def test_correct_output_2(self):
        "Check output is correct"
        command = self.answers.get(2)
        if not command:
            self.fail("Could not find command. Make sure you follow the submission instructions")
        if not "sed" in command:
            self.fail("You must use sed for this question.")
        # set up temp dir and test command
        dir = mkdtemp()
        shutil.copyfile(f"{DATA_DIR}HK_domain.faa", dir)
        result = subprocess.run(
            command,
            cwd=dir,
            text=True,
            capture_output=True
        )
        if result.returncode != 0:
            self.fail("Your command returned a non-zero exit code.")
        # Check output
        with open(f"{DATA_DIR}HK_domain.faa") as f:
            original = [i for i in f]
        outfile = Path(f"{dir}out_1.fna")
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
