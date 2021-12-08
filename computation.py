"""
This module provides computational support for measuring sperm parameters.



Created on 21 Feb 2012

@author: Brian Duffy
"""
from __future__ import division

from PyQt4.QtGui import (QVector2D, QGraphicsView, QGraphicsScene, QPainter, QApplication, QPen)
from PyQt4.QtCore import (QPointF, QLineF, QRectF, Qt)

from math import (pi, cos, acos, atan2, atan, degrees, log, isnan)
from geometry import (toPoint, toVector, intersectPoint)

from mygraphicsitems import (PolyLine)

from scipy.interpolate import (splprep, splev)
from numpy import linspace

#import Numeric
import numpy
import pylab
import sys


def average(values):
    """
        Return the average of a set of scalar values using built in python functions.
    """
    return sum(values) / len(values)


def setValue(size=0, value=0.0):
    """
        Return a python list with every value initialised to value.
    """

    lst = []

    i = 0

    while i < size:
        lst.append(value)
        i += 1

    return lst


def maxFlagellumLength(lst=None):
    """
        Return the maximum flagellum length from the list of flagella lst.
    """

    if lst is None:
        return 0

    lengths = [len(i) for i in lst]

    return max(lengths)


def minFlagellumLength(lst=None):
    """
        Return the minimum flagellum length from the list of flagella lst.
    """

    if lst is None:
        return 0

    lengths = [len(i) for i in lst]

    return min(lengths)


def GrayHancockCoefficients(l=0.001, b=0.09):
    """
        Return the resistive force coefficients for a default set of parameters.

        The resistive forces that are exerted on the flagellum by the fluid the cell is swimming in are given
        by this function. These were originally estimated by Gray and Hancock in 1955.
    """

    Ct = (2.0 * pi) / (log((2.0 * l) / b) - 0.5)
    Cn = 2.0 * Ct

    return Ct, Cn


def convertPathForNumPy(path=None):
    """
        Return x, y, the numpy conversion of the python list of QPointF objects.
    """

    if path is None:
        return

    N = len(path)
    lst = setValue(N)
    x = numpy.array(lst)
    y = numpy.array(lst)

    for i in range(N):
        x[i] = path[i].x()
        y[i] = path[i].y()

    return x, y


def convertNumPyToPath(x, y):
    """
        Return path, the combination of numpy arrays x and y into a list of QPointF objects.
    """

    path = []

    N = len(x)

    for i in range(N):
        path.append(QPointF(x[i], y[i]))

    return path


def fitSpline(points, smoothness, degree, nPoints=100):
    """
        Return a smoothed list of QPointF points representing a path.

        This function uses the native numpy library to smooth a set of points and to interpolate values to a
        specific number of points for computation later.

        points      : the set of points to be smoothed of arbitrary size.
        smoothness  : smoothness parameter.
        degree      : the degree of the polynomial used to do smooth interpolation between points.
        nPoints     : number of points to output on the smoothed path.
    """

    x, y = convertPathForNumPy(points)

    # find the knot points

    t, u = splprep([x, y], s=smoothness, k=degree)

    # evaluate spline, including interpolated points
    xNew, yNew = splev(linspace(0, 1, nPoints), t)

    return convertNumPyToPath(xNew, yNew)


def factorial(n):
    """
        Return the factorial of a number n.
    """

    f = 1.0

    for i in range(0, n):
        f *= (n - i)

    return f


def choose(n, k):
    """
        Return the number of permutations for a set of numbers and choices.
    """

    return factorial(n) / (factorial(k) * factorial(n - k))


def binomialCoefficients(n):
    """
        Return a list of the binomial coefficients for a polygon.
    """

    coefficients = []

    if n > 0:
        for i in range(0, n + 1):
            coefficients.append((-1.0 ** i) * choose(n, i))

    return coefficients


