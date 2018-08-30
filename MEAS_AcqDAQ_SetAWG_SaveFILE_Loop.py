# -*- coding: utf-8 -*-
"""
Created on Mon Sep 05 16:07:52 2016

Edit: 2017-01-08

@author: Jan
"""
#Define Save-Directory
path = r"D:\Marti\Data\170109_plateau_tests\python_acquisition"
filename = "acquired_"

import numpy 
import matplotlib.pyplot as plt
import os
import ctypes  # An included library with Python install.
import win32com.client #python activex client
import time #for time delay function time.sleep
import visa
import acquireDaq as AQ # Module with basic DAQ commands for acquiring n points at rate r on selected physical channel.
import PP_81160A as AWG # Module with standard Agilent AWG-Commands for PumpProbe
import basicMeasTasks as bT # Module with standard Tasks such as sweep, ramp, loop?


#==============================================================================
# Testfunctions
#==============================================================================
testdata = AQ.DAQreadToArray("Dev1/ai0",1000,660000)
AWG.printClasses()

#==============================================================================
# Main programme
#==============================================================================

#create new instance of PP_81160A Arbitrary Wavefunction Generator
Agi = AWG.PP_81160A()


#Testfunctions
Agi.setChanVolt(2)
Agi.pumpprobe_intAM()
Agi.setpulseposition(1,10)
Agi.set_delay_perc(0)


#==============================================================================
# Initialize Variables with Sweep-Parameters & savedata  
#==============================================================================
voltSweep = bT.sweepParameter(0.0,2,0.2,1)
delaySweepPerc = bT.sweepParameter(100,0,-10)
delaySweep = bT.sweepParameter(0,99,1)


def makeSaveArray(sweeparray, Npoints=1005, Nloops=1): # We are using 1006 Point to get the following structure:  [ Timestamp | SweepParamValue | 3 WHY?? | Mean Value | Standard Dev | 1000 Points of raw data ]
    savedata = np.zeros((len(sweeparray)*Nloops, Npoints))
    return savedata
    
savedata = makeSaveArray(delaySweepPerc,1005,10)

#==============================================================================
# Initial State for Agilent
#==============================================================================
Agi.pumpprobe_intAM()
Agi.ChanOutState("ON",1,1)

#Agi.resetInstrument()
#Agi.setChanFreq(100)
#Agi.setChanVolt(2)
#Agi.ChanOutState("ON")

#==============================================================================
# OPT 1 : Perform measurement / acquire data
#==============================================================================
for i in voltSweep:
    print "Ampl. = " + str(i) +" Volts"
    Agi.setChanVolt(i,1)
    for j in delaySweep:
        print "Delay=" + str(j)
        Agi.ChanOffset(j/100,1)
    #savedataOld.append(AQ.DAQreadToArray("Dev1/ai0",100,1000).tolist()) #call function DAQreadToArray from module acquireDaq with standard parameters
        savedata = numpy.append(savedata,AQ.DAQreadToArray("Dev1/ai0",20,1000))
      
#==============================================================================
# OPT 2 : Volt sweep & acquire to savedata      
#==============================================================================
      
index = 0        
for i in voltSweep:
    print "Ampl. = " + str(i) +" Volts"
    Agi.setChanVolt(i,1)
    savedata[index,5:1005] = AQ.DAQreadToArray("Dev1/ai0",1000,1000).reshape((1,1000))
    savedata[index,0] = time.clock()
    savedata[index,1] = i
    savedata[index,2] = 3
    savedata[index,3] = numpy.mean(numpy.abs(savedata[index,5:1005]))
    savedata[index,4] = numpy.std(numpy.abs(savedata[index,5:1005]))
    index +=1

#==============================================================================
# OPT 3 : Delay sweep & acquire to savedata
#==============================================================================

index = 0        
for i in delaySweepPerc:
    print "Delay. = " + str(i) +" Percent"
    Agi.set_delay_perc(i)
    savedata[index,5:1005] = AQ.DAQreadToArray("Dev1/ai0",1000,1000).reshape((1,1000))
    savedata[index,0] = time.clock()
    savedata[index,1] = i
    savedata[index,2] = 3
    savedata[index,3] = numpy.mean(numpy.abs(savedata[index,5:1005]))
    savedata[index,4] = numpy.std(numpy.abs(savedata[index,5:1005]))
    index +=1

