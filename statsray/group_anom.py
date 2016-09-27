import kray
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import xray
from scipy import interpolate as interp
from scipy.stats.stats import pearsonr
from scipy import stats


# Function for creating anomalies by group
def group_anom(ds_in, grouping_var, groups, var, period):
    '''
    Functions common to a number of CalRad scripts.
    Anomaly of group based on monthly or daily composite
    '''

    # -------------------------------------------------------------------------
    # Group anomalies
    # -------------------------------------------------------------------------
    anom = xray.Dataset()

    # Aggregate grouping variables
    group_ds = kray.group_mean(ds_in, grouping_var, groups)
    group_ds = kray.combinevars(group_ds, groups,
                                new_dim_name=grouping_var, combinevarname=var)

    # Time averaging -- monthly averaging
    # Monthly mean composite
    comp_mean = group_ds.groupby('time.month').mean('time')

    # -------------------------------------------------------------------------
    # Monthly, mean anomaly
    # -------------------------------------------------------------------------
    if period == 'month':
        anom['mean'] = group_ds.groupby('time.month') - comp_mean
        anom['std'] = group_ds.resample(freq='M', dim='time', how='std')

    # -------------------------------------------------------------------------
    # Daily, mean anomaly -- interpolate monthly composite
    # -------------------------------------------------------------------------
    elif period == 'day':
        # Daily composite mean calculated from interpolation of monthly composite mean
        x_day = group_ds['time.dayofyear'].values
        comp_mean_daily = xray.Dataset()
        # Julian day of month mid point for non-leap year. Force the function to be cyclic
        x_month = np.array([0, 15.5, 45, 74.5, 105, 135.5, 166, 196.5, 227.5,
                            258, 288.5, 319, 349.5, 365])

        # Daily anomaly for each group
        for n, gr in enumerate(groups):
            y = comp_mean.loc[{grouping_var: gr}].values
            y_cyclic = np.mean([y[0], y[-1]])
            y = np.insert(y, 0, y_cyclic)
            y = np.append(y, y_cyclic)
            # Interpolation function of monthly composite
            daily_interp_f = interp.interp1d(x_month, y, kind='linear',
                                             fill_value='extrapolate')
            # Assign to structure
            comp_mean_daily[gr] = (('dayofyear'), daily_interp_f(x_day))

        # Fill out coords
        comp_mean_daily.coords['dayofyear'] = group_ds['time.dayofyear']
        comp_mean_daily = kray.combinevars(comp_mean_daily, groups,
                                           new_dim_name=grouping_var,
                                           combinevarname=var)
        anom['anom_mean'] = group_ds.groupby('time.dayofyear') - comp_mean_daily

    return anom
