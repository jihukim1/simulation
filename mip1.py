# -*- coding: utf-8 -*-
"""
Created on Wed May 27 16:22:48 2020

@author: JIHU
"""
from initialize import *
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
#trip data excel for cplex
ODlist = [T.OD for T in Triplist]
Plist = [(OD[0],OD[1]) for OD in ODlist]
Dlist = [(OD[2],OD[3]) for OD in ODlist]
nodelist = [station_o]+Plist+Dlist+[station_d]
############################################################

#data
n = len(Triplist)
P = list(range(1,n+1))
D = list(range(n+1,2*n+1))
PD = P+D
N = [0]+PD+[2*n+1]
t = [[1/6 + distance(nodelist[i], nodelist[j])/v_avg for j in N] for i in N]#travel time b/w each node
q = [0]+[1]*n+[-1]*n+[0]#load at node i, pickup 1 delivery -1
c = [[1 if ((i in P) and (j in D))
      else 0 for j in N] for i in N]

#model
model = Model()

#binary variables
##arc b/w each nodes
x = [[model.add_var('x({},{})'.format(i,j), var_type = BINARY)
      for j in N] for i in N]
#vehicle variable
v = [model.add_var('v({})'.format(i), var_type = INTEGER, lb=0, ub=numofveh) for i in N]
#time that veh start serving at node i 
B = [model.add_var('B({})'.format(i), var_type = CONTINUOUS, lb=0, ub=totaltime) for i in N]  
#veh load (boarding count)
Q = [model.add_var('Q({})'.format(i), var_type = INTEGER, lb=0, ub=capacity) for i in N] 


#objrctive function: maximize the serve rate
model.objective = maximize(xsum(c[i][j] * x[i][j] for i in N for j in N))

#constraint
model += xsum(x[0][j] for j in N) == numofveh
model += xsum(x[i][N[-1]] for i in N) == numofveh
#constraint: flow in
for j in PD:
    model += xsum(x[i][j] for i in N) <= 1
#constraint: flow out
for i in PD:
    model += xsum(x[i][j] for j in N) <= 1
#constraint: flow
for i in PD:
    model += xsum(x[i][j] for j in N) - xsum(x[j][i] for j in N) == 0
#constraint: timelimit1
from itertools import product
for product1 in list(product(N,N)):
    (i,j) = product1
    model += B[j] >= B[i] + t[i][j] - 10000*(1-x[i][j])
#constraint: timelimit2
for i in P:
    model += B[n+i] >= B[i] + t[i][n+i]
#constraint: capacitylimit1
for product1 in list(product(N,N)):
    (i,j) = product1
    model += Q[j] >= Q[i] + q[j] - 100*(1-x[i][j])
#constraint: capacitylimit2
for i in N:
    model += q[i] <= Q[i]
    model += capacity + q[i] >= Q[i]
#constraint: veh id
for i in P:
    model += v[n+i] == v[i]
    model += v[i] <= numofveh
#constraint: veh limit1
for j in PD:
    model += v[j] >= j*x[0][j]
    model += v[j] <= j * x[0][j] - n*(x[0][j]-1)
#constraint: veh limit3
for product1 in list(product(PD,PD)):
    (i,j) = product1
    model += v[j] >= v[i] + n*(x[i][j]-1)
    model += v[j] <= v[i] + n * (1-x[i][j])


#optimizing
model.optimize()

CompuataionT = time.clock()-compT0


# printing the solution
print('')
print('computation time: {}'.format(CompuataionT))
print('Objective value: {model.objective_value:.3}'.format(**locals()))
#print('Solution: ', end='')
sol_arc = pd.DataFrame(columns=['i','j','value'])
sol_time = []
sol_vlist = []
sol_count = []
for var in model.vars:
    if 'x' in var.name:
#        sol_arc.append(var.x)
        sol_arc.loc[len(sol_arc)]=[int(var.name.split(',')[0][2:]),int(var.name.split(',')[1][:-1]),var.x]
#        print('{var.name} = {var.x}'.format(**locals()))
    elif 'B' in var.name:
        sol_time.append(var.x)
    elif 'v' in var.name:
        sol_vlist.append(var.x)
    elif 'Q' in var.name:
        sol_count.append(var.x)
        
