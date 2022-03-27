# DTM-2-STL
Turn Digital Terrain Models (DTMs) to STL files (TIFFs from Astropedia)

-------

Download a DEM image of choice from [Astropedia](https://astrogeology.usgs.gov/search?pmi-target=moon) (or elsewhere), for example [this DEM from Mars' moon Phobos](https://astrogeology.usgs.gov/search/map/Phobos/MarsExpress/HRSC/Phobos_ME_HRSC_DEM_Global_2ppd):

![image](https://user-images.githubusercontent.com/31905278/160262329-6fdf7eba-76d3-4c92-a629-0c32c273ffe4.png)

From the metadata/PDS label configure the following setups (coverage, conversion, data type, etc.):

```
# User Preferences
FileName = "Phobos" # name of output STL file (DO NOT include .stl extension)
poleSquare = bool(0) # boolean for whether source image is a "polar square" or normal "equi-rectangular", 1(T) or 0(F)
normalize = bool(1) # boolean to select whether or not to normalize the units to max(max()) dimension, 1(T) or 0(F)
plotShow = bool(0) # show surface plot (1/T) or not (0/F)
OutCSV = bool(0) # output pixel data to csv (1/T) or not (0/F)

# Base Body/Model Parameters
R0 = 11100 # base 'radius' of parent body (m)
LatRange = [90, -90] # range of latitudes (°) Top to Bottom
LongRange = [-180, 180] # range of longitudes (°) Left to Right
def radiusFunc(DN): # Data Number (DN) to Radius Function (change as needed)
    radius = DN + R0
    return radius
if (poleSquare):
    arc = 30 # angular width of "pole square" data (2x latitude range, °)

# Load Image of DTM (change array data type as needed)
DTM = Image.open(dirname + "\Image_Filename.tif")
DTM_Array = np.array(DTM,'int16') # make sure the data type is correct
```

The script creates a UTF-8 encoded STL from the data. Here is the STL output for the Phobos DEM:

![image](https://user-images.githubusercontent.com/31905278/160262428-a1db00b9-93df-4338-b576-3b37f14a851f.png)

The "ridges" are an artifact from the data, not the script.

Here is another example of [the Lunar south pole](https://astrogeology.usgs.gov/search/map/Moon/LRO/LOLA/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014) (1/32 resolution, 75° S):

![image](https://user-images.githubusercontent.com/31905278/160266583-502572e7-1e03-4665-800e-94d6f08c4901.png)

You can use the attached TIFF_Reduction.m MATLAB script to reduce very large TIFFs (~GBs) to more manageable sizes. This was done for the above Lunar maps.
