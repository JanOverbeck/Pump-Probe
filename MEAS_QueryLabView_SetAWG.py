# -*- coding: utf-8 -*-
"""
Created on Thu Oct 06 10:20:32 2016

@author: Jan

This script switches between two time delays of pump and probe pulse, depending on the cycle number read from labview.

"""

import numpy
import matplotlib
import ctypes  # An included library with Python install.
import win32com.client #python activex client
import time #for time delay function time.sleep
import visa
rm = visa.ResourceManager()
inst = rm.open_resource('USB0::0x0957::0x4108::MY51400616::INSTR')
print(inst.query("*IDN?"))
#==============================================================================
# TODO: running the VI w/ VI.Call() 'breaks' the console, ie. current command 
# has to be aborted... why?
#==============================================================================
#TODO: write code:
#for data analysis which splits the conductance columns into two separate
# files of even and odd conductances, ie. file1: Z G_1 G_1 G_1 .... file2: Z G_2 G_2 G_2 (1=odd, 2=even) 

#TODO: how to tell python when to go and look at cycle number in labview?
#there seem to be 2 ways of doing this: 
#   1: let python ask labview at a faster rate than interramp delay, which is 3s,
# what cycle number is. Although, Labview really switches cycle number at the end of the
#interramp delay 
#   2: make labview tell python, maybe w/ labpython ?

#TODO look up 'alert' functionality

LabVIEW = win32com.client.Dispatch("Labview.Application")
# NB! typing 'r' before a string tells python to read the string RAW, which it otherwise wouldn't.
# by default python recognises string as unicode, which is why if you write backslash '\' it reads it as ESCAPE CODE
#and subsequently messes up eg. your file path. So, for file paths: either use r'' and single '\' or leave 'r' and write 
#backslash as '\\'
VI = LabVIEW.getvireference(r'D:\Marti\Labview\STABLE_Labview_BJ_Acq_MO_OffsetCv1\TerSubIV\MXUpDownCycles_2Conv.vi') # Path to labVIEW VI
result = VI.getcontrolvalue('cycle nb') #Get return value
print(result) #print value to console


def build_pulse_waveform(startper,endper): 
    mywaveform = numpy.zeros(100, dtype=np.int)
    if startper > endper:
        mywaveform[0:endper]=1
        mywaveform[startper:100]=1
    else:
        mywaveform[startper:endper]=1 
    return mywaveform 
    
def setpulseposition(startper,endper,channel=2):
    pulsepositionstr = str(build_pulse_waveform(startper,endper)).replace(" ",", ").replace("\n","")[1:-1]
    inst.write(":DATA%d VOLATILE, "%channel +pulsepositionstr )#TODO edit either so that DATA%d takes 
#desired channel; or leave at DATA2 and write separate line for channel 1
    
inst.write(":AM2:INT:FREQ 15KHZ")

setpulseposition(40,41,1) # to (de)activate eg pump pulse, in brackets set (40,40,1) 
setpulseposition(78,87)
probe_early_start = 78
probe_early_end = 87
probe_late_start = 60
probe_late_end = 69
early_probe_positionstr = str(build_pulse_waveform(probe_early_start, probe_early_end)).replace(" ",", ").replace("\n","")[1:-1]
late_probe_positionstr = str(build_pulse_waveform(probe_late_start, probe_late_end)).replace(" ",", ").replace("\n","")[1:-1]

#==============================================================================
# inst.write(":MEM:STAT:NAME 3, PROBE_EARLY")
# inst.query("MEM:STAT:NAME? 4")
# Does not seem to do anything to waveforms stored in nonvolatile memory. USB stuff??
#==============================================================================

inst.write("DATA2:COPY PROBE_EARLY, VOLATILE") #Copy from Volatile to first empty nonvol, specified name
inst.write("DATA1:DEL PROBE_EARLY") #Need to specify name, not storage position
inst.query("DATA1:NVOL:CAT?")
inst.query("FUNC2:USER?")
inst.write("FUNC2:USER PROBE_EARLY")


inst.write("DATA1")
inst.write(":VOLT1:OFFSET 0")    

