### Python imports
import sys

### PyQt imports
from PyQt4.QtGui  import ( QApplication, QGraphicsItem, QGraphicsScene, QGraphicsView, QGraphicsSimpleTextItem,
                           QPainter, QColor, QPixmap, QPen, QDialog, QDoubleSpinBox, QPushButton, QFont,
                           QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QResizeEvent )
from PyQt4.QtCore import ( Qt, QPointF, QLineF, QRectF, QString, QRegExp, QFile, QTextStream, qWarning, QIODevice,
                           SIGNAL, SLOT, pyqtSlot, QSize )

### Global Variables
SCALE_X = 1.0; SCALE_Y = 1.0; PLOT_WIDTH = 800; PLOT_HEIGHT = 600; MIN_VALUE = 1.0; MAX_VALUE = 1.0

axisTypes = { QString('real')    : float,   QString('float')   : float,
              QString('int')     : int,     QString('integer') : int,
              QString('string')  : QString, QString('nominal') : QString }

def typeToSimpleString( t ):
    string = QString(str(type(t)))
    typePart = QRegExp('<type \'')
    classPart = QRegExp('<class \'')
    lastPart  = QRegExp('\'>')
    string.replace(typePart,'')
    string.replace(classPart,'')
    string.replace(lastPart,'')
    return string
#end def

def myMax( lst ):
    if len(lst) > 0:
        maximum = lst[0]
        for i in range( 1, len(lst) ):
            if lst[i] > maximum: maximum = lst[i]
        # end for
        return maximum
    # end if
    return None
# end def

def myMin( lst ):
    if len(lst) > 0:
        minimum = lst[0]
        for i in range( 1, len(lst) ):
            if lst[i] < minimum: minimum = lst[i]
            # end for
        return minimum
        # end if
    return None
# end def

def mapToPlot( point ):
    # map point to the range x = [0, 1] and y = [0, 1] and then point to the
    # screen space also need to invert the drawing for the Y
    global SCALE_X, SCALE_Y, PLOT_WIDTH, PLOT_HEIGHT
    return QPointF( point.x()*SCALE_X*PLOT_WIDTH, PLOT_HEIGHT - (point.y()*SCALE_Y*PLOT_HEIGHT)  )
# end def

def mapFromPlot( point ):
    # reverse of the mapping in mapToPlot()
    global SCALE_X, SCALE_Y, PLOT_WIDTH, PLOT_HEIGHT
    return QPointF( point.x()/(SCALE_X*PLOT_WIDTH), (PLOT_HEIGHT - point.y())/(SCALE_Y*PLOT_HEIGHT) )
# end def

def positionTextBelow(string, item, font, offset=0.0):
    position    = item.getBottom()
    label       = QGraphicsSimpleTextItem(string)
    label.setFont(font)
    labelBounds = label.boundingRect()
    label.translate( position.x() - (labelBounds.width()*0.5), position.y() + offset )
    return label
# end def

def positionTextAbove(string, item, font, offset=0.0):
    position    = item.getTop()
    label       = QGraphicsSimpleTextItem(string)
    label.setFont(font)
    labelBounds = label.boundingRect()
    label.translate( position.x() - (labelBounds.width()*0.5), position.y() - labelBounds.height() - offset )
    return label
# end def

class Axis:

    """
        Axis is a is the basic component of the parallel coordinate plot and
        can store three different types of data floating point, integer and nominal data
    """

    def __init__(self, label, type=float, values=None):

        self.__myLabel = label
        if values is None: self.__myValues = []
        else:              self.__myValues = values
        self.__myWords = []
        self.__myType = type

    # end def

    def getLabel(self):
        return self.__myLabel
    # end def

    def setLabel(self, label):
        self.__myLabel = label
    # end def

    def getType(self):
        return self.__myType
    # end def

    def append(self, item):
        if type(item) is self.__myType:
            self.__myValues.append(item)
            if self.__myType is QString and item not in self.__myWords:
                self.__myWords.append(item)
            # end if
        # end if
    # end def

    def max(self):
        return max(self.__myValues)
    # end def

    def min(self):
        return min(self.__myValues)
    # end def

    def maxNumerical(self):
        if self.__myType is QString:
            return len(self.__myWords)-1
        else:
            return max(self.__myValues)
        # end if
    # end def

    def minNumerical(self):
        if self.__myType is QString:
            return 0
        else:
            return min(self.__myValues)
        # end if
    # end def

    def index(self, item):
        if self.__myType is not QString:
            return self.__myValues.index(item)
        else:
            return self.__myWords.index(item)
        # end if
    # end def

    def getWordItem(self,item):
        return self.__myWords[item]
    # end def

    def __getitem__(self, item):
        return self.__myValues[item]
    # end def

    def __len__(self):
        return len(self.__myValues)
    # end def

    def __str__(self):
        return "%s, %s, %s" % (self.__myLabel, self.__myType, self.__myValues)
    # end def

    def __repr__(self):
        return "Axis('%s','%s', '%s')" % (self.__myLabel, self.__myType, self.__myValues)
    # end def

