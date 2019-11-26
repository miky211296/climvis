"""This configuration module is a container for parameters and constants."""
import os
import sys

def cru_cfg_file():
    if not os.path.exists(os.path.expanduser('~/.climvis')):
        sys.exit('No file .climvis in {}. '\
                 'Create one with the path '\
                 'of data dir.'.format(os.path.expanduser('~')))
    else:
        with open(os.path.expanduser('~/.climvis')) as f:
            global cru_dir
            cru_dir = f.readline()[:-1]
            print(cru_dir)

cru_cfg_file()
#cru_dir = '/home/michele211296/Documents/scipro/data/'
cru_tmp_file = cru_dir + 'cru_ts4.03.1901.2018.tmp.dat.nc'
cru_pre_file = cru_dir + 'cru_ts4.03.1901.2018.pre.dat.nc'
cru_topo_file = cru_dir + 'cru_cl1_topography.nc'

for file in (cru_tmp_file, cru_pre_file, cru_topo_file):
    if not os.path.exists(file):
        sys.exit('The CRU files are not available on this system.' \
                 'For cruvis to work properly, please create a file called' \
                 '".cruvis" in your HOME directory, and indicate the path ' \
                 'to the CRU directory in it.')

bdir = os.path.dirname(__file__)
html_tpl = os.path.join(bdir, 'data', 'template.html')
world_cities = os.path.join(bdir, 'data', 'world_cities.csv')

default_zoom = 8
