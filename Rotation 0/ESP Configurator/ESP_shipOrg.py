# ESP_shipOrg.py
# This script organizes the SHIPPING group data in the ESP configurator
import xlwings as xw
import re           # regular expressions module
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    #wb = xw.Book('ESP_config.xlsm')
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]

    # Import Shipping data as an array (list of lists)
    rowSHP = cF.findHeader(pmpDataSht, 'SHIPPING GROUP')
    rowEnd = cF.findHeader(pmpDataSht, 'COAT/PAINT GROUP')
    colEnd = pmpDataSht[rowSHP+1,0].end('right').column
    rngSHP = pmpDataSht[rowSHP+1:rowEnd,0:colEnd].options(empty='').value

    # Determine values for necessary column
    colSeries = rngSHP[0].index("Series")
    colItemN = rngSHP[0].index("Item Notes")
    colDesc = rngSHP[0].index("Description")

    # Define strings to match in description of the SHIPPING group (and item notes)
    searchPattern = re.compile("T.")

    # Main loop that populates the array (list of lists) for SHIPPING group data
    for rowi in range(1,len(rngSHP)):
        desc = rngSHP[rowi][colDesc]
        itemN = rngSHP[rowi][colItemN]
        shipExtDesc = desc + " " + itemN
        # Search using regular expressions
        descMatch = re.search(searchPattern, shipExtDesc)
        if descMatch:
            # Series
            rngSHP[rowi][colSeries] = descMatch.group(0)

    # Export modified SHIPPING data back to worksheet
    pmpDataSht[rowSHP+2,0].value = rngSHP[1:]
