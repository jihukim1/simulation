# -*- coding: utf-8 -*-
"""
Created on Wed May 13 13:32:47 2020

@author: JIHU
"""

#필요한 것
#isolated station condition filtering 
#station change --> cost calculate


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
from routing import *
import ClassDef as cl

compT0 = time.clock()
###########################################################################
with open('data/Triplist.pickle','rb') as f:
    Triplist = pickle.load(f)  
with open('data/Routelist.pickle','rb') as f:
    Routelist = pickle.load(f)  
with open('data/Deliveredlist.pickle','rb') as f:
    Deliveredlist = pickle.load(f)  
Rtablelist = []
for R in Routelist:
    Rtablelist.append(Rtable_making(R))
###########################################################################
    
def IVT(R):
    #average in-vehicle travel time for the Route
    ivt = 0 
    Rtable = Rtable_making(R)
    for i in range(len(Rtable)):
        C = Rtable['C'][i]
        if len(C.triplist)!=0:
            for T in C.triplist:
                for j in range(len(Rtable)):
                    C1 = Rtable['C'][j]
                    if T in C1.droplist:
                        ivt += Rtable['time'][j]-Rtable['time'][i]
    return ivt

def Rcost(R):
    Rtable = Rtable_making(R)
    TT = list(Rtable['time'])[-1]
    Tlist = []
    for C in R.clusterlist:
        Tlist = Tlist + C.droplist
    ivtsum = sum([T.IVT for T in Tlist] )
    
    Rcost = TT + ivtsum
    
    return Rcost

def Isolist(Routelist):
    Isolist = [] #list of triplist
    for R in Routelist:
        for i,C in enumerate(R.clusterlist):
            tmplist = C.droplist
            if len(tmplist)!=0:
                for j,C1 in enumerate(R.clusterlist):
                    if j<i and (set(tmplist)==set(C1.triplist)): #탑승=하차 (pick/drop을 함께 변경 가능)
                        Isolist.append(tmplist)
    return Isolist

def Detour(iso,Rtablelist): #
    detour = 0
    for i,Rtable in enumerate(Rtablelist):
        Clist = list(Rtable['C'])
        if iso[0].clusterO in Clist:
            routenum = i 
            for j,C in enumerate(Clist):
                for k,C1 in enumerate(Clist):
                    if j<k:
                        if set(C.triplist)==set(C1.droplist):
                            clusternum_d = k
                            clusternum_o = j
                            idx = Clist.index(iso[0].clusterO)
                            detour = detour + distance(Clist[idx-1].cent, Clist[idx].cent)
                            try:
                                detour = detour + distance(Clist[idx].cent, Clist[idx+1].cent)
                                detour = detour - distance(Clist[idx-1].cent, Clist[idx+1].cent)
                            except: pass
    #routenum i, clusternum j, detour score
    return routenum, clusternum_o, clusternum_d, detour 

def Isogroupselect(isolist, Routelist):
    Rtablelist = []
    for R in Routelist:
        Rtablelist.append(Rtable_making(R))
    #inefficient group selection
    alpha = 0.5
    ###########################
    ineffscore = 0
    for i, iso in enumerate(isolist):
        IVT = sum([T.IVT for T in iso])
        routenum, clusternum_o, clusternum_d, detour = Detour(iso,Rtablelist)
        ##detour cost calculate
        inefficiency = IVT + detour ###### 수정 필요 @@@
        ineffscore = max(ineffscore, inefficiency)
        if ineffscore == inefficiency:
            routeN, clusteroN, clusterdN = routenum, clusternum_o, clusternum_d
#            print(clusternum_o)
            ineffidx = copy.deepcopy(i)
    Isogroup = isolist[ineffidx]
    return Isogroup, routeN, clusteroN, clusterdN 

def increase_dist(R,n,C): #거리증가량 #해당R, 삽입할C, 위치n
    increase_dist = 0
    try:increase_dist = -distance(R.clusterlist[n].cent,R.clusterlist[n+1].cent)
    except:pass
    increase_dist = increase_dist + distance(R.clusterlist[n].cent,C.cent)
    try:increase_dist = increase_dist + distance(C.cent,R.clusterlist[n+1].cent)
    except:pass
    return increase_dist


def Rtablelist_making(Routelist):
    Rtablelist = []
    for R in Routelist:
        Rtablelist.append(Rtable_making(R))
    return Rtablelist

