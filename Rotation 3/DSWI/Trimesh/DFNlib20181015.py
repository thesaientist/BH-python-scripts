################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Tobias Hoeink
##    tobias.hoeink@bhge.com
##
################################################################################
import pickle
import numpy as np

__authors__ = 'Tobias Hoeink, Yuxing Ben'
__organization__ = 'Baker Hughes | RDS | R&D'
__date__ = '2018-03-29'
__version__ = '1.1'

__updateLog__ = """
1.1  now supporting Fractures and DFN's with properties
0.96 among other edits, added dfn.cropWithBoundingBox(), patch.cutWithPlane(), bbox.setPointsWith2Coordinates()
0.95 added Case, Cell, BoundingBox objects and LoadNumUpscCase()
     to read DFNExport files
[Yuxing's additions are not in this file]
0.93: added Connection.getBCTag(), setBCTag()
0.93: added DFN.scale()
0.92: changed DFN generators from class to functions
0.91: added DFN.writeTSFile()
0.91: added DFN generation from ascii files
"""

TOLERANCE = 1e-6

# Geometric Objects

class Point(object):
    def __init__(self, coords=(), id=None):
        self.id = id
        if type(coords) == Vector:
            self.setCoordinates(coords.getComponents())
        else:
            self.setCoordinates(coords)

    def __repr__(self):
        if self.id is not None:
            s =  'Point %d: ' % self.id
        else:
            s =  'Point: '
        s += '%s' % str(self.coords)
        return s

    def __add__(self, point):
        coords = tuple(self.getData() + point.getData())
        return Vector(comps=coords)

    def __sub__(self, point):
        coords = tuple(self.getData() - point.getData())
        return Vector(comps=coords)

    def __div__(self, a):
        coords = tuple(1./float(a) * self.getData())
        return Vector(comps=coords)

    def __mul__(self, a):
        coords = tuple(a * self.getData())
        return Vector(comps=coords)

    def __rmul__(self, a):
        return self.__mul__(a)

    def getId(self):
        return self.id

    def setId(self, id):
        self.id = id
        return

    def setCoordinates(self, coords):
        coords = tuple(coords)
        self.coords = coords
        self.x = coords[0]
        if len(coords) > 1:
            self.y = coords[1]
        if len(coords) > 2:
            self.z = coords[2]
        return

    def roundCoordinates(self, n=6):
        " rounds coordinates to n-th decimal"
        self.setCoordinates(np.round(self.getCoordinates(), n))
        return

    def getCoordinates(self):
        return self.coords

    def setData(self, coords):
        return self.setCoordinates(coords)

    def getData(self):
        return np.array(self.getCoordinates())

    def toVector(self):
        return Vector(self.getData())

    def translate(self, v):
        if not type(v) == Vector:
            v = Vector(v)
        coords = Point(self + v).getCoordinates()
        self.setCoordinates(coords)
        return

    def scale(self, ax, ay, az):
        coords = (self.coords[0] * ax, self.coords[1] * ay, self.coords[2] * az)
        self.setCoordinates(coords)
        return

    def rotate(self, v, a):
        " rotate point an angle a (in radians) with rotation vector v "
        if not type(v) == Vector:
            v = Vector(v)
        v.normalize()
        vp = Vector(comps=self.getCoordinates())
        newVec = vp * np.cos(a) + v.cross(vp) * np.sin(a) + v * v.dot(vp) * (1.-np.cos(a))
        self.setCoordinates(newVec.getComponents())
        return

    def distance(self, point):
        v = self - point
        return v.getLength()


class Vector(object):
    def __init__(self, comps=(), id=None):
        self.id = id
        if type(comps) == Point:
            self.setComponents(comps.getCoordinates())
        else:
            self.setComponents(comps)

    def __repr__(self):
        if self.id is not None:
            s =  'Vector %d: ' % self.id
        else:
            s =  'Vector: '
        s += '%s' % str(self.getComponents())
        return s

    def __add__(self, v):
        comps = self.getData() + v.getData()
        return Vector(comps=comps)

    def __pos__(self):
        return self

    def __neg__(self):
        return Vector(comps = -self.getData())

    def __sub__(self, v):
        return self.__add__(-v)

    def __mul__(self, a):
        comps = tuple(a * self.getData())
        return Vector(comps=comps)

    def __rmul__(self, a):
        return self.__mul__(a)

    def __div__(self, a):
        comps = tuple(1./float(a) * self.getData())
        return Vector(comps=comps)

    def setComponents(self, comps):
        comps = tuple(comps)
        self.comps = comps
        self.x = comps[0]
        if len(comps) > 1:
            self.y = comps[1]
        if len(comps) > 2:
            self.z = comps[2]
        return

    def getComponents(self):
        return self.comps

    def setData(self, comps):
        return self.setComponents(comps)

    def getData(self):
        return np.array(self.getComponents())

    def toPoint(self):
        return Point(self.getData())

    def getSigns(self):
        return np.sign(self.getData())

    def dot(self, v):
        ans = np.dot(self.getData(), v.getData())
        return ans

    def cross(self, v):
        ans = np.cross(self.getData(), v.getData())
        return Vector(comps=ans)

    def translate(self, v):
        comps = tuple((self + v).getData())
        self.setComponents(comps)
        return

    def scale(self, ax, ay=None, az=None):
        if ay == az == None:
            ay = az = ax
        self.setComponents((self.x * ax, self.y * ay, self.z * az))
        return

    def rotate(self, v, a):
        p = Point(self.getData())
        p.rotate(v, a)
        self.setComponents(p.getData())
        return

    def getLength(self):
        return np.sqrt(self.dot(self))

    def normalize(self):
        len = self.getLength()
        if len != 0:
            self.setComponents((self.getData()/len))
        return

    def getAngle(self, v, inDegrees=False):
        v1 = Vector(self.getComponents())
        v2 = Vector(v.getComponents())
        v1.normalize()
        v2.normalize()
        if np.all(v1.getComponents() == v2.getComponents()):
            angle = 0.
        else:
            tmp = v1.dot(v2)
            if abs(tmp) < 1:
                angle = np.arccos(v1.dot(v2))
            else:
                angle = {1:0, -1:np.pi}[np.sign(tmp)]
            if inDegrees:
                angle = angle/np.pi*180.
        return angle

    def isParallel(self, v, threshold=1e-6):
        if self.cross(v).getLength() <= threshold:
            return True
        else:
            return False


class Line(object):
    def __init__(self, point=None, vector=None, id=None):
        self.id = id
        if not point or not vector:
            print('ERROR: A line is defined by point and vector.')
        self.p = point
        vector.normalize()
        self.v = vector

    def __repr__(self):
        if self.id is not None:
            s =  'Line %d:' % self.id
        else:
            s =  'Line: '
        s += '(%s, %s)' % (self.p, self.v)
        return s

    def getVectorToPoint(self, point):
        vec1 = self.p - point
        return vec1 - vec1.dot(self.v) * self.v

    def getDistanceToPoint(self, point):
        v = self.getVectorToPoint(point)
        return v.getLength()

    def isPointOn(self, point, tolerance=1e-4):
        return self.getDistanceToPoint(point) < tolerance

    def getDistanceToLine(self, line):
        if self.v == line.v:
            # lines are parallel
            d = self.getDistanceToPoint(line.p)
        else:
            v = self.p - line.p
            d = v.dot(self.v.cross(line.v))
            d = abs(d)
        return d

    def getIntersection(self, line):
        length = self.v.cross(line.v).getLength()
        if length!= 0:
            v = (line.p - self.p).cross(line.v)
            t = v.getLength() / length
            x1 = self.getPointOn(t)
            if line.isPointOn(x1, tolerance=self.v.getLength()/3.):
                ans = x1
            else:
                x2 = self.getPointOn(-t)
                ans = x2
        else:
            # print 'ERROR: Lines are parallel and do not intersect!'
            ans = None
        return ans

    def getPointOn(self, a):
        x = self.p + a * self.v
        return x.toPoint()