# end class

#noinspection PyOldStyleClasses
class AxisItem(QGraphicsItem):

    def __init__(self, bottom, top, thickness =3.0, parent=None):
        super(AxisItem,self).__init__(parent)
        self.__myBottom = mapToPlot( bottom )
        self.__myTop    = mapToPlot( top    )
        self.__myThickness = thickness
    # end def

    def boundingRect(self):
        return QRectF( 0, 0, 2, MAX_VALUE - MIN_VALUE )
    # end def

    def paint(self, painter, option, widget=None):
        painter.setBrush(Qt.NoBrush)
        painter.setPen( QPen(Qt.black, self.__myThickness) )
        axis = QLineF( self.__myBottom, self.__myTop )
        painter.drawLine( axis )
    # end def

    def getBottom(self):
        return self.__myBottom
    # end def

    def getTop(self):
        return self.__myTop
    # end def

# end class

#noinspection PyOldStyleClasses
class PointItem(QGraphicsItem):

    """
        Control Polygon item
    """

    def __init__(self, coordinates, colour=QColor(255, 0, 0, 50), thickness=1.0, parent=None):
        super(PointItem, self).__init__(parent)
        self.__myCoordinates = coordinates
        self.__myDrawColour  = colour
        self.__myThickness   = thickness
    # end def

    def boundingRect(self):
        return QRectF(0,0,PLOT_WIDTH,PLOT_HEIGHT)
    # end def

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen( QPen(self.__myDrawColour, self.__myThickness) )
        for i in range( len(self.__myCoordinates) - 1):
            painter.drawLine( self.__myCoordinates[i], self.__myCoordinates[i+1])
        # end for
    # end def

    def __getitem__(self, item):
        return self.__myCoordinates[item]
    # end def

# end class