def forwardDifference(f, n=1):
    """
        Return a list, diff, of the forward discrete approximations of the nth derivatives for a 1D function.

        This is a general purpose function for computing the finite forward difference approximation of the
        derivatives of a function f to the nth degree, i.e. n = 1 yields the first derivative.
    """

    N = len(f)

    coefficients = binomialCoefficients(n)
    diff = setValue(N)

    for x in range(N):
        for i in range(n):
            index = x + (n - i)
            if index > N - 1:
                index = N - 1
            diff[x] += coefficients[i] * f[index]

    return diff


def backwardDifference(f, n=1):
    """
        Return a list, diff, of backward discrete approximations of the nth derivatives for a 1D function.

        This is a general purpose function for computing the finite backward difference approximation of the
        derivatives of a function f to the nth degree, i.e. n = 1 yields the first derivative.
    """

    N = len(f)
    coefficients = binomialCoefficients(n)
    diff = setValue(N)

    for x in range(N):
        for i in range(n):
            index = x - i
            if index < 0:
                index = 0
            diff[x] += coefficients[i] * f[index]

    return diff


def centralDifference(f, n=1):
    """
        Return a list, diff, of central discrete approximations of the nth derivatives for a 1D function.

        This is a general purpose function for computing the finite central difference approximation of the
        derivatives of a function f to the nth degree, i.e. n = 1 yields the first derivative.
    """

    N = len(f)

    even = ((n % 2) == 0)
    coefficients = binomialCoefficients(n)
    diff = setValue(N)

    for x in range(N):
        for i in range(n):
            index = x + n - 2 * i

            if even:
                index = x + ((n * 0.5) - i)

            if index < 0:
                index = 0

            if index > N - 1:
                index = N - 1

            diff[x] = coefficients[i] * f[index]

        if not even:
            diff[x] *= 0.5

    return diff


def distance(p1, p2):
    """
        Return the Euclidean distance between two QPointF objects.

        Euclidean distance function in 2D using Pythagoras Theorem and linear algebra
        objects. QPointF and QVector2D member functions.
    """

    if not (isinstance(p1, QPointF) and isinstance(p2, QPointF)):
        raise ValueError('ValueError, computing distance p1 or p2 not of Type QPointF')

    return toVector(p2 - p1).length()


def closestPoint(point, pointSet):

    minDist = distance(point, pointSet[0])
    minPT = pointSet[0]

    for p in pointSet:
        if minDist > distance(point, p):
            minDist = distance(point, p)
            minPT = point

    return minPT


def slopeFromPoints(p1, p2):
    """
        Euclidean slope defined by two 2D points
    """

    if not (isinstance(p1, QPointF) and isinstance(p2, QPointF)):
        raise ValueError('computing distance p1 or p2 not of Type QPointF')

    numerator = p2.y() - p1.y()
    denominator = p2.x() - p1.x()

    if denominator == 0.0:
        return numerator

    return numerator / denominator


def slopeFromVector(v):
    """
        Return the slope of a vector from a QVector2D object.
    """

    if v.x() == 0.0:
        return v.y()

    return v.y() / v.x()


def averageVelocity(centroids=None):
    """
        Return the average instantaneous velocity of a path given a list of QPointF objects.

       Compute the average velocity from the instantaneous velocities of an arbitrary path in 2D.
       All that is required is that the path is a set of QPointF objects
    """

    if centroids is None:
        return 0.0

    N = len(centroids)

    if N < 3:
        return 0.0

    avgVelocity = 0.0
    
    for i in range(1, N - 1):

        if not isinstance(centroids[i], QPointF):
            print 'this is not at QPointF? -> %s' % centroids[i]
            raise TypeError('computing average velocity')

        avgVelocity += 0.5 * (distance(centroids[i + 1], centroids[i]) + distance(centroids[i], centroids[i - 1]))

    # if we handle the boundary conditions separately we can avoid repeatedly
    # evaluating if statements in the main loop to determine if the boundary
    # conditions have been met
    avgVelocity += distance(centroids[1], centroids[0])
    avgVelocity += distance(centroids[-1], centroids[-2])
    
    return avgVelocity / N


