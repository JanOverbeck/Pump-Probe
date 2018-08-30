# -*- coding: utf-8 -*-
"""
Created on Mon Sep 05 16:07:52 2016

@author: Jan
"""
#Define Save-Directory

import numpy
import os
import ctypes  # An included library with Python install.
import win32com.client #python activex client
import time #for time delay function time.sleep
import visa
import re

rm = visa.ResourceManager()
inst = rm.open_resource('USB0::0x0957::0x4108::MY51400616::INSTR')

# Declaration of variable passed by reference
 
#==============================================================================
# Basic Functions
#==============================================================================
def setChanVolt(volt,channel=1):
    inst.write(":VOLT%i %f" %(channel,volt))
     
def setChanFreq(freq,channel=1):
    """Set Frequency on channel 1/2, e.g.: 50, "50Hz", "50KHZ", 50000, "1MHZ" """
    inst.write(":FREQ%i %s"%(channel,freq))  
    
def ChanOffset(volt,channel=1):
    inst.write(":VOLT%i:OFFSET %f" %(channel,volt))
    
def ChanOutState(state="off", channel=1, inverted=0):
    """Turn output "on/ON" or "off/OFF" on channel 1 or 2. For inverted output specify 1. """
    if inverted == 0:
        inst.write("OUTP%i %s" %(channel,state))    
    elif inverted == 1:
        inst.write("OUTP%i:COMP %s" %(channel,state))    

def addChanOut1(add="plus"):
    """Add channels: "Plus" or "OFF". """
    inst.write("CHAN:MATH %s" %add)
    
def AMstate(AM="OFF",channel=1):
    """Turn Amplitude Modulation "ON" or "OFF". """
    inst.write(":AM%i:STAT %s" %(channel,AM))
    
def AMdepth(depthPerc=100,channel=1):
    """Set Depth of Amplitude Modulation from 0-100 (%). """
    inst.write(":AM%i:DEPT %iPCT" %(channel,depthPerc))   
    
def AMfreq(freq,channel=1):
    """Set AM-Frequency on channel 1/2, e.g.: 50, "50Hz", "50KHZ", 50000, "1MHZ" """    
    inst.write("AM%i:INT:FREQ %s"%(channel,freq))   
    
def AMshape(shape="SIN",channel=1):
    """Set AM-shape on channel 1/2, e.g.: "SIN","SQU","RAMP","NRAM","TRI","NOIS","USER". """    
    inst.write("AM%i:INT:FUNC %s"%(channel,shape))   
    
def dispState(state="ON"):
    inst.write("DISP %s" %state)
    
def resetInstrument():
    inst.write("*RST")
    
def set_delay(delay):
    """for our pump_probe setup no channel has to be specified, because the Agilent delay settings can only be set on channels w/o amplitude modulation AM active"""
    inst.write("PULS:DEL %f" %(delay))
    
def set_delay_ns(delay):
    """for our pump_probe setup no channel has to be specified, because the Agilent delay settings can only be set on channels w/o amplitude modulation AM active"""
    inst.write("PULS:DEL %f NS" %(delay))
#==============================================================================
# Arbitrary Waveform definition    
#==============================================================================

def build_pulse_waveform(startper,endper):
    """This is the function help"""
    mywaveform = numpy.zeros(100, dtype=numpy.int)
    if startper > endper:
        mywaveform[0:endper]=1
        mywaveform[startper:100]=1
    else:
        mywaveform[startper:endper]=1 
    return mywaveform 
    
def setpulseposition(startper,endper,channel=2):
    """This is the function help"""
    pulsepositionstr = str(build_pulse_waveform(startper,endper)).replace(" ",", ").replace("\n","")[1:-1]
    inst.write(":DATA%d VOLATILE, "%channel +pulsepositionstr )#TODO edit either so that DATA%d takes 
 

    
def set_delay_perc(delay):
    """for our pump_probe setup no channel has to be specified, because the Agilent delay settings can only be set on channels w/o amplitude modulation AM active"""
    currentFreq = float(inst.query("FREQ1?"))
    perc=((1/currentFreq)/100)*delay*1E9
    print perc
    inst.write("PULS:DEL %f NS" %(perc)) # adding NS lets python recognise unit of time as nanoseconds
    
#==============================================================================
# write pump/probe signal into function
#==============================================================================

#todo: somehow reference probe to pump??

def pumpprobe_intAM(chan1=1,chan2=2):
    """Set Agilent to output pump_probe signal, ie. a 1V pump on chan1 (1% duty cycle) and a .1V probe on chan 2 (10% duty cycle),
    w/ both channels output at output 1 and chan2 w/ amplitude modulation"""
    inst.write("*RST")
    #inst.write("DISP OFF")
    inst.write(":FUNC%i USER" %chan1)
    inst.write("FUNC%i:USER PUMP_1PER" %chan1)
    setChanVolt(2)   
    setChanFreq(200000)


    inst.write(":FUNC%i USER" %chan2)
    inst.write("FUNC2:USER PROBE_EARLY")
    setChanVolt(.2,2)
    setChanFreq(200000,2)
    AMdepth(100,2)
    AMshape("SQU",2)
    AMfreq(15000,2)
    AMstate("on",2)
    
    addChanOut1("plus")
    ChanOutState("on",1)

#pumpprobe_intAM(1,2)



def pumpprobe_signal_test_build():
    """This is the function help"""
    inst.write("*RST")
    #inst.write("DISP OFF")
    inst.write(":TRAC:CHAN1 ON") # enables channel coupling at output 1
    inst.write(":FUNC1 USER")    # set signal output to Arbitrary
    inst.write("FUNC1:USER p_short_1per") # set Arbitrary waveform to pump pulse
    #inst.query("FUNC1:USER?")
    #inst.write("FUNC1 USER")
    #inst.write("FUNC1:USER 100KHZ, 0.1") #FUNC can't seem to overwrite freq & amp settings
    
    inst.write(":VOLT1 1")
    inst.write(":FREQ1 200KHZ")    
    
    inst.write(":AM1:DEPT 100PCT")
    inst.write(":AM1:STAT ON")  #AM needs activation using STATus ON
    
    inst.write(":AM1:SOUR EXT") #sets source of AM
    
    
    inst.write("FUNC2:USER probe_2_12_p")
    #inst.query("FUNC2:USER?")
    inst.write(":VOLT2 .1")
    inst.write(":FREQ2 200KHZ")
    inst.write(":AM2:DEPT 100PCT")
    inst.write(":AM2:STAT ON")
    
    inst.write("CHAN:MATH plus") #adds both channels at one output
    inst.write(":OUTP1 ON")