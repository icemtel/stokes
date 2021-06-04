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
  None are perfect. The latest I have been using is `vedo`.
- `matplotlib` is good when you do not want or cannot install other packages for 3D visualization.
- examples in `mesh.plot.example`

### `vedo` a.k.a. vtkplotter

- https://github.com/marcomusy/vedo 
- `vedo` is built on top of `trimesh`(?), therefore they work in a similar way.
- `vedo` has more features; can plot frame axes, arrows, etc

#### Installation

Requirements:
```
vtk=8 # vedo works slower with vtk=9
vedo=2020.4.2
```
Install via conda-forge channel.

#### Axes options:
  - 1: scale
  - 3: large axes
  - 4: small axes in the corner
  - 7: ruler
  - 9: box
  - 12: radial angle
  - 13: scalebar? not clear what it measures
  - Customize: https://github.com/marcomusy/vedo/blob/master/examples/pyplot/customAxes.py

- To avoid crashes in notebooks - close the plotter
    ```
    plotter = m.show(axes=1)
	plotter.close()
	```

#### Lights
- `plane.lighting('off')` can help with the plane being too light/too dark.
- But cilia shapes become unrealistic with this option

#### camera
- when adding something to the screen should keep resetcam=False
- plotter.add() resets camera if not render=False
- in show() set resetcam=False even if `camera` option is used.

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
vtk=8 # ? 
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
```
mayavi>=4.6
vtk=8
```

### `matplotlib` 
- Works rather slow.
- Right now no arrows implemented and can't set aspect ratio.
