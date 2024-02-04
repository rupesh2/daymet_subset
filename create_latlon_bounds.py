#!/usr/bin/env python3
"""import modules"""
from pyproj import Proj
import numpy as np
import netCDF4 as nc

############################################################
# example daymet file
DAYMET_F = 'daymet_v4_daily_na_prcp_2016.nc'
############################################################

# This scripts adds two new variables to the Daymet files 'lat_vertices'
# and 'lon_vertices', that defines the Daymet cell boundaries.

def lcc_to_latlon(lcc_y, lcc_x):
    """"Converts x, y coordinates in Lambert Conformal Conic (Daymet
    native projection) to lat, lon coordinates"""
    spx =  np.tile(lcc_x, (len(lcc_y), 1))
    spy =  np.transpose([lcc_y] * len(lcc_x))
    # Creating proj class with LCC proj-string
    p = Proj("+proj=lcc +ellps=WGS84 +a=6378137 +b=6356752.314245 +lat_1=25 +lat_2=60 +lon_0=-100 +lat_0=42.5 +x_0=0 +y_0=0 +units=m +no_defs")
    o_latlng = p(spx, spy, inverse=True)
    return o_latlng

def main():
    """main function"""

    with nc.Dataset(DAYMET_F, 'r+') as ds:
        # add vertices dimension
        dname = 'vertices'
        ds.createDimension(dname, 4)

        # reading lat/lon variables
        lat = ds['lat']
        lon = ds['lon']

        # create lat_vertices variable
        lat_v = 'lat_vertices'
        latvert = ds.createVariable(lat_v, lat.dtype, ('y', 'x', 'vertices',), zlib=True)
        latvert.setncattr('units', lat.units)
        # add bound attributes to lat variable
        lat.setncattr('bounds', lat_v)

        # create lon_vertices variable
        lon_v = 'lon_vertices'
        lonvert = ds.createVariable(lon_v, lon.dtype, ('y', 'x', 'vertices',), zlib=True)
        lonvert.setncattr('units', lon.units)
        # add bound attributes to lon variable
        lon.setncattr('bounds', lon_v)

        # read x/y coordinates (m) in LCC projection
        y = ds['y'][:]
        x = ds['x'][:]

        # compute x/y bounds
        res = 1000 # daymet xy resolution (m)
        ymin = y - res/2
        ymax = y + res/2
        xmin = x - res/2
        xmax = x + res/2
        bounds = [(ymin, xmax), (ymax, xmax), (ymax, xmin), (ymin, xmin)]

        # compute bound coordinates
        for i, (yy, xx) in enumerate(bounds):
            latlon = lcc_to_latlon(yy, xx)
            lonvert[:, :, i] = latlon[0]
            latvert[:, :, i] = latlon[1]

if __name__ == "__main__":
    main()