def straightLineVector(centroids=None):
    """
        Return the straight line vector from a path of centroids QPointF objects.

        This is the vector between the start and end points of the path.
    """

    if centroids is None:
        return QVector2D(0.0, 0.0)

    N = len(centroids)

    if N < 1:
        QVector2D(1.0, 0.0)

    return toVector(centroids[len(centroids) - 1] - centroids[0])


def straightLineVelocity(centroids=None):
    """
        Return the straight line velocity from a path of centroids QPointF objects.
    """

    if centroids is None:
        return 0.0

    N = len(centroids)

    if N < 1:
        return 0.0

    return distance(centroids[-1], centroids[0]) / N


def averagePosition(centroids=None):
    """
        Return the average position from the set of QPointF points.
    """

    if centroids is None:
        return QPointF(0.0, 0.0)

    N = len(centroids)

    avgPathos = QPointF(0.0, 0.0)

    for pos in centroids:
        avgPathos += pos
    
    return avgPathos / N


def averageVector(centroids=None):
    """
        Return the average direction vector from a set of QPointF points
    """

    if centroids is None:
        return QPointF(0.0, 0.0)

    N = len(centroids)

    avgVec = QVector2D(0.0, 0.0)

    for i in range(N - 1):
        avgVec += toVector(centroids[i + 1] - centroids[i])
    
    return avgVec / (N - 1)


def hanning(w):
    """
        Return a Hanning window, a list of floating point weights, of length w.
    """

    window = []

    m = int(w * 0.5)
    a = w * 0.5

    for j in range(-m, m + 1):
        window.append(0.5 * (1.0 + cos((pi * j) / a)))

    return window


def hamming(w):
    """
        Return a Hamming window, a list of floating point weights, of length w.
    """

    window = []

    m = int(w * 0.5)
    a = w * 0.5

    for j in range(-m, m + 1):
        window.append(0.54 + 0.46 * cos((pi * j) / a))

    return window


def blackman(w):
    """
        Return a Blackman window, a list of floating point weights, of length w.

        The coefficients in this function are taken from the description of the Blackman window on Wikipedia.
    """

    c0 = 0.42659
    c1 = 0.24828
    c2 = 0.038424

    window = []

    m = int(w * 0.5)
    a = w * 0.5

    for j in range(-m, m + 1):
        window.append(c0 + c1 * cos((pi * j) / a) + c2 * cos((2.0 * pi * j) / a))

    return window


def smooth(path, window):
    """
        Return a smoothed list of QPointF point objects that are smoothed using an arbitrary window.

        Here we take a list of points representing a path and smooth the path by passing a window over the points.

        path   : is a list of QPointF objects representing a path.
        window : is a list of scalar weights precomputed using a window function i.e. hanning, hamming or blackman.

    """

    N = len(path)
    w = len(window)

    padded = setValue(w, path[0]) + path + setValue(w, path[-1])
    smoothed = []

    if N < w or w < 3:
        return path

    n = 2.0 / w

    smoothed.append(path[0])

    for i in range(w + 1, w + N - 1):

        m = int(w * 0.5)
        sumPoint = QPointF(0.0, 0.0)
        k = 0

        for j in range(-m, m + 1):
            sumPoint += padded[i + j] * window[k]
            k += 1
        
        sumPoint *= n
        smoothed.append(sumPoint)
    
    smoothed.append(path[N - 1])

    return smoothed


