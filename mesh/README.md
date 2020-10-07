# mesh

- Create meshed system of objects. Use it to run FBEM.
- Examples of use available in FBEM/example

Features:
- **Create**: define simple objects, set density of grid points.
- **Transform**: rotate, translate in space
- **Combine**: combine objects in a nested dictionary; on each level a transform can be applied.
- **Triangulate:** create a triangular mesh (defined by coordinates of nodes, and indices of nodes in each triangle).
- **Visualize:** `mesh.plot`

---

## Create mesh
- Look at examples
- Unmeshed objects are kept in a form of nested dictionaries
  (e.g. (1) object1 -> rotate;  (2) object2 -> translate;   (3): combine (1)+(2))
- Meshed objected are stored as Triangulation class with attributes `coordinates`, `triangulation` (triangles), `velocities`;
  - Note: there is some inconsistency with triangulation read from FBEM input files; they are read as two arrays: 
    `coordinates`, `triangles`.

## mesh.plot

There are different ways to visualize 3D objects in Python: `matplotlib`, `mayavi`, `trimesh`, `vedo`.
- Therefore there are several python files for each of these methods.
- Recommended way: `vedo` or `trimesh`. 
- examples in `mesh.plot.example`

### `vedo` 
- https://github.com/marcomusy/vedo 
- `vedo` is built on top of `trimesh`, therefore they work in a similar way.
- `vedo` has more features; can plot frame axes, arrows, etc.
- a.k.a. vtkplotter?


#### Installation

-  Install via conda
   ```
   conda install -c conda-forge vedo
   ```
- May need additional packages, but  
   I already had `vtk` and `trimesh` installed, so nothing extra was required.
-  For notebooks: install extra?
    ```
    conda install -c conda-forge k3d 
    ```
   
#### Problems
- Embedded in jupyter lab: "Loading widget..."  (already after installation of `k3d`)

#### Usage

- Axes:
  - 1: scale
  - 3: large axes
  - 4: small axes in the corner
  - Customize: https://github.com/marcomusy/vedo/blob/master/examples/pyplot/customAxes.py

- Successful example on plotting arrows in LAMAS_SPP_code 2020 
- To avoid crashes - close the plotter
    ```
    plotter = m.show(axes=1)
	plotter.close()
	```

#### Installation

### `trimesh` 
Feature-rich library to work with triangular meshes.  
- Visualization of meshes is only one application.
- Can possibly use it to work with the meshes, e.g.,
    - combine meshes
    - check orientaiton of triangles
    - subdivide meshes      
    
#### Installation
https://github.com/mikedh/trimesh/

```	
conda install trimesh      # 3.8.4
conda install networkx     # 2.5 # for visualization
# for a pop-up window when run from a script (don't need if run from jupyter lab)
conda install pyglet	   # 1.5.7 
```


#### Usage

- Hotkeys when called from a python script:
  - `w`: toggle wireframe view
  - `a`: toggle axes


### `mayavi` 
- Class MeshViewer to visualize triangulated mesh and velocities, forces
- `mayavi` is a very good tool, but I had problems with Windows installation on my machine.

#### Installation

From conda-forge

### `matplotlib` 
- Works rather slow.
- Right now no arrows implemented and can't set aspect ratio.
