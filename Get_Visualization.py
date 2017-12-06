# -*- coding: utf-8 -*-
"""
Created on Wed Jun 08 15:23:55 2016

@ Author: Liu, Yulin
@ Institute: UC Berkeley
"""
from __future__ import division
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from descartes import PolygonPatch
from Get_TMA_Traj import TMApoly
from dateutil import parser

def VisualizeTMA(DATE,FWAYPT = 'WayPoint.csv'):

    """
    Visualize terminal trajectories for specific days.
    Input: 
        List of Filenames for original datafile
        List of Date for specific day(s), could be in almost any date format
            e.g. ['%yyyy%mm%dd', '%yyyy-%mm-%dd', '%yyyy/%mm/%dd']
    Sample Code:    
    Fopename = ['NASA_20150809.cm_sim','NASA_20150810_1.cm_sim','NASA_20150810_2.cm_sim','NASA_20150811.cm_sim',
           'NASA_20150812_1.cm_sim','NASA_20150812_2.cm_sim','NASA_20150813.cm_sim','NASA_20150814.cm_sim','NASA_20150815.cm_sim']
    VisualizeTMA(Fopename,DATE = ['20150809','20150810'])    
    """

    TMA_Poly, TMA_Ring, MeterPntList = TMApoly(FWAYPT)
    MeterPntList = np.asarray(MeterPntList)
    
    i = -1
    IDX = []
    fname_TMA = os.listdir(os.getcwd()+'/TMA_DATA')
    for tname in fname_TMA:
        i += 1
        for date in DATE:
            date = parser.parse(date).strftime('%Y%m%d')
            if date in tname:            
                IDX.append(i)
        
    for i in IDX:    
        TMA_DFW = pd.read_csv(os.getcwd()+'/TMA_DATA/'+fname_TMA[i], header = 0, 
                              names = ['TYPE','Elap_time','ACID','X','Y','Lat','Lon','Alt','V_z',
                                       'V_GD','A_GD','Heading','Heading_rate','TMA','Air_ID','WTC','WakeCat','FAAWeight'])
        MFX_Coords = pd.DataFrame(MeterPntList, columns = ['Lon','Lat'])
        
        ax1 = TMA_DFW.plot(x = 'Lon', y = 'Lat', kind = 'scatter', s = 0.03, figsize=(12,10),grid = True)
        ax1 = MFX_Coords.plot(x = 'Lon', y = 'Lat', kind = 'scatter', s = 50, c = 'r', ax = ax1,grid = True)
        x,y = TMA_Ring.xy
        ax1.plot(x, y, alpha=0.7, linewidth=3, solid_capstyle='round')
        patch = PolygonPatch(TMA_Poly, alpha=0.2)
        ax1.add_patch(patch)
        ax1.set_xlim(-97.8,-96.2)
        ax1.set_ylim(32.2,33.6)
        ax1.set_title('Terminal Area Trajectories')
        plt.show()