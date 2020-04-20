# ESP_cplgOrg.py
# This script organizes the COUPLING data in the ESP configurator
import xlwings as xw
import re           # regular expressions module
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]

    # Import COUPLING data as an array (list of lists)
    rowCPLG = cF.findHeader(pmpDataSht, 'COUPLING')
    rowEnd = pmpDataSht[rowCPLG+1,0].end('down').row
    colEnd = pmpDataSht[rowCPLG+1,0].end('right').column
    rngCPLG = pmpDataSht[rowCPLG+1:rowEnd,0:colEnd].value

    # Determine values for necessary column
    colSeries = rngCPLG[0].index("Series")
    colStgType = rngCPLG[0].index("Stage Type")
    colSize = rngCPLG[0].index("Size")
    colMat = rngCPLG[0].index("Material")
    colMS = rngCPLG[0].index("MS")
    colItemN = rngCPLG[0].index("Item Notes")
    colDesc = rngCPLG[0].index("Description")

    # Define strings to match description of coupling (and item notes)
    searchPattern = re.compile("CO?U?PLI?N?G,PU?MP (?P<series>T.) (?P<stgtype>\w+) (?P<size>\d+/\d+)")
    matList = ["MNL","NIT","INC"]

    # Main loop that populates the array (list of lists) for coupling data
    for rowi in range(1,len(rngCPLG)):
        desc = rngCPLG[rowi][colDesc]
        itemN = rngCPLG[rowi][colItemN]
        if itemN is None:
            itemN = ""
        cplgExtDesc = desc + " " + itemN
        # Search description using regular expressions
        descMatch = re.search(searchPattern, cplgExtDesc)
        if descMatch:
            # Series
            rngCPLG[rowi][colSeries] = descMatch.group('series')
            # Stage type
            rngCPLG[rowi][colStgType] = descMatch.group('stgtype')
            # Shaft size
            rngCPLG[rowi][colSize] = descMatch.group('size')
        # Material
        rngCPLG[rowi][colMat] = ", ".join(cMat for cMat in matList if cMat in cplgExtDesc)

    # Export modified COUPLING data back to the worksheet
    pmpDataSht[rowCPLG+2,0].value = rngCPLG[1:]
