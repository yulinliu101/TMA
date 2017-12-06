# -*- coding: utf-8 -*-
"""
Created on Thu May 20 11:11:46 2016

@ Author: Liu, Yulin
@ Institute: UC Berkeley
"""
from __future__ import division
import numpy as np

# In[19]:

def ReshapeTrajLine(Traj):
    RepeatIndex = np.ones(Traj.shape[0],dtype=int)*2
    RepeatIndex[0] = 1
    RepeatIndex[-1] = 1
    NewTraj = np.repeat(Traj,RepeatIndex,axis = 0)
    NewTraj = NewTraj.reshape(Traj.shape[0]-1,Traj.shape[1]*2)
    return NewTraj

def LineDist(Si,Ei,Sj,Ej,Out = 'All'):
    """
    Get line segment distance between SjEj and SiEi
    Input must be numpy array
    Line segment 1: SiEi
    Line segment 2: SjEj
    Project Line SjEj to SiEi
    
    test code
    LineDist(np.array([0,1]),np.array([1,1]),np.array([0,0]),np.array([1,0]))
    """
    SiEi = Ei - Si
    SjEj = Ej - Sj
    
    SiSj = Sj - Si
    SiEj = Ej - Si
    
    u1 = np.dot(SiSj, SiEi)/np.dot(SiEi,SiEi)
    u2 = np.dot(SiEj, SiEi)/np.dot(SiEi,SiEi)
    
    Ps = Si + np.dot(u1,SiEi)
    Pe = Si + np.dot(u2,SiEi)
    
    CosTheta = np.dot(SiEi,SjEj)/np.sqrt(np.dot(SiEi,SiEi))/np.sqrt(np.dot(SjEj,SjEj))   
    
    L_perp1 = np.sqrt(np.dot(Sj-Ps,Sj-Ps))
    L_perp2 = np.sqrt(np.dot(Ej-Pe,Ej-Pe))
    
    if L_perp1 + L_perp2 == 0:
        D_perp = 0
    else:
        D_perp = (L_perp1**2 + L_perp2**2)/(L_perp1+L_perp2)
    
    L_para1 = min(np.sqrt(np.dot(Ps-Si,Ps-Si)),np.sqrt(np.dot(Ps-Ei,Ps-Ei)))
    L_para2 = min(np.sqrt(np.dot(Ei-Pe,Ei-Pe)),np.sqrt(np.dot(Si-Pe,Si-Pe)))
    D_para = min(L_para1,L_para2)
    
    if CosTheta >= 0 and CosTheta < 1:
        D_theta = np.sqrt(np.dot(SjEj,SjEj)) * np.sqrt(1-CosTheta**2)
    elif CosTheta < 0:
        D_theta = np.sqrt(np.dot(SjEj,SjEj))
    else:
        D_theta = 0        
    
    D_line = D_perp + D_para + D_theta    
    
    if Out == 'All':
        return D_perp, D_para, D_theta, D_line
    elif Out == 'Total':
        return D_line
    elif Out == 'Nopara':
        return D_perp + D_theta
    else:
        raise ValueError('Out can only be All, Total or Nopara')
# In[27]:

def MDL_PAR(Traj, m, n, dist = lambda a, b: np.sqrt(sum((a - b)**2))):
    LH  = (dist(Traj[m],Traj[n]))
    LD = 0
    for i in range(m,n):
        DD = LineDist(Traj[m],Traj[n],Traj[i],Traj[i+1])
        LD += (DD[0]) + (DD[2])  
    LL = LH + LD
    return LL

def MDL_NOPAR(Traj, m, n, dist = lambda a, b: np.sqrt(sum((a - b)**2))):
    LD = 0
    LH = 0
    for i in range(m,n):
        LH += (dist(Traj[i],Traj[i+1]))

    LL = LD + LH
    return LL


# In[35]:

def GetCharaPnt(Traj,alpha):
    """
    Get Characteristic points
    
    # test code
    Traj = np.random.random((300,2))
    aa = time.time()
    CP = GetCharaPnt(Traj,1.5)
    print time.time() - aa
    print len(CP)
    """
    startIndex = 0
    Length = 1
    CP = [startIndex]
    while startIndex + Length < Traj.shape[0]:
        
        currIndex = startIndex + Length
#         print currIndex
        cost_par = MDL_PAR(Traj, startIndex, currIndex)
        cost_nopar = MDL_NOPAR(Traj, startIndex, currIndex)

        if cost_par > cost_nopar * alpha:
            CP.append(currIndex-1)
            startIndex = currIndex - 1
            Length = 1
        else:
            Length += 1
    CP.append(Traj.shape[0]-1)
    return CP


# In[5]:

#def N_Rep_Pnt(Traj, n):
#    """
#    Get N representative points
#    # Test Code
#    Traj = np.random.random((10,2))
#    aa = time.time()
#    a = N_Rep_Pnt(Traj, 10)
#    print time.time() - aa
#
#    """
#    m = len(Traj) - 2
#    L = np.zeros((n,m))
#    for i in range(n):
#        for j in range(m):
#            if i == 0:
#                L[i][j] = Err(Traj,0,j+1)
#
#            else:
#                for kk in range(j):
#                    cost = 999999
#                    cost = min(cost,L[i-1][kk] + Err(Traj, kk+1,j+1))
#                    L[i][j] = cost
#    return L

