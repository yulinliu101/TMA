# -*- coding: utf-8 -*-
"""
Created on Wed Jun 03 13:16:31 2016

@ Author: Liu, Yulin
@ Institute: UC Berkeley
"""

from __future__ import division
import csv
from datetime import datetime
import os
# In[ ]:


def GetData(Fopename, TYPE = 'TRACK'):
    """
    To use the script, you need to input a LIST of names of NASA CTAS tracking file, and specify the types of data you want.
    The name of the CTAS file should have the format of 'NASA_YYYYMMDD.cm_sim'
    
    Also, you need to specify the TYPE of file you would like to extract.
    There are four types of file:
        'TRACK': radar track file. this is the main file to get all locations of trajectories
        'ETA': Estimated time of arrival for each flight 
        'STA': Scheduled time of arrival for each flight
        'REC': Record data, including aircraft type info
    
    Example code to run the script:
    Fopename = ['NASA_20150809.cm_sim','NASA_20150810_1.cm_sim','NASA_20150810_2.cm_sim','NASA_20150811.cm_sim',
           'NASA_20150812_1.cm_sim','NASA_20150812_2.cm_sim','NASA_20150813.cm_sim','NASA_20150814.cm_sim','NASA_20150815.cm_sim']
    GetData(Fopename, TYPE = 'TRACK')   
        
    """
    print('------ Extracting -----')
    SubDir = TYPE + '_DATA'
    try:
        os.makedirs(SubDir)
    except:
        pass
    for i in range(len(Fopename)):
        print(i)
        Name = Fopename[i]
        if Name[13] != '_':
            f1 = open(Name,'r')
            first_line = f1.readline()
            field1 = first_line.split()
            DT = datetime.strptime(field1[4] + ' ' + field1[5][:8], "%Y%m%d %H:%M:%S")
            
            if TYPE == 'TRACK':
                fname = 'NASA_AC_DATA_' + DT.strftime("%Y%m%d_%H_%M_%S") + '.csv'
                with open(os.path.join(SubDir, fname),'w') as csvfile:
                    TrackData = csv.writer(csvfile,lineterminator='\n',delimiter=',')
                    for line in f1:
                        field = line.split()
                        if len(field) > 0 and field[0] == 'AC_DATA':
                            field[5] = int(field[5][:2]) + int(field[5][2:4])/60 + float(field[5][4:])/3600
                            field[6] = -(int(field[6][:3]) + int(field[6][3:5])/60 + float(field[6][5:])/3600)
                            TrackData.writerow(field)
                f1.close()
                
            elif TYPE == 'ETA':
                fname = 'NASA_ETA_' + DT.strftime("%Y%m%d_%H_%M_%S") + '.csv'
                with open(os.path.join(SubDir, fname),'w') as csvfile:
                    TrackData = csv.writer(csvfile,lineterminator='\n',delimiter=',')
                    for line in f1:
                        field = line.split()
                        if len(field) > 0 and field[0] == 'ETA_INFORMATION':
                            TrackData.writerow(field)
                f1.close()
            elif TYPE == 'STA':
                fname = 'NASA_STA_' + DT.strftime("%Y%m%d_%H_%M_%S") + '.csv'
                with open(os.path.join(SubDir, fname),'w') as csvfile:
                    TrackData = csv.writer(csvfile,lineterminator='\n',delimiter=',')
                    for line in f1:
                        field = line.split()
                        if len(field) > 0 and field[0] == 'STA_INFORMATION':
                            TrackData.writerow(field)
                f1.close()
            elif TYPE == 'REC':
                fname = 'NASA_REC_' + DT.strftime("%Y%m%d_%H_%M_%S") + '.csv'
                with open(os.path.join(SubDir, fname),'w') as csvfile:
                    TrackData = csv.writer(csvfile,lineterminator='\n',delimiter=',')
                    for line in f1:
                        field = line.split()
                        if len(field) > 0 and field[0] == 'RECORD_DATA' and field[5] != 'NOT_SET':
                            TrackData.writerow(field)
                f1.close()
            else:
                raise ValueError('TYPE can only be TRACK, ETA or STA')
                
                
        elif Name[14] == '1':
            f1 = open(Name,'r')
            f2 = open(Fopename[i+1],'r')
            first_line = f1.readline()
            field1 = first_line.split()
            DT1 = datetime.strptime(field1[4] + ' ' + field1[5][:8], "%Y%m%d %H:%M:%S")
            first_line2 = f2.readline()
            field2 = first_line2.split()
            DT2 = datetime.strptime(field2[4] + ' ' + field2[5][:8], "%Y%m%d %H:%M:%S")
            
            if TYPE == 'TRACK':
                fname = 'NASA_AC_DATA_' + DT1.strftime("%Y%m%d_%H_%M_%S") + '.csv'
    
                with open(os.path.join(SubDir, fname),'w') as csvfile:
                    TrackData = csv.writer(csvfile,lineterminator='\n',delimiter=',')
                    for line in f1:
                        field = line.split()
                        if len(field) > 0 and field[0] == 'AC_DATA':
                            field[5] = int(field[5][:2]) + int(field[5][2:4])/60 + float(field[5][4:])/3600
                            field[6] = -(int(field[6][:3]) + int(field[6][3:5])/60 + float(field[6][5:])/3600)
                            TrackData.writerow(field)
                    for line in f2:
                        field = line.split()
                        if len(field) > 0 and field[0] == 'AC_DATA':
                            field[1] = int(field[1]) + (DT2 - DT1).seconds
                            field[5] = int(field[5][:2]) + int(field[5][2:4])/60 + float(field[5][4:])/3600
                            field[6] = -(int(field[6][:3]) + int(field[6][3:5])/60 + float(field[6][5:])/3600)
                            TrackData.writerow(field)
                f1.close()
                f2.close()
            elif TYPE == 'ETA':
                fname = 'NASA_ETA_' + DT1.strftime("%Y%m%d_%H_%M_%S") + '.csv'
                with open(os.path.join(SubDir, fname),'w') as csvfile:
                    TrackData = csv.writer(csvfile,lineterminator='\n',delimiter=',')
                    for line in f1:
                        field = line.split()
                        if len(field) > 0 and field[0] == 'ETA_INFORMATION':
                            TrackData.writerow(field)
                    for line in f2:
                        field = line.split()
                        if len(field) > 0 and field[0] == 'ETA_INFORMATION':
                            field[1] = int(field[1]) + (DT2 - DT1).seconds
                            TrackData.writerow(field)
                f1.close()
                f2.close()
                
            elif TYPE == 'STA':
                fname = 'NASA_STA_' + DT1.strftime("%Y%m%d_%H_%M_%S") + '.csv'
                with open(os.path.join(SubDir, fname),'w') as csvfile:
                    TrackData = csv.writer(csvfile,lineterminator='\n',delimiter=',')
                    for line in f1:
                        field = line.split()
                        if len(field) > 0 and field[0] == 'STA_INFORMATION':
                            TrackData.writerow(field)
                    for line in f2:
                        field = line.split()
                        if len(field) > 0 and field[0] == 'STA_INFORMATION':
                            field[1] = int(field[1]) + (DT2 - DT1).seconds
                            TrackData.writerow(field)
                f1.close()
                f2.close()
            
            elif TYPE == 'REC':
                fname = 'NASA_REC_' + DT1.strftime("%Y%m%d_%H_%M_%S") + '.csv'
                with open(os.path.join(SubDir, fname),'w') as csvfile:
                    TrackData = csv.writer(csvfile,lineterminator='\n',delimiter=',')
                    for line in f1:
                        field = line.split()
                        if len(field) > 0 and field[0] == 'RECORD_DATA' and field[5] != 'NOT_SET':
                            TrackData.writerow(field)
                    for line in f2:
                        field = line.split()
                        if len(field) > 0 and field[0] == 'RECORD_DATA' and field[5] != 'NOT_SET':
                            field[1] = int(field[1]) + (DT2 - DT1).seconds
                            TrackData.writerow(field)
                f1.close()
                f2.close()
                
            else:
                raise ValueError('TYPE can only be TRACK, ETA or REC')
        else:
            pass
    print('------ Finish! -----')