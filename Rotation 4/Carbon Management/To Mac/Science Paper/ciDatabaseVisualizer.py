# -*- coding: utf-8 -*-
"""
Created on Wed Apr 8 2020

@author: 212566876
"""

import seaborn as sns
import matplotlib.pyplot as plt
# import openpyxl
import pandas as pd
import numpy as np
from datetime import datetime

# start timer
startTime = datetime.now()

# import CI database from excel into pandas dataframe
ciData = pd.read_excel (r'./Carbon Intensity - Global Dataset of Fields.xlsx', sheet_name='CI Database')
cidf = pd.DataFrame(ciData, columns=['Country','Field','Basin','Block / Contract', \
                                    'Province','Production Type','On/Offshore', \
                                    'Depth/Elevation (ft)','Archetype', \
                                    'Production Start Year', 'Company 1/Operator', \
                                    'Operator Type','Company 1/Operator Interest (%)', \
                                    'Company 2','Company 2 Interest (%)','Company 3', \
                                    'Company 3 Interest (%)','Company 4', \
                                    'Company 4 Interest (%)','Company 5', \
                                    'Company 5 Interest (%)','Company 6', \
                                    'Company 6 Interest (%)','Company 7', \
                                    'Company 7 Interest (%)','Production (bbl/d)', \
                                    'EXPLORATION CI (gCO2e/MJ)','DRILLING CI (gCO2e/MJ)', \
                                    'PRODUCTION CI (gCO2e/MJ)','PROCESSING CI (gCO2e/MJ)', \
                                    'MAINTENANCE CI (gCO2e/MJ)','VFF CI (gCO2e/MJ)', \
                                    'MISCELLANEOUS CI (gCO2e/MJ)','TRANSPORT CI (gCO2e/MJ)', \
                                    'OFFSITE EMISSIONS CREDIT/DEBIT CI (gCO2e/MJ)', \
                                    'CO2 SEQUESTRATION CI (gCO2e/MJ)', 'CI (gCO2e/MJ)'
                                    ])

# define subsets for useful comparisons and plots
df = cidf.dropna(subset=['Basin'])
#subsetOnshorevOffshore = cidf[(cidf['On/Offshore'] == 'Onshore') | (cidf['On/Offshore'] == 'Offshore')]
#ssOnOff2 = subsetOnshorevOffshore.drop(subsetOnshorevOffshore[subsetOnshorevOffshore['Field']=='Beatrice'].index)   # drop outlier in Offshore
#ssOnOff2.drop(ssOnOff2[ssOnOff2['Field']=='Gilli Gilli'].index, inplace=True)   # drop outlier in onshore
northSeaDF = df[df['Province'].str.contains('North Sea')]


# plot benchmarking plots and statistical distributions

# PLOT: archetypes CI distribution comparison (excluding outliers)
df_archetype = df.sort_values(['Archetype'])
ax = sns.boxplot(x='Archetype', y='CI (gCO2e/MJ)', data=df_archetype)
ax.set_ylim(0,100)      # limits how many outliers to show
ax.set_title('Archetype Oilfield Carbon Intensity Distributions \n (excludes extreme outliers)')
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
plt.tight_layout()
plt.savefig('archetype_CI_distributions.png',dpi=300)

# PLOT: archetypes CI averages breakdown
archetype_avgs = df_archetype.groupby(['Archetype']).mean()
N = len(archetype_avgs.index)
ind = np.arange(N)
dndCI = archetype_avgs['DRILLING CI (gCO2e/MJ)']
prodCI = archetype_avgs['PRODUCTION CI (gCO2e/MJ)']
procCI = archetype_avgs['PROCESSING CI (gCO2e/MJ)']
mainCI = archetype_avgs['MAINTENANCE CI (gCO2e/MJ)']
vffCI = archetype_avgs['VFF CI (gCO2e/MJ)']
miscCI = archetype_avgs['MISCELLANEOUS CI (gCO2e/MJ)']
transCI = archetype_avgs['TRANSPORT CI (gCO2e/MJ)']
offsiteCI = archetype_avgs['OFFSITE EMISSIONS CREDIT/DEBIT CI (gCO2e/MJ)']
netCI = archetype_avgs['CI (gCO2e/MJ)']

fieldLabels = archetype_avgs.index.tolist()
# legendLabels = ['Drilling', 'Production', 'Processing', 'Maintenance', 'VFF', \
#                 'Misc.', 'Transport']

fig, ax = plt.subplots()
width = 0.75
# color=(45/255, 96/255, 179/255, 0.8)  # color for exploration bar if ever added
dnd_bar = ax.bar(ind, dndCI, width, label='Drilling', \
                 color=(232/255, 159/255, 12/255, 0.8))
prod_bar = ax.bar(ind, prodCI, width, bottom=dndCI, label='Production', \
                  color=(7/255, 71/255, 77/255, 0.8))
proc_bar = ax.bar(ind, procCI, width, bottom=dndCI + prodCI, \
                  label='Processing', color=(247/255, 208/255, 12/255, 0.8))
