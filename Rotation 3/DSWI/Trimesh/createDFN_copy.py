################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Tobias Hoeink
##    tobias.hoeink@bhge.com
##
################################################################################
import numpy as np
import DFNlib20181015 as DFNlib
import loglib20181015 as loglib

if 0:
    fname_las = 'DSWI_CR6H_ChapmanRothe_Post_Contour82.las'
    fname_path = 'CR6H.path'
else:
    fname_las = 'DSWI_AC1H_Challenger_Post_Contour82.las'
    fname_path = 'AC1H.path'

las = loglib.LogData(fname_las)
# path = np.loadtxt(fname_path, unpack=1, usecols=[4,5,6])
#path = np.loadtxt(fname_path, unpack=1, usecols=[0, 1, 2, 4, 5, 6])

class Path():
    pass

def load_path(fname_path):
    d = np.loadtxt(fname_path, unpack=1, usecols=[0, 1, 2, 4, 5, 6, 7, 8, 9])
    path = Path()
    path.md = d[0]
    path.azi = d[1]
    path.inc = d[2]
    path.x = d[3]
    path.y = d[4]
    path.z = d[5]
    path.dx = d[6]
    path.dy = d[7]
    path.dz = d[8]
    return path

def interpolate_from_path(md, path):
    x = np.interp(md, path.md, path.x)
    y = np.interp(md, path.md, path.y)
    z = np.interp(md, path.md, path.z)
    azi = np.interp(md, path.md, path.azi)
    return x,y,z, azi


path = load_path(fname_path)

dfn = DFNlib.DFN()
for d in np.array(las.getData()).T[::10]:
    md, hzup, hzdn, vtdn, vtup, intn = d
    x0, y0, z0, azi = interpolate_from_path(md, path)
    dx = hzup
    dy = hzdn
    p1 = DFNlib.Point(coords=(0, 0, 0))
    p2 = DFNlib.Point(coords=(0, 0, 0+vtup))
    p3 = DFNlib.Point(coords=(0, 0, 0+vtdn))
    p4 = DFNlib.Point(coords=(0+hzup, 0, 0))
    p5 = DFNlib.Point(coords=(0+hzdn, 0, 0))
    f = DFNlib.Fracture([p2,p4,p3,p5])
    f.setProperty('intn', intn)
    ##f.setNormal([0, 1, 0])
    # f.setNormal([path.dy[-1], path.dy[-1], 0])
    f.rotateHorizontally(-azi/180.*np.pi)

    # rotate to account for inclindation
    incl = ...
#    v2 = (index finger)
    v2 = f.getNormal().cross(DFNlib.Vector([0,0,1]))
    v2.normalize()
    f.rotate(v2, incl)

    f.translate(x0, y0, z0)
    dfn.addFracture(f)

    f.writeTSFile('frac-%d.ts' % f.getId())

dfn.writeTSFile('dfn2.ts')
