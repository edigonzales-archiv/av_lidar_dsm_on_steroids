# -*- coding: utf-8 -*-

import os

class Settings:

    def __init__(self, opts):
        # restrict tile
        self.restrict_tile = opts.restrict_tile
        
        # restrict class
        self.restrict_class = opts.restrict_class
        
        # target dir
        self.target_dir = opts.target_dir
        
        # URL
        self.url  = "http://maps.zh.ch/download/hoehen/2014/lidar/"
        
        # temporary directory
        self.tmp_dir = "/tmp/las/"
        
        # tileindex
        self.tileindex =  "/home/stefan/Projekte/av_lidar_dsm_on_steroids/tileindex/lidar2014.shp"
        
        # blocksize
        self.blocksize = 256
        
        # dtm/dsm resolution
        self.resolution = 0.5
                
    def get_logfile_path(self):
        return os.path.join("./",  "rasterize_laz.log") 


