#! /usr/bin/python
# -*- coding: utf-8 -*-
import functools
import numpy as np
import dask.array as da
import skimage as ski

def view(offset_y, offset_x, size_y, size_x, step=1):
    """
    Calculates views for windowes operations on arrays.
    
    For windowed operations on arrays instead of looping through
    every numpy element and then do a second loop for the window,
    the element loop can be substituted by shifting the whole array
    against itself while looping through the window.
    
    In order to do this without padding the array first this implementation
    swaps views when the shift is "outside" the array dimensions.
    
   
    Parameters
    ----------
    offset_y : integer
        Row offset of current window row index from center point.
    offset_x : integer
        Column offset of current window column index from center point.
    size_y : integer
        Number of rows of array
    size_x : integer
        Number of columns of array
    step : integer, optional
    
    Returns
    -------
    tuple of 2D numpy slices
    
    
    Example
    -------
    window_size = 3

    radius = int(window/2)
 
    rows, columns = data.shape
    temp_sum = np.zeros((rows, columns))
 
    # Our window loop  
    for y in range(window):

    #we need offsets from centre !
        y_off = y - radius

        for x in range(window):
            x_off = x - radius
 
            view_in, view_out = view(y_off, x_off, rows, columns)
 
            temp_sum[view_out] += data[view_in]
    
    Notes
    -----
    Source: https://landscapearchaeology.org/2018/numpy-loops/
    """
 
    x = abs(offset_x)
    y = abs(offset_y)
 
    x_in = slice(x , size_x, step) 
    x_out = slice(0, size_x - x, step)
 
    y_in = slice(y, size_y, step)
    y_out = slice(0, size_y - y, step)
 
    # the swapping trick    
    if offset_x < 0: x_in, x_out = x_out, x_in                                 
    if offset_y < 0: y_in, y_out = y_out, y_in
 
    # return window view (in) and main view (out)
    return np.s_[y_in, x_in], np.s_[y_out, x_out]

def num_neighbours(lag=1):
    """
    Calculate number of neigbour pixels for a given lag.
    
    Parameters
    ----------
    lag : int
        Lag distance, defaults to 1.
        
    Returns
    -------
    int
        Number of neighbours
    """
    win_size = 2*lag + 1
    neighbours = win_size**2 - (2*(lag-1) + 1)**2
    
    return neighbours

def create_kernel(n=5, geom="square", kernel=None):
    """
    Create a kernel of size n.
    
    Parameters
    ----------
    n : int, optional
        Kernel size, defaults to 5.
    geom : {"square", "round"}
        Geometry of the kernel. Defaults to square.
    kernel : np.array, optional
        Custom kernel to convolve with. If kernel argument is given
        parameters n and geom are ignored.
    
    Returns
    -------
    np.array
    """
    if kernel is None:
        if geom == "square":
            k = np.ones((n,n))
        elif geom == "round":
            xind, yind = np.indices((n, n))
            c = n // 2
            center = (c, c)
            radius = c / 2

            circle = (xind - center[0])**2 + (yind - center[1])**2 < radius**2
            k = circle.astype(np.int)
    else:
        k = kernel
    
    return k


def neighbour_diff_squared(arr1, arr2=None, lag=1):
    """
    Calculates the squared difference between a pixel and its neighbours
    at the specified lag.
    
    If only one array is supplied variogram is calculated
    for itself (same array is used as the second array).
    
    Parameters
    ----------
    arr1 : np.array
    arr2 : np.array, optional
    lag : int, optional
        The lag distance for the variogram, defaults to 1.
    
    Returns
    -------
    np.array
        Variogram
    
    """
    win = 2*lag + 1
    radius = win // 2
    rows, cols = arr1.shape
    
    #arr1 = np.asarray(arr1)
    
    if arr2 is None:
        arr2 = arr1.copy()
    
    out_arr = np.zeros_like(arr1)

    r = list(range(win))
    for y in r:
        y_off = y - radius

        if y == min(r) or y == max(r):
            x_r = r
        else:
            x_r = [max(r), min(r)]
        
        for x in x_r:
            x_off = x - radius
            view_in, view_out = view(y_off, x_off, rows, cols)
            out_arr[view_out] += (arr1[view_out] - arr2[view_in])**2
            
    return out_arr


