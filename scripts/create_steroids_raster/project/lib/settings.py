# -*- coding: utf-8 -*-

import os

class Settings:

    def __init__(self, opts):
        # QGIS project
        self.qgis_project = "/home/stefan/Projekte/av_lidar_dsm_on_steroids/qgis/qgs/dsm_on_steroids_v4.qgs"
        
        # restrict tile
        self.restrict_tile = opts.restrict_tile
                
        # temporary directory
        self.tmp_dir = "/tmp/dsm_on_steroids/"
        
        # target dir
        self.target_dir = "/home/stefan/mr_candie_nas/Geodaten/ch/zh/are/hoehen/2014/dsm_on_steroids/relief/50cm/"
        #self.target_dir = "/mnt/mr_candie_nas/Geodaten/ch/zh/are/hoehen/2014/dsm_on_steroids/"
                
        # tileindex
        #self.tileindex =  "/home/stefan/Projekte/av_lidar_dsm_on_steroids/tileindex/dtm2014_test1.shp"
        self.tileindex =  "/home/stefan/Projekte/av_lidar_dsm_on_steroids/tileindex/dtm2014.shp"
    
        # dtm/dsm resolution
        self.resolution = 0.5
                
    def get_logfile_path(self):
        return os.path.join("./",  "create_steroids_raster.log") 


