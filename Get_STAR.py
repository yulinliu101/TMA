# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 11:46:16 2016

@ Author: Liu, Yulin
@ Institute: UC Berkeley
"""
from __future__ import division
import pandas as pd
import os
import csv
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import math
from shapely.geometry import Polygon
from shapely.geometry.polygon import LinearRing
from descartes import PolygonPatch

# Extract STAR Procedure



def GetSTAR(Infile, Outfile):
    """
    Infile = os.getcwd()+'/DFW_STAR/KDFW_routes.xml'
    Outfile = os.getcwd() + '/DFW_STAR/STAR.csv'
    """
    try:
        os.makedirs('DFW_STAR')
    except:
        pass
    
    fopen = open(Infile,'r')
    DFW_STAR = ET.parse(fopen)
    fopen.close()
    STAR = DFW_STAR.getroot()
    
    i = 0
    STAR_ROUTE = {}
    
    for Routes in STAR.iter('{http://www.springframework.org/schema/beans}bean'):
        i += 1
        if i > 1:
            try:
                key = Routes.attrib['id']
                Procedure = Routes.attrib['class'].split('.')[-1]
                WPlist = []
            except:
                for WayPnt in Routes:
                    try:
                        WP = WayPnt.find('{http://www.springframework.org/schema/beans}ref').attrib['bean']
                        WPlist.append(WP)
                    except:
                        # Altitude ignored
                        pass
            STAR_ROUTE[key] = {'Procedure':Procedure, 'STAR':WPlist}
    
    with open(Outfile,'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['STAR','Procedure','WaypointID'])
        for item in STAR_ROUTE.items():
            for starwp in item[1]['STAR']:
                writer.writerow([item[0],item[1]['Procedure'],starwp])
    return pd.read_csv(Outfile, header = 0)

def GetWaypointCoords(Infile, Outfile):
    """
    Infile = os.getcwd()+'/DFW_STAR/KDFW_waypoints.xml'
    Outfile = os.getcwd() + '/DFW_STAR/DFW_Waypoint_coords.csv'
    """    
    try:
        os.makedirs('DFW_STAR')
    except:
        pass
    fopen = open(Infile,'r')
    DFW_waypoint = ET.parse(fopen)
    fopen.close()
    WP_Coords = DFW_waypoint.getroot()
    
    with open(Outfile,'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['WaypointID','Lat','Lon'])
        for waypoint in WP_Coords:
            WP_ID = waypoint.attrib['id']
            LatString = waypoint.findall('{http://www.springframework.org/schema/beans}property')[1].attrib['value'].split(':')
            LonString = waypoint.findall('{http://www.springframework.org/schema/beans}property')[2].attrib['value'].split(':')
            Lat = float(LatString[0]) + float(LatString[1])/60 + float(LatString[2])/3600
            if float(LonString[0]) < 0:
                Lon = float(LonString[0]) - float(LonString[1])/60 - float(LonString[2])/3600
            else:
                Lon = float(LonString[0]) + float(LonString[1])/60 + float(LonString[2])/3600
            WRI = [WP_ID, Lat, Lon]
            writer.writerow(WRI)
    return pd.read_csv(Outfile, header = 0)
    
def GetFinalSTAR(STAR_file = False, WP_file = False, STAR_data = False, Waypoint_data = False):
    """
    STAR_file: output from GetSTAR
    WP_file: output from GetWaypointCoords
    STAR_data: pandas dataframe
    Waypoint_data: pandas dataframe
    """
    if STAR_data:
        STAR = STAR_data
    else:
        STAR = pd.read_csv(STAR_file, header = 0)
        
    if Waypoint_data:
        STAR_WP_Coords = Waypoint_data
    else:
        STAR_WP_Coords = pd.read_csv(WP_file, header = 0)
    
    STAR = STAR.merge(STAR_WP_Coords, left_on='WaypointID', right_on='WaypointID', how='left')
    
    def EQPT(x):
        if 'JET' in x:
            return 'JET'
        elif 'TURBO_PROP' in x:
            return 'TURBO'
        elif 'PISTON' in x:
            return 'PISTON'
        else:
            return 'ALL'
    def Meteorology(x):
        if 'IFR' in x:
            return 'IFR'
        elif 'VFR' in x:
            return 'VFR'
        else:
            return 'ALL'
    
    STAR['EQPT'] = STAR.STAR.apply(lambda x: EQPT(x))
    STAR['Meteorology'] = STAR.STAR.apply(lambda x: Meteorology(x))
    
    return STAR
    
def Visualization(STAR_DEP, RouteName, procedure = 'ArrivalRoute'):
    
    """
    RouteName can be obtained by using:
    RouteName = STAR_DEP.STAR.unique()
    """    
    
    STAR = STAR_DEP[(STAR_DEP.Procedure == procedure)]
    SubSTAR = STAR[(STAR.STAR.isin(RouteName))].reset_index(drop = 1)
        
    mLat = STAR.groupby('STAR').head(1).Lat.values
    mLon = STAR.groupby('STAR').head(1).Lon.values
    MeterPntList = STAR.groupby('STAR').head(1)[['Lon','Lat']].values.tolist()
    mlat = sum(mLat) / len(mLat)
    mlng = sum(mLon) / len(mLon)
    
    def algo(x):
        return (math.atan2(x[0] - mlng, x[1] - mlat) + 2 * math.pi) % (2*math.pi)
    
    MeterPntList.sort(key=algo)
    TMA_Ring = LinearRing(MeterPntList)
    TMA_Poly = Polygon(MeterPntList)
    
    fig, ax1 = plt.subplots(figsize = (12,8))
    ax1 = STAR.groupby('STAR').tail(1).plot(x = 'Lon',y = 'Lat', kind = 'scatter', ax = ax1,  c = 'k',zorder = 20)
    
    i = 0
    for idx, gp in SubSTAR.groupby('STAR'):
        i += 1
#        if 'FEVER' in idx or 'ORVLL' in idx or 'DEBBB' in idx:
        ax1 = gp.plot(x = 'Lon',y = 'Lat', legend=False, ax = ax1, style = 'o-', figsize = (12,10),grid = True)
    ax1.set_xlim(-97.8, -96.2)
    ax1.set_ylim(32.2,33.6)
#    
    x,y = TMA_Ring.xy
    ax1.plot(x, y, 'ro')
    ax1.plot(x, y, alpha=0.7, linewidth=3, solid_capstyle='round', c = 'g')
    patch = PolygonPatch(TMA_Poly, alpha=0.2)
    ax1.add_patch(patch)
    ax1.set_xlim(-97.8,-96.2)
    ax1.set_ylim(32.2,33.6)
    return SubSTAR