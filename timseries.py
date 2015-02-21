import numpy as np
import scipy as sp
from scipy import stats
import trend_ts
reload(trend_ts)
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from dateutil.parser import parse
import sam_analysis_data as sad

""" Analyze time series in 20CR, CMIP5 and HadSLP2r

Neil Swart, v4, Feb 2015
Neil.Swart@ec.gc.ca

"""

# set font size
plt.close('all')
plt.ion()
font = {'size'   : 12}
plt.rc('font', **font)

#
# Define some global variables that we use repeatedly
#
# the names of the reanalyses we are using (in column-order of the dataframes)
rean     = ['R1', 'R2', '20CR', 'ERA', 'CFSR', 'MERRA']
num_rean = len( rean )
# corresponding colors to use for plotting each reanalysis
rlc      = [ 'k' , 'y', 'g' , 'b' , 'c' , 'm' ] 
rlc      = [ 'g' , 'y', 'g' , 'b' , 'c' , 'm' ]
seas     = ['mam', 'jja', 'son', 'djf', 'ann']  # names of the seasons
lensea   = len( seas )
xtics    = [datetime(1870,1,1) + relativedelta(years=20*jj) for jj in range(8) ] 
# xticks for time-series plot.
#============================================#
# Load the data which is saved in HDF. The data are in pandas dataframes. There 
#is one dataframe for each variable of interest
# (SAM, jet speed = maxpsd, jet position = locmax and jet width. For each 
#variable there is one dataframe for reanalyses and
# one dataframe for the CMIP5 models. With each dataframe the indices (rows) 
#are 
#a datetime index representing the monthly data
# while each column refers to an individual reanalysis or CMIP5 model. The 
#column order of the reanalyses is given in the variable
# rean above. We're not differentiating models by name here.
press, maxspd, locmax, width, modpress, modmaxspd, modlocmax, modwidth =\
                      sad.load_sam_df()

press.columns = rean
maxspd.columns = rean
locmax.columns = rean
width.columns = rean

# load in the Marshall SAM data
dfmarshall = pd.read_csv('/HOME/ncs/data/marshall_sam/marshall_sam.csv', 
		  index_col=0, parse_dates=True)

# load the reanalysis data
h5f = pd.HDFStore('/raid/ra40/data/ncs/cmip5/sam/rean_sam.h5', 'a')
dfr = h5f['sam/df']
h5f.close()
dfhadslp = dfr['HadSLP2r']/100.
#============================================#


def modtsplot(df, ax):
    """ For the columns of df, compute the columnwise-ensemble mean and 95% 
        confidence interval, then plot the envelope and mean.
    """
    # compute the ensemble mean across all columns (models).
    ens_mean = df.mean( axis=1 )
    # compute the 95% CI with n -1 degrees of freedom.
    num_models =  len( df.columns )
    ens_std = df.std(axis=1) 
    c = sp.stats.t.isf(0.025, num_models - 1 )
    ts_95_ci = ( c * ens_std ) / np.sqrt( num_models )

    # reample to annual and plot
    ens_mean = ens_mean.resample('A')
    ts_95_ci = ts_95_ci.resample('A')
    ax.fill_between(ens_mean.index , ( ens_mean - ts_95_ci ) ,  ( ens_mean + 
                    ts_95_ci), color='r', alpha=0.25, linewidth=0)  
    ax.plot(ens_mean.index, ens_mean, color='r',linewidth=3 ,label='CMIP5')   
                  
def rean_proc(dfr, axts):
    """ Loop over the columns of dfr (corresponding to different reanalyses) 
        and plot the time-series in axis axts.
    """
    for (i, name) in enumerate( ['20CR'] ):#enumerate( rean ):     
        axts.plot(dfr.resample('A').index, dfr[name].resample('A'), 
                  color=rlc[ i ], linewidth=2, alpha=1, label=name)
        axts.set_axisbelow(True)
              
                          
#========= SAM - press ===============#

# Set up the figures
f1 = plt.figure(1)
plt.figure(1).set_size_inches((8,8), forward=True )

f1a = plt.subplot( 421 )
f1b = plt.subplot( 423 )
f1c = plt.subplot( 425 )
f1d = plt.subplot( 427 )

rean_proc(press, axts=f1a)    
modtsplot(modpress, f1a)

#dfmarshall['sam'].resample('A').plot(ax=f1a, color='0.5', style='-', 
             #linewidth=2, grid=False, label='Marshall', zorder=3)
dfhadslp['sam'].resample('A').plot(ax=f1a, color='k', style='--', 
             linewidth=3, grid=False, label='HadSLP2r')

rean_proc(maxspd, axts=f1b)
modtsplot(modmaxspd, f1b)

rean_proc(locmax, axts=f1c)
modtsplot(modlocmax, f1c)

rean_proc(width, axts=f1d)
modtsplot(modwidth, f1d)

# FIGURE 1: Time-series
# defines some lists of labels.
f1ax = [ f1a, f1b, f1c, f1d ]
panlab = ['a)', 'b)', 'c)', 'd)', 'e)', 'f)' ,'g)', 'h)']
yaxlab1 = ['SAM Index (hPa)' , 'Umax (m s$^{-1}$)','Position ($^{\circ}$S)', 
	   'Width ($^{\circ}$ lat.)']

# Loop of figure 1 and label plus adjust subplots.
for i, ax in enumerate( f1ax ):
    ax.set_xticks( xtics )
    ax.set_xlim( [datetime(1880,1,1) , datetime(2013,12,31)] )
    ax.autoscale(enable=True, axis='y', tight=True )
    ylim = ax.get_ylim()
    yrange =  max(ylim) - min(ylim)
    ax.text( datetime(1885,1,1), max( ylim ) -0.15*yrange, panlab[i])
    ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(6) )
    ax.set_ylabel( yaxlab1[i] )

    if (ax != f1d): # only keep xlabels for the bottom panels
        ax.set_xticklabels([])
        ax.set_xlabel('')
    else: 
        plt.setp( ax.xaxis.get_majorticklabels(), rotation=35, ha='right' )
        ax.set_xlabel('Year')

yt = [-54, -52, -50, -48]
f1c.set_yticks(yt)
f1c.set_yticklabels([str(t*-1) for t in yt])
f1d.set_yticks([30, 31, 32, 33])
#f1b.set_yticks([6, 6.5, 7, 7.5, 8])
      
plt.figure(1).subplots_adjust(hspace=0.05)

f1a.legend( ncol=3, prop={'size':12}, bbox_to_anchor=(1.05, 1.3),
            handlelength=2.2, handletextpad=0.075, columnspacing=1.2,
            frameon=False )

# save some pdfs
plt.figure(1).savefig('sam_pos_str_width_ts_v5.pdf',format='pdf',dpi=300,
                      bbox_inches='tight')
