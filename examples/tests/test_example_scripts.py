import pytest
from os import path
from glob import glob
from subprocess import run

def get_examples_dir():
    fpath = path.abspath(__file__)
    return path.dirname(path.dirname(fpath))

def get_scripts():
    examples_dir = get_examples_dir()
    scripts = glob(examples_dir + path.sep + '*.sh')
    return scripts

@pytest.mark.parametrize('script', get_scripts())
def test_script(script):
    out = run(script, check=True)
    assert out.returncode == 0
