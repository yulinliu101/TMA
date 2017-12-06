# -*- coding: utf-8 -*-
"""
Created on Wed Jun 03 13:43:34 2016

@ Author: Liu, Yulin
@ Institute: UC Berkeley
"""

from __future__ import division
#import urllib2
#from urllib.request import urlopen
#from bs4 import BeautifulSoup
import math
import csv
import pandas as pd
#import numpy as np
from datetime import datetime
from shapely.geometry import Polygon, Point
from shapely.geometry.polygon import LinearRing
import os
#import LatLon

# # 1. Combine files w/ Aircraft Type
# # 2. Extract radar records
# # 3. Merge on Aircraft type
# # 4. Get Terminal area trajectories

class GetTMATraj:
    """
    This script is to get the Terminal zone trajectories
    Sample Code:
        Fopename = ['NASA_20150809.cm_sim','NASA_20150810_1.cm_sim','NASA_20150810_2.cm_sim','NASA_20150811.cm_sim',
                    'NASA_20150812_1.cm_sim','NASA_20150812_2.cm_sim','NASA_20150813.cm_sim','NASA_20150814.cm_sim','NASA_20150815.cm_sim']
        a = GetTMATraj(Fopename)
        a.OutputTMA(LandingZone = [32.8,33,-97.2,-96.9,300,1000])
    """
    def __init__(self,Fopename, FWAYPT = 'WayPoint.csv', FACtype = 'FAA_AC_type.csv'):
        self.Fopename = Fopename
        self.FACtype = FACtype
        self.fname_TRACK, self.fname_ETA,self.fname_STA, self.fname_REC = self.InputFile()  
        self.Fwaypt = FWAYPT
        self.TMA_Poly, self.TMA_RING, self.MeterPntList = TMApoly(self.Fwaypt,self.fname_STA)
        
    def InputFile(self):
        
        fname_TRACK = []
        fname_ETA = []
        fname_REC = []
        fname_STA = []
        for Name in self.Fopename:
            if Name[14] != '2':
                f1 = open(Name,'r')
                first_line = f1.readline()
                field1 = first_line.split()
                DT = datetime.strptime(field1[4] + ' ' + field1[5][:8], "%Y%m%d %H:%M:%S")
                fname_TRACK.append('NASA_AC_DATA_' + DT.strftime("%Y%m%d_%H_%M_%S") + '.csv')
                fname_ETA.append('NASA_ETA_' + DT.strftime("%Y%m%d_%H_%M_%S") + '.csv')
                fname_REC.append('NASA_REC_' + DT.strftime("%Y%m%d_%H_%M_%S") + '.csv')        
                fname_STA.append('NASA_STA_' + DT.strftime("%Y%m%d_%H_%M_%S") + '.csv')                
                f1.close()
        return fname_TRACK, fname_ETA, fname_STA, fname_REC
        
    def OutputTMA(self,LandingZone = [32.8,33,-97.2,-96.9,300,1000]):
        print('------ Constructing TMA Polygon -----')
        SubDir = 'TMA_DATA'
        try:
            os.makedirs(SubDir)
        except:
            pass
        
        def GetAir(x):
            AC = x.split('/')
            if len(AC) == 1:
                return AC[0]
            elif len(AC) == 2:
                return AC[0]
            else:
                return AC[1]
        
        def IsInTMA(x,TMA_Poly):
            pnt = Point(x)
            if pnt.within(TMA_Poly) == True:
                return 1
            else:
                return 0
        def GetCleanTraj(TMA_DATA, MinPt, MaxPt):
            a = TMA_DATA.groupby('ACID')['TYPE'].count().reset_index(drop = 0)
            a = a[(a['TYPE']>MinPt) & (a['TYPE']<=MaxPt)]
            return TMA_DATA[TMA_DATA['ACID'].isin(a.ACID)].reset_index(drop = 1)

        FAA_AC_Type = pd.read_csv(self.FACtype, header = None, usecols=(0,1,2,4,5,8),
                                  names= ['Model','Manuf','Air_ID','WTC','WakeCat','FAAWeight'],index_col = False)
        FAA_AC_Type = FAA_AC_Type.groupby('Air_ID').tail(1).reset_index(drop = 1)
        print('------ Processing -----')
        for i in range(len(self.fname_TRACK)):
            print(self.fname_TRACK[i])
                        
            ETA_DATA = pd.read_csv(os.getcwd()+'/ETA_DATA/'+self.fname_ETA[i], header = None, usecols=(0,1,2,3,4,5),
                                   names = ['TYPE','Elap_time','ACID','Fix_Type','DES','Fix_Name'])
                                                                         
            TRACK = pd.read_csv(os.getcwd()+'/TRACK_DATA/'+self.fname_TRACK[i],header=None, usecols=(0,1,2,3,4,5,6,7,8,9,10,11,12),
                                names=['TYPE','Elap_time','ACID','X','Y','Lat','Lon','Alt','V_z','V_GD',
                                       'A_GD','Heading','Heading_rate'])
            REC_DATA = pd.read_csv(os.getcwd()+'/REC_DATA/'+self.fname_REC[i], header = None, usecols=(0,1,4,5),
                                   names = ['TYPE','Elap_time','ACID','Aircraft'])
        
            REC_DATA['ACID'] = REC_DATA['ACID']+'_'+str(i)
            TRACK['ACID'] = TRACK['ACID']+'_'+str(i)
            ETA_DATA['ACID'] = ETA_DATA['ACID'] + '_' + str(i)
            
            REC_DATA1 = REC_DATA.groupby('ACID').tail(1).reset_index(drop = 1)
            REC_DATA1['Air_ID'] = REC_DATA1['Aircraft'].apply(lambda x: GetAir(x))
            REC_DATA1 = REC_DATA1.merge(FAA_AC_Type.ix[:,['Air_ID','WTC','WakeCat','FAAWeight']], on = 'Air_ID', how = 'left')
            
            ETA_DATA = ETA_DATA.sort_values(by = ['ACID','Elap_time']).reset_index(drop = 1)
            ETA_RWY = ETA_DATA[(ETA_DATA['Fix_Type']=='RWY')].groupby('ACID').tail(1).reset_index(drop = 1)
            ETA_FAF = ETA_DATA[(ETA_DATA['Fix_Type']=='FAF')].groupby('ACID').tail(1).reset_index(drop = 1)
            ETA_MFX = ETA_DATA[(ETA_DATA['Fix_Type']=='MFX')].groupby('ACID').tail(1).reset_index(drop = 1)
            ETA_Fixed = pd.concat([ETA_RWY, ETA_MFX, ETA_FAF], axis=1, join='inner')
            ETA_Fixed = ETA_Fixed.ix[:,[0,1,2,3,4,5,9,11,15,17]]
            
            TRACK = TRACK.sort_values(by = ['Elap_time']).reset_index(drop = 1)
            
            ARR_DFW = ETA_Fixed[ETA_Fixed['DES']=='KDFW'].ACID.unique()
