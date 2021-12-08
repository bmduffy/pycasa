from PyQt4.QtGui import (QVector2D, QPainter, QGraphicsItem, QGraphicsScene, QGraphicsView,
                         QPen, QBrush, QColor, QPolygonF, QGraphicsLineItem, QGraphicsRectItem,
                         QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsSimpleTextItem, QFont)

from PyQt4.QtCore import (Qt, QPoint, QPointF, QLineF, QRectF, qWarning, pyqtSlot)

from glyphdesigns import (timeColourMap)

from math import (degrees, atan2)
from computation import (polarAngle)
from geometry import (QtHull, square)

from mygraphicsitems import (PolyLine)

import glyphdesigns as designs

from pycasadata import(START_POSITION, END_POSITION)


#noinspection PyOldStyleClasses
class GlyphItem(QGraphicsItem):

    def __init__(self, CBase, CScale, HScale, TScale,
                 position, parameters, drawFunc, thickness, summary, parent=None):

        super(GlyphItem, self).__init__(parent)

        self.__drawFunc = drawFunc
        self.__myThickness = thickness

        self.setPos(position)

        self.__CBase = CBase
        self.__CScale = CScale
        self.__HScale = HScale
        self.__TScale = TScale
        self.__summary = summary

        if parameters is not None:
            self.__headUncertainty = parameters[0]
            self.__flagellumUncertainty = parameters[1]
            self.__vcl = parameters[2]
            self.__vap = parameters[3]
            self.__vsl = parameters[4]
            self.__bcf = parameters[5]
            self.__alh = parameters[6]
            self.__mad = parameters[7]
            self.__angle = parameters[8]
            self.__length = parameters[9]
            self.__width = parameters[10]
            self.__arcLength = parameters[11]
            self.__changeInAngle = parameters[12]
            self.__torque = parameters[13]
            self.__asymmetry = parameters[14]

        self.__size = ((self.__CBase + self.__vcl) / self.__CScale) * 1.2

    def boundingRect(self):
        return square(self.__size)

    def paint(self, painter, option, widget=None):

        self.__drawFunc(painter, self.__CBase, self.__CScale, self.__HScale, self.__TScale,
                        self.__headUncertainty, self.__flagellumUncertainty,
                        self.__angle,    self.__width,    self.__length,
                        self.__vcl,      self.__vap,      self.__vsl,       self.__bcf,
                        self.__alh,      self.__mad,      self.__arcLength, self.__changeInAngle,
                        self.__torque,   self.__asymmetry, self.__myThickness, self.__summary)

    def setDrawFunction(self, function):
        self.__drawFunc = function

    def setPosition(self, position):
        if isinstance(position, QPointF):
            self.setPos(position)
        else:
            raise TypeError

    def setSize(self, size):
        self.__size = size

    def setRotation(self, vector):
        """
            This function allows you to orient the glyph in the correct direction
        """
        if isinstance(vector, QVector2D):
            theta = degrees(atan2(vector.y(), vector.x()))
            self.rotate(theta)
        else:
            raise ValueError


