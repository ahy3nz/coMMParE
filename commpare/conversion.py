import pandas as pd
import commpare

def spawn_engine_simulations(structure, engines=None,
        round_decimal=None, hoomd_kwargs={}):
    simulate_engine = {}
    if engines is None:
        import commpare
        engines = commpare.identify_engines()

    if round_decimal is not None:
        for atom in structure.atoms:
            atom.xx = round(atom.xx,round_decimal)
            atom.xy = round(atom.xy,round_decimal)
            atom.xz = round(atom.xz,round_decimal)

    # For each identified engine, measure energy, store in dataframe
    energies = pd.DataFrame()
    for engine in engines:
        if engine == 'cassandra':
            import commpare.cassandra
            energies = energies.append(
                    commpare.cassandra.build_run_measure_cassandra(structure))
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

