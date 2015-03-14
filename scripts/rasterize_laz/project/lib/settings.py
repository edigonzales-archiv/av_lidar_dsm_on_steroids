# -*- coding: utf-8 -*-

import os

class Settings:

    def __init__(self, opts):
        # restrict tile
        self.restrict_tile = opts.restrict_tile
        
        # restrict class
        self.restrict_class = opts.restrict_class
                
        # URL
        self.url  = "http://maps.zh.ch/download/hoehen/2014/lidar/"
        
        # temporary directory
        self.tmp_dir = "/tmp/las/"
        
        # target dir
        self.target_dir = "/home/stefan/mr_candie_nas/Geodaten/ch/zh/are/hoehen/2014/dsm_on_steroids/"
        #self.target_dir = "/mnt/mr_candie_nas/Geodaten/ch/zh/are/hoehen/2014/dsm_on_steroids/"
        
        # dtm vrt
        self.dtm_vrt = "/home/stefan/mr_candie_nas/Geodaten/ch/zh/are/hoehen/2014/dtm/grid/50cm/dtm2014.vrt"
        #self.dtm_vrt = "/mnt/mr_candie_nas/Geodaten/ch/zh/are/hoehen/2014/dtm/grid/50cm/dtm2014.vrt"
        
        # target
        self.dtm_vrt = "/home/stefan/mr_candie_nas/Geodaten/ch/zh/are/hoehen/2014/dtm/grid/50cm/dtm2014.vrt"
        #self.dtm_vrt = "/mnt/mr_candie_nas/Geodaten/ch/zh/are/hoehen/2014/dtm/grid/50cm/dtm2014.vrt"
        
        # tileindex
        self.tileindex =  "/home/stefan/Projekte/av_lidar_dsm_on_steroids/tileindex/lidar2014.shp"
        
        # blocksize
        self.blocksize = 256
        
        # dtm/dsm resolution
        self.resolution = 0.5
                
    def get_logfile_path(self):
        return os.path.join("./",  "rasterize_laz.log") 