main_bar = ax.bar(ind, mainCI, width, bottom=dndCI + prodCI + procCI, \
            label='Maintenance', color=(201/255, 195/255, 0, 0.8))
vff_bar = ax.bar(ind, vffCI, width, bottom=dndCI + prodCI + procCI + \
            mainCI, label='VFF', color=(225/255, 10/255, 0, 0.8))
misc_bar = ax.bar(ind, miscCI, width, bottom=dndCI + prodCI + procCI + \
            mainCI + vffCI, label='Misc.', color=(164/255,225/255,237/255,0.8))
trans_bar = ax.bar(ind, transCI, width, bottom=dndCI + prodCI + procCI + \
            mainCI + vffCI + miscCI, label='Transport', \
            color=(69/255,74/255,65/255,0.8))
offsite_bar = ax.bar(ind, offsiteCI, width, bottom=dndCI + prodCI + procCI + \
            mainCI + vffCI + miscCI + transCI, label='Offsite', \
            color=(0,128/255,1,0.8))
netCI_marker = ax.plot(ind, netCI, 'k*', label='Net CI')

ax.set_title('Archetype Oilfields Average Carbon Intensities')
ax.set_xticks(ind.tolist())
ax.set_xticklabels(fieldLabels)
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
ax.set_ylabel('CI (gCO2e/MJ)')
# ax.set_ytick

# Shrink current axis by 20%
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.width*0.2, box.width*0.8, box.height*0.8])

handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1], loc='center left', \
          bbox_to_anchor=(1, 0.5))

plt.savefig('archetype_avgs_breakdown.png', dpi=300)

# PLOT: North Sea field CIs
northSeaDF = northSeaDF.sort_values(['CI (gCO2e/MJ)'])
N = len(northSeaDF.index)
ind = np.arange(N)
dndCI = northSeaDF['DRILLING CI (gCO2e/MJ)']
prodCI = northSeaDF['PRODUCTION CI (gCO2e/MJ)']
procCI = northSeaDF['PROCESSING CI (gCO2e/MJ)']
mainCI = northSeaDF['MAINTENANCE CI (gCO2e/MJ)']
vffCI = northSeaDF['VFF CI (gCO2e/MJ)']
miscCI = northSeaDF['MISCELLANEOUS CI (gCO2e/MJ)']
transCI = northSeaDF['TRANSPORT CI (gCO2e/MJ)']
offsiteCI = northSeaDF['OFFSITE EMISSIONS CREDIT/DEBIT CI (gCO2e/MJ)']
netCI = northSeaDF['CI (gCO2e/MJ)']

fieldLabels = northSeaDF['Field'].tolist()
# legendLabels = ['Drilling', 'Production', 'Processing', 'Maintenance', 'VFF', \
#                 'Misc.', 'Transport']

fig, ax = plt.subplots()
width = 0.05
# color=(45/255, 96/255, 179/255, 0.8)  # color for exploration bar if ever added
dnd_bar = ax.bar(ind, dndCI, width, label='Drilling', \
                 color=(232/255, 159/255, 12/255, 0.8))
#prod_bar = ax.bar(ind, prodCI, width, bottom=dndCI, label='Production', \
#                  color=(7/255, 71/255, 77/255, 0.8))
proc_bar = ax.bar(ind, procCI, width, bottom=dndCI + prodCI, \
                  label='Processing', color=(247/255, 208/255, 12/255, 0.8))
main_bar = ax.bar(ind, mainCI, width, bottom=dndCI + prodCI + procCI, \
            label='Maintenance', color=(201/255, 195/255, 0, 0.8))
vff_bar = ax.bar(ind, vffCI, width, bottom=dndCI + prodCI + procCI + \
            mainCI, label='VFF', color=(225/255, 10/255, 0, 0.8))
misc_bar = ax.bar(ind, miscCI, width, bottom=dndCI + prodCI + procCI + \
            mainCI + vffCI, label='Misc.', color=(164/255,225/255,237/255,0.8))
trans_bar = ax.bar(ind, transCI, width, bottom=dndCI + prodCI + procCI + \
            mainCI + vffCI + miscCI, label='Transport', \
            color=(69/255,74/255,65/255,0.8))
offsite_bar = ax.bar(ind, offsiteCI, width, bottom=dndCI + prodCI + procCI + \
            mainCI + vffCI + miscCI + transCI, label='Offsite', \
            color=(0,128/255,1,0.8))
netCI_marker = ax.plot(ind, netCI, 'k*', label='Net CI')

ax.set_title('North Sea Fields Carbon Intensities')
ax.set_xticks(ind.tolist())
ax.set_xticklabels(fieldLabels)
ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha="right")
ax.set_ylabel('CI (gCO2e/MJ)')
# ax.set_ytick

# Shrink current axis by 20%
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.width*0.2, box.width*0.8, box.height*0.8])

handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1], loc='center left', \
          bbox_to_anchor=(1, 0.5))

plt.savefig('North Sea Fields CI.png', dpi=300)