def catMullRomFit(p, nPoints=100):
    """
        Return as smoothed path from a list of QPointF objects p, interpolating points if needed.

        This function takes a set of points and fits a CatMullRom Spline to the data. It then
        interpolates the set of points and outputs a smoothed path with the desired number of points
        on it.

        p       : the path to be smoothed
        nPoints : the desired number of points in the smoothed path
    """

    N = len(p)

    #there is no re interpolation required
    if N == nPoints:
        return p

    interp = []
    dj = 1.0 / nPoints

    for j in range(0, nPoints):

        di = j * dj * (N - 1)
        i = int(di)

        x = di - i
        xx = x * x
        xxx = x * x * x

        c0 = 2.0 * xxx - 3.0 * xx + 1.0
        c1 = xxx - 2.0 * xx + x
        c2 = -2.0 * xxx + 3.0 * xx
        c3 = xxx - xx

        p0 = p[i]
        p1 = p0
        p2 = p0
        p3 = p0

        if i + 1 < N:
            p1 = p[i + 1]

        if i - 1 > -1:
            p2 = p[i - 1]

        if i + 2 < N:
            p3 = p[i + 2]

        m0 = toVector(p1 - p2) * 0.5
        m1 = toVector(p3 - p0) * 0.5
        px = (c0 * toVector(p0)) + (c1 * m0) + (c2 * toVector(p1)) + (c3 * m1)

        interp.append(toPoint(px))

    # pop back the last one
    interp.pop()

    # make sure the last point in the original polygon is still the last one
    interp.append(p[-1])

    return interp


def amplitudes(path, avgPath):
    """
        Return a list of the amplitudes of sperm tract

        Where the amplitude is defined as the difference between the corresponding points of the sperm path and its
        average path.
    """

    N = len(path)
    M = len(avgPath)

    if not (M == N):
        raise IndexError('IndexError, dimensions of curvilinear and average paths don\'t match')

    amps = setValue(N)

    for i in range(N):
        amps[i] = 2.0 * (toVector(path[i]) - toVector(avgPath[i])).length()
    
    return amps


def intersectPoints(path, avgPath):
    """
        Return a list of all of the intersection points between the sperm path and it's average path

        This is achieved using a less than optimal algorithm, N^2. All line segments are computed for
        each of the paths and all line segments are tested for intersection.

        path     : set of QPointF objects representing the path of a sperm
        avgPath  : a smoothed version of path
    """

    intersections = []
    N = len(path)
    M = len(avgPath)

    if not (M == N):
        return intersections
    
    pathLines = []
    avgLines = []

    for i in range(0, N - 1):
        p1 = path[i]
        p2 = path[i + 1]
        q1 = avgPath[i]
        q2 = avgPath[i + 1]

        pathLines.append(QLineF(p1, p2))
        avgLines.append(QLineF(q1, q2))

    # N^2 algorithm unfortunately
    for l1 in pathLines:
        for l2 in avgLines:
            isIntersect, intersect = intersectPoint(l1, l2)
            if isIntersect:
                intersections.append(intersect)

    if not len(intersections):
        intersections.append(path[-1])

    elif intersections[-1] != path[-1]:
        intersections.append(path[-1])

    return intersections


def signedAngle(u, v):
    """
        Return the signed angle between two vectors.
    """

    m1 = slopeFromVector(u)
    m2 = slopeFromVector(v)

    return atan(abs(m2 - m1) / (1 + m1 * m2))


#noinspection PyArgumentList
def dotAngle(u, v):
    """
        Return the unsigned angle between two vectors using the dot product.
    """

    theta = QVector2D.dotProduct(u, v) / (u.length() * v.length())

    return degrees(acos(theta))


def polarAngle(u):
    """
        Return for a given vector, its polar angle in radians given and orthonormal basis.
    """
    return atan2(u.y(), u.x())


def meanAngularDensity(centroids, rads=False):
    """
       Return the average of the instantaneous turning angles of the head of the cell.
    """

    N = len(centroids)
    mad = 0.0
    angle = 0.0

    for i in range(1, N - 1):
        u = toVector(centroids[i] - centroids[i - 1])
        v = toVector(centroids[i + 1] - centroids[i])
        signed = signedAngle(u, v)
        angle += signed
        mad += abs(signed)
    
    mad /= (N - 2)
    angle /= (N - 2)

    if rads:
        return mad, angle

    return degrees(mad), degrees(angle)


def arcLength(flagellum):
    """
        Return the arc length of a set of QPointF objects representing a flagellum.
    """

    N = len(flagellum)
    arcLength = 0.0

    for i in range(N - 1):
        arcLength += distance(flagellum[i], flagellum[i + 1])

    return arcLength


