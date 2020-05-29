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
from mip import Model, xsum, maximize, BINARY, INTEGER, CONTINUOUS

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
    return n,P,D,PD,N,t,q,c

def makeData(data): #x,v,B,Q
    n,P,D,PD,N,t,q,c = makeSet(data)
    x = [[(i,j) for j in N] for i in N]
    x = sum(x,[])
    t = [[1/6 + distance(nodelist[i], nodelist[j])/v_avg for j in N] for i in N]#travel time b/w each node
    t = sum(t,[])
    x = list(zip(x,t)) # ((x,y),t) 
    v = [(i,i,i) for i in N] 
    B = [i for i in N] 
    Q = [i for i in N] 
    return x+v+B+Q

def makeDvar(individual):
    x = individual[:(4* (n+1)**2)]
    v = individual[(4* (n+1)**2):(4* (n+1)**2)+(2*n+2)]
    B = individual[(4* (n+1)**2)+(2*n+2):(4* (n+1)**2)+(2*n+2)*2]
    Q = individual[(4* (n+1)**2)+(2*n+2)*2:]
    
    tmp = int(np.sqrt(len(x)))
    x=[x[i:i+tmp] for i in range(0,len(x),tmp)]
    
    return x,v,B,Q

############################################################
n,P,D,PD,N,t,q,c = makeSet(Triplist)
data = makeData(Triplist)
ga = pyeasyga.GeneticAlgorithm(data, 
                               mutation_probability=0,
                               maximise_fitness=False)

def create_individual(data): #individual
    global Triplist
    global capacity
    global numofveh
    n = len(Triplist)
    individual_x = [random.randint(0, 1) for _ in range(4* (n+1)**2)]
    individual_v = [random.randint(0, numofveh) for _ in range(2*n+2)]
    individual_B = [random.random() for _ in range(2*n+2)]
    individual_Q = [random.randint(0, capacity) for _ in range(2*n+2)]
    return individual_x + individual_v + individual_B + individual_Q
ga.create_individual = create_individual

#def crossover

#def mutate

#def selection

def fitness(individual, data):
    global Triplist
    global capacity
    n,P,D,PD,N,t,q,c = makeSet(Triplist)
    #unchanged values: n,P,D,PD,N,t,q,c
    #changed values: x,v,B,Q
    x,v,B,Q = makeDvar(individual)

    while (True):
        condition = 1
        # route num / flow
        if not (sum(np.array([x[0][j] for j in N]).flatten())==numofveh):condition = 0
        if not (sum(np.array([x[i][N[-1]] for i in N]).flatten())==numofveh):condition = 0
        for j in PD:
            if not ( sum(np.array([x[i][j] for i in N]).flatten())<=1):condition = 0
        for i in PD:
            if not ( sum(np.array([x[i][j] for j in N]).flatten())<=1):condition = 0
        for i in PD:
            if not ( sum(np.array([x[i][j] for j in N]).flatten()) == sum(np.array([x[j][i] for j in N]).flatten())):condition = 0
        # timelimit
        for product1 in list(product(N,N)):
            (i,j) = product1
            if not ( B[j] >= B[i] + t[i][j] - 10000*(1-x[i][j])):condition = 0
        for i in P:
            if not ( B[n+i] >= B[i] + t[i][n+i]):condition = 0
        #capacitylimit
        for product1 in list(product(N,N)):
            (i,j) = product1
            if not ( Q[j] >= Q[i] + q[j] - 100*(1-x[i][j])):condition = 0
        for i in N:
            if not ( q[i] <= Q[i]):condition = 0
            if not ( capacity + q[i] >= Q[i]):condition = 0
        #veh id
        for i in P:
            if not ( v[n+i] == v[i]):condition = 0
            if not ( v[i] <= numofveh):condition = 0
        for j in PD:
            if not ( v[j] >= j*x[0][j]):condition = 0
            if not ( v[j] <= j * x[0][j] - n*(x[0][j]-1)):condition = 0
        for product1 in list(product(PD,PD)):
            (i,j) = product1
            if not ( v[j] >= v[i] + n*(x[i][j]-1)):condition = 0
            if not ( v[j] <= v[i] + n * (1-x[i][j])):condition = 0
        
        if condition==1:
            fitness = sum([c[i][j] * x[i][j] for i in N for j in N])
        else: fitness =0
        
        if fitness!=0:
            break
    
    return fitness


ga.fitness_function = fitness
ga.run()
CompuataionT = time.clock()-compT0

sol = ga.best_individual()