#noinspection PyOldStyleClasses
class ParallelCoordinates(QGraphicsView):

    """
        Parallel coordinates object is a specialization of QGraphicsScene that is exclusively for drawing parallel
        coordinate plots
    """

    def __init__(self, title='Parallel Coordinates', opacity=50, parent=None):

        super(ParallelCoordinates, self).__init__(parent)

        self.__myAxes         = []
        self.__myMaxNumerical = []
        self.__myMinNumerical = []
        self.__myTitle   = title
        self.__myOpacity = opacity
        self.__myPolygonThickness = 1.0
        self.__myAxesThickness = 3.0

        theScene = QGraphicsScene( QRectF( 0, 0, PLOT_WIDTH, PLOT_HEIGHT) )

        # view set up
        self.setScene( theScene )
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setInteractive(True)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setWindowTitle(QString('Parallel Coordinates'))
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setMinimumSize( PLOT_WIDTH * 0.25, PLOT_HEIGHT * 0.25 )

    # end def

    ### public functions

    def addAxis(self, axis):
        self.__myAxes.append(axis)
        self.update()
    # end def

    def readSTFFile(self, filename):

        """
            This function takes a QString object as a file name and reads the data from and STF file into a parallel
            coordinates graphical object. Returns a boolean to indicate success or failure and the parallel coordinates
            object or None.
        """
        stfExt = QRegExp('*.stf')
        stfExt.setPatternSyntax(QRegExp.Wildcard)

        if not stfExt.exactMatch(filename):
            qWarning( '%s is not an stf file... could not open.' % filename )
            return False
        # end if

        input = QFile(filename)
        if not input.open(QIODevice.ReadOnly | QIODevice.Text):
            qWarning('failed to open file... %s' % filename)
            return False
        # end if

        print('reading data from %s' % filename)

        data = QTextStream(input)

        while not data.atEnd():
            line = data.readLine()                  # 1. grab a line from the file
            if line.startsWith('#'):                # 2. line is a comment, ignore it
                continue
            elif QRegExp("\\d+").exactMatch(line):  # 3. header information, process it
                N, success  = line.toInt()
                print('number of columns - %d' % N )
                for xPosition in range(N):
                    header = data.readLine().split(QRegExp('\\s+'))     # split the line on white spaces
                    if len(header) != 2:
                        qWarning('failed to read header info... terminated file load')
                        return False
                    else:
                        label = header[0]
                        type  = axisTypes[ header[1].toLower() ]
                        self.__myAxes.append( Axis(label, type) )
                    # end if
                # end for
            else:                                    # 4. it has to be a row data set
                row = line.split(QRegExp('\\s+'))          # split the line on white spaces
                if len(row) != len(self.__myAxes):
                    qWarning('row mismatch while reading data... terminated file load')
                    return False
                    # end if
                for i in range( len(row) ):
                    convertToType = self.__myAxes[i].getType()
                    if convertToType is float:
                        floatValue, success = row[i].toFloat()
                        self.__myAxes[i].append( floatValue )
                    elif convertToType is int:
                        intValue, success = row[i].toInt()
                        self.__myAxes[i].append( intValue )
                    else:
                        self.__myAxes[i].append( row[i] )
                    # end if
                # end for
            # finished reading data

        input.close()

        self.update()

        return True

    # end def

    def writeSTFFile(self, filename):

        """
            This function takes a QString object as a file name and reads the data from and STF file into a parallel
            coordinates graphical object. Returns a boolean to indicate success or failure and the parallel coordinates
            object or None.
        """
        stfExt = QRegExp('*.stf')
        stfExt.setPatternSyntax(QRegExp.Wildcard)

        if not stfExt.exactMatch(filename):
            qWarning( '%s is not an stf file... could not open.' % filename )
            return False
        # end if

        output = QFile(filename)
        if not output.open(QIODevice.ReadWrite | QIODevice.Text):
            qWarning('failed to open file... %s' % filename)
            return False
        # end if

        print('writing data to %s' % filename) # make sure you use the stf format

        output.writeData( '%d\n' % len(self.__myAxes) ) # first write the number of columns

        for axis in self.__myAxes:  # second write labels and types
            output.writeData( '%s %s\n' % ( axis.getLabel(), typeToSimpleString( str(axis.getType()) ) ) )
        # end for
        N = len(self.__myAxes[0])
        for i in range(N):
            for x, axis in enumerate(self.__myAxes): # third write out all axis data
                if x < N-1 :
                    output.writeData( '%s ' % axis[i] )
                else:
                    output.writeData( '%s' % axis[i] )
                # end if
            # end for
            output.writeData('\n')
        # end for

        output.close()

        return True

    # end def

    ### Qt reimplemented functions

    def update(self):

        # update object data
        self.__myMaxNumerical = [ self.__myAxes[i].maxNumerical() for i in range( len(self.__myAxes) ) ]
        self.__myMinNumerical = [ self.__myAxes[i].minNumerical() for i in range( len(self.__myAxes) ) ]

        # update global data
        global MAX_VALUE, MIN_VALUE

        MAX_VALUE = myMax( self.__myMaxNumerical )
        MIN_VALUE = myMin( self.__myMinNumerical )
    # end def

    def resizeEvent(self, event):
        ### make sure to reference the global variables for the plot
        global SCALE_X, SCALE_Y, PLOT_WIDTH, PLOT_HEIGHT

        # clear the scene before drawing
        self.scene().clear()

        w = event.size().width()
        h = event.size().height()

        SCALE_X = 1.0 / float( len(self.__myAxes)-1 )
        SCALE_Y = 1.0 #/ (MAX_VALUE - MIN_VALUE)

        PLOT_WIDTH  = w - (0.08 * w)
        PLOT_HEIGHT = h - (0.15 * h)

        self.scene().setSceneRect( QRectF(0.0,0.0,PLOT_WIDTH,PLOT_HEIGHT) )

        #titleItem = QGraphicsSimpleTextItem( self.__myTitle )
        #bt = titleItem.boundingRect()
        #bounds = self.sceneRect()
        #bx = bounds.x(); by = bounds.y(); bw = bounds.width()
        #titleItem.translate( bx + (bw - bt.width())*0.5, by - bt.height() - 20 )
        #self.scene().addItem(titleItem)

        textSize   = int(11 + PLOT_HEIGHT * PLOT_WIDTH * 0.000005)
        textWeight = int(50 + PLOT_HEIGHT * PLOT_WIDTH * 0.00005)
        font = QFont("Arial", textSize, textWeight)

        # draw parallel coordinates axes, labels, minimum and maximum values
        for x, axis in enumerate( self.__myAxes ):
            # axisItem  = AxisItem( QPointF(x,MIN_VALUE), QPointF(x,MAX_VALUE) )
            axisItem  = AxisItem( QPointF(x,0.0), QPointF(x, 1.0), self.__myAxesThickness) # normalized axis
            labelItem = positionTextBelow( axis.getLabel(), axisItem, font, 20 )

            minLabel = QString(''); maxLabel = QString('')

            if axis.getType() is float:
                minLabel = QString('%.1f' % self.__myMinNumerical[x])
            elif axis.getType() is int:
                minLabel = QString('%d' % self.__myMinNumerical[x] )
            else:
                minLabel = axis.getWordItem(self.__myMinNumerical[x])
            # end if

            if axis.getType() is float:
                maxLabel = QString('%.1f' % self.__myMaxNumerical[x])
            elif axis.getType() is int:
                maxLabel = QString('%d' % self.__myMaxNumerical[x] )
            else:
                maxLabel = axis.getWordItem(self.__myMaxNumerical[x])
            # end if
            
            minItem   = positionTextBelow( minLabel, axisItem, font )
            maxItem   = positionTextAbove( maxLabel, axisItem, font )
            self.scene().addItem( axisItem  )
            self.scene().addItem( labelItem )
            self.scene().addItem( minItem   )
            self.scene().addItem( maxItem   )
        # end for

        # draw control polygons that represent multidimensional points
        numberOfPoints = len( self.__myAxes[0])
        for p in range(numberOfPoints):
            coordinates = []
            # gather all the coordinates that represent the control polygon of the higher dimensional point
            for x, axis in enumerate( self.__myAxes ):
                norm  = (self.__myMaxNumerical[x] - self.__myMinNumerical[x])
                scale = 1.0
                if norm > 0.0 : scale = 1.0 / norm
                if axis.getType() is not QString:
                    value = ( axis[p] - self.__myMinNumerical[x] ) * scale
                    coordinates.append( mapToPlot( QPointF(x, value) ) )
                else:
                    value = float( axis.index(axis[p]) - self.__myMinNumerical[x] ) * scale
                    coordinates.append( mapToPlot( QPointF(x, value) ) )
                # end if

            # end for
            self.scene().addItem( PointItem(coordinates, QColor(255,0,0,self.__myOpacity), self.__myPolygonThickness) )
        # end for

        #self.update()
    # end def

    @pyqtSlot(float)
    def polygonOpacityChanged(self, value):
        self.__myOpacity = value
        self.resizeEvent( QResizeEvent( self.size(), self.size() )  )
    # end def

    @pyqtSlot(float)
    def polygonThicknessChanged(self, value):
        self.__myPolygonThickness = value
        self.resizeEvent( QResizeEvent( self.size(), self.size() ) )
    # end def

    @pyqtSlot(float)
    def axesThicknessChanged(self, value):
        self.__myAxesThickness = value
        self.resizeEvent( QResizeEvent( self.size(), self.size() ) )
    # end def

    ### overloaded member functions

    def __getitem__(self, item):
        return self.__myAxes[item]
    # end def

    def __len__(self):
        return len(self.__myAxes)
    # end def

    def __str__(self):
        str = ''
        for i in range( len(self.__myAxes) ):
            str += ( '%s\n' % self.__myAxes[i] )
        # end for
        return str
    # end def

    def __repr__(self):
        return "ParallelCoordinates('Axes = %d','Points = %d')" % (len(self.__myAxes), len(self.__myNDPoints))
    # end def

