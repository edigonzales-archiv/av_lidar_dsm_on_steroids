# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import os
import sys
import logging
import time
import datetime
import urllib
import ntpath

from lib import Options
from lib import Settings

if __name__ == '__main__':    
    # read the options and arguments from the command line / and some more settings
    options = Options()
    opts = options.parse(sys.argv[1:])    
    my_settings = Settings(opts)
    restrict_tile = my_settings.restrict_tile
    tmp_dir = my_settings.tmp_dir
    target_dir = my_settings.target_dir
    resolution = my_settings.resolution
    tileindex = my_settings.tileindex
    qgis_project = my_settings.qgis_project
    
    # configure logging
    FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename = my_settings.get_logfile_path(), filemode = "w", format = FORMAT, level = logging.DEBUG)

    # log some general information
    logging.info("Settings: " + str(my_settings.__dict__))
    starttime = datetime.datetime.now()    
    logging.info("Start time is " + str(starttime))
    
    # current directory
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
   # initialize QGIS
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath("/home/stefan/Apps/qgis_master", True)
    QgsApplication.initQgis() 
    
    # QGIS-Projekt laden
    QgsProject.instance().setFileName(qgis_project)
    if not QgsProject.instance().read():
        logging.error("QGIS project not found.")
        sys.exit("QGIS project not found.")
    
    # list with all layers in the QGIS project
    lst = []
    layerTreeRoot = QgsProject.instance().layerTreeRoot()
    for id in layerTreeRoot.findLayerIds():
        node = layerTreeRoot.findLayer(id)
        lst.append(id)
        
    logging.debug("Layers in QGIS project: " + str(lst))
    print lst

    # load tileindex file
    layer_name = ntpath.basename(tileindex)[:-4]
    print layer_name

    vlayer = QgsVectorLayer(tileindex + "|layername=" + layer_name, "Blatteinteilung", "ogr")
    if not vlayer.isValid():
        logging.error("Could not load tileindex.")        
        sys.exit("Could not load tileindex.")
    
    # Rasterkarten erstellen
    iter = vlayer.getFeatures()
    for feature in iter:
        idx = vlayer.fieldNameIndex('location')
        number = feature.attributes()[idx].toString()

        if restrict_tile and number <> restrict_tile:
            continue
            
        logging.info("Processing: " + number)
        print number
                        
#        dpi = 508
#        scale = 10000

        geom = feature.geometry()
        p1 = geom.vertexAt(0)
        p2 = geom.vertexAt(2)

        rect = QgsRectangle(p1, p2)

        dx = rect.width()
        dy = rect.height()

#        width = (dx/scale) / 0.0254 * dpi
#        height = (dy/scale) / 0.0254 * dpi
        
        width = dx / resolution
        height = dy  / resolution
        
        print dx
        print dy
        print width
        print height
        
        
        
        mapSettings = QgsMapSettings()
        mapSettings.setMapUnits(0)
        mapSettings.setExtent(rect)
#        mapSettings.setOutputDpi(dpi)
        mapSettings.setOutputSize(QSize(width, height))
        mapSettings.setLayers(lst)
        mapSettings.setFlags(QgsMapSettings.DrawLabeling)

        img = QImage(QSize(width, height), QImage.Format_ARGB32)
#        img.setDotsPerMeterX(dpi / 25.4 * 1000)
#        img.setDotsPerMeterY(dpi / 25.4 * 1000)
        
        p = QPainter()
        p.begin(img)

        mapRenderer = QgsMapRendererCustomPainterJob(mapSettings, p)
        mapRenderer.start()
        mapRenderer.waitForFinished()

        p.end()

        cmd = "rm -rf " + tmp_dir
        os.system(cmd)
        cmd = "mkdir " + tmp_dir
        os.system(cmd)
        
        output_png = os.path.join(tmp_dir, str(number)[:-4] + str(".png")) 
        img.save(output_png, "png")
        logging.debug("Image saved.")

        # create worldfile
        output_pngw = os.path.join(tmp_dir, str(number)[:-4] + str(".pngw")) 
        with open(output_pngw, 'w') as outfile:
            outfile.write(str(resolution))
            outfile.write("\n")
            outfile.write("0.0")
            outfile.write("\n")
            outfile.write("0.0")
            outfile.write("\n")
            outfile.write(str(-1*resolution))
            outfile.write("\n")
            outfile.write(str(rect.xMinimum()+0.5*resolution))
            outfile.write("\n")
            outfile.write(str(rect.yMaximum()-0.5*resolution))
            outfile.close()
            logging.debug("Worldfile created.")

        # create geotiff and add overviews
        output_tif = os.path.join(target_dir, str(number)[:-4] + str(".tif")) 
        cmd = "gdal_translate -of GTiff -a_srs EPSG:21781 -co 'TILED=YES' -co 'BLOCKXSIZE=256' -co 'BLOCKYSIZE=256' -co 'COMPRESS=DEFLATE' -co 'PHOTOMETRIC=RGB' " +output_png + " " + output_tif
        print cmd
        os.system(cmd)

        cmd = "gdaladdo -r average " + output_tif + " --config COMPRESS_OVERVIEW DEFLATE --config GDAL_TIFF_OVR_BLOCKSIZE 256 2 4 8 16 32 64"
        print cmd
        os.system(cmd)

    # without this we get an error
    del vlayer

    # close QGIS
    QgsApplication.exitQgis()

    overall_duration = datetime.datetime.now() - starttime
    logging.info("Task complete. Overall duration: " + str(overall_duration))
    logging.shutdown()

