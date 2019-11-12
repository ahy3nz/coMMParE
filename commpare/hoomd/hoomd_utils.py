import warnings
import pandas as pd

from mbuild.formats.hoomd_simulation import create_hoomd_simulation
import hoomd
import hoomd.md


def build_run_measure_hoomd(structure, **kwargs):
    """ Build and run a HOOMD simulation from a parmed.Structure """
    hoomd.util.quiet_status()
    hoomd.context.initialize("--msg-file=hoomd.out")
    create_hoomd_simulation(structure, **kwargs)

    all_group = hoomd.group.all()
    # Arbitrary small simulation
    hoomd.md.integrate.mode_standard(dt=0.00001)
    hoomd.md.integrate.nve(all_group, limit=0.001)
    hoomd.run(1)

    hoomd_force_groups = get_hoomd_force_groups()
    energies = {'hoomd': {key: get_hoomd_energy(key, 
                                                hoomd_force_groups, 
                                                all_group) 
                                                for key in hoomd_force_groups}}
    df = pd.DataFrame.from_dict(energies, orient='index')

    df = df[['bond', 'angle', 'dihedral', 'LJ', 'QQ', 'nonbond', 'all']]

    return df

def get_hoomd_force_groups():
    """ Get various hoomd force objects 
    
    Returns
    -------
    hoomd_force_groups : dictionary
        string : list of hoomd force objects
        Keys are 'bond', 'angle', 'dihedral', 'LJ', 'QQ', 'nonbond', 'all'
        """
    hoomd_force_groups = {'bond':[], 'angle':[], 
            'dihedral':[], 'LJ':[], 'QQ':[], 'nonbond':[], 'all':[]}

    for force in hoomd.context.current.forces:
        if force.__module__ == 'hoomd.md.bond':
            hoomd_force_groups['bond'].append(force)
            hoomd_force_groups['all'].append(force)
        elif force.__module__ == 'hoomd.md.angle':
            hoomd_force_groups['angle'].append(force)
            hoomd_force_groups['all'].append(force)
        elif force.__module__ == 'hoomd.md.dihedral':
            hoomd_force_groups['dihedral'].append(force)
            hoomd_force_groups['all'].append(force)
        elif (isinstance(force, hoomd.md.pair.lj) or
                isinstance(force, hoomd.md.special_pair.lj)):
            hoomd_force_groups['LJ'].append(force)
            hoomd_force_groups['nonbond'].append(force)
            hoomd_force_groups['all'].append(force)
        elif (isinstance(force, hoomd.md.charge.pppm) or
                isinstance(force, hoomd.md.pair.ewald) or
                isinstance(force, hoomd.md.special_pair.coulomb)):
            hoomd_force_groups['QQ'].append(force)
            hoomd_force_groups['nonbond'].append(force)
            hoomd_force_groups['all'].append(force)
        else:
            warnings.warn("Hoomd Force {} unrecognized, ignoring".format(force))

    return hoomd_force_groups

def get_hoomd_energy(key, hoomd_force_groups, calc_group):
    """ Calculate energy for a list of hoomd forces 
    
    Parameters
    ---------
    key : str
    hoomd_force_groups : dictionary 
        str : list of Hoomd forces
    calc_group : hoomd.group
    
    Returns
    -------
    total_energy : float"""

    total_energy = 0
    total_energy = sum([a.get_energy(calc_group) 
                        for a in hoomd_force_groups[key]])
    return total_energy