#noinspection PyOldStyleClasses
class GridItem(QGraphicsItem):

    def __init__(self, width, height, pixelScale, ticks=12, gridOn=True, parent=None):

        super(GridItem, self).__init__(parent)

        self.setZValue(-10.0)

        self.__myGridOn = gridOn

        self.__myPixelScale = pixelScale
        self.__myWidth = width
        self.__myHeight = height
        self.__myXTicks = 1.0
        self.__myYTicks = 1.0
        self.__myDX = 1.0
        self.__myDY = 1.0

        if width < height:
            ratio = height / width
            self.__myXTicks = int(ticks)
            self.__myYTicks = int(ticks * ratio)
        else:
            ratio = width / height
            self.__myXTicks = int(ticks * ratio)
            self.__myYTicks = int(ticks)

        self.__myDX = width / self.__myXTicks
        self.__myDY = height / self.__myYTicks

        self.__annotate()

    def boundingRect(self):
        return QRectF(0.0, 0.0,  self.__myWidth, self.__myHeight)

    def paint(self, painter, option, widget=None):

        if self.__myGridOn is True:

            painter.setBrush(Qt.NoBrush)
            # set the grid to a transparent light grey
            painter.setPen(QPen(QColor(50, 50, 50, 100), 0.5, Qt.DashLine))

            for x in range(0, self.__myXTicks + 1):
                xPos = x * self.__myDX
                painter.drawLine(QLineF(QPointF(xPos, -10.0), QPointF(xPos, self.__myHeight)))

            for y in range(0, self.__myYTicks + 1):
                yPos = y * self.__myDY
                painter.drawLine(QLineF(QPointF(-10.0, yPos), QPointF(self.__myWidth, yPos)))

    def __annotate(self):

        brush = QBrush(QColor(50, 50, 50, 255))
        font = QFont('Helvetica [Cronyx]', 8)

        for x in range(0, self.__myXTicks + 1):
            xPos = x * self.__myDX
            text = QGraphicsSimpleTextItem('%.1f' % (xPos * self.__myPixelScale), self)
            text.setPen(QPen(Qt.NoPen))
            text.setBrush(brush)
            text.setFont(font)
            textHeight = text.boundingRect().height()
            text.translate(xPos - (textHeight * 0.5), -15.0)
            text.rotate(-60.0)

        for y in range(0, self.__myYTicks + 1):
            yPos = y * self.__myDY
            text = QGraphicsSimpleTextItem('%.1f' % (yPos * self.__myPixelScale), self)
            text.setPen(QPen(Qt.NoPen))
            text.setBrush(brush)
            text.setFont(font)
            textWidth = text.boundingRect().width()
            textHeight = text.boundingRect().height()
            text.translate(-10.0 - textWidth, yPos - (textHeight * 0.5))

    def toggle(self):
        state = (not self.__myGridOn)
        self.__myGridOn = state
        self.update()
        return state

    def setState(self, state):
        self.__myGridOn = state
        self.update()

    def getState(self):
        return self.__myGridOn


