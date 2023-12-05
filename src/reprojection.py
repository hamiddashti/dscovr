# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 12:51:14 2022
​
@author: hliu
​
Process file which only contians file 20 or 30
"""
import h5py
import osgeo
import glob
import os
import numpy as np
import pandas as pd
from osgeo import gdal, gdal_array
import fiona
import rasterio
import rasterio.mask
import netCDF4 as nc
​import warnings
warnings.filterwarnings('ignore')

​
def read_h5(h5f, xyf, outpath, field, date, tile):    
​
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
​
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
​
def gdal_grid(root, field, date, tile):
    os.chdir(root)  
    if tile == 'tile20':
        xmin, xmax = -180,-115
    elif tile == 'tile30':
        xmin, xmax = -115,-24.9
    inputfile1 = "{0}_{1}_{2}".format(tile, field, date)
    inputfile2 = "{0}_{1}_{2}.vrt".format(tile, field, date)
    outputfile = "{0}_{1}_{2}.tif".format(field, date, tile) 
    
    scmd = 'gdal_grid -a linear:radius=0:nodata=-9999.0 -txe %f %f -tye -0.1 85 -tr 0.1 0.1 -a_srs EPSG:4326 -of GTiff -ot Float64 -l %s %s %s'\
            % (xmin, xmax, inputfile1, inputfile2, outputfile)
    os.system(scmd)
​
def gdal_warp(root, output, field, date, tile):
    os.chdir(root) 
    inputfile = "{0}_{1}_{2}.tif".format(field, date, tile) 
    outputfile = os.path.join(output, "{0}_{1}.tif".format(field, date))
    scmd = 'gdalwarp -srcnodata -9999.0 -overwrite  %s %s'% (inputfile, outputfile)
    os.system(scmd)
        
lat_d = 0      
lat_u = 85 
lon_l = -180 
lon_r = -25 
​
year = 2018
root = r"F:\MAIAC\h5\{0}".format(year)
outpath1 = r"F:\MAIAC\nc\temp9"
outpath2 = r"F:\MAIAC\nc\temp10"
if not os.path.exists(outpath1):
    os.makedirs(outpath1)
if not os.path.exists(outpath2):
    os.makedirs(outpath2)
    
xyPath  = os.path.join("F:/MAIAC/h5", "MCDLCHKM.V2010_01.REGIONALbio.10018m.BlocksOP.h5")
xyf = h5py.File(xyPath, "r") 
​
"""
test the procedure 
"""
count = 0 
​
files = os.listdir(root)
for file in files:   
    import shutil
    shutil.rmtree(outpath1)
    os.mkdir(outpath1)     
    if file.split(".")[1] == "h5":
        h5fpath  = os.path.join(root, file)   
        h5f = h5py.File(h5fpath, "r") 
        if ('tile20' in h5f.keys()) and ('tile30' in h5f.keys()):
            continue 
        elif ('tile20' in h5f.keys()) or ('tile30' in h5f.keys()):
            
            if 'tile20' in h5f.keys():
                tile = "tile20"
            elif 'tile30' in h5f.keys():
                tile = "tile30"
            date = file.split("_")[5]
            print(date)
            
            """
            Test codes 
            """
            """
            read_h5(h5f, xyf, outpath1, "BRF_780", date, tile)
            gdal_grid(outpath1, outpath2, "BRF_780", date, tile)
​
            ds = gdal.Open("{0}_{1}.tif".format("BRF_780", date))
            arr = np.array(ds.GetRasterBand(1).ReadAsArray())
  
            arr[arr < 1000] = np.nan            
            """
​
            fields = ["BRF_780", "BRF_680", "BRF_551", "Solar_zen_angle"]
            height, width = 851, 1551
            #outfile = "F:/MAIAC/nc/{0}/{1}.nc".format(year, file.split(".")[0])
            outfile = "F:/MAIAC/nc/{0}s/{1}.nc".format(year, file.split(".")[0])
​
            nc_w = nc.Dataset(outfile,'w',format = 'NETCDF4')   #创建一个格式为.nc文件 
            
            nc_w.createDimension('latitude', height)   
            nc_w.createDimension('longitude', width)
    
            nc_w.createVariable('latitude',np.float32,('latitude'))  
            nc_w.createVariable('longitude',np.float32,('longitude'))
    
            nc_w.variables['latitude'][:] = np.arange(lat_u, lat_d-0.1, -0.1)  
            nc_w.variables['longitude'][:] = np.arange(lon_l, lon_r+0.1, 0.1) 
​
            for field in fields:
                read_h5(h5f, xyf, outpath1, field, date, tile)
                gdal_grid(outpath1, field, date, tile)
                gdal_warp(outpath1, outpath2, field, date, tile)
                
                os.chdir(outpath2) 
                nc_w.createVariable(field, np.float32,('latitude', 'longitude')) 
                
                ds = gdal.Open("{0}_{1}.tif".format(field, date))
                arr = np.array(ds.GetRasterBand(1).ReadAsArray())
                #arr = gdal_array.LoadFile("{0}_{1}.tif".format(field, date))
​
                out = np.full((height, width), np.nan)
                
                if field == "Solar_zen_angle":
                    arr[arr < 0] = np.nan
                else:
                    arr[arr < 1000] = np.nan
​
                if tile == 'tile20':
                    nc_w.variables[field][:,0:650] = arr
                else:
                    nc_w.variables[field][:,650:] = arr
​
            nc_w.close() 
            ds = None