class LineSegment(object):
    def __init__(self, p1, p2, id=None):
        if not isinstance(p1, Point):
            p1 = Point(p1)
        if not isinstance(p2, Point):
            p2 = Point(p2)
        self.p1 = p1
        self.p2 = p2
        self.id = id

    def __repr__(self):
        if self.id is not None:
            s =  'LineSegment %d:' % self.id
        else:
            s =  'LineSegment: '
        s += '(%s, %s)' % (self.p1, self.p2)
        return s

    def getPoints(self):
        return [self.p1, self.p2]

    def getPointCoordinates(self):
        return [self.p1.getCoordinates(), self.p2.getCoordinates()]

    def getDirection(self):
        v = self.p2 - self.p1
        return v

    def getLength(self):
        v = self.getDirection()
        return v.getLength()

    def getCenter(self):
        center = (self.p1+self.p2)/2.
        return center.toPoint()

    def isPointOn(self, p, tolerance=1e-6):
        if (self.p1 - p).getLength() < tolerance:
            ans = True
        elif (self.p2 - p).getLength() < tolerance:
            ans = True
        else:
            v1 = self.p1 - p
            v2 = p - self.p2
            v1.normalize()
            v2.normalize()
            ans = (v1-v2).getLength() < tolerance
        return ans

    def getLineIntersection(self, line):
        # make a line for self
        line1 = Line(self.p1, self.p2-self.p1)
        if not line1:
            return None

        # find intersectionPoint
        p = line1.getIntersection(line)
        if p is None:
            ans = None
        else:
            # check if intersection Point is on self
            if self.isPointOn(p):
                ans = p
            else:
                ans = None
        return ans

    def getIntersection(self, lineSegment):
        # make a line for self and for lineSegment
        line1 = Line(self.p1, self.p2-self.p1)
        line2 = Line(lineSegment.p1, lineSegment.p2-lineSegment.p1)

        # find intersectionPoint
        p = line1.getIntersection(line2)
        if p is None:
            ans = None
        else:
            # check if intersection Point is within both lineSegments
            if self.isPointOn(p) and lineSegment.isPointOn(p):
                ans = p
            else:
                ans = None

        return ans

    def writeXYZFile(self, fname=None):
        if fname is None:
            if self.fname:
                fname = self.fname
            else:
                if self.id:
                    fname = 'LineSegment-' + self.id + '.xyz'
                else:
                    fname = 'LineSegment.xyz'

        s = ''
        for point in self.getPoints():
            s += '%f %f %f\n' % point.getCoordinates()
        open(fname, 'w').write(s)
        print('written file ', fname)
        return

    def writePLFile(self, fname=None):
        if fname is None:
            if self.fname:
                fname = self.fname
            else:
                if self.id:
                    fname = 'LineSegment-' + self.id + '.pl'
                else:
                    fname = 'LineSegment.pl'

        s = 'GOCAD PLine 1\n'
        s += 'HEADER{\n'
        s += 'name:%s\n' % self.id
        s += '}\n'
        s += 'GOCAD_ORIGINAL_COORDINATE_SYSTEM\n'
        s += 'NAME from_XYZ\n'
        s += 'AXIS_NAME "U" "V" "W"\n'
        s += 'AXIS_UNIT "m" "m" "m"\n'
        s += 'ZPOSITIVE Depth\n'
        s += 'END_ORIGINAL_COORDINATE_SYSTEM\n'
        s += 'GEOLOGICAL_TYPE Undefined\n'
        s += 'ILINE\n'
        for i, point in enumerate(self.getPoints()):
            c = point.getCoordinates()
            s += 'VRTX %d %f %f %f\n' % (i+1, c[0], c[1], c[2])
        s += 'SEG 1 2 \n'
        s += 'END\n'
        open(fname, 'w').write(s)
        print('written file ', fname)
        return


class Plane(object):
    def __init__(self, point=None, normal=None, id=None):
        self.id = id
        if not point or not normal:
            print('ERROR: A plane is defined by point and normal vector.')
        self.p = point
        normal.normalize()
        self.n = normal

    def __repr__(self):
        if self.id is not None:
            s =  'Plane %d:' % self.id
        else:
            s =  'Plane: '
        s += '(%s, %s)' % (self.p, self.n)
        return s

    def isPointOn(self, p, tolerance=1e-6):
        return abs(self.n.dot(self.p - p)) < tolerance

    def getVectorToPoint(self, point):
        return (point-self.p).dot(self.n) * self.n

    def getDistanceToPoint(self, point):
        v = self.getVectorToPoint(point)
        return v.getLength()

    def getLineIntersection(self, line):
        tmp = self.n.dot(line.v)
        if tmp == 0:
            print('ERROR: Plane and Line are parallel and do not intersect!')
            ans = None
        else:
            t = (self.p - line.p).dot(self.n) / tmp
            ans = line.getPointOn(t)
        return ans

    def getIntersection(self, plane):
        # line direction is orthogonal to both plane normals
        v = self.n.cross(plane.n)
        if v.getLength() != 0.:
            h1 = self.n.dot(self.p.toVector())
            h2 = plane.n.dot(plane.p.toVector())
            n1n2 = self.n.dot(plane.n)
            tmp = (1. - n1n2**2)
            if tmp == 0:
                # print 'ERROR: Planes are parallel and do not intersect!'
                return None
            c1 = (h1 - h2 * n1n2) / tmp
            c2 = (h2 - h1 * n1n2) / tmp
            p = (c1*self.n + c2*plane.n).toPoint()
            ans = Line(p, v)
        else:
            # print 'ERROR: Planes are parallel and do not intersect!'
            ans = None

        return ans


class Triangle(object):
    def __init__(self, nodes=(), id=None, silent=False):
        self.id = id
        self.nodes = nodes  # each node is supposed to be a Point object
        if not silent and len(self.nodes) != 3:
            print('ERROR: A triangle needs THREE (3) nodes. Not more, not less.')
            print('       I will use the first 3 nodes from the %d you provided.' % len(self.nodes))
        self.nodes = self.nodes[:3]

    def __repr__(self):
        if self.id is not None:
            s =  'Triangle %d: ' % self.id
        else:
            s =  'Triangle: '
        s += ', '.join(['%s' % str(node.id) for node in self.getNodes()])
        return s

    def getId(self):
        return self.id

    def setId(self, i):
        self.id = i

    def setNodes(self, nodes):
        self.nodes = nodes

    def getNodes(self):
        return self.nodes

    def getNodeIds(self):
        return [n.getId() for n in self.nodes]

    def replaceNode(self, oldNode, newNode):
        self.setNodes(_replaceInTuple(self.nodes, oldNode, newNode))

    def getBBox(self):
        coords = np.array([point.getCoordinates() for point in self.getNodes()]).T
        return (tuple(coords.min(axis=1)), tuple(coords.max(axis=1)))

    def getBBoxDimension(self):
        return tuple(np.array(self.getBBox()[1]) - np.array(self.getBBox()[0]))

    def getCenter(self, bbox=False):
        """ Returns an array of center coordinates based on all points.
          If bbox=True the min/max coordinates are used instead. """
        if bbox:
            coords2 = np.average(self.getBBox(), axis=0)
        else:
            coords = np.array([point.getCoordinates() for point in self.getNodes()]).T
            coords2 = np.average(coords, axis=1)
        return Point(coords=tuple(coords2))

    def getArea(self):
        v1 = self.nodes[0] - self.nodes[1]
        v2 = self.nodes[0] - self.nodes[2]
        ans = 0.5 * v1.getLength() * v2.getLength() * np.sin(v1.getAngle(v2))
        return ans

    def getNormal(self):
        " Returns the normal vector of a Triangle "
        v1 = self.nodes[0] - self.nodes[1]
        v2 = self.nodes[0] - self.nodes[2]
        v = v1.cross(v2)
        v.normalize()
        return v


