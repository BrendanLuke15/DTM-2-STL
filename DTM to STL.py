# By: Brendan Luke
# Date: March 26, 2022
# Purpose: turn digital terrain models (DTMs) into 3D STL files (no facet normal)
from datetime import datetime
startTime = datetime.now()

# import modules
import math
import numpy as np
import matplotlib.pyplot as plt
import PIL.Image as Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import os

# for relative filepaths
dirname = os.path.dirname(__file__)

# User Preferences
FileName = "Lunar South Pole" # name of output STL file (DO NOT include .stl extension)
poleSquare = bool(1) # boolean for whether source image is a "polar square" or normal "equi-rectangular", 1(T) or 0(F)
normalize = bool(1) # boolean to select whether or not to normalize the units to max(max()) dimension, 1(T) or 0(F)
plotShow = bool(0) # show surface plot (1/T) or not (0/F)
OutCSV = bool(0) # output pixel data to csv (1/T) or not (0/F)

# Base Body/Model Parameters
R0 = 1737400 # base 'radius' of parent body (m)
LatRange = [-75, -90] # range of latitudes (°) Top to Bottom
LongRange = [-180, 180] # range of longitudes (°) Left to Right
def radiusFunc(DN): # Data Number (DN) to Radius Function (change as needed)
    radius = 0.5*DN + R0
    return radius
if (poleSquare):
    arc = 30 # angular width of "pole square" data (2x latitude range, °)

# Load Image of DTM (change array data type as needed)
#DTM = Image.open(dirname + "/Image_Filename.tif")
DTM = Image.open(dirname + "\myfile.tif")
DTM_Array = np.array(DTM,'int16')
#dims = DTM_Array.shape
#DTM_Array = DTM_Array[:,0:math.floor(dims[1]/2)] # putting to numpy array doubles the image horizontally (why??)

# make necessary modifications to data below
    # description of modifications:
    # poor data; some of last rows are zeros, creating undesirable artifacts in STL file
    # changes to be same data from nearest valid row
#DTM_Array[dims[0]-1,:] = DTM_Array[dims[0]-3,:] 
#DTM_Array[dims[0]-2,:] = DTM_Array[dims[0]-3,:] 
#DTM_Array[dims[0]-5,:] = DTM_Array[dims[0]-4,:] 

if OutCSV:
    np.savetxt("ImgArray.csv", DTM_Array, delimiter=",")
dims = DTM_Array.shape
print("Image is " + str(dims) + " px")
maxDim = np.abs(DTM_Array).max()

# Create collection (tuple) of cartesian points (vertices of STL)
xLin, yLin, zLin = [], [], [] # declare linear x,y,z (for plotting)
if (poleSquare):
    horizontalScale = R0*arc/180*math.pi # horizontal scale of view (m)
    X, Y = np.linspace(-horizontalScale/2,horizontalScale/2,dims[0]), np.linspace(-horizontalScale/2,horizontalScale/2,dims[0])
    arcSpan = np.linspace(-arc/2,arc/2,dims[0])
    x, y, z = np.zeros((dims[0],dims[0])), np.zeros((dims[0],dims[0])), np.zeros((dims[0],dims[0])) # declare x,y,z
    for i in range(dims[0]):
        for j in range(dims[0]):
            R = radiusFunc(float(DTM_Array[i,j]))
            phi = math.atan2(Y[j],X[i]) # pseudo longitude (rad)
            d = math.sqrt(X[i]**2 + Y[j]**2) # inplane distance to point (m)
            theta = math.atan(d/R0) # pseudo latitude (rad)

            xLin.append(X[i])
            yLin.append(Y[j])
            zLin.append(math.cos(theta)*R)

            x[i,j] = X[i]
            y[i,j] = Y[j]
            z[i,j] = math.cos(theta)*R
else:
    lat = np.linspace(LatRange[0], LatRange[1],dims[0]-1)
    long = np.linspace(LongRange[0], LongRange[1],dims[1]-1)
    x, y, z = np.zeros((len(lat),len(long))), np.zeros((len(lat),len(long))), np.zeros((len(lat),len(long))) # declare x,y,z
    for i in range(len(lat)-1):
        for j in range(len(long)-1):
            R = radiusFunc(float(DTM_Array[i,j]))
            xLin.append(R*math.cos(math.radians(lat[i]))*math.cos(math.radians(long[j])))
            yLin.append(R*math.cos(math.radians(lat[i]))*math.sin(math.radians(long[j])))
            zLin.append(R*math.sin(math.radians(lat[i])))

            x[i,j] = R*math.cos(math.radians(lat[i]))*math.cos(math.radians(long[j]))
            y[i,j] = R*math.cos(math.radians(lat[i]))*math.sin(math.radians(long[j]))
            z[i,j] = R*math.sin(math.radians(lat[i]))

