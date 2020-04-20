################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2019
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################

import os
import pandas as pd
# import openpyxl
# import openpyxl_lib as xlLib
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import datetime
import matplotlib.dates as mdates
# import matplotlib.backends.backend_pdf

# read in history from Fekete tab in history excel Workbook
history_df = pd.read_excel('For SPU History per well_Fekette.xlsx', sheet_name='Fekete', index_col=0)
# print(history_df['FECHA'].head(10))

# group by date and sum for fields
history_df = history_df.set_index('FECHA')
coyol_history_df = history_df.groupby([pd.Grouper(freq="D"), 'CAMPO']).sum().reset_index()
coyol_history_df = coyol_history_df.set_index('FECHA')
coyol_2013 = coyol_history_df.loc['2013-01-01':'2018-12-31'].reset_index()
# print(coyol_2013)

# plot history
fig, ax1 = plt.subplots()
ax1.semilogy(coyol_2013['FECHA'], coyol_2013['NP_monthly']/1000, 'g.', label='Oil')
ax1.set_ylabel('Oil, MBBL/M')
ax1.tick_params(axis='y', labelcolor='g')
ax1.minorticks_on()

ax2 = ax1.twinx()   # instantiate a second axes that shares the same x-axis
ax2.semilogy(coyol_2013['FECHA'], coyol_2013['GP_monthly'], 'r.', label='Gas')
ax2.set_ylabel('Gas, MMPCD/M')
ax2.tick_params(axis='y', labelcolor='r')


fig.suptitle('Coyol History')
#fig.tight_layout()
ax1.grid()
plt.show()
