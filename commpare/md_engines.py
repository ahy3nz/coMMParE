import shutil
import importlib

#### Identify the local MD engines available to test against
def identify_engines():
    engines = []
    if detect_gromacs():
        engines.append('gromacs')
    if detect_openmm():
        engines.append('openmm')
    if detect_hoomd():
        engines.append('hoomd')
    if detect_amber():
        engines.append('amber')
    if detect_desmond():
        engines.append("desmond")

    return engines

def detect_gromacs():
    if shutil.which('gmx'):
        return True
    if shutil.which('gmx_d'):
        return True
    return False

def detect_openmm():
    try: 
        importlib.import_module('simtk')
        return True
    except ModuleNotFoundError:
        return False

def detect_hoomd():
    try:
        importlib.import_module('hoomd')
        return True
    except ModuleNotFoundError:
        return False

def detect_amber():
    # Not a supported engine
    return False

def detect_desmond():
    # Not a supported engine
    return False

