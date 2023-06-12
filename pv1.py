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
renderView1.ViewSize = [955, 839]
renderView1.AxesGrid = 'GridAxes3DActor'
renderView1.CenterOfRotation = [199.5, 199.5, 0.0]
renderView1.StereoType = 'Crystal Eyes'
renderView1.CameraPosition = [-226.86561597067842, 778.2689044876158, 654.7491995324801]
renderView1.CameraFocalPoint = [412.3920709426576, -84.38915112459519, -373.19219180635963]
renderView1.CameraViewUp = [0.6148468637105988, -0.37261898625698414, 0.6950672091719317]
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
layout1.SetSize(955, 839)

# ----------------------------------------------------------------
# restore active view
SetActiveView(renderView1)
# ----------------------------------------------------------------

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create a new 'Legacy VTK Reader'
elevationvtk = LegacyVTKReader(registrationName='elevation.vtk', FileNames=['elevation.vtk'])

# create a new 'Warp By Scalar'
warpByScalar1 = WarpByScalar(registrationName='WarpByScalar1', Input=elevationvtk)
warpByScalar1.Scalars = ['POINTS', 'Scalars8']
warpByScalar1.ScaleFactor = 0.15960000000000002

# create a new 'Extract Surface'
extractSurface1 = ExtractSurface(registrationName='ExtractSurface1', Input=warpByScalar1)

# create a new 'Generate Surface Normals'
generateSurfaceNormals1 = GenerateSurfaceNormals(registrationName='GenerateSurfaceNormals1', Input=extractSurface1)

# ----------------------------------------------------------------
# setup the visualization in view 'renderView1'
# ----------------------------------------------------------------

# show data from generateSurfaceNormals1
generateSurfaceNormals1Display = Show(generateSurfaceNormals1, renderView1, 'GeometryRepresentation')

# get color transfer function/color map for 'Scalars8'
scalars8LUT = GetColorTransferFunction('Scalars8')
scalars8LUT.RGBPoints = [5.0, 0.831373, 0.909804, 0.980392, 8.125, 0.74902, 0.862745, 0.960784, 11.25, 0.694118, 0.827451, 0.941176, 17.5, 0.568627, 0.760784, 0.921569, 23.75, 0.45098, 0.705882, 0.901961, 30.0, 0.345098, 0.643137, 0.858824, 36.25, 0.247059, 0.572549, 0.819608, 42.5, 0.180392, 0.521569, 0.780392, 45.0, 0.14902, 0.490196, 0.74902, 50.0, 0.129412, 0.447059, 0.709804, 55.0, 0.101961, 0.427451, 0.690196, 57.5, 0.094118, 0.403922, 0.658824, 60.0, 0.090196, 0.392157, 0.639216, 62.5, 0.082353, 0.368627, 0.619608, 65.0, 0.070588, 0.352941, 0.6, 67.5, 0.066667, 0.329412, 0.568627, 70.0, 0.07451, 0.313725, 0.541176, 72.5, 0.086275, 0.305882, 0.509804, 75.0, 0.094118, 0.286275, 0.478431, 77.5, 0.101961, 0.278431, 0.45098, 80.0, 0.109804, 0.266667, 0.411765, 82.5, 0.113725, 0.258824, 0.380392, 85.0, 0.113725, 0.25098, 0.34902, 87.5, 0.109804, 0.266667, 0.321569, 90.0, 0.105882, 0.301961, 0.262745, 92.5, 0.094118, 0.309804, 0.243137, 95.0, 0.082353, 0.321569, 0.227451, 97.5, 0.07451, 0.341176, 0.219608, 100.0, 0.070588, 0.360784, 0.211765, 102.5, 0.066667, 0.380392, 0.215686, 105.0, 0.062745, 0.4, 0.176471, 111.25, 0.07451, 0.419608, 0.145098, 117.5, 0.086275, 0.439216, 0.117647, 123.75, 0.121569, 0.470588, 0.117647, 130.0, 0.184314, 0.501961, 0.14902, 136.25, 0.254902, 0.541176, 0.188235, 142.5, 0.32549, 0.580392, 0.231373, 148.75, 0.403922, 0.619608, 0.278431, 155.0, 0.501961, 0.670588, 0.333333, 162.5, 0.592157, 0.729412, 0.4, 167.5, 0.741176, 0.788235, 0.490196, 172.5, 0.858824, 0.858824, 0.603922, 180.0, 0.921569, 0.835294, 0.580392, 192.5, 0.901961, 0.729412, 0.494118, 205.0, 0.858824, 0.584314, 0.388235, 217.5, 0.8, 0.439216, 0.321569, 230.0, 0.678431, 0.298039, 0.203922, 242.5, 0.54902, 0.168627, 0.109804, 248.75, 0.478431, 0.082353, 0.047059, 255.0, 0.45098, 0.007843, 0.0]
scalars8LUT.ColorSpace = 'RGB'
scalars8LUT.NanColor = [0.25, 0.0, 0.0]
scalars8LUT.ScalarRangeInitialized = 1.0

