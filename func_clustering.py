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

def clustering(Triplist, Boardinglist):
    Opointlist = [(T.OD[0], T.OD[1]) for T in Triplist]
    Dpointlist = [(T.OD[2], T.OD[3]) for T in Boardinglist]
    
    pointlist = Opointlist + Dpointlist
    
    Clusterlist = []
    
    if len(pointlist)<=8:
        for i, point in enumerate(pointlist):
            C = cl.Cluster(i, point[0], point[1], None, None) #ID, x, y, t, typeofcluster
            Clusterlist.append(C)
        
        for i, T in enumerate(Triplist):
            T.clusterO = Clusterlist[i]
            Clusterlist[i].triplist = Clusterlist[i].triplist + [T]
        for i, T in enumerate(Boardinglist):
            j=i+len(Triplist)
            T.clusterD = Clusterlist[j]
            Clusterlist[j].droplist = Clusterlist[j].droplist + [T]
        
        newclusterlist = []
        for C in Clusterlist:    
            C.count = len(C.triplist) + len(C.droplist)
            if C.count != 0:
                newclusterlist.append(C)
        Clusterlist = newclusterlist
        
        return Clusterlist, Triplist, Boardinglist
    
    
    kmeans = KMeans().fit(pointlist)
    clusteridlist = list(set(kmeans.labels_))
    clusterseed = kmeans.cluster_centers_
    for i, cid in enumerate(clusteridlist):
        C = cl.Cluster(cid, clusterseed[i][0], clusterseed[i][1], None, None) #ID, x, y, t, typeofcluster
        Clusterlist.append(C)
        
    sizecheck=1
    while(sizecheck==1):
        for C in Clusterlist:
            C.triplist = []
            C.droplist = []
        #가장 가까운 clsuter에 trip 배정
        kmeans = KMeans(n_clusters=len(Clusterlist), init=clusterseed, n_init=1).fit(pointlist)
        
        #data update (cluster id, triplist)
        for i, T in enumerate(Triplist):
            T.clusterO = Clusterlist[kmeans.labels_[i]]
            Clusterlist[kmeans.labels_[i]].triplist = Clusterlist[kmeans.labels_[i]].triplist + [T]
        for i, T in enumerate(Boardinglist):
            j=i+len(Triplist)
            T.clusterD = Clusterlist[kmeans.labels_[j]]
            Clusterlist[kmeans.labels_[j]].droplist = Clusterlist[kmeans.labels_[j]].droplist + [T]
        
        if len(kmeans.labels_) != len(list(set(kmeans.labels_))):
            for i, C in enumerate(Clusterlist):
                if i not in kmeans.labels_:
                    Clusterlist.remove(C)
        
                
        #####size check
        sizecheck = -1
        for C in Clusterlist:
            
            #cluster별 trip 추출
            tmptriplist=[T for T in Triplist if T.clusterO.ID==C.ID] 
            tmptriplist_d = [T for T in Boardinglist if T.clusterD.ID==C.ID]
            ###cluster center update
            if len(tmptriplist+tmptriplist_d)!=0:
                Ox, Oy = 0,0
                for T in tmptriplist:
                    Ox += T.OD[0]
                    Oy += T.OD[1]
                for T in tmptriplist_d:
                    Ox += T.OD[2]
                    Oy += T.OD[3]
                try:
                    Ox, Oy = Ox/len(tmptriplist+tmptriplist_d), Oy/len(tmptriplist+tmptriplist_d)
                except:
                    pass
                C.cent = (Ox, Oy)
#            #cluster center --> grid
#                newpoint = point2grid(C.cent[:2])
#                C.cent = (newpoint[0], newpoint[1])
            
            if len(C.triplist+C.droplist)<=1:
                continue   
            else:
                center = C.cent[:2]
                
                maxtimed = 0
                index=-1
                for i, T in enumerate(tmptriplist+tmptriplist_d):
                    tripcenter = T.OD[:2]
                    #center of cluster - point 거리: walking limit 이상
                    timed = (abs(center[0]-tripcenter[0]) + abs(center[1]-tripcenter[1]))/v_walk
                    if timed >walking_timelimit:
                        if timed>maxtimed:
                            maxtimed = timed
                            index=i
                    
                if index!=-1:
                    tmp_totaltriplist = tmptriplist+tmptriplist_d
                    #tmptriplist[index]인 T가 가장멀리떨어진 trip이다! 
                    C = cl.Cluster(Clusterlist[-1].ID +1, tmp_totaltriplist[index].OD[0], tmp_totaltriplist[index].OD[1], None, None) 
                    Clusterlist.append(C)
                    clusterseed = np.array([C.cent[:2] for C in Clusterlist])
                    sizecheck = 1 
    
    
    newclusterlist = []
    for C in Clusterlist:    
        C.count = len(C.triplist) + len(C.droplist)
        if C.count != 0:
            newclusterlist.append(C)
    Clusterlist = newclusterlist
#    
    
    return Clusterlist, Triplist, Boardinglist

