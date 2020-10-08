#  vedo


- https://github.com/marcomusy/vedo 
- `vedo` is built on top of `trimesh`, therefore they work in a similar way.
- `vedo` has more features; can plot frame axes, arrows, etc.
- a.k.a. vtkplotter?


## Usage

- Axes:
  - 1: scale
  - 3: large axes
  - 4: small axes in the corner
  - 7: ruler
  - 9: box
  - 12: radial angle
  - 13: scalebar? not clear what it measures
  - Customize: https://github.com/marcomusy/vedo/blob/master/examples/pyplot/customAxes.py

- Successful example on plotting arrows in LAMAS_SPP_code 2020 
- To avoid crashes - close the plotter
    ```
    plotter = m.show(axes=1)
	plotter.close()
	```

### Lights
- `plane.lighting('off')` can help with the plane being too light/too dark.
- But cilia shapes become unrealistic with this option

### camera
- when adding something to the screen should keep resetcam=False
- plotter.add() resets camera if not render=False
- in show() set resetcam=False even if `camera` option is used.



## Installation

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
   
## Problems
- Embedded in jupyter lab: "Loading widget..."  (already after installation of `k3d`)

