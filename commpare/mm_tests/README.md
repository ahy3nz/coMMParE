# MM tests
These tests will take input from various forms 
(amber, gromacs, openmm, mosdef, etc.),
process them into a `pmd.Structure`,
and then output to all available engines for energy calculation.

## Reference systems
The testing suite attempts to find the [`validate package`](https://github.com/ctk3b/validate/tree/master/validate/tests)
and proceed to use those testing files