def averageArcLength(flagella):
    """
        Return the average arc length of a set of flagella.
    """

    N = len(flagella)
    avg = 0.0

    for i in range(N):
        avg += arcLength(flagella[i])
    
    return avg / N


def changeInAngle(centroid, flagellum):
    """
        Return the change in angle of the flagellum over its entire length

        centroid  : the centroid position of head of the cell is needed to compute the medial axis.
        flagellum : the set of points representing the captured flagellum.
    """

    if len(flagellum) < 1:
        return 0.0

    axis = toVector(flagellum[0] - centroid)
    u = toVector(flagellum[1] - flagellum[0])
    v = toVector(flagellum[-1] - flagellum[-2])
    baseAngle = abs(signedAngle(axis, u))
    endAngle = abs(signedAngle(axis, v))

    return endAngle - baseAngle


def averageChangeInAngle(centroids, flagella, rads=False):
    """
        Return the average change in angle of a set of captured flagella.
    """

    N = len(flagella)
    avg = 0.0

    for i in range(N):
        avg += changeInAngle(centroids[i], flagella[i])
    
    avg /= N

    if rads:
        return avg

    return degrees(avg)


def normalVector(vec):
    """
        Return the 2D normal vector of a QVector2D object.
    """
    return QVector2D(-vec.y(), vec.x())


def tangentVector(flagellum, j=0):
    """
        Return the tangent vector to a polygon representing a flagellum at the jth position.
    """

    last = len(flagellum) - 1

    if j < 0 or j > last:
        return QVector2D(0.0, 0.0)

    if not j:
        return toVector(flagellum[j + 1] - flagellum[j]) / distance(flagellum[j + 1], flagellum[j])

    elif last == j:
        return toVector(flagellum[j] - flagellum[j - 1]) / distance(flagellum[j], flagellum[j - 1])

    else:
        return toVector(flagellum[j + 1] - flagellum[j - 1]) / (distance(flagellum[j + 1], flagellum[j - 1]) * 0.5)


def positionVector(i, j, flagella):
    """
        Return the change in position of the flagellum at the ith frame using differencing.
    """

    last = len(flagella) - 1

    if i < 0 or i > last:
        return QVector2D(0.0, 0.0)
    
    if not i:
        return toVector(flagella[i + 1][j] - flagella[i][j])

    elif i == last:
        return toVector(flagella[i][j] - flagella[i - 1][j])

    else:
        return toVector(flagella[i + 1][j] - flagella[i - 1][j]) * 0.5


def viscousDrag(i, flagella):
    """
        Return the viscous drag forces as a vector, acting on the flagellum at the ith frame.
    """

    l = arcLength(flagella[i])
    Ct, Cn = GrayHancockCoefficients(l)
    
    def substitute(i, j):

        t = tangentVector(flagella[i], j)
        n = normalVector(t)
        U = positionVector(i, j, flagella)

        #noinspection PyArgumentList
        sn = QVector2D.dotProduct(n, U) * Cn

        #noinspection PyArgumentList
        st = QVector2D.dotProduct(t, U) * Ct

        F = t * st
        G = n * sn

        return F, G

    N = len(flagella[i])

    viscousDrag = QVector2D(0.0, 0.0)

    for j in range(N - 1):
        dS = distance(flagella[i][j], flagella[i][j + 1])
        Fij, Gij = substitute(i, j)
        Fij1, Gij1 = substitute(i, j + 1)
        viscousDrag += dS * (Fij + Gij + 0.5 * (Fij1 + Gij1 - Fij - Gij))
    
    return viscousDrag


def averageViscousDrag(flagella):
    """
      Return the average viscous drag forces over a set of captured flagella.
    """

    N = len(flagella)

    totalViscousDrag = 0.0

    for i in range(N):
        totalViscousDrag += viscousDrag(i, flagella)
    
    return totalViscousDrag / N
 

