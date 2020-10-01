This is a collection of packages
- `FBEM`: solve Stokes equation via FBEM
- `mesh`: creates triangulated mesh for FBEM 
- `mesh.plot`: visualizations
- `simulation`: helper code to run lare-scale simulations with multi-threading.




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