# define function which switches Agilent voltage output for odd/even traces
def py_ask_lab_cycle_nb_switch_probe(rate, maxcycles):
        cycle_nb = 0  # necessary to define variable cycle_nb before it enters while loop        
        #vhigh=0.55  #on 11.10.16 this is the Agilent value required to get Labview Voltage AI to be 9.96E-1 V
                    # BUT w/ 1:10 voltage divider attached! Ansatz: tune Agilent output voltage until you reach standard value 9.96E-1
        #vlow=0.495 # switch between high/low value to achieve distinct difference in data
        while cycle_nb<maxcycles: #tells python to go look at cycle number as long as condition met 
            n_prev = cycle_nb
            cycle_nb = VI.getcontrolvalue('cycle nb')
#            print("cycle: "+ str(cycle_nb) + " , n_prev: " + str(n_prev)) #print value to console
            if (cycle_nb % 2 == 0): #even; read: if cycle_nb modulo 2 is 0, we have even
                if cycle_nb != n_prev:
                    inst.write(":DATA2 VOLATILE, " +late_probe_positionstr)
                    print("I`m writing")
#                if inst.query(":DATA2:ATTR:AVER?") == 'late':  # != not equal
            
# ---->              TODO write conditions for probe_pulse positions!!
            

            else: #odd
                if cycle_nb != n_prev:
#                if float(inst.query(":DATA2:ATTR:AVER?")) < .09:
                    inst.write(":DATA2 VOLATILE, " +early_probe_positionstr)
                    print("I`m writing" + "cycle nb")
            time.sleep(1/rate)
                     

py_ask_lab_cycle_nb_switch_probe(10,1000) # execute function!

#==============================================================================
# edits from 24.11.16
#==============================================================================
def py_ask_lab_cycle_nb_switch_pump(rate, maxcycles):
        cycle_nb = 0  # necessary to define variable cycle_nb before it enters while loop        
        #vhigh=0.55  #on 11.10.16 this is the Agilent value required to get Labview Voltage AI to be 9.96E-1 V
                    # BUT w/ 1:10 voltage divider attached! Ansatz: tune Agilent output voltage until you reach standard value 9.96E-1
        #vlow=0.495 # switch between high/low value to achieve distinct difference in data
        while cycle_nb<maxcycles: #tells python to go look at cycle number as long as condition met 
            n_prev = cycle_nb
            cycle_nb = VI.getcontrolvalue('cycle nb')
#            print("cycle: "+ str(cycle_nb) + " , n_prev: " + str(n_prev)) #print value to console
            if (cycle_nb % 2 == 0): #even; read: if cycle_nb modulo 2 is 0, we have even
                if cycle_nb != n_prev:
                    inst.write(":VOLT1:OFFS 0.019")
                    inst.write(":VOLT1 .1")
                    print("I`m writing")
#                if inst.query(":DATA2:ATTR:AVER?") == 'late':  # != not equal

            else: #odd
                if cycle_nb != n_prev:
#                if float(inst.query(":DATA2:ATTR:AVER?")) < .09:
                    inst.write(":VOLT1:OFFS 0")
                    inst.write(":VOLT1 2")
                    print("I`m writing" + "cycle nb")
            time.sleep(1/rate)

py_ask_lab_cycle_nb_switch_pump(10,150)

#==============================================================================
# edits from 28.11.16
#==============================================================================

def set_delay_perc(delay):
    """for our pump_probe setup no channel has to be specified, because the Agilent delay settings can only be set on channels
    w/o amplitude modulation AM active. Set the position of the pump relative to the probe by specifying a
    percentage value for the delay"""
    currentFreq = float(inst.query("FREQ1?"))
    perc=((1/currentFreq)/100)*delay*1E9
    print perc
    inst.write("PULS:DEL %f NS" %(perc)) # adding NS lets python recognise unit of time as nanoseconds
    
set_delay_perc(100)


setpulseposition(72,81)

def sweep_pump(rate):
    """this function sweeps the pump pulse, in percentage of the cycle frequency at which pump and probe are set. the function
    starts at maximum delay and moves backwards. set the speed of the sweep by determining a rate value"""
    delay=100
    while delay>13: #a delay of 13 percent equates to the 'late probe' position
        delay=delay-1
        set_delay_perc(delay)
        time.sleep(1/rate)
        
sweep_pump(100)
    
        
        








#==============================================================================
# 
#==============================================================================

#testing the messagebox function
ctypes.windll.user32.MessageBoxW(0, u"Your text", u'Your title', 1)  # u implies unicode string, otherwise use MessageBoxA

#testvar = ctypes.windll.user32.MessageBoxW(0, u"Your text", u'Your title', 1)    
#while testvar!=1:
#    print "läuft"
#    time.sleep(1)
#
#        
#testvar = 0        
#testvar = 

