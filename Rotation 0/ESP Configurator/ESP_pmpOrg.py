# ESP_pmpOrg.py
# This script organizes the EXISTING ESP PUMP data in the PumpData sheet of the ESP configurator
import xlwings as xw
import re           # regular expressions module
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]

    # Import EXISTING ESP PUMP data as an array (list of lists)
    rowPMP = cF.findHeader(pmpDataSht, 'EXISTING ESP PUMPS')
    rowEnd = cF.findHeader(pmpDataSht, 'COMMON')
    colEnd = pmpDataSht[rowPMP+1,0].end('right').column
    rngPMP = pmpDataSht[rowPMP+1:rowEnd,0:colEnd].value

    # Determine values for necessary column
    colSeries = rngPMP[0].index("Series")
    colBPD = rngPMP[0].index("BPD")
    colType = rngPMP[0].index("Type")
    colHsgNum = rngPMP[0].index("Housing Number")
    colStgCount = rngPMP[0].index("Stage Count")
    colDesc = rngPMP[0].index("Description")

    # Define strings to match in description of pumps
    searchPattern1 = re.compile("PU?MP,(?P<series>T.) ?(?P<BPD>\d+) (?P<stgtype>[a-zA-Z]+) (?P<stgcount>\d+)STG \#(?P<hsgnum>\d+)")
    searchPattern2 = re.compile("PU?MP,(?P<series>T.) ?(?P<BPD>\d+) (?P<stgtype1>[a-zA-Z]+)[ -](?P<stgtype2>[a-zA-z]+) (?P<stgcount>\d+)/\d+B \#(?P<hsgnum>\d+)")
    SPs = [searchPattern1, searchPattern2]

    # Main loop that populates the array (list of lists) for PUMP data
    for rowi in range(1,len(rngPMP)):
        desc = rngPMP[rowi][colDesc]
        # Search using regular expressions
        descMatch = [re.search(SP, desc) for SP in SPs]
        if any(descMatch):
            ind = [i for i,v in enumerate(descMatch) if v][0]
            # Series
            rngPMP[rowi][colSeries] = descMatch[ind].group('series')
            # BPD
            rngPMP[rowi][colBPD] = descMatch[ind].group('BPD')
            # Type
            if ind == 0:
                rngPMP[rowi][colType] = descMatch[ind].group ('stgtype')
            else:
                rngPMP[rowi][colType] = descMatch[ind].group('stgtype1') + "-" + \
                                        descMatch[ind].group('stgtype2')
            # Housing number
            rngPMP[rowi][colHsgNum] = descMatch[ind].group('hsgnum')
            # Stage count
            rngPMP[rowi][colStgCount] = descMatch[ind].group('stgcount')

    # Export modified PUMP data back to worksheet
    pmpDataSht[rowPMP+2,0].value = rngPMP[1:]
