# -*- coding: utf-8 -*-
"""
Created on Wed May 20 09:47:18 2020

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

#####################################################################################
##preliminary result summary
#for T in Deliveredlist:
#    T.TT = T.t1 - T.t0
#TotalTT = sum([T.TT for T in Deliveredlist])
#avgTT = TotalTT/len(Deliveredlist)
#servedrate = len(Deliveredlist)/demand*100
#Totaldistance = sum([list(Rtable['distance'])[-1] for Rtable in Rtablelist])
#Totaldrivingtime = sum([list(Rtable['time'])[-1] for Rtable in Rtablelist])
#
#col = "# of veh,demand,served %,Distance,DrivingT,ComputationT"
#table = pd.DataFrame(columns=col.split(','))
#data = [numofveh, demand, servedrate, Totaldistance, Totaldrivingtime, CompuataionT]
#table.loc[len(table)]=data
#
#path = wd+'result/summary'+'.csv' 
#if os.path.isfile(path):
#    table.to_csv(path, index=False, mode='a', header=False)
#else: table.to_csv(path, index=False, mode='a')
#            
#        #additional stop station
#
#####################################################################################
