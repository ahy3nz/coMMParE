import pandas as pd
import simtk.openmm as openmm
import simtk.unit as unit


def build_run_measure_openmm(structure, **kwargs):
    """ Build OpenMM simulation from a parmed.Structure """
    try:
        omm_system = structure.createSystem()

        integrator = openmm.VerletIntegrator(1.0)
        omm_context = openmm.Context(omm_system, integrator)
        omm_context.setPositions(structure.positions)

        set_omm_force_groups(omm_context)
        omm_force_groups = get_omm_force_groups(omm_context)
        energies = {'openmm': {key: get_omm_energy(key, 
                                                    omm_force_groups, 
                                                    omm_context)._value
                                                    for key in omm_force_groups}}
        df = pd.DataFrame.from_dict(energies, orient='index')
    except:
        df = pd.DataFrame.from_dict({'openmm':{}}, orient='index')

    return df

def get_omm_energy(key, omm_force_groups, omm_context):
    """ Calculate energy for a set of openmm force groups 
    
    Notes
    ----
    Default OpenMM energy units are kJ/mol"""
    if key == 'all':
        return (omm_context.getState(getEnergy=True).getPotentialEnergy())
    if len(omm_force_groups[key]) == 0:
        return 0 * unit.kilojoule_per_mole
    return (omm_context.getState(getEnergy=True, groups=omm_force_groups[key])
                        .getPotentialEnergy())


def get_omm_force_groups(omm_context):
    """ Get force groups associated with the openmm forces """
    omm_force_groups = {'bond':set(), 'angle':set(), 
            'dihedral':set(), 'nonbond':set(), 'all':{-1}}
    for force in omm_context.getSystem().getForces():
        if isinstance(force, openmm.HarmonicBondForce):
            omm_force_groups['bond'].add(force.getForceGroup())
        elif isinstance(force, openmm.HarmonicAngleForce):
            omm_force_groups['angle'].add(force.getForceGroup())
        elif isinstance(force, openmm.RBTorsionForce):
            omm_force_groups['dihedral'].add(force.getForceGroup())
        elif isinstance(force, openmm.PeriodicTorsionForce):
            omm_force_groups['dihedral'].add(force.getForceGroup())
        elif isinstance(force, openmm.NonbondedForce):
            omm_force_groups['nonbond'].add(force.getForceGroup())
        else:
            print("OMM Force {} unrecognized, ignoring".format(force))

    return omm_force_groups

def set_omm_force_groups(omm_context):
    """ Separate OpenMM forces into separate groups for computation """
    for force in omm_context.getSystem().getForces():
        if isinstance(force, openmm.HarmonicBondForce):
            force.setForceGroup(0)
        elif isinstance(force, openmm.HarmonicAngleForce):
            force.setForceGroup(1)
        elif isinstance(force, openmm.RBTorsionForce):
            force.setForceGroup(12)
        elif isinstance(force, openmm.PeriodicTorsionForce):
            force.setForceGroup(12)
        elif isinstance(force, openmm.NonbondedForce):
            force.setForceGroup(11)
        else:
            print("OMM Force {} unrecognized, ignoring".format(force))

