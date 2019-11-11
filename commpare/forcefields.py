import importlib

def identify_forcefields():
    forcefields = {}
    try: 
        foyer = importlib.import_module('foyer')
        if 'load_GAFF' in dir(foyer.forcefields):
            forcefields['GAFF'] = foyer.forcefields.load_GAFF()
        if 'load_OPLSAA' in dir(foyer.forcefields):
            forcefields['OPLSAA'] = foyer.forcefields.load_OPLSAA()

        return forcefields
    except ModuleNotFoundError:
        return forcefields

