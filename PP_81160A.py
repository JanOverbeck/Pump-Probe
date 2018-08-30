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


#==============================================================================
# Example for function that doesnt belong to a class
#==============================================================================

def printClasses():
    print "PP_81160A"

# Declaration of variable passed by reference
 
#==============================================================================
# Basic Functions
#==============================================================================
class PP_81160A:
    def __init__(self):
        self.rm = visa.ResourceManager()
        self.inst = self.rm.open_resource('USB0::0x0957::0x4108::MY51400616::INSTR') # assuming that this is a permanent device-specific address
    
    def sendArbCommandStr(self, commandStr=""):
        self.inst.write(commandStr)
    
    def setChanVolt(self, volt,channel=1):
        self.inst.write(":VOLT%i %f" %(channel,volt))
         
    def setChanFreq(self, freq,channel=1):
        """Set Frequency on channel 1/2, e.g.: 50, "50Hz", "50KHZ", 50000, "1MHZ" """
        self.inst.write(":FREQ%i %s"%(channel,freq))  
        
        
    def ChanOffset(self, volt,channel=1):
        self.inst.write(":VOLT%i:OFFSET %f" %(channel,volt))
        
    def ChanOutState(self, state="off", channel=1, inverted=0):
        """Turn output "on/ON" or "off/OFF" on channel 1 or 2. For inverted output specify 1. """
        if inverted == 0:
            self.inst.write("OUTP%i %s" %(channel,state))    
        elif inverted == 1:
            self.inst.write("OUTP%i:COMP %s" %(channel,state))    
    
    def addChanOut1(self, add="plus"):
        """Add channels: "Plus" or "OFF". """
        self.inst.write("CHAN:MATH %s" %add)
        
    def AMstate(self, AM="OFF",channel=1):
        """Turn Amplitude Modulation "ON" or "OFF". """
        self.inst.write(":AM%i:STAT %s" %(channel,AM))
        
    def AMdepth(self, depthPerc=100,channel=1):
        """Set Depth of Amplitude Modulation from 0-100 (%). """
        self.inst.write(":AM%i:DEPT %iPCT" %(channel,depthPerc))   
        
    def AMfreq(self, freq,channel=1):
        """Set AM-Frequency on channel 1/2, e.g.: 50, "50Hz", "50KHZ", 50000, "1MHZ" """    
        self.inst.write("AM%i:INT:FREQ %s"%(channel,freq))   
        
    def AMshape(self, shape="SIN",channel=1):
        """Set AM-shape on channel 1/2, e.g.: "SIN","SQU","RAMP","NRAM","TRI","NOIS","USER". """    
        self.inst.write("AM%i:INT:FUNC %s"%(channel,shape))   
        
    def dispState(self, state="ON"):
        self.inst.write("DISP %s" %state)
        
    def resetInstrument(self):
        self.inst.write("*RST")
        
    def set_delay_string(self, delayString):
        """Set the delay as string PULS:DEL %s.
        For our pump_probe setup no channel has to be specified, because the Agilent delay settings can only be set on channels w/o amplitude modulation AM active"""
        self.inst.write("PULS:DEL %s" %(delayString))
        
    def set_delay(self, delayS):
        """Set the delay in seconds (float).
        For our pump_probe setup no channel has to be specified, because the Agilent delay settings can only be set on channels w/o amplitude modulation AM active"""
        self.inst.write("PULS:DEL %f" %(delayS))
        
    def set_delay_ns(self, delayNS):
        """Set the delay in nano-seconds (float).
        For our pump_probe setup no channel has to be specified, because the Agilent delay settings can only be set on channels w/o amplitude modulation AM active"""
        self.inst.write("PULS:DEL %f NS" %(delayNS))
        
    def set_delay_perc(self, delayPCT):
        """Set the delay in percent (float).
        For our pump_probe setup no channel has to be specified, because the Agilent delay settings can only be set on channels w/o amplitude modulation AM active"""
#        currentFreq = float(self.inst.query("FREQ1?"))
#        perc=((1/currentFreq)/100)*delay*1E9
#        print perc
        self.inst.write("PULS:DEL %f PCT" %(delayPCT)) # adding NS lets python recognise unit of time as nanoseconds
    #==============================================================================
    # Arbitrary Waveform definition    
    #==============================================================================
    
    def build_pulse_waveform(self, startper,endper):
        """This is the function help"""
        mywaveform = numpy.zeros(100, dtype=numpy.int)
        if startper > endper:
            mywaveform[0:endper]=1
            mywaveform[startper:100]=1
        else:
            mywaveform[startper:endper]=1 
        return mywaveform 
        
    def setpulseposition(self, startper,endper,channel=2):
        """This is the function help"""
        pulsepositionstr = str(self.build_pulse_waveform(startper,endper)).replace(" ",", ").replace("\n","")[1:-1]
        self.inst.write(":DATA%d VOLATILE, "%channel +pulsepositionstr )#TODO edit either so that DATA%d takes 
     
    
        

        
    #==============================================================================
    # write pump/probe signal into function
    #==============================================================================
    
    #todo: somehow reference probe to pump??
    
    def pumpprobe_intAM(self, chan1=1,chan2=2):
        """Set Agilent to output pump_probe signal, ie. a 1V pump on chan1 (1% duty cycle) and a .1V probe on chan 2 (10% duty cycle),
        w/ both channels output at output 1 and chan2 w/ amplitude modulation"""
        self.inst.write("*RST")
        #self.inst.write("DISP OFF")
        self.inst.write(":FUNC%i USER" %chan1)
        self.inst.write("FUNC%i:USER PUMP_1PER" %chan1)
        self.setChanVolt(2)   
        self.setChanFreq(200000)
    
    
        self.inst.write(":FUNC%i USER" %chan2)
        self.inst.write("FUNC2:USER PROBE_EARLY")
        self.setChanVolt(.2,2)
        self.setChanFreq(200000,2)
        self.AMdepth(100,2)
        self.AMshape("SQU",2)
        self.AMfreq(15000,2)
        self.AMstate("on",2)
        
        self.addChanOut1("plus")
        self.ChanOutState("on",1)
    
    #pumpprobe_intAM(1,2)
    
    
    
    def pumpprobe_signal_test_build(self):
        """This is the function help"""
        self.inst.write("*RST")
        #self.inst.write("DISP OFF")
        self.inst.write(":TRAC:CHAN1 ON") # enables channel coupling at output 1
        self.inst.write(":FUNC1 USER")    # set signal output to Arbitrary
        self.inst.write("FUNC1:USER p_short_1per") # set Arbitrary waveform to pump pulse
        #self.inst.query("FUNC1:USER?")
        #self.inst.write("FUNC1 USER")
        #self.inst.write("FUNC1:USER 100KHZ, 0.1") #FUNC can't seem to overwrite freq & amp settings
        
        self.inst.write(":VOLT1 1")
        self.inst.write(":FREQ1 200KHZ")    
        
        self.inst.write(":AM1:DEPT 100PCT")
        self.inst.write(":AM1:STAT ON")  #AM needs activation using STATus ON
        
        self.inst.write(":AM1:SOUR EXT") #sets source of AM
        
        
        self.inst.write("FUNC2:USER probe_2_12_p")
        #self.inst.query("FUNC2:USER?")
        self.inst.write(":VOLT2 .1")
        self.inst.write(":FREQ2 200KHZ")
        self.inst.write(":AM2:DEPT 100PCT")
        self.inst.write(":AM2:STAT ON")
        
        self.inst.write("CHAN:MATH plus") #adds both channels at one output
        self.inst.write(":OUTP1 ON")