# class ParallelCoordinates


#noinspection PyOldStyleClasses
class ParallelCoordinateDialog(QDialog):
    """
        Class that holds a Parallel Coordinates display and attached functionality to it.

        Functionality and features are attached to the Parallel Coordinates display via
        QPushButtons and QDoubleSpinBoxes
    """

    def __init__(self, parent=None):
        super(ParallelCoordinateDialog,self).__init__(parent)
        testFile = QString('averageSperms.stf')

        self.__myParallelCoordinates = ParallelCoordinates( testFile, 50, self)
        success = self.__myParallelCoordinates.readSTFFile( testFile )

        if success:
            print('loaded test file....')
        else:
            qWarning('failed to read test file - %s ...' % testFile)

        viewLayout = QVBoxLayout()
        viewLayout.addWidget(self.__myParallelCoordinates)

        # now that we have a nice dialog going on the
        controlLayout = QHBoxLayout()

        capture          = QPushButton('Cheese!!!')
        polygonOpacity   = QDoubleSpinBox()
        polygonThickness = QDoubleSpinBox()
        axisThickness    = QDoubleSpinBox()

        polygonOpacity.setMinimum  (0.0); polygonOpacity.setMaximum  (255.0); polygonOpacity.setValue(50.0)
        polygonThickness.setMinimum(1.0); polygonThickness.setMaximum(10.0)
        axisThickness.setMinimum(3.0);    axisThickness.setMaximum (10.0)

        self.connect( capture, SIGNAL("clicked()"), self, SLOT("captureScene()") )

        self.connect( polygonOpacity,      SIGNAL("valueChanged(double)"),
                      self.__myParallelCoordinates, SLOT  ("polygonOpacityChanged(double)") )
        self.connect( polygonThickness,    SIGNAL("valueChanged(double)"),
                      self.__myParallelCoordinates, SLOT  ("polygonThicknessChanged(double)") )
        self.connect( axisThickness,       SIGNAL("valueChanged(double)"),
                      self.__myParallelCoordinates, SLOT  ("axesThicknessChanged(double)") )

        controlLayout.addWidget(capture)

        controlLayout.addWidget( QLabel('Polygon Opacity') )
        controlLayout.addWidget( polygonOpacity )

        controlLayout.addWidget( QLabel('Polygon Thickness') )
        controlLayout.addWidget( polygonThickness )

        controlLayout.addWidget( QLabel('Axes Thickness') )
        controlLayout.addWidget( axisThickness )

        viewLayout.addLayout( controlLayout )

        self.setLayout(viewLayout)

    # end def

    @staticmethod
    def imageFormats():
        return "*.png *.bmp *.jpg *.jpeg *.ppm"
    # end def

    @pyqtSlot()
    def captureScene(self):
        oFile = QString("")
        oFile = QFileDialog.getSaveFileName( None, "Save Screen Capture",
            oFile, "Image Formats(%s)" % self.imageFormats() )

        if oFile.isEmpty() : return False

        oldSize = self.size()
        tempSize = QSize( oldSize.width()*1.5, oldSize.height()*1.5 )

        self.resize( tempSize )


        image = QPixmap.grabWidget(self.__myParallelCoordinates)

        if oFile.endsWith(".png"):
            image.save(oFile, "PNG")
        elif oFile.endsWith(".bmp"):
            image.save(oFile, "BMP")
        elif oFile.endsWith(".jpg"):
            image.save(oFile, "JPG")
        elif oFile.endsWith(".jpeg"):
            image.save(oFile, "JPEG")
        elif oFile.endsWith(".ppm"):
            image.save(oFile, "PPM")
        else:
            # if a valid extension hasn't been given be nice and save it as a PNG file
            oFile.append(".png")
            image.save(oFile, "PNG")
        # end if

        self.resize( oldSize )
        return True
    # end def

# end class

### Test suit for parallel coordinates

def testParallelCoordinates():

    app = QApplication(sys.argv)
    app.setApplicationName('Parallel Coordinates')

    pcd = ParallelCoordinateDialog()
    pcd.show()
    sys.exit(app.exec_())

# function testParallelCoordinates

if __name__ == '__main__':
    testParallelCoordinates()
# end unit testing
