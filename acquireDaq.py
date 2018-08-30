# -*- coding: utf-8 -*-
"""
Created on Mon Sep 05 16:07:52 2016

Edit: 2017-01-08

@author: Jan
"""



from PyDAQmx import * # when running this in standalone, this clutters the Variable explorer.

#==============================================================================
# import PyDAQmx # this would be nicer to use, however it means that DAQmxCreateTask() has to be changed to PyDAQmx.DAQmxCreateTask() and so on...
# #What would be the cleanes way to do this??
#==============================================================================

import numpy

#Reset device to avoid NI-DAQmx Error -50103
DAQmxResetDevice("Dev1")



# Declaration of variable passed by reference

def DAQreadToArray(physChan="Dev1/ai0",npoints=1000,rate=500):
    """Acquires npoints on physChan with at rate points/s and returns it as numpy array of length npoints"""
    taskHandle = TaskHandle()
    read = int32()
    data = numpy.zeros((npoints,), dtype=numpy.float64)
    
    try:
        # DAQmx Configure Code
        DAQmxCreateTask("",byref(taskHandle))
        # taskHandle, physicalChannel, nameToAssignToChannel, terminalConfig, minVal, maxVal, units, customScaleName
        DAQmxCreateAIVoltageChan(taskHandle,physChan,"",DAQmx_Val_Cfg_Default,-10.0,10.0,DAQmx_Val_Volts,None)
        # taskHandle, source, rate, activeEdge, sampleMode, sampsPerChan
        DAQmxCfgSampClkTiming(taskHandle,"",rate,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,npoints)
    
        # DAQmx Start Code - acquire now
        DAQmxStartTask(taskHandle)
    
        # DAQmx Read Code - read from buffer: taskHandle, numSampsPerChan, timeout, fillMode, readArray, arraySizeInSamps, sampsPerChanRead, reserved
        DAQmxReadAnalogF64(taskHandle,npoints,10.0,DAQmx_Val_GroupByChannel,data,npoints,byref(read),None)
    
        print "Acquired %d points"%read.value
    except DAQError as err:
        print "DAQmx Error: %s"%err
    finally:
        if taskHandle:
            # DAQmx Stop Code
            DAQmxStopTask(taskHandle)
            DAQmxClearTask(taskHandle)
    return data