class PointSet(object):
    def __init__(self, points=[], id=None):
        self.points = []
        for p in points:
            if isinstance(p, Point):
            # if hasattr(p, 'getCoordinates'):
                self.addPoint(p)
            else:
                self.addPointByCoordinate(p)
        self.id = id

    def __repr__(self):
        if self.id is not None:
            s =  'PointSet %s: ' % self.id
        else:
            s =  'PointSet: '
        s += '(%d Points)' % self.points.__len__()
        return s

    def __len__(self):
        return len(self.getPoints())

    def getId(self):
        return self.id

    def setId(self, id):
        self.id = id
        return

    def addPoint(self, p):
        self.points.append(p)
        return

    def addPointByCoordinate(self, c):
        try:
            n = max(self.getPointIds()) + 1
        except:
            n = 1
        p = Point(coords=c, id=n)
        self.addPoint(p)
        return

    def addPointsByCoordinates(self, coords):
        for c in coords:
            self.addPointByCoordinate(c)
        return

    def getPoints(self):
        return self.points

    def setPoints(self, points):
        self.points = points
        return

    def getCoordinates(self):
        coords = [p.getCoordinates() for p in self.getPoints()]
        return coords

    def getPointIds(self):
        idxs = [p.getId() for p in self.getPoints()]
        return idxs

    def removePointById(self, n):
        self.points = [p for p in self.getPoints() if p.getId()!=n]
        return

    def removePointsAtSameLocation(self, n=6):
        """removes points at same location after rounding coordinates to n-th decimal
        Note: this will destroy points IDs
        Note: n should match tolerance in LineSegment.isPointOn()
        """
        coords = []
        for p in self.getPoints():
            p.roundCoordinates(n)
            coords.append(p.getCoordinates())

        coords = set(coords)
        self.setPoints([])
        self.addPointsByCoordinates(coords)
        return

    def translate(self, v):
        for point in self.getPoints():
            point.translate(v)
        return

    def scale(self, ax, ay=None, az=None):
        # check if all three scale factors are given, else use only the first for all directions
        if ay == az == None:
            ay = az = ax
        for point in self.getPoints():
            point.scale(ax, ay, az)
        return

    def scaleInPlace(self, ax, ay, az):
        if ay == az == None:
            ay = az = ax
        vec = Vector(self.getCenter())
        self.translate(-vec)
        self.scale(ax, ay, az)
        self.translate(vec)
        return

    def flipInplace(self, v):
        vec = Vector(self.getCenter())
        self.translate(-vec)
        self.scale((-1)**v[0], (-1)**v[1], (-1)**v[2])
        self.translate(vec)
        return

    def rotate(self, v, a):
        for point in self.getPoints():
            point.rotate(v, a)
        return

    def rotateInplace(self, v, a):
        vec = Vector(self.getCenter())
        self.translate(-vec)
        self.rotate(v, a)
        self.translate(vec)
        return

    def rotateHorizontally(self, angle):
        " rotate around a vertical line at the center \n angle in radians"
        point = self.getCenter()
        v = Vector(point)
        self.translate(-v)
        rotationAxis = np.array([0, 0, 1])
        self.rotate(rotationAxis, angle)
        self.translate(v)
        return

    def getBBox(self):
        coords = np.array([point.getCoordinates() for point in self.getPoints()]).T
        return (tuple(coords.min(axis=1)), tuple(coords.max(axis=1)))

    def getBBoxDimension(self):
        return tuple(np.array(self.getBBox()[1]) - np.array(self.getBBox()[0]))

    def getCenter(self, bbox=False):
        """ Returns an array of center coordinates based on all points.
          If bbox=True the min/max coordinates are used instead. """
        if bbox:
            point = np.average(self.getBBox(), axis=0)
            #point = np.average([coords.min(axis=1), coords.max(axis=1)], axis=0)
        else:
            coords = np.array([point.getCoordinates() for point in self.getPoints()]).T
            point = np.average(coords, axis=1)
        return Point(coords=tuple(point))

    def moveToOrigin(self):
        v = Vector(comps=tuple(self.getBBox()[0]))
        self.translate(-v)
        return

    def centerOnOrigin(self, bbox=False):
        center = self.getCenter(bbox=bbox)
        origin = Point(coords=tuple(np.zeros_like(center.getCoordinates())))
        v = origin - center
        self.translate(v)
        return

    def getNormal(self):
        """ Returns the normal vector of a PointSet, which is assumed to be flat such that it's
        surface can be described by the min/max coordinates in each direction"""
        if len(self.getPoints()) < 3:
            print('ERROR: Point cloud must have at least 3 points to compute normal')

        # find 4 points at the ends
        points = sorted(set([p for p in self.getPoints()]), key=lambda l: -l.getCoordinates()[2])
        point1 = points[0]
        point2 = points[-1]
        points = sorted(set([p for p in self.getPoints()]), key=lambda l: l.getCoordinates()[0]+l.getCoordinates()[1])
        point3 = points[0]
        point4 = points[-1]
        #logthis('Picked 4 points:' )
        #logthis('\n'.join([str(i) for i in [p1,p2,p3,p4]]))
        # compute normal
        vec1 = point2 - point1
        vec2 = point4 - point3
        n = vec2.cross(vec1)
        n.normalize()
        #logthis('\nPoint Surface Normal : (%.3f  %.3f  %.3f)' % tuple(n))

        # if stuff fails (can happen with a few poorly positioned points) use the first three
        if n.getLength() == 0:
            t = Triangle(nodes=self.getPoints()[:3])
            n = t.getNormal()
        return n

    def writeXYZFile(self, fname=None):
        if fname is None:
            if self.fname:
                fname = self.fname
            else:
                if self.id:
                    fname = 'PointSet-' + self.id + '.xyz'
                else:
                    fname = 'PointSet.xyz'

        s = ''
        for point in self.getPoints():
            s += '%f %f %f\n' % point.getCoordinates()
        open(fname, 'w').write(s)
        print('written file ', fname)
        return


