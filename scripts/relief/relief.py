#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr
from osgeo import osr
import os
import sys

ogr.UseExceptions()

TYPE = "DTM"
OUT_PATH = "/home/stefan/Geodaten/ch/zh/are/hoehen/2014/" + TYPE.lower() + "/relief/50cm/"
TMP_PATH = "/tmp/" + TYPE.lower() + "/"
VRT = "/home/stefan/Geodaten/ch/zh/are/hoehen/2014/" + TYPE.lower() + "/grid/50cm/" + TYPE.lower() + "2014.vrt"
TILEINDEX = "/home/stefan/Projekte/av_lidar_dsm_on_steroids/tileindex/" + TYPE.lower() + "2014.shp"
BUFFER = 10
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
    
    # Since we are running out of space on /tmp/, we do delete the directory
    # in every loop.
    cmd = "rm -rf " + TMP_PATH
    os.system(cmd)
    cmd = "mkdir " + TMP_PATH
    os.system(cmd)
    
    outfile_name = os.path.join(TMP_PATH, infile_name)

    cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -s_srs epsg:21781 -t_srs epsg:21781 -te "  + str(x_min - BUFFER) + " " +  str(y_min - BUFFER) + " " +  str(x_max + BUFFER) + " " +  str(y_max + BUFFER)
    cmd += " -tr 0.5 0.5 -wo NUM_THREADS=ALL_CPUS -co 'TILED=YES' -co 'PROFILE=GeoTIFF'"
    cmd += " -co 'INTERLEAVE=BAND' -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=" + str(BLOCKSIZE) + "' -co 'BLOCKYSIZE=" + str(BLOCKSIZE) + "'"
    cmd += " -r bilinear " + VRT + " " + outfile_name
    #print cmd
    os.system(cmd)

    infile = outfile_name
    outfile = os.path.join(TMP_PATH, "relief_gray_" + infile_name)
    cmd = "/usr/local/gdal/gdal-dev/bin/gdaldem hillshade -alt 60 -az 270 -compute_edges " + infile + " " + outfile
    #print cmd
    os.system(cmd)
    
    #infile = outfile
    #outfile = os.path.join(TMP_PATH, "relief_color_" + infile_name)
    #cmd = "/usr/local/gdal/gdal-dev/bin/gdaldem color-relief " + infile +  " ramp_1.txt " + outfile
    #print cmd
    #os.system(cmd)

    infile = outfile
    outfile = os.path.join(OUT_PATH, infile_name)
    cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -overwrite -s_srs epsg:21781 -t_srs epsg:21781 -te "  + str(x_min) + " " +  str(y_min) + " " +  str(x_max) + " " +  str(y_max)
    cmd += " -tr 0.5 0.5 -wo NUM_THREADS=ALL_CPUS -co 'TILED=YES' -co 'PROFILE=GeoTIFF'"
    cmd += " -co 'INTERLEAVE=BAND' -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=" + str(BLOCKSIZE) + "' -co 'BLOCKYSIZE=" + str(BLOCKSIZE) + "'"
    cmd += " -r bilinear " + infile + " " + outfile
    #print cmd
    os.system(cmd)

    cmd = "/usr/local/gdal/gdal-dev/bin/gdaladdo -r average "
    cmd += "--config COMPRESS_OVERVIEW DEFLATE --config GDAL_TIFF_OVR_BLOCKSIZE " + str(BLOCKSIZE) + " " 
    cmd += outfile + " 2 4 8 16 32 64 128"
    #print cmd
    os.system(cmd)


infiles = os.path.join(OUT_PATH, "*.tif")
outfile = os.path.join(OUT_PATH, TYPE.lower() + "2014.vrt")
cmd = "/usr/local/gdal/gdal-dev/bin/gdalbuildvrt " + outfile + " " + infiles 
os.system(cmd)

infile = os.path.join(OUT_PATH, TYPE.lower() + "2014.vrt")
outfile = os.path.join(OUT_PATH, TYPE.lower() + "2014_5m.tif")
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

