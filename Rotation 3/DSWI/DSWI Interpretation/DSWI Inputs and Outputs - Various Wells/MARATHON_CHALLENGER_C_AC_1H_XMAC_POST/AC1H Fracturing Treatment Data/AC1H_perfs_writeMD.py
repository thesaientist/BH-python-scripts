# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 09:45:03 2018

@author: 212566876
"""
import numpy as np

perfs_data = np.loadtxt('AC1H_Perfs.dat', dtype=float, delimiter='\t', usecols=[0,1,2])

#zData = perfs_data[:,0]
fid = open('AC1H_perfs_md.txt', 'w')
for i in range(perfs_data.shape[0]):
    fid.write(str(perfs_data[i,0]) + '\t')
    fid.write(str(perfs_data[i,1]) + '\n')

fid.close()
