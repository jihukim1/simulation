# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 11:09:40 2020

@author: JIHU
"""


import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import scipy.stats as ss
import pickle
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D

from initialize import *
import ClassDef as cl


try:
    os.mkdir(wd+'/data')
except:
    pass
try:
    os.mkdir(wd+'/result')
except:
    pass

gridnum_x = int(network_size/len_link)
gridnum_y = int(network_size_y/len_link)
numlength = max(gridnum_x,gridnum_y)
namelen = len(str(numlength))
#numoflink = gridnum_x*(gridnum_y+1) + (gridnum_x+1)*gridnum_y

Linklist = []
for i in range(gridnum_x+1):
    for j in range(gridnum_y):
        x0=str(i).zfill(namelen)
        y0=str(j).zfill(namelen)
        x1=x0
        y1=str(j+1).zfill(namelen)
        ID = x0+y0+x1+y1
        L = cl.Link(ID, len_link)
        Linklist.append(L)
for i in range(gridnum_y+1):
    for j in range(gridnum_x):
        x0=str(j).zfill(namelen)
        y0=str(i).zfill(namelen)
        x1=str(j+1).zfill(namelen)
        y1=y0
        ID = x0+y0+x1+y1
        L = cl.Link(ID, len_link)
        Linklist.append(L)


savename = wd+'data/Linklist.pickle'
with open(savename, 'wb') as f:
    pickle.dump(Linklist, f)
