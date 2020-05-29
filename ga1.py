# -*- coding: utf-8 -*-
"""
Created on Wed May 27 16:22:48 2020

@author: JIHU
"""
from initialize import *
from pyeasyga import pyeasyga
import random
import numpy as np
import pickle
from itertools import product
#from mip import Model, xsum, maximize, BINARY, INTEGER, CONTINUOUS

import time

compT0 = time.clock()


def distance(pointc, point): ##이동거리
    dist = abs(pointc[0]-point[0])+abs(pointc[1]-point[1])
    return dist

with open('data/Triplist_original.pickle','rb') as f:
    Triplist = pickle.load(f)    
Triplist = Triplist[:10]

############################################################


def makeNodelist(data):
    global station_o
    global station_d
    ODlist = [T.OD for T in data]
    Plist = [(OD[0],OD[1]) for OD in ODlist]
    Dlist = [(OD[2],OD[3]) for OD in ODlist]
    nodelist = [station_o]+Plist+Dlist+[station_d]
    return nodelist

def makeSet(data):
    global v_avg
    nodelist = makeNodelist(data)
    n = len(data)
    P = list(range(1,n+1))
    D = list(range(n+1,2*n+1))
    PD = P+D
    N = [0]+PD+[2*n+1]
    t = [[1/6 + distance(nodelist[i], nodelist[j])/v_avg for j in N] for i in N]#travel time b/w each node
    q = [0]+[1]*n+[-1]*n+[0]#load at node i, pickup 1 delivery -1
    c = [[1 if ((i in P) and (j in D)) else 0 for j in N] for i in N]
    return nodelist,n,P,D,PD,N,t,q,c

def makeData(data): #x,v,B,Q
    nodelist,n,P,D,PD,N,t,q,c = makeSet(data)
    x = [[(i,j) for j in N] for i in N]
    x = sum(x,[])
    t = [[1/6 + distance(nodelist[i], nodelist[j])/v_avg for j in N] for i in N]#travel time b/w each node
    t = sum(t,[])
    x = list(zip(x,t)) # ((x,y),t) 
#    v = [(i,i,i) for i in PD] 
#    B = [i for i in N] 
#    Q = [i for i in N] 
    return x#+v+B+Q

def makeDvar(individual):
#    nodelist,n,P,D,PD,N,t,q,c = makeSet(data)
    x = individual[:(4* (n+1)**2)]
#    v = individual[(4* (n+1)**2):(4* (n+1)**2)+len(N)]
#    B = individual[(4* (n+1)**2)+len(N):(4* (n+1)**2)+len(N)*2]
#    Q = individual[(4* (n+1)**2)+len(N)*2:]
    
    tmp = int(np.sqrt(len(x)))
    x=[x[i:i+tmp] for i in range(0,len(x),tmp)]
    
    return x#,v,B,Q

def timecheck(route):
    global Triplist
    nodelist,n,P,D,PD,N,t,q,c = makeSet(Triplist)
    
    timem = 0
    for r in route:
        time = 0
        r=[0]+r+[N[-1]]
        for i in range(len(r)-1):
            time += t[r[i]][r[i+1]]
        timem = max(timem, time)
    return timem

def calculate():
    global wd
    nodelist,n,P,D,PD,N,t,q,c = makeSet(Triplist)
    savename = wd+'/garoute.pickle'
    with open(savename,'rb') as f:
        route = pickle.load(f) 
    
    B = [0]*len(N)
    Q = [0]*len(N)
    for r in route:
        for i in range(len(r)-1):
            B[r[i+1]] = B[r[i]]+t[r[i]][r[i+1]]
            Q[r[i+1]] = Q[r[i]]+q[r[i+1]]
    return B,Q
    
############################################################
nodelist,n,P,D,PD,N,t,q,c = makeSet(Triplist)
data = makeData(Triplist)
ga = pyeasyga.GeneticAlgorithm(data, 
                               mutation_probability=0.2,
                               generations=100,
                               maximise_fitness=True)