class PolyLine(object):
    # container for LineSegments
    def __init__(self, points=[], id=None, segments=[]):
        self.segments = []

        # catch if a pointset is used to initialize
        if hasattr(points, 'getPoints'):
            points = points.getPoints()

        # create line segments from points
        if points:
            self.segments = []
            for i in range(len(points)-1):
                s = LineSegment(points[i], points[i+1])
                self.segments.append(s)

            # close the loop
            if points[0] != points[-1]:
                s = LineSegment(points[-1], points[0])
                self.segments.append(s)

            #self.points = points[:-1]

        # or use given segments
        elif segments:
            self.segments = segments

        self.id = id

    def __repr__(self):
        if self.id is not None:
            s =  'PolyLine %s: ' % self.id
        else:
            s =  'PolyLine: '
        s += '(%d Segments)' % self.segments.__len__()
        return s

    def getId(self):
        return self.id

    def setId(self, i):
        self.id = i

    def addSegment(self, seg):
        return self.segments.append(seg)

    def getSegments(self):
        return self.segments

    def getData(self):
        return self.getSegments()

    def getPoints(self):
        #return self.points
        return [s.p1 for s in self.getSegments()]

    def getLineIntersection(self, line):
        points = []
        for s in self.getSegments():
            points.append(s.getLineIntersection(line))

        return [p for p in points if p is not None]

    def getLength(self):
        "returns sum of all segment lengths"
        length = 0.
        for seg in self.getSegments():
            length += seg.getLength()
        return length

    def writeXYZFile(self, fname=None):
        if fname is None:
            if self.fname:
                fname = self.fname
            else:
                if self.id:
                    fname = 'PolyLine-' + self.id + '.xyz'
                else:
                    fname = 'PolyLine.xyz'

        s = ''
        for point in self.getPoints():
            s += '%f %f %f\n' % point.getCoordinates()
        s += '%f %f %f\n' % self.getPoints()[0].getCoordinates()
        open(fname, 'w').write(s)
        print('written file ', fname)
        return

    def writePLFile_old(self, fname=None, isLoop=True):
        if fname is None:
            if self.fname:
                fname = self.fname
            else:
                if self.id:
                    fname = 'PolyLine-' + self.id + '.pl'
                else:
                    fname = 'PolyLine.pl'

        s = 'GOCAD PLine 1\n'
        s += 'HEADER{\n'
        s += 'name:%s\n' % self.id
        s += '}\n'
        s += 'GOCAD_ORIGINAL_COORDINATE_SYSTEM\n'
        s += 'NAME from_XYZ\n'
        s += 'AXIS_NAME "U" "V" "W"\n'
        s += 'AXIS_UNIT "m" "m" "m"\n'
        s += 'ZPOSITIVE Depth\n'
        s += 'END_ORIGINAL_COORDINATE_SYSTEM\n'
        s += 'GEOLOGICAL_TYPE Undefined\n'
        s += 'ILINE\n'
        if isLoop:
            for i, point in enumerate(self.getPoints()):
                c = point.getCoordinates()
                s += 'VRTX %d %f %f %f\n' % (i+1, c[0], c[1], c[2])
            for i, seg in enumerate(self.getSegments()[:-1]):
                s += 'SEG %d %d\n' % (i+1, i+2)
            s += 'SEG %d %d\n' % (i+2, 1)
            s += 'END\n'

        else:
            s2 = ''
            cnt = 0
            for i, seg in enumerate(self.getSegments()):
                for point in seg.getPoints():
                    c = point.getCoordinates()
                    s += 'VRTX %d %f %f %f\n' % (cnt+1, c[0], c[1], c[2])
                    cnt += 1
                s2 += 'SEG %d %d \n' % (cnt-2, cnt-1)
            s += s2
            s += 'END\n'
        open(fname, 'w').write(s)
        print('written file ', fname)
        return

    def writePLFile(self, fname=None):
        if fname is None:
            if self.fname:
                fname = self.fname
            else:
                if self.id:
                    fname = 'PolyLine-' + self.id + '.pl'
                else:
                    fname = 'PolyLine.pl'

        s = 'GOCAD PLine 1\n'
        s += 'HEADER{\n'
        s += 'name:%s\n' % self.id
        s += '}\n'
        s += 'GOCAD_ORIGINAL_COORDINATE_SYSTEM\n'
        s += 'NAME from_XYZ\n'
        s += 'AXIS_NAME "U" "V" "W"\n'
        s += 'AXIS_UNIT "m" "m" "m"\n'
        s += 'ZPOSITIVE Depth\n'
        s += 'END_ORIGINAL_COORDINATE_SYSTEM\n'
        s += 'GEOLOGICAL_TYPE Undefined\n'

        cnt = 0
        for i, seg in enumerate(self.getSegments()):
            s += 'ILINE\n'
            p1, p2 = seg.getPoints()

            c = p1.getCoordinates()
            cnt += 1
            s += 'VRTX %d %f %f %f\n' % (cnt, c[0], c[1], c[2])

            c = p2.getCoordinates()
            cnt += 1
            s += 'VRTX %d %f %f %f\n' % (cnt, c[0], c[1], c[2])

            s += 'SEG %d %d \n' % (cnt-1, cnt)
        s += 'END\n'

        open(fname, 'w').write(s)
        print('written file ', fname)
        return


class BoundingBox(PointSet):
    """Bounding box (2D / 4 sides)"""
    def __repr__(self):
        if self.id is not None:
            s =  'BBox %s: ' % self.id
        else:
            s =  'BBox: '
        s += '(%d Points)' % self.points.__len__()
        return s

    def setPointsWith2Coordinates(self, c1, c2):
        """takes 2 coordinate tuples and returns
        8 points that make a box"""
        # bbox = BoundingBox()
        self.addPointByCoordinate((c1[0], c1[1], c1[2]))
        self.addPointByCoordinate((c1[0], c2[1], c1[2]))
        self.addPointByCoordinate((c2[0], c2[1], c1[2]))
        self.addPointByCoordinate((c2[0], c1[1], c1[2]))
        self.addPointByCoordinate((c1[0], c1[1], c2[2]))
        self.addPointByCoordinate((c1[0], c2[1], c2[2]))
        self.addPointByCoordinate((c2[0], c2[1], c2[2]))
        self.addPointByCoordinate((c2[0], c1[1], c2[2]))
        return

    def get4Planes(self):
        planes = []
        if len(self.getPoints()) >= 4:
            p1, p2, p3, p4 = self.getPoints()[:4]
        else:
            print('ERROR: Getting 4 sides from a bounding box requires 4 corner points.')
            return []
        #
        planes.append(Plane(p1, p2-p3))
        planes.append(Plane(p2, p3-p4))
        planes.append(Plane(p3, p4-p1))
        planes.append(Plane(p4, p1-p2))
        return planes

    def get6Planes(self):
        planes = []
        if len(self.getPoints()) >= 8:
            p1, p2, p3, p4, p5, p6, p7, p8 = self.getPoints()[:8]
        else:
            print('ERROR: Getting 4 sides from a bounding box requires 4 corner points.')
            return []
        #
        planes.append(Plane(p1, p2-p3))
        planes.append(Plane(p2, p3-p4))
        planes.append(Plane(p3, p4-p1))
        planes.append(Plane(p4, p1-p2))
        planes.append(Plane(p1, p1-p5))
        planes.append(Plane(p5, p5-p1))
        return planes

    def get4Patches(self):
        """ (not following Abaqus' face numbering for 8-node elements)
            face sequence now consistent with
            the definition in dfn.getConnectedClusters3D()
        """
        patches = []
        if len(self.getPoints()) >= 8:
            p1, p2, p3, p4, p5, p6, p7, p8 = self.getPoints()[:8]
        else:
            print('ERROR: Getting 6 sides from a bounding box requires 8 corner points.')
            return []

        # the sequence of the planes where patches sits is:
        # x, y axis are parallel to the surfaces of bbox
        # x=x1,x=xn(x1<xn), y=y1, y=yn (y1<yn) in the local coordinates
        patches.append(Patch(points=[p4, p8, p5, p1]))
        patches.append(Patch(points=[p2, p6, p7, p3]))
        patches.append(Patch(points=[p1, p5, p6, p2]))
        patches.append(Patch(points=[p3, p7, p8, p4]))

        return patches

    def get6Patches(self):
        """ following Abaqus' face numbering for 8-node elements"""
        patches = []
        if len(self.getPoints()) >= 8:
            p1, p2, p3, p4, p5, p6, p7, p8 = self.getPoints()[:8]
        else:
            print('ERROR: Getting 6 sides from a bounding box requires 8 corner points.')
            return []
        #
        patches.append(Patch(points=[p1, p2, p3, p4]))
        patches.append(Patch(points=[p5, p8, p7, p6]))
        patches.append(Patch(points=[p1, p5, p6, p2]))
        patches.append(Patch(points=[p2, p6, p7, p3]))
        patches.append(Patch(points=[p3, p7, p8, p4]))
        patches.append(Patch(points=[p4, p8, p5, p1]))
        return patches

    def setTopBottom(self, z_bottom, z_top):
        self.setPoints(self.getPoints()[:4])
        for p in self.getPoints():
            p.setCoordinates(p.getCoordinates()[:2] + (z_bottom,))
        coords = []
        for p in self.getPoints():
            coords.append(p.getCoordinates()[:2] + (z_top,))
        for c in coords:
            self.addPointByCoordinate(c)
        return

    def getBBoxSize(self):
        bboxsize = []
        if len(self.getPoints()) >= 8:
            p1, p2, p3, p4, p5, p6, p7, p8 = self.getPoints()[:8]
        else:
            print('ERROR: Getting 6 sides from a bounding box requires 8 corner points.')
            return []
        patch1 = Patch(points=[p2, p6, p7, p3])
        plane1 = patch1.getPlane()
        bboxsize.append(plane1.getDistanceToPoint(p4))

        patch2 = Patch(points=[p3, p7, p8, p4])
        plane2 = patch2.getPlane()
        bboxsize.append(plane2.getDistanceToPoint(p1))

        patch3 = Patch(points=[p5, p8, p7, p6])
        plane3 = patch3.getPlane()
        bboxsize.append(plane3.getDistanceToPoint(p1))

        return bboxsize

    def sort8Points(self, azimuth=0.):
        """sorts the eight points that define this bbox
        so that get6Patches() return patches in the correct order.
        uses local coordinates
        """

        points = [Point(c, id=i) for i,c in enumerate(self.getCoordinates())]
        ps = PointSet(points)
        ps.rotateHorizontally(azimuth)

        dx, dy, dz = ps.getBBoxDimension()
        dr = np.sqrt(dx*dx + dy*dy + dz*dz) / 10.
        (x0, y0, z0), (xn, yn, zn) = ps.getBBox()

        points = []
        points.append([p for p in ps.points if p.distance(Point((x0,y0,z0))) < dr][0])
        points.append([p for p in ps.points if p.distance(Point((xn,y0,z0))) < dr][0])
        points.append([p for p in ps.points if p.distance(Point((xn,yn,z0))) < dr][0])
        points.append([p for p in ps.points if p.distance(Point((x0,yn,z0))) < dr][0])
        points.append([p for p in ps.points if p.distance(Point((x0,y0,zn))) < dr][0])
        points.append([p for p in ps.points if p.distance(Point((xn,y0,zn))) < dr][0])
        points.append([p for p in ps.points if p.distance(Point((xn,yn,zn))) < dr][0])
        points.append([p for p in ps.points if p.distance(Point((x0,yn,zn))) < dr][0])
        ps.setPoints(points)
        ids = ps.getPointIds()

        points0 = self.getPoints()
        points = []
        for i in ids:
            points.append(points0[i])

        self.setPoints(points)
        return

    def isInside(self, p, tolerance=TOLERANCE):
        "check whether point is inside bounding box"
        center = self.getCenter()
        ans = True
        for plane in self.get6Planes():
            # p1 is where line defined by p, bboxCenter hits plane
            p1 = plane.getLineIntersection(Line(p, p-center))
            if p1:
                if p.distance(center) > p1.distance(center) + tolerance:
                    ans = False

        return ans

