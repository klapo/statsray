####################################################################################################
# Karl's xray/CalRad functions
# Karl Lapo September/2015
####################################################################################################
# Functions common to a number of CalRad scripts
####################################################################################################

# Import statements
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import xray
from scipy import interpolate as interp
from scipy.stats.stats import pearsonr
from scipy import stats


def group_mean(ds_in, grouping_var, groups):
    '''Function taking mean across grouping variable, leaving other dimensions
    untouched. '''
    gr_ds = xray.Dataset()
    for gr in groups:
        gr_ds[gr] = ds_in.loc[{grouping_var: gr}].mean(grouping_var)
    return(gr_ds)