#noinspection PyOldStyleClasses
class ColourMapItem(QGraphicsItem):

    def __init__(self, width, height, nFrames, fps, ticks=10, parent=None):

        super(ColourMapItem, self).__init__(parent)

        self.__myWidth = width
        self.__myHeight = height
        self.__myNFrames = nFrames
        self.__myFPS = fps
        self.__myTicks = ticks
        self.__myDT = 1.0

        # draw the colour map horizontally
        if self.__myWidth > self.__myHeight:
            self.__myDT = self.__myWidth / self.__myTicks
        else:
            self.__myDT = self.__myHeight / self.__myTicks

        self.__annotate()

    def boundingRect(self):
        return QRectF(0, 0, self.__myWidth, self.__myHeight)

    def paint(self, painter, option, widget=None):

        painter.drawRect(self.boundingRect())

        # draw the colour map horizontally
        if self.__myWidth > self.__myHeight:

            dx = self.__myWidth / (self.__myNFrames - 1)
            x = 0.0
            painter.setPen(QPen(Qt.NoPen))

            # draw the bars in the colour map
            for i in range(self.__myNFrames):

                value = float(i) / float(self.__myNFrames)
                red = timeColourMap(value)[0]
                green = timeColourMap(value)[1]
                blue = timeColourMap(value)[2]

                drawColour = QColor.fromRgbF(red, green, blue, 1.0)

                painter.setBrush(QBrush(drawColour))
                painter.drawRect(QRectF(x, 0, dx * 1.1, self.__myHeight))
                x += dx

            painter.setPen(QPen(Qt.black))
            painter.setBrush(QBrush(Qt.NoBrush))

            # draw the ticks
            for t in range(0, self.__myTicks + 1):
                tPos = t * self.__myDT
                painter.drawLine(QLineF(QPointF(tPos - dx * 0.5, 0), QPointF(tPos - dx * 0.5, self.__myHeight + 5.0)))

        else:

            # the colour map has to be vertical
            dy = self.__myHeight / (self.__myNFrames - 1)
            y = self.__myHeight - 1

            painter.setPen(QPen(Qt.NoPen))

            # draw the bars in the colour map
            for i in range(self.__myNFrames):
                value = float(i) / float(self.__myNFrames)
                red = timeColourMap(value)[0]
                green = timeColourMap(value)[1]
                blue = timeColourMap(value)[2]
                drawColour = QColor.fromRgbF(red, green, blue, 1.0)
                painter.setBrush(QBrush(drawColour))
                painter.drawRect(QRectF(0, y, self.__myWidth, dy * 1.5))
                y -= dy

            # draw the tick marks

            painter.setPen(QPen(Qt.black))
            painter.setBrush(QBrush(Qt.NoBrush))

            # draw the ticks
            for t in range(self.__myTicks, -1, -1):

                tPos = t * self.__myDT
                painter.drawLine(QLineF(QPointF(0, tPos + dy * 0.5), QPointF(self.__myWidth + 5.0, tPos + dy * 0.5)))

    def __annotate(self):

        dt = (self.__myNFrames - 1.0) / (self.__myTicks * self.__myFPS)

        # draw the colour map horizontally
        if self.__myWidth > self.__myHeight:

            dx = self.__myWidth / self.__myNFrames
            for t in range(0, self.__myTicks + 1):
                tPos = t * self.__myDT
                string = '%.1f' % (t * dt)
                text = QGraphicsSimpleTextItem(string, self)
                text.translate(tPos - dx * 0.5, self.__myHeight + 6.0)
                text.rotate(-60.0)

        else:

            # the colour map has to be vertical
            for t in range(self.__myTicks, -1, -1):
                tPos = t * self.__myDT
                string = '%.1f' % ((self.__myTicks - t) * dt)
                text = QGraphicsSimpleTextItem(string, self)
                textOffset = text.boundingRect().height() * 0.5
                text.translate(self.__myWidth + 6.0, tPos - textOffset)


