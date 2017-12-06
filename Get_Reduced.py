# -*- coding: utf-8 -*-
"""
Created on Thu Jun 09 10:34:07 2016

@ Author: Liu, Yulin
@ Institute: UC Berkeley
"""
# In[1]:

from __future__ import division
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dateutil import parser
from shapely.geometry import Point, LineString
from FastDist_Refine import Distance_Matrix
import Partitioning
import os

class MDL_DP:
    """
    This script is to reduce the dimension of Trajectories and further 
    construct distance matrix based on either DTW or LCSS distance.
    
    Input:
        Date: Designated days to do clustering analysis, if TMA_DATA is entered, 
              then this is not necessary
        TMA_DATA: if Date is specified, then this is not necessary. 
        D_thre: Distance threshold to assign trajectories to MFX/RWY pair, in degree
        N_MFX: The first N_MFX points of each trajectories will be used to comstruct
               a line string, and further compute its distance away from MFX points
        N_RWY: The last N_RWY points of each trajectories will be used to comstruct
               a line string, and further compute its distance away from RWY points
        N_MEM: Only keep groups (MFX/RWY pair) that have more than N_MEM trajectories.
        VisualAid: bool. If need visual aid to do MDL, then enter True. This arg is 
               valid only if we select 'Manual' method.
        Method: 'Auto' or 'Manual'. The way to do MDL and Distance Matrix. If 'Auto',
                then no need to specify every MDL paramters. (Need prior knowledge)
        FAF, MFX, RWY: filenames for FAF, MFX and RWY coordinates.
    Sample Code:
        A = Get_Reduced.MDL_DP(['20150809','20150810','20150815'], Method='Auto')
        B = A.DistMat(Scheme = 'FastDTW')
    """    
    
    
    def __init__(self, Date=None, TMA_DATA = None, D_thre = 0.05,N_MFX=20,N_RWY=35, 
                 N_MEM = 200, VisualAid = True, Method = 'Manual',
                 FAF = 'FAFPoint.csv',MFX = 'WayPoint.csv',RWY = 'RunWay.csv',):
        if Date == None:
            self.TMA_DATA = TMA_DATA
        else:
            self.DATE = Date
        
        if TMA_DATA is None:
            self.TMA_DATA = LoadTMAdata(self.DATE)
        else:
            self.TMA_DATA = TMA_DATA
        
        try:
            os.makedirs('DIST_MAT')
        except:
            pass        
        
        self.D_thre = D_thre
        self.N_MFX = N_MFX
        self.N_RWY = N_RWY
        self.N_MEM = N_MEM
        self.Method = Method
        self.FAF_LATLON, self.MFX_LATLON, self.RWY_LATLON = GetFix(FAF,MFX,RWY)
        self.All_Traj_2d, self.Unique_Label, self.ACID_Group_id = self.AssignRWY_MFX() 
        self.GroupIndex = self.TargetGroup()
        self.VisualAid = VisualAid
        print('%d group(s) with more than %d trajectories Processed\n' %(len(self.GroupIndex),self.N_MEM))
        print('GroupIndices are: ', self.GroupIndex)
        if self.Method == 'Auto':
            print('\nYou select the Auto mode to execute MDL and DistanceMatrix')
        elif self.Method == 'Manual':
            print('\nPlease Specify the Group Index to process MDL...')
        else:
            raise ValueError('Method Can only be Auto or Manual')
        self.Traj_Group_new, self.Traj_Group, self.Traj_Group_ACID, self.INDEX = self.MDL()
        
    def AssignRWY_MFX(self):
        
        # # Store Trajectories as 2D numpy array
        All_Traj_2d = []
        All_Traj_LatLon = []
        ACID_idx = []
        ACID_AC = []
        for name, group in self.TMA_DATA.groupby('ACID'):
            CoordTemp = pd.concat([group.head(self.N_MFX),group.tail(self.N_RWY)]).reset_index(drop = 1)[['Lon','Lat']].values
            # CoordTemp2 = group.reset_index(drop = 1)[['Lat_SCA','Lon_SCA','Alt_SCA']].values
            CoordTemp3 = group[['Lat','Lon']].values
            ACID_idx.append(name)
            ACID_AC.append(group.iloc[0]['AC_CAT'])
            # Construct Linestring
            All_Traj_LatLon.append(LineString(CoordTemp))
            # Construct 2D coords
            All_Traj_2d.append(CoordTemp3)
            
        ACID_idx = np.asarray(ACID_idx)
        All_Traj_2d = np.asarray(All_Traj_2d)
        
        # # Assign MFX/RWY
        