class Patch(PointSet):
    def __init__(self, points=[], id=None):
        # catch if a pointset is used to initialize
        if hasattr(points, 'getPoints'):
            points = points.getPoints()
        PointSet.__init__(self, points=points, id=id)
        self.normal = None
        self.triangles = None
        self.area = None

    def __repr__(self):
        if self.id is not None:
            s =  'Patch %s: ' % self.id
        else:
            s =  'Patch: '
        s += '(%d Points)' % self.points.__len__()
        return s

    def compute2DRepresentation(self):
        # rotate into 2D plane
        n = self.getNormal()    # fracture normal
        v = Vector((0,0,1))
        r = n.cross(v)          # rotation vector
        r.normalize()
        a = n.getAngle(v)       # rotation angle
        #self.rotateInplace(r, a)

        # set up 2D points
        ps = PointSet([Point(coord) for coord in self.getCoordinates()])
        c = Vector(ps.getCenter())
        ps.translate(-c)
        ps.rotate(r, a)
        c = Vector(ps.getCenter())
        ps.translate(-c)
        self.points2D = [Point(coords[:2]) for coords in ps.getCoordinates()]
        return

    def createPolyLine(self):
        self.polyline = PolyLine(self.points)

    def getPolyLine(self):
        return self.polyline

    def getIntersection(self, patch):
        # create a plane for each patch
        plane1 = self.getPlane() # Plane(self.getPoints()[0], self.getNormal())
        #plane2 = Plane(patch.getPoints()[0], patch.getNormal())
        plane2 = patch.getPlane()

        # find intersection line between planes
        line = plane1.getIntersection(plane2)
        if not line:
            return None

        # collect points where line intersects with polylines from each patch
        self.createPolyLine()
        patch.createPolyLine()
        points1 = self.polyline.getLineIntersection(line)
        points2 = patch.polyline.getLineIntersection(line)

        ps = PointSet(points1)
        ps.removePointsAtSameLocation()
        points1 = ps.getPoints()
        ps = PointSet(points2)
        ps.removePointsAtSameLocation()
        points2 = ps.getPoints()

        # return here if line doesn't intersect both patches
        if len(points1) != 2 or len(points2) != 2:
            return None

        # find where patches intersect
        s1 = LineSegment(p1=points1[0], p2=points1[1])
        s2 = LineSegment(p1=points2[0], p2=points2[1])

        ans1 = [s2.isPointOn(p, tolerance=0.001*s2.getLength()) for p in points1]
        ans2 = [s1.isPointOn(p, tolerance=0.001*s1.getLength()) for p in points2]

        # identify the two points that define a LineSegment of the intersection
        if sum(ans1+ans2) == 2:
            p1, p2 = [v for (c,v) in zip(ans1+ans2, points1+points2) if c ]
            ans = LineSegment(p1, p2)
        elif sum(ans1+ans2) == 3:
            if sum(ans1) == 2:
                ans = LineSegment(points1[0], points1[1])
            else:
                ans = LineSegment(points2[0], points2[1])
        elif sum(ans1+ans2) == 4:
            ans = LineSegment(points1[0], points1[1])
        else:
            ans = None
        return ans

    def getPlane(self):
        return Plane(self.getPoints()[0], self.getNormal())

    def cutWithPlane(self, plane):
        "cuts a Patch with a Plane and returns two Patches or None"

        # find intersection line between planes
        line = self.getPlane().getIntersection(plane)
        if not line:
            return None

        self.createPolyLine()
        # points = self.polyline.getLineIntersection(line)

        points1 = []
        points2 = []
        for seg in self.polyline.getSegments():
            dir1 = plane.getVectorToPoint(seg.p1).dot(plane.n)
            dir2 = plane.getVectorToPoint(seg.p2).dot(plane.n)

            # both segment points are on the plane
            if np.sign(dir1) == np.sign(dir2) == 0.:
                points1.append(seg.p1)
                points2.append(seg.p1)

            # both segment points are on same side of the plane
            elif np.sign(dir1) == np.sign(dir2):
                if dir1 > 0:
                    points1.append(seg.p1)
                else:
                    points2.append(seg.p1)

            # both segment points are on different sides of the plane
            else:
                p = seg.getLineIntersection(line)
                if dir1 > 0:
                    points1.append(seg.p1)
                    points1.append(p)
                    points2.append(p)
                else:
                    points2.append(seg.p1)
                    points2.append(p)
                    points1.append(p)

        # don't return patches with less than 3 points,
        # and take care of potential rounding errors
        if len(points1) > 2:
            if len(points1) > len(self.points):
                ps = PointSet(points1)
                ps.removePointsAtSameLocation()
                points1 = ps.getPoints()
            patch1 = Patch(points=points1)
        else:
            patch1 = Patch()

        if len(points2) > 2:
            if len(points2) > len(self.points):
                ps = PointSet(points2)
                ps.removePointsAtSameLocation()
                points2 = ps.getPoints()
            patch2 = Patch(points=points2)
        else:
            patch2 = Patch()

        return patch1, patch2

    def computeNormal(self):
        self.normal = PointSet.getNormal(self)
        return

    def getNormal(self):
        if not self.normal:
            self.computeNormal()
        return self.normal

    def rotate(self, v, a):
        # rotating changes a stored normal vector
        # delete it first to avoid confusion
        self.normal = None
        PointSet.rotate(self, v, a)
        return

    def triangulate(self):
        "triangulate path from self.points and patch center"
        center = self.getCenter()
        # center.setId(0)
        points = self.getPoints()
        # for i, p in enumerate(points):
            # p.setId(i+1)

        triangles = []
        for i in range(len(points)-1):
            t = Triangle([center, points[i], points[i+1]], id=i)
            triangles.append(t)

        if points[0] != points[-1]:
            t = Triangle([center, points[-1], points[0]], id=i+1)
            triangles.append(t)

        self.triangles = triangles
        return

    def triangulate2(self):
        # "triangulate path from self.polyline.segments and patch center"
        # center = self.getCenter()
        # self.createPolyLine()

        # triangles = []
        # for seg in self.polyline.getSegments():
            # t = Triangle([center] + seg.getPoints())
            # triangles.append(t)

        # self.triangles = triangles
        return

    def getTriangles(self):
        return self.triangles

    def computeArea(self):
        ans = 0.
        if not self.getTriangles():
            self.triangulate()
        for tr in self.getTriangles():
            ans += tr.getArea()
        self.area = ans
        return

    def getArea(self):
        if not self.area:
            self.computeArea()
        return self.area

    def writeTSFile(self, fname=None):
        if fname is None:
            if hasattr(self, 'fname'):
                fname = self.fname
            else:
                if self.id:
                    fname = 'Patch-' + str(self.id) + '.ts'
                else:
                    fname = 'Patch.ts'

        # if not hasattr(self, 'triangles'):
            # self.triangulate()

        s = 'GOCAD TSurf 1\n'
        s += 'HEADER{\n'
        s += 'name:%s\n' % self.id
        s += 'mesh:false\n'
        s += '}\n'
        s += 'GOCAD_ORIGINAL_COORDINATE_SYSTEM\n'
        s += 'NAME from_XYZ\n'
        s += 'AXIS_NAME "U" "V" "W"\n'
        s += 'AXIS_UNIT "ftUS" "ftUS" "ft"\n'
        s += 'ZPOSITIVE Depth\n'
        s += 'END_ORIGINAL_COORDINATE_SYSTEM\n'
        s += 'GEOLOGICAL_TYPE Undefined\n'

        s += 'TFACE\n'

        center = self.getCenter()
        c = center.getCoordinates()
        s += 'VRTX %d %f %f %f\n' % (1, c[0], c[1], c[2])

        points = self.getPoints()
        for i, p in enumerate(points):
            c = p.getCoordinates()
            s += 'VRTX %d %f %f %f\n' % (i+2, c[0], c[1], c[2])

        for i in range(len(points)-1):
            s += 'TRGL %d %d %d\n' % (1, i+2, i+3)

        if points[0] != points[-1]:
            s += 'TRGL %d %d %d\n' % (1, i+3, 2)

        s += 'END\n'

        open(fname, 'w').write(s)
        print('written file ', fname)
        return



