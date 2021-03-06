""" Retrieve CCMP data from the NCAR RDA website and join it together.

    NOTE: You must have credentials for http://rda.ucar.edu/ and enter them
          into the wget file: wget_ccmp.sh

.. moduleauthor:: Neil Swart <neil.swart@ec.gc.ca>

"""
import subprocess
import glob
import os
import mv_to_dest

def get_ccmp_data(destination='.', src_path='./'):

    # make sure permissions are set on the wget.
    wget_file = os.path.join(src_path, 'wget_ccmp.sh') 
    subprocess.Popen(['chmod', 'u+x', wget_file])

    # download the data, which is specified in the defined wget script.
    subprocess.Popen(['./' + wget_file]).wait()

    # unzip the data
    gzfiles = glob.glob('month_*_v11l35flk.nc.gz')
    subprocess.Popen('gunzip month_*_v11l35flk.nc.gz', shell=True).wait()
    
    # time join the data
    files = glob.glob('month_*_v11l35flk.nc')
    subprocess.Popen(['cdo', 'mergetime', ' '.join(files),
                      'CCMP_198701-201112.nc']).wait()

    # cleanup
    for f in files:
        os.remove(f) 

    # move to destination
    mv_to_dest.mv_to_dest(destination, 'CCMP_198701-201112.nc')

if __name__=='__main__':
    get_ccmp_data('../data/')