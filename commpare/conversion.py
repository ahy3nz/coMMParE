import pandas as pd
import commpare

def spawn_engine_simulations(structure, engines=None,
        hoomd_kwargs={}):
    simulate_engine = {}
    if engines is None:
        engines = commpare.identify_engines()

    # For each identified engine, measure energy, store in dataframe
    energies = pd.DataFrame()
    for engine in engines:
        if engine == 'gromacs':
            energies.append(commpare.gromacs.build_run_measure_gromacs(structure))
        if engine == 'openmm':
            energies.append(commpare.openmm.build_run_measure_openmm(structure))
        if engine == 'hoomd':
            energies.append(commpare.hoomd.build_run_measure_hoomd(structure,
                **hoomd_kwargs))

    return energies

