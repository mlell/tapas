#!/usr/bin/env python

import numpy as np
from scipy.optimize import curve_fit
import sys

import matplotlib
matplotlib.use('Agg') # Off-screen rendering to PNG
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Read some value tuples from standard input

data = [line.split()[0:2] for line in sys.stdin]
data = [[int(s) for s in elem] for elem in data]
data_x = [x[0] for x in data]
data_y = [x[1] for x in data]

fun = lambda x,a,t:a * (x**2) + t 

popt, pcov = curve_fit(fun, data_x, data_y)

def functionGraph(fun, nsteps, *args, **kwargs):
    xmin,xmax = plt.xlim()
    x = np.linspace(xmin,xmax,nsteps)
    y = fun(x,*args,**kwargs)
    plt.plot(x,y)

plt.plot(data_x, data_y)
functionGraph(fun, 20, *popt)

plt.savefig("output.png")

print(popt)
print(pcov)
