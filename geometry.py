from __future__ import division

from math import (pi, sin, cos, sqrt)
from numpy import (dot, concatenate, repeat, argmax, argmin, take, random, array)

from PyQt4.QtGui import (QPolygonF, QVector2D)
from PyQt4.QtCore import (QPointF, QRectF, Qt)

import pylab


def toVector(p):
    """
        Return a QPointF object as a QVector2D.
    """
    return QVector2D(p.x(), p.y())


def toPoint(v):
    """
        Return a QVector2D object as a QPointF
    """
    return QPointF(v.x(), v.y())


def circleCircumference(radius):
    """
        Return the circumference of a circle of given radius.
    """
    return 2.0 * pi * radius


def circleArea(radius):
    """
        Return the area of a circle of given radius.
    """
    return pi * radius * radius


def circleRadius(circumference):
    """
        Return the radius of a circle of given circumference
    """
    return circumference / (2.0 * pi)


def square(r, position=QPointF(0.0, 0.0)):
    """
        Return a QRectF object at a given position which contains a circle of radius r.
    """
    return QRectF(position.x() - r, position.y() - r, 2.0 * r, 2.0 * r)


def rectangle(r1, r2, position=QPointF(0.0, 0.0)):
    """
        Return a QRectF object at a given position which contains an ellipse with major radius r1 and minor radius r2.
    """
    return QRectF(position.x() - r1, position.y() - r2, 2.0 * r1, 2.0 * r2)


def polygon(rectangle):
    """
        Return a QPolygonF from a QRectF object.
    """
    return QPolygonF([QPointF(rectangle.x(),                     rectangle.y()),
                      QPointF(rectangle.x() + rectangle.width(), rectangle.y()),
                      QPointF(rectangle.x() + rectangle.width(), rectangle.y() + rectangle.height()),
                      QPointF(rectangle.x(),                     rectangle.y() + rectangle.height())])


def waveyBorder(radius, ALH, BCF):
    """
        Return a QPolygonF that represents a circle of radius that encodes two parameters in it.
    """
    polygon = []
    theta = 0.0
    delta = (2.0 * pi) * 0.001
    while theta <= 2.0 * pi:
        wave = ALH * sin(theta * round(BCF))
        polygon.append(QPointF((radius + wave) * cos(theta), (radius + wave) * sin(theta)))
        theta += delta
    return QPolygonF(polygon)


def spottyBorder(painter, radius, ALH, BCF):
    """
        Draw a primitive border that represents a circle of radius that encodes two parameters in it.
    """
    theta = 0.0
    if BCF > 0.0:
        delta = (2.0 * pi) * (1.0 / BCF)
        while theta < 2.0 * pi:
            c = QPointF(radius * cos(theta), radius * sin(theta))
            rect = square(ALH * 0.5)
            rect.translate(c.x(), c.y())
            painter.setPen(Qt.black)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(rect)
            theta += delta


def lineBorder(painter, radius, ALH, BCF):
    """
        Draw a primitive border that represents a circle of radius that encodes two parameters in it.
    """
    theta = 0.0
    if BCF > 0.0:
        delta = (2.0 * pi) * (1.0 / BCF)
        while theta < 2.0 * pi:
            p1 = QPointF((radius + ALH) * cos(theta), (radius + ALH) * sin(theta))
            p2 = QPointF((radius - ALH) * cos(theta), (radius - ALH) * sin(theta))
            painter.drawLine(p1, p2)
            theta += delta


def isLeft(p1, p2, p3):
    """
        Return a value that indicates if the three QPointF objects make a left turn or not.
    """
    return (p2.x() - p1.x()) * (p3.y() - p1.y()) - (p3.x() - p1.x()) * (p2.y() - p1.y())


def midpoint(p1, p2):
    """
        Return the midpoint between two QPointF objects.
    """
    return QPointF((p1.x() + p2.x()) * 0.5, (p1.y() + p2.y()) * 0.5)


def intersect(l1, l2):
    """
        Return a boolean value indicating if two line segments intersect.

        Taken from Real-Time Rendering
    """
    a = toVector(l2.p2() - l2.p1())
    b = toVector(l1.p2() - l1.p1())
    c = toVector(l1.p1() - l2.p1())
    ap = QVector2D(-a.y(), a.x())
    bp = QVector2D(-b.y(), b.x())

    #noinspection PyArgumentList
    d = QVector2D.dotProduct(c, ap)

    #noinspection PyArgumentList
    e = QVector2D.dotProduct(c, bp)

    #noinspection PyArgumentList
    f = QVector2D.dotProduct(a, bp)

    if f > 0.0:
        if d < 0.0 or d > f:
            return False
        if e < 0.0 or e > f:
            return False
    else:
        if d > 0.0 or d < f:
            return False
        if e > 0.0 or e < f:
            return False

    return True


def intersectPoint(l1, l2):
    """
        Return a bool indicating if two line segments intersect and if they do also return the point of intersection.
    """
    if not intersect(l1, l2):
        return False, QPointF(0.0, 0.0)

    p1 = l1.p1()
    p2 = l1.p2()
    p3 = l2.p1()
    p4 = l2.p2()

    # figure out the intersection point
    a = p1.x() * p2.y() - p1.y() * p2.x()
    b = p3.x() * p4.y() - p3.y() * p4.x()
    d = (p1.x() - p2.x()) * (p3.y() - p4.y()) - (p1.y() - p2.y()) * (p3.x() - p4.x())
    x = a * (p3.x() - p4.x()) - (p1.x() - p2.x()) * b
    y = a * (p3.y() - p4.y()) - (p1.y() - p2.y()) * b

    return True, QPointF(x / d, y / d)


