# FBEM 

![two_cilia.png](../assets/two_cilia.png)

A software to solve the Stokes equation with fast-multipole boundary element method.

- Generates input files for a third-party hydrodynamic solver (FMM-BEM [1]).
- Computes velocities from a given surface force distribution. 
  Can solve the inverse and mixed problems (where not all forces are known).
    - Computing forces from velocities is a backward-problem, where a linear system is solved with GMRES.
    - In this code is adapted for the inverse problem.
- FBEM = fast Boundary Element Method

## Installation
- Download FBEM executables.
    - Go to http://www.yijunliu.com/
    - Get thee C2 package: 3D Stokes Flow.
    - Unpack. Read license and help files.
- Place FBEM executables to `FBEM/exe/` folder:
  - Windows executable `3D_Stokes_Flow_FMM_64.exe`
  - Linux executable `3D_Stokes_Flow_FMM_linux.exe`
    (we requested the file directly from the author, as it had not been available on the website)
- For Linux: give execution permission.

## Usage 

See `example` folder.
For simplicity, the fluid viscosity is set to 1. For different visosity, one can rescale input velocities.

[1] https://www.yijunliu.com/ Package C2