# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 11:05:27 2019

@author: Transmatics
"""


import os
import numpy as np
import pandas as pd
import pickle
import datetime 
import math
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans

from initialize import *
from funcs import *
import ClassDef as cl


###########################################################################
with open('data/Triplist.pickle','rb') as f:
    Triplist = pickle.load(f)    

#clusterseed 생성
Clusterlist = []
i=0
while((3*i+1)*len_link < network_size):
    j=0
    while((3*j+1)*len_link < network_size_y):
        k=0
        while((3*k+1)*walking_timelimit < totaltime):
            try:
                C = cl.Cluster(Clusterlist[-1].ID +1, (2*i+1)*len_link, (2*j+1)*len_link, (2*k+1)*walking_timelimit, 'O') #ID, x, y, t, typeofcluster
            except:
                C = cl.Cluster(0, (2*i+1)*len_link, (2*j+1)*len_link, (2*k+1)*walking_timelimit, 'O') #ID, x, y, t, typeofcluster
            Clusterlist.append(C)
            k+=1
        j+=1
    i+=1


Opointlist = [(T.OD[0], T.OD[1], T.genT) for T in Triplist]

sizecheck=1
while(sizecheck==1):
    #triplist reset
    for C in Clusterlist:
        C.triplist=[]
    #seed 생성
    clusterseed = np.array([C.cent for C in Clusterlist])
    
    #가장 가까운 cluster에 trip 배정
    kmeans = KMeans(n_clusters=len(Clusterlist), init=clusterseed, n_init=1).fit(Opointlist)
    
    #data update (cluster id, triplist)
    for i, T in enumerate(Triplist):
        T.clusterO = kmeans.labels_[i]
        for C in Clusterlist:
            if C.ID==kmeans.labels_[i]:
                C.triplist=C.triplist+[T]
    #trip이 배정되지 않은 cluster 삭제
    Clusterlist = [C for C in Clusterlist if len(C.triplist)!=0]  
    

    #####size check
    sizecheck = -1
    for C in Clusterlist:
        
        #cluster별 trip 추출
        tmptriplist=[T for T in Triplist if T.clusterO==C.ID]
        ###cluster center update
        if len(tmptriplist)!=0:
            Ox, Oy, Ot = 0,0,0
            for T in tmptriplist:
                Ox += T.OD[0]
                Oy += T.OD[1]
                Ot += T.genT
            try:
                Ox, Oy, Ot = Ox/len(tmptriplist), Oy/len(tmptriplist), Ot/len(tmptriplist)
            except:
                pass
            C.cent = (Ox, Oy, Ot)
        
        #cluster center --> grid
#        for C in Clusterlist:
            newpoint = point2grid(C.cent[:2])
            C.cent = (newpoint[0], newpoint[1], int(C.cent[2]))
        
        if len(C.triplist)<=1:
            continue   
        else:
            center = C.cent[:2]
            
            maxtimed = 0
            index=-1
            for i, T in enumerate(tmptriplist):
                tripcenter = T.OD[:2]
                #center of cluster - point 거리: walking limit 이상
                timed = (abs(center[0]-tripcenter[0]) + abs(center[1]-tripcenter[1]))/v_walk
                #or, genT difference b/w point and clustercenter > 10min
                timed = max(timed, abs(C.cent[2]-T.genT))
                if timed >walking_timelimit:
                    if timed>maxtimed:
                        index=i
                
            if index!=-1:
                #tmptriplist[index]인 T가 가장멀리떨어진 trip이다! 
                tmptriplist[index]
                C = cl.Cluster(Clusterlist[-1].ID +1, tmptriplist[index].OD[0], tmptriplist[index].OD[1], tmptriplist[index].genT, 'O') 
                Clusterlist.append(C)
#                print('updated cluster: '+str(C.ID))
                sizecheck = 1 
#    print(len(Clusterlist))

newclusterlist = []
for C in Clusterlist:    
    C.count = len(C.triplist)
    newclusterlist.append(C)
Clusterlist = newclusterlist

savename = wd+'data/Triplist.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Triplist, f)
savename = wd+'data/Clusterlist.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Clusterlist, f)

##=================================================
###저장!! 
#with open('table_trip.pickle', 'wb') as f:
#    pickle.dump(table_trip,f)
#with open('table_cluster.pickle', 'wb') as f:
#    pickle.dump(table_cluster,f)
#with open('table_tripcluster.pickle', 'wb') as f:
#    pickle.dump(table_tripcluster,f)
##-------
#    
#
#
#
#table_trip.to_csv('table_trip.csv', mode='w', index=False)
#table_cluster.to_csv('table_cluster.csv', mode='w', index=False)
#table_tripcluster.to_csv('table_tripcluster.csv', mode='w', index=False)


#count=0
#for C in Clusterlist:
#    count+=len(C.triplist)