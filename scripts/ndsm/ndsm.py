#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr
from osgeo import osr
import os
import sys

ogr.UseExceptions()

BASE_PATH = "/home/stefan/Geodaten/ch/zh/are/hoehen/2014/"
OUT_PATH = "/home/stefan/Geodaten/ch/zh/are/hoehen/2014/ndsm/grid/50cm/"
TILEINDEX = "/home/stefan/Geodaten/ch/zh/are/hoehen/2014/dom/grid/50cm/dom2014.shp"
BLOCKSIZE = 256

shp = ogr.Open(TILEINDEX)
layer = shp.GetLayer(0)

for feature in layer:
    infile_name = feature.GetField('location')
    print "**********************: " + infile_name

    geom = feature.GetGeometryRef()
    env = geom.GetEnvelope()

    x_min = int(env[0] + 0.001)
    y_min = int(env[2] + 0.001)
    x_max = int(env[1] + 0.001)
    y_max = int(env[3] + 0.001)
    
    print x_min 
    print y_min
    
    infile_a = os.path.join(BASE_PATH, "dom/grid/50cm/", infile_name)
    infile_b = os.path.join(BASE_PATH, "dtm/grid/50cm/", infile_name)
    outfile = os.path.join(OUT_PATH, infile_name)
    
    # We try to smooth the noise by setting everything to zero where the
    # difference is less the 10cm.
    cmd = "/usr/local/gdal/gdal-dev/bin/gdal_calc.py --overwrite "
    cmd += " -A " + infile_a + " -B " + infile_b + " --outfile " + outfile
    cmd += " --calc=\"0*((A-B)<0.1) + (A-B)*((A-B)>0.1)\""
    cmd += " --NoDataValue=-3.40282e+38 --co 'TILED=YES' --co 'PROFILE=GeoTIFF'"
    cmd += " --co 'INTERLEAVE=BAND' --co 'COMPRESS=DEFLATE'" 
    cmd += " --co 'BLOCKXSIZE=" + str(BLOCKSIZE) + "' --co 'BLOCKYSIZE=" + str(BLOCKSIZE) + "'"
    #print cmd
    os.system(cmd)

    cmd = "/usr/local/gdal/gdal-dev/bin/gdaladdo -r average "
    cmd += "--config COMPRESS_OVERVIEW DEFLATE --config GDAL_TIFF_OVR_BLOCKSIZE " + str(BLOCKSIZE) + " " 
    cmd += outfile + " 2 4 8 16 32 64 128"
    #print cmd
    os.system(cmd)

infiles = os.path.join(OUT_PATH, "*.tif")
outfile = os.path.join(OUT_PATH, "ndsm2014.vrt")
cmd = "/usr/local/gdal/gdal-dev/bin/gdalbuildvrt " + outfile + " " + infiles 
os.system(cmd)

infile = os.path.join(OUT_PATH, "ndsm2014.vrt")
outfile = os.path.join(OUT_PATH, "ndsm2014_5m.tif")
cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -tr 5.0 5.0 -of GTiff"
cmd += " -co 'TILED=YES' -co 'PROFILE=GeoTIFF'  -co 'INTERLEAVE=BAND'"
cmd += " -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=" + str(BLOCKSIZE) + "' -co 'BLOCKYSIZE="+ str(BLOCKSIZE) + "'" 
cmd += " -wo NUM_THREADS=ALL_CPUS -s_srs epsg:21781 -t_srs epsg:21781"
cmd += " " + infile + " " + outfile
os.system(cmd)

cmd  = "/usr/local/gdal/gdal-dev/bin/gdaladdo -r average"
cmd += " --config COMPRESS_OVERVIEW DEFLATE --config GDAL_TIFF_OVR_BLOCKSIZE " + str(BLOCKSIZE) + " " 
cmd += " " + outfile + " 2 4 8 16 32 64 128"
os.system(cmd)