#        FAF_Dist = np.zeros((len(All_Traj_LatLon),len(self.FAF_LATLON)))
        MFX_Dist = np.zeros((len(All_Traj_LatLon),len(self.MFX_LATLON)))
        RWY_Dist = np.zeros((len(All_Traj_LatLon),len(self.RWY_LATLON)))
        
        for i in range(len(All_Traj_LatLon)):
#            for j in range(len(self.FAF_LATLON)):
#                FAF_Dist[i][j] = All_Traj_LatLon[i].distance(self.FAF_LATLON[j][1]) + All_Traj_LatLon[i].distance(self.RWY_LATLON[j][1])
            for k in range(len(self.MFX_LATLON)):
                MFX_Dist[i][k] = All_Traj_LatLon[i].distance(self.MFX_LATLON[k][1])
            for m in range(len(self.RWY_LATLON)):
                RWY_Dist[i][m] = All_Traj_LatLon[i].distance(self.RWY_LATLON[m][1])
#        Min_FAF = np.amin(FAF_Dist, axis = 1)
        Min_MFX = np.amin(MFX_Dist, axis = 1)
        Min_RWY = np.amin(RWY_Dist, axis = 1)
        
#        Assign_FAF = np.argmin(FAF_Dist, axis = 1)
        Assign_MFX = np.argmin(MFX_Dist, axis = 1)
        Assign_RWY = np.argmin(RWY_Dist, axis = 1)
        
