"""
    This module is a repository of glyph designs and colour maps. I have put the rest of the preliminary designs
    in designs_backup.txt as they aren't really needed anymore
"""

import geometry
from PyQt4.QtGui  import ( QColor, QPolygonF, QPen )
from PyQt4.QtCore import ( QPointF, Qt )
from pylab import *

### SciPy colour look-up tables ###

VSLColourDict = { 'red'  : ((0.00,0.0,0.0), (0.0035,1.0,1.0), (0.083,1.0,1.0), (0.16,1.0,1.0),
                            (0.33,0.5,0.5), (0.6600,0.0,0.0), (1.000,0.0,0.0)),
                  'green': ((0.0,0.0,0.0), (0.0035,1.0,1.0), (0.083,0.75,0.75), (0.16,0.0,0.0),
                            (0.33,1.0,1.0), (0.66,1.0,1.0), (1.0,0.0,0.0)),
                  'blue' : ((0.0,0.0,0.0), (0.0035,0.0,0.0), (0.083,0.5,0.5),   (0.16,1.0,1.0),
                            (0.33,0.5,0.5), (0.66,1.0,1.0), (1.0,1.0,1.0))   }

UncertaintyColourDict = { 'red'  : ((0.0,0.0,0.0), (0.5,1.0,1.0), (1.0,1.0,1.0)),
                          'green': ((0.0,1.0,1.0), (0.5,1.0,1.0), (1.0,0.0,0.0)),
                          'blue' : ((0.0,0.0,0.0), (0.5,0.0,0.0), (1.0,0.0,0.0))   }

timeColourDict = { 'red':   ( (0.0, 0.894117647, 0.894117647), (0.2, 0.556862745, 0.556862745),
                              (0.4, 0.529411765, 0.529411765), (0.6, 0.890196078, 0.890196078),
                              (0.8, 0.084507042, 0.084507042), (1.0, 0.239215686, 0.23921568 ) ),
                   'green': ( (0.0, 0.674509804, 0.674509804), (0.2, 0.854901961, 0.854901961),
                              (0.4, 0.439215686, 0.439215686), (0.6, 0.207843137, 0.207843137),
                              (0.8, 0.823529412, 0.823529412), (1.0, 0.098039216, 0.098039216) ),
                   'blue':  ( (0.0, 0.674509804, 0.674509804), (0.2, 0.592156863, 0.592156863),
                              (0.4, 0.815686275, 0.815686275), (0.6, 0.207843137, 0.207843137),
                              (0.8, 0.2,         0.2        ), (1.0, 0.68627451,  0.68627451 ) ) }

VSLColourMap         = matplotlib.colors.LinearSegmentedColormap('VSLColormap',VSLColourDict,256)
UncertaintyColourMap = matplotlib.colors.LinearSegmentedColormap('UncertaintyColormap',UncertaintyColourDict,256)
timeColourMap        = matplotlib.colors.LinearSegmentedColormap('TimeColormap',timeColourDict,256)

GLYPH_DESIGN = 0; BIRMINGHAM_DESIGN = 1; CHEN_DESIGN = 2; CHEN_ALT_DESIGN = 3

START_POSITION = 0; MIDDLE_POSITION = 1; END_POSITION = 2; AVERAGE_POSITION = 3; MIDPOINT_POSITION = 4