for count in range(int(demand/2)):
    ###########################################################################
    #isolated trip clusters filtering
    #isolated group list
    #Ocluster와 Dcluster가 순수한 그룹으로 짝지어진?
    ##droplist group이 같은 cluster에서 탑승했고, 다른 유저가 없는 경우! 
    isolist = Isolist(Routelist)
    #Group_isolated
    ###########################################################################
    #inefficient isolated trip group select
    ##해당 pair 전후로 detour가 큰 것
    Isogroup, routeN, clusteroN, clusterdN = Isogroupselect(isolist, Routelist)
    ###########################################################################
    #cost 재계산
    ##isocluster 빼고 rtable 새로 생성
    isogroup = copy.deepcopy(Routelist[routeN].clusterlist[clusteroN].triplist)
    tmp_clusterO = Routelist[routeN].clusterlist[clusteroN]
    tmp_clusterD = Routelist[routeN].clusterlist[clusterdN]
    Routelist[routeN].clusterlist.remove(tmp_clusterO)
    Routelist[routeN].clusterlist.remove(tmp_clusterD)
    Rtablelist = Rtablelist_making(Routelist)
    
    #isogroup으로 생성된 cluster가 들어갈 수 있는 Rtable 공간 찾기
    ##isocluster_o와 가까운 cluster 찾기
    ##있다면 이후에 isocluster_d와 가까운 cluster 찾기
    ###o와 가까운 cluster, d와 가까운 cluster를 찾고 그 합이 가장 작은 위치 결정
    dist = 10**10
    for n, R in enumerate(Routelist):
        for i,C in enumerate(R.clusterlist):
            for j,C in enumerate(R.clusterlist):
                if j>i:
                    tmp_dist = increase_dist(R,i,tmp_clusterO)
                    tmp_dist = tmp_dist + increase_dist(R,j,tmp_clusterD)
                    dist = min(tmp_dist, dist)
                    if dist == tmp_dist:
                        idx_o = i
                        idx_d = j
                        routenum = n
    try:
        Routelist[routenum].clusterlist.insert(idx_d+1,tmp_clusterD)
        Routelist[routenum].clusterlist.insert(idx_o+1,tmp_clusterO)
    #    Routelist = tmp_Routelist
    except:
        Routelist[routeN].clusterlist.insert(clusterdN,tmp_clusterD)
        Routelist[routeN].clusterlist.insert(clusteroN,tmp_clusterO)


############################여기까지 셔플과정 ########################
############################여기부터 insert과정 ######################
#Deliveredlist = []
#for R in Routelist:
#    for C in R.clusterlist:
#        Deliveredlist = Deliveredlist + C.triplist

###Triplist에 있는 trip 중 insertion이 가능한 것을 Route에 삽입
for n,T in enumerate(Triplist):
    #1cluster 1trip인 cluster 생성
    C1 = cl.Cluster(2*n, T.OD[0], T.OD[1], None, None)
    C2 = cl.Cluster(2*n + 1,T.OD[2],T.OD[3],None,None)
    dist=10**10
    Rtablelist = Rtablelist_making(Routelist)
    for k, R in enumerate(Routelist):
        if list(Rtablelist[k]['time'])[-1]>totaltime: continue
        #Tinsertion_limit 3min
        #가장 insertion cost가 작은 route와 position을 찾기
        for i,C in enumerate(R.clusterlist):
            for j,C in enumerate(R.clusterlist):
                if j>i:
                    tmp_dist = increase_dist(R,i,C1)
                    tmp_dist = tmp_dist + increase_dist(R,j,C2)
                    if tmp_dist<0:
                        break
                    dist = min(tmp_dist, dist)
                    if dist == tmp_dist:
                        idx_o = i
                        idx_d = j
                        routenum = k
    #limit 만족 확인
    if dist/v_avg < Tinsertion_limit:
        T.clusterO = C1
        T.clusterD = C2
        C1.triplist=[T]
        C2.droplist=[T]
        Triplist.remove(T)
        Deliveredlist.append(T)
        #routelist update
        Routelist[routenum].clusterlist.insert(idx_o+1, C1)
        Routelist[routenum].clusterlist.insert(idx_d+1, C2)

Rtablelist = Rtablelist_making(Routelist)

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
data_hold = wd+'iteration_data/'+'type'+str(demand_scenario)+'_'+str(numofveh)+'_'+str(demand)+'/improvement/'
savename = data_hold+'Triplist.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Triplist, f)
savename = data_hold+'Routelist.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Routelist, f)
savename = data_hold+'Deliveredlist.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Deliveredlist, f)
#savename = wd+'data/Rtablelist.pickle'
#with open(savename, 'wb') as f:
#    pickle.dump(Rtablelist, f)



CompuataionT = time.clock()-compT0
##### shuffle 반복 구현 (demand의 50%)
##### result 뽑기

#####################################################################################
##result summary
TotalIVT=0
Totaldirectdist = 0
for T in Deliveredlist:
    T.TT = T.t1 - T.t0
    try:TotalIVT = TotalIVT + T.IVT
    except:pass
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

path = wd+'result/002_improvement'+'.csv' 
if os.path.isfile(path):
    table.to_csv(path, index=False, mode='a', header=False)
else: table.to_csv(path, index=False, mode='a')
#            
#        #additional stop station
#
#####################################################################################