# Physical Objects

class Fracture(Patch):
    def __init__(self, points=[], points2D=[], id=None, aperture=0., dip=None, strike=None, properties={}):
        # catch if a pointset is used to initialize
        if hasattr(points, 'getPoints'):
            points = points.getPoints()
        Patch.__init__(self, points=points, id=id)
        self.setAperture(aperture)
        self.dip = dip
        self.strike = strike
        self.properties = {}
        for k in properties:
            self.setProperty(k, properties[k])

    def __repr__(self):
        if self.id is not None:
            s =  'Fracture %s: ' % self.id
        else:
            s =  'Fracture: '
        s += '(%d Points)' % self.__len__()
        return s

    def setAperture(self, aperture):
        self.aperture = aperture
        return

    def getAperture(self):
        return self.aperture

    def setProperty(self, k, v):
        self.properties[k] = v

    def getProperty(self, k):
        return self.properties[k]

    def getProperties(self):
        return sorted(self.properties.keys())

    def setArea(self, area):    # getArea defined in Patch object
        self.area = area
        return

    def setNormal(self, normal):
        if type(normal) == Vector:
            self.normal = normal
        else:
            self.normal = Vector(normal)

        length = self.normal.getLength()
        if length > 0 :
            self.normal = self.normal.__div__(length)
        return

    def getIntersection(self, fracture):
        seg = Patch.getIntersection(self, fracture)
        if seg is None:
            return None
        else:
            con = Connection(fractures=[self.id, fracture.id], segment=seg)
        return con

    def computeDip(self, tolerance=1e-6):
        n = self.getNormal()
        d = n.getData()
        if abs(d[2]) < tolerance:
            self.dip = 0.
        else:
            d[2] = 0.
            a = n.getAngle(Vector(d))
            a = min(a, np.pi-a)
            self.dip = np.sign(n.getData()[2]) * a
        return

    def getDip(self, inDegrees=False):
        if not self.dip:
            self.computeDip()
        ans = self.dip
        if inDegrees:
            ans = self.dip / np.pi * 180.
        return ans

    def computeStrike2(self, north=None):
        " uses horizontal plane located at fracture center "
        if not north:
            north = Vector((0,1,0))
        plane = Plane(self.getCenter(), Vector((0,0,1)))
        line = self.getPlane().getIntersection(plane)
        self.strike = line.v.getAngle(north)
        return

    def computeStrike(self, north=None):
        """ uses normal vector projected into x-y plane
            if north not specified, then direction (0,1,0) is assumed for north
        """
        if not north:
            north = Vector((0,1,0))
        # east = north.cross(Vector((0,0,1)))

        n = self.getNormal()
        d = n.getData()
        d[2] = 0.
        v = Vector(d)
        a = v.getAngle(north)
        a = np.pi/2. - a
        self.strike = min(a, np.pi-a)
        return

    def getStrike(self, inDegrees=False):
        if not self.strike:
            self.computeStrike()
        ans = self.strike
        if inDegrees:
            ans = self.strike / np.pi * 180.
        return ans

    def rotate(self, v, a):
        # rotating changes a stored normal vector, dip and strike
        # delete it first to avoid confusion
        self.dip = None
        self.strike = None
        self.normal = None
        PointSet.rotate(self, v, a)
        return

    def cutWithPlane(self, plane):
        patch1, patch2 = Patch.cutWithPlane(self, plane)
        f1 = Fracture(patch1, aperture=self.getAperture())
        f2 = Fracture(patch2, aperture=self.getAperture())
        return f1, f2


class Connection(object):
    def __init__(self, segment=None, id=None, fractures=[], bc=None):
        self.segment = segment
        self.id = tuple(sorted(fractures))
        self.bc = self.setBCTag(bc)

    def __repr__(self):
        if self.id:
            s =  'Connection %s ' % str(self.id)
        else:
            s =  'Connection '
        return s

    def setId(self, id):
        self.id = id
        return

    def getId(self):
        return self.id

    def getSegment(self):
        return self.segment

    def setBCTag(self, bc):
        self.bc = bc

    def getBCTag(self):
        return self.bc


