# By: Brendan Luke
# Date: October 15, 2021
# Purpose: turn digital terrain models (DTMs) into 3D STL files (no facet normal)
from datetime import datetime
startTime = datetime.now()

# import modules
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import PIL.Image as Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import os

# relative filepaths sometimtes don't work
dirname = os.path.dirname(__file__)

# Base Body Constants
R0 = 11100 # base 'radius' of parent body (m)
LatRange = [-90, 90] # range of latitudes (°)
LongRange = [-180, 180] # range of longitudes (°)
FileName = "Phobos" # name of output STL file (DO NOT include .stl extension)

# Load Image of DTM (change array data type as needed)
DTM = Image.open("C:/Users/ext-brl01021/Downloads/Phobos_ME_HRSC_DEM_Global_2ppd.tif")
DTM_Array = np.array(DTM,'int16')
DTM_Array = np.flip(DTM_Array,0) # flip array to fix orientation
dims = DTM_Array.shape
print("Image is " + str(dims) + " px")

# Data Number (DN) to Radius Function (change as needed)
def radiusFunc(DN):
    radius = DN + R0
    return radius

# Create collection (tuple) of cartesian points (vertices of STL)
lat = np.linspace(LatRange[0], LatRange[1],dims[0]-1)
long = np.linspace(LongRange[0], LongRange[1],dims[1]-1)
xLin, yLin, zLin = [], [], [] # declare linear x,y,z (for plotting)
x, y, z = np.zeros((len(lat),len(long))), np.zeros((len(lat),len(long))), np.zeros((len(lat),len(long))) # declare x,y,z
rowRemove, colRemove = 3, 1 # remove rows/columns of zeros data as needed
startEndBool = bool(1) # remove from start(T,1) or end(F,0) of data
for i in range(len(lat)-1-rowRemove):
    for j in range(len(long)-1-colRemove):
        if startEndBool: # remove from start
            R = radiusFunc(float(DTM_Array[i+rowRemove,j+colRemove]))
            xLin.append(R*math.cos(math.radians(lat[i]))*math.cos(math.radians(long[j])))
            yLin.append(R*math.cos(math.radians(lat[i]))*math.sin(math.radians(long[j])))
            zLin.append(R*math.sin(math.radians(lat[i])))

            x[i,j] = R*math.cos(math.radians(lat[i]))*math.cos(math.radians(long[j]))
            y[i,j] = R*math.cos(math.radians(lat[i]))*math.sin(math.radians(long[j]))
            z[i,j] = R*math.sin(math.radians(lat[i]))
        else: # remove from end
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
stringOut = "solid " + FileName # initialize empty string to write STL file to
for i in range(len(lat)-2-rowRemove):
    for j in range(len(long)-2-colRemove):
        # first triangle in 1x1 px square (top left)
        stringOut += ("\nfacet normal 0.0e+01 0.0e+01 0.0e+01\n" + "outer loop\n"
                    +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,j], vy = y[i,j], vz = z[i,j]) # top left point
                    +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,j], vy = y[i+1,j], vz = z[i+1,j]) # bottom left point
                    +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,j+1], vy = y[i,j+1], vz = z[i,j+1]) # top right point
                    +"endloop\n" + "endfacet")
        # second triangle in 1x1 px square (bottom right)
        stringOut += ("\nfacet normal 0.0e+01 0.0e+01 0.0e+01\n" + "outer loop\n"
                    +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,j+1], vy = y[i+1,j+1], vz = z[i+1,j+1]) # bottom right point
                    +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,j+1], vy = y[i,j+1], vz = z[i,j+1]) # top right point
                    +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,j], vy = y[i+1,j], vz = z[i+1,j]) # bottom left point
                    +"endloop\n" + "endfacet")
    print("Rows {:.1f}".format(100*i/(len(lat)-3-rowRemove))+"% complete")
for i in range(len(lat)-2-rowRemove): # write end:start facets
    # first triangle in 1x1 px square (top left)
    stringOut += ("\nfacet normal 0.0e+01 0.0e+01 0.0e+01\n" + "outer loop\n"
                +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,len(long)-3-colRemove], vy = y[i,len(long)-3-colRemove], vz = z[i,len(long)-3-colRemove]) # top left point
                +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,len(long)-3-colRemove], vy = y[i+1,len(long)-3-colRemove], vz = z[i+1,len(long)-3-colRemove]) # bottom left point
                +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,0], vy = y[i,0], vz = z[i,0]) # top right point
                +"endloop\n" + "endfacet")
    # second triangle in 1x1 px square (bottom right)
    stringOut += ("\nfacet normal 0.0e+01 0.0e+01 0.0e+01\n" + "outer loop\n"
                +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,0], vy = y[i+1,0], vz = z[i+1,0]) # bottom right point
                +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i,0], vy = y[i,0], vz = z[i,0]) # top right point
                +"vertex {vx:e} {vy:e} {vz:e}\n".format(vx = x[i+1,len(long)-3-colRemove], vy = y[i+1,len(long)-3-colRemove], vz = z[i+1,len(long)-3-colRemove]) # bottom left point
                +"endloop\n" + "endfacet")
stringOut += "\nendsolid " + FileName # close out STL data
with open(dirname + "/" + FileName + ".stl", "w") as outFile:
    outFile.write(stringOut)

# Stop Clock & Show Plots(s)
print('Done! Execution took ' + str(datetime.now() - startTime))
plt.show()