def polygonArea(vertices):
    """
        Return the area of polygon from a set of vertices that must be sorted in cw or ccw order.
    """

    area = 0.0

    # ensure the polygon is at least a triangle
    # note : should also test for co-plainiarity & self intersections of polygon
    #        Jordan test, Real Time Rendering
    if len(vertices) > 2:
        for i in range(len(vertices) - 1):
            area += vertices[i].x() * vertices[i + 1].y() - vertices[i + 1].x() * vertices[i].y()
        area *= 0.5

    return area


def polygonPerimeter(vertices):
    """
        Return the perimeter of polygon from a set of vertices that must be sorted in cw or ccw order.
    """

    perimeter = 0.0

    if len(vertices) > 2:
        for i in range(len(vertices) - 1):
            x = vertices[i + 1].x() - vertices[i].x()
            y = vertices[i + 1].y() - vertices[i].y()
            perimeter += sqrt(x * x + y * y)

    return perimeter


def polygonCentroid(vertices):
    """
        Return the centroid of polygon from a set of vertices that must be sorted in cw or ccw order.
    """
    N = len(vertices)

    if N > 2:
        area = 0.0
        x = 0.0
        y = 0.0

        for i in range(len(vertices) - 1):
            areaTerm = vertices[i].x() * vertices[i + 1].y() - vertices[i + 1].x() * vertices[i].y()
            area += areaTerm
            x += (vertices[i].x() + vertices[i + 1].x()) * areaTerm
            y += (vertices[i].y() + vertices[i + 1].y()) * areaTerm

        area *= 0.5
        scale = 1.0 / (area * 6.0)

        return QPointF(x * scale, y * scale)
    elif N == 2:
        return QPointF(vertices[0].x() - vertices[1].x() * 0.5, (vertices[0].y() - vertices[1].y()) * 0.5)
    else: 
        return QPointF(vertices[0].x(), vertices[0].y())


def qHull(sample):
    """
        Return the convexhull of a set of arbitrary tuple objects samples in the plane.

        sample : as set of points that are represented as tuple objects.
    """
    link = lambda a, b: concatenate((a, b[1:]))
    edge = lambda a, b: concatenate(([a], [b]))

    def dome(sample, base):
        h, t = base
        dists = dot(sample - h, dot(((0, -1), (1, 0)), (t - h)))
        outer = repeat(sample, dists > 0, 0)

        if len(outer):
            pivot = sample[argmax(dists)]
            return link(dome(outer, edge(h, pivot)),
                        dome(outer, edge(pivot, t)))
        else:
            return base
    
    if len(sample) > 2:
        axis = sample[:, 0]
        base = take(sample, [argmin(axis), argmax(axis)], 0)
        return link(dome(sample, base),
                    dome(sample, base[::-1]))
    else:
        return sample


def convertToQPoints(points):
    """
        Return a set of QPointF objects that are converted from tuple objects.
    """

    qtPoints = []

    for point in points:
        qtPoints.append(QPointF(point[0], point[1]))

    return qtPoints


def convertFromQPoints(points):
    """
        Return a set of tuple objects that are converted from QPointF objects.
    """
    numpyPoints = []
    for point in points:
        numpyPoints.append((point.x(), point.y()))

    return array(numpyPoints)


def QtHull(points):
    """
        Return the convexhull of a set of arbitrary QPointF objects samples in the plane.

        sample : as set of points that are represented as QPointF objects.

        This is a wrapper function around the qhull function.
    """

    n = convertFromQPoints(points)

    return convertToQPoints(qHull(n))


if __name__ == "__main__":
    #sample = 10*array([(x,y) for x in arange(10) for y in arange(10)])
    sample = 100 * random.random((32, 2))
    hull = qHull(sample)
    
    pointsX = []
    pointsY = []
    hullX = []
    hullY = []
    
    for (x, y) in sample:
        pointsX.append(x)
        pointsY.append(y)
    
    for (x, y) in hull:
        hullX.append(x)
        hullY.append(y)
        print("(%.2f %.2f)" % (x, y))
    
    px = array(pointsX)
    py = array(pointsY)
    
    hx = array(hullX)
    hy = array(hullY)
    
    qtHull = convertToQPoints(hull)
    
    # compute some measures of the polygon    
    centroid = polygonCentroid(qtHull)
    print("Polygon Centroid  : (%.2f, %.2f)" % (centroid.x(), centroid.y()))
    print("Polygon Perimeter : %f          " % (polygonPerimeter(qtHull)))
    print("Polygon Area      : %f          " % (polygonArea(qtHull)))
    
#    length, width= headDimensions(qtHull)
#    
#    print "Polygon Dimensions : %f, %f" % (length, width)
    
    cx = array([centroid.x()])
    cy = array([centroid.y()])
        
    # show the convex hull and the set of random points
    pylab.plot(px, py, 'ro', hx, hy, 'b-', cx, cy, 'gs')
    pylab.show()
