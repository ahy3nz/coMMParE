import contextlib
import tempfile
import shutil

# Useful routines to safely build and tear down temporary
# directories when invoking MM engines

# Taken from
# https://github.com/rsdefever/foyer/blob/2bb9d60a49e13406330efc207593d0fe85b0adce/foyer/utils/tempdir.py

@contextlib.contextmanager
def temporary_directory():
    import shutil
    import tempfile
    tmp_dir = tempfile.mkdtemp()
    try:
        yield tmp_dir
    finally:
        shutil.rmtree(tmp_dir)

@contextlib.contextmanager
def temporary_cd(dir_path):
    import os
    prev_dir = os.getcwd()
    os.chdir(os.path.abspath(dir_path))
    try:
        yield
    finally:
        os.chdir(prev_dir)
