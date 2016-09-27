####################################################################################################
# Karl's xray/CalRad functions
# Karl Lapo October/2015
####################################################################################################
# Functions common to a number of CalRad scripts. 
# Anomaly of based on monthly or daily composite
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

#### Function for creating anomalies by group
#### Anomaly
def anom(ds_in,period):
	## Helper function for creating extrapolated values (linear)
	# http://stackoverflow.com/questions/2745329/...
	# ...how-to-make-scipy-interpolate-give-an-extrapolated-result-beyond-the-input-range
	def extrap1d(interpolator):
		from scipy import array
		xs = interpolator.x
		ys = interpolator.y

		def pointwise(x):
			if x < xs[0]:
				return ys[0]+(x-xs[0])*(ys[1]-ys[0])/(xs[1]-xs[0])
			elif x > xs[-1]:
				return ys[-1]+(x-xs[-1])*(ys[-1]-ys[-2])/(xs[-1]-xs[-2])
			else:
				return interpolator(x)

		def ufunclike(xs):
			return array(map(pointwise, array(xs)))

		return ufunclike

	## Group anomalies
	# Initialize output Dataset
	anom = xray.Dataset()

	# Time averaging -- monthly averaging
	# Monthly mean composite
	comp_mean = ds_in.groupby('time.month').mean('time')

	## Monthly, mean anomaly 
	if period == 'month':
		anom['mean'] = ds_in.groupby('time.month') - comp_mean
		anom['std'] = ds_in.resample(freq='M', dim='time', how='std')
	
	## Daily, mean anomaly -- interpolate monthly composite
	elif period == 'day':
		# Daily composite mean calculated from interpolation of monthly composite mean
		x_day = ds_in['time.dayofyear'].values
		comp_mean_daily = xray.Dataset()
		# Julian day of month mid point for non-leap year. Force the function to be cyclic
		x_month = np.array([0,15.5, 45, 74.5, 105, 135.5, 166, 196.5, 227.5, 258, 288.5, 319, 349.5,365])
		
		# Daily anomaly for each group
		y = comp_mean.values
		y_cyclic = np.mean([y[0],y[-1]])
		y = np.insert(y,0,y_cyclic)
		y = np.append(y,y_cyclic)
		# Interpolation function of monthly composite
		daily_interp_f = interp.interp1d(x_month,y)
		# Linear extrapolation for beginning and end of year
		daily_interp_f = extrap1d(daily_interp_f)
		# Assign to structure
		comp_mean_daily = (('dayofyear'),daily_interp_f(x_day))

		# Fill out coords
		comp_mean_daily.coords['dayofyear'] = group_ds['time.dayofyear']
		anom['anom_mean'] = group_ds.groupby('time.dayofyear') - comp_mean_daily
		
		# This needs to be changed to day of year grouping if it is to be used
#         anom['std'] = group_ds.resample(freq='D', dim='time', how='std')
	return anom