class DFN(object):
    def __init__(self, fractures={}, connectivity={}, description='', properties=[]):
        self.description = description
        self.fractures = {}
        for i,f in enumerate(fractures):
            if f.id:
                self.addFracture(f, id=f.id)
            else:
                self.addFracture(f, id=i)

        self.connectivity = {}  # key=connection id, value=list of fracture.id
        if connectivity:
            for c in connectivity:
                self.addConnection(c)
        self.properties = properties
        self.north = None       # North direction

    def __repr__(self):
        s =  'DFN: '
        s += '(%d Fractures, ' % self.fractures.__len__()
        s += '%d Connections)' % self.connectivity.__len__()
        return s

    def __add__(self, dfn):
        # creates new DFN from two existing DFN's
        # fracture and connection ID's are updated
        # description is added
        dfn2 = DFN(fractures=self.getFractures(), connectivity=self.getConnectivity())

        newID = max(dfn2.getFractureIds())
        IDmap = {}  # remember how fracture id's where changed, and use that for adding connectivity
        for f in dfn.getFractures():
            newID += 1
            IDmap[f.getId()] = newID
            f.setId(newID)
            dfn2.addFracture(f, id=newID)

        for c in dfn.getConnectivity():
            i1, i2 = c.getId()
            c.setId((IDmap[i1], IDmap[i2]))
            dfn2.addConnection(c)

        if self.getNorthDirection() and dfn.getNorthDirection():
            # if self.getNorthDirection() != dfn.getNorthDirection():
            if abs(self.getNorthDirection().getAngle(dfn.getNorthDirection())) > 0:
                print("WARNING: DFN's have different North directions!")
                print("        ", self, '\t', self.getNorthDirection())
                print("        ", dfn, '\t', dfn.getNorthDirection())
        elif self.getNorthDirection():
            dfn2.setNorthDirection(self.getNorthDirection())
        elif dfn.getNorthDirection():
            dfn2.setNorthDirection(dfn.getNorthDirection())

        # description
        txt = 'result from dfn1 + dfn2\n'
        txt += 'DFN1: ' + self.description + '\n'
        txt += 'DFN2: ' + dfn.description + '\n'
        dfn2.setDescription(txt)
        return dfn2

    def getDescription(self):
        return self.description

    def setDescription(self, txt):
        self.description = txt
        return

    def addFracture(self, f, id=None):
        if id is None:
            if len(self.getFractures()) == 0:
                id = 0
            else:
                id = sorted(self.getFractureIds())[-1] + 1
        f.setId(id)
        self.fractures[id] = f
        return

    def removeFracture(self, id):
        if isinstance(id, Fracture):
            id = id.id
        self.fractures.pop(id)
        return

    def setFractures(self, fractures):
        for f in fractures:
            self.addFracture(f, id=f.id)
        return

    def getFractures(self):
        # return self.fractures.values()
        return self.fractures.values()

    def getFractureIds(self):
        # return self.fractures.keys()
        return self.fractures.keys()

    def getFracture(self, n):
        return self.fractures[n]

    def getProperties(self):
        if len(self.properties) < 1:
            tmp = []
            for f in self.getFractures():
                tmp.extend(f.getProperties())
            self.properties = sorted(set(tmp))
        return self.properties

    def getConnection(self, connId):
        try:
            return self.connectivity[connId]
        except:
            return None

    def addConnection(self, connection):
        self.connectivity.update({connection.getId(): connection})
        return

    def removeConnection(self, id):
        if isinstance(id, Connection):
            id = id.id
        self.connectivity.pop(id)
        return

    def getConnectivity(self):
        return self.connectivity.viewvalues()

    def viewConnectivity(self):
        return self.connectivity.viewitems()

    def computeConnectivity(self, silent=True):
        self.connectivity = {}
        # self.connections = {}

        connections = []
        sortedkeys = sorted(self.getFractureIds())
        for i,k in enumerate(sortedkeys[:-1]):
            fracture = self.getFracture(k)
            # print 'working on fracture: ', fracture
            if not silent:
                print('working on ', fracture)
            for k2 in sortedkeys[i+1:]:
            # for k2 in sortedkeys:
                fracture2 = self.getFracture(k2)
                con = fracture.getIntersection(fracture2)
                if con:
                    connections.append(con)
                    # self.connectivity[id] = sorted([fracture.id, fracture2.id])

        self.connectivity = dict([(c.id, c) for c in connections])
        print('Found %d connections.' % len(self.connectivity))
        return

    def getConnectedFractureIds(self, fractureId, recursive=False, ignoreIds=[]):
        "returns a list of fractures that is connected to <fracture>"
        # print '\nsearching for fractureId = ' , fractureId
        # if ignoreIds:
            # print '    skipping ', ignoreIds

        fractureIds = []
        if not recursive:
            for k in list(set(self.connectivity.keys()) - set(ignoreIds)):
                if fractureId in k:
                    fractureIds.extend(k)

            fractureIds = sorted(set(fractureIds)-set([fractureId]))

            # print '    fractureIds=', fractureIds
        else:
            foundIds = set([fractureId])

            # print '\n-------------\ndegree 1'
            # print 'fractureIds = ', fractureIds
            # print 'foundIds = ', foundIds
            # print 'ignoreIds = ', ignoreIds

            fractureIds = self.getConnectedFractureIds(fractureId, ignoreIds=fractureIds)

            n = len(fractureIds)
            # for tmp in range(7):
            # while(len(foundIds) < len(fractureIds)):
            if len(fractureIds) == 0:
                keepGoing = False
            else:
                keepGoing = True
            while(keepGoing):

                # print '\n-------------\ndegree '
                # print 'fractureIds = ', fractureIds
                # print 'foundIds = ', foundIds

                ids = set([])
                for k in set(fractureIds)-set(foundIds):
                    for id in self.getConnectedFractureIds(k, ignoreIds=foundIds):
                        ids.add(id)

                [foundIds.add(fr) for fr in fractureIds]
                fractureIds = sorted(set(fractureIds + list(ids)))

                # print '    fractureIds=', fractureIds

                if len(foundIds) == len(fractureIds): keepGoing = False

            # print '\n-------------\ndegree 3'
            # print 'fractureIds = ', fractureIds
            # print 'foundIds = ', foundIds

            # ids = set([])
            # for k in set(fractureIds)-set(foundIds):
                # for id in self.getConnectedFractureIds(k, ignoreIds=foundIds):
                    # ids.add(id)

            # [foundIds.add(fr) for fr in fractureIds]
            # fractureIds = sorted(set(fractureIds + list(ids)))

            # print '\nFINAL: fractureIds=', fractureIds
        return fractureIds

    def getConnectedFractureIds_v2(self, fractureId, recursive=False, ignoreIds=[]):
        "returns a list of fractures that is connected to <fracture>"
        print('\nsearching for fractureId = ' , fractureId)
        if ignoreIds:
            print('    skipping ', ignoreIds)

        fractureIds = []
        if not recursive:
            for k in list(set(self.connectivity.keys()) - set(ignoreIds)):
                if fractureId in k:
                    fractureIds.extend(k)

            fractureIds = sorted(set(fractureIds)-set([fractureId]))

        else:
            foundIds = set([fractureId])

            print('\n-------------\ndegree 1')
            print('fractureIds = ', fractureIds)
            print('foundIds = ', foundIds)
            print('ignoreIds = ', ignoreIds)

            fractureIds = self.getConnectedFractureIds(fractureId, ignoreIds=fractureIds)


            print('\n-------------\ndegree 2')
            print('fractureIds = ', fractureIds)
            print('foundIds = ', foundIds)

            ids = set([])
            for k in set(fractureIds)-set(foundIds):
                for id in self.getConnectedFractureIds(k, ignoreIds=foundIds):
                    ids.add(id)

            [foundIds.add(fr) for fr in fractureIds]
            fractureIds = sorted(set(fractureIds + list(ids)))


            print('\n-------------\ndegree 3')
            print('fractureIds = ', fractureIds)
            print('foundIds = ', foundIds)

            ids = set([])
            for k in set(fractureIds)-set(foundIds):
                for id in self.getConnectedFractureIds(k, ignoreIds=foundIds):
                    ids.add(id)

            [foundIds.add(fr) for fr in fractureIds]
            fractureIds = sorted(set(fractureIds + list(ids)))


            # keepGoing = True
            # while(keepGoing):
                # print 'n < len(fractureIds) : ', n, ' < ', len(fractureIds)

                # ans = []
                # for k in fractureIds:
                    # ans.extend( self.getConnectedFractureIds(k, recursive=False) )

                # fractureIds = sorted(set(ans+fractureIds)-set([fractureId]))
                # keepGoing = bool(set(ans))
                # print 'ans = ', ans
        print('FINAL: fractureIds=', fractureIds)
        return fractureIds

    def getConnectedFractureIds_v1(self, fractureId, recursive=False):
        "returns a list of fractures that is connected to <fracture>"
        print('\nfractureId = ' , fractureId)
        fractureIds = []
        if not recursive:
            for k in self.connectivity.keys():
                if fractureId in k:
                    fractureIds.extend(k)

            fractureIds = sorted(set(fractureIds)-set([fractureId]))
        else:
            n = len(fractureIds)
            fractureIds = self.getConnectedFractureIds(fractureId, recursive=False)
            keepGoing = True
            while(keepGoing):
                print('n < len(fractureIds) : ', n, ' < ', len(fractureIds))

                ans = []
                for k in fractureIds:
                    ans.extend( self.getConnectedFractureIds(k, recursive=False) )

                fractureIds = sorted(set(ans+fractureIds)-set([fractureId]))
                keepGoing = bool(set(ans))
                print('ans = ', ans)

        print('fractureIds=', fractureIds)
        return fractureIds

    def isConnectedTo(self, fractureId1, fractureId2):
        return fractureId2 in self.getConnectedFractureIds(fractureId1)

    def getBBox(self):
        if not self.getFractures():
            print('ERROR: Fracture Network does not contain fractures. Cannot compute bounding box.')
            return
        bb = np.array([f.getBBox() for f in self.getFractures()])
        return (tuple(bb[:,0,:].min(axis=0)), tuple(bb[:,1,:].max(axis=0)))

    def getBBoxDimension(self):
        return tuple(np.array(self.getBBox()[1]) - np.array(self.getBBox()[0]))

    def setNorthDirection(self, v):
        if not type(v) == Vector:
            v = Vector(v)
        self.north = v
        return

    def getNorthDirection(self):
        return self.north

    def scale(self, ax, ay=None, az=None):
        for f in self.getFractures():
            f.scale(ax, ay, az)
        return

    def cropWithBoundingBox(self, bbox):
        """crops fractures with bbox object
        and returns new dfn object"""

        center = bbox.getCenter()
        dfn = DFN(fractures=self.getFractures())

        for patch in bbox.get6Patches():
            plane = patch.getPlane()
            v = plane.getVectorToPoint(center)
            for i in range(len(dfn.getFractures())):
                fid, f = dfn.fractures.popitem()
                patch1, patch2 = f.cutWithPlane(plane)
                for pp in [patch1, patch2]:
                    if len(pp.getPoints()) > 0:
                        if plane.getVectorToPoint(pp.getCenter()).dot(v) > 0:
                            f2 = Fracture(points=pp.getPoints())
                            f2.aperture = f.getAperture()
                            dfn.addFracture(f2)

        # reset fracture ids
        for i, id in enumerate(sorted(dfn.getFractureIds())):
            dfn.addFracture(dfn.fractures.pop(id), id=i)

        return dfn

    def save(self, fname):
        pickle.dump(self, open(fname, 'w'))

    def writeTSFile(self, fname=None):
        """ writes TS file containing all fractures
            each fracture is written as a triangle, formed by two consecutive points
            and the fracture center
        """
        if fname is None:
            if hasattr(self, 'fname'):
                fname = self.fname
            else:
                fname = 'DFN.ts'

        # header
        s = 'GOCAD TSurf 1\n'
        s += 'HEADER{\n'
        s += 'name:%s\n' % fname
        s += 'mesh:false\n'
        s += '}\n'
        if len(self.getProperties()) > 0:
            s += 'PROPERTIES '
        for k in self.getProperties():
            s += k + ' '
        s += '\n'
        s += 'GOCAD_ORIGINAL_COORDINATE_SYSTEM\n'
        s += 'NAME from_XYZ\n'
        s += 'AXIS_NAME "U" "V" "W"\n'
        s += 'AXIS_UNIT "ftUS" "ftUS" "ft"\n'
        s += 'ZPOSITIVE Depth\n'
        s += 'END_ORIGINAL_COORDINATE_SYSTEM\n'
        s += 'GEOLOGICAL_TYPE Undefined\n'

        cnt1 = 0  # counting fractures
        for f in self.getFractures():
            cnt1 += 1
            s += 'TFACE %s\n'% str(f.getId())
            points = f.getPoints()
            center = f.getCenter()
            c = center.getCoordinates()
            s += 'VRTX %d %f %f %f' % (cnt1, c[0], c[1], c[2])
            for k in self.getProperties():
                s += ' %f' % f.properties[k]
            s += '\n'

            nPoints = len(points)
            cnt2 = 0   # counting points of current fracture
            for i, p in enumerate(points):
                cnt2 += 1
                c = p.getCoordinates()
                s += 'VRTX %d %f %f %f' % (cnt1+cnt2, c[0], c[1], c[2])
                for k in self.getProperties():
                    s += ' %f' % f.properties[k]
                s += '\n'

            for i in range(1, len(points)):
                s += 'TRGL %d %d %d\n' % (cnt1, cnt1+i, cnt1+i+1)

            if points[0] != points[-1]:
                s += 'TRGL %d %d %d\n' % (cnt1, cnt1+cnt2, cnt1+1)

            cnt1 = cnt1 + cnt2

        s += 'END\n'

        open(fname, 'w').write(s)
        print('written file ', fname)
        return

    def writeASCIIFile(self, fname=None):
        """ writes Fracture ID and coordinates to ASCII file
            so that DFN can be transferred between different
            versions of DFNlib
        """
        if fname is None:
            if hasattr(self, 'fname'):
                fname = self.fname
            else:
                fname = 'DFN.ascii'

        newfile = open(fname, 'w')
        for f in self.getFractures():
            s = str( (f.getId(), f.getCoordinates(), f.getAperture()) )
            newfile.write('F ' + s + '\n')

        for c in self.getConnectivity():
            s = str( (c.getId(), c.getSegment().getPointCoordinates() ) )
            newfile.write('C ' + s + '\n')

        newfile.close()

        print('written file ', fname)
        return

    def writeConnectivityPLFile(self, fname=None):
        """ writes PL file containing connectivity line segments"""
        if fname is None:
            if hasattr(self, 'fname'):
                fname = self.fname
            else:
                fname = 'Connectivitiy.pl'

        pl = PolyLine()
        pl.setId('Connectivitiy')
        for con in self.getConnectivity():
            seg = con.getSegment()
            pl.addSegment(seg)

        pl.writePLFile(fname)
        return
