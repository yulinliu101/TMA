# -*- coding: utf-8 -*-
"""
Created on Thu May 20 15:30:24 2016

@ Author: Liu, Yulin
@ Institute: UC Berkeley
"""

from __future__ import absolute_import, division, print_function, unicode_literals
import bisect
import numpy as np
from Partitioning import ReshapeTrajLine
from six.moves import xrange
from collections import defaultdict

"""
This script is to Construct Distance Matrix based on DTW or LCSS

"""
def fastdtw(x, y, radius=1, dist=lambda a, b: abs(a - b)):
    min_time_size = radius + 2
    if len(x) < min_time_size or len(y) < min_time_size:
        return dtw(x, y, dist=dist)

    x_shrinked = __reduce_by_half(x)
    y_shrinked = __reduce_by_half(y)
    distance, path = fastdtw(x_shrinked, y_shrinked, radius=radius, dist=dist)
    window = __expand_window(path, len(x), len(y), radius)
    return dtw(x, y, window, dist=dist)


def dtw(x, y, window=None, dist=lambda a, b: abs(a - b)):
    len_x, len_y = len(x), len(y)
    if window is None:
        window = [(i, j) for i in xrange(len_x) for j in xrange(len_y)]
    window = [(i + 1, j + 1) for i, j in window]
    D = defaultdict(lambda: [float('inf')])
    D[0, 0] = [0, 0, 0]
    for i, j in window:
        D[i, j] = min([D[i-1, j][0], i-1, j], [D[i, j-1][0], i, j-1], [D[i-1, j-1][0], i-1, j-1], key=lambda a: a[0])
        D[i, j][0] += dist(x[i-1], y[j-1])
    path = []
    i, j = len_x, len_y
    while not (i == j == 0):
        path.append((i-1, j-1))
        i, j = D[i, j][1], D[i, j][2]
     
    path.reverse()
    return (D[len_x, len_y][0], path)


def __reduce_by_half(x):
    if len(x) % 2 == 0:
        red_x = [(x[i] + x[1+i]) / 2 for i in xrange(0, len(x), 2)]
    else:
        red_x = [(x[i] + x[1+i]) / 2 for i in xrange(0, len(x)-1, 2)]
        red_x.append(x[-1])
    return red_x


def __expand_window(path, len_x, len_y, radius):
    path_ = set(path)
    for i, j in path:
        for a, b in ((i + a, j + b) for a in xrange(-radius, radius+1) for b in xrange(-radius, radius+1)):
            path_.add((a, b))

    window_ = set()
    for i, j in path_:
        for a, b in ((i * 2, j * 2), (i * 2, j * 2 + 1), (i * 2 + 1, j * 2), (i * 2 + 1, j * 2 + 1)):
            window_.add((a, b))

    window = []
    start_j = 0
    for i in xrange(0, len_x):
        new_start_j = None
        for j in xrange(start_j, len_y):
            if (i, j) in window_:
                window.append((i, j))
                if new_start_j is None:
                    new_start_j = j
            elif new_start_j is not None:
                break
        start_j = new_start_j

    return window
    
def Fast_Traj_LCS(X, Y, Delta = 1,Epsilon = 1, dist = lambda a, b: sum((a - b)**2)):
    m = len(X)
    n = len(Y)
    L = np.zeros((m+1,n+1))
    for i in range(m+1):
        for j in range(n+1):
            if abs((i-1) - (j-1)) <= Delta:
                if i == 0 or j == 0 :
                    L[i][j] = 0
                elif dist(X[i-1], Y[j-1]) <= Epsilon:
                    L[i][j] = L[i-1][j-1]+1
                else:
                    L[i][j] = max(L[i-1][j] , L[i][j-1])
            else:
                pass
    Similar = L.max()/min(m,n)
    return 1 - Similar

def Distance_Matrix(Traj_Group, method = 'LCSS',TYPE = 'Line',Del = 20,Eps = 0.01, Rad = 1, Dist = lambda a, b: sum(abs(a - b))):
    if TYPE == 'Line':
        for kk in range(len(Traj_Group)):
            Traj_Group[kk] = ReshapeTrajLine(Traj_Group[kk])
    elif TYPE == 'Point':
        pass
    else:
        raise ValueError('TYPE can either be Line or Point')
    
    Dist_G = np.zeros((len(Traj_Group),len(Traj_Group)))
    if method == 'LCSS':
        for i in range(len(Traj_Group)):
            for j in range(i+1,len(Traj_Group)):
                Dist_G[i][j] = Fast_Traj_LCS(Traj_Group[i],Traj_Group[j], Delta = Del,Epsilon = Eps, dist = Dist)
        Dist_G = Dist_G + Dist_G.T
        
    elif method == 'FastDTW':
        for i in range(len(Traj_Group)):
            for j in range(i+1,len(Traj_Group)):
                Dist_G[i][j], temp = fastdtw(Traj_Group[i],Traj_Group[j], radius=Rad, dist = Dist)
        Dist_G = Dist_G + Dist_G.T  
    elif method == 'DTW':
        for i in range(len(Traj_Group)):
            for j in range(i+1,len(Traj_Group)):
                Dist_G[i][j], temp = dtw(Traj_Group[i],Traj_Group[j], dist = Dist)
        Dist_G = Dist_G + Dist_G.T
    else:
        raise ValueError('method can only be LCSS, FastDTW or DTW')
    return Dist_G
    
    
#a = Distance_Matrix([np.asarray([np.ones(3),np.ones(3)]),np.asarray([np.ones(3),np.ones(3)])])
#x = [2,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
#y = [1,2,4,3,5,7,6,8,9,12,10,11,13,15,14,17,16]
#print(fastdtw(x,y))