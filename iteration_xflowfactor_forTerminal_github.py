#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 10:16:41 2019

@author: xiaorong
"""

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')
from matplotlib.path import Path
import matplotlib.pyplot as plt

import os.path as osPath

import os as OS
import fnmatch
import csv
from shutil import copyfile
import subprocess
import time

###############################################################################


pitch = 34.0e-3 #m rod's pitch
L1 = 0.136 #m dimension along X
L2 = L1 #m dimension along Y
L3 = 0.96 #m dimension along Z

nSPE = 4


###############################################################################
def CorrectCrossVel():
    ''' Previously the CFD cross velocities were extracted from the raw CFD 
    data without considering the corresponding signs defined in CTF code. Now
    need to compare CTF and CFD cross velocities directly, therefore need to 
    correct the direction/sign for the CFD data. In other words: flip the sign 
    in the flip gaps. Then plot corrected velocities.
    '''
    crossFlowCFD = pd.read_csv('Data_crossflow.csv', index_col = 'Unnamed: 0')
    gapsToFlip = [2,4,6,7,9,11,13,14,16,18,20,21] #note: index starting from 1
    gapsToFlipIndex = [x - 1 for x in gapsToFlip]
    for i in gapsToFlipIndex:
        crossFlowCFD.iloc[i,:] = -crossFlowCFD.iloc[i,:]
    crossFlowCFD.to_csv('Data_crossflow_corrected.csv')
    
    axialno = [i for i in range(1,15)]
    plotgaps = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]

    scattergap = []
    for gap in plotgaps:
        leg = "gap" + str(gap)
        scattergap.append(plt.plot(axialno, crossFlowCFD.iloc[gap-1,:],\
                                   label=leg))
    #plt.legend(loc='lower right', ncol=4, fontsize=7)
    plt.grid(True, linestyle=':')
    plt.xticks(axialno)
    plt.xlabel('Axial node number')
    plt.ylabel('lateral velocity, m/s')
    plt.savefig("lateral_velocity_in_gaps_correctedCFD.png", dpi=160)
    plt.show()
    plt.close()     
    return 0
    

###############################################################################    
def CrossFactorIteration(sourceIncrement, CTFvelToRead):
    #sourceIncrement = 0.01 
    CTFcrossFlow = CTFvelToRead + '.csv'
#    basefilename = 'C:\\Users\\xiaorli\\CTF40\\simulations\\xflow_data'
    basefilename = 'xflow_data'
    gapno = 24
    
    crossFlowCFD = pd.read_csv('Data_crossflow_corrected.csv', index_col = 'Unnamed: 0')
    myheader = crossFlowCFD.columns.values.tolist()
    
    columnsCTF = range(0,14)
    crossFlowCTF = pd.read_csv(CTFcrossFlow,  skipinitialspace = True, \
                               usecols=columnsCTF, header = None)
    crossFlowCTF.columns = myheader
    crossFlowCTF = crossFlowCTF.rename(index=lambda s: 'gap'+str(s))
    
    Err = crossFlowCFD.subtract(crossFlowCTF)
    ErrSquare = Err.pow(2)
    SSE = ErrSquare.sum().sum()  # overall difference between CTF and CFD
    SSEboundary = (ErrSquare.sum()[0], ErrSquare.sum()[1], ErrSquare.sum()[2], \
                   ErrSquare.sum()[3])
    #SSEboundary = max(ErrSquare.iloc[:,0])
    #print 'SSE                   Node0               Node1                  Node2\
    #            Node3'
    #print SSE, SSEboundary
    
#    f = open('SSE', 'a')
#    f.write(str(SSE) + ',')
#    f.close()        
    relativeErr = crossFlowCFD.divide(crossFlowCTF)
    relativeErr = relativeErr.replace([np.inf, -np.inf], [5, -5])
    #replace value does not matter, it occurs before the MV position
    
    #read in CFD velocities
    
    gapsToFlip = [2,4,6,7,9,11,13,14,16,18,20,21] #note: index starting from 1
    gapsToFlipIndex = [x - 1 for x in gapsToFlip]
    for i in range(0,gapno):
        crossfile = basefilename + str(i+1) 
        crossfile_old = crossfile + 'copy'
        copyfile(crossfile, crossfile_old)
        cross_oldhd = open(crossfile_old, 'r') #open the original xflow file for gap i
        lines = [line.rstrip('\n') for line in cross_oldhd.readlines()]
        cross_newhd = open(crossfile, 'w') # replance old crossfile

        count = 0 
        while count < 9: # the first 8 lines remain untouched
            cross_newhd.write(lines[count] + '\n')
            count += 1
        while count < 10: # set the first source term to zero -- no CFD data
            line = lines[count]
            parsedline = line.split()
            newline = parsedline[0] + '   ' + str(0)
            cross_newhd.write(newline + '\n')
            count += 1
        while count < 24:
            j = count - 12 + 2# j is axial node index, starting from 2!!!
            #j = count - 10 # j is axial node index, starting from 0!
            if j == 0:
                sign = 20
            if j == 3 or j == 3:
                sign = 8
            else:
                sign = 1
            line = lines[count]
            parsedline = line.split()
            if relativeErr.iloc[i,j] > 1.01: #|CFD| > |CTF| "significantly"
                if crossFlowCFD.iloc[i,j] > 0:
                    newsource = float(parsedline[1]) \
                    + relativeErr.iloc[i,j] * sourceIncrement * sign
                else:
                    newsource = float(parsedline[1]) \
                    - relativeErr.iloc[i,j] * sourceIncrement * sign
            elif relativeErr.iloc[i,j] < 0.99 and relativeErr.iloc[i,j] > 0:
                if crossFlowCFD.iloc[i,j] > 0:
                    newsource = float(parsedline[1]) \
                    - min(1/relativeErr.iloc[i,j],5) * sourceIncrement * sign
                    #- relativeErr.iloc[i,j] * sourceIncrement * sign
                else:
                    newsource = float(parsedline[1]) \
                    + min(1/relativeErr.iloc[i,j],5) * sourceIncrement * sign
            elif relativeErr.iloc[i,j] <= 1.01 and \
            relativeErr.iloc[i,j] >= 0.99: # CFD and CTF comparable
                newsource = float(parsedline[1])
            else: # in this case CFD and CTF have opposite signs
                if crossFlowCFD.iloc[i,j] > 0:
                    newsource = float(parsedline[1]) \
                    + 5 * sourceIncrement * sign
                    #+ abs(relativeErr.iloc[i,j]) * sourceIncrement * sign
                else:
                    newsource = float(parsedline[1]) \
                    - 5 * sourceIncrement * sign
                    #- abs(relativeErr.iloc[i,j]) * sourceIncrement * sign
            newline = parsedline[0] + '   ' + str(newsource)
            cross_newhd.write(newline + '\n')
            count += 1
        while count < 30: # last 6 lines kept untouched
            cross_newhd.write(lines[count] + '\n')
            count += 1
        cross_newhd.close()
        cross_oldhd.close()
    #print relativeErr.iloc[:,0]
    return 0
###############################################################################
def getGapVel(filename,outfilename,number):
    ''' extract gap velocity from CTF out put into csv file and plot. i is used 
    to name sequential figures
    '''
    totalInteval = 20
    totalGap = 24
    filehd = open(filename, 'r')
    lines =[line.rstrip('\n') for line in filehd.readlines()]

    linetracker = 0
    lateralVelocities = np.zeros([totalGap, totalInteval])
    times = []
    
    #determine end time of the simulation
    for line in lines:
        if 'Fluid properties for gap' in line:
            parsedline = line.split()
            time = parsedline[-2]
            times.append(time)
    endtime = max(times)
            
    for line in lines:
        linetracker += 1
        if 'Fluid properties for gap' in line:
            parsedline = line.split()
            gapno = int(parsedline[4])
            time = parsedline[-2]
            if time == endtime:
                for inteval in range(0, totalInteval):
                    target = lines[linetracker - 1 + 12 + inteval]
                    parsedtarget = target.split()
                    lateralVel = parsedtarget[6]
                    lateralVelocities[gapno - 1][inteval] = lateralVel
    #lateralVelocities = np.flip(lateralVelocities, 1)
    #numpy version in docker container was too old to use np.flip, solution below
    lateralVelocities = np.fliplr(lateralVelocities)
    np.savetxt(outfilename + ".csv", lateralVelocities, delimiter=',')
###############################################################################
# plot the lateral velocities
    gapno = [i for i in range(1,25)]
    axialno = [i for i in range(1,15)]
    lateralvelCTF = pd.read_csv(outfilename + ".csv", header=None)
    #choose which gaps to plot
    plotgaps = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
    scattergap = []
    for gap in plotgaps:
        leg = "gap" + str(gap)
        scattergap.append(plt.plot(axialno, lateralvelCTF.iloc[gap-1,0:14],\
                                   linewidth=0.5, label=leg))
    plt.legend(loc='lower right', ncol=4, fontsize=7)
    plt.grid(True, linestyle=':')
    plt.xticks(axialno)
    plt.xlabel('Axial node number')
    plt.ylabel('lateral velocity, m/s')
    plt.savefig(outfilename + str(number) + ".jpg", dpi=160) #bbox_inches = 'tight'
    print outfilename, ' ', number, '.jpg has been saved!'
    plt.close()   
    

###############################################################################
    
    
    return 0


###############################################################################
def calSSE(CTFvelToRead):
    CTFcrossFlow = CTFvelToRead + '.csv'
    crossFlowCFD = pd.read_csv('Data_crossflow_corrected.csv', index_col = 'Unnamed: 0')
    myheader = crossFlowCFD.columns.values.tolist()
    
    columnsCTF = range(0,14)
    crossFlowCTF = pd.read_csv(CTFcrossFlow,  skipinitialspace = True, \
                               usecols=columnsCTF, header = None)
    crossFlowCTF.columns = myheader
    crossFlowCTF = crossFlowCTF.rename(index=lambda s: 'gap'+str(s))
    
    Err = crossFlowCFD.subtract(crossFlowCTF)
    ErrSquare = Err.pow(2)
    SSE = ErrSquare.sum().sum()  # overall difference between CTF and CFD
    
    
    return SSE
###############################################################################


#CorrectCrossVel() # flip the CFD cross velocity in certain gaps, do only once
#filename = 'deck_distributed_inlet_temperature_realgeo_directedOnly_iterating.ctf.gaps.out'
filename = 'deck_flatinlet_temperature_realgeo_directedOnly_iterating_final.ctf.gaps.out'
getGapVel(filename, 'lateral velocities iteration final', 0)
SSE = 0.008 #initiate as 20.
correction = 0.001 # souce term increment starts from 0.01
number = 248 # index for saving the pictures of lateral velocities
while SSE >= 0.0005 and correction >= 0.00001:
    number= number+1
    print 'current number is: ', number
    SSE_before = SSE
    SSE = calSSE('lateral velocities iteration final')
    f = open('SSE', 'a')
    f.write(str(SSE) + ',')
    f.close()  
    
    if SSE/SSE_before <= 0.2:
        correction = correction * 2
    elif SSE/SSE_before > 0.2 and SSE/SSE_before <= 0.99:
        correction = correction
    elif SSE/SSE_before > 0.99:
        correction = correction * 0.5
    
    CrossFactorIteration(correction, 'lateral velocities iteration final')

    subprocess.call(["./cobratf", "deck_flatinlet_temperature_realgeo_directedOnly_iterating_final.inp"])
    getGapVel(filename, 'lateral velocities iteration final', number) # get lateral velocity in .csv file

    print "CTF has run with correction = ", correction
    print "SSE_before was: ", SSE_before
    print "SSE was: ", SSE
    time.sleep(10)
    
if SSE < 0.001:
    print "SSE < 0.001, iterations finished!"
else:
    print "correction is too small, iterations are stopped!"