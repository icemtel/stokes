# Stokes: 

[TODO: visualization of mesh]

This is a collection of packages - see individual README files. [TODO]
- `FBEM`: solve Stokes equation via a third-party hydrodynamic solver (FMM-BEM [1])
- `mesh`: creates triangulated mesh for FBEM 
  - `mesh.plot`: 3D mesh visualizations
- `simulation`: helper code to run large-scale simulations with multi-threading.



## Installation:
- Run `setup.py` with `develop` option.
`python setup.py develop`
- Copy FBEM executables to `FBEM/exe` folder (see below).

### FBEM

A software to solve Stokes equation with fast-multipole boundary element method.
Can find velocities from forces, or vice-versa, and mixed problems
(the backwards problem is a linear system which is solved with GMRES).


- Download FBEM executables
- Go to http://www.yijunliu.com/
- Get thee C2 package: 3D Stokes Flow.
- Unpack. Read license and help files.
- Place FBEM executables to `FBEM/exe/` folder:
  - `3D_Stokes_Flow_FMM_64.exe` for Windows
  - `3D_Stokes_Flow_FMM_linux.exe` for Linux (might not be included on the website?)
- Check if there is execution permission on Linux.


Usage:
- see examples in `FBEM/example`
- For simplicity, the fluid viscosity is always set to 1.

[1] Liu 2006... TODO
[2] Solovev arxiv TODO