def torque(i, flagella, viscosity):
    """
        Return the viscous drag forces as a single scalar value, acting on the flagellum at the ith frame.
    """

    Ct, Cn = GrayHancockCoefficients()
    
    def substitute(i, j):

        t = tangentVector(flagella[i], j)
        n = normalVector(t)
        U = positionVector(i, j, flagella)

        #noinspection PyArgumentList
        sn = QVector2D.dotProduct(n, U) * Cn

        #noinspection PyArgumentList
        st = QVector2D.dotProduct(t, U) * Ct

        F = t * st
        G = n * sn

        return F + G

    N = len(flagella[i])

    torque = 0.0

    for j in range(N - 1):

        dS = distance(flagella[i][j], flagella[i][j + 1])
        fij = substitute(i, j)
        fij1 = substitute(i, j + 1)
        Xij = flagella[i][j]
        Xij1 = flagella[i][j + 1]

        torque += dS * ((Xij.x() * fij.y() - Xij.y() * fij.x()) +
                        0.5 * (Xij1.x() * fij1.y() - Xij1.y() * fij1.x()
                               - Xij.x() * fij.y() - Xij.y() * fij.x()))
    
    if isnan(torque):
        torque = 0.0

    return abs(torque) * viscosity


def averageTorque(flagella, viscosity):
    """
      Return the average viscous drag forces over a set of captured flagella.
    """

    N = len(flagella)

    totalTorque = 0.0

    for i in range(N):
        totalTorque += torque(i, flagella, viscosity)
    
    return totalTorque / N


def signedDistance(p, l1, l2):
    """
        Return the signed distance of a point in relation to a line segment.
    """
    return  (l1.x() - p.x()) * (l2.y() - p.y()) - (l2.x() - p.x()) * (l1.y() - p.y())


def asymmetry(centroid, flagellum):
    """
        Return the amount of asymmetry in the flagellum about the medial axis.
    """

    if len(flagellum) < 1:
        return 0.0

    l1 = centroid
    l2 = flagellum[0]
    a = 0.0

    for p in flagellum:
        a += signedDistance(p, l1, l2)
    
    return a


def averageAsymmetry(centroids, flagella):
    """
        Return the average asymmetry over a set of flagella.
    """

    N = len(flagella)

    totalAsymmetry = 0.0

    for i in range(N):
        totalAsymmetry += asymmetry(centroids[i], flagella[i])
    
    return totalAsymmetry / N


def printPath(centroids):
    """
        Print a path of QPointF objects.
    """
    for pair in enumerate(centroids):
        print "%.2f, %.2f" % (pair[1].x(), pair[1].y())


def graphKinematics(path, avgPath, ints):
    fig = pylab.figure()
    pathX, pathY = convertPathForNumPy(path)
    avgX, avgY = convertPathForNumPy(avgPath)
    intX, intY = convertPathForNumPy(ints)
    curvilinear, average, intersections = pylab.plot(pathX,  pathY,  'r-',
                                                     avgX,   avgY,   'g-',
                                                     intX,   intY,   'bo')
    fig.legend((curvilinear, average, intersections), ('curvilinear', 'average', 'intersections'), 'upper right')
    pylab.xlabel('x position')
    pylab.ylabel('y position')
    pylab.title('Sperm Kinematics')
    pylab.grid(True)
    pylab.savefig('sperm_kinematics')
    pylab.show()