#def neighbour_diff_squared1(arr1, arr2=None, lag=1):
    #"""
    #Calculates the (pseudo-) variogram between two arrays.
    
    #If only one array is supplied variogram is calculated
    #for itself (same array is used as the second array).
    
    #Parameters
    #----------
    #arr1 : np.array
    #arr2 : np.array, optional
    #lag : int, optional
        #The lag distance for the variogram, defaults to 1.
    
    #Returns
    #-------
    #np.array
        #Variogram
    
    #"""
    #twoband = False
    #win = 2*lag + 1
    #radius = int(win/2)
    
    ##if arr2 is None:
    ##    arr2 = arr1.copy()
    #inshape0 = arr1.shape[0]
    #if len(arr1.shape) == 3:# and inshape0 == 2:
        #input1 = arr1[0,:,:]
        #input2 = arr1[1,:,:]
        #twoband = True
    ##elif len(arr1.shape) == 2:
    ##    print(arr1.shape)
    ##    input1 = arr1
    ##    input2 = arr1.copy()
    #elif arr2 is not None:
        ##Raise error only two bands are allowed
        ##pass
        #input1 = arr1
        #input2 = arr2
    
    
    #input1 = np.asarray(input1)
    #rows, cols = input1.shape
    
    #out_arr = np.zeros(input1.shape, dtype=input1.dtype.name)
    
    #r = list(range(win))
    #for x in r:
        #x_off = x - radius

        #if x == min(r) or x == max(r):
            #y_r = r
        #else:
            #y_r = [max(r), min(r)]
        
        #for y in y_r:
            #y_off = y - radius
            
            ##view_in, view_out = view(y_off, x_off, rows, cols)
             
            #x_in = slice(abs(x_off) , cols, 1) 
            #x_out = slice(0, cols - abs(x_off), 1)

            #y_in = slice(abs(y_off), rows, 1)
            #y_out = slice(0, rows - abs(y_off), 1)

            ## the swapping trick    
            #if x_off < 0: x_in, x_out = x_out, x_in                                 
            #if y_off < 0: y_in, y_out = y_out, y_in

            ## return window view (in) and main view (out)
            ##return np.s_[y_in, x_in], np.s_[y_out, x_out]
            #out_arr[y_out, x_out] += (input1[y_out, x_out] - input2[y_in, x_in])**2
   
    #if twoband:
        #arr1[0,:,:] = out_arr
        #return arr1
    #else:
        #return out_arr

def _dask_neighbour_diff_squared(x, y=None, lag=1):
    """
    Calculate quared difference between pixel and its
    neighbours at specified lag for dask arrays
    
    Parameters
    ----------
    x : np.array
    y : np.array, optional
        Defaults to None
    lag : int, optional
    
    Returns
    -------
    np.array
        Difference part of variogram calculations
    """
    pvario = functools.partial(neighbour_diff_squared, lag=lag)
    
    if y is None:
        x = da.overlap.overlap(x, depth={0: lag, 1: lag}, boundary={0: "reflect", 1: "reflect"})
        y = x
    else:
        x = da.overlap.overlap(x, depth={0: lag, 1: lag}, boundary={0: "reflect", 1: "reflect"})
        y = da.overlap.overlap(y, depth={0: lag, 1: lag}, boundary={0: "reflect", 1: "reflect"})
    
    res = da.map_blocks(pvario, x, y)
    res = da.overlap.trim_internal(res, {0: lag, 1: lag})
    
    return res


def _win_view_stat(x, win_size=5, stat="nanmean"):
    """
    Calculates specified basic statistical measure for a moveing window
    over an array.

    Parameters
    ----------
    x : np.array
    win_size : int, optional
        Window size, defaults to 5.
    stat : {"nanmean", "nanmax", "nanmin", "nanmedian", "nanstd"}
        Statistical measure to calculate.

    Returns
    -------
    np.array

    """
    measure = getattr(np, stat)

    pad = int(win_size//2)
    data = np.pad(x, (pad, pad), mode="constant", constant_values=(np.nan))

    #get windowed view of array
    windowed = ski.util.view_as_windows(data, (win_size, win_size))

    #calculate measure over last to axis
    res = measure(windowed, axis=(2, 3))

    return res
