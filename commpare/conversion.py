import pandas as pd
import commpare

def spawn_engine_simulations(structure, engines=None,
        hoomd_kwargs={}):
    simulate_engine = {}
    if engines is None:
        import commpare
        engines = commpare.identify_engines()

    # For each identified engine, measure energy, store in dataframe
    energies = pd.DataFrame()
    for engine in engines:
        if engine == 'gromacs':
            import commpare.gromacs
            energies = energies.append(
                    commpare.gromacs.build_run_measure_gromacs(structure))
        if engine == 'openmm':
            import commpare.openmm
            energies = energies.append(
                    commpare.openmm.build_run_measure_openmm(structure))
        if engine == 'hoomd':
            import commpare.hoomd
            energies = energies.append(
                    commpare.hoomd.build_run_measure_hoomd(structure,
                                                        **hoomd_kwargs))

    return energies

