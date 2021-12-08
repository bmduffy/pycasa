from PyQt4.QtGui  import ( QGraphicsItem, QPen, QPolygonF )
from PyQt4.QtCore import ( Qt )

#noinspection PyOldStyleClasses
class PolyLine(QGraphicsItem):

    def __init__(self, points=None, parent=None):
        super(PolyLine,self).__init__(parent)
        self.__myPoints = QPolygonF(points)
        self.__myPen = QPen(Qt.red, 1.0)
    # end def

    def __init__(self, points=None, pen=QPen(Qt.red,1.0), parent=None):
        super(PolyLine,self).__init__(parent)
        self.__myPoints = QPolygonF(points)
        self.__myPen = pen
    # end def

    def boundingRect(self):
        return self.__myPoints.boundingRect()
    # end def

    def paint(self, painter, option, widget=None):
        painter.setPen( self.__myPen )
        painter.drawPolyline( QPolygonF(self.__myPoints) )
    # end def

    def setPen(self, pen):
        self.__myPen = pen
    # end def

    def setPolyLine(self, points):
        self.__myPoints = QPolygonF(points)
    # end def

# end class