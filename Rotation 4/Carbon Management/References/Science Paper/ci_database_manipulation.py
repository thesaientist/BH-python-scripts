# -*- coding: utf-8 -*-
"""
Created on Mon Apr 6 2020

@author: 212566876
"""

#import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import ciDatabase

# start timer
startTime = datetime.now()

# create ciDatabase class object for all further data manipulation
ciDB = ciDatabase.ciDatabase()

# generate source dataframe (categorized)
# ciDB.create_sourceData_dataframe(True)
# sourceData = ciDB.get_source_dataframe()

# find local ci_database.pkl file and load dataframe, otherwise 
# match fields between source dataframe and output ci database excel sheet
# and populate field metdata in excel and then convert to dataframe
ciDB.create_ci_dataframe()
cidf = ciDB.get_ci_dataframe()
df = cidf.dropna(subset=['Basin'])    # subset of CI dataset that has been categorized

# ------------------------------------
# Offshore fields
# ------------------------------------
offshoreFilter = df['On/Offshore']=='Offshore'
offshore_df = df[offshoreFilter]
offshore_subset = ciDatabase.ciSubset('Offshore', offshore_df)
offshore_subset.groupby_vwavg_ci('Archetype')
offshore_avgs = offshore_subset.get_averages()

# print time taken to execute script
print(datetime.now() - startTime)

# # generate emissions breakdown plot for each field
# N = len(emissions.index)
# ind = np.arange(N)
# dndCI = emissions['Drilling Combustion CI']
# prodCI = emissions['Production Combustion CI']
# procCI = emissions['Processing Combustion CI']
# mainCI = emissions['Maintenance Combustion CI']
# vffCI = emissions['Total VFF CI']
# miscCI = emissions['Miscellaneous CI']
# transCI = emissions['Transportation CI']
# offsiteCI = emissions['Offsite CI']
#
# fieldLabels = emissions['Field'].tolist()
# # legendLabels = ['Drilling', 'Production', 'Processing', 'Maintenance', 'VFF', \
# #                 'Misc.', 'Transport']
#
# fig, ax = plt.subplots()
# width = 0.75
# # color=(45/255, 96/255, 179/255, 0.8)  # color for exploration bar if ever added
# dnd_bar = ax.bar(ind, dndCI, width, label='Drilling', \
#                  color=(232/255, 159/255, 12/255, 0.8))
# prod_bar = ax.bar(ind, prodCI, width, bottom=dndCI, label='Production', \
#                   color=(7/255, 71/255, 77/255, 0.8))
# proc_bar = ax.bar(ind, procCI, width, bottom=dndCI + prodCI, \
#                   label='Processing', color=(247/255, 208/255, 12/255, 0.8))
# main_bar = ax.bar(ind, mainCI, width, bottom=dndCI + prodCI + procCI, \
#             label='Maintenance', color=(201/255, 195/255, 0, 0.8))
# vff_bar = ax.bar(ind, vffCI, width, bottom=dndCI + prodCI + procCI + \
#             mainCI, label='VFF', color=(225/255, 10/255, 0, 0.8))
# misc_bar = ax.bar(ind, miscCI, width, bottom=dndCI + prodCI + procCI + \
#             mainCI + vffCI, label='Misc.', color=(164/255,225/255,237/255,0.8))
# trans_bar = ax.bar(ind, transCI, width, bottom=dndCI + prodCI + procCI + \
#             mainCI + vffCI + miscCI, label='Transport', \
#             color=(69/255,74/255,65/255,0.8))
# offsite_bar = ax.bar(ind, offsiteCI, width, bottom=dndCI + prodCI + procCI + \
#             mainCI + vffCI + miscCI + transCI, label='Offsite', \
#             color=(0,128/255,1,0.8))
#
# ax.set_title('GHG Emissions Intensity Comparison')
# ax.set_xticks(ind.tolist())
# ax.set_xticklabels(fieldLabels)
# ax.set_ylabel('GHG Intensity (gCO2e/MJ crude oil)')
# # ax.set_ytick
#
# # Shrink current axis by 20%
# box = ax.get_position()
# ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
#
# handles, labels = ax.get_legend_handles_labels()
# ax.legend(handles[::-1], labels[::-1], loc='center left', \
#           bbox_to_anchor=(1, 0.5))
# # ax.legend()
#
# plt.savefig('emissions_breakdown.png', dpi=300)