#         Use MFX/RWY
#        ACID_MFX_FAF = np.asarray(zip(Assign_MFX,Assign_RWY))
        ACID_MFX_FAF_Min = np.asarray(zip(Assign_MFX,Assign_RWY, Min_MFX, Min_RWY))
        
        ACID_Group_id = np.asarray(zip(ACID_idx,ACID_AC,Assign_MFX,Assign_RWY))
        ACID_Group_id = ACID_Group_id[ACID_MFX_FAF_Min[:,2] < self.D_thre]
        Unique_Label = np.asarray(list(i for i in set(map(tuple,ACID_Group_id[:,1:4]))))
        All_Traj_2d = All_Traj_2d[ACID_MFX_FAF_Min[:,2] < self.D_thre]
        
        return All_Traj_2d, Unique_Label, ACID_Group_id
        
    def TargetGroup(self):
        GroupIndex = []
        for i in range(len(self.Unique_Label)):
            Member_ACID = ((self.ACID_Group_id[:,1] == self.Unique_Label[i][0])&
                           (self.ACID_Group_id[:,2] == self.Unique_Label[i][1])&
                           (self.ACID_Group_id[:,3] == self.Unique_Label[i][2]))
            if sum(Member_ACID) >= self.N_MEM:
                GroupIndex.append(i)
        return GroupIndex
    
    def MDL(self):
                
        if self.Method == 'Auto':
            print('\nPlease Specify the MDL shrinkage factor (1.0 ~ 2.0)...')     
            Alpha = float(raw_input())
            print('\n------------ Auto Mode to MDL -----------')
            for Idx in self.GroupIndex:
                print('Processing Group %d...' %Idx)
                Member_ACID = ((self.ACID_Group_id[:,1] == self.Unique_Label[Idx][0])&
                       (self.ACID_Group_id[:,2] == self.Unique_Label[Idx][1])&
                       (self.ACID_Group_id[:,3] == self.Unique_Label[Idx][2]))
                Traj_Group = self.All_Traj_2d[Member_ACID]
                Traj_Group_ACID = self.ACID_Group_id[Member_ACID,0]
                Traj_Group_new = []
                for jj in range(Traj_Group.shape[0]):
                    CP = Partitioning.GetCharaPnt(Traj_Group[jj],Alpha)
                    Traj_Group_new.append(Traj_Group[jj][CP])
                Traj_Group_new = np.asarray(Traj_Group_new)
                np.save(os.getcwd()+'\\DIST_MAT\\'+'NEW_Traj_Group_ACID'+str(Idx), Traj_Group_ACID)
                np.save(os.getcwd()+'\\DIST_MAT\\'+'NEW_Traj_Group'+str(Idx), Traj_Group_new)
            print('Finished!')
            return Traj_Group_new, Traj_Group, Traj_Group_ACID, Idx
        else:        
            Accept = 'No'
            INDEX = int(raw_input())
            Member_ACID = ((self.ACID_Group_id[:,1] == self.Unique_Label[INDEX][0])&
                           (self.ACID_Group_id[:,2] == self.Unique_Label[INDEX][1])&
                           (self.ACID_Group_id[:,3] == self.Unique_Label[INDEX][2]))
            Traj_Group = self.All_Traj_2d[Member_ACID]
            Traj_Group_ACID = self.ACID_Group_id[Member_ACID,0]
            
            print('Group Index: %d' %(INDEX))
            print('Number of Trajectories in the group: %d\n\n' %(sum(Member_ACID)))
            
            while Accept not in ['Y', 'Yes', 'YES','yes','y']:
                print('Please Specify the MDL shrinkage factor...')
                Alpha = float(raw_input())
                Traj_Group_new = []
                for jj in range(Traj_Group.shape[0]):
                    CP = Partitioning.GetCharaPnt(Traj_Group[jj],Alpha)
                    Traj_Group_new.append(Traj_Group[jj][CP])
        #            CPLen = len(CP)
        #            MAX_CP = 0
        #            MIN_CP = 999
        #            MAX_CP_Ratio = 0
        #            MIN_CP_Ratio = 99
        #            Ratio = (len(Traj_Group[jj])-len(CP))/len(Traj_Group[jj])
        #            MAX_CP = max(MAX_CP,CPLen)
        #            MIN_CP = min(MIN_CP,CPLen)
        #            MAX_CP_Ratio = max(MAX_CP_Ratio,Ratio)
        #            MIN_CP_Ratio = min(MIN_CP_Ratio,Ratio)
        #            print MAX_CP,MIN_CP,MAX_CP_Ratio*100,MIN_CP_Ratio*100
                Traj_Group_new = np.asarray(Traj_Group_new)
                
                if self.VisualAid == True:
                    print('\n\nEnter the number of trajectories you want to visualize...')
                    NN = int(raw_input())
                    plt.figure(figsize=(10,8))
                    for i in np.random.randint(0,Traj_Group.shape[0],NN):
                        plt.plot(Traj_Group[i][:,1],Traj_Group[i][:,0],'b')
                        plt.scatter(Traj_Group_new[i][:,1],Traj_Group_new[i][:,0],marker='o', facecolor = 'w',edgecolor = 'r')
                    plt.show()
                else:
                    pass
                print('Is MDL result good? ...YES/NO\n')
                Accept = raw_input()
            return Traj_Group_new, Traj_Group, Traj_Group_ACID, INDEX
        
    def DistMat(self, Scheme = 'FastDTW', TYPE = 'Line', SAVE = False):
        if self.Method == 'Auto':
            for Idx in self.GroupIndex:
                print('Constructing Distance Matrix for Group %d...' %Idx)
                Traj_Group_new = np.load(os.getcwd()+'\\DIST_MAT\\'+'NEW_Traj_Group'+str(Idx)+'.npy')
                DTW_Group_Dist = Distance_Matrix(Traj_Group_new, method = Scheme, TYPE = TYPE,Rad = 1,
                                           Dist = lambda a, b: Partitioning.LineDist(a[:int(len(a)/2)],a[int(len(a)/2):],
                                                                                       b[:int(len(a)/2)],b[int(len(a)/2):],'Nopara'))
                np.save(os.getcwd()+'\\DIST_MAT\\'+'NEW_DTW_Group_Dist'+str(Idx)+'.npy', DTW_Group_Dist)
            return 'Auto Process Finished! See saved file in the directory ...\DIST_MAT'
        else:
            DTW_Group_Dist = Distance_Matrix(self.Traj_Group_new, method = Scheme, TYPE = TYPE,Rad = 1,
                                               Dist = lambda a, b: Partitioning.LineDist(a[:int(len(a)/2)],a[int(len(a)/2):],
                                                                                           b[:int(len(a)/2)],b[int(len(a)/2):],'Nopara'))
            if SAVE == True:
                np.save(os.getcwd()+'\\DIST_MAT\\'+'NEW_DTW_Group_Dist'+str(self.INDEX), DTW_Group_Dist)
                np.save(os.getcwd()+'\\DIST_MAT\\'+'NEW_Traj_Group_ACID'+str(self.INDEX), self.Traj_Group_ACID)
        return DTW_Group_Dist
        
