####################################################################################################
# Karl's xray/CalRad functions
# Karl Lapo September/2015
####################################################################################################
# Functions common to a number of CalRad scripts
####################################################################################################

## Import statements
# netcdf/numpy/xray/stats
import kray
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import xray
from scipy import interpolate as interp
from scipy.stats.stats import pearsonr
from scipy import stats

#### Function for combining xray data variables into a single array with new labeled dimension
def combinevars(ds_in,dat_vars,new_dim_name='new_dim',combinevarname='new_var'):
    ds_out = xray.Dataset()
    ds_out = xray.concat([ds_in[dv] for dv in dat_vars],dim='new_dim')
    ds_out = ds_out.rename({'new_dim': new_dim_name})
    ds_out.coords[new_dim_name] = dat_vars
    ds_out.name = combinevarname

    return ds_out