def drawGlyphDesign( painter, CBase, CScale, HScale, FScale,
                     headUncertainty, flagellumUncertainty, headAngle, width, length,
                     vcl, vap, vsl, bcf, alh, mad,
                     arcLength, changeInAngle, torque, asymmetry, thickness = 1.0, summary = False ):

    r     = CBase / CScale
    Rvsl  = (CBase + vsl) / CScale
    Rvap  = (CBase + vap) / CScale
    Rvcl  = (CBase + vcl) / CScale
    Ralh  = (CBase + vap + alh) / CScale

    # draw the circles representing the velocities of the head
    painter.setPen( QColor.fromRgbF( 0.55, 0.5, 0.5 )  )
    painter.setBrush( Qt.white )
    painter.drawEllipse( geometry.square( Rvcl ) ) # draw VCL

    Rbcf = Rvcl
    if (Rvcl - Rvap) < (alh / CScale) :    Rbcf = Ralh
    # draw the BCF
    painter.setPen( Qt.NoPen )
    painter.setBrush( QColor.fromRgbF( 0.85, 0.85, 0.85 )   )
    startAngle = 180.0 * 16.0
    spanAngle  = (-bcf) * 16.0
    painter.drawPie(geometry.square(Rbcf), startAngle, spanAngle)

    # now draw the ALH
    painter.setPen(Qt.black)
    painter.drawLine( QPointF( 0.0, 0.0 ), QPointF( Ralh, 0.0 ) )
    painter.drawLine( QPointF( 0.0, 0.0 ), QPointF(-Ralh, 0.0 ) )

    painter.setPen( Qt.black )
    painter.setBrush( Qt.white )
    painter.drawEllipse( geometry.square( Rvap ) ) # draw VAP

    painter.setPen( QColor.fromRgbF( 0.5, 0.5, 0.5 )  )
    red   = VSLColourMap(vsl/300.0)[0]
    green = VSLColourMap(vsl/300.0)[1]
    blue  = VSLColourMap(vsl/300.0)[2]
    painter.setBrush( QColor.fromRgbF( red, green, blue )  )
    painter.drawEllipse( geometry.square( Rvsl ) ) # draw VSL

    painter.setPen( Qt.NoPen )
    painter.setBrush( QColor.fromRgbF( 0.85, 0.85, 0.85 )  )
    painter.drawEllipse( geometry.square(r) ) # inner light grey disc

    if not summary:
        # draw the arrow that marks the orientation
        painter.setBrush( Qt.black )
        direction = QPolygonF( [ QPointF(   0.0,  -r*0.5) + QPointF(0.0,-Rvcl*1.03),
                                 QPointF(-r*0.25,    0.0) + QPointF(0.0,-Rvcl*1.03),
                                 QPointF( r*0.25,    0.0) + QPointF(0.0,-Rvcl*1.03) ] )
        painter.drawPolygon(direction)
    # end if

    # draw the circle sector that represents the MAD
    painter.setPen( QColor.fromRgbF( 0.5, 0.5, 0.5 ) )
    painter.setBrush( Qt.white )
    MAD = geometry.square(r)
    startAngle = (90.0 - (mad*0.5) ) * 16.0
    spanAngle  = mad * 16.0
    painter.drawPie(MAD, startAngle, spanAngle)

    painter.setBrush( QColor.fromRgbF( 0.8, 0.8, 0.8 ) )
    painter.setPen  ( QColor.fromRgbF( 0.5, 0.5, 0.5 ) )
    flagellum = geometry.square( (arcLength * FScale) / CScale )
    startAngle = (270.0 - (changeInAngle*0.5) ) * 16.0
    spanAngle  = changeInAngle * 16.0
    painter.translate( QPointF(0.0, r) )
    painter.drawPie(flagellum, startAngle, spanAngle)
    painter.translate( QPointF(0.0,-r) )

    # draw guide lines
    painter.setPen( Qt.white )
    painter.drawLine( QPointF(-r,0.0), QPointF(r,0.0) )
    painter.drawLine( QPointF(0.0,0.0), QPointF(0.0,r + (arcLength * FScale) / CScale )  )

    asymmetryPen = QPen(Qt.black)
    asymmetryPen.setWidthF((torque * 4.0 * FScale)/ CScale )
    painter.setPen( asymmetryPen )
    asymmetry = math.degrees(asymmetry)
    painter.translate(0.0, r)
    painter.rotate(asymmetry)
    painter.drawLine( QPointF( 0.0, 0.0 ), QPointF( 0.0, Rvcl-r ) )
    painter.translate(0.0, Rvcl-r)
    painter.setBrush(Qt.black)
    painter.drawEllipse( geometry.square(r*0.1) )
    painter.translate(0.0, -Rvcl+r)
    painter.rotate(-asymmetry)
    painter.translate(0.0, -r)

    # Draw the head with the uncertainty mapping
    painter.rotate(headAngle)
    painter.setPen( Qt.black )
    red   = UncertaintyColourMap(headUncertainty)[0]
    green = UncertaintyColourMap(headUncertainty)[1]
    blue  = UncertaintyColourMap(headUncertainty)[2]
    painter.setBrush( QColor.fromRgbF( red, green, blue )  )
    painter.drawEllipse( geometry.rectangle( (width*HScale)/CScale, (length*HScale)/CScale ) )
