
import matplotlib
matplotlib.use("Agg")
import os

os.environ['MPLCONFIGDIR'] ='/home/migjen/'

import numpy as np
from pylab import *
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

#readfile = start_completeobstruction.csv

xs = []
ys = []
zs = []
the_fourth_dimension= []
import csv

with open ("3dtopcpu.txt", 'rb') as csvfile:
        reader = csv.reader(csvfile)
	for row in reader:
		xs.append(int(row[0]))
		ys.append(int(row[1]))
		zs.append(int(row[2]))
		the_fourth_dimension.append(float(row[3]))                
fig = plt.figure()

ax = fig.add_subplot(111,projection='3d')
#n = 100


colors = the_fourth_dimension#/max(the_fourth_dimension))
#colors = [the_fourth_dimension*2**n for n in range(len(xs))] 
colmap = cm.ScalarMappable(cmap=cm.hsv)
colmap.set_array(the_fourth_dimension)

yg = ax.scatter(xs, ys, zs,s = 500, c=colors, marker='o')
#cb = fig.colorbar(colmap)

ax.set_xlabel('Cords')
ax.set_ylabel('Cords')
ax.set_zlabel('Planes')

plt.savefig("3dtopcpu")