#            ARR_DFW = ETA_DATA[ETA_DATA['DES']=='KDFW'].ACID.unique()
        
            Track1 = TRACK.groupby(['ACID']).tail(1).reset_index(drop = True)
            DFW_ARR_FLY = Track1[(Track1['Lat']>LandingZone[0]) & (Track1['Lat'] < LandingZone[1]) & 
                                 (Track1['Lon']>LandingZone[2]) & (Track1['Lon'] < LandingZone[3]) & 
                                 (Track1['Alt']>=LandingZone[4]) & (Track1['Alt'] < LandingZone[5]) &
                                 (Track1['ACID'].isin(ARR_DFW))].reset_index(drop = 1)
            FlyToDFW = DFW_ARR_FLY.ACID.unique()
            ARR_DFW = TRACK[TRACK['ACID'].isin(FlyToDFW)].reset_index(drop = True)
            
            TMA_DFW = ARR_DFW.copy()
            TMA_DFW['TMA'] = TMA_DFW[['Lon','Lat']].apply(lambda x: IsInTMA(x,self.TMA_Poly), axis = 1)
            TMA_DFW = TMA_DFW[TMA_DFW ['TMA']==1].reset_index(drop = 1)
            TMA_DFW = TMA_DFW.merge(REC_DATA1.ix[:,['ACID','Air_ID','WTC','WakeCat','FAAWeight']], on='ACID',how='left')
            TMA_DFW = GetCleanTraj(TMA_DFW, 50, 500)
            print('------ Write to File -----')
            TMA_DFW.to_csv(os.path.join(SubDir, 'TMA_'+self.fname_TRACK[i]), index = 0)
            
        print('------ Finish! -----')

#def FixCoords(Fixname,HEAD = 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'):
#    urllink = 'https://nfdc.faa.gov/nfdcApps/services/airspaceFixes/fix_search.jsp?selectType=state&selectName=AK&keyword='+Fixname
##    req = urllib2.Request(urllink, headers={'User-Agent' : HEAD})
#    response = urlopen(urllink)
#    
#    html = response.read()
#    soup = BeautifulSoup(html)
#    table = soup.findAll('td')
#    try:
#        palmyra = LatLon.string2latlon(table[1].string.split('\n')[0], table[3].string.split('\n')[0], 'd%-%m%-%S% %H')
#        Coords = palmyra.to_string()
#        return [float(Coords[1]), float(Coords[0])]
#    except:
#        print(Fixname)
#        return []

def TMApoly(Fwaypt = None, fname_STA = None):
        MeterPntList = []
        if Fwaypt != None:
            with open(Fwaypt,'r') as csvfile:
                line = csv.reader(csvfile)
                for field in line:
                    MeterPntList.append([float(field[1]),float(field[0])])
#        else:
#            All_Meter_Name = np.array([])
#            for name in fname_STA:
#                a = np.genfromtxt(os.getcwd()+'\STA_DATA\\'+name, usecols = (6,7,8),dtype=[('RWY','S10'),('FAF','S10'),('MFX','S10')],delimiter=",")
#                All_Meter_Name = np.append(All_Meter_Name,a['MFX'])
#            All_Meter_Name = np.unique(All_Meter_Name)
#            with open('WayPoint1.csv','wb') as wcsvfile:
#                wri = csv.writer(wcsvfile)
#                for MFX in All_Meter_Name:
#                    Coords = FixCoords(MFX)
#                    if len(Coords) != 0:
#                        MeterPntList.append(Coords)
#                        wri.writerow(Coords+[MFX])
#                    else:
#                        pass
        
        mlat = sum(x[0] for x in MeterPntList) / len(MeterPntList)
        mlng = sum(x[1] for x in MeterPntList) / len(MeterPntList)

        def algo(x):
            return (math.atan2(x[0] - mlat, x[1] - mlng) + 2 * math.pi) % (2*math.pi)
            
        MeterPntList.sort(key=algo)
        TMA_Ring = LinearRing(MeterPntList)
        TMA_Poly = Polygon(MeterPntList)
        return TMA_Poly, TMA_Ring, MeterPntList
