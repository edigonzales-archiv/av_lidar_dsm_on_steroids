#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr
from osgeo import osr
import os
import sys
import urllib

ogr.UseExceptions()

URL = "http://maps.zh.ch/download/hoehen/2014/lidar/"
TMP_PATH = "/tmp/las"

BASE_PATH = "/home/stefan/Geodaten/ch/zh/are/hoehen/2014/"
OUT_PATH = "/home/stefan/Geodaten/ch/zh/are/hoehen/2014/ndsm/grid/50cm/"
TILEINDEX = "/home/stefan/Projekte/av_lidar_dsm_on_steroids/tileindex/lidar2014.shp"
BLOCKSIZE = 256

shp = ogr.Open(TILEINDEX)
layer = shp.GetLayer(0)

for feature in layer:
    file_name = feature.GetField('dateiname')
    print "**********************: " + file_name

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

    outfile = os.path.join(TMP_PATH, file_name)
    laz = urllib.URLopener()
    laz.retrieve(URL + file_name, outfile)    
    
    # We need to use laszip.exe because the liblas utilites do not support laz (10.03 binaries).
    infile = outfile
    outfile = os.path.join(TMP_PATH, file_name[:-3] + "las")
    cmd = "laszip.exe -i " + infile + " -o " + outfile
    os.system(cmd)
    
    #TODO: Catch IOError/Timeout "IOError: [Errno socket error] [Errno 110] Connection timed out"
    
    infile_las = outfile
    outfile = os.path.join(TMP_PATH, file_name[:-4] + "_buildings.las")
    cmd = "las2las --keep-classes 6 -i " + infile_las + " -o " + outfile
    os.system(cmd)
    
    infile = outfile
    outfile = os.path.join(TMP_PATH, file_name[:-4] + "_buildings.shp")
    cmd = "las2ogr -i " + infile + " -o " + outfile + " -f 'ESRI Shapefile'"
    os.system(cmd)
    
    
    outfile = os.path.join(TMP_PATH, file_name[:-4] + "_vegetation_low.las")
    cmd = "las2las --keep-classes 3 -i " + infile_las + " -o " + outfile
    os.system(cmd)
    
    outfile = os.path.join(TMP_PATH, file_name[:-4] + "_vegetation_medium.las")
    cmd = "las2las --keep-classes 4 -i " + infile_las + " -o " + outfile
    os.system(cmd)

    outfile = os.path.join(TMP_PATH, file_name[:-4] + "_vegetation_high.las")
    cmd = "las2las --keep-classes 5 -i " + infile_las + " -o " + outfile
    os.system(cmd)

    break
    

