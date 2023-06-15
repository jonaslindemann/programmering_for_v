# state file generated using paraview version 5.10.1

# uncomment the following three lines to ensure this script works in future versions
#import paraview
#paraview.compatibility.major = 5
#paraview.compatibility.minor = 10

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# ----------------------------------------------------------------
# setup views used in the visualization
# ----------------------------------------------------------------

# get the material library
materialLibrary1 = GetMaterialLibrary()

# Create a new 'Render View'
renderView1 = CreateView('RenderView')
renderView1.ViewSize = [1856, 1088]
renderView1.AxesGrid = 'GridAxes3DActor'
renderView1.CenterOfRotation = [199.5, 199.5, 0.0]
renderView1.StereoType = 'Crystal Eyes'
renderView1.CameraPosition = [-157.53438561025428, 833.4911514203418, 312.0280783634667]
renderView1.CameraFocalPoint = [334.06824403491464, -39.454788162731475, -117.60511672619899]
renderView1.CameraViewUp = [0.14383332920946137, -0.37060346596724814, 0.9175865323889544]
renderView1.CameraFocalDisk = 1.0
renderView1.CameraParallelScale = 282.13560569343247
renderView1.BackEnd = 'OSPRay raycaster'
renderView1.OSPRayMaterialLibrary = materialLibrary1

SetActiveView(None)

# ----------------------------------------------------------------
# setup view layouts
# ----------------------------------------------------------------

# create new layout object 'Layout #1'
layout1 = CreateLayout(name='Layout #1')
layout1.AssignView(0, renderView1)
layout1.SetSize(1856, 1088)

# ----------------------------------------------------------------
# restore active view
SetActiveView(renderView1)
# ----------------------------------------------------------------

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create a new 'Legacy VTK Reader'
elevationvtk = LegacyVTKReader(registrationName='elevation.vtk', FileNames=['C:\\Users\\Jonas Lindemann\\Development\\programmering_for_v\\elevation.vtk'])

# create a new 'Warp By Scalar'
warpByScalar1 = WarpByScalar(registrationName='WarpByScalar1', Input=elevationvtk)
warpByScalar1.Scalars = ['POINTS', 'Scalars8']
warpByScalar1.ScaleFactor = 0.15960000000000002

# ----------------------------------------------------------------
# setup the visualization in view 'renderView1'
# ----------------------------------------------------------------

# show data from warpByScalar1
warpByScalar1Display = Show(warpByScalar1, renderView1, 'StructuredGridRepresentation')

# get color transfer function/color map for 'Scalars8'
scalars8LUT = GetColorTransferFunction('Scalars8')
scalars8LUT.RGBPoints = [5.0, 0.231373, 0.298039, 0.752941, 130.0, 0.865003, 0.865003, 0.865003, 255.0, 0.705882, 0.0156863, 0.14902]
scalars8LUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'Scalars8'
scalars8PWF = GetOpacityTransferFunction('Scalars8')
scalars8PWF.Points = [5.0, 0.0, 0.5, 0.0, 255.0, 1.0, 0.5, 0.0]
scalars8PWF.ScalarRangeInitialized = 1

# trace defaults for the display properties.
warpByScalar1Display.Representation = 'Surface'
warpByScalar1Display.ColorArrayName = ['POINTS', 'Scalars8']
warpByScalar1Display.LookupTable = scalars8LUT
warpByScalar1Display.SelectTCoordArray = 'None'
warpByScalar1Display.SelectNormalArray = 'None'
warpByScalar1Display.SelectTangentArray = 'None'
warpByScalar1Display.OSPRayScaleArray = 'Scalars8'
warpByScalar1Display.OSPRayScaleFunction = 'PiecewiseFunction'
warpByScalar1Display.SelectOrientationVectors = 'None'
warpByScalar1Display.ScaleFactor = 39.900000000000006
warpByScalar1Display.SelectScaleArray = 'Scalars8'
warpByScalar1Display.GlyphType = 'Arrow'
warpByScalar1Display.GlyphTableIndexArray = 'Scalars8'
warpByScalar1Display.GaussianRadius = 1.995
warpByScalar1Display.SetScaleArray = ['POINTS', 'Scalars8']
warpByScalar1Display.ScaleTransferFunction = 'PiecewiseFunction'
warpByScalar1Display.OpacityArray = ['POINTS', 'Scalars8']
warpByScalar1Display.OpacityTransferFunction = 'PiecewiseFunction'
warpByScalar1Display.DataAxesGrid = 'GridAxesRepresentation'
warpByScalar1Display.PolarAxes = 'PolarAxesRepresentation'
warpByScalar1Display.ScalarOpacityFunction = scalars8PWF
warpByScalar1Display.ScalarOpacityUnitDistance = 10.437319885687145

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
warpByScalar1Display.ScaleTransferFunction.Points = [5.0, 0.0, 0.5, 0.0, 255.0, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
warpByScalar1Display.OpacityTransferFunction.Points = [5.0, 0.0, 0.5, 0.0, 255.0, 1.0, 0.5, 0.0]

# setup the color legend parameters for each legend in this view

# get color legend/bar for scalars8LUT in view renderView1
scalars8LUTColorBar = GetScalarBar(scalars8LUT, renderView1)
scalars8LUTColorBar.Title = 'Scalars8'
scalars8LUTColorBar.ComponentTitle = ''

# set color bar visibility
scalars8LUTColorBar.Visibility = 1

# show color legend
warpByScalar1Display.SetScalarBarVisibility(renderView1, True)

# ----------------------------------------------------------------
# setup color maps and opacity mapes used in the visualization
# note: the Get..() functions create a new object, if needed
# ----------------------------------------------------------------

# ----------------------------------------------------------------
# restore active source
SetActiveSource(warpByScalar1)
# ----------------------------------------------------------------


if __name__ == '__main__':
    # generate extracts
    SaveExtracts(ExtractsOutputDirectory='extracts')