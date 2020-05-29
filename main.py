# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 10:06:53 2019

@author: Transmatics
"""
import time

time_start = time.clock()

print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
print("%%%%%%%%%%%%%                                %%%%%%%%%%%%%")
print("%%%%%%%%%%%%%  Routing Algorithm simulation  %%%%%%%%%%%%%")
print("%%%%%%%%%%%%%                                %%%%%%%%%%%%%")
print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")


print("\nImporting dependencies")
import numpy as np
import math
import random
import pandas as pd
#import math
#from plotly.graph_objs import *

print("\nInitializing Simulation Environment")
import ClassDef as cl
from initialize import *
from funcs import *

data_hold = wd+'iteration_data/'
try:
    os.mkdir(data_hold+'type'+str(demand_scenario)+'_'+str(numofveh)+'_'+str(demand)) 
    os.mkdir(data_hold+'type'+str(demand_scenario)+'_'+str(numofveh)+'_'+str(demand)+'/initialroute')
    os.mkdir(data_hold+'type'+str(demand_scenario)+'_'+str(numofveh)+'_'+str(demand)+'/improvement')
except:pass

#if os.path.isfile(path):
#    table.to_csv(path, index=False, mode='a', header=False)
#else: table.to_csv(path, index=False, mode='a')

#check = input("Trip regeneration?(y/n): ")
while(1):
    try:
        time_start = time.clock()
        check = 'y'
        if check =='y':
            from genTrip import *
        else:
            pass
        
        print("\nInitial routing ")
        from routing import *
        print("\nImprovement")
        from improvement import *
        time_elapsed = (time.clock() - time_start)
        
        print('network size: '+ str(network_size) + ' ' + str(network_size_y))
        print('demand: '+str(demand))
        print('veh num:'+ str(numofveh))
        #print(len(servedtriplist))
        print(time_elapsed)
        #print('%10.2f'%time_elapsed+'\t'+str(len(servedtriplist)))
        
        #from result_route import *
        
        #
        #print('demand: '+str(demand))
        #print('veh num:'+ str(numofveh))
        ##print(len(servedtriplist))
        ##print(time_elapsed)
        #print(str(time_elapsed)+'\t'+str(len(servedtriplist)))
        break
    except: pass