# trace defaults for the display properties.
generateSurfaceNormals1Display.Representation = 'Surface'
generateSurfaceNormals1Display.ColorArrayName = ['POINTS', 'Scalars8']
generateSurfaceNormals1Display.LookupTable = scalars8LUT
generateSurfaceNormals1Display.Specular = 1.0
generateSurfaceNormals1Display.SelectTCoordArray = 'None'
generateSurfaceNormals1Display.SelectNormalArray = 'Normals'
generateSurfaceNormals1Display.SelectTangentArray = 'None'
generateSurfaceNormals1Display.OSPRayScaleArray = 'Scalars8'
generateSurfaceNormals1Display.OSPRayScaleFunction = 'PiecewiseFunction'
generateSurfaceNormals1Display.SelectOrientationVectors = 'None'
generateSurfaceNormals1Display.ScaleFactor = 39.900000000000006
generateSurfaceNormals1Display.SelectScaleArray = 'Scalars8'
generateSurfaceNormals1Display.GlyphType = 'Arrow'
generateSurfaceNormals1Display.GlyphTableIndexArray = 'Scalars8'
generateSurfaceNormals1Display.GaussianRadius = 1.995
generateSurfaceNormals1Display.SetScaleArray = ['POINTS', 'Scalars8']
generateSurfaceNormals1Display.ScaleTransferFunction = 'PiecewiseFunction'
generateSurfaceNormals1Display.OpacityArray = ['POINTS', 'Scalars8']
generateSurfaceNormals1Display.OpacityTransferFunction = 'PiecewiseFunction'
generateSurfaceNormals1Display.DataAxesGrid = 'GridAxesRepresentation'
generateSurfaceNormals1Display.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
generateSurfaceNormals1Display.ScaleTransferFunction.Points = [5.0, 0.0, 0.5, 0.0, 255.0, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
generateSurfaceNormals1Display.OpacityTransferFunction.Points = [5.0, 0.0, 0.5, 0.0, 255.0, 1.0, 0.5, 0.0]

# setup the color legend parameters for each legend in this view

# get color legend/bar for scalars8LUT in view renderView1
scalars8LUTColorBar = GetScalarBar(scalars8LUT, renderView1)
scalars8LUTColorBar.Title = 'Scalars8'
scalars8LUTColorBar.ComponentTitle = ''

# set color bar visibility
scalars8LUTColorBar.Visibility = 1

# show color legend
generateSurfaceNormals1Display.SetScalarBarVisibility(renderView1, True)

# ----------------------------------------------------------------
# setup color maps and opacity mapes used in the visualization
# note: the Get..() functions create a new object, if needed
# ----------------------------------------------------------------

# get opacity transfer function/opacity map for 'Scalars8'
scalars8PWF = GetOpacityTransferFunction('Scalars8')
scalars8PWF.Points = [5.0, 0.0, 0.5, 0.0, 255.0, 1.0, 0.5, 0.0]
scalars8PWF.ScalarRangeInitialized = 1

# ----------------------------------------------------------------
# restore active source
SetActiveSource(generateSurfaceNormals1)
# ----------------------------------------------------------------

Interact()