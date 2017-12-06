# -*- coding: utf-8 -*-
"""
Created on Thu May 05 15:22:13 2016

@ Author: Liu, Yulin
@ Institute: UC Berkeley
"""

from __future__ import division
import numpy as np
from matplotlib import pyplot as plt

## Example
# DP_Main(dist_Mat,0.3,0.5)


# In[75]:

def DP_Main(dist_ij,rho_c,rho_c2,N):
    den_arr = cal_density(dist_ij, rho_c)
    mdist2peaks = cal_minDist2Peaks(dist_ij, den_arr)
#     mdist2peaks = MinDist2Peaks(dist_ij, den_arr)
    print('Plot Decision Graph')
    centroids = plot_decisionGraph(den_arr, mdist2peaks,N)
    Assign_Result = assign_cluster(dist_ij,den_arr,centroids,rho_c2)
#    del coords, ix, iy    
    return Assign_Result,centroids

# # Compute local density

# In[32]:

def cal_density(dist_ij, rho_c):
    n = dist_ij.shape[0]
    den_arr = np.zeros(n, dtype=np.int)
    for i in range(n):
        for j in range(i+1, n):
            if dist_ij[i][j] < rho_c:
                den_arr[i] += 1
                den_arr[j] += 1
    return (den_arr)


# # Measure \delta

# In[63]:

def cal_minDist2Peaks(dist_ij, den_arr):
    n = dist_ij.shape[0]
    mdist2peaks = np.repeat(999.9, n)
    max_pdist = 0 # to store the maximum pairwise distance
    for i in range(n):
        mdist_i = mdist2peaks[i]
        for j in range(i+1, n):
            max_pdist = max(max_pdist, dist_ij[i][j])
            if den_arr[i] < den_arr[j]:
                mdist_i = min(mdist_i, dist_ij[i][j])
            elif den_arr[j] <= den_arr[i]:
                mdist2peaks[j] = min(mdist2peaks[j], dist_ij[i][j])
        mdist2peaks[i] = mdist_i
        
    # Update the value for the point with highest density
    max_den_points = np.argwhere(mdist2peaks == 999.9)
    mdist2peaks[max_den_points] = dist_ij[max_den_points,:].max()
#     mdist2peaks[max_den_points] = max_pdist
    return (mdist2peaks)


# In[33]:

def MinDist2Peaks(dist_ij, den_arr1):
    n = dist_ij.shape[0]
    mdist2peaks = np.repeat(999, n)
    for i in range(n):
        Index = den_arr1 > den_arr1[i]
        Index2 = den_arr1 <= den_arr1[i]
        Index2[i] = False
        try:
            mdist2peaks[i] = min(dist_ij[i][Index])
            mdist2peaks[Index2] = np.minimum(mdist2peaks[Index2],dist_ij[i][Index2])
        except:
            mdist2peaks[i] = dist_ij.max()
            mdist2peaks[Index2] = np.minimum(mdist2peaks[Index2],dist_ij[i][Index2])
    return mdist2peaks


# # Decision Graph

class SelectClustCenter(object):
    def __init__(self, x,y,N):
        fig = plt.figure(figsize=(12,8))
        ax = fig.add_subplot(111)
        ax.scatter(x,y,color='red', marker='o', alpha=0.5, s=25,picker=True)
        self.canvas = ax.get_figure().canvas
        self.N = N
        self.X = x
        self.Y = y
        self.cid = None
        self.Coords = []
        self.connect_sf()
        plt.show()
        
    def connect_sf(self):
        if self.cid is None:
            self.cid = self.canvas.mpl_connect('pick_event',
                                               self.click_event)
    def disconnect_sf(self):
        if self.cid is not None:
            self.canvas.mpl_disconnect(self.cid)
            self.cid = None

    def click_event(self, event):
        ind = event.ind
        ix, iy = self.X[ind], self.Y[ind]
        self.Coords.append((ix, iy))
        print('x = %f, y = %f'%(ix, iy))
        if len(self.Coords) >= self.N:
            self.canvas.mpl_disconnect(self.cid)
        
    def return_points(self):
        data = self.Coords
        return data

