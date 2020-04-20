# ESP_comPartOrg.py
# This script organizes the COMMON data in the PumpData sheet in the ESP configurator
import xlwings as xw
import re           # regular expressions module
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]

    # Import COMMON (com parts) data as an array (list of lists)
    rowCOM = cF.findHeader(pmpDataSht, 'COMMON')
    rowEnd = cF.findHeader(pmpDataSht, 'STAGE GROUP')
    colEnd = pmpDataSht[rowCOM+1,0].end('right').column
    rngCOM = pmpDataSht[rowCOM+1:rowEnd,0:colEnd].options(empty='').value

    # Determine values for necessary column
    colSeries = rngCOM[0].index("Series")
    colStgType = rngCOM[0].index("Stage Type")
    colShaftSize = rngCOM[0].index("Shaft Size")
    colDesignation = rngCOM[0].index("Designation")
    colItemN = rngCOM[0].index("Item Notes")
    colDesc = rngCOM[0].index("Description")

    # Define strings to match in description of the COM PART group (and item notes)
    searchPattern = re.compile("(COM PART,PU?MP) (?P<series>T.) (?P<stgtype1>[a-zA-Z]+)[ -](?P<stgtype2>[a-zA-Z]+) (?P<size>\.\d+)")
    listDesig = ["UHP","NLP","WAG"]

    # Main loop that populates the array (list of lists) for COM PART group data
    for rowi in range(1,len(rngCOM)):
        desc = rngCOM[rowi][colDesc]
        itemN = rngCOM[rowi][colItemN]
        comExtDesc = desc + " " + itemN
        # Search using regular expressions
        descMatch = re.search(searchPattern, comExtDesc)
        if descMatch:
            # Series
            rngCOM[rowi][colSeries] = descMatch.group('series')
            # Stage type
            rngCOM[rowi][colStgType] = descMatch.group('stgtype1') + "-" + descMatch.group('stgtype2')
            # Shaft size
            rngCOM[rowi][colShaftSize] = descMatch.group('size')
        # Designation
        if descMatch.group('series') == "TA":
            rngCOM[rowi][colDesignation] = "NLP"
        else:
            rngCOM[rowi][colDesignation] = ", ".join(dTyp for dTyp in listDesig if dTyp in comExtDesc)

    # Export modified COMMON data back to worksheet
    pmpDataSht[rowCOM+2,0].value = rngCOM[1:]