# end def

def drawBirminghamDesign( painter, CBase, CScale, HScale, FScale,
                          headUncertainty, flagellumUncertainty, headAngle, width, length,
                          vcl, vap, vsl, bcf, alh, mad,
                          arcLength, changeInAngle, torque, asymmetry, thickness = 1.0, summary = False ):

    rangeBCF   = 1.0/30.0
    r     = CBase / CScale
    Rvsl  = (CBase + vsl) / CScale
    Rvap  = (CBase + vap) / CScale
    Rvcl  = (CBase + vcl) / CScale
    Ralh  = (CBase + vcl + alh) / CScale

    Rbcf  = (CBase + vcl + 25.0) / CScale

    # draw the BCF
    painter.setPen( Qt.NoPen )
    painter.setBrush( QColor.fromRgbF( 0.85, 0.85, 0.85 )   )
    startAngle = 180.0 * 16.0
    spanAngle  = -bcf * 16.0
    painter.drawPie(geometry.square(Rbcf), startAngle, spanAngle)

    # now draw the ALH
    painter.setPen(Qt.black)
    painter.drawLine( QPointF( 0.0, 0.0 ), QPointF( Ralh, 0.0 ) )
    painter.drawLine( QPointF( 0.0, 0.0 ), QPointF(-Ralh, 0.0 ) )

    # draw the circles representing the velocities of the head
    painter.setPen( QColor.fromRgbF( 0.55, 0.5, 0.5 )  )
    painter.setBrush( Qt.white )
    painter.drawEllipse( geometry.square( Rvcl ) ) # draw VCL

    painter.setPen( Qt.black )
    painter.setBrush( Qt.white )
    painter.drawEllipse( geometry.square( Rvap ) ) # draw VAP

    painter.setPen( QColor.fromRgbF( 0.5, 0.5, 0.5 )  )
    red   = VSLColourMap(vsl/300.0)[0]
    green = VSLColourMap(vsl/300.0)[1]
    blue  = VSLColourMap(vsl/300.0)[2]
    painter.setBrush( QColor.fromRgbF( red, green, blue )  )
    painter.drawEllipse( geometry.square( Rvsl ) ) # draw VSL

    painter.setPen( Qt.NoPen )
    painter.setBrush( QColor.fromRgbF( 0.85, 0.85, 0.85 )  )
    painter.drawEllipse( geometry.square(r) ) # inner light grey disc

    if not summary:
        # draw the arrow that marks the orientation
        painter.setBrush( Qt.black )
        direction = QPolygonF( [ QPointF(   0.0,  -r*0.5) + QPointF(0.0,-Rvcl*1.03),
                                 QPointF(-r*0.25,    0.0) + QPointF(0.0,-Rvcl*1.03),
                                 QPointF( r*0.25,    0.0) + QPointF(0.0,-Rvcl*1.03) ] )
        painter.drawPolygon(direction)
    # end if

    # draw the circle sector that represents the MAD
    painter.setPen( QColor.fromRgbF( 0.5, 0.5, 0.5 ) )
    painter.setBrush( Qt.white )
    MAD = geometry.square(r)
    startAngle = (90.0 - (mad*0.5) ) * 16.0
    spanAngle  = mad * 16.0
    painter.drawPie(MAD, startAngle, spanAngle)

    painter.setBrush( QColor.fromRgbF( 0.8, 0.8, 0.8 ) )
    painter.setPen  ( QColor.fromRgbF( 0.5, 0.5, 0.5 ) )
    flagellum = geometry.square( (arcLength * FScale) / CScale )
    startAngle = (270.0 - (changeInAngle*0.5) ) * 16.0
    spanAngle  = changeInAngle * 16.0
    painter.translate( QPointF(0.0, r) )
    painter.drawPie(flagellum, startAngle, spanAngle)
    painter.translate( QPointF(0.0,-r) )

    # draw guide lines

    painter.setPen( Qt.white )

    painter.drawLine( QPointF(-r,0.0), QPointF(r,0.0) )
    painter.drawLine( QPointF(0.0,0.0), QPointF(0.0,r + (arcLength * FScale) / CScale )  )

    flagellumColour = QColor.fromRgbF( UncertaintyColourMap(flagellumUncertainty)[0],
                                       UncertaintyColourMap(flagellumUncertainty)[1],
                                       UncertaintyColourMap(flagellumUncertainty)[2] )
    painter.setPen( QPen( flagellumColour, 3.0 ) )
    painter.translate(0.0, r)
    painter.drawLine( QPointF(0.0,0.0), QPointF(0.0,(arcLength * FScale) / CScale )  )
    painter.translate(0.0, -r)

    asymmetryPen = QPen(Qt.black)
    asymmetryPen.setWidthF((torque * 4.0 * FScale)/ CScale )
    painter.setPen( asymmetryPen )
    asymmetry = math.degrees(asymmetry)
    painter.translate(0.0, r)
    painter.rotate(asymmetry)
    painter.drawLine( QPointF( 0.0, 0.0 ), QPointF( 0.0, Rvcl-r ) )
    painter.translate(0.0, Rvcl-r)
    painter.setBrush(Qt.black)
    painter.drawEllipse( geometry.square(r*0.1) )
    painter.translate(0.0, -Rvcl+r)
    painter.rotate(-asymmetry)
    painter.translate(0.0, -r)

    # Draw the head with the uncertainty mapping
    painter.rotate(headAngle)
    painter.setPen( Qt.black )

    headColour = QColor.fromRgbF( UncertaintyColourMap(headUncertainty)[0],
                                  UncertaintyColourMap(headUncertainty)[1],
                                  UncertaintyColourMap(headUncertainty)[2] )

    painter.setBrush( headColour  )
    painter.drawEllipse( geometry.rectangle( (width*HScale)/CScale, (length*HScale)/CScale ) )