def plot_decisionGraph(den_arr, mdist2peaks,N):
    
    cc = SelectClustCenter(den_arr,mdist2peaks,N)
    
    coords = cc.return_points()    
    centroids = np.array([],dtype = int)
    noncenter_points = np.array([],dtype = int)    
    for i in range(len(coords)):
        centroids = np.append(centroids,np.argwhere((mdist2peaks == coords[i][1]) & (den_arr == coords[i][0])))
    noncenter_points = np.delete(range(den_arr.shape[0]),centroids) 
    #centroids = np.argwhere(((mdist2peaks == coords[0][1]) & (den_arr == coords[0][0])) | 
    #                        ((mdist2peaks == coords[1][1]) & (den_arr == coords[1][0]))).flatten()
    #noncenter_points = np.argwhere(~(((mdist2peaks == coords[0][1]) & (den_arr == coords[0][0])) | 
    #                        ((mdist2peaks == coords[1][1]) & (den_arr == coords[1][0])))).flatten()
    plt.figure(figsize=(12,8))
    plt.scatter(x=den_arr[noncenter_points],
            y=mdist2peaks[noncenter_points],
            color='red', marker='o', alpha=0.5, s=50)
    
    plt.scatter(x=den_arr[centroids],
            y=mdist2peaks[centroids],
            color='blue', marker='o', alpha=0.6, s=140)
    
    plt.title('Decision Graph', size=20)
    plt.xlabel(r'$\rho$', size=25)
    plt.ylabel(r'$\delta$', size=25)
    plt.ylim(ymin=min(mdist2peaks-0.5), ymax=max(mdist2peaks+0.5))
    plt.tick_params(axis='both', which='major', labelsize=18)
    plt.show()

    return centroids


# # Assignment
# In[82]:

def assign_cluster(dist_ij,den_arr,centroids,rho_c):

    nsize = den_arr.shape[0]
    cmemb = np.ndarray(shape=(nsize,5), dtype='int')
    cmemb[:,:] = -1
    ncm = 0
    for i,cix in enumerate(centroids):
        cmemb[i,0] = cix # centroid index
        cmemb[i,1] = i   # cluster index
        cmemb[i,2] = 0   # Border or not
        cmemb[i,3] = den_arr[cix]   # density
        cmemb[i,4] = 1   # Core or not
        ncm += 1

#    da = np.delete(den_arr, centroids)
    inxsort = np.argsort(den_arr)    
    
    for i in range(den_arr.shape[0]-1, -1, -1):
        ix = inxsort[i]
        if ix in centroids:
            pass
        else:      
            dist = dist_ij[ix][cmemb[:ncm,0]]
                
            nearest_nieghb = np.argmin(dist)
            cmemb[ncm,0] = ix
            cmemb[ncm,3] = den_arr[ix]
            cmemb[ncm,1] = cmemb[nearest_nieghb, 1]
            
            ncm += 1
    
    # Construct Halo
    for i in range(cmemb.shape[0]):
        try:
            cmemb[i,2] = min(dist_ij[cmemb[i,0]][cmemb[cmemb[:,1] != cmemb[i,1],0]]) < rho_c
        except:
            cmemb[i,2] = 0
            
    Rho_b = np.zeros(len(centroids))
    Border = cmemb[cmemb[:,2] == 1]
    for i in range(len(centroids)):
        try:
            Rho_b[i] = Border[Border[:,1] == i][:,3].max()
        except:
            pass
        cmemb[cmemb[:,1] == i,4] = cmemb[cmemb[:,1] == i,3] > max(0,Rho_b[i])
    
    return cmemb
    
# In[36]:

def AssignClust(dist_ij,den_arr,centroids,rho_c):

    nsize = dist_ij.shape[0]
    ArguCent = np.ndarray(shape=(nsize,5), dtype='int')
    ArguCent[:,:] = -1

    for i,cix in enumerate(centroids):
        ArguCent[i,0] = cix # centroid index
        ArguCent[i,1] = i   # cluster index
        ArguCent[i,2] = 0   # Border or not
        ArguCent[i,3] = 999   # density
        ArguCent[i,4] = 1   # Core or not
    
    # Initial Assignment
    da = np.delete(den_arr, centroids)
    inxsort = np.argsort(den_arr) # small to large
    ClusterID = np.zeros(nsize)
    Board = np.zeros(nsize)
    for i in range(da.shape[0]-1, -1, -1):
        ix = inxsort[i]
        ArguCent[nsize-1 - i,0] = ix
        ArguCent[nsize-1 - i,1] = ArguCent[np.argmin(dist_ij[ix][ArguCent[:(nsize-1-i),0]]),1]
        ix2 = ArguCent[:nsize-1-i,1] != ArguCent[nsize-1 - i,1]
        ArguCent[nsize-1 - i,3] = den_arr[ix]

    # Construct Halo
    for i in range(ArguCent.shape[0]):
        try:
            ArguCent[i,2] = min(dist_ij[ArguCent[i,0]][ArguCent[ArguCent[:,1] != ArguCent[i,1],0]]) < rho_c
        except:
            ArguCent[i,2] = 0
    Rho_b = np.zeros(len(centroids))
    Border = ArguCent[ArguCent[:,2] == 1]
    for i in range(len(centroids)):
        try:
            Rho_b[i] = Border[Border[:,1] == i][:,3].max()
        except:
            pass
        ArguCent[ArguCent[:,1] == i,4] = ArguCent[ArguCent[:,1] == i,3] > Rho_b[i]
    
    return ArguCent




