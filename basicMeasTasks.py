# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 09:59:18 2016

@author: Jan
"""

import numpy

def sweepParameter(start,stop,step,andBack=0):
    parameterList = numpy.arange(start,stop+step,step)
    if andBack==1:
        parameterList = numpy.append(parameterList,parameterList[::-1])
    return parameterList