# end def

def drawChenDesign( painter, CBase, CScale, HScale, FScale,
                          headUncertainty, flagellumUncertainty, headAngle, width, length,
                          vcl, vap, vsl, bcf, alh, mad,
                          arcLength, changeInAngle, torque, asymmetry, thickness = 1.0, summary = False ):

    r     = CBase / CScale

    lineWidth = (thickness * FScale)/ CScale

    Rvsl  = (CBase + vsl) / CScale
    Rvap  = (CBase + vap) / CScale
    Rvcl  = (CBase + vcl) / CScale
    Ralh  = (CBase + vcl + alh) / CScale

    Rbcf  = (CBase + vcl + (2.5*HScale) ) / CScale

    startAngle =  240.0 * 16.0
    toAngle    = -300.0 * 16.0
    oneSegment =  6.0 * 16.0
    fiveSegments = oneSegment * 5.0

    # draw the BCF
    painter.setPen( Qt.NoPen ) #QColor.fromRgbF(0.7,0.7,0.7) )
    painter.setBrush( QColor.fromRgbF( 0.85, 0.85, 0.85 )   )
    spanAngle  = -bcf * oneSegment
    intPart = int(spanAngle / fiveSegments)
    span2Angle = (intPart-1) * fiveSegments

    if intPart*fiveSegments == spanAngle:
        span2Angle = spanAngle

    painter.drawPie(geometry.square(Rbcf), startAngle, spanAngle)

    # draw 15 degree markers
    painter.setPen( QPen( QColor.fromRgbF(0.7,0.7,0.7), lineWidth ) )

    boundAngle = ((abs(int(span2Angle))) / 16 ) + 1

    for x in range(0,boundAngle,30):
        painter.save()    # push matrix
        painter.rotate(x + 120.0)
        painter.drawLine( QPointF( Rvcl, 0.0 ), QPointF( Rbcf, 0.0 ) )
        painter.restore() # pop matrix
    # end for

    # now draw the ALH
    painter.setPen( QPen( Qt.black, lineWidth ) )
    painter.drawLine( QPointF( 0.0, 0.0 ), QPointF( Ralh, 0.0 ) )
    painter.drawLine( QPointF( 0.0, 0.0 ), QPointF(-Ralh, 0.0 ) )

    # draw the circles representing the velocities of the head
    painter.setBrush(Qt.white)
    painter.setPen(Qt.NoPen)
    painter.drawPie(geometry.square(Rvcl), startAngle, toAngle) # draw VCL
    painter.setPen( QPen(QColor.fromRgbF( 0.5, 0.5, 0.5 ), lineWidth)  )
    painter.drawArc(geometry.square(Rvcl), startAngle, toAngle) # draw VCL

    painter.setPen(Qt.NoPen)
    painter.drawPie(geometry.square(Rvap), startAngle, toAngle) # draw VCL
    painter.setPen( QPen(Qt.black, lineWidth) )
    painter.drawArc(geometry.square(Rvap), startAngle, toAngle) # draw VAP

    red   = VSLColourMap(vsl/300.0)[0]
    green = VSLColourMap(vsl/300.0)[1]
    blue  = VSLColourMap(vsl/300.0)[2]
    painter.setPen( Qt.NoPen )
    painter.setBrush( QColor.fromRgbF( red, green, blue )  )
    painter.drawPie(geometry.square(Rvsl), startAngle, toAngle) # draw VSL

    painter.setPen( QPen(QColor.fromRgbF( 0.5, 0.5, 0.5 ), lineWidth) )
    painter.drawArc(geometry.square(Rvsl), startAngle, toAngle) # draw VSL

    painter.setBrush( QColor.fromRgbF( 0.85, 0.85, 0.85 )  )
    painter.drawEllipse( geometry.square(r) ) # inner light grey disc

    if not summary:
        # draw the arrow that marks the orientation
        painter.setPen( Qt.NoPen )
        painter.setBrush( Qt.black )

        direction = QPolygonF( [ QPointF(   0.0,  -r*0.5) + QPointF(0.0,-Rvcl*1.03),
                                 QPointF(-r*0.25,    0.0) + QPointF(0.0,-Rvcl*1.03),
                                 QPointF( r*0.25,    0.0) + QPointF(0.0,-Rvcl*1.03) ] )

        painter.drawPolygon(direction)
    # end if

    # draw the circle sector that represents the MAD
    painter.setPen( QPen(QColor.fromRgbF( 0.5, 0.5, 0.5 ), lineWidth) )
    painter.setBrush( Qt.white )
    MAD = geometry.square(r)
    startAngle = (90.0 - (mad*0.5) ) * 16.0
    spanAngle  = mad * 16.0
    painter.drawPie(MAD, startAngle, spanAngle)

    painter.setBrush( QColor.fromRgbF( 0.8, 0.8, 0.8 ) )
    painter.setPen  ( QPen(QColor.fromRgbF( 0.5, 0.5, 0.5 ), lineWidth) )
    flagellum = geometry.square( (arcLength * FScale) / CScale )
    startAngle = (270.0 - (changeInAngle*0.5) ) * 16.0
    spanAngle  = changeInAngle * 16.0

    painter.save()    # push matrix
    painter.translate( QPointF(0.0, r) )
    painter.drawPie(flagellum, startAngle, spanAngle)
    painter.restore() # pop matrix

    # draw guide lines

    painter.setPen( QPen(Qt.white,lineWidth) )

    painter.drawLine( QPointF(-r,0.0), QPointF(r,0.0) )
    painter.drawLine( QPointF(0.0,0.0), QPointF(0.0, r + (arcLength * FScale) / CScale )  )

    flagellumColour = QColor.fromRgbF( UncertaintyColourMap(flagellumUncertainty)[0],
                                       UncertaintyColourMap(flagellumUncertainty)[1],
                                       UncertaintyColourMap(flagellumUncertainty)[2] )

    painter.setPen( QPen( flagellumColour, lineWidth * 3.0  ) )
    painter.save()    # push matrix
    painter.translate(0.0, r)
    painter.drawLine( QPointF(0.0,0.0), QPointF(0.0,(arcLength * FScale) / CScale )  )
    painter.restore() # pop matrix

    asymmetryPen = QPen(Qt.black, (lineWidth * torque * 2.1 ) + 0.1 )
    painter.setPen( asymmetryPen )

    asymmetry *= 30.0

    painter.save() # push matrix

    painter.translate(0.0, r)
    painter.rotate(-asymmetry)

    # compute the length of the symmetry measure
    k  = int(arcLength / 50.0) + 1
    dk = ( 50.0 * FScale ) / CScale
    asymmetryLength = k * dk

    painter.drawLine( QPointF( 0.0, 0.0 ), QPointF( 0.0, asymmetryLength ) )

    painter.setBrush(Qt.black)
    for i in range(k+1):
        painter.drawEllipse( geometry.square(r*0.1) )
        painter.translate(0.0, dk)
    # end for

    painter.restore() # pop matrix

    # Draw the head with the uncertainty mapping
    painter.rotate(headAngle)
    painter.setPen( QPen(Qt.black, lineWidth) )

    headColour = QColor.fromRgbF( UncertaintyColourMap(headUncertainty)[0],
                                  UncertaintyColourMap(headUncertainty)[1],
                                  UncertaintyColourMap(headUncertainty)[2] )

    painter.setBrush( headColour  )
    painter.drawEllipse( geometry.rectangle( (width*HScale)/CScale, (length*HScale)/CScale ) )

