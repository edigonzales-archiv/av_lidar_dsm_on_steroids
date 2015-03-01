# -*- coding: utf-8 -*-

from argparse import ArgumentParser

class Options:
    def __init__(self):
        self._init_parser()

    def _init_parser(self):
        usage = 'bin/rasterize_laz'
        self.parser = ArgumentParser(usage=usage)
        self.parser.add_argument('--tile',
                                action = 'store',
                                type = str, 
                                default = "",
                                dest ='restrict_tile',
                                help = 'Only create the tile with the specified name, even if there are more tiles in the tile index than just this one. This tile must be listed in the tile index file (e.g. 6950_2450.laz)')

        self.parser.add_argument('--class',
                                action = 'store',
                                type = str, 
                                default = "",
                                dest ='restrict_class',
                                help = 'Only create the tile of the specified class.')

    def parse(self, args=None):
        return self.parser.parse_args(args)