def GetFix(FAF = 'FAFPoint.csv',MFX = 'WayPoint.csv',RWY = 'RunWay.csv'):
    FAF_LATLON = []
    with open(FAF,'r') as csvfile:
        FAF_Coord = csv.reader(csvfile)
        next(FAF_Coord)
        for line in FAF_Coord:
            if float(line[1]) <= -97:
                FAF_LATLON.append([line[2],Point(float(line[1]),float(line[0]))])
    
    MFX_LATLON = []
    with open(MFX,'r') as csvfile:
        MFX_Coord = csv.reader(csvfile)
        for line in MFX_Coord:
            MFX_LATLON.append([line[2],Point(float(line[1]),float(line[0]))])
            
    RWY_LATLON = []
    with open(RWY,'r') as csvfile:
        RWY_Coord = csv.reader(csvfile)
        for line in RWY_Coord:
            RWY_LATLON.append([line[2],Point(float(line[1]),float(line[0]))])
    return FAF_LATLON, MFX_LATLON, RWY_LATLON

def LoadTMAdata(DATE):
        fname_TMA = os.listdir(os.getcwd() + '\TMA_DATA')
        i = -1
        IDX = []
        for tname in fname_TMA:
            i += 1
            for date in DATE:                
                date = parser.parse(date).strftime('%Y%m%d')
                if date in tname:            
                    IDX.append(i)
                    
        if len(IDX) == 0:
            raise ValueError('NO DATA LOADED! PLEASE CHECK YOUR DIRECTORY OR DATE')            
            
        elif len(IDX) == 1:
            TMA_DFW = pd.read_csv(os.getcwd()+'\TMA_DATA\\'+fname_TMA[IDX[0]])
        else:
            TMA_DFW = pd.read_csv(os.getcwd()+'\TMA_DATA\\'+fname_TMA[IDX[0]])
            IDX.remove(IDX[0])
            for i in IDX:
                TMA_DFW = TMA_DFW.append(pd.read_csv(os.getcwd()+'\TMA_DATA\\'+fname_TMA[i]))
        
        TMA_DFW = TMA_DFW.reset_index(drop = True)
#        TMA_DFW['Lat_SCA'] = (TMA_DFW.Lat - min(TMA_DFW.Lat))/(max(TMA_DFW.Lat) - min(TMA_DFW.Lat))
#        TMA_DFW['Lon_SCA'] = (TMA_DFW.Lon - min(TMA_DFW.Lon))/(max(TMA_DFW.Lon) - min(TMA_DFW.Lon))
#        TMA_DFW['Alt_SCA'] = (TMA_DFW.Alt - min(TMA_DFW.Alt))/(max(TMA_DFW.Alt) - min(TMA_DFW.Alt))
        TMA_DFW['AC_CAT'] = np.where((TMA_DFW['Air_ID'].str[:1]=='A')&(TMA_DFW['FAAWeight']=='L'), 'LA', 
                                np.where((TMA_DFW['Air_ID'].str[:1]=='B')&(TMA_DFW['Air_ID'].str[:2]!='BE')&(TMA_DFW['FAAWeight']=='L'), 'LB',
                                    np.where((TMA_DFW['FAAWeight']=='J'), 'J',
                                        np.where((TMA_DFW['FAAWeight']=='H'), 'H',
                                            np.where((TMA_DFW['FAAWeight']=='S+'), 'S+',
                                                np.where((TMA_DFW['FAAWeight']=='S'), 'S','LO'))))))
        return TMA_DFW