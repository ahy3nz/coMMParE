import shutil
import tempfile
import subprocess

import pandas as pd

def build_run_measure_cassandra(structure):
    # TODO: Alex, should we use the with: commands here
    tmp_dir = tempfile.mkdtemp() # Create a tempdir for any temporary I/O
    mcf_file = '{tmp_dir}/structure.mcf'.format(tmp_dir=tmp_dir)
    xyz_file = '{tmp_dir}/structure.xyz'.format(tmp_dir=tmp_dir)

    structure.save(mcf_file)
    structure.save(xyz_file)

    inp_file = write_cassandra_inp(tmp_dir)
    fraglib_setup, cassandra = detect_cassandra_binaries()
    output = run_fraglib_setup(fraglib_setup, cassandra, inp_file, mcf_file,
            output='{tmp_dir}/out'.format(tmp_dir=tmp_dir))
    output = run_cassandra(cassandra, inp_file, mcf_file, xyz_file, output=output)

    energies = get_cassandra_energy(output + ".edr")

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
    key_to_col = {'bond': None, 
                 'angle': None, 
              'dihedral': None, 
               'nonbond':['Energy_LJ', 'Energy_Elec'], 
                   'all':['Energy_Total']} 
    
    prp_df = pd.read_fwf(prpfile,header=1,comment="#") 
    
    for canonical_name, df_cols in key_to_col.items(): 
        if df_cols is not None: 
            cassandra_force_groups['cassandra'][canonical_name] = sum([ 
                                    float(prp_df.iloc[1][col]) for col in df_cols 
                                    if col in prp_df.columns]) 
        else: 
            cassandra_force_groups['cassandra'][canonical_name] = 'N/A' 

    return cassandra_force_groups

def run_fraglib_setup(fraglib_setup,cassandra,inp_file,mcf_file,pdb_file,output='out'):
    fraglib_cmd = ('python2 {fraglib_setup} {cassandra} '.format(fraglib_setup=fraglib_setup,
                                                                  cassandra=cassandra) + 
                   '{inp_file} {pdb_file}'.format(inp_file=inp_file, pdb_file= pdb_file))
    p = subprocess.Popen(fraglib_cmd,
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True)
    out,err = p.communicate()
    with open ('casssandra_fraglib.out', 'w') as fraglib_out:
        fraglib_out.write(out)
    with open ('casssandra_fraglib.err', 'w') as fraglib_err:
        fraglib_err.write(err)
    if p.returncode != 0:
        print('Cassandra fragment library generation failed, '
              'see cassandra_fraglib.err')

    # TODO: Alex, what is going on here? 
    return output

def run_cassandra(cassandra, inp_file):
    cassandra_cmd = ('{cassandra} {inp_file}'.format(cassandra=cassandra,
                                                     inp_file=inp_file))
    p = subprocess.Popen(cassandra_cmd,
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True)
    out,err = p.communicate()
    with open ('casssandra.out', 'w') as fraglib_out:
        fraglib_out.write(out)
    with open ('casssandra.err', 'w') as fraglib_err:
        fraglib_err.write(err)
    if p.returncode != 0:
        print('Cassandra failed, see cassandra.err')

    # TODO: Alex, what is going on here? 
    return output


def detect_cassandra_binaries():

    cassandra = shutil.which('cassandra.exe')
    fraglib_setup = shutil.which('library_setup.py')

    if cassandra is None or fraglib_setup is None:
        raise ValueError("Error detecting cassandra. Both 'cassandra.exe' and "
                         "library_setup.py must be in your PATH")

    return fraglib_setup, cassandra

def write_cassandra_inp(tmp_dir):
    filename = '{tmp_dir}/enertest.inp'.format(tmp_dir=tmp_dir)
    with open(filename, 'w') as inpfile:
        inpfile.write("""! Input file for testing energies

# Run_Name
enertest.out
!------------------------------------------------------------------------------

# Sim_Type
nvt_mc
!------------------------------------------------------------------------------

# Nbr_Species
1
!------------------------------------------------------------------------------

# VDW_Style
lj cut_tail 12.0
!------------------------------------------------------------------------------

# Charge_Style
coul ewald 12.0 1e-5
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

# Prob_Rotation
1
1.0

# Prob_Regrowth
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
energy_lj
energy_elec
energy_total
!------------------------------------------------------------------------------

# CBMC_Info
kappa_ins 10
kappa_dih 10
rcut_cbmc 6.5
!------------------------------------------------------------------------------
!---------------------------Exact choices unimportant for single frame energies

# Fragment_Files
!------------------------------------------------------------------------------
!------------------------------frag_library_setup.py will autofill this section 

END""")

    return filename