#noinspection PyOldStyleClasses
class GlyphScene(QGraphicsScene):

    DEFAULT_FRAME_WIDTH = 640
    DEFAULT_FRAME_HEIGHT = 480
    DEFAULT_FPS = 15.0
    ALIGN_BOTTOM_CENTER = 0
    ALIGN_BOTTOM_LEFT = 1
    ALIGN_BOTTOM_RIGHT = 2
    ALIGN_TOP_CENTER = 3
    ALIGN_TOP_LEFT = 4
    ALIGN_TOP_RIGHT = 5
    CENTER_IN_SCENE = 6
    ALIGN_RIGHT_CENTER = 7

    def __init__(self, parent=None):

        super(GlyphScene, self).__init__(parent)

        self.updateFrame(self.DEFAULT_FRAME_WIDTH, self.DEFAULT_FRAME_HEIGHT)

    def updateFrame(self, frameWidth, frameHeight, showFrame=True):

        # clear the scene
        self.clear()

        # 1. __myWorkSpaceItem is where we will render all the auxiliary
        #    information such as text and colour bars
        workSpace = QRectF(0, 0, frameWidth * 1.2, frameHeight * 1.2)
        self.__myWorkSpaceItem = QGraphicsRectItem(workSpace, None, self)
        self.__myWorkSpaceItem.setPen(QPen(Qt.NoPen))

        #   2. __myFrameItem is where the glyphs and grid and that are rendered

        frame = QRectF(0, 0, frameWidth, frameHeight)
        self.__myFrameItem = QGraphicsRectItem(frame, self.__myWorkSpaceItem, self)

        if not showFrame:
            self.__myFrameItem.setPen(QPen(Qt.NoPen))

        #   3. translate the __myFrame so that it is centered in the __myWorkSpace
        dx = (workSpace.width() - frame.width()) * 0.5
        dy = (workSpace.height() - frame.height()) * 0.5
        self.__myFrameItem.translate(dx, dy)
        self.__myFrameItem.setZValue(-10)

        # 4. set the the viewing rectangle of the scene
        self.setSceneRect(self.__myWorkSpaceItem.rect())

    def getFrameWidth(self):
        return self.__myFrameItem.boundingRect().width()

    def getFrameHeight(self):
        return self.__myFrameItem.boundingRect().height()

    def getWorkSpace(self):
        return self.__myWorkSpaceItem

    def getWorkSpaceBoundingRect(self):
        return self.__myWorkSpaceItem.boundingRect()

    def getWorkSpaceWidth(self):
        return self.__myWorkSpaceItem.boundingRect().width()

    def getWorkSpaceHeight(self):
        return self.__myWorkSpaceItem.boundingRect().height()

    def panScene(self, dx, dy):
        self.__myWorkSpaceItem.translate(dx, dy)

    ### I need to implement my own functions to make sure that I add to the frame and the workspace
    def addItemToFrame(self, item):
        if isinstance(item, QGraphicsItem) and item is not self.__myWorkSpaceItem and item is not self.__myFrameItem:
            item.setParentItem(self.__myFrameItem)
        else:
            qWarning('in GlyphScene.addItemToFrame( item )... item is not of type QGraphicsItem... omitting')

    def addItemToWorkSpace(self, item, justification, offset=0.0):
        if isinstance(item, QGraphicsItem) and item is not self.__myWorkSpaceItem and item is not self.__myFrameItem:
            item.setParentItem(self.__myWorkSpaceItem)
            self.__positionItem(item, justification, offset)
        else:
            qWarning('in GlyphScene.addItemToWorkSpace( item )... item is not of type QGraphicsItem... omitting')

    def __positionItem(self, item, justification, offset=0.0):
        bFrame = self.__myFrameItem.boundingRect()
        bWorkSpace = self.__myWorkSpaceItem.boundingRect()
        bItem = item.boundingRect()
        center = bFrame.center()
        xOffset = bFrame.width() * 0.5
        yOffset = bFrame.height() * 0.5
        dx = (bWorkSpace.width() - bFrame.width()) * 0.5
        dy = (bWorkSpace.height() - bFrame.height()) * 0.5

        if justification is self.ALIGN_BOTTOM_CENTER:
            item.translate(center.x() - bItem.width() * 0.5 + dx, center.y() + yOffset + dy + offset)

        elif justification is self.ALIGN_BOTTOM_LEFT:
            item.translate((center.x() - xOffset) + dx, center.y() + yOffset + dy + offset)

        elif justification is self.ALIGN_BOTTOM_RIGHT:
            item.translate(center.x() + xOffset + dx - bItem.width(), center.y() + yOffset + dy + offset)

        elif justification is self.ALIGN_TOP_CENTER:
            item.translate(center.x() - bItem.width() * 0.5 + dx, center.y() - yOffset + dy + offset - bItem.height())

        elif justification is self.ALIGN_TOP_LEFT:
            item.translate((center.x() - xOffset) + dx, center.y() - yOffset + dy + offset - bItem.height())

        elif justification is self.ALIGN_TOP_RIGHT:
            item.translate(center.x() + xOffset + dx - bItem.width(),
                           center.y() - yOffset + dy + offset - bItem.height())

        elif justification is self.CENTER_IN_SCENE:
            item.translate(center.x() - bItem.width() * 0.5 + dx, center.y() - bItem.height() * 0.5 + dy)

        elif justification is self.ALIGN_RIGHT_CENTER:
            item.translate(center.x() + xOffset + dx + offset, center.y() - bItem.height() * 0.5 + dy)

        else:
            qWarning('in GlyphScene.__positionItem()... justification wrong...')


