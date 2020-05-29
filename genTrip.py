# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 18:24:15 2019

@author: Transmatics
"""


import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import scipy.stats as ss
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D
import random

from initialize import *
from funcs import *
import ClassDef as cl
from genNet import *

def distance(pointc, point): ##이동거리
    dist = abs(pointc[0]-point[0])+abs(pointc[1]-point[1])
    return dist

def linkOD2coord(linkOD):
#    linkOD = (linkO, PMO, linkD, PMD)
    linknamelen = int(len(linkOD[0])/4)
    linkOx0 = int(linkOD[0][:linknamelen])
    linkOy0 = int(linkOD[0][linknamelen:2*linknamelen])
    if linkOD[0][:linknamelen]!=linkOD[0][2*linknamelen:3*linknamelen]:
        x0 = linkOx0*len_link+linkOD[1]
        y0 = linkOy0*len_link
    else:
        x0 = linkOx0*len_link
        y0 = linkOy0*len_link+linkOD[1]
        
    linknamelen = int(len(linkOD[0])/4)
    linkDx0 = int(linkOD[2][:linknamelen])
    linkDy0 = int(linkOD[2][linknamelen:2*linknamelen])
    if linkOD[2][:linknamelen]!=linkOD[2][2*linknamelen:3*linknamelen]:
        x1 = linkDx0*len_link+linkOD[3]
        y1 = linkDy0*len_link
    else:
        x1 = linkDx0*len_link
        y1 = linkDy0*len_link+linkOD[3]
        
    return (x0, y0, x1, y1)


def getposition(): #random position
    while(1):
        global dist
        global min_dist
        global max_dist
        dist = min_dist + random.random()*(max_dist-min_dist)
        theta = random.uniform(0,2*math.pi)
            
        disty = (dist/2 * math.sin(theta)) #y range
        distx = (dist/2 * math.cos(theta)) #x range
    #    if disty > network_size_y/2:
    #        disty = network_size_y/2
    #    if distx > network_size/2:
    #        distx = network_size/2
        rangey = (disty,network_size_y-disty)
        rangex = (distx,network_size-distx)  
        midpoint = (np.random.uniform(rangex[0], rangex[1]),np.random.uniform(rangey[0], rangey[1]))
        
        [x0,x1,y0,y1] = [midpoint[0]-distx, midpoint[0]+distx, midpoint[1]-disty, midpoint[1]+disty]
        
        if min([x0,x1,y0,y1])<0 or max([x0,x1])>network_size or max([y0,y1])>network_size_y:
            pass
        else: break
    return (x0,y0,x1,y1)

def getposition_1():
    global centerpointlist
    global walking_timelimit
    global min_dist
    global v_walk
    global network_size
    global network_size_y
    while(1):
        sigma = 0.7
        max_dist = walking_timelimit*v_walk #from centerpoint
        (centerpointO, centerpointD) = random.sample(centerpointlist,2)
        
        x0 = centerpointO[0] + random.gauss(0,sigma)*max_dist
        y0 = centerpointO[1] + random.gauss(0,sigma)*max_dist
        
        x1 = centerpointD[0] + random.gauss(0,sigma)*max_dist
        y1 = centerpointD[1] + random.gauss(0,sigma)*max_dist
        if min([x0,x1,y0,y1])<0 or max([x0,x1])>network_size or max([y0,y1])>network_size_y:
            pass
        elif distance((x0,y0), (x1,y1)) < min_dist: pass
        else: break
    return (x0,y0,x1,y1)

def getposition_2():
    global centerpointO
    global walking_timelimit
    global v_walk
    global min_dist
    global network_size
    global network_size_y
    while(1):
        sigma = 0.7
        max_dist = walking_timelimit*v_walk #from centerpoint
        
        x0 = centerpointO[0] + random.gauss(0,sigma)*max_dist
        y0 = centerpointO[1] + random.gauss(0,sigma)*max_dist
        
        x1 = random.uniform(0,network_size)
        y1 = random.uniform(0,network_size_y)
        if min([x0,x1,y0,y1])<0 or max([x0,x1])>network_size or max([y0,y1])>network_size_y:
                pass
        elif distance((x0,y0), (x1,y1)) < min_dist: pass
        else: break
    
    return (x0,y0,x1,y1)

def getposition_3():
    (x1,y1,x0,y0) = getposition_2()
    return (x0,y0,x1,y1)

def getposition_4(): #random position
    while(1):
        global dist
        global min_dist
        global max_dist
        global network_size
        global network_size_y
        sigma = 1
        
        x = [random.uniform(0,network_size),random.uniform(0,network_size)]
        x.sort()
        y = [network_size_y/2 + random.gauss(0,sigma)*network_size_y/2,network_size_y/2 + random.gauss(0,sigma)*network_size_y/2]
        
        [x0,x1,y0,y1] = [midpoint[0]-distx, midpoint[0]+distx, midpoint[1]-disty, midpoint[1]+disty]
        
        if min([x0,x1,y0,y1])<0 or max([x0,x1])>network_size or max([y0,y1])>network_size_y:
            pass
#        elif abs(theta) > math.pi/2 : pass
        else: break
    return (x0,y0,x1,y1)
    
    
    

#==============================================
#(1) random generation 
##random triplist 생성
#od 거리 distribution + theta distribution 
#중심점 feasible range 설정
#random select
#(2) 
#
#with open('data/Linklist.pickle', 'rb') as f:
#    Linklist = pickle.load(f)
#==============================================
"""
demand_scenario type
0: random
1: concentrated O / concentrated D
2,3: concentrated O / spread D, vice versa
4: oblong city - concentrated O / spread D
"""

#(0) random generation 
if demand_scenario == 0:
    Triplist = []
    t=0
    for i in range(demand):
    #    while(t==0):
        T = cl.Trip(i)
        
        T.OD = getposition()
#        T.taxiT = dist/v_avg
        
        Triplist.append(T)
    
#(1) concentrated O/D
elif demand_scenario == 1:
    centerpoint1 = (network_size*1/4,network_size_y*1/4)
    centerpoint2 = (network_size*3/4,network_size_y*1/4)
    centerpoint3 = (network_size*1/4,network_size_y*3/4)
    centerpoint4 = (network_size*3/4,network_size_y*3/4)
    centerpointlist = [centerpoint1,centerpoint2,centerpoint3,centerpoint4]
    
    Triplist = []
    for i in range(demand):
        T = cl.Trip(i)
        
        T.OD = getposition_1()
#        T.taxiT = 
        
        Triplist.append(T)

#(2) concentrated O, spread D
elif demand_scenario == 2:
    centerpointO = (network_size/2,network_size_y/2)
    
    Triplist = []
    for i in range(demand):
        T = cl.Trip(i)
        
        T.OD = getposition_2()
#        T.taxiT = 
        
        Triplist.append(T)

#(3) concentrated D, spread O
elif demand_scenario == 3:
    centerpointD = (network_size/2,network_size_y/2)
    
    Triplist = []
    for i in range(demand):
        T = cl.Trip(i)
        
        T.OD = getposition_3()
#        T.taxiT = 
        
        Triplist.append(T)
        
#(4) oblong city  - concentrated O / spread D
elif demand_scenario == 4:
    station_o = (0,network_size_y/2)
    station_d = (network_size, network_size_y/2)
    
    Triplist = []
    for i in range(demand):
        T = cl.Trip(i)
        T.OD = getposition_4()
        Triplist.append(T)

#########################################################
savename = wd+'data/Triplist.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Triplist, f)
savename = wd+'data/Triplist_original.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Triplist, f)
data_hold = wd+'iteration_data/'+'type'+str(demand_scenario)+'_'+str(numofveh)+'_'+str(demand)+'/initialroute/'
savename = data_hold+'Triplist_original.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Triplist, f)


#########################################################
#for comparison algorithm
data_hold = wd+'iteration_data/'+'type'+str(demand_scenario)+'_'+str(numofveh)+'_'+str(demand)+'/initialroute/'
df = pd.DataFrame(columns=['demand','capacity','v_avg','numofveh'])
df.loc[len(df)] = [demand, capacity, v_avg, numofveh]
savename = data_hold+'initialize.xlsx'
df.to_excel(savename, index=False)

Pointlist = [(station_o)]+ [(T.OD[0], T.OD[1]) for T in Triplist] + [(T.OD[2], T.OD[3]) for T in Triplist] +[(station_d)]
df = pd.DataFrame(list(zip([point[0] for point in Pointlist],[point[1] for point in Pointlist])),columns=['x','y'])
savename = data_hold+'nodelist.xlsx'
df.to_excel(savename, index=False)

############## ###########################################################
##graph for trip point
Ox, Oy, Dx, Dy = [],[],[],[]
for T in Triplist:
    Ox.append(T.OD[0])
    Oy.append(T.OD[1])
    Dx.append(T.OD[2])
    Dy.append(T.OD[3])
plt.scatter(Ox,Oy,c='b')
plt.scatter(Dx,Dy,c='r')
plt.xlim(0,network_size)
plt.ylim(0,network_size_y)
    
fig = plt.gcf()

fig.set_size_inches(network_size/network_size*10, network_size_y/network_size*10)
filename = wd+'/image'+'/genTrip_demandtype'+str(demand_scenario)+'.png'
fig.savefig(filename, dpi=350)
plt.close()
#savefig('foo.png', bbox_inches='tight')
#########################################################################