# end def

def drawChenAltDesign( painter, CBase, CScale, HScale, FScale,
                    headUncertainty, flagellumUncertainty, headAngle, width, length,
                    vcl, vap, vsl, bcf, alh, mad,
                    arcLength, changeInAngle, torque, asymmetry, thickness = 1.0, summary = False ):

    r     = CBase / CScale
    Rvsl  = (CBase + vsl) / CScale
    Rvap  = (CBase + vap) / CScale
    Rvcl  = (CBase + vcl) / CScale
    Ralh  = (CBase + vcl + alh) / CScale

    Rbcf  = (CBase + vcl + 25.0) / CScale

    startAngle =  240.0 * 16.0
    toAngle    = -300.0 * 16.0
    oneSegment =  6.0 * 16.0
    fiveSegments = oneSegment * 5.0

    # draw the BCF
    painter.setPen( Qt.NoPen ) #QColor.fromRgbF(0.7,0.7,0.7) )
    painter.setBrush( QColor.fromRgbF( 0.85, 0.85, 0.85 )   )
    spanAngle  = -bcf * oneSegment
    intPart = int(spanAngle / fiveSegments)
    span2Angle = (intPart-1) * fiveSegments

    if intPart*fiveSegments == spanAngle:
        span2Angle = spanAngle

    painter.drawPie(geometry.square(Rbcf), startAngle, spanAngle)
    painter.setPen( QColor.fromRgbF( 0.5, 0.5, 0.5 )  )

    # draw 15 degree markers
    painter.setPen( QColor.fromRgbF(0.7,0.7,0.7) )

    boundAngle = ((abs(int(span2Angle))) / 16 ) + 1
    realAngle =  ((abs(int(spanAngle))) / 16 )

    for x in range(0,boundAngle,30):
        painter.save()    # push matrix
        painter.rotate(x + 120.0)
        painter.drawLine( QPointF( Rvcl, 0.0 ), QPointF( Rbcf, 0.0 ) )
        painter.restore() # pop matrix
        # end for

    # now draw the ALH
    painter.setPen( QPen( Qt.black, (2.0 * FScale)/ CScale) )
    painter.drawLine( QPointF( 0.0, 0.0 ), QPointF( Ralh, 0.0 ) )
    painter.drawLine( QPointF( 0.0, 0.0 ), QPointF(-Ralh, 0.0 ) )

    # draw the circles representing the velocities of the head
    painter.setBrush(Qt.white)
    painter.setPen(Qt.NoPen)
    painter.drawPie(geometry.square(Rvcl), startAngle, toAngle) # draw VCL
    painter.setPen( QColor.fromRgbF( 0.5, 0.5, 0.5 )  )
    painter.drawArc(geometry.square(Rvcl), startAngle, toAngle) # draw VCL

    painter.setPen(Qt.NoPen)
    painter.drawPie(geometry.square(Rvap), startAngle, toAngle) # draw VCL
    painter.setPen( Qt.black )
    painter.drawArc(geometry.square(Rvap), startAngle, toAngle) # draw VAP

    red   = VSLColourMap(vsl/300.0)[0]
    green = VSLColourMap(vsl/300.0)[1]
    blue  = VSLColourMap(vsl/300.0)[2]
    painter.setPen( Qt.NoPen )
    painter.setBrush( QColor.fromRgbF( red, green, blue )  )
    painter.drawPie(geometry.square(Rvsl), startAngle, toAngle) # draw VSL

    painter.setPen( QColor.fromRgbF( 0.5, 0.5, 0.5 )  )
    painter.drawArc(geometry.square(Rvsl), startAngle, toAngle) # draw VSL

    painter.setBrush( QColor.fromRgbF( 0.85, 0.85, 0.85 )  )
    painter.drawEllipse( geometry.square(r) ) # inner light grey disc

    if not summary:
        # draw the arrow that marks the orientation
        painter.setBrush( Qt.black )

        direction = QPolygonF( [ QPointF(   0.0,  -r*0.5) + QPointF(0.0,-Rvcl*1.03),
                                 QPointF(-r*0.25,    0.0) + QPointF(0.0,-Rvcl*1.03),
                                 QPointF( r*0.25,    0.0) + QPointF(0.0,-Rvcl*1.03) ] )

        painter.drawPolygon(direction)
        # end if

    # draw the circle sector that represents the MAD
    painter.setPen( QColor.fromRgbF( 0.5, 0.5, 0.5 ) )
    painter.setBrush( Qt.white )
    MAD = geometry.square(r)
    startAngle = (90.0 - (mad*0.5) ) * 16.0
    spanAngle  = mad * 16.0
    painter.drawPie(MAD, startAngle, spanAngle)

    painter.setBrush( QColor.fromRgbF( 0.8, 0.8, 0.8 ) )
    painter.setPen  ( QColor.fromRgbF( 0.5, 0.5, 0.5 ) )
    flagellum = geometry.square( (arcLength * FScale) / CScale )
    startAngle = (270.0 - (changeInAngle*0.5) ) * 16.0
    spanAngle  = changeInAngle * 16.0

    painter.save()    # push matrix
    painter.translate( QPointF(0.0, r) )
    painter.drawPie(flagellum, startAngle, spanAngle)
    painter.restore() # pop matrix

    # draw guide lines

    painter.setPen( Qt.white )

    painter.drawLine( QPointF(-r,0.0), QPointF(r,0.0) )
    painter.drawLine( QPointF(0.0,0.0), QPointF(0.0,r + (arcLength * FScale) / CScale )  )

    # compute the length of the symmetry measure
    k  = int(arcLength / 50.0) + 1
    dk = ( 50.0 * FScale ) / CScale
    guideLength = k * dk

    flagellumColour = QColor.fromRgbF( UncertaintyColourMap(flagellumUncertainty)[0],
                                       UncertaintyColourMap(flagellumUncertainty)[1],
                                       UncertaintyColourMap(flagellumUncertainty)[2] )

    painter.save()    # push matrix
    painter.translate(0.0, r)

    painter.setPen( QPen( flagellumColour, (3.0 * FScale)/ CScale  ) )
    painter.drawLine( QPointF(0.0,0.0), QPointF(0.0, guideLength) )

    painter.setBrush( flagellumColour )
    painter.setPen( Qt.black )
    for i in range(k+1):
        painter.drawEllipse( geometry.square(r*0.1) )
        painter.translate(0.0, dk)
    # end for

    painter.restore() # pop matrix

    asymmetryPen = QPen(Qt.black, (torque * 4.0 * FScale)/ CScale )
    painter.setPen( asymmetryPen )

    asymmetry *= -30.0

    painter.save() # push matrix

    painter.translate(0.0, r)
    painter.rotate(asymmetry)

    painter.drawLine( QPointF( 0.0, 0.0 ), QPointF( 0.0, guideLength ) )

    painter.setBrush(Qt.black)
    painter.translate(0.0, k*dk)
    painter.drawEllipse( geometry.square(r*0.1) )
    # end for

    painter.restore() # pop matrix

    # Draw the head with the uncertainty mapping
    painter.rotate(headAngle)
    painter.setPen( Qt.black )

    headColour = QColor.fromRgbF( UncertaintyColourMap(headUncertainty)[0],
                                  UncertaintyColourMap(headUncertainty)[1],
                                  UncertaintyColourMap(headUncertainty)[2] )

    painter.setBrush( headColour  )
    painter.drawEllipse( geometry.rectangle( (width*HScale)/CScale, (length*HScale)/CScale ) )

# end def