# -*- coding: utf-8 -*-
"""
Created on Thu Jun 09 15:11:44 2016

@ Author: Liu, Yulin
@ Institute: UC Berkeley
"""
from __future__ import division
import matplotlib.pyplot as plt
import DenPeak_Clutsering

"""
Key Parameters:
    rho_c:  Distance threshold to construct decision diagram
    rho_c2: Distance threshold to be treated as outliers
    N:      Number of clusters
"""

def Vis_DP(TMA_DFW, DTW_Group_Dist, Traj_Group_ACID, rho_c,rho_c2,N):
    Assign_Result,centroid = DenPeak_Clutsering.DP_Main(DTW_Group_Dist,rho_c,rho_c2,N)
    colors = ['b','g','c','m','y']
    fig = plt.figure(figsize=(16, 8))
    ax1 = fig.add_subplot(1,2,1)
    ax2 = fig.add_subplot(1,2,2)
    for i in range(Assign_Result[:,1].max()+1):
#         ax1 = fig.add_subplot(1,2,i)
        class_member_mask = Assign_Result[(Assign_Result[:,1] == i)&(Assign_Result[:,4] == 1),0]
        Outlier = Assign_Result[Assign_Result[:,4] == 0,0]
        col = colors[i]

        Member_ACID = Traj_Group_ACID[class_member_mask]
        print(col,'Num. of members %d' %len(Member_ACID))
        Outlier_ID = Traj_Group_ACID[Outlier]
        Center = Traj_Group_ACID[centroid]
        
        try:
            ax1 = TMA_DFW[(TMA_DFW['ACID'].isin(Member_ACID))].plot(x = 'Lon', y = 'Lat', 
                                                              facecolors='none', edgecolors=col,zorder = i,
                                                              kind = 'scatter', s = 0.3, grid = True, 
                                                              ax = ax1)
            ax1 = TMA_DFW[(TMA_DFW['ACID'].isin(Center))].plot(x = 'Lon', y = 'Lat', 
                                                              facecolors='none', edgecolors='r',
                                                              kind = 'scatter', s = 3, grid = True, 
                                                              ax = ax1)
            TMA_DFW[(TMA_DFW['ACID'].isin(Outlier_ID))].plot(x = 'Lon', y = 'Lat', 
                                                          facecolors='none', edgecolors='k',
                                                          kind = 'scatter', s = 0.01, grid = True, ax = ax2)
        except:
            pass
    print('Number of Outliers: %f' %len(Outlier))
    plt.show()
    return len(Outlier)/(Assign_Result.shape[0]), Assign_Result

    