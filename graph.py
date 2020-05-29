# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 13:28:29 2020

@author: JIHU
"""
#
import os
import numpy as np
import pandas as pd
import pickle
import math
import matplotlib.pyplot as plt

from initialize import *


wd = os.getcwd()

try:
    os.mkdir(wd+'/graph')
except:
    pass


with open('data/Triplist.pickle','rb') as f:
    Triplist = pickle.load(f)    
with open('data/Clusterlist.pickle','rb') as f:
    Clusterlist = pickle.load(f)    
    
#trip plot
X = [T.OD[0] for T in Triplist]
Y = [T.OD[1] for T in Triplist]
#T = [T.genT for T in Triplist]
plt.scatter(X,Y,s=10,c='black')

plt.title("trip plot")
plt.xlim([-100,network_size+100])
plt.ylim([-100,network_size_y+100])
plt.xticks(np.arange(0,network_size+1,len_link))
plt.yticks(np.arange(0,network_size_y+1,len_link))
plt.grid(True)

fig = plt.gcf()

fig.set_size_inches(network_size/network_size*10, network_size_y/network_size*10)
filename = wd+'/graph'+'/trip.png'
fig.savefig(filename, dpi=350)
plt.close()


#trip plot _ consider genT
X = [T.OD[0] for T in Triplist]
Y = [T.OD[1] for T in Triplist]
T = [T.genT for T in Triplist]
import matplotlib.cm as cm
plt.scatter(X, Y, c= T, cmap=cm.RdGy)

plt.title("trip plot - genT(red-grey)")
plt.xlim([-100,network_size+100])
plt.ylim([-100,network_size_y+100])
plt.xticks(np.arange(0,network_size+1,len_link))
plt.yticks(np.arange(0,network_size_y+1,len_link))
plt.grid(True)

fig = plt.gcf()

fig.set_size_inches(network_size/network_size*10, network_size_y/network_size*10)
filename = wd+'/graph'+'/trip_genT.png'
fig.savefig(filename, dpi=350)
plt.close()




#trip plot - cluster result
#10개씩~ 
C0 = [T.clusterO for T in Triplist]
C0 = list(set(C0))
C0.sort()
num = int((len(C0)-len(C0)%10)/10) +1

for i in range(num):
    cluster = C0[i*10:(i+1)*10]
    tmpTriplist = [T for T in Triplist if T.clusterO in cluster]
    
    X = [T.OD[0] for T in tmpTriplist]
    Y = [T.OD[1] for T in tmpTriplist]  
    C = [T.clusterO for T in tmpTriplist]
    
    import matplotlib.cm as cm
    plt.scatter(X, Y, c= C, cmap=cm.tab10)
    
    plt.title("trip - cluster")
    plt.xlim([-100,network_size+100])
    plt.ylim([-100,network_size_y+100])
    plt.xticks(np.arange(0,network_size+1,len_link))
    plt.yticks(np.arange(0,network_size_y+1,len_link))
    plt.grid(True)
    
    fig = plt.gcf()
    fig.set_size_inches(network_size/network_size*10, network_size_y/network_size*10)
    
    filename = wd+'/graph'+'/trip_cluster_'+str(i+1)+'-'+str(num)+'.png'
    fig.savefig(filename, dpi=350)
    plt.close()


##########################################################
#cluster 간격 표 생성
df = pd.DataFrame(columns='TripID,dist2cent,walkingtime'.split(','))
distlist = []
wtlist = []
for T in Triplist:
    C = [C for C in Clusterlist if C.ID==T.clusterO][0]
    distance = abs(T.OD[0]-C.cent[0]) + abs(T.OD[1]-C.cent[1])
    walkingtime = distance / v_walk
    distlist.append(distance)
    wtlist.append(walkingtime)

df.TripID = [T.ID for T in Triplist]
df.dist2cent = distlist
df.walkingtime = wtlist

filename = wd+'/graph'+'/dist_table.csv'
df.to_csv(filename, mode='w', index=False)


