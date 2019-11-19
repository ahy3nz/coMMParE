import shutil
import tempfile
import contextlib
import subprocess
import os

import pandas as pd
import mdtraj
import mbuild as mb

from mbuild.formats.cassandramcf import write_mcf

def build_run_measure_cassandra(structure):

    fraglib_setup, cassandra = detect_cassandra_binaries()
    workdir = os.getcwd()
    mcf_file = 'structure.mcf'
    xyz_file = 'structure.xyz'
    pdb_file = 'structure.pdb'

    with temporary_directory() as tmp_dir:
        with temporary_cd(tmp_dir):
            # Guess dihedral type...from contents of structure
            if len(structure.dihedrals) > 0:
                dihedral_style = 'charmm'
            else:
                dihedral_style = 'opls'
            write_mcf(structure,mcf_file,angle_style='harmonic',
                    dihedral_style=dihedral_style)
            mb.load(structure).save(xyz_file)
            mb.load(structure).to_trajectory().save_pdb(pdb_file)

            inp_file,output = write_cassandra_inp()
            successful_fraglib = run_fraglib_setup(fraglib_setup, cassandra,
                                 inp_file, mcf_file, pdb_file, workdir)
            if successful_fraglib:
                run_cassandra(cassandra, inp_file, workdir)
                energies = get_cassandra_energy(output + '.log')
            else:
                print("Cassandra failed due to unsuccessful fragment generation")

    df = pd.DataFrame.from_dict(energies, orient='index')

    return df

def get_cassandra_energy(prpfile):
    """ Parse and canonicalize energies from cassandra prp file

    Notes
    -----
    Cassandra energy units are kJ/mol
    Currently only support nonbond and all energy since Cassandra
    does not support writing bond/angle/dihedral energies
    """

    cassandra_force_groups = {'cassandra': {}}
    key_to_data = {'bond':['Bondenergy'],
                  'angle':['Bondangleenergy'],
               'dihedral':['Dihedralangleenergy'],
                'nonbond':['Intramoleculevdw','Intramoleculeq','Intermoleculevdw',
                           'Intermoleculeq', 'Reciprocalewald','Selfewald'],
                    'all':['Totalsystemenergy']}

    prp_dict = {}
    read_lines = False
    with open(prpfile) as f:
        for line in f:
            if line.strip() == 'Compute total energy':
                read_lines = True
            if read_lines == True and line.strip().split() != []:
                key = ''
                for word in line.strip().split()[:-1]:
                    key += word
                val = line.strip().split()[-1]
                prp_dict[key] = val


    #Factor to convert atomic energy (amu A^2/ ps^2) to kJ/mol
    atomic_to_kJmol = 0.01
    for canonical_name, cass_names in key_to_data.items():
        if cass_names is not None:
            cassandra_force_groups['cassandra'][canonical_name] = sum([
                                    float(prp_dict[item])*atomic_to_kJmol
                                    for item in cass_names
                                    if item in prp_dict.keys()])
        else:
            cassandra_force_groups['cassandra'][canonical_name] = 'N/A'

    return cassandra_force_groups

def run_fraglib_setup(fraglib_setup,cassandra,inp_file,mcf_file,pdb_file,workdir):
    fraglib_cmd = ('python2 {fraglib_setup} {cassandra} '.format(fraglib_setup=fraglib_setup,
                                                                  cassandra=cassandra) +
                   '{inp_file} {pdb_file}'.format(inp_file=inp_file, pdb_file= pdb_file))
    p = subprocess.Popen(fraglib_cmd,
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True)
    out,err = p.communicate()
    with open (workdir+'/casssandra_fraglib.out', 'w') as fraglib_out:
        fraglib_out.write(out)
    with open (workdir+'/casssandra_fraglib.err', 'w') as fraglib_err:
        fraglib_err.write(err)
    if p.returncode != 0:
        print('Cassandra fragment library generation failed, '
              'see cassandra_fraglib.err')
        return False
    return True

