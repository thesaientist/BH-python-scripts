# ESP_ldfOrg.py
# This script organizes the LOWER DIFFUSER data in the ESP configurator
import xlwings as xw
import re           # regular expressions module
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]

    # Import LOWER DIFFUSER data as an array (list of lists)
    rowLDF = cF.findHeader(pmpDataSht, 'LOWER DIFFUSER')
    rowEnd = cF.findHeader(pmpDataSht, 'KEYSTOCK')
    colEnd = pmpDataSht[rowLDF+1,0].end('right').column
    rngLDF = pmpDataSht[rowLDF+1:rowEnd,0:colEnd].value

    # Determine values for necessary column
    colSeries = rngLDF[0].index("Series")
    colBPD = rngLDF[0].index("BPD")
    colType1= rngLDF[0].index("Type 1")
    colType2= rngLDF[0].index("Type 2")
    colMat = rngLDF[0].index("Material")
    colCoat = rngLDF[0].index("Coating Material")
    colMS = rngLDF[0].index("MS")
    colItemN = rngLDF[0].index("Item Notes")
    colDesc = rngLDF[0].index("Description")

    # Define strings to match in description of the lower diffuser (and item notes)
    searchPattern = re.compile("DIFFUSER,LO?WE?R (?P<series>T.) ?(?P<BPD1>\d+)/?(?P<BPD2>\d+)?")
    StageTypes = ["CMP","FLT","C/F"]
    type2List = [re.compile("P-MA?CH"),re.compile("CA?ST"),re.compile("MA?CH")]
    matList = ["N1","N2","N3","N4","DPX","SDX","3SS","CI"]
    coatType = ["NDP","FPS","CRP","SF2","DGS","BDP"]

    # Main loop that populates the array (list of lists) for lower diffuser data
    for rowi in range(1,len(rngLDF)):
        desc = rngLDF[rowi][colDesc]
        itemN = rngLDF[rowi][colItemN]
        if itemN is None:
            itemN = ""
        ldfExtDesc = desc + " " + itemN
        # Search description using regular expressions
        descMatch = re.search(searchPattern, ldfExtDesc)
        if descMatch:
            # Series
            rngLDF[rowi][colSeries] = descMatch.group('series')
            # BPD1
            rngLDF[rowi][colBPD] = descMatch.group('BPD1')
            # BPD2 (if at all)
            if descMatch.group('BPD2') is not None:
                rngLDF[rowi][colBPD] = rngLDF[rowi][colBPD] + "/" + descMatch.group('BPD2')
        # Type 1 (stage type)
        type1Match = [re.search(s, ldfExtDesc) for s in StageTypes]
        if any(type1Match):
            firstMatchIndex = [i for i,v in enumerate(type1Match) if v][0]
            sTyp = type1Match[firstMatchIndex].group(0)
            # If combo stage type found, then spell out the types
            if sTyp == "C/F":
                sTyp = "CMP/FLT"
            rngLDF[rowi][colType1] = sTyp
        # Type 2
        type2Match = [re.search(t, ldfExtDesc) for t in type2List]
        if any(type2Match):
            firstMatchIndex = [i for i,v in enumerate(type2Match) if v][0]
            tTyp = type2Match[firstMatchIndex].group(0)
            # correct abbreviations if needed
            if tTyp == "P-MCH":
                tTyp = "P-MACH"
            elif tTyp == "CAST":
                tTyp = "CST"
            elif tTyp == "MCH":
                tTyp = "MACH"
            rngLDF[rowi][colType2] = tTyp
        # Material (stg material)
        if any(sMat in ldfExtDesc for sMat in matList):
            rngLDF[rowi][colMat] = ", ".join(sMat for sMat in matList if sMat in ldfExtDesc)
        else:
            rngLDF[rowi][colMat] = "N1"
        # Coating type
        rngLDF[rowi][colCoat] = ", ".join(cTyp for cTyp in coatType if cTyp in ldfExtDesc)

    # Export modified LOWER DIFFUSER data back to worksheet
    pmpDataSht[rowLDF+2,0].value = rngLDF[1:]
