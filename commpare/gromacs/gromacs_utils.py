import shutil
import tempfile
import subprocess

import pandas as pd
import panedr

from commpare.utils import temporary_directory, temporary_cd

def build_run_measure_gromacs(structure):
    with temporary_directory() as tmpdir:
        with temporary_cd(tmpdir):

            gro_file = 'structure.gro'
            top_file = 'structure.top'

            structure.save(gro_file, overwrite=True)
            structure.save(top_file, overwrite=True)

            mdp_file = write_gmx_mdp()
            grompp, mdrun = detect_gmx_binaries()
            output = run_grompp(grompp, mdp_file, gro_file, top_file, 
                    output='out')
            output = run_mdrun(mdrun, output=output)

            energies  = get_gmx_energy(output + ".edr")

            df = pd.DataFrame.from_dict(energies, orient='index')

            df = df[['bond', 'angle', 'dihedral', 'LJ', 'QQ', 'nonbond', 'all']]

    return df 

def get_gmx_energy(edrfile):
    """ Parse and canonicalize energies from gromacs edr file 
    
    Notes
    -----
    gromacs energy units are kJ/mol
    """
    gmx_force_groups = {'gromacs': {}}
    key_to_col = {'bond':['Bond'], 
            'angle':['Angle'], 
            'dihedral':['Proper Dih.', 'Ryckaert-Bell.'],
            'LJ': ['LJ-14', 'LJ (SR)'],
            'QQ': ['Coulomb-14', 'Coulomb (SR)'],
            'nonbond':['LJ-14', 'Coulomb-14', 'LJ (SR)', 'Coulomb (SR)'],
            'all':['Potential']}

    edr_df = panedr.edr_to_df(edrfile) # From the edr

    for canonical_name, df_cols in key_to_col.items():
        gmx_force_groups['gromacs'][canonical_name] = sum([
                                    edr_df.iloc[0][col] for col in df_cols
                                    if col in edr_df.columns])

    return gmx_force_groups

def run_mdrun(mdrun, output='out'):
    mdrun_cmd = '{mdrun} -deffnm {output}'.format(mdrun=mdrun, output=output)
    p = subprocess.Popen(mdrun_cmd,
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True)
    out, err = p.communicate()
    with open('gmx_mdrun.out', 'w') as mdrun_out: 
        with open('gmx_mdrun.err', 'w') as mdrun_err:
            mdrun_out.write(out)
            mdrun_err.write(err)
            if p.returncode != 0:
                mdrun_err.write("gmx mdrun command {} failed".format(mdrun_cmd) +
                ", see gmx_mdrun.err")

    return output

def run_grompp(grompp, mdp_file, gro_file, top_file, output='out'):
    grompp_cmd = ('{grompp} -f {mdp_file} '.format(grompp=grompp,
                                                        mdp_file=mdp_file) +
            '-c {gro_file} -p {top_file} '.format(gro_file=gro_file,
                                                top_file=top_file) +
            '-o {output} -maxwarn 5'.format(output=output))
    p = subprocess.Popen(grompp_cmd,
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True)
    out, err = p.communicate()
    with open('gmx_grompp.out', 'w') as grompp_out:
        with open('gmx_grompp.err', 'w') as grompp_err:
            grompp_out.write(out)
            grompp_err.write(err)
            if p.returncode != 0:
                grompp_err.write("gmx grompp command {} ".format(grompp_cmd) +
                "failed , see gmx_grommpp.err")

    return output


def detect_gmx_binaries():
    grompp = None
    mdrun = None

    if shutil.which('gmx'):
        grompp = 'gmx grompp '
        mdrun = 'gmx mdrun '
    elif shutil.which('gmx_d'):
        grompp = 'gmx_d grompp'
        mdrun = 'gmx_d mdrun'
    if grompp is None or mdrun is None:
        raise ValueError("Error detecting gromacs binaries")

    return grompp, mdrun

def write_gmx_mdp():
    filename = 'grompp.mdp'
    with open(filename, 'w') as mdpfile:
        # Taken from
        # https://github.com/ctk3b/validate/blob/master/validate/tests/gromacs/grompp.mdp
        mdpfile.write("""; RUN CONTROL PARAMETERS =
integrator               = md
; start time and timestep in ps =
tinit                    = 0
dt                       = 0.002
nsteps                   = 0
; printing energy
nstenergy                = 1
; mode for center of mass motion removal =
comm-mode                = Linear
; number of steps for center of mass motion removal =
nstcomm                  = 1
; group(s) for center of mass motion removal =
comm-grps                =
; NEIGHBORSEARCHING PARAMETERS =
; nblist update frequency =
nstlist                  = 1
; ns algorithm (simple or grid) =
ns_type                  = grid
; Periodic boundary conditions: xyz or no =
pbc                      = xyz
; nblist cut-off         =
rlist                    = 0.9

; OPTIONS FOR ELECTROSTATICS AND VDW =
; Method for doing electrostatics =
cutoff-scheme            = verlet
coulombtype              = PME
coulomb-modifier         = None
rcoulomb                 = 1.999
; Dielectric constant (DC) for cut-off or DC of reaction field =
epsilon-r                = 1
; Method for doing Van der Waals =
vdw-type                 = cut-off
vdw-modifier             = None
; cut-off lengths        =
rvdw                     = 1.999
; Apply long range dispersion corrections for Energy and Pressure =
DispCorr                 = Ener
; Spacing for the PME/PPPM FFT grid =
fourierspacing           = 0.1
; EWALD/PME/PPPM parameters =
pme_order                = 4
ewald_rtol               = 1e-06
ewald_geometry           = 3d
epsilon_surface          = 0

; OPTIONS FOR BONDS     =
constraints              = none

; GENERATE VELOCITIES FOR STARTUP RUN =
gen_vel                  = no
continuation             = yes """)

    return filename