#noinspection PyOldStyleClasses
class GlyphView(QGraphicsView):

    GLYPH_VIEW = 0
    SPERM_VIEW = 1
    PATH_VIEW = 2
    SUMMARY_VIEW = 3

    def __init__(self, spermContainer, glyphControlDialog=None, parent=None):

        super(GlyphView, self).__init__(parent)

        self.__mySpermContainer = spermContainer
        self.__myGridItem = None

        self.__myDisplaySettings = glyphControlDialog

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setInteractive(True)

        self.__myPanFrom = QPoint(0, 0)
        self.__mySceneScale = 1.0
        self.__myViewMode = self.GLYPH_VIEW

        theScene = GlyphScene(self)

        self.setScene(theScene)
        self.resize(theScene.width() * 1.01, theScene.height() * 1.01)
        self.setMinimumSize(theScene.width() * 1.01, theScene.height() * 1.01)

        self.setCursor(Qt.OpenHandCursor)

    def update(self):

        fBox = self.scene().getWorkSpace().mapToScene(QPointF(0.0, 0.0))

        if self.__mySpermContainer.isEmpty():

            frameWidth = self.scene().getFrameWidth()
            frameHeight = self.scene().getFrameHeight()
            pixelScale = 3.0

            self.scene().updateFrame(frameWidth, frameHeight)

            label = QGraphicsSimpleTextItem('Resolution [ N/A x N/A ]  FPS - N/A  Frames - N/A ~ N\A secs')
            self.scene().addItemToWorkSpace(label, GlyphScene.ALIGN_BOTTOM_RIGHT)
            self.scene().addItemToWorkSpace(QGraphicsSimpleTextItem('Filename : N/A'), GlyphScene.ALIGN_BOTTOM_LEFT)
            self.__myGridItem = GridItem(frameWidth, frameHeight, pixelScale)
            self.scene().addItemToWorkSpace(self.__myGridItem, GlyphScene.CENTER_IN_SCENE)

        else:

            self.scene().updateFrame(self.__mySpermContainer.getFrameWidth(), self.__mySpermContainer.getFrameHeight())

            fileName = self.__mySpermContainer.getFilename()
            frameWidth = self.scene().getFrameWidth()
            frameHeight = self.scene().getFrameHeight()
            fps = self.__mySpermContainer.getFPS()
            nFrames = self.__mySpermContainer.getNFrames()
            pixelScale = self.__mySpermContainer.getPixelSize()
            seconds = self.__mySpermContainer.getNFrames() / self.__mySpermContainer.getFPS()

            fileName = QGraphicsSimpleTextItem('Filename : %s' % fileName)

            fileSpec = QGraphicsSimpleTextItem('Resolution [ %d  x %d ]  FPS - %.2f  Frames - %d ~ %.2f secs'
                                               % (frameWidth, frameHeight, fps, nFrames, seconds))

            self.scene().addItemToWorkSpace(fileSpec, GlyphScene.ALIGN_BOTTOM_RIGHT)
            self.scene().addItemToWorkSpace(fileName, GlyphScene.ALIGN_BOTTOM_LEFT)

            gridState = self.__myGridItem.getState()
            self.__myGridItem = GridItem(frameWidth, frameHeight, pixelScale)

            # keep the grid with a consistent state
            self.__myGridItem.setState(gridState)

            if self.__myViewMode is self. GLYPH_VIEW:
                self.scene().addItemToWorkSpace(self.__myGridItem, GlyphScene.CENTER_IN_SCENE)
                self.scene().addItemToWorkSpace(ColourMapItem(20, frameHeight, nFrames, fps),
                                                GlyphScene.ALIGN_RIGHT_CENTER, 5.0)
                self.__drawGlyphs()

            elif self.__myViewMode is self.PATH_VIEW:
                self.scene().addItemToWorkSpace(self.__myGridItem, GlyphScene.CENTER_IN_SCENE)
                self.__drawPath()

            elif self.__myViewMode is self.SPERM_VIEW:
                self.scene().addItemToWorkSpace(self.__myGridItem, GlyphScene.CENTER_IN_SCENE)
                self.__drawSperm()

            elif self.__myViewMode is self.SUMMARY_VIEW:
                self.__drawSummaryGlyph()

            else:
                qWarning('unknown view mode....')

        if self.__myPanFrom != QPoint(0, 0):
            self.scene().panScene(fBox.x(), fBox.y())

    def toggleGrid(self):

        if self.__myGridItem is not None:
            return self.__myGridItem.toggle()

    @pyqtSlot(float)
    def cBaseChanged(self, CBase):
        self.__myCBase = CBase
        self.update()

    @pyqtSlot(float)
    def cScaleChanged(self, CScale):
        self.__myCScale = CScale
        self.update()

    @pyqtSlot(float)
    def hScaleChanged(self, HScale):
        self.__myHScale = HScale
        self.update()

    @pyqtSlot(float)
    def tScaleChanged(self, TScale):
        self.__myTScale = TScale
        self.update()

    @pyqtSlot(int)
    def designChanged(self, design):
        if design is designs.GLYPH_DESIGN:
            self.__drawFunction = designs.drawGlyphDesign

        elif design is designs.BIRMINGHAM_DESIGN:
            self.__drawFunction = designs.drawBirminghamDesign

        elif design is designs.CHEN_DESIGN:
            self.__drawFunction = designs.drawChenDesign

        elif design is designs.CHEN_ALT_DESIGN:
            self.__drawFunction = designs.drawChenAltDesign

        self.update()

    @pyqtSlot(int)
    def positionChanged(self, strategy):
        self.__myPositionStrategy = strategy
        self.update()

    @pyqtSlot(int)
    def toggleColourPath(self, state):
        self.__myColourPathOn = state
        self.update()

    @pyqtSlot(int)
    def toggleSegmentsOn(self, state):
        self.__mySegmentsOn = state
        self.update()

    @pyqtSlot(int)
    def thicknessChanged(self, thickness):
        self.__thickness = thickness
        self.update()

    def getGlyphScaleParameters(self):
        return self.__myCBase, self.__myCScale

    def clear(self):
        self.scene().clear()

    def setViewMode(self, viewMode):
        self.__myViewMode = viewMode
        self.update()

    def wheelEvent(self, event):

        # How fast we zoom
        scaleFactor = 1.15

        if event.delta() > 0:
            # zoom in
            self.scale(scaleFactor, scaleFactor)
        else:
            # zooming out
            self.scale(1.0 / scaleFactor, 1.0 / scaleFactor)

    def mousePressEvent(self, event):
        self.__myPanFrom = event.pos()
        self.setCursor(Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)

    def mouseMoveEvent(self, event):
        if not self.__myPanFrom.isNull():
            delta = self.mapToScene(event.pos()) - self.mapToScene(self.__myPanFrom)
            self.__myPanFrom = event.pos()
            self.scene().panScene(delta.x(), delta.y())

    ### private member functions of the class

    def __drawGlyphs(self):

        CBase = self.__myDisplaySettings.getCurrentCBase()
        CScale = self.__myDisplaySettings.getCurrentCScale()
        TScale = self.__myDisplaySettings.getCurrentTScale()
        HScale = self.__myDisplaySettings.getCurrentHScale()
        drawFunc = self.__myDisplaySettings.getCurrentDesign()
        strategy = self.__myDisplaySettings.getCurrentPositioning()
        colourPath = self.__myDisplaySettings.getCurrentPathState()
        segmentsOn = self.__myDisplaySettings.areSegmentsOn()
        thickness = self.__myDisplaySettings.getCurrentThickness()

        print "number of sperm to visualize -- %d" % (len(self.__mySpermContainer))
        for (i, sperm) in enumerate(self.__mySpermContainer):

            numberOfGlyphs = sperm.getNumberOfGlyphs()
            print "sperm %d : number of glyphs -- %d" % (i, numberOfGlyphs)

            positions = sperm.getCentroids(0, len(sperm))

            for index in range(len(positions) - 1):

                drawColour = QColor(0, 206, 209)

                if colourPath:
                    value = float(index) / float(self.__mySpermContainer.getNFrames())
                    red = timeColourMap(value)[0]
                    green = timeColourMap(value)[1]
                    blue = timeColourMap(value)[2]
                    drawColour = QColor.fromRgbF(red, green, blue, 1.0)

                pen = QPen(QBrush(drawColour), 2.0)
                line = QGraphicsLineItem(QLineF(positions[index], positions[index + 1]))
                line.setPen(pen)
                self.scene().addItemToFrame(line)

            if segmentsOn:

                starts = sperm.getPositions(START_POSITION)
                ends = sperm.getPositions(END_POSITION)

                pen = QPen(QBrush(Qt.red), 2.0)

                ellipse = QGraphicsEllipseItem(QRectF(starts[0].x() - 2, starts[0].y() - 2, 4, 4))
                ellipse.setPen(Qt.red)
                ellipse.setBrush(QBrush(Qt.red))

                self.scene().addItemToFrame(ellipse)
                for index in range(len(starts)):
                    line = QGraphicsLineItem(QLineF(starts[index], ends[index]))
                    line.setPen(pen)
                    self.scene().addItemToFrame(line)
                    ellipse = QGraphicsEllipseItem(QRectF(ends[index].x() - 2, ends[index].y() - 2, 4, 4))
                    ellipse.setPen(Qt.red)
                    ellipse.setBrush(QBrush(Qt.red))
                    self.scene().addItemToFrame(ellipse)

            glyphPositions = sperm.getPositions(strategy)
            glyphDirections = sperm.getDirections(strategy)

            for index in range(numberOfGlyphs):
                print 'drawing glyphs'
                glyph = GlyphItem(CBase, CScale, HScale, TScale,
                                  glyphPositions[index], sperm.getParameters(index), drawFunc,
                                  thickness, False)
                # start from the x-axis
                glyph.rotate(90.0)
                orientAngle = degrees(polarAngle(glyphDirections[index]))
                glyph.rotate(orientAngle)
                self.scene().addItemToFrame(glyph)

        def __drawSummaryGlyph(self):
            """
                Draw a summary glyph of the sperm tract.
            """

            CBase = self.__myDisplaySettings.getCurrentCBase()
            CScale = self.__myDisplaySettings.getCurrentCScale()
            TScale = self.__myDisplaySettings.getCurrentTScale()
            HScale = self.__myDisplaySettings.getCurrentHScale()
            drawFunc = self.__myDisplaySettings.getCurrentDesign()
            thickness = self.__myDisplaySettings.getCurrentThickness()

            for sperm in self.__mySpermContainer:
                x = self.scene().getWorkSpace().boundingRect().width() * 0.5
                y = self.scene().getWorkSpace().boundingRect().height() * 0.5
                center = self.scene().getWorkSpace().mapToScene(QPointF(x, y))
                glyph = GlyphItem(CBase, CScale, HScale, TScale, center,
                                  sperm.getSummaryParameters(), drawFunc, thickness, True)
                self.scene().addItemToFrame(glyph)

    def __drawSperm(self):

        for sperm in self.__mySpermContainer:
            for index in range(0, len(sperm), 40):

                pos = sperm.getBeatCycleLength() * index

                if pos > len(sperm) - 1:
                    pos = len(sperm) - 1

                frame = sperm.getFrame(pos)
                head = QPolygonF(QtHull(frame.head))
                headPolygon = QGraphicsPolygonItem(head)
                headPolygon.setPen(Qt.black)
                tail = frame.flagellum
                tailPolygon = PolyLine(tail)
                self.scene().addItemToFrame(headPolygon)
                self.scene().addItemToFrame(tailPolygon)

    def __drawPath(self):

        for sperm in self.__mySpermContainer:
            path = PolyLine(sperm.getCentroids(0, len(sperm)))
            path.setPen(QPen(QColor(0, 206, 209), 3.0))
            self.scene().addItemToFrame(path)