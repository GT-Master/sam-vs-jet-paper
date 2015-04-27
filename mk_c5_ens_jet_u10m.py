"""
Calculate the kinematic properties of the SH westerly jet for the CMIP5 ensemble 
and saves them in an HDF store containing PD DataFrames.

.. moduleauthor:: Neil Swart <neil.swart@ec.gc.ca>
"""

import os
import numpy as np
from netCDF4 import Dataset,num2date,date2num
os.system( 'rm -rf /tmp/cdo*') # clean out tmp to make space for CDO processing.
import pandas as pd
import cmipdata as cd
import cdo as cdo; cdo = cdo.Cdo() # recommended import
import matplotlib.pyplot as plt
plt.ion()

# The data location
pp = '/raid/ra40/data/ncs/cmip5/sam/c5_uas/'

# list in the pre-defined list of files to use. Should be 30 models.
f = open(pp + 'list')
names = f.read()
names = filter(None, names.split('\n') ) # split and remove empty strings

def jetprop(uas, lat):
    region = (lat>-70) & (lat<-20)
    rlat = lat[region]
    ruas = uas[: ,region]
    jetmax = ruas.max(axis=1)

    jetmax2 = np.zeros( len(jetmax) )
    latofmax = np.zeros( len(jetmax) )
    jetwidth = np.zeros( len(jetmax) )
    latn = np.zeros( len(jetmax) ) ; lats = np.zeros( len(jetmax) )
    yy = np.linspace(-70,-20,201)

    for t in range(len(jetmax)):
        u2 = np.interp(yy, rlat,ruas[t, :]) 
        jetmax2[t] = u2.max()
        indofmax = u2 == jetmax2[t]
        lom = yy[ indofmax ]
        latofmax[t] = lom[0] if lom.shape !=() else lom

        lat_of_gt_halfmax = yy[u2 >= 0.]
        latn[t] = lat_of_gt_halfmax.max()
        lats[t] = lat_of_gt_halfmax.min()
        jetwidth = latn - lats
        #plt.plot(rlat, ruas[t, :])
        #plt.plot(yy, u2, 'r--')
        #raw_input('go?')
    return  jetmax2, latofmax, latn, lats, jetwidth    

ri = 10
width = np.zeros((1596, 30))
umax = np.zeros((1596, 30))
uloc = np.zeros((1596, 30))
 
for i, name in enumerate(names):
    # load the data and make dataframes
    dims = cd.get_dimensions(pp + name, 'uas', toDatetime=True)
    nc = Dataset(pp + name)
    uas = nc.variables['uas'][:].squeeze()
    lat = dims['lat']
    jetmax, latofmax, latn, lats, jetwidth = jetprop(uas, lat)
    umax[:,i] = jetmax
    uloc[:,i] = latofmax
    width[:,i] = jetwidth
    #plt.close()
    #plt.plot( lat, uas[ri,:], 'k-o', linewidth=2)
    #plt.plot( lat, lat*0, 'k--')
    #plt.plot( latofmax[ri], jetmax[ri], 'rx', markersize=8, markeredgewidth=1)
    #plt.plot(  [-90, 90], [ jetmax[ri],jetmax[ri]  ], 'r--')
    #plt.plot(  [-90, 90], [ jetmax[ri]*0.5, jetmax[ri]*0.5], 'r--')
    
    #print latn[ri], lats[ri]
    #plt.plot( [latn[ri], latn[ri]], [-10, 10], 'r--')
    #plt.plot( [lats[ri], lats[ri]], [-10, 10], 'r--')
    #raw_input('go?')

df_umax = pd.DataFrame(umax, index=dims['time'], columns=np.arange(1,31))
df_uloc = pd.DataFrame(uloc, index=dims['time'], columns=np.arange(1,31))
df_width = pd.DataFrame(width, index=dims['time'], columns=np.arange(1,31))
    
## Create a place to put the data
store = pd.HDFStore(
           '/raid/ra40/data/ncs/cmip5/sam/c5_zonmean_sam-jet_analysis.h5', 
           'a')
store['width'] = df_width
store['maxspd'] = df_umax
store['locmax'] = df_uloc
store.close()      