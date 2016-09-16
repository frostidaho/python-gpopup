import unittest
import os
from glob import glob
from subprocess import run

def get_scripts():
    dirname = os.path.dirname
    this_path = os.path.abspath(__file__)
    examples_dir = dirname(dirname(this_path))
    # root_dir = dirname(dirname(this_path))
    # examples_dir = os.path.join(this_path, 'examples')
    scripts = glob(examples_dir + os.path.sep + '*.sh')
    return scripts


class TestScripts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scripts = get_scripts()

    def test_scripts(self):
        for script in self.scripts:
            out = run(script, check=True)
            self.assertEqual(out.returncode, 0)
