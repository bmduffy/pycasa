"""
    This module provides a set of useful dialogs for manipulating widgets and glyphs
"""

from PyQt4.QtGui  import ( QDialog, QLabel, QSpinBox, QDoubleSpinBox, QLayout, QHBoxLayout, QVBoxLayout, QGroupBox,
                           QGraphicsSimpleTextItem, QGridLayout, QComboBox, QCheckBox )

from PyQt4.QtCore import ( SIGNAL, SLOT )

import glyphdesigns as designs

def VGroupBox(label='group label', items = None, flat = False):
    group  = QGroupBox(label)
    group.setFlat(flat)
    layout = QVBoxLayout()
    for item in items:
        if isinstance(item, QLayout):
            layout.addLayout(item)
        else:
            layout.addWidget(item)
    group.setLayout(layout)
    return group
# end def

def HGroupBox(label='group label', items = None, flat = False):
    group  = QGroupBox(label)
    group.setFlat(flat)
    layout = QHBoxLayout()
    for item in items:
        if isinstance(item, QLayout):
            layout.addLayout(item)
        else:
            layout.addWidget(item)
    group.setLayout(layout)
    return group
# end def

def centreTextLabelAbove(string, glyph):
    position    = glyph.pos()
    glyphBounds = glyph.boundingRect()
    label       = QGraphicsSimpleTextItem(string)
    labelBounds = label.boundingRect()
    label.translate( position.x() - (labelBounds.width()*0.5),
                     position.y() - (glyphBounds.height()*0.5 + labelBounds.height()) )
    return label
# end def

def centreTextLabelBelow(string, glyph, offset=10.0):
    position    = glyph.pos()
    label       = QGraphicsSimpleTextItem(string)
    labelBounds = label.boundingRect()
    label.translate( position.x() - (labelBounds.width()*0.5),
                     position.y() + offset )
    return label
# end def

#noinspection PyOldStyleClasses
class LabelSpinBox(QDialog):
    
    def __init__(self, label="label", minimum = 0.0, maximum=1.0, value=0.5,
                       slots=None, signal="valueChanged(double)", parent=None):
        super(LabelSpinBox,self).__init__(parent)
        self.spinBox = QDoubleSpinBox(self)
        self.spinBox.setRange( minimum, maximum )
        self.spinBox.setValue( value )
        self.spinBox.setSingleStep(0.01)
        self.label = QLabel(label, self)
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.spinBox)
        
        for slot in slots:
            self.connect(self.spinBox,SIGNAL(signal),slot)
        # end for
        
        self.setLayout(layout)
    # end def
    
    def value(self):
        return self.spinBox.value()
    # end def
    
    def setRange(self, minimum, maximum):
        self.spinBox.setRange(minimum, maximum)
    
    def setSingleStep(self, value):
        self.spinBox.setSingleStep(value)
    
    def setLabel(self, label):
        self.label.setText(label)
        
    def setMinimum(self, value):
        self.spinBox.setMinimum(value)
        if  value > self.spinBox.value():
            self.spinBox.setValue(value)
    # end def
    
    def setMaximum(self, value):
        self.spinBox.setMaximum(value)
        if  value < self.spinBox.value():
            self.spinBox.setValue(value)
    # end def
# end class