def create_individual(data): #individual
    global Triplist
    global capacity
    global numofveh
    global totaltime
    nodelist,n,P,D,PD,N,t,q,c = makeSet(Triplist)
    
    ### route decision
    route = [[]]*numofveh
    x = [[0 for j in N] for i in N]
    B = [0]*len(N)
    Q = [0]*len(N)
    
    P_tmp = list(range(1,n+1))
    
    while(True):
#        print('check create_individual')
        idx = random.choice(P_tmp) #trip선택
        P_tmp.remove(idx)
        idx_route = random.choice(range(len(route)))#route 선택
        if len(route[idx_route])==0:
            route[idx_route].append(idx)
            route[idx_route].append(n+idx)
        else:
            l = route[idx_route]
            l = [random.choice(range(len(l))),random.choice(range(len(l)))]
            l.sort()
            route[idx_route] = route[idx_route][:l[0]]+[idx]+route[idx_route][l[0]:l[1]]+[n+idx]+route[idx_route][l[1]:]
        if timecheck(route)>totaltime or len(P_tmp)==0 : break
    
    for i,r in enumerate(route):
        route[i] = [0]+r+[N[-1]]
    
    #### x value / time / occ / v setting
    global wd
    for r in route:
        for i in range(len(r)-1):
            x[r[i]][r[i+1]]=1
            B[r[i+1]] = B[r[i]]+t[r[i]][r[i+1]]
            Q[r[i+1]] = Q[r[i]]+q[r[i+1]]
            
    savename = wd+'/garoute.pickle'
    with open(savename, 'wb') as f:
        pickle.dump(route, f)
        
    v=[0]*(2*n+2)
        
    individual_v = v
    individual_B = B
    individual_x = list(np.array(x).flatten())
    individual_Q = [random.randint(0, capacity) for _ in range(2*n+2)]
    return individual_x #+ individual_v + individual_B + individual_Q #len: 548
ga.create_individual = create_individual
#individual = create_individual(data)

def fitness(individual, data):
    global Triplist
    global capacity
    nodelist,n,P,D,PD,N,t,q,c = makeSet(Triplist)
    #unchanged values: n,P,D,PD,N,t,q,c
    #changed values: x,v,B,Q
    x = makeDvar(individual)#,v,B,Q
    B,Q = calculate()
    condition = 1
    # route num / flow
    for j in PD:
        if not ( sum(np.array([x[i][j] for i in N]).flatten())<=1):
            condition = 0
#                print('flow in error')
#                print(i)
#                print(j)
#            if not ( v[j] >= j*x[0][j]):condition = 0
#            if not ( v[j] <= j * x[0][j] - n*(x[0][j]-1)):condition = 0
    for i in PD:
        if not ( sum(np.array([x[i][j] for j in N]).flatten())<=1):
            condition = 0
#                print('flow out error')
    # timelimit
#        for product1 in list(product(N,N)):
#            (i,j) = product1
#            if not ( Q[j] >= Q[i] + q[j] - 100*(1-x[i][j])):
#                condition = 0
#                print('capacity  error1')
#        for i in P:
#            pass
#            if not ( v[n+i] == v[i]):condition = 0
#            if not ( v[i] <= numofveh):condition = 0
    #capacitylimit
    for i in N:
#            if not ( q[i] <= Q[i]):
#                condition = 0
#                print('capacity  error2')
        if not ( capacity >= Q[i]):
            condition = 0
#                print('capacity  error3')
    #veh id
#        for product1 in list(product(PD,PD)):
#            (i,j) = product1
#            if not ( v[j] >= v[i] + n*(x[i][j]-1)):condition = 0
#            if not ( v[j] <= v[i] + n * (1-x[i][j])):condition = 0
    
    if condition==1:
        fitness1 = sum([c[i][j] * x[i][j] for i in N for j in N])
    else: fitness1 =0
    
    return fitness1


ga.fitness_function = fitness
ga.run()
CompuataionT = time.clock()-compT0
print(CompuataionT)

sol = ga.best_individual()
print(sol[0])

#B,Q
