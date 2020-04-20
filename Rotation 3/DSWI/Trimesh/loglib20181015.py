"""
Baker Hughes Python LAS support
################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Tobias Hoeink
##    tobias.hoeink@bhge.com
##
################################################################################
"""

# Still missing:
# - unit conversion
# - resampling (use interp?)

import numpy as np

# class definitions

class Channel(object):
    """Channel object"""

    def __init__(self, line=None, mnem=None, data=[], description=None, unit=None, nullvalue=None):
        self.mnem = mnem
        self.unit = unit
        self.nullvalue = nullvalue
        self.data = []
        for d in data:
            self.addData(d)
        self.description = description

        if line:
            self.mnem = line.split('.')[0].strip()
            self.unit = line.split('.')[1].split(' ')[0].strip()
            self.description = line.split(':')[-1].strip()

    def __repr__(self):
        s = 'Channel: %s.%s (len=%d)' % (self.mnem, self.unit, len(self.data))
        return s

    def setNullvalue(self, v):
        self.nullvalue = v
        return

    def addData(self, d):
        self.data.append(d)
        return

    def setData(self, d):
        self.data = d
        return

    def getData(self, masked=False):
        if masked:
            # return np.ma.masked_values(self.data, self.nullvalue)
            return np.ma.masked_not_equal(self.data, self.nullvalue)
        else:
            return np.array(self.data)

    def getMask(self):
        ans = self.getData(masked=True)
        return ans.mask

    def getMnem(self):
        return self.mnem

    def changeToUnit(self, unit=None):
        print('not implemented yet')
        return


class LogData(object):
    """LogData object"""

    def __init__(self, fname=None):
        self.channels = []
        self.nullvalue = None
        self.versionInfo = ''
        self.wellInfo = ''
        if fname:
            self.loadFromLAS(fname)

    def __repr__(self):
        s = 'Log with %d data channels: ' % len(self.channels)
        for d in self.channels:
            s += '\n  ' + d.__repr__()
        return s

    def loadFromLAS(self, fname):
        self.channels = []
        self.versionInfo = ''
        self.wellInfo = ''

        scope = None

        for line in open(fname):

            if line[0] == '#':
                scope = 'Comment'

            if scope == 'CurveDef':
                if len(line) > 1:
                    ch = Channel(line=line)
                    self.addChannel(ch)
                    if self.nullvalue:
                        ch.setNullvalue(self.nullvalue)

            elif scope == 'CurveData':
                try:
                    d = map(float, line.split())
                except:
                    d = []
                    for dd in line.split():
                        try:
                            d.append(float(dd))
                        except:
                            d.append(dd)

                # print ' '
                # print 'd = ', d
                for i, x in enumerate(d):
                    # print '\ti,x = ', i,x
                    self.channels[i].addData(x)

            elif scope == 'WellDef':
                self.wellInfo += line
                if line[:4] == 'NULL':
                    self.nullvalue = float('.'.join(line.split('.')[1:]).split(':')[0].split()[-1])

            elif scope == 'Version':
                self.versionInfo += line

            # set scope
            if line[:2] == '~C':
                scope = 'CurveDef'
                self.channels = []

            elif line[:2] == '~A':
                scope = 'CurveData'

            elif line[:2] == '~W':
                scope = 'WellDef'

            elif line[:2] == '~V':
                scope = 'Version'

    def writeLAS(self, fname):
        sepLine = '#==================================================================\n'
        f = open(fname, 'w')
        f.write('# Created by JewelSuite 6 Geomechanics / Python')
        f.write(sepLine)

        f.write('~Version\n')
        f.write(self.versionInfo)
        f.write(sepLine)

        f.write('~Well\n')
        f.write(self.wellInfo)
        f.write(sepLine)

        f.write('~Curve\n')
        for ch in self.channels:
            s = '%-4s .%s        :%s\n' % (ch.mnem, ch.unit, ch.description)
            f.write(s)
        f.write('\n')
        f.write(sepLine)

        f.write('~Ascii\n')
        A = [ch.data for ch in self.channels]
        for i in range(len(self.channels[0].getData())):
            s = ''
            for j in range(len(self.channels)):
                s += '%s ' % str(A[j][i])
            s += '\n'
            f.write(s)

        f.close()
        return

    def setHeader(self, log):
        self.versionInfo = log.versionInfo
        self.wellInfo = log.wellInfo
        return

    def getChannels(self):
        return self.channels

    def getChannel(self, mnem):
        ans = [ch for ch in self.getChannels() if ch.mnem.upper() == mnem.upper()]
        if len(ans) > 0:
            ans = ans[0]
        else:
            ans = None
        return ans

    def addChannel(self, ch):
        self.channels.append(ch)
        return

    def getData(self, masked=False):
        if not masked:
            return [ch.getData(masked) for ch in self.channels]
        else:
            masks = [ch.getData(masked).mask for ch in self.channels]
            mask = np.prod(masks)
            return [ch.getData()[mask] for ch in self.channels]

    def getMnems(self):
        return [c.getMnem() for c in self.getChannels()]

    def getMask(self):
        mask = True
        for ch in self.getChannels():
            mask = mask * ch.getMask()
        return mask

# USER CODE STARTS HERE
def run():
    # input logs
    log1 = LogData('Well-A_Dens.LAS')
    log2 = LogData('Well-A_GammeRay.LAS')

    # output logs
    litho = LogData()
    vshale = LogData()

    # copy well information from input logs
    litho.setHeader(log1)
    vshale.setHeader(log1)

    # copy depth channel
    vshale.addChannel(log2.getChannel('DEPT'))
    litho.addChannel(log2.getChannel('DEPT'))

    # compute Vshale log based on min and max GRmax
    gr_data = log2.getChannel('GammeRay').getData()
    GRmin = min(gr_data)
    GRmax = max(gr_data)
    new_data = [100.*(i-GRmin)/(GRmax-GRmin) for i in gr_data]

    ch = Channel(mnem='VSH', description='Vshale', unit='%')
    ch.setData(new_data)
    vshale.addChannel(ch)

    # create lithology based on GR and density filters
    density = log1.getChannel('Dens').getData()
    gr_data = log2.getChannel('GammeRay').getData()
    GR_cutoff = 150.
    DENS_cutoff = 1.7

    ch = Channel(mnem='LITHO', description='Lithology', unit='Lithology')
    for i, gr in enumerate(gr_data):
        if gr > GR_cutoff:
            ch.addData('Shale')
        else:
            if density[i] < DENS_cutoff:
                ch.addData('Coal')
            else:
                ch.addData('Sand')

    litho.addChannel(ch)

    # save new log to LAS files
    vshale.writeLAS('Well-A_VSH.LAS')
    litho.writeLAS('Well-A_LITHO.LAS')
