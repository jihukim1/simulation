# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 04:10:25 2020

@author: JIHU
"""

import os
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import copy

from sklearn.cluster import KMeans
from kneed import KneeLocator

from initialize import *
from funcs import *
from func_clustering import *
import ClassDef as cl



 
with open('data/Routelist.pickle', 'rb') as f:
    Routelist = pickle.load(f)
#with open('data/Rtablelist.pickle', 'rb') as f:
#    Rtablelist = pickle.load(f)
    
path = wd+'result'
try: 
    shutil.rmtree(path)
    time.sleep(2)
except: pass

try: os.mkdir(path)
except: pass

####routelist csv files
Rtablelist=[]
for i,R in enumerate(Routelist):
    colname = "x,y,t,t_move,diff,clusterID,onboard,count,pickup,dropoff"
    Routetable = pd.DataFrame(columns=colname.split(','))
    onboard=[]
    droplist = sum([C.droplist for C in R.clusterlist],[])
    for C in R.clusterlist:
        onboard = onboard+[T.ID for T in C.triplist if T in droplist]
        for T in C.droplist:
            if T.ID in onboard:
                onboard.remove(T.ID)
        data = [C.cent[0],C.cent[1],C.cent[2],None,None,
                C.ID, onboard, len(onboard),
                [T.ID for T in C.triplist if T in droplist], [T.ID for T in C.droplist]]
        Routetable.loc[len(Routetable)] = data
    Routetable['t_move'][1:] = [tt((Routetable.x[i],Routetable.y[i]),(Routetable.x[i+1],Routetable.y[i+1]))+Routetable.t[i] for i in range(len(Routetable)-1)]
    Routetable['diff'][1:] = [Routetable.t[i+1] - Routetable.t_move[i+1] for i in range(len(Routetable)-1)]
    path = wd+'result/Routeresult_'+str(i+1)+'.csv'   
    Routetable.to_csv(path, index=False)
    Rtablelist.append(Routetable)
#
savename = wd+'data/Rtablelist.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Rtablelist, f)

#####routelist route graphs
#for i,R in enumerate(Routelist):
#    plt.figure()
#    centlist = [station_o] + [C.cent for C in R.clusterlist] + [station_d]
#    x = [e[0] for e in centlist]
#    y = [e[1] for e in centlist]
#    t = [R.clusterlist[0].cent[2]-tt(R.clusterlist[0].cent, station_o)]
#    t = t+[C.cent[2] for C in R.clusterlist]
#    t = t+[R.clusterlist[-1].cent[2]+tt(R.clusterlist[0].cent, station_d)]
#    plt.axis([0,network_size,0,network_size_y])
#    plt.plot(x,y)
#    for j in range(len(x)):
#        plt.text(x[j], y[j], str(t[j]))
#    path = wd+'result/graph_'+str(i+1)+'.png'  
#    plt.savefig(path, dpi=300)
    


####routelist route graphs
for i,R in enumerate(Routelist):
    
    fig = plt.figure(figsize=(20,5))
    ax2 = fig.add_subplot(121)
    ax3 = fig.add_subplot(122,projection='3d')
    ax2.axis([0,network_size,0,network_size_y])
    ax3.set_xlim(0, totaltime )
    ax3.set_ylim(0, network_size )
    ax3.set_zlim(0, network_size_y )
    
    #route plot
    centlist = gridcentlist4plot(R)
    x = [e[0] for e in centlist] 
    x = x + [x[-1]] + [station_d[0]]
    y = [e[1] for e in centlist] 
    y = y + [station_d[1]] + [station_d[1]]
    t = [R.clusterlist[0].cent[2]-tt(R.clusterlist[0].cent, station_o)]
    t = t+[C[2] for C in centlist[1:]] 
    t = t + [t[-1]+ tt((x[-3],y[-3]),(x[-2],y[-2]))] + [t[-1] + tt(R.clusterlist[-1].cent, station_d)]
    c = list(Rtablelist[i]['count'])
    c = sum([[e,e] for e in c],[])
    c = [0] + c + [0]
#    t = t+[R.clusterlist[-1].cent[2]+tt(R.clusterlist[0].cent, station_d)]
    ax3.plot(t,x,y)
    ax3.set_xlabel('t')
    ax3.set_ylabel('x')
    ax3.set_zlabel('y')
#    plt.show()
    
#    cmap = plt.cm.Blues
    cmap = [plt.cm.Blues, plt.cm.Reds, plt.cm.Greens,
            plt.cm.Purples, plt.cm.Greys, plt.cm.Oranges]
    
    for j in range(len(x)-1):
        ax2.plot(x[j:j+2], y[j:j+2], linewidth=c[j]+1, c=cmap[i]((j+4)/(len(x)+5)))
        
#    ax2.plot(x,y, linewidth=c)
#    ax2.plot(x,y)
    ax2.set_xlabel('x')
    ax2.set_ylabel('y')
    
    #passedcluster plot
    tmpClist = [C for C in R.clusterlist]
    xp = [C.cent[0] for C in tmpClist]
    yp = [C.cent[1] for C in tmpClist]
    tp = [C.cent[2] for C in tmpClist]
    ax3.scatter(tp,xp,yp, c='black')
    ax2.scatter(xp,yp, c='black')
    
    for j in range(len(xp)):
        ax2.text(xp[j], yp[j], '%10.1f'%tp[j])
#    l = os.listdir(graphfolder)
    path = wd+'result/graph3d_'+str(i+1)+'.png' 
    plt.savefig(path, dpi=300)
    
    
    fig2 = plt.figure(figsize=(10,5))
    ax22 = fig2.add_subplot(111)
    ax22.axis([0,network_size,0,network_size_y])
    for j in range(len(x)-1):
        ax22.plot(x[j:j+2], y[j:j+2], linewidth=c[j]+1, c=cmap[i]((j+4)/(len(x)+5)))
    ax22.set_xlabel('x')
    ax22.set_ylabel('y')    
    ax22.scatter(xp,yp, c='black')
    for j in range(len(xp)):
        ax22.text(xp[j], yp[j], '%10.1f'%tp[j])
    path = wd+'result/graph_'+str(i+1)+'.png' 
    plt.savefig(path, dpi=300)
    

#all route graph
fig = plt.figure(figsize=(10,5))
ax2 = fig.add_subplot(111)
ax2.axis([0,network_size,0,network_size_y])
for i,R in enumerate(Routelist):
    centlist = gridcentlist4plot(R)
    x = [e[0] for e in centlist] 
    x = x + [x[-1]] + [station_d[0]]
    y = [e[1] for e in centlist] 
    y = y + [station_d[1]] + [station_d[1]]
    t = [R.clusterlist[0].cent[2]-tt(R.clusterlist[0].cent, station_o)]
    t = t+[C[2] for C in centlist[1:]] 
    t = t + [t[-1]+ tt((x[-3],y[-3]),(x[-2],y[-2]))] + [t[-1] + tt(R.clusterlist[-1].cent, station_d)]
    c = list(Rtablelist[i]['count'])
    c = sum([[e,e] for e in c],[])
    c = [0] + c + [0]
    cmap = [plt.cm.Blues, plt.cm.Reds, plt.cm.Greens,
            plt.cm.Purples, plt.cm.Greys, plt.cm.Oranges]
    for j in range(len(x)-1):
        ax2.plot(x[j:j+2], y[j:j+2], c=cmap[i]((j+4)/(len(x)+5)))
        
#    ax2.plot(x,y, linewidth=c)
#    ax2.plot(x,y)
    ax2.set_xlabel('x')
    ax2.set_ylabel('y')
    
    path = wd+'result/graph_total'+'.png' 
    plt.savefig(path, dpi=300)


    
#### result summary
#차량 출발시각/운행시간/도착시각
#운행 승객 수
servelist = []
for R in Routelist:
    for C in R.clusterlist:
        
        servelist = servelist+C.droplist
        servenum = len(servelist)
#TRIP 별 출발/도착/tt/TAXI_T와의 차이/
col = "genT,deptT,arivT,TT,taxiT,diff,maxT,ratio(TT/maxT)"
table = pd.DataFrame(columns=col.split(','))
for T in servelist:
    data = [T.genT, T.deptT, T.arivT, T.TT, T.taxiT, T.TT-T.taxiT, T.maxarivT, T.TT/T.maxarivT]
    table.loc[len(table)] = data
#
path = wd+'result/Tripresult'+'.csv'   
table.to_csv(path, index=False)






