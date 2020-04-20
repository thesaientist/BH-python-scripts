################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################

import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm

# Get historical data into arrays
years_hist = np.arange(1936, 2019)
years_dt = []
for i in range(len(years_hist)):
    years_dt.append(datetime.datetime(years_hist[i], 12, 31))
yearsFmt = mdates.DateFormatter('%Y')
years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month

# Load historical and field name data (already in rates)
oil_hist = np.load('../oil_hist.npy')
gas_hist = np.load('../gas_hist.npy')
water_hist = np.load('../water_hist.npy')
fields = np.load('../../fields.npy')

# min/max for plots
min_liquid = np.nanmin(np.array([np.nanmin(oil_hist), np.nanmin(water_hist)]))
if min_liquid <= 0:
    min_liquid = 1
max_liquid = np.nanmax(np.array([np.nanmax(oil_hist), np.nanmax(water_hist)]))
min_gas = np.nanmin(gas_hist)
if min_gas <= 0:
    min_gas = 1
max_gas = np.nanmax(gas_hist)

# plot historical production
arial_font = fm.FontProperties(family='arial', size=8)
# arial_font.set_family('arial')
for i in range(len(fields)):
    # plot 1 (oil, water and gas)
    fig, ax1 = plt.subplots()
    ln1 = ax1.semilogy(years_dt, oil_hist[:, i], 'g-', label='Oil')
    ln2 = ax1.semilogy(years_dt, water_hist[:, i], 'b-', label='Water')
    # ax1.yaxis.grid(which="major", linestyle='-', linewidth=1)
    # ax1.yaxis.grid(which="minor", linestyle='-', linewidth=0.5)
    ax1.set_ylim(min_liquid, max_liquid)
    # ax1.set_xlim(years_dt[0], years_dt[-1])
    ax1.xaxis.set_major_locator(years)
    ax1.xaxis.set_major_formatter(yearsFmt)
    ax1.xaxis.set_minor_locator(years)
    ax1.set_xlabel('Year', fontname='Arial', fontsize=8)
    ax1.set_ylabel('Liquid Rate (BPD)', fontname='Arial', fontsize=8)
    for tick in ax1.get_xticklabels():
        tick.set_fontname("Arial")
    for tick in ax1.get_yticklabels():
        tick.set_fontname("Arial")

    ax2 = ax1.twinx()
    ln3 = ax2.semilogy(years_dt, gas_hist[:, i], 'r-', label='Gas')
    ax2.set_ylim(min_gas, max_gas)
    ax2.set_ylabel('Gas Rate (MCFD)', color='r', fontname='Arial', fontsize=8)
    for tick in ax2.get_xticklabels():
        tick.set_fontname("Arial")
    for tick in ax2.get_yticklabels():
        tick.set_fontname("Arial")

    # legend display
    lns = ln1 + ln2 + ln3
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc=0, prop=arial_font)

    # Date labels look better
    fig.autofmt_xdate()

    fig.suptitle('{} Field, Colombia History'.format(fields[i]), fontname='Arial', fontsize=8)
    fig.tight_layout()
    # plt.show()
    plt.savefig('./{}_history.png'.format(fields[i]))
    plt.close()
