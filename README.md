# Gaussian-Amesp

**大师大法好！**

## Introduction

Gaussian-Amesp is a solution for invoking Amesp from Gaussian, which means one
can do optimization, frequencies, or even irc tasks using the algorithms from
Gaussian and at the levels supported by Amesp.

## Usage

To use this script `gamesp.py`, these softwares have to be installed.

- [Gaussian](https://gaussian.com/)
- [Amesp](https://amesp.xyz)
- Python3

Then a Amesp input template should be given with the name of `template.aip`.
Here is an example of `B3LYP-D3BJ/6-31G**` level. The `xyz` section is
unnecessary.

```
% npara 10
% maxcore 2000
! B3LYP D3BJ 6-31G**
```

Then a Gaussian input file should be put under the same directory with
`template.inp`. In the Gaussian input file, the method and basis set should be
replaced by `python3 -u /path/to/gamesp.py`, since Gaussian serves as an
optimizer here. When Gaussian input file and Amesp template file are prepared,
run this task like normal Gaussian task.

Currently, this script can parse the output of energy, dipole, force, and
hessian from Amesp output. If you will use methods without analytical hessian
and need to calculate frequencies, write `freq=num` in Gaussian will work. In
this case, Gaussian will call Amesp to calculate force, and Gaussian will use
these force data to calculate hessian, then you can obtain the frequencies.

## Example

Here is an example of ts and irc tasks of CH3CN <-> CH3NC reaction under `examples/CH3CN`.

