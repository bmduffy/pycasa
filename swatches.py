import sys

from glyphview import ( GlyphView, GlyphScene, GlyphItem )

from PyQt4.QtGui import ( QApplication, QDialog, QPen, QBrush, QHBoxLayout,
                           QPushButton, QVBoxLayout, QGraphicsRectItem, QGraphicsSimpleTextItem,
                           QPixmap, QFileDialog, QPainter, QComboBox, QSpinBox )

from PyQt4.QtCore import ( QRectF, QString, QPointF, SIGNAL, SLOT, Qt, pyqtSlot, QSize)

from dialogs import ( centreTextLabelBelow )

import glyphdesigns as designs

#noinspection PyOldStyleClasses
class SwatchBoard(QDialog):

    SWATCH_BOARD = 0; MAMMAL_SWATCH = 1; CRASH_TEST = 2

    def __init__(self, parent=None):

        super(SwatchBoard,self).__init__(parent)

        self.__myMode       = self.SWATCH_BOARD
        self.__drawFunction = designs.drawChenDesign
        self.__thickness    = 2

        self.view = GlyphView(self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.TextAntialiasing)
        vLayout = QVBoxLayout()
        vLayout.addWidget( self.view )

        self.changeMode(self.__myMode) # figure out what to render

        capture = QPushButton('capture a screen shot of current state')
        self.connect( capture, SIGNAL("clicked()"), self, SLOT("captureScene()") )

        chooseDesign = QComboBox()
        designChoices = [ 'Original', 'Birmingham', 'Chen', 'Chen Alt' ]
        chooseDesign.addItems( designChoices )
        chooseDesign.setCurrentIndex(designs.CHEN_DESIGN)
        self.connect( chooseDesign, SIGNAL("currentIndexChanged(int)"), self, SLOT("changeDesign(int)"))

        chooseMode = QComboBox()
        modeChoices = [ 'Swatch', 'Mammals', 'Crash' ]
        chooseMode.addItems( modeChoices )
        self.connect( chooseMode, SIGNAL("currentIndexChanged(int)"), self, SLOT("changeMode(int)") )

        thicknessSpinBox = QSpinBox()
        thicknessSpinBox.setMinimum( 1 )
        thicknessSpinBox.setMaximum( 100 )
        thicknessSpinBox.setValue( self.__thickness )

        self.connect( thicknessSpinBox, SIGNAL("valueChanged(int)"), self, SLOT("thicknessChanged(int)") )

        hLayout = QHBoxLayout()
        hLayout.addWidget( capture          )
        hLayout.addWidget( chooseDesign     )
        hLayout.addWidget( chooseMode       )
        hLayout.addWidget( thicknessSpinBox )

        vLayout.addLayout(hLayout)
        self.setLayout(vLayout)

    # end def

    @staticmethod
    def imageFormats():
        return "*.png *.bmp *.jpg *.jpeg *.ppm"
    # end def

    @pyqtSlot(int)
    def thicknessChanged(self, thickness):
        self.__thickness = thickness
        self.changeMode( self.__myMode )
    # end def

    @pyqtSlot(int)
    def changeMode(self, mode):
        if mode is self.SWATCH_BOARD:
            self.setWindowTitle("Glyph Swatch Board")
            self.swatchBoard()
        elif mode is self.MAMMAL_SWATCH:
            self.setWindowTitle("Mammal Swatch Board")
            self.mammalSwatch()
        elif mode is self.CRASH_TEST:
            self.setWindowTitle(" !!! CRASH TEST !!! ")
            self.crashTest()
        # end if
        self.__myMode = mode
    # end def

    @pyqtSlot(int)
    def changeDesign(self, design):
        if design is designs.GLYPH_DESIGN:
            self.__drawFunction = designs.drawGlyphDesign
        elif design is designs.BIRMINGHAM_DESIGN:
            self.__drawFunction = designs.drawBirminghamDesign
        elif design is designs.CHEN_DESIGN:
            self.__drawFunction = designs.drawChenDesign
        elif design is designs.CHEN_ALT_DESIGN:
            self.__drawFunction = designs.drawChenAltDesign
        # end if
        self.changeMode( self.__myMode )
    # end def

    @pyqtSlot()
    def captureScene(self):
        oFile = QString("")
        oFile = QFileDialog.getSaveFileName( None, "Save Screen Capture",
            oFile, "Image Formats(%s)" % self.imageFormats() )

        if oFile.isEmpty() : return False

        zoomFactor = 3.0

        oldSize = self.size()
        tempSize = QSize( oldSize.width()*zoomFactor , oldSize.height()*zoomFactor  )

        self.resize( tempSize )
        self.view.scale( zoomFactor, zoomFactor )

        image = QPixmap.grabWidget(self.view)

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

        self.view.scale( 1.0/zoomFactor ,1.0/zoomFactor )
        self.resize( oldSize )

        return True
    # end def

    def crashTest(self):

        width = 920.0; height = 230.0
        self.view.setSceneRect( QRectF(0.0,0.0,width,height) )
        self.view.scene().updateFrame(width,height)

        sizes = range(2, 11)
        dScale = 1.0/(len(sizes)-1.0)
        x         =  80.0;   xStep = 130;   scaled = 80
        angle     = -90.0;   angleDelta     = 180.0*dScale
        parameter =   0.0;   parameterDelta = 1.0
        p2        =   0.0;   p2Delta = 1.0*dScale
        asymmetry =  -1.0;   asymmetryDelta = 2.0*dScale
        y         =   100;   flagTheta =   0.0
        bcf = 0

        CBase  = 50.0
        HScale = 4.0;  TScale = 1.25

        for CScale in sizes:
            #Scale glyphs test
            sizeLabel = QGraphicsSimpleTextItem( "%.2f px" % (CBase/(CScale*0.37)) )
            sizeBound = sizeLabel.boundingRect()
            sizeLabel.translate(x - sizeBound.width()*0.5, y + ((CBase + 150)/CScale))
            self.view.scene().addItemToFrame(sizeLabel)
            glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( x, y ),
                [ 0.0, 0.0,         # certainty
                  79.2, 45.6, 20.0, # velocities
                  14.0, 10.0, 35.0,  # BCF ALH MAD
                  0.0, 5.03, 3.21,  # head angle, length, width
                  54.5,             # arc length
                  45.0, # change in angle
                  0.5, # torque
                  -1.0, # asymmetry
                ], self.__drawFunction, self.__thickness, False )
            self.view.scene().addItemToFrame(glyph)

            asymmetry += asymmetryDelta
            parameter += parameterDelta
            p2        += p2Delta
            angle     += angleDelta
            flagTheta += angleDelta
            x         += xStep
            xStep *= 0.92
            scaled    += (CScale+10.0)*2.0
            bcf += 1
            # end for

            title  = QGraphicsSimpleTextItem(QString("Glyph Crash Test"))
            # some labels to explain what is going on
            self.view.scene().addItemToWorkSpace( title, GlyphScene.ALIGN_TOP_CENTER )

            # end if
        # end for

        self.view.scene().update()

    # end def

    def swatchBoard(self):
        """
            setParameters(uncertainty, vcl, vap, vsl, bcf, alh, mad,
                          length, width, arc, theta, torque, asymmetry)
        """
        width = 1000; height = 1100
        self.view.scene().updateFrame(width,height)

        sizes = range(2, 9)
        dScale = 1.0/(len(sizes)-1.0)
        x         =  80.0;   xStep = 110;   scaled = 80
        angle     = -90.0;   angleDelta     = 180.0*dScale
        parameter =   0.0;   parameterDelta = 1.0
        p2        =   0.0;   p2Delta = 1.0*dScale
        asymmetry =  -1.0;   asymmetryDelta = 2.0*dScale
        glyphSize =  20.0;   y = 100
        flagTheta =   0.0;   step     = 100
        bcf = 0

        CBase  = 42; CScale = 4.0
        HScale = 4.0;  TScale = 1.25

        textOffset = 20

        for size in sizes:

            # Rotation test
            rotationLabel = QGraphicsSimpleTextItem( "%.2f deg" % angle )
            rotationBound = rotationLabel.boundingRect()
            rotationLabel.translate(x - rotationBound.width()*0.5, y + glyphSize + textOffset)
            self.view.scene().addItemToFrame(rotationLabel)
            glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( x, y ),
                [ 0.0, 0.0, # certainty
                  79.2, 45.6, 40.9, # velocities
                  6, 5.2, 11.86,  # BCF ALH MAD
                  0.0, 5.03, 3.21,   # head angle, length, width
                  54.5, # arc length
                  45.0, # change in angle
                  0.5, # torque
                  0.0, # asymmetry
                ], self.__drawFunction, self.__thickness, False)
            glyph.rotate(angle)
            self.view.scene().addItemToFrame(glyph)

            # Uncertainty test
            uncertaintyLabel = QGraphicsSimpleTextItem( "%.2f" % p2 )
            uncertaintyBound = uncertaintyLabel.boundingRect()
            uncertaintyLabel.translate(x - uncertaintyBound.width()*0.5, y + step + glyphSize + textOffset)
            self.view.scene().addItemToFrame(uncertaintyLabel)
            glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( x, y + step ),
                [ p2, p2, # certainty
                  79.2, 45.6, 40.9, # velocities
                  6, 5.2, 11.86, # BCF ALH MAD
                  0.0, 5.03, 3.21,   # head angle, length, width
                  54.5, # arc length
                  45.0, # change in angle
                  0.5, # torque
                  0.0, # asymmetry
                ], self.__drawFunction, self.__thickness, False )
            self.view.scene().addItemToFrame(glyph)

            # VCL, VAP, VSL test
            velocityLabel = QGraphicsSimpleTextItem( "[%d,%d,%d]" %
                                                     (20.0 + parameter*6.0, 10.0 + parameter*6.0, 5.0 + parameter*6.0) )
            velocityBound = velocityLabel.boundingRect()
            velocityLabel.translate(x - velocityBound.width()*0.5, y + (step*2) + glyphSize + textOffset)
            self.view.scene().addItemToFrame(velocityLabel)
            glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( x, y + step*2 ),
                [ 0.0, 0.0, # certainty
                  25.0 + parameter*7.0, 15.0 + parameter*7.0, 5.0 + parameter*7.0, # velocities
                  6, 5.2, 11.86,  # BCF ALH MAD
                  0.0, 5.03, 3.21,   # head angle, length, width
                  54.5, # arc length
                  45.0, # change in angle
                  0.5, # torque
                  0.0, # asymmetry
                ], self.__drawFunction, self.__thickness, False )
            self.view.scene().addItemToFrame(glyph)

            # BCF, ALH test
            patternLabel = QGraphicsSimpleTextItem( "%d vs %d" % (parameter*5.0, parameter*7.0) )
            patternBound = patternLabel.boundingRect()
            patternLabel.translate(x - patternBound.width()*0.5, y + (step*3) + glyphSize + textOffset )
            self.view.scene().addItemToFrame(patternLabel)
            glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( x, y + step*3 ),
                [  0.0, 0.0, # certainty
                   79.2, 45.6, 40.9, # velocities
                   parameter*5.0, parameter*7.0, 11.86,  # BCF ALH MAD
                   0.0, 5.03, 3.21,   # head angle, length, width
                   54.5, # arc length
                   45.0, # change in angle
                   0.5, # torque
                   0.0, # asymmetry
                ], self.__drawFunction, self.__thickness, False )
            self.view.scene().addItemToFrame(glyph)

            # MAD test
            madLabel = QGraphicsSimpleTextItem( "%.2f" % parameter )
            madBound = madLabel.boundingRect()
            madLabel.translate(x - madBound.width()*0.5, y + (step*4) + glyphSize + textOffset)
            self.view.scene().addItemToFrame(madLabel)
            glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( x, y + step*4 ),
                [  0.0, 0.0, # certainty
                   79.2, 45.6, 40.9, # velocities
                   6, 5.2, angle,  # BCF ALH MAD
                   0.0, 5.03, 3.21,   # head angle, length, width
                   54.5, # arc length
                   45.0, # change in angle
                   0.5, # torque
                   0.0, # asymmetry
                ], self.__drawFunction, self.__thickness, False )
            self.view.scene().addItemToFrame(glyph)
            # length, width test
            headLabel = QGraphicsSimpleTextItem( "%.2f vs %.2f" % (1.03 + parameter, 0.21 + parameter) )
            headBound = headLabel.boundingRect()
            headLabel.translate(x - headBound.width()*0.5, y + (step*5) + glyphSize + textOffset )
            self.view.scene().addItemToFrame(headLabel)
            glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( x, y + step*5 ),
                [  0.0, 0.0, # certainty
                   79.2, 45.6, 40.9, # velocities
                   6, 5.2, 11.86,  # BCF ALH MAD
                   0.0,  1.03 + parameter, 0.21 + parameter,   # head angle, length, width
                   54.5, # arc length
                   45.0, # change in angle
                   0.5, # torque
                   0.0, # asymmetry
                ], self.__drawFunction, self.__thickness, False )
            self.view.scene().addItemToFrame(glyph)
            # arc length test
            arcLabel = QGraphicsSimpleTextItem( "%.2f" % (50.5+(parameter*3.0)) )
            arcBound = arcLabel.boundingRect()
            arcLabel.translate(x - arcBound.width()*0.5, y + (step*6) + glyphSize + textOffset )
            self.view.scene().addItemToFrame(arcLabel)
            glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( x, y + step*6 ),
                [  0.0, 0.0, # certainty
                   79.2, 45.6, 40.9, # velocities
                   6, 5.2, 11.86,  # BCF ALH MAD
                   0.0, 5.03, 3.21,   # head angle, length, width
                   50.5+(parameter*3.0), # arc length
                   45.0, # change in angle
                   0.5, # torque
                   0.0, # asymmetry
                ], self.__drawFunction, self.__thickness, False )
            self.view.scene().addItemToFrame(glyph)
            #  flagellum theta test
            thetaLabel = QGraphicsSimpleTextItem( "%.2f deg" % flagTheta )
            thetaBound = thetaLabel.boundingRect()
            thetaLabel.translate(x - thetaBound.width()*0.5, y + (step*7) + glyphSize + textOffset )
            self.view.scene().addItemToFrame(thetaLabel)
            glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( x, y + step*7 ),
                [  0.0, 0.0, # certainty
                   79.2, 45.6, 40.9, # velocities
                   6, 5.2, 11.86,  # BCF ALH MAD
                   0.0, 5.03, 3.21,   # head angle, length, width
                   54.5, # arc length
                   flagTheta, # change in angle
                   0.5, # torque
                   0.0, # asymmetry
                ], self.__drawFunction, self.__thickness, False )
            self.view.scene().addItemToFrame(glyph)
            # torque test
            torqueLabel = QGraphicsSimpleTextItem( "%.2f" % p2 )
            torqueBound = torqueLabel.boundingRect()
            torqueLabel.translate(x - torqueBound.width()*0.5, y + (step*8) + glyphSize + textOffset )
            self.view.scene().addItemToFrame(torqueLabel)
            glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( x, y + step*8 ),
                [  0.0, 0.0, # certainty
                   79.2, 45.6, 40.9, # velocities
                   6, 5.2, 11.86,  # BCF ALH MAD
                   0.0, 5.03, 3.21,   # head angle, length, width
                   54.5, # arc length
                   45.0, # change in angle
                   p2, # torque
                   0.0, # asymmetry
                ], self.__drawFunction, self.__thickness, False )
            self.view.scene().addItemToFrame(glyph)
            #  asymmetry test
            asymmetryLabel = QGraphicsSimpleTextItem( "%.2f" % asymmetry )
            asymmetryBound = asymmetryLabel.boundingRect()
            asymmetryLabel.translate(x - asymmetryBound.width()*0.5, y + (step*9) + glyphSize + textOffset )
            self.view.scene().addItemToFrame(asymmetryLabel)
            glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( x, y + step*9 ),
                [  0.0, 0.0,  # certainty
                   79.2, 45.6, 40.9, # velocities
                   6, 5.2, 11.86,  # BCF ALH MAD
                   0.0, 5.03, 3.21,   # head angle, length, width
                   54.5, # arc length
                   45.0, # change in angle
                   0.5, # torque
                   asymmetry, # asymmetry
                ], self.__drawFunction, self.__thickness, False )
            self.view.scene().addItemToFrame(glyph)

            asymmetry += asymmetryDelta
            parameter += parameterDelta
            p2        += p2Delta
            angle     += angleDelta
            flagTheta += 10.0
            x         += xStep
            scaled    += (size+10)*2
            bcf += 1
            # end for

        title  = QGraphicsSimpleTextItem(QString("Glyph Swatch Board"))
        # some labels to explain what is going on
        self.view.scene().addItemToWorkSpace( title, GlyphScene.ALIGN_TOP_CENTER )

        labels = [ QGraphicsSimpleTextItem(QString("orientation [-90, 90] ")),
                   QGraphicsSimpleTextItem(QString("uncertainty [0.0, 1.0]")),
                   QGraphicsSimpleTextItem(QString("VCL, VAP, VSL")),
                   QGraphicsSimpleTextItem(QString("BCF vs. ALH")),
                   QGraphicsSimpleTextItem(QString("MAD")),
                   QGraphicsSimpleTextItem(QString("head length vs. width")),
                   QGraphicsSimpleTextItem(QString("flagellum arc length")),
                   QGraphicsSimpleTextItem(QString("change in flagellum angle")),
                   QGraphicsSimpleTextItem(QString("torque")),
                   QGraphicsSimpleTextItem(QString("asymmetry")) ]
        y = 100
        for pair in enumerate(labels):
            pair[1].translate( 790, y + step*pair[0] )
            self.view.scene().addItemToFrame(pair[1])
            # end for

        self.view.scene().update()

    # end def

    def mammalSwatch(self):

        width = 1250; height = 450
        self.view.scene().updateFrame(width,height,False)

        background = QBrush(Qt.white)
        border     = QPen(Qt.black)
        rect = QGraphicsRectItem(QRectF(0,10,630,190))
        rect.setPen(border)
        rect.setBrush(background)
        self.view.scene().addItemToFrame(rect)

        CBase  = 60.0; CScale = 3.75
        HScale = 3.0;  TScale = 1.25
        # draw mammal swatch board 
        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( 50, 100 ),
            [ 0.0, 0.75, # certainty
              79.2, 45.6, 40.9, # velocities
              6, 5.2, 11.86,  # BCF ALH MAD
              0.0, 5.03, 3.21,   # head angle, length, width
              54.5, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True  )
        label = centreTextLabelBelow("Average", glyph, 50.0)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( 150, 100 ),
            [ 0.0, 0.75, # certainty
              64.88478, 59.701995, 57.092085, # velocities
              4, 10.56, 14.95,  # BCF ALH MAD
              0.0, 5.03, 3.21,   # head angle, length, width
              54.5, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True  )
        label = centreTextLabelBelow("Grade A", glyph, 50.0)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( 250, 100 ),
            [ 0.0, 0.75, # certainty
              49.99563, 41.12289, 24.926715, # velocities
              4.0, 10.122163, 8.77,  # BCF ALH MAD
              0.0, 5.03, 3.21,   # head angle, length, width
              54.5, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True  )
        label = centreTextLabelBelow("Grade B", glyph, 50.0)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( 350, 100 ),
            [ 0.0, 0.75, # certainty
              0.0, 0.0, 0.0, # velocities
              7.0, 17.0, 40.54,  # BCF ALH MAD
              0.0, 5.03, 3.21,   # head angle, length, width
              54.5, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True  )
        label = centreTextLabelBelow("Grade C", glyph, 50.0 )
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem(CBase, CScale, HScale, TScale, QPointF( 450, 100 ),
            [ 0.0, 0.75, # certainty
              0.0, 0.0, 0.0, # velocities
              0.0, 0.0, 0.0,  # BCF ALH MAD
              0.0, 5.03, 3.21,   # head angle, length, width
              54.5, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True )
        label = centreTextLabelBelow("Grade D", glyph, 50.0)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( 550, 100 ),
            [ 0.0, 0.75, # certainty
              180.0, 90.0, 81.0, # velocities
              6.0, 1.0, 4.0,  # BCF ALH MAD
              0.0, 5.03, 3.21,   # head angle, length, width
              54.5, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True )
        label = centreTextLabelBelow("Hyperactivated", glyph, 70.0)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( 690, 75 ),
            [ 0.0, 0.75, # certainty
              109.9, 59.0, 35.9, # velocities
              5.8, 7.2, 0.0,  # BCF ALH MAD
              0.0, 8.23, 4.36,   # head angle, length, width
              39.75, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True  )
        label = centreTextLabelBelow("Boar", glyph, 65.0)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( 800, 75 ),
            [ 0.0, 0.75, # certainty
              142.7, 100.0, 91.5, # velocities
              21.6, 5.1, 0.0,  # BCF ALH MAD
              0.0, 9.56, 4.91,   # head angle, length, width
              46.61, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True )
        label = centreTextLabelBelow("Bull", glyph, 65)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( 910, 75 ),
            [ 0.0, 0.75, # certainty
              93.9, 58.5, 40.3, # velocities
              12.2, 3.65, 0.0,  # BCF ALH MAD
              0.0, 6.41, 3.0,   # head angle, length, width
              53.6, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True  )
        label = centreTextLabelBelow("Donkey", glyph, 65)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( 460, 300 ),
            [ 0.0, 0.75, # certainty
              127.8, 53.0, 41.3, # velocities
              1.51, 31.5, 0.0,  # BCF ALH MAD
              0.0, 5.0, 3.56,   # head angle, length, width
              41.56, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True )
        label = centreTextLabelBelow("Gazelle", glyph, 85)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( 1010, 75 ),
            [ 0.0, 0.75, # certainty
              132.85, 113.95, 108.35, # velocities
              2.8, 5.8, 27.2,  # BCF ALH MAD
              0.0, 5.0, 3.0,   # head angle, length, width
              42.0, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True )
        label = centreTextLabelBelow("Marmoset", glyph, 65)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( 860, 300  ),
            [ 0.0, 0.75, # certainty
              316.2, 259.1, 239.7, # velocities
              33.1, 9.7, 0.0,  # BCF ALH MAD
              0.0, 4.5, 2.0,   # head angle, length, width
              40.5, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True )
        label = centreTextLabelBelow("Sperm Whale", glyph, 125)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( 1130, 75 ),
            [ 0.0, 0.75, # certainty
              151.8, 120.5, 107.8, # velocities
              42.8, 2.5, 0.0,  # BCF ALH MAD
              0.0, 4.76, 2.56,   # head angle, length, width
              54.59, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True )
        label = centreTextLabelBelow("Cat", glyph,65)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF(100, 300 ),
            [ 0.0, 0.75, # certainty
              205.26, 128.54, 77.4, # velocities
              30.96, 47.12, 36,  # BCF ALH MAD
              0.0, 8.27, 3.65,   # head angle, length, width
              125.0, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True )
        label = centreTextLabelBelow("Mouse", glyph, 85)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( 250, 300 ),
            [ 0.0, 0.75, # certainty
              87.45, 45.26, 33.77, # velocities
              24.62, 4.18, 0.0,  # BCF ALH MAD
              0.0, 8.33, 4.81,   # head angle, length, width
              49.51, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True )
        label = centreTextLabelBelow("Rabbit", glyph, 85)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( 350, 300 ),
            [ 0.0, 0.75, # certainty
              83.81, 51.77, 39.97, # velocities
              17.05, 5.4, 0.0,  # BCF ALH MAD
              0.0, 12.1, 1.8,   # head angle, length, width
              177.0, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True )
        label = centreTextLabelBelow("Rat", glyph, 85)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( 1100, 300 ),
            [ 0.0, 0.75, # certainty
              342.2, 163.7, 98.5, # velocities
              24.4, 23.2, 0.0,  # BCF ALH MAD
              0.0, 12.1, 1.8,   # head angle, length, width
              177.0, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True )
        label = centreTextLabelBelow("Rat On Drugs", glyph,125)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        glyph = GlyphItem( CBase, CScale, HScale, TScale, QPointF( 650, 300 ),
            [ 0.0, 0.75, # certainty
              262.0, 211.0, 188.0, # velocities
              19.4, 13.4, 0.0,  # BCF ALH MAD
              0.0, 15.2, 2.51,   # head angle, length, width
              176.8, # arc length
              30.0, # change in angle
              0.5, # torque
              0.0, # asymmetry
            ], self.__drawFunction, self.__thickness, True )
        label = centreTextLabelBelow("Hamster", glyph, 125)
        self.view.scene().addItemToFrame(label)
        self.view.scene().addItemToFrame(glyph)

        human       = QGraphicsSimpleTextItem(QString("Human"))
        human.translate(30.0, 20.0)
        self.view.scene().addItemToFrame(human)

        self.view.scene().update()

        # end def

# end class

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Glyph Testing Board")
    view = SwatchBoard()
    view.show()
    sys.exit(app.exec_())
# end def

if __name__ == "__main__":
    main() # run the main application window