# Create Surface Plot
fig = plt.figure()
ax = plt.axes(projection='3d')
surf = ax.plot_trisurf(xLin, yLin, zLin)
plt.axis('off')

# Write ASCII STL File (no facet normal)
stringOut = ["solid " + FileName] # initialize empty string to write STL file to
if (poleSquare):
    if normalize: # normalize dimensions
        normFactor = R0+maxDim # normalization factor
        for i in range(dims[0]-1):
            for j in range(dims[0]-1):
                # first triangle in 1x1 px square (top left)
                stringOut.append("\nfacet normal 0.0e+01 0.0e+01 0.0e+01\n" + "outer loop\n"
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,j]/(normFactor), vy = y[i,j]/(normFactor), vz = z[i,j]/(normFactor)) # top left point
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,j]/(normFactor), vy = y[i+1,j]/(normFactor), vz = z[i+1,j]/(normFactor)) # bottom left point
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,j+1]/(normFactor), vy = y[i,j+1]/(normFactor), vz = z[i,j+1]/(normFactor)) # top right point
                            +"endloop\n" + "endfacet")
                # second triangle in 1x1 px square (bottom right)
                stringOut.append("\nfacet normal 0.0e+01 0.0e+01 0.0e+01\n" + "outer loop\n"
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,j+1]/(normFactor), vy = y[i+1,j+1]/(normFactor), vz = z[i+1,j+1]/(normFactor)) # bottom right point
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,j+1]/(normFactor), vy = y[i,j+1]/(normFactor), vz = z[i,j+1]/(normFactor)) # top right point
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,j]/(normFactor), vy = y[i+1,j]/(normFactor), vz = z[i+1,j]/(normFactor)) # bottom left point
                            +"endloop\n" + "endfacet")
            print("Rows {:.1f}".format(100*i/(dims[0]-2))+"% complete")
    else: # do not normalize dimensions
        for i in range(dims[0]-1):
            for j in range(dims[0]-1):
                # first triangle in 1x1 px square (top left)
                stringOut.append("\nfacet normal 0.0e+01 0.0e+01 0.0e+01\n" + "outer loop\n"
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,j], vy = y[i,j], vz = z[i,j]) # top left point
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,j], vy = y[i+1,j], vz = z[i+1,j]) # bottom left point
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,j+1], vy = y[i,j+1], vz = z[i,j+1]) # top right point
                            +"endloop\n" + "endfacet")
                # second triangle in 1x1 px square (bottom right)
                stringOut.append("\nfacet normal 0.0e+01 0.0e+01 0.0e+01\n" + "outer loop\n"
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,j+1], vy = y[i+1,j+1], vz = z[i+1,j+1]) # bottom right point
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,j+1], vy = y[i,j+1], vz = z[i,j+1]) # top right point
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,j], vy = y[i+1,j], vz = z[i+1,j]) # bottom left point
                            +"endloop\n" + "endfacet")
            print("Rows {:.1f}".format(100*i/(dims[0]-2))+"% complete")
