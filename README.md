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

While more-sophisticated packaging may come, here is a list of dependencies:

## Creating and parametrizing molecular models (inputs)
* [mbuild](https://github.com/mosdef-hub/mbuild)
* [foyer](https://github.com/mosdef-hub/foyer)
* [openforcefield](https://github.com/openforcefield/openforcefield)

## MD-interconversion tools
* [parmed](https://github.com/ParmEd/ParmEd)
* [this mbuild PR](https://github.com/mosdef-hub/mbuild/pull/622)

## MD engines for measuring energy (outputs)
* [openmm](https://github.com/openmm/openmm)
* [hoomd](https://github.com/glotzerlab/hoomd-blue)
* [gromacs](http://manual.gromacs.org/)
