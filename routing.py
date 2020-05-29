# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 23:42:25 2020

@author: JIHU
"""


import os
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import copy
import shutil
import time
import warnings

from sklearn.cluster import KMeans
from kneed import KneeLocator

from initialize import *
from funcs import *
from func_clustering import *
import ClassDef as cl

compT0 = time.clock()
###########################################################################
with open('data/Triplist.pickle','rb') as f:
    Triplist = pickle.load(f)  
#with open('data/Clusterlist.pickle','rb') as f:
#    Clusterlist = pickle.load(f)  
###########################################################################
#########functions

def cos_theta(point0, point1):
    vec0 = (station_d[0] - point0[0] , station_d[1] - point0[1])
    vec1 = (point1[0] - point0[0] , point1[1] - point0[1])
    cos_theta = np.dot(vec0, vec1)/(np.linalg.norm(vec0)* np.linalg.norm(vec1))
    return cos_theta

def distance(pointc, point): ##이동거리
    dist = abs(pointc[0]-point[0])+abs(pointc[1]-point[1])
    return dist

def update_Rtable(Rtable, pointc, C):
    idx = list(Rtable.columns)
    try:
        currentcount = list(Rtable['count'])[-1]
        currenttime = list(Rtable['time'])[-1]
        cumdist = list(Rtable['distance'])[-1]
    except:
        currentcount = 0
        currenttime = 0
        cumdist = 0
    newtime = currenttime + 5*2/60 + 5/60 * len(C.triplist+C.droplist) + distance(pointc,C.cent)/v_avg
    newdist = cumdist + distance(pointc,C.cent)
    line = {idx[0]:C, idx[1]:C.ID, idx[2]:[currentcount+len(C.triplist)-len(C.droplist)], idx[3]:[len(C.triplist)], idx[4]:[len(C.droplist)], idx[5]:newtime, idx[6]:newdist}
    line = pd.DataFrame(data = line, columns=idx, index=[max(len(Rtable)-0.5, 0)])
    Rtable = pd.concat([Rtable, line]).reset_index(drop=True)
    TTcalculate(C, Rtable)
    return Rtable

def firstcluster_select(R,pointc,clusterlist,Rtable):
    ##nearest cluster from current point + count 
    alpha = 0.5 ####@@@@@
    scorelist = [distance(pointc, C.cent)*alpha + 1/(C.count)*(1-alpha) for C in clusterlist]
    idx = scorelist.index(min(scorelist))
    R.clusterlist = R.clusterlist + [clusterlist[idx]]
    pointc = copy.copy(R.clusterlist[-1])
#    
    Rtable = update_Rtable(Rtable,pointc.cent,clusterlist[idx])
    
    return R, pointc, Rtable 

def nextcluster_score(pointc, Clusterlist):
    global alpha
    global beta
    ###@@@@@
    scorelist = [network_size/distance(pointc.cent, C.cent)*alpha + len(C.triplist)*beta + len(C.droplist)*(1-beta) + C.count**2 for C in Clusterlist]
    return scorelist
    
def TTcalculate(C, Rtable):
    time = list(Rtable['time'])[-1]
    for T in C.triplist:
        T.t0 = time
    for T in C.droplist:
        T.t1 = time

def additional_point(pointc, pointd, candidate_clusterlist):
    #candiate_clusterlist 중 midway_dest에 가는 동안 들를 만한 곳들
    feasible_clusterlist = [C for C in candidate_clusterlist if C.type=='D' or feasible(pointc.cent, C.cent)]
    #pointc - C - midway (time limit)
    tmp = []
    
    for C in feasible_clusterlist:
        if additional_timetest(pointc, pointd, C):
            tmp.append(C)
        
    feasible_clusterlist = tmp
    return feasible_clusterlist

def update_Rtable(Rtable, pointc, C):
    idx = list(Rtable.columns)
    try:
        currentcount = list(Rtable['count'])[-1]
        currenttime = list(Rtable['time'])[-1]
        cumdist = list(Rtable['distance'])[-1]
    except:
        currentcount = 0
        currenttime = 0
        cumdist = 0
    newtime = currenttime + 5*2/60 + 5/60 * len(C.triplist+C.droplist) + distance(pointc,C.cent)/v_avg
    newdist = cumdist + distance(pointc,C.cent)
    line = {idx[0]:C, idx[1]:C.ID, idx[2]:[currentcount+len(C.triplist)-len(C.droplist)], idx[3]:[len(C.triplist)], idx[4]:[len(C.droplist)], idx[5]:newtime, idx[6]:newdist}
    line = pd.DataFrame(data = line, columns=idx, index=[max(len(Rtable)-0.5, 0)])
    Rtable = pd.concat([Rtable, line]).reset_index(drop=True)
    TTcalculate(C, Rtable)
    return Rtable

def Rtable_making(R):
#    R = cl.Route(veh)
    global station_o
    cols = "C,CID,count,pickup,dropoff,time,distance"
    Rtable = pd.DataFrame(columns=cols.split(','))
    idx = list(Rtable.columns)
    pointc = copy.copy(station_o)
    
    for C in R.clusterlist:
        Rtable = update_Rtable(Rtable, pointc, C)
    
    tmpTlist = []
    for C in R.clusterlist:
        tmpTlist = tmpTlist + C.droplist
        
    for i,T in enumerate(tmpTlist):
        try:
            pickuptime = list(Rtable['time'])[list(Rtable['C']).index(T.clusterO)]
            dropofftime = list(Rtable['time'])[list(Rtable['C']).index(T.clusterD)]
            T.IVT = dropofftime-pickuptime
        except: pass
    
    return Rtable
    
    
#
#plt.plot(range(len(Triplist)), sum_of_squared_distance, 'bx-')
#plt.ylabel('Sum_of_squared_distances')
#plt.show()
###########################################################################
#########sequential priority search
Routelist = []
Rtablelist = []
#
Boardinglist = []
Deliveredlist = []
#pointc: current point, point0
#station_o, station_d
#v0: (station_d[0] - pointc[0],station_d[1] - pointc[1])

#Clusterlist_tmp = copy.copy(Clusterlist)
#try:        
#    os.mkdir(wd + 'graph')  
#except:
#    pass
for veh in range(numofveh):

    R = cl.Route(veh)
    cols = "C,CID,count,pickup,dropoff,time,distance"
    Rtable = pd.DataFrame(columns=cols.split(','))
    
    pointc = copy.copy(station_o)
    
    ####################################### ####################################
    #clustering
    Clusterlist, Triplist , Boardinglist= clustering(Triplist, Boardinglist)
    
    ####################################### ####################################
    #first O
    if len(Triplist)==0:
        Routelist.append(R)
        continue
    R, pointc, Rtable = firstcluster_select(R, pointc, Clusterlist, Rtable)
    
    while(1):
        #######################################################
        #reclustering
        lastC = R.clusterlist[-1]
        try:
            for T in lastC.triplist:
                Triplist.remove(T)
        except:
            pass
        try:
            for T in next_cluster.droplist:
                Boardinglist.remove(T)
                Deliveredlist.append(T)
        except:
            pass
        Boardinglist = Boardinglist + lastC.triplist
        
        if len(Triplist+Boardinglist)==0:
            break
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            Clusterlist, Triplist, Boardinglist = clustering(Triplist, Boardinglist)
        
        
        ###########################################################################
        #########set next cluster
        current_pax = list(Rtable['count'])[-1]
        alpha=1
        beta = (capacity-current_pax)/capacity
        scorelist = nextcluster_score(pointc, Clusterlist)
        idx = scorelist.index(max(scorelist))
        next_cluster = Clusterlist[idx]  #<-- midway destination point
        ###########additional cluster
        
        ###########additional cluster complete
        R.clusterlist = R.clusterlist + [next_cluster]
        
        Rtable = update_Rtable(Rtable, pointc.cent, next_cluster)
        
        if list(Rtable['time'])[-1] > totaltime or len(Triplist)==0:
#            Triplist = Boardinglist + Triplist
#            ##여기서 Rtable과 T의 Time 수정 필요!!! 
            ######board but not drop --> 제외
            test=0
            while(test==0):
                test=1
                totaldrop = []
                for C in R.clusterlist:
                    totaldrop = totaldrop+C.droplist
                    
                for C in R.clusterlist:
                    for T in C.triplist:
                        if T not in totaldrop:
                            C.triplist.remove(T)
                            C.count = C.count-1
                    if C.count==0:
                        R.clusterlist.remove(C)
                    else:
                        C.cent = ((sum([T.OD[0] for T in C.triplist])+sum([T.OD[2] for T in C.droplist]))/(len(C.triplist)+len(C.droplist)),(sum([T.OD[1] for T in C.triplist])+sum([T.OD[3] for T in C.droplist]))/(len(C.triplist)+len(C.droplist)))#cent update

                if list(Rtable_making(R)['count'])[-1]!=0:
                    test=0
                else: 
                    Rtablelist.append(Rtable_making(R))
#                    print(veh)
                
#            Boardinglist = []
            break
    Routelist.append(R)

    ##lastcheck
    lastC = R.clusterlist[-1]
    try:
        for T in lastC.triplist:
            Triplist.remove(T)
    except:
        pass
    try:
        for T in next_cluster.droplist:
            Boardinglist.remove(T)
            Deliveredlist.append(T)
    except:
        pass
    Triplist = Triplist + Boardinglist
    Boardinglist = []

CompuataionT = time.clock()-compT0

#####################################################################################
##preliminary result summary
##routing result summary
TotalIVT=0
Totaldirectdist = 0
for T in Deliveredlist:
    T.TT = T.t1 - T.t0
    try: TotalIVT = TotalIVT + T.IVT
    except: pass
    Totaldirectdist = distance(T.OD[:2],T.OD[2:4])
TotalTT = sum([T.TT for T in Deliveredlist])
avgTT = TotalTT/len(Deliveredlist)
avgIVT = TotalIVT/len(Deliveredlist)
servedrate = len(Deliveredlist)/demand*100
Totaldistance = sum([list(Rtable['distance'])[-1] for Rtable in Rtablelist])

for Rtable in Rtablelist:
    tmp = distance(station_o,list(Rtable['C'])[0].cent)
    for i,count in enumerate(list(Rtable['count'])):
        if count==0 and i!=(len(list(Rtable['count']))-1):
            tmp = tmp+distance(list(Rtable['C'])[i].cent,list(Rtable['C'])[i+1].cent)
TotalTransdist = Totaldistance-tmp

Totaldrivingtime = sum([list(Rtable['time'])[-1] for Rtable in Rtablelist])
TransDistRatio = TotalTransdist/Totaldistance#TransportationDistanceRatio #transportationdist/Totaldistance
avgoccupancy = sum([sum(list(Rtable['count'])) for Rtable in Rtablelist])/sum([len(Rtable) for Rtable in Rtablelist])
EffVehTransDistRatio = Totaldirectdist/Totaldistance#

col = "# of veh,demand,served %,TotalIVT,avgIVT,TotalvehTransDistRatio,EffTransDistRatio,avgoccupancy,Distance,DrivingT,ComputationT"
table = pd.DataFrame(columns=col.split(','))
data = [numofveh, demand, servedrate, TotalIVT, avgIVT, TransDistRatio, EffVehTransDistRatio, avgoccupancy, Totaldistance, Totaldrivingtime, CompuataionT]
table.loc[len(table)]=data

path = wd+'result/001_initialroute'+'.csv' 
if os.path.isfile(path):
    table.to_csv(path, index=False, mode='a', header=False)
else: table.to_csv(path, index=False, mode='a')
#            
#        #additional stop station
#
#####################################################################################
#data save
#Routelist
#Rtablelist
#Triplist
#Deliveredlist
###Triplist + Deliveredlist + Boardinglist = total demand! 


##########################################################################
savename = wd+'data/Triplist.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Triplist, f)
savename = wd+'data/Routelist.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Routelist, f)
savename = wd+'data/Deliveredlist.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Deliveredlist, f)
    
##########################################################################
data_hold = wd+'iteration_data/'+'type'+str(demand_scenario)+'_'+str(numofveh)+'_'+str(demand)+'/initialroute/'
savename = data_hold+'Triplist.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Triplist, f)
savename = data_hold+'Routelist.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Routelist, f)
savename = data_hold+'Deliveredlist.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Deliveredlist, f)
savename = data_hold+'Deliveredlist.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Deliveredlist, f)
#savename = wd+'data/Rtablelist.pickle'
#with open(savename, 'wb') as f:
#    pickle.dump(Rtablelist, f)

#    
##남은것: 이동 방향성 고려 선택
#
#servedtriplist=sum([C.triplist for C in sum([R.clusterlist for R in Routelist],[])],[])
##
##len(servedtriplist)