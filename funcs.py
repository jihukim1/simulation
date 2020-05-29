# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 14:23:57 2020

@author: JIHU
"""

#import math

from initialize import *
import ClassDef as cl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

###########################################################################
###Network /  calculate coordinate 
def crosspointlist():
    gridnum_x = int(network_size/len_link)
    gridnum_y = int(network_size_y/len_link)
    
    Crosslist = []
    for x in range(gridnum_x+1):
        for y in range(gridnum_y+1):
            Cross = cl.Cross(len(Crosslist), x*len_link, y*len_link)
            Crosslist.append(Cross)
    return Crosslist

def point2grid(point): #point: (x,y)
    Crosslist = crosspointlist()
    #find nearest cross to point
    mindist = len_link
    for i, cross in enumerate(Crosslist):
        dist = math.sqrt((cross.loc[0]-point[0])**2 + (cross.loc[1]-point[1])**2)#cross.loc과 point의 거리 측정
        if dist < mindist:
            mindist = dist
            idx = i
    cross = Crosslist[idx]
    
    #cross.loc 과 point에서 less difference coord selection
    if abs(cross.loc[0]-point[0]) < abs(cross.loc[1]-point[1]): #x의 차이가 더 작은
        #x의 차이가 더 적은
        #y는 그대로, x로 정렬
        newpoint = (cross.loc[0], point[1])
    else:
        newpoint = (point[0], cross.loc[1])
    
    return newpoint

def tt(point0, point1): #traveltime
    global v_avg
    tt = (abs(point0[0]-point1[0])+abs(point0[1]-point1[1]))/v_avg
    return tt
    

def maxtt(Trip):
    return tt(Trip.OD[:2], Trip.OD[2:])
    

def feasible(point0, point1):
    if tt(point0, point1)<point1[2]-point0[2]:
        return True
    else:
        return False
    
def gridcentlist4plot(R):
    #grid 따라 이동하기 위한 list 생성
    centlist = [station_o] + [C.cent for C in R.clusterlist] #+ [station_d]
    pointlist = []
    for cent in centlist:
        try: 
            if pointlist[-1][0]==None:
                try: pointlist[-1] = (cent[0], pointlist[-1][1], pointlist[-1][2])
                except: pointlist[-1] = (cent[0], pointlist[-1][1])
            else:
                try: pointlist[-1] = (pointlist[-1][0], cent[1], pointlist[-1][2])
                except: pointlist[-1] = (pointlist[-1][0], cent[1])
            tmpt = (abs(pointlist[-1][0]-cent[0])+abs(pointlist[-1][1]-cent[1]))/v_avg
            pointlist[-1] = (pointlist[-1][0], pointlist[-1][1],cent[2]-tmpt)
        except:
            pass
        pointlist.append(cent)
        #400 나누어떨어지는 direction을 고정한 채로 이동
        if cent[0]%400==0:
            try:
                pointlist.append((None, cent[1], cent[2]))
            except:
                pointlist.append((None, cent[1]))
        else:            
            try:
                pointlist.append((cent[0], None, cent[2]))
            except:
                pointlist.append((cent[0], None))
        
    ########
    pointlist = pointlist[:-1]
    return pointlist

    

def plot(R,candidate_clusterlist,midway_dest,graphfolder): #current point, candidate cluster point, start/end station
#    global R
#    global C
#    global candidate_clusterlist
#    global midway_dest
#    global graphfolder
    
    plt.figure(figsize=(10,5))
    
    centlist = gridcentlist4plot(R)
    
    x = [e[0] for e in centlist]
    y = [e[1] for e in centlist]
#    t = [R.clusterlist[0].cent[2]-tt(R.clusterlist[0].cent, station_o)]
#    t = t+[C.cent[2] for C in R.clusterlist]
#    t = t+[R.clusterlist[-1].cent[2]+tt(R.clusterlist[0].cent, station_d)]
    plt.axis([0,network_size,0,network_size_y])
    plt.plot(x,y)
    
    x1 = [C.cent[0] for C in candidate_clusterlist]
    y1 = [C.cent[1] for C in candidate_clusterlist]
    c1 = [C.count * 10 for C in candidate_clusterlist]
    plt.scatter(x1,y1, s=c1)
    
    xm = midway_dest.cent[0]
    ym = midway_dest.cent[1]
    cm = midway_dest.count *10
    plt.scatter(xm,ym,s=cm, c='r')
    
#    for j in range(len(x)):
#        plt.text(x[j], y[j], str(t[j]))
    l = os.listdir(graphfolder)
    l = [i for i in l if '3dgraph' not in i]
    num = len(l)
    path = graphfolder+'graph_'+str(num)+'.png'  
    plt.savefig(path, dpi=300)
    

def plot3d(R,candidate_clusterlist,midway_dest,graphfolder): #current point, candidate cluster point, start/end station
#    global R
#    global C
#    global candidate_clusterlist
#    global midway_dest
#    global graphfolder
    
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
    y = [e[1] for e in centlist]
    t = [R.clusterlist[0].cent[2]-tt(R.clusterlist[0].cent, station_o)]
    t = t+[C[2] for C in centlist[1:]]
#    t = t+[R.clusterlist[-1].cent[2]+tt(R.clusterlist[0].cent, station_d)]
    ax3.plot(t,x,y)
    ax3.set_xlabel('t')
    ax3.set_ylabel('x')
    ax3.set_zlabel('y')
#    plt.show()
    
    ax2.plot(x,y)
    
    ax2.set_xlabel('x')
    ax2.set_ylabel('y')
    
    #candidate cluster scatter
    x1 = [C.cent[0] for C in candidate_clusterlist]
    y1 = [C.cent[1] for C in candidate_clusterlist]
    t1 = [C.cent[2] for C in candidate_clusterlist]
    t1 = [0 if t==None else t for t in t1]
    c1 = [(C.count**2) * 10 for C in candidate_clusterlist]
    ax3.scatter(t1, x1, y1, s=c1)
    ax2.scatter(x1,y1, s=c1)
    
    #midway plot
    xm = midway_dest.cent[0]
    ym = midway_dest.cent[1]
    tm = midway_dest.cent[2]
    if type(tm)!=float:
        tm=totaltime
    cm = (midway_dest.count**2) *10
    ax3.scatter(tm,xm,ym,s=cm, c='red')
    ax2.scatter(xm,ym,s=cm, c='red')
    
    #passedcluster plot
    tmpClist = [C for C in R.clusterlist]
    xp = [C.cent[0] for C in tmpClist]
    yp = [C.cent[1] for C in tmpClist]
    tp = [C.cent[2] for C in tmpClist]
    ax3.scatter(tp,xp,yp,s=cm, c='black')
    ax2.scatter(xp,yp,s=cm, c='black')
    
#    for j in range(len(x)):
#        plt.text(x[j], y[j], str(t[j]))
    l = os.listdir(graphfolder)
    l = [i for i in l if '3dgraph' in i]
    num = len(l)
    path = graphfolder+'3dgraph_'+str(num)+'.png'  
    plt.savefig(path, dpi=300)


