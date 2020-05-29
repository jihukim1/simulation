# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 17:43:26 2019

@author: Transmatics
"""

import numpy as np
import math

class Cross:
    def __init__(self, ID, x, y):
        self.ID     =ID
        self.loc    =(x,y)
        
        self.info = "ID, loc"

class Link:
    def __init__(self, ID, length):
        self.ID     = ID
        self.length = length
        self.connection = None
        
        self.info = "ID, length, connection"
        
class Trip:
    def __init__(self, ID):
        self.ID     = ID
        self.OD     = None #(x0,y0,x1,y1)
        self.TT     = None
        self.IVT    = None
        self.taxiT = None
        self.clusterO = None
        self.clusterD = None
        self.t0 = None
        self.t1 = None
        
        self.info = "ID, OD, TT, IVT, taxiT, clusterO, clusterD, t0, t1"
        

class Route:
    def __init__(self, ID):
        self.ID = ID
#        self.deptT = None
#        self.arivT = None
        self.distance = None
#        self.dir = None 
        self.triplist = []
        self.clusterlist = []
        
#        self.info = "ID, deptT, arivT, distance, dir, triplist, clusterlist"
        self.info = "ID, distance, triplist, clusterlist"
        

class Cluster: 
    def __init__(self, ID, x, y, t, typeofcluster):
        self.ID = ID
        self.cent = (x,y,t)
        self.triplist = []
        self.veh = None #veh, bus, route
        self.type = typeofcluster #Ocluster, Dcluster, assigned
        self.count = 0
        self.droplist = []
        
        self.info = "ID, cent, triplist, veh, type, count, droplist"
        