def testKinematics():     
    path = [QPointF(0, 0), QPointF(2, -4), QPointF(5, -1), QPointF(7, 3), QPointF(7, 6),
            QPointF(6, 8), QPointF(7, 12), QPointF(10, 15), QPointF(13, 14), QPointF(16, 10),
            QPointF(19, 9), QPointF(22, 12), QPointF(22, 15), QPointF(23, 18), QPointF(26, 19),
            QPointF(29, 16), QPointF(29, 13), QPointF(32, 11), QPointF(34, 9), QPointF(34, 5), QPointF(30, 2)]

    han = hanning(10)
    print 'hanning : ', len(han)
    avgPath = smooth(path, han)
    ints = intersectPoints(path, avgPath)
    amps = amplitudes(path, avgPath)
    
    VCL = averageVelocity(path)
    VAP = averageVelocity(avgPath) 
    VSL = straightLineVelocity(path)
    mad, angle = meanAngularDensity(path)
    
    print "----------  Kinematic Measures  -------------"
    print "\nCell Vigour \n---------------------"
    print "VCL           : %f micrometers per second" % VCL
    print "VAP           : %f micrometers per second" % VAP
    print "VSL           : %f micrometers per second" % VSL
    print "\nCell Swimming Pattern \n---------------------"
    print "ALH (maximum) : %f micrometers" % max(amps)
    print "ALH (average) : %f micrometers" % (sum(amps) / len(amps))
    print "BCF           : %f Hz         " % len(ints)
    print "MAD           : %f degrees    " % mad
    print "\nCell Progressiveness \n---------------------"
    print "LIN           : %f " % (VSL / VCL)
    print "WOB           : %f " % (VAP / VCL)
    print "STR           : %f " % (VSL / VAP)
    
    fig = pylab.figure()
    pathX, pathY = convertPathForNumPy(path)
    avgX, avgY = convertPathForNumPy(avgPath)
    intX, intY = convertPathForNumPy(ints)
    
    curvilinear, average, ints = pylab.plot(pathX,  pathY,  'rs-',
                                            avgX,   avgY,   'gs-',
                                            intX,   intY,   'bs')

    fig.legend((curvilinear, average, ints), ('curvilinear', 'average', 'intersections'), 'upper right')
    pylab.xlabel('x position')
    pylab.ylabel('y position')
    pylab.title('Sperm Kinematics')
    pylab.grid(True)
    pylab.savefig('sperm_kinematics')
    pylab.show()


def testMechanics():
    
    flagellum = [QPointF(0.0, 5.0), QPointF(0.5, 4.8),  QPointF(1.0, 4.6),  QPointF(1.5, 4.2),
                 QPointF(2.0, 4.1), QPointF(2.5, 4.3), QPointF(3.0, 5.0),  QPointF(3.5, 5.6),
                 QPointF(4.0, 6.0), QPointF(4.5, 6.1), QPointF(5.0, 6.25), QPointF(5.5, 6.2),
                 QPointF(6.0, 6.1), QPointF(6.5, 6.2), QPointF(7.0, 6.4),  QPointF(7.5, 6.37),
                 QPointF(8.0, 6.35)]
    
    axis = [QPointF(0.0, 5.0), QPointF(8.0, 5.0)]

    asymmetry(QPointF(-1.0, 5.0), flagellum)

    fx, fy = convertPathForNumPy(flagellum)
    ax, ay = convertPathForNumPy(axis)

    pylab.plot(fx,  fy, 'r-')
    pylab.plot(ax,  ay, 'b-')
    pylab.xlabel('x position')
    pylab.ylabel('y position')
    pylab.title('Sperm Mechanics')
    pylab.grid(True)
    pylab.savefig('sperm_mechanics')
    pylab.show()


def testCatMullRom():

    print "calling CatMulRom test"

    poly = [QPointF(10.0, 150.0), QPointF(125.0, 175.0),
            QPointF(170.0,  50.0), QPointF(210.0,  40.0),
            QPointF(320.0, 400.0), QPointF(450.0, 321.0)]

    width = 800
    height = 600

    print "polygon : ", poly

    print('testing dialogs')
    app = QApplication(sys.argv)
    app.setApplicationName("Test CatMullRom")

    scene = QGraphicsScene(QRectF(0.0, 0.0, width, height))
    scene.setItemIndexMethod(QGraphicsScene.NoIndex)
    scene.addItem(PolyLine(poly, QPen(Qt.red, 3.0)))

    polyFit = catMullRomFit(poly, 100)
    scene.addItem(PolyLine(polyFit, QPen(Qt.green, 3.0)))

    view = QGraphicsView(scene)
    view.setRenderHint(QPainter.Antialiasing)
    view.setRenderHint(QPainter.TextAntialiasing)

    print "setting scene"
    view.scene().setItemIndexMethod(QGraphicsScene.NoIndex)

    view.show()

    sys.exit(app.exec_())

if __name__ == "__main__":

    testCatMullRom()