#noinspection PyOldStyleClasses
class GlyphControlDialog(QDialog):

    def __init__(self, CBase, CScale, HScale, TScale, thickness=2,
                 design   = designs.CHEN_ALT_DESIGN,
                 strategy = designs.MIDDLE_POSITION,
                 parent=None):
        super(GlyphControlDialog,self).__init__(parent)

        self.setWindowTitle("Glyph Controls")

        self.__cBaseSpinBox     = QDoubleSpinBox()
        self.__cScaleSpinBox    = QDoubleSpinBox()
        self.__hScaleSpinBox    = QDoubleSpinBox()
        self.__tScaleSpinBox    = QDoubleSpinBox()
        self.__thicknessSpinBox = QSpinBox()

        self.__cBaseSpinBox.setMinimum (1.0); self.__cBaseSpinBox.setMaximum (1000.0)
        self.__cScaleSpinBox.setMinimum(1.0); self.__cScaleSpinBox.setMaximum(1000.0)
        self.__hScaleSpinBox.setMinimum(1.0); self.__hScaleSpinBox.setMaximum(1000.0)
        self.__tScaleSpinBox.setMinimum(1.0); self.__tScaleSpinBox.setMaximum(1000.0)
        self.__thicknessSpinBox.setMinimum(1); self.__thicknessSpinBox.setMaximum(100)

        self.__cBaseSpinBox.setValue(CBase)
        self.__cScaleSpinBox.setValue(CScale)
        self.__hScaleSpinBox.setValue(HScale)
        self.__tScaleSpinBox.setValue(TScale)
        self.__thicknessSpinBox.setValue(thickness)

        groupsLayout = QVBoxLayout()

        scalingGroup  = QGroupBox('Scaling', self)
        scalingLayout = QGridLayout()

        scalingLayout.addWidget( QLabel('Base Size'), 0, 0 )
        scalingLayout.addWidget( self.__cBaseSpinBox, 0, 1 )
        scalingLayout.addWidget( QLabel('microns'),   0, 2 )

        scalingLayout.addWidget( QLabel('GlyphScale'),1, 0 )
        scalingLayout.addWidget( self.__cScaleSpinBox,1, 1 )
        scalingLayout.addWidget( QLabel('microns'),   1, 2 )

        scalingLayout.addWidget( QLabel('Head Scale'),2, 0 )
        scalingLayout.addWidget( self.__hScaleSpinBox,2, 1 )
        scalingLayout.addWidget( QLabel('microns'),   2, 2 )

        scalingLayout.addWidget( QLabel('Tail Scale'),3, 0 )
        scalingLayout.addWidget( self.__tScaleSpinBox,3, 1 )
        scalingLayout.addWidget( QLabel('microns'),   3, 2 )

        scalingLayout.addWidget( QLabel('Line Thickness'), 4, 0)
        scalingLayout.addWidget( self.__thicknessSpinBox,  4, 1)
        scalingLayout.addWidget( QLabel('pt'), 4, 2)

        scalingGroup.setLayout( scalingLayout )

        designGroup  = QGroupBox('Design', self)
        designLayout = QGridLayout()

        self.__designComboBox = QComboBox()
        self.__designComboBox.addItems( [ 'A1', 'B1', 'C1', 'C2' ] )
        self.__designComboBox.setCurrentIndex( design )
        designLayout.addWidget( QLabel('Glyph Designs'), 0, 0 )
        designLayout.addWidget( self.__designComboBox, 0, 1 )

        designGroup.setLayout(designLayout)

        positionGroup  = QGroupBox('Layout Strategy', self)
        positionLayout = QGridLayout()

        self.__positionComboBox = QComboBox()
        self.__positionComboBox.addItems( [ 'start', 'middle', 'end', 'average', 'midpoint' ] )
        self.__positionComboBox.setCurrentIndex( strategy )

        self.__colourPathCheckBox = QCheckBox()
        self.__colourPathCheckBox.setChecked(True)

        self.__segmentsCheckBox = QCheckBox()
        self.__segmentsCheckBox.setChecked(False)

        positionLayout.addWidget( QLabel('Strategy'), 0, 0 )
        positionLayout.addWidget( self.__positionComboBox, 0, 1 )
        positionLayout.addWidget( QLabel('Colour Path'), 1, 0 )
        positionLayout.addWidget( self.__colourPathCheckBox, 1, 1)
        positionLayout.addWidget( QLabel('Segments'), 2, 0 )
        positionLayout.addWidget( self.__segmentsCheckBox, 2, 1)

        positionGroup.setLayout(positionLayout)

        groupsLayout.addWidget( scalingGroup )
        groupsLayout.addWidget( designGroup  )
        groupsLayout.addWidget( positionGroup )

        self.setLayout(groupsLayout)

    # end def

    def getCurrentCBase(self):
        return self.__cBaseSpinBox.value()
    # end def

    def getCurrentCScale(self):
        return self.__cScaleSpinBox.value()
    # end def

    def getCurrentTScale(self):
        return self.__tScaleSpinBox.value()
    # end def

    def getCurrentHScale(self):
        return self.__hScaleSpinBox.value()
    # end def

    def getCurrentDesign(self):

        design = self.__designComboBox.currentIndex()

        if design is designs.GLYPH_DESIGN:
            return designs.drawGlyphDesign
        elif design is designs.BIRMINGHAM_DESIGN:
            return designs.drawBirminghamDesign
        elif design is designs.CHEN_DESIGN:
            return  designs.drawChenDesign
        elif design is designs.CHEN_ALT_DESIGN:
            return designs.drawChenAltDesign
        # end if

    # end def

    def getCurrentPositioning(self):
        return self.__positionComboBox.currentIndex()
    # end def

    def getCurrentPathState(self):
        return self.__colourPathCheckBox.isChecked()
    # end def

    def getCurrentThickness(self):
        return self.__thicknessSpinBox.value()
    # end def

    def areSegmentsOn(self):
        return self.__segmentsCheckBox.isChecked()
    # end def

    def connectToCBase(self, widget, slot):
        self.connect( self.__cBaseSpinBox, SIGNAL("valueChanged(double)"), widget, SLOT(slot) )
    # end def

    def connectToCScale(self, widget, slot):
        self.connect( self.__cScaleSpinBox, SIGNAL("valueChanged(double)"), widget, SLOT(slot) )
    # end def

    def connectToHScale(self, widget, slot):
        self.connect( self.__hScaleSpinBox, SIGNAL("valueChanged(double)"), widget, SLOT(slot) )
    # end def

    def connectToFScale(self, widget, slot):
        self.connect( self.__tScaleSpinBox, SIGNAL("valueChanged(double)"), widget, SLOT(slot) )
    # end def

    def connectToPositionComboBox(self, widget, slot):
        self.connect( self.__positionComboBox, SIGNAL("currentIndexChanged(int)"), widget, SLOT(slot) )
    # end def

    def connectToDesignComboBox(self, widget, slot):
        self.connect( self.__designComboBox, SIGNAL("currentIndexChanged(int)"), widget, SLOT(slot) )
    # end def

    def connectToPathColourCheckBox(self, widget, slot):
        self.connect( self.__colourPathCheckBox, SIGNAL("stateChanged(int)"), widget, SLOT(slot) )
    # end def

    def connectToSegmentsCheckBox(self, widget, slot):
        self.connect( self.__segmentsCheckBox, SIGNAL("stateChanged(int)"), widget, SLOT(slot) )
    # end def

    def connectToThicknessSpinBox(self, widget, slot):
        self.connect( self.__thicknessSpinBox, SIGNAL("valueChanged(int)"), widget, SLOT(slot) )
    # end def

# end class