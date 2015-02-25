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

def keep_las_classes(las_class):
    pass

def las2shp(las_file):
    pass
    
def rasterize_shp(shp_file):
    pass


if __name__ == '__main__':    
    # read the options and arguments from the command line / and some more settings
    options = Options()
    opts = options.parse(sys.argv[1:])    
    my_settings = Settings(opts)
    restrict_tile = my_settings.restrict_tile
    tmp_dir = my_settings.tmp_dir
    url = my_settings.url
    
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
        print "**********************: " + file_name
        
        if restrict_tile and file_name <> restrict_tile:
            continue
            
#        if restrict_tile and file_name == restrict_tile:
 #           print "found"
  #          tile_found = True

        geom = feature.GetGeometryRef()
        env = geom.GetEnvelope()

        # int() is flooring a value. So we need to add some very small value.
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
        
        outfile = os.path.join(tmp_dir, file_name)
        laz = urllib.URLopener()
        laz.retrieve(url + file_name, outfile)    
        
        #TODO: Catch IOError/Timeout "IOError: [Errno socket error] [Errno 110] Connection timed out" (try/catch/continue)
        
    overall_duration = datetime.datetime.now() - starttime
    logging.info("Task complete. Overall duration: " + str(overall_duration))
    logging.shutdown()

