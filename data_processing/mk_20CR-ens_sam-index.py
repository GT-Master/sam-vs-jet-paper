"""
Computes the SAM index for the 20CR ensemble and saves them to DataFrames in HDF5.

.. moduleauthor:: Neil Swart <neil.swart@ec.gc.ca>
"""
import os
import numpy as np
from netCDF4 import Dataset,num2date,date2num
import pandas as pd
import cmipdata as cd
from calc_sam import calc_sam

def mk_20cr_sam_index(datapath='.'):
    """Calculates the SAM index for the 20CR ensemble
    """
    #The pre-computed zonal mean SLP file
    zmfn = os.path.join(datapath, 'zonal-mean_remap_20CR_ens_slp.mon.mean.nc')

    # load the data and make dataframes
    dims = cd.get_dimensions(zmfn, 'slp', toDatetime=True)
    sam_20cr = calc_sam(zmfn, 'slp', start_date='1871-01-01',
                        end_date='2013-12-31')

    df_sam = pd.DataFrame(sam_20cr, index=dims['time'])
    
    # Store the DataFrame in HDF5
    out_file = os.path.join(datapath, '20cr_ensemble_sam_analysis.h5')
    store = pd.HDFStore(out_file, 'a')
    store['sam'] = df_sam
    store.close()

if __name__ == '__main__':
    mk_20cr_sam_index(datapath='../data_retrieval/data/')