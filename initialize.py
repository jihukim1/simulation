# -*- coding: utf-8 -*-
"""main 모듈 반복
Created on Tue Nov 12 11:16:20 2019

@author: Transmatics
"""


import os
import numpy as np
import pandas as pd
import pickle
import math


############################################################################

wd = os.getcwd() + "/"

############################################################################

#simulation
totaltime = 1 * 60 #n hours (min)
demand = 5  #total demand size
numofveh = 1
vehTT = 60#min
v_avg = 45 *1000 /60 #(km/h) --> m/min
v_walk = 4 *1000 /60 #(km/h) --> m/min
capacity = 15 
walking_timelimit = 3 #(min)

#network info
network_size = 3000 #(m)
network_size_y = 3000
len_link = 250 #(m)
station_o = (network_size/2,network_size_y/2)
station_d = (network_size/2, network_size_y/2)

#demand scenario select
demand_scenario = 0
"""
0: random
1: concentrated O / concentrated D
2,3: concentrated O / spread D, vice versa
4: oblong city - concentrated O / spread D
"""
#trip generation 
min_dist = 600 #(m)
max_dist = (network_size**2 + network_size_y**2)**(1/2)
   
#improvement
Tinsertion_limit = 3 #min #detour

