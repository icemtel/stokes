# Stokes: create triangulated surface mesh and solve hydrodynamic Stokes equation

![two_cilia.png](../assets/two_cilia.png)

This is a collection of packages
- `FBEM`: solve Stokes equation via a third-party hydrodynamic solver (FMM-BEM, Refs. [1,2])
- `mesh`: creates triangulated mesh for FBEM 
  - `mesh.plot`: 3D mesh visualizations
- `simulation_helpers`: helper code to run large-scale simulations with multi-threading.

## Installation:
- Use `setup.py` file: `python setup.py develop` to install in developing mode.
- Copy FBEM executables to `FBEM/exe` folder (see [FBEM README](FBEM/README.md)).
- additional packages can be installed for 3D mesh visualizaiton (see [mesh README](mesh/README.md))

## Usage

- see examples in `/example/`
- See individual subprojects README files.

## Authors

- [Anton Solovev](https://github.com/icemtel)
- [Benjamin M. Friedrich](https://cfaed.tu-dresden.de/friedrich-home), email: benjamin.m.friedrich@tu-dresden.de

To reference in a scientific publication, please cite [3].

- [1] [Dr. Yijun Liu webpage](https://www.yijunliu.com/). Package C2
- [2] [Liu & Nishimura 2006](https://doi.org/10.1016/j.enganabound.2005.11.006)
- [3]: [Solovev & Friedrich 2021 EPJ E ST](https://link.springer.com/article/10.1140/epje/s10189-021-00016-x); 
       also available as [arXiv preprint](https://arxiv.org/abs/2010.08111) 
- [4]: [Solovev & Friedrich 2020 arXiv:2012:11741](https://arxiv.org/abs/2012.11741)