def run_cassandra(cassandra, inp_file, workdir):
    cassandra_cmd = ('{cassandra} {inp_file}'.format(cassandra=cassandra,
                                                     inp_file=inp_file))
    p = subprocess.Popen(cassandra_cmd,
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True)
    out,err = p.communicate()
    with open (workdir+'/casssandra.out', 'w') as fout:
        fout.write(out)
    with open (workdir+'/casssandra.err', 'w') as ferr:
        ferr.write(err)
    if p.returncode != 0:
        print('Cassandra failed, see cassandra.err')

def detect_cassandra_binaries():

    cassandra_exec_names = [ 'cassandra.exe',
                             'cassandra_gfortran.exe',
                             'cassandra_pgfortran.exe',
                             'cassandra_gfortran_openMP.exe',
                             'cassandra_pgfortran_openMP.exe',
                             'cassandra_intel_openMP.exe' ]

    py2_exec_names = [ 'python2', 'python2.7' ]

    for name in cassandra_exec_names:
        cassandra = shutil.which(name)
        if cassandra is not None:
            break

    fraglib_setup = shutil.which('library_setup.py')

    if cassandra is None or fraglib_setup is None:
        raise ValueError("Error detecting cassandra. Both 'cassandra_*.exe' and "
                         "'library_setup.py' must be in your PATH")

    for name in py2_exec_names:
        py2 = shutil.which(name)
        if py2 is not None:
            break
    if py2 is None:
        raise ValueError("Error detecting python2. library_setup.py requires python2")

    print("Using the following executables for Cassandra:")
    print("Python: {}".format(py2))
    print("library_setup: {}".format(fraglib_setup))
    print("Cassandra: {}".format(cassandra))

    return fraglib_setup, cassandra

def write_cassandra_inp():
    filename = 'enertest.inp'
    output = 'enertest.out'
    with open(filename, 'w') as inpfile:
        inpfile.write("""! Input file for testing energies

# Run_Name
{output}
!------------------------------------------------------------------------------

# Sim_Type
nvt_mc
!------------------------------------------------------------------------------

# Nbr_Species
1
!------------------------------------------------------------------------------

# VDW_Style
lj cut 19.99
!------------------------------------------------------------------------------

# Charge_Style
coul ewald 19.99 1e-5
!------------------------------------------------------------------------------

# Seed_Info
1 2
!------------------------------------------------------------------------------

# Rcutoff_Low
0.5
!------------------------------------------------------------------------------

# Molecule_Files
structure.mcf 1
!------------------------------------------------------------------------------

# Box_Info
1
cubic
100.
!------------------------------------------------------------------------------

# Temperature_Info
300.0
!------------------------------------------------------------------------------

# Move_Probability_Info
!------------------------------------------------------------------------------
!-------------------------Choices don't matter for the single frame energy calc

# Prob_Translation
1
1.0

# Done_Probability_Info
!------------------------------------------------------------------------------

# Start_Type
read_config 1 structure.xyz
!------------------------------------------------------------------------------

# Run_Type
production   1
!------------------------------------------------------------------------------

# Simulation_Length_Info
units        sweeps
prop_freq    1
coord_freq   1
run          0
!------------------------------------------------------------------------------

# Property_Info 1
energy_total
!------------------------------------------------------------------------------

# Fragment_Files
!------------------------------------------------------------------------------
!-----------------------------------library_setup.py will autofill this section

END""".format(output=output))

    return filename,output

@contextlib.contextmanager
def temporary_cd(dir_path):
    import os
    prev_dir = os.getcwd()
    os.chdir(os.path.abspath(dir_path))
    try:
        yield
    finally:
        os.chdir(prev_dir)

@contextlib.contextmanager
def temporary_directory():
    import shutil
    import tempfile
    tmp_dir = tempfile.mkdtemp()
    try:
        yield tmp_dir
    finally:
        shutil.rmtree(tmp_dir)


