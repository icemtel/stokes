# Stokes: create triangulated surface meshes and solve hydrodynamic Stokes equation

![two_cilia.png](../assets/two_cilia_small.png)

This is a collection of Python packages (previously used to solve biological hydrodynamics problems, see Refs. [3,4])
- `FBEM`: routines to solve Stokes equation using a third-party hydrodynamic solver (Liu's fast multipole boundary element method FMM-BEM, see Refs. [1,2])
- `mesh`: routines to be create triangulated meshes to be used as input files for FBEM 
  - `mesh.plot`: routines for 3D mesh visualizations
- `simulation_helpers`: helpful routines to run large-scale simulations with multi-threading.

## Installation:
- Use `setup.py` file: `python setup.py develop` to install in development mode.
- Copy FBEM executables to `FBEM/exe` folder (see [FBEM README](FBEM/README.md)).
- additional packages can be installed for 3D mesh visualizaiton (see [mesh README](mesh/README.md)).

## Usage

- please see examples in `/example/` (
- the folders of the individual subprojects contain additional README files.

## Authors

- [Anton Solovev](https://github.com/icemtel)
- [Benjamin M. Friedrich](https://cfaed.tu-dresden.de/friedrich-home), email: benjamin.m.friedrich@tu-dresden.de

If you want to use this code in a scientific publication, please cite [3].

- [1] [Dr. Yijun Liu webpage](https://www.yijunliu.com/). Package C2
- [2] [Liu & Nishimura 2006](https://doi.org/10.1016/j.enganabound.2005.11.006)
- [3]: [Solovev & Friedrich 2021 EPJ E ST](https://link.springer.com/article/10.1140/epje/s10189-021-00016-x); 
       also available as [arXiv preprint](https://arxiv.org/abs/2010.08111) 
- [4]: [Solovev & Friedrich 2020 arXiv:2012:11741](https://arxiv.org/abs/2012.11741)
