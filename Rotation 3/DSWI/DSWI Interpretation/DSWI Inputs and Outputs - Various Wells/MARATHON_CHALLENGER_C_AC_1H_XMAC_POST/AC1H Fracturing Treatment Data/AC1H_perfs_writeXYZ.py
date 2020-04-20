# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 09:45:03 2018

@author: 212566876
"""
import numpy as np
import XMAClib2018 as xmacLib

wellSurveyData, _ = xmacLib.parseWellSurvey('C:\\Users\\212566876\\Box Sync\\Rotation 3\\DSWI\\Marathon_Challenger_C_AC_1H_XMAC_PRE\\C_AC_1H.well.trajectory.txt')

perfs_data = np.loadtxt('AC1H_perfs_md.txt', dtype=float, delimiter='\t')
start_idx = np.argmin(np.absolute(perfs_data[:,1]-14))
end_idx = np.argmin(np.absolute(perfs_data[:,1]-17))
perfs_data = perfs_data[start_idx:end_idx,:]

#zData = perfs_data[:,0]
fid = open('AC1H_Perfs_stg14-16.txt', 'w')
fid.write('x y z\n')
fid.write('ft ft ft\n')
for i in range(perfs_data.shape[0]):
    md = perfs_data[i,0]
    x, y, z = xmacLib.wellInterp(md, wellSurveyData)
    fid.write(str(x) + ' ' + str(y) + ' ' + str(z) + '\n')
fid.close()