#==============================================================================
# OPT 4 : DUMMY delay sweep & acquire to savedata
#==============================================================================

index = 0        
dump = AQ.DAQreadToArray("Dev1/ai0",1000,1000).reshape((1,1000))
for i in delaySweepPerc:
    print "Delay. = " + str(i) +" Percent"
    #Agi.set_delay_perc(i)
    savedata[index,5:1005] = AQ.DAQreadToArray("Dev1/ai0",1000,1000).reshape((1,1000))
    savedata[index,0] = time.clock()
    savedata[index,1] = i
    savedata[index,2] = 3
    savedata[index,3] = numpy.mean(numpy.abs(savedata[index,5:1005]))
    savedata[index,4] = numpy.std(numpy.abs(savedata[index,5:1005]))
    index +=1

#==============================================================================
# OPT 5 : looped delay sweep & acquire to savedata
#==============================================================================

index = 0 
for j in numpy.arange(10): # loop n-times      
    for i in delaySweepPerc:
        print "Delay. = " + str(i) +" Percent"
        Agi.set_delay_perc(i)
        savedata[index,5:1005] = AQ.DAQreadToArray("Dev1/ai0",1000,10000).reshape((1,1000))
        savedata[index,0] = time.clock()
        savedata[index,1] = i
        savedata[index,2] = 3
        savedata[index,3] = numpy.mean(numpy.abs(savedata[index,5:1005]))
        savedata[index,4] = numpy.std(numpy.abs(savedata[index,5:1005]))
        index +=1

#==============================================================================
# OPT 6 : looped pump amplitude sweep & acquire to savedata      
#==============================================================================


index = 0 
for k in numpy.arange(10): # loop n-times
    for i in voltSweep:
        print "Ampl. = " + str(i) +" Volts"
        Agi.setChanVolt(i,1)
        savedata[index,5:1005] = AQ.DAQreadToArray("Dev1/ai0",1000,1000).reshape((1,1000)) # 10x faster!
        savedata[index,0] = time.clock()
        savedata[index,1] = i
        savedata[index,2] = 3
        savedata[index,3] = numpy.mean(numpy.abs(savedata[index,5:1005]))
        savedata[index,4] = numpy.std(numpy.abs(savedata[index,5:1005]))
        index +=1
AQ.DAQreadToArray("Dev1/ai0",1000,1000).reshape((1,1000))
#help(numpy.ndarray.sort)
#savedataSorted = savedata[savedata[:, 1].argsort()]

j=0
newarray2 = numpy.zeros((len(numpy.unique(savedata[:,1])),5))
for param in numpy.unique(savedata[:,1]):
    i=0
    newarray1 = numpy.zeros((len(savedata[:,0])/len(numpy.unique(savedata[:,1])),5))
    for row in savedata:  
        if row[1] == param:
            newarray1[i,0:5]=row[0:5] 
            i+=1
            print(i)
    newarray2[j,0:5] = numpy.mean(newarray1,axis=0)
    j+=1
        

#==============================================================================
# Plotting the acquired data
#==============================================================================
# Testdata:
plt.plot(testdata)
plt.show()

# Acquired data

plt.plot(savedata[0,5:1005]) # Plot Raw Data of Row 0

plt.plot(savedata[:,3]) # Plot Mean
plt.plot(savedata[:,4]) # Plot Standard Dev
plt.show()

#==============================================================================
# save data
#==============================================================================
systime = str(time.gmtime()[0:6]).replace(",", "_").replace(" ","").replace("(","").replace(")","")  
filename_ex = filename + systime
filepath = os.path.join(path,filename_ex) # joins filename to directory_sting  
numpy.savetxt(filepath,savedata)
filename_ex = filename + systime + "_s"
filepath = os.path.join(path,filename_ex) # joins filename to directory_sting  
numpy.savetxt(filepath,savedata[:,0:5])


#==============================================================================
# 
#==============================================================================
