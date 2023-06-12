import numpy as np
from vedo import *
# Create a scalar field: the distance from point (15,15,15)
X, Y, Z = np.mgrid[:30, :30, :30]
scalar_field = ((X-15)**2 + (Y-15)**2 + (Z-15)**2)/225
# Create the Volume from the numpy object
vol = Volume(scalar_field)
# Generate the surface that contains all voxels in range [1,2]
lego = vol.legosurface(1,2)
show(lego, axes=True)