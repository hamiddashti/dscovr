import os
import numpy as np
import pandas as pd
from osgeo import gdal, osr
import h5py
import matplotlib.pylab as plt


# Open the hdf file
root = "/home/hamid/dscovr/"
file = "data/DSCOVR_EPIC_L2_VESDR_02_20160401025239_03.h5"
h5fpath  = os.path.join(root, file)   
h5f = h5py.File(h5fpath, "r") 
date = file.split("_")[5]

# Get the exisitng tile list in the file
tile_list = [key for key in h5f.keys()]

# Open on one tile
tile = tile_list[0]

# extract NDVI
ndvi_field = '05_NDVI'
qa_field = '06_QA_VESDR'
Scale_factor_VESDR = 0.001














xyPath  = root+ "MCDLCHKM.V2010_01.REGIONALbio.10018m.BlocksOP.h5"
xyf = h5py.File(xyPath, "r") 


outpath = r"/home/hamid/dscovr/"

field = '19_MAIAC_CloudLWmask'
tile = "tile20"


# Get geolocations from land cover map and create a vrt map
xyf_x = np.array(xyf[tile]['Geolocation']['Longitude']).reshape(-1,1)
xyf_y = np.array(xyf[tile]['Geolocation']['Latitude']).reshape(-1,1)
h5f_t = np.array(h5f[tile][field]).reshape(-1,1)

out = np.hstack((xyf_x, xyf_y, h5f_t))
out = out.astype(float)
df = pd.DataFrame(out, columns = ['Lon','Lat','data'])

df = df[df['Lon'] > -999.0]
df = df[df['Lat'] > -999.0]
df.data[df.data <= -9998] = -9999.0

df.to_csv(os.path.join(outpath, "{0}_{1}_{2}.csv".format(tile, field, date)),sep=",",index=False)
msg = '''<OGRVRTDataSource>
    <OGRVRTLayer name="{0}_{1}_{2}">
        <SrcDataSource>{3}_{4}_{5}.csv</SrcDataSource>
        <GeometryType>wkbPoint</GeometryType>
        <GeometryField encoding="PointFromColumns" x="Lon" y="Lat" z="data"/>
    </OGRVRTLayer>
</OGRVRTDataSource>'''.format(tile, field, date, tile, field, date)
        
msgpath = os.path.join(outpath, "{0}_{1}_{2}.vrt".format(tile, field, date))
file = open(msgpath, 'w')
file.write(msg)   
file.close()  

if (tile=='tile00'):
    xmin, xmax = -25,65
    ymin,ymax = 0,90
if (tile=='tile01'):
    xmin, xmax = -25,65
    ymin,ymax = -90,0

if (tile=='tile10'):
    xmin, xmax = 65,155
    ymin,ymax = 0,90

if (tile=='tile11'):
    xmin, xmax = 65,155
    ymin,ymax = -90,0

if (tile=='tile20'):
    xmin, xmax = -115,155
    ymin,ymax = 0,90

if (tile=='tile21'):
    xmin, xmax = -115,155
    ymin,ymax = -90,0

if (tile=='tile30'):
    xmin, xmax = -115,-25
    ymin,ymax = 0,90

if tile == 'tile31':
    xmin, xmax = -115,-25
    ymin,ymax = -90,0

inputfile1 = "{0}_{1}_{2}".format(tile, field, date)
inputfile2 = "{0}_{1}_{2}.vrt".format(tile, field, date)
outputfile = "{0}_{1}_{2}_{3}.tif".format(field, date, tile,"155_180") 
outputfile = outputfile
# scmd = 'gdal_grid -a linear:radius=0:nodata=-9999.0 -txe %f %f -tye %f %f -tr 0.1 0.1 -a_srs EPSG:4326 -of GTiff -ot Float64 -l %s %s %s'\
#         % (xmin, xmax,ymin,ymax, inputfile1, inputfile2, outputfile)
xmin, xmax = 155,180   # Swap the values
scmd = 'gdal_grid -a linear:radius=0:nodata=-9999.0 -txe %f %f -tye %f %f -tr 0.1 0.1 -a_srs EPSG:4326 -of GTiff -ot Float64 -l %s %s %s' \
       % (xmin, xmax, ymin, ymax, inputfile1, inputfile2, outputfile)
os.system(scmd)
