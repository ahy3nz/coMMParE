import warnings
import pandas as pd
import simtk.openmm as openmm
import simtk.unit as unit

# After having written this, it looks like ParmEd already
# did something similar for OpenMM energy decompositions
def build_run_measure_openmm(structure, **kwargs):
    """ Build OpenMM simulation from a parmed.Structure """
    omm_system = structure.createSystem()

    integrator = openmm.VerletIntegrator(1.0)
    omm_context = openmm.Context(omm_system, integrator)
    omm_context.setPositions(structure.positions)

    set_omm_force_groups(omm_context)
    omm_force_groups = get_omm_force_groups(omm_context)

    # To decompose OpenMM's nonbonded force into LJ, QQ, and total energies
    # This requires updating the particle parameters to "zero out"
    # charges to get the LJ energy. 
    # The QQ energy is then the total nonbond energy minus LJ energy
    energies_total = {'openmm': {key: get_omm_energy(key, 
                                                omm_force_groups, 
                                                omm_context)._value
                                                for key in omm_force_groups}}

    original_particle_parameters = zero_out_qq(omm_system, omm_context, 
            original_particle_parameters=None)
    energies_lj = {'openmm': {key: get_omm_energy(key, 
                                                omm_force_groups, 
                                                omm_context)._value
                                                for key in omm_force_groups}}

    energies_total['openmm']['LJ'] = energies_lj['openmm']['nonbond']
    energies_total['openmm']['QQ'] = (energies_total['openmm']['nonbond'] - 
            energies_total['openmm']['LJ'])
    df = pd.DataFrame.from_dict(energies_total, orient='index')
    df = df[['bond', 'angle', 'dihedral', 'LJ', 'QQ', 'nonbond', 'all']]

    return df

def zero_out_qq(omm_system, omm_context,
        original_particle_parameters=None):
    """ For all OpenMM particle parameters, set charge to 0 """
    build_original_pparams = False
    if original_particle_parameters is None:
        original_particle_parameters = []
        build_original_pparams = True
    for force in omm_context.getSystem().getForces():
        if isinstance(force, openmm.NonbondedForce):
            for i in range(force.getNumParticles()):
                if build_original_pparams:
                    original_particle_parameters.append(
                            force.getParticleParameters(i))
                force.setParticleParameters(i,
                        0.0,
                        original_particle_parameters[i][1],
                        original_particle_parameters[i][2])
            force.updateParametersInContext(omm_context)

    return original_particle_parameters

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
            warnings.warn("OMM Force {} unrecognized, ignoring".format(force))

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
            force.setCutoffDistance(2)
        else:
            warnings.warn("OMM Force {} unrecognized, ignoring".format(force))

