# -*- coding: utf-8 -*-
import os
import sys
import logging
import time
import datetime
import urllib
import ntpath
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
    logging.debug("keep only class: " + str(las_class))
    
    outfile = file_name[:-4] + "_" + str(las_class) + ".las"
    cmd = "las2las --keep-classes " + str(las_class) + " -i " + file_name + " -o " + outfile
    logging.debug("cmd: " + cmd)
    os.system(cmd)
    return outfile
    
def convert_file_to_shapefile(file_name):
    logging.debug("convert las to shapefile")    
    
    outfile = file_name[:-4] + ".shp"
    cmd = "las2ogr -i " + file_name + " -o " + outfile + " -f 'ESRI Shapefile'"
    logging.debug("cmd: " + cmd)    
    os.system(cmd) 
    return outfile
    
def rasterize_shapefile(file_name, resolution, x_min, y_min, x_max, y_max):
    logging.debug("rasterize shapefile")
    
    dx = x_max - x_min
    dy = y_max - y_min
    
    px = dx / resolution
    py = dy / resolution
    logging.debug("Size of raster: " + str(px) + " " +str(py))
        
    layer_name = ntpath.basename(file_name)[:-4]
    outfile_wrong_georef = file_name[:-4] + "_wrong_georef.tif"
    
    cmd = "gdal_grid -a_srs EPSG:21781 -a nearest:radius1=" + str(1)
    cmd +=":radius2=" + str(1) + "nodata=0 -txe " + str(x_min) + " " + str(x_max) 
    cmd += " -tye " +str(y_min) + " " + str(y_max) + " -outsize " + str(px) + " " + str(py) 
    cmd += " -of GTiff -ot Float32 -l " + layer_name + " " + file_name + " " + outfile_wrong_georef 
    cmd += " --config GDAL_NUM_THREADS ALL_CPUS"
    logging.debug("cmd: " + cmd)    
    os.system(cmd)
    
    # Fix wrong metadata (switched bbox coordinates)?
    # And we can also set nodata to 0.
    outfile = file_name[:-4] + ".tif"
    cmd = "gdalwarp -s_srs EPSG:21781 -t_srs EPSG:21781 -srcnodata 0 -dstnodata 0" 
    cmd += " " + outfile_wrong_georef + " " + outfile
    logging.debug("cmd: " + cmd)    
    os.system(cmd)

    return outfile

def normalize_dsm(las_class, dsm_file_name, target_dir, dtm_vrt, resolution, x_min, y_min, x_max, y_max):
    logging.debug("normalize dsm")    
    # Ok, this one was hard to figure out the correct settings with nodata. I think one 
    # problem is that gdal_grid does not proper set nodata value?
    
    # gdal_calc.py needs rasters of the same dimension. 
    # -> Create 500x500m tif files from dtm vrt.
    dtm_file_name = dsm_file_name[:-4] + "_dtm.tif"
    cmd = "gdalwarp -s_srs EPSG:21781 -t_srs EPSG:21781 -te "  + str(x_min) + " " +  str(y_min) + " " +  str(x_max) + " " +  str(y_max)
    cmd += " -tr " + str(resolution) + " " + str(resolution) + " -wo NUM_THREADS=ALL_CPUS -co 'TILED=YES' -co 'PROFILE=GeoTIFF'"
    cmd += " -co 'INTERLEAVE=BAND' -co 'COMPRESS=DEFLATE' -srcnodata -3.40282346638529011e+38 -dstnodata 0"
    cmd += " -r bilinear " + dtm_vrt + " " + dtm_file_name
    logging.debug("cmd: " + cmd)
    os.system(cmd)
    
    outfile = dsm_file_name[:-4] + "_normalized.tif"
    cmd = "gdal_calc.py --overwrite"
    cmd += " -A " + dsm_file_name + " -B " + dtm_file_name + " --outfile " + outfile
    cmd += " --calc=\"0*((A-B)<0.1) + (A-B)*((A-B)>0.1)\""
    #cmd += " --calc=\"(A-B)\""
    cmd += " --NoDataValue=0 --co 'TILED=YES' --co 'PROFILE=GeoTIFF'"
    cmd += " --co 'INTERLEAVE=BAND' --co 'COMPRESS=DEFLATE'" 
    logging.debug("cmd: " + cmd)    
    os.system(cmd)
    
    outfile_final = os.path.join(target_dir, "class_" + str(las_class), "grid", ntpath.basename(outfile))
    cmd = "gdal_translate -a_srs EPSG:21781 -co 'TILED=YES' -co 'INTERLEAVE=BAND' -co 'COMPRESS=DEFLATE' -co 'PREDICTOR=2'"
    cmd += " " + outfile + " " + outfile_final
    logging.debug("cmd: " + cmd)        
    os.system(cmd)
    
    cmd = "gdaladdo -r average "
    cmd += "--config COMPRESS_OVERVIEW DEFLATE " 
    cmd += outfile_final + " 2 4 8 16 32 64 128"
    logging.debug("cmd: " + cmd)    
    os.system(cmd)

    return outfile

