# coMMParE - Comparing Molecular Mechanics Potential Energies

The goal of this package is to evaluate energies using
ParmEd as a middleman.
Ideas derive slightly from
[Christoph Klein's `validate` repo](https://github.com/ctk3b/validate).

Some overarching goals:

* Validate FF parameter and molecular model translation to
a particular format or data structure
* Assess consistency of MM engines in calculating energies

The broad steps to compare energy via various permutations:

* Input of molecular model (MM input files, Pythonic creation, etc)
    * These inputs get turned into `parmed.Structure`
* Output of molecular model for energy calculation (MM engine)
    * The `parmed.Structure` gets converted to its respective
    MM engine data object/format

While more-sophisticated packaging may come, here is a list of possible dependencies,
with conda links where available. 
The packages for "inputs" and "outputs" are not all required, just packages
whose conversions/energy evaluations are supported here.
The only real, core package necessary is ParmEd, as it is the core data
structure used.

## Creating and parametrizing molecular models (inputs)
* [mbuild](https://github.com/mosdef-hub/mbuild) [(conda)](https://anaconda.org/mosdef/mbuild)
* [foyer](https://github.com/mosdef-hub/foyer) [(conda)](https://anaconda.org/mosdef/foyer)
* [parmed](https://github.com/ParmEd/ParmEd) [(conda)](https://anaconda.org/omnia/parmed)
* [openforcefield](https://github.com/openforcefield/openforcefield) [(conda)](https://anaconda.org/omnia/openforcefield)

## MM-interconversion tools
* [parmed](https://github.com/ParmEd/ParmEd) [(conda)](https://anaconda.org/omnia/parmed)
* [this mbuild PR](https://github.com/mosdef-hub/mbuild/pull/622)

## MM engines for measuring energy (outputs)
* [openmm](https://github.com/openmm/openmm) [(conda)](https://anaconda.org/omnia/openmm)
* [hoomd](https://github.com/glotzerlab/hoomd-blue) [(conda)](https://anaconda.org/conda-forge/hoomd)
* [gromacs](http://manual.gromacs.org/) [(conda)](https://anaconda.org/bioconda/gromacs)
    * [panedr](https://github.com/jbarnoud/panedr) [(conda)](https://anaconda.org/conda-forge/panedr)


# Contributing
There are multiple ways to expand this testing suite - more MM engines or more 
reference systems.

## Contributing new MM engine functionality
* Desired Input: `parmed.Structure` containing molecular model
* Desired Output: `pandas.DataFrame` containing energies
* Given a `parmed.Structure` object, be able to use your MM engine to 
    build your simulation and measure the energy from the intial configuration
    and molecular model parameters within the `parmed.Structure`.
    * If input files need to be written, please use the `tempfile` library
    to create and dump files to a temp directory 
    (`commpare/gromacs` utilizes temp directories)
* After building your MM engine's simulation, measure the energy and
"canonicalize" the energy terms.
    * Ultimately, we want a `pandas.DataFrame` whose `index` is the MM engine
    with `columns`: `bond`, `angle`, `dihedral`, `nonbond`. The values should be
    energies in kJ/mol. The energy breakdown may be further decomposed, but 
    the goal for now is those 4 energy groups.
* While a single function gets called in `conversion.py`, inputs a `parmed.Structure` 
(and possibly optional arguments like in `commpare/hoomd`), and 
outputs a canonicalized `pandas.DataFrame`, helper functions
are certainly welcomed and encouraged to enhance readability and debugging
* `md_engines.py` will need to be updated to detect the new MM engine
* `conversion.py` will need to be updated to convert and run the 
`parmed.Structure` in the MD engine
* Add unit tests in `commpare/tests` that, given a `parmed.Structure`, will
build the particular MM engine's simulation and return the `pandas.DataFrame`
with canonicalized energy terms.

## Contributing new MM tests
* The goal is to test different molecular model/force field terms and
observe how well they translate to different MM engines
* Ideally, there should be some directory organization to the MM tests such that
each directory is a particular chemical system understood by `parmed`
* `reference_systems.py` will need to be updated to detect the locally
available reference systems against which to test the local MM engines
* Using `pytest`, put together some test scripts in `commpare/mm_tests` that will
construct the `parmed.Structure` from the reference systems, then 
run `commpare.spawn_engine_simulations` to "shotgun" a variety of 
energy calculations