else:
    if normalize: # normalize dimensions
        normFactor = R0+maxDim # normalization factor
        for i in range(len(lat)-2):
            for j in range(len(long)-2):
                # first triangle in 1x1 px square (top left)
                stringOut.append("\nfacet normal 0.0e+01 0.0e+01 0.0e+01\n" + "outer loop\n"
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,j]/(normFactor), vy = y[i,j]/(normFactor), vz = z[i,j]/(normFactor)) # top left point
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,j]/(normFactor), vy = y[i+1,j]/(normFactor), vz = z[i+1,j]/(normFactor)) # bottom left point
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,j+1]/(normFactor), vy = y[i,j+1]/(normFactor), vz = z[i,j+1]/(normFactor)) # top right point
                            +"endloop\n" + "endfacet")
                # second triangle in 1x1 px square (bottom right)
                stringOut.append("\nfacet normal 0.0e+01 0.0e+01 0.0e+01\n" + "outer loop\n"
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,j+1]/(normFactor), vy = y[i+1,j+1]/(normFactor), vz = z[i+1,j+1]/(normFactor)) # bottom right point
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,j+1]/(normFactor), vy = y[i,j+1]/(normFactor), vz = z[i,j+1]/(normFactor)) # top right point
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,j]/(normFactor), vy = y[i+1,j]/(normFactor), vz = z[i+1,j]/(normFactor)) # bottom left point
                            +"endloop\n" + "endfacet")
            print("Rows {:.1f}".format(100*i/(len(lat)-3))+"% complete")
        for i in range(len(lat)-2): # write end:start facets
            # first triangle in 1x1 px square (top left)
            stringOut.append("\nfacet normal 0.0e+01 0.0e+01 0.0e+01\n" + "outer loop\n"
                        +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,len(long)-3]/(normFactor), vy = y[i,len(long)-3]/(normFactor), vz = z[i,len(long)-3]/(normFactor)) # top left point
                        +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,len(long)-3]/(normFactor), vy = y[i+1,len(long)-3]/(normFactor), vz = z[i+1,len(long)-3]/(normFactor)) # bottom left point
                        +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,0]/(normFactor), vy = y[i,0]/(normFactor), vz = z[i,0]/(normFactor)) # top right point
                        +"endloop\n" + "endfacet")
            # second triangle in 1x1 px square (bottom right)
            stringOut.append("\nfacet normal 0.0e+01 0.0e+01 0.0e+01\n" + "outer loop\n"
                        +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,0]/(normFactor), vy = y[i+1,0]/(normFactor), vz = z[i+1,0]/(normFactor)) # bottom right point
                        +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,0]/(normFactor), vy = y[i,0]/(normFactor), vz = z[i,0]/(normFactor)) # top right point
                        +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,len(long)-3]/(normFactor), vy = y[i+1,len(long)-3]/(normFactor), vz = z[i+1,len(long)-3]/(normFactor)) # bottom left point
                        +"endloop\n" + "endfacet")
    else: # do not normalize dimensions
        for i in range(len(lat)-2):
            for j in range(len(long)-2):
                # first triangle in 1x1 px square (top left)
                stringOut.append("\nfacet normal 0.0e+01 0.0e+01 0.0e+01\n" + "outer loop\n"
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,j], vy = y[i,j], vz = z[i,j]) # top left point
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,j], vy = y[i+1,j], vz = z[i+1,j]) # bottom left point
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,j+1], vy = y[i,j+1], vz = z[i,j+1]) # top right point
                            +"endloop\n" + "endfacet")
                # second triangle in 1x1 px square (bottom right)
                stringOut.append("\nfacet normal 0.0e+01 0.0e+01 0.0e+01\n" + "outer loop\n"
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,j+1], vy = y[i+1,j+1], vz = z[i+1,j+1]) # bottom right point
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,j+1], vy = y[i,j+1], vz = z[i,j+1]) # top right point
                            +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,j], vy = y[i+1,j], vz = z[i+1,j]) # bottom left point
                            +"endloop\n" + "endfacet")
            print("Rows {:.1f}".format(100*i/(len(lat)-3))+"% complete")
        for i in range(len(lat)-2): # write end:start facets
            # first triangle in 1x1 px square (top left)
            stringOut.append("\nfacet normal 0.0e+01 0.0e+01 0.0e+01\n" + "outer loop\n"
                        +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,len(long)-3], vy = y[i,len(long)-3], vz = z[i,len(long)-3]) # top left point
                        +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,len(long)-3], vy = y[i+1,len(long)-3], vz = z[i+1,len(long)-3]) # bottom left point
                        +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,0], vy = y[i,0], vz = z[i,0]) # top right point
                        +"endloop\n" + "endfacet")
            # second triangle in 1x1 px square (bottom right)
            stringOut.append("\nfacet normal 0.0e+01 0.0e+01 0.0e+01\n" + "outer loop\n"
                        +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,0], vy = y[i+1,0], vz = z[i+1,0]) # bottom right point
                        +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,0], vy = y[i,0], vz = z[i,0]) # top right point
                        +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,len(long)-3], vy = y[i+1,len(long)-3], vz = z[i+1,len(long)-3]) # bottom left point
                        +"endloop\n" + "endfacet")
stringOut.append("\nendsolid " + FileName) # close out STL data
stringOut = ''.join(stringOut) # join list to string
with open(dirname + "/" + FileName + ".stl", "w") as outFile:
    outFile.write(stringOut)

# Stop Clock & Show Plots(s)
print('Done! Execution took ' + str(datetime.now() - startTime))
if plotShow:
    plt.show()
