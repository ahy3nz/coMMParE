# coMMParE - Comparing Molecular Mechanics Potential Energies

The goal of this package is to evaluate energies using
ParmEd as a middleman.
Ideas derive slightly from
[Christoph Klein's `validate` repo](https://github.com/ctk3b/validate).

Some overarching goals:

* Validate FF parameter and molecular model translation to
a particular format or data structure
* Assess consistency of MD engines in calculating energies

The broad steps to compare energy via various permutations:

* Input of molecular model (MD input files, Pythonic creation, etc)
    * These inputs get turned into `parmed.Structure`
* Output of molecular model for energy calculation (MD engine)
    * The `parmed.Structure` gets converted to its respective
    MD engine data object/format

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

## MD-interconversion tools
* [parmed](https://github.com/ParmEd/ParmEd) [(conda)](https://anaconda.org/omnia/parmed)
* [this mbuild PR](https://github.com/mosdef-hub/mbuild/pull/622)

## MD engines for measuring energy (outputs)
* [openmm](https://github.com/openmm/openmm) [(conda)](https://anaconda.org/omnia/openmm)
* [hoomd](https://github.com/glotzerlab/hoomd-blue) [(conda)](https://anaconda.org/conda-forge/hoomd)
* [gromacs](http://manual.gromacs.org/)
    * [panedr](https://github.com/jbarnoud/panedr) [(conda)](https://anaconda.org/conda-forge/panedr)
