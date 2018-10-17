import numpy as np


def nresample(ds, n, dim):
    '''
    Aggregate every 'n'-th value along a dimension, 'dim', for the dataset 'ds'
    and return the mean.
    I do not know why this function drops all variables without a dimension.
    '''
    # Use integer division (e.g., 3 // 2 = 1) to create indices for grouping
    ind = np.arange(len(ds[dim])) // n

    # Create a new dimension for the groupby command
    ds['agg_dim'] = (dim, ind)

    # For some reason the groupby function drops the x dimension and replaces
    # it with the 'agg_dim' temp variable. Let's instead return the mean of
    # dim using the same aggregation.
    new_dim = ds.swap_dims({dim: 'agg_dim'})[dim].groupby('agg_dim').mean(dim='agg_dim')

    # Group every n observations together and take the mean
    ds = ds.groupby('agg_dim', squeeze=False).mean(dim=dim)

    # Add the original dimenion, averaged over n values, to the dataset
    ds[dim] = ('agg_dim', new_dim)
    ds = ds.swap_dims({'agg_dim': dim}).drop('agg_dim')
    return(ds)
