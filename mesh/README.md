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

## mesh.plot

There are different ways to visualize 3D objects in Python: `matplotlib`, `mayavi`, `trimesh`.
- Therefore there are several python files for each of these methods.
- examples in `mesh.plot.example`

### `trimesh` 
Feature-rich library to work with triangular meshes.  
- combine meshes
- check orientaiton of triangles
- visualzie meshes
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
- Class MeshViewer to visualzie triangulated mesh and velocities, forces
- `mayavi` is a very good tool, but I had problems with Windows installation on my machine.

#### Installation

From conda-forge

### `matplotlib` 
- Works rather slow.
- Right now no arrows implemented and can't set aspect ratio.
