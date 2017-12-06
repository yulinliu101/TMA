# -*- coding: utf-8 -*-
"""
Created on Thu Jun 09 16:22:24 2016

@ Author: Liu, Yulin
@ Institute: UC Berkeley
"""

import Get_All_Data
import Get_TMA_Traj
import Get_Visualization
import Get_Reduced
import Get_DPCluster
import numpy as np
import os

# # Extract flight track from CTAS raw data

Fopename = ['NASA_20150809.cm_sim','NASA_20150810_1.cm_sim','NASA_20150810_2.cm_sim','NASA_20150811.cm_sim',
                    'NASA_20150812_1.cm_sim','NASA_20150812_2.cm_sim','NASA_20150813.cm_sim','NASA_20150814.cm_sim','NASA_20150815.cm_sim']
Get_All_Data.GetData(Fopename,'REC')
Get_All_Data.GetData(Fopename,'ETA')
Get_All_Data.GetData(Fopename,'STA')
Get_All_Data.GetData(Fopename,'TRACK')

# # Extract Valid terminal procedure trajectories
Fopename = ['NASA_20150809.cm_sim','NASA_20150810_1.cm_sim','NASA_20150810_2.cm_sim','NASA_20150811.cm_sim',
            'NASA_20150812_1.cm_sim','NASA_20150812_2.cm_sim','NASA_20150813.cm_sim','NASA_20150814.cm_sim','NASA_20150815.cm_sim']
a = Get_TMA_Traj.GetTMATraj(Fopename,FWAYPT='WayPoint.csv')
a.OutputTMA(LandingZone = [32.8,33,-97.2,-96.9,300,1000])


# # Visualize trajectories for specific day
Get_Visualization.VisualizeTMA(DATE = ['20150809','20150810','20150815']) 


# # Dimension Reduction (MDL) & Distance Matrix Construction (FastDTW)
A = Get_Reduced.MDL_DP(['20150809','20150810','20150815'], Method='Auto')
A.DistMat(Scheme = 'FastDTW')


# # Density Peak Clustering

# In[2]:

TMA_DATA = Get_Reduced.LoadTMAdata(['20150809','20150810','20150815'])
DTW_Group_Dist = np.load(os.getcwd() + '\DIST_MAT\\' + 'NEW_DTW_Group_Dist4.npy')
Traj_Group_ACID = np.load(os.getcwd() + '\DIST_MAT\\' + 'NEW_Traj_Group_ACID4.npy')
OutRatio, Assignment = Get_DPCluster.Vis_DP(TMA_DATA,DTW_Group_Dist, Traj_Group_ACID, rho_c = 0.25, rho_c2 = 0.05,N = 3)
print('Percentage of Outliers: %f%%' %(100*OutRatio))

