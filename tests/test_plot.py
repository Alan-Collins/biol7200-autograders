import unittest
from pathlib import Path
import shutil
import tempfile
import subprocess
from PIL import Image, ImageChops

from gradescope_utils.autograder_utils.decorators import weight, number, visibility
from gradescope_utils.autograder_utils.files import check_submitted_files

from utils import PointCounter

SUBMISSION_PATH = "/autograder/submission/"
SOLUTION_SCRIPT = "plot.py"
SCRIPT_PATH = f"{SUBMISSION_PATH}{SOLUTION_SCRIPT}"
PLOT_PATH = f"{SUBMISSION_PATH}plot.png"
DATA_DIR = "/autograder/biol7200-autograders/data/"

Q_NUM = 1

POINT_NUM = PointCounter(0)

class TestFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = Path(tempfile.mkdtemp())
        cls.input_files = [
            "Flu",
            "covid_spike",
            "covid_rates",
            "global_temperature"
        ]
        for file in cls.input_files:
            shutil.copytree(f"{DATA_DIR}{file}", f"{cls.dir}/{file}")
        cls.submitted = True
        cls.outfile = Path(f"{cls.dir}/plot.png")
       
        if not Path(SCRIPT_PATH).exists():
            cls.submitted = False
            return cls
        # copy script to dir with data
        shutil.copy(SCRIPT_PATH, f"{cls.dir}/")
        Path(f"{cls.dir}/{SOLUTION_SCRIPT}").chmod(0o777)

        cls.result = subprocess.run(
            [f"./{SOLUTION_SCRIPT}"],
            text=True,
            capture_output=True,
            cwd=cls.dir
        )

       
        if cls.result.returncode != 0 or cls.result.stderr.strip() != "":
            cls.error = True
            return cls
        
        cls.error = False
        
        if not cls.outfile.exists() or not Path(PLOT_PATH).exists():
            return cls
        
        sub_img = Image.open(PLOT_PATH)
        out_img = Image.open(cls.outfile)

        size = sub_img.height * sub_img.width
        cls.dims = {
            "submitted": (sub_img.height, sub_img.width),
            "output": (out_img.height, out_img.width)
        }

        if sub_img.height != out_img.height or sub_img.width != out_img.width:
            cls.size_same = True
        else:
            cls.size_same = False

        diffs = len([i for i in ImageChops.difference(sub_img, out_img).getdata() if any(i)])

        cls.prcnt_diff = round(100*(diffs/size), 2)


    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir)

    @weight(0)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("on_fail")
    def test_submitted_files(self):
        """Check submitted files"""
        missing_files = check_submitted_files([f'{SOLUTION_SCRIPT}', f'{PLOT_PATH}'])
        for path in missing_files:
            print(f'Missing {path}')
        self.assertEqual(
            len(missing_files),
            0,
            f'Missing required submission file(s), follow instructions carefully'
        )
        print(f'All required files submitted successfully')
    
    @weight(100)
    @number(f"{Q_NUM}.{POINT_NUM.next()}")
    @visibility("visible")
    def test_plot(self):
        """Check plot generated"""
        if not self.submitted:
            self.fail("Missing required submission file(s), follow instructions carefully")
        if self.error:
            self.fail(
                f"your script produced an error:\nexitcode: {self.result.returncode}\n"
                f"stderr: {self.result.stderr.strip()}"
            )
        if not self.outfile.exists():
            self.fail("Your script did not produce a plot.png file")

        if not self.size_same:
            self.fail(
                "The image you uploaded is not the same size as the image produced by your script.\n"
                f"Your submission image is {' x '.join(self.dims['submission'])} pixels, while your script "
                f"produces an image with dimensions of {' x '.join(self.dims['output'])} pixels"
            )

        if self.prcnt_diff > 5:
            self.fail(
                "Your script produces an image that differs from the uploaded image "
                "to an unexpected degree. Make sure you set seed to produce reproducible randomness\n\n"
                f"Your images differ by {self.prcnt_diff}%"
            )
        print("Your script produces an image that matches the submitted image.")
        