def create_relief(las_class, file_name, target_dir):
    logging.debug("create relief")
    
    outfile = os.path.join(target_dir, "class_" + str(las_class), "relief", ntpath.basename(file_name)[:-4] + "_relief.tif")
    cmd = "gdaldem hillshade -co 'TILED=YES' -co 'INTERLEAVE=BAND' -co 'COMPRESS=DEFLATE' -co 'PREDICTOR=2'" 
    cmd += " -alt 60 -az 270 -compute_edges " + file_name + " " + outfile
    logging.debug("cmd: " + cmd) 
    os.system(cmd)
    
    cmd = "gdaladdo -r average "
    cmd += "--config COMPRESS_OVERVIEW DEFLATE " 
    cmd += outfile + " 2 4 8 16 32 64 128"
    logging.debug("cmd: " + cmd)    
    os.system(cmd)

    return outfile

def process_point_cloud(las_class, file_name, paths, raster_parameters, bbox):
    x_min = bbox['x_min']
    x_max = bbox['x_max']
    y_min = bbox['y_min']
    y_max = bbox['y_max']
    
    resolution = raster_parameters['resolution']
    
    dtm_vrt = paths['dtm_vrt']
    target_dir = paths['target_dir']
    
    outfile_keep_class = keep_class_in_file(las_class, file_name)
    outfile_shp = convert_file_to_shapefile(outfile_keep_class)
    outfile_dsm = rasterize_shapefile(outfile_shp, resolution, x_min, y_min, x_max, y_max)    
    outfile_dsm_normalized = normalize_dsm(las_class, outfile_dsm, target_dir, dtm_vrt, resolution, x_min, y_min, x_max, y_max)
    outfile_dsm_relief = create_relief(las_class, outfile_dsm, target_dir)

if __name__ == '__main__':    
    # read the options and arguments from the command line / and some more settings
    options = Options()
    opts = options.parse(sys.argv[1:])    
    my_settings = Settings(opts)
    restrict_tile = my_settings.restrict_tile
    tmp_dir = my_settings.tmp_dir
    target_dir = my_settings.target_dir
    url = my_settings.url
    resolution = my_settings.resolution
    dtm_vrt = my_settings.dtm_vrt
    
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
        logging.debug("Tile: " + file_name)
        print "**********************: " + file_name
        
        if restrict_tile and file_name <> restrict_tile:
            continue
            
        logging.debug("Processing: " + file_name)
            
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
        
        bbox = {}
        bbox['x_min'] = x_min
        bbox['y_min'] = y_min
        bbox['x_max'] = x_max
        bbox['y_max'] = y_max
        
        logging.debug("x_min" + "x_min")
        logging.debug("y_min" + "y_min")
        logging.debug("x_max" + "x_max")
        logging.debug("y_max" + "y_max")
        
        paths = {}
        paths['dtm_vrt'] = dtm_vrt
        paths['target_dir'] = target_dir
        
        raster_parameters = {}
        raster_parameters['resolution'] = resolution
    
        # For lack of space we just create and delete a temporary directory (in every loop).
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
            
        # buildings
        logging.debug("buildings")
        process_point_cloud(6, outfile_las, paths, raster_parameters, bbox)
        
        # high vegetation
        logging.debug("high vegetation")
        process_point_cloud(5, outfile_las, paths, raster_parameters, bbox)

        # medium vegetation
        logging.debug("medium vegetation")        
        process_point_cloud(4, outfile_las, paths, raster_parameters, bbox)

        # low vegetation
        logging.debug("low vegetation")
        process_point_cloud(3, outfile_las, paths, raster_parameters, bbox)

    overall_duration = datetime.datetime.now() - starttime
    logging.info("Task complete. Overall duration: " + str(overall_duration))
    logging.shutdown()

