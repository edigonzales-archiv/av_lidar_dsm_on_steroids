# -*- coding: utf-8 -*-
import os
import sys
import logging
import time
import datetime
import urllib
from osgeo import ogr
from osgeo import osr

from lib import Options
from lib import Settings

ogr.UseExceptions() 

def download_file(url, outfile):
    logging.debug("url: " + url)
    logging.debug("outfile: " + outfile)
    laz = urllib.URLopener()
    laz.retrieve(url, outfile)    

def keep_class_in_file(las_class, file_name):
    outfile = file_name[:-4] + "_" + str(las_class) + ".las"
    cmd = "las2las --keep-classes " + str(las_class) + " -i " + file_name + " -o " + outfile
    logging.debug("cmd: " + cmd)
    os.system(cmd)
    return outfile
    
def convert_file_to_shapefile(file_name):
    print file_name
    outfile = file_name[:-4] + ".shp"
    cmd = "las2ogr -i " + file_name + " -o " + outfile + " -f 'ESRI Shapefile'"
    os.system(cmd) 
    return outfile
    
def rasterize_shapefile(file_name, resolution, x_min, y_min, x_max, y_max):
    
    # px, py können hier berechnet werden.
    
    cmd = "gdal_grid -a_srs epsg:21781 -a nearest:radius1="+str(resolution)
    cmd +=":radius2="+str(resolution)+":nodata=-9999 -txe " + str(minX) + " " + str(maxX+1) + " -tye " +str(minY) + " " + str(maxY) + " -outsize " + str(px) + " " + str(py) + " -of GTiff -ot Float32 -l dtm_xyz " + DTM_DIR + "dtm_xyz.vrt " + DTM_DIR + dtm_base_name + "_tmp_wrong_nodata.tif"
    print cmd
    #os.system(cmd)


if __name__ == '__main__':    
    # read the options and arguments from the command line / and some more settings
    options = Options()
    opts = options.parse(sys.argv[1:])    
    my_settings = Settings(opts)
    restrict_tile = my_settings.restrict_tile
    tmp_dir = my_settings.tmp_dir
    url = my_settings.url
    resolution = my_settings.resolution
    
    # configure logging
    FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename = my_settings.get_logfile_path(), filemode = "w", format = FORMAT, level = logging.DEBUG)

    # log some general information
    logging.info("Settings: " + str(my_settings.__dict__))
    starttime = datetime.datetime.now()    
    logging.info("Start time is " + str(starttime))
    
    shp = ogr.Open(my_settings.tileindex)
    layer = shp.GetLayer(0)

    # 6885_2835.laz
    # 6950_2450.laz

    for feature in layer:
        file_name = feature.GetField('dateiname')
        logging.info("Processing: " + file_name)
        print "**********************: " + file_name
        
        if restrict_tile and file_name <> restrict_tile:
            continue
            
#        if restrict_tile and file_name == restrict_tile:
 #           print "found"
  #          tile_found = True

        geom = feature.GetGeometryRef()
        env = geom.GetEnvelope()

        # int() is flooring a value (?). So we need to add some very small value.
        x_min = int(env[0] + 0.001)
        y_min = int(env[2] + 0.001)
        x_max = int(env[1] + 0.001)
        y_max = int(env[3] + 0.001)
    
        print x_min 
        print y_min
        
        # For lack of space we just create and delete a temporary directory.
        # in every loop.
        cmd = "rm -rf " + tmp_dir
        os.system(cmd)
        cmd = "mkdir " + tmp_dir
        os.system(cmd)
        
        try:
            outfile_las = os.path.join(tmp_dir, file_name)     
            download_file(url + file_name, outfile_las)
        except IOError, e:
            logging.error(e)
            print e
            continue
        
        outfile_keep_class = keep_class_in_file(6, outfile_las)
        outfile_shp = convert_file_to_shapefile(outfile_keep_class)
        outfile_tif = rasterize_shapefile(file_name, resolution, x_min, y_min, x_max, y_max)
        
    overall_duration = datetime.datetime.now() - starttime
    logging.info("Task complete. Overall duration: " + str(overall_duration))
    logging.shutdown()

