"""
Created on 8 Feb 2012

@author: Brian Duffy

this is the main window of the application created using PyQt4
"""

import sys

from PyQt4.QtGui import (QApplication, QMainWindow, QFileDialog, QIcon, QMenu, QAction, QMessageBox, QDesktopWidget,
                         QKeySequence, QPixmap, QDialog, QGridLayout, QTabWidget)

from PyQt4.QtCore import (SIGNAL, QString, QFileInfo, QSize)

from glyphview import (GlyphView)
from pycasadata import (SpermContainer)
from timeseries import (timeSeries, timeSeriesAll)
from parallelcoordinates import (ParallelCoordinates, Axis)
from dialogs import ( GlyphControlDialog )
from glyphdesigns import(CHEN_DESIGN, AVERAGE_POSITION)


#noinspection PyOldStyleClasses
class MainWindow(QMainWindow):

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)

        self.__mySpermContainer = SpermContainer()
        self.glyphControlDialog = GlyphControlDialog(20.0, 4.5, 4.0, 1.5, 2, CHEN_DESIGN, AVERAGE_POSITION,  self)

        self.__myGlyphView      = GlyphView(self.__mySpermContainer, self.glyphControlDialog, self)
        self.__display = GlyphView.GLYPH_VIEW
        self.setCentralWidget( self.__myGlyphView )
        self.center()
        self.setWindowTitle('PyCASA ~o')
        self.statusBar().showMessage('Ready...', 5000)

        self.__myGlyphView.update()
        self.createMenus()
    # end def
        
    def createMenus(self):
        """
            This function creates all menus, tool bars and actions for the main window widget
        """
        
        fileOpenAction   = self.createAction( "&Open", self.openFile, QKeySequence.Open, None, "Open a sperm file")
        fileCloseAction  = self.createAction( "&Close", self.closeFile, QKeySequence.Close, None,
                                              "Close the current sperm file")
        fileQuitAction   = self.createAction( "&Quit", self.close, "Ctrl+Q", None, "Quit PyCASA application")
        screenShotAction = self.createAction( "&Screen Shot", self.captureScene, "Ctrl+P", None,
                                              "Take a screen shot of the scene")

        self.glyphDisplayAction = self.createAction("&Glyphs", self.displayGlyphs, "Display the glyphs", True)
        self.glyphDisplayAction.setChecked(True)
        self.spermDisplayAction   = self.createAction("&Sperms", self.displaySperms, "Display sperm geometry", True)
        self.pathDisplayAction    = self.createAction("&Paths",  self.displayPaths,  "Display CASA like paths", True)
        self.summaryDisplayAction = self.createAction("&Summary", self.displaySummary, "Display Summary Glyph", True)

        self.toggleGridAction = self.createAction("&Grid", self.toggleGrid, "Toggle the grid on or off", True)
        self.toggleGridAction.setChecked(True)

        self.setGlyphControlAction = self.createAction("&Glyph Controls", self.showControlDialog, "Show the control dialog")

        timeSeriesAction = self.createAction( "&Time Series", self.displayTimeSeries,
                                              "Display the time series data for the sperms")
        parallelCoordinatesAction = self.createAction( "&Parallel Coordinates", self.displayParallelCoordinates,
                                                       "Display parallel coordinates of the sperm data")

        # create menus
        fileMenu = self.menuBar().addMenu("&File")
        viewMenu = self.menuBar().addMenu("&View")
        toolMenu = self.menuBar().addMenu("&Tools")
        otherMenu = self.menuBar().addMenu("&Other")
        #helpMenu = self.menuBar().addMenu("&Help")
        
        # add actions to menus 
        self.addActions(fileMenu,  ( fileOpenAction, fileCloseAction, None, fileQuitAction ) )
        self.addActions(viewMenu,  ( self.glyphDisplayAction, self.spermDisplayAction,
                                     self.pathDisplayAction, self.summaryDisplayAction ) )
        self.addActions(toolMenu,  ( screenShotAction, None, self.toggleGridAction, self.setGlyphControlAction ) )
        self.addActions(otherMenu, ( timeSeriesAction, parallelCoordinatesAction ) )

        # set up the glyph control dialog

        self.glyphControlDialog.connectToCBase ( self.__myGlyphView, "cBaseChanged(double)"  )
        self.glyphControlDialog.connectToCScale( self.__myGlyphView, "cScaleChanged(double)" )
        self.glyphControlDialog.connectToHScale( self.__myGlyphView, "hScaleChanged(double)" )
        self.glyphControlDialog.connectToFScale( self.__myGlyphView, "tScaleChanged(double)" )

        self.glyphControlDialog.connectToDesignComboBox  ( self.__myGlyphView, "designChanged(int)"   )
        self.glyphControlDialog.connectToPositionComboBox( self.__myGlyphView, "positionChanged(int)" )

        self.glyphControlDialog.connectToPathColourCheckBox( self.__myGlyphView, "toggleColourPath(int)"   )
        self.glyphControlDialog.connectToSegmentsCheckBox  ( self.__myGlyphView, "toggleSegmentsOn(int)" )

        self.glyphControlDialog.connectToThicknessSpinBox( self.__myGlyphView, "thicknessChanged(int)")
    # end def 
    
    def changeRendering(self,value):
        self.__display = value
        #self.updateVis()
    # end def
    
    def addActions(self, target, actions):
        """
            Helper function for adding actions to a specified widget, cuts down on code
        """
        for action in actions:
            if action is None:
                target.addSeparator()
            elif isinstance(action, QMenu):
                target.addMenu(action)
            else:
                target.addAction(action)
            # end if
        # end for
    # end def
        
    def createAction(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
        """
            Helper function for creating actions, cuts down on code
        """
        action = QAction(text, self)

        if icon     is not None:  action.setIcon( QIcon(":/%s.png" % icon)  )
        if shortcut is not None:  action.setShortcut(shortcut)
        if slot     is not None:  self.connect(action,SIGNAL(signal),slot)
        if checkable:             action.setCheckable(True)

        if tip      is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        # end if

        return action

    # end def
        
    def openFile(self):
        """
            High level method for opening file. The responsibility of manipulating the pycasa
            files calls to the SpermContainer object. This high level method allows this object
            to interface with the file and catch any exceptional behaviour
        """
        self.statusBar().showMessage('opening file...', 5000)
        path  = QFileInfo(self.__mySpermContainer.getFilename()).path() \
                          if not self.__mySpermContainer.getFilename().isEmpty() else "."

        fName = QFileDialog.getOpenFileName(None, "Load a sperm file from disk", path,
                                            "Sperm file (%s)" % self.__mySpermContainer.formats())
        if not fName.isEmpty():
            try:
                ok, msg = self.__mySpermContainer.loadDataSet(fName)
                self.statusBar().showMessage(msg, 5000)
                if ok:
                    self.__myGlyphView.update()
            except (IOError, OSError) as e:
                QMessageBox.warning( None, "File Load Error ", unicode(e))
    # end def
        
    def closeFile(self):
        self.statusBar().showMessage('closing file...', 5000)
        if not self.okToContinue('Are you sure you want to close this file?'):
            return
        # assign a fresh sperm container, the old sperm container will be garbage collected
        self.spermContainer = SpermContainer()
        self.__myGlyphView.clear()
    # end def

    def closeEvent(self, event):
        """
            Re-implement the closeEvent so if the user accidentally clicks close
            they have an option to cancel the close event
        """
        if self.okToContinue('Are you sure you want to close PyCasa?'):
            event.accept()
        else:
            event.ignore()
    # end def

    def okToContinue(self, message):
        """
            This helper creates a standard QMessageBox with a specified message, i.e. a dumb dialog.
            It returns a boolean indicating the users response to the message.
            A simple wrapper function to cut down on code
        """
        reply = QMessageBox.question(self, "Message", message, QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            return True
        else:
            return False
    # end def
    
    def center(self):
        """
            This is a helper method that centres the Qt window in the desktop
        """
        widget  = self.frameGeometry()
        desktop = QDesktopWidget().availableGeometry().center()
        widget.moveCenter(desktop)
        self.move(widget.topLeft())
    # end def
    
    @staticmethod
    def imageFormats():
        return "*.png *.bmp *.jpg *.jpeg *.ppm"
    # end def 
    
    def captureScene(self):
        oFile = QString("")
        oFile = QFileDialog.getSaveFileName( None, "Save Screen Capture",
                                             oFile, "Image Formats(%s)" % self.imageFormats() )
        
        if oFile.isEmpty() :
            self.statusBar().showMessage("no save file specified", 5000)
            return False
        # end if

        zoomFactor = 3.0

        oldSize = self.size()
        tempSize = QSize( oldSize.width()*zoomFactor , oldSize.height()*zoomFactor  )

        self.resize( tempSize )
        self.__myGlyphView.scale( zoomFactor, zoomFactor )

        image = QPixmap.grabWidget(self.__myGlyphView)
            
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

        self.__myGlyphView.scale( 1.0/zoomFactor ,1.0/zoomFactor )
        self.resize( oldSize )

        return True

    # end def

    def displayGlyphs(self):
        self.__myGlyphView.setViewMode( GlyphView.GLYPH_VIEW )
        self.glyphDisplayAction.setChecked(True)
        self.pathDisplayAction.setChecked(False)
        self.spermDisplayAction.setChecked(False)
        self.summaryDisplayAction.setChecked(False)
    # end def

    def displaySperms(self):
        self.__myGlyphView.setViewMode( GlyphView.SPERM_VIEW )
        self.glyphDisplayAction.setChecked(False)
        self.pathDisplayAction.setChecked(False)
        self.spermDisplayAction.setChecked(True)
        self.summaryDisplayAction.setChecked(False)
    # end def

    def displayPaths(self):
        self.__myGlyphView.setViewMode( GlyphView.PATH_VIEW )
        self.glyphDisplayAction.setChecked(False)
        self.pathDisplayAction.setChecked(True)
        self.spermDisplayAction.setChecked(False)
        self.summaryDisplayAction.setChecked(False)
    # end def

    def displaySummary(self):
        self.__myGlyphView.setViewMode( GlyphView.SUMMARY_VIEW)
        self.glyphDisplayAction.setChecked(False)
        self.pathDisplayAction.setChecked(False)
        self.spermDisplayAction.setChecked(False)
        self.summaryDisplayAction.setChecked(True)
    # end def

    def toggleGrid(self):
        state = self.__myGlyphView.toggleGrid()
        self.toggleGridAction.setChecked(state)
    # end def

    def displayTimeSeries(self):
        print('rendering time series of the data...')
        id = 1
        for sperm in self.__mySpermContainer:
            if sperm.getNumberOfGlyphs() < 1.0:
                id += 1
                continue
            # end if
            timeSeriesAll(sperm, id)
            id += 1
        # end for
    # end def

    def displayParallelCoordinates(self):
        print('rendering parallel coordinates...')

        if self.__mySpermContainer.isEmpty():  return

        # we will have a parallel coordinates plot for each time step
        spermIDs      = []
        uncertainties = []
        VCLs = []; VAPs = []; VSLs =[]; WOBs=[]; LINs = []; STRs = []; ALHs = []; BCFs = []; MADs = []
        headLengths = []; headWidths = []; headAngles =[]; arcLengths = []; asymmetries =[]; torques = []
        changesInAngles = []
        id = 1

        tabs = QTabWidget()

        for sperm in self.__mySpermContainer:
            if sperm.getNumberOfGlyphs() < 1.0:
                id += 1
                continue
            # end if
            spermIDs.append(id)
            uncertainties.append( sperm.getAvgUncertainty() )
            VCLs.append( sperm.getAvgVCL() )
            VAPs.append( sperm.getAvgVAP() )
            VSLs.append( sperm.getAvgVSL() )
            WOBs.append( sperm.getAvgWOB() )
            LINs.append( sperm.getAvgLin() )
            STRs.append( sperm.getAvgSTR() )
            ALHs.append( sperm.getAvgALH() )
            BCFs.append( sperm.getAvgBCF() )
            MADs.append( sperm.getAvgMAD() )
            headLengths.append( sperm.getAvgHeadLength() )
            headWidths.append( sperm.getAvgHeadWidth() )
            headAngles.append( sperm.getAvgHeadAngle() )
            arcLengths.append( sperm.getAvgArcLength() )
            asymmetries.append( sperm.getAvgAsymmetry(True) )
            torques.append( sperm.getAvgTorques(True) )
            changesInAngles.append( sperm.getAvgChangeInAngle() )
            id += 1
        # end for

        avgPC = ParallelCoordinates( QString('Average Parameter Values'), 255 )
        avgPC.addAxis( Axis('ID', int, spermIDs ) )
        avgPC.addAxis( Axis('UC', float, uncertainties) )
        avgPC.addAxis( Axis('VCL', float, VCLs) )
        avgPC.addAxis( Axis('VAP', float, VAPs) )
        avgPC.addAxis( Axis('VSL', float, VSLs) )
        avgPC.addAxis( Axis('WOB', float, WOBs) )
        avgPC.addAxis( Axis('LIN', float, LINs) )
        avgPC.addAxis( Axis('STR', float, STRs) )
        avgPC.addAxis( Axis('ALH', float, ALHs) )
        avgPC.addAxis( Axis('BCF', float, BCFs) )
        avgPC.addAxis( Axis('MAD', float, MADs) )
        avgPC.addAxis( Axis('HL', float, headLengths) )
        avgPC.addAxis( Axis('HW', float, headWidths)  )
        avgPC.addAxis( Axis('HA', float, headAngles)  )
        avgPC.addAxis( Axis('FTA', float, arcLengths) )
        avgPC.addAxis( Axis('FTC', float, changesInAngles) )
        avgPC.addAxis( Axis('FTT', float, torques) )
        avgPC.addAxis( Axis('FAS', float, asymmetries))

        tabs.addTab( avgPC, QString('AVG') )
        #avgPC.captureScene( QString('averageParallelCoordinatesValues.png') )
        avgPC.writeSTFFile('averageSperms.stf')

        # now do the same except for each time step

        for t in range(self.__mySpermContainer.getMaxNumberOfGlyphs()):
            spermIDs      = []
            uncertainties = []
            VCLs = []; VAPs = []; VSLs =[]; WOBs=[]; LINs = []; STRs = []; ALHs = []; BCFs = []; MADs = []
            headLengths = []; headWidths = []; headAngles =[]; arcLengths = []; asymmetries =[]; torques = []
            changesInAngles = []
            id = 1
            for sperm in self.__mySpermContainer:
                # end if
                spermIDs.append(id)
                if sperm.getUncertainty(t) is not None : uncertainties.append( sperm.getUncertainty(t) )
                else        : uncertainties.append( 0.0 )
                if sperm.getVCL(t) is not None : VCLs.append( sperm.getVCL(t) )
                else        : VCLs.append( 0.0 )
                if sperm.getVAP(t) is not None : VAPs.append( sperm.getVAP(t) )
                else        : VAPs.append( 0.0 )
                if sperm.getVSL(t) is not None : VSLs.append( sperm.getVSL(t) )
                else        : VSLs.append( 0.0 )
                if sperm.getWOB(t) is not None : WOBs.append( sperm.getWOB(t) )
                else        : WOBs.append( 0.0 )
                if sperm.getLIN(t) is not None : LINs.append( sperm.getLIN(t) )
                else        : LINs.append( 0.0 )
                if sperm.getSTR(t) is not None : STRs.append( sperm.getSTR(t) )
                else        : STRs.append( 0.0 )
                if sperm.getALH(t) is not None : ALHs.append( sperm.getALH(t) )
                else        : ALHs.append( 0.0 )
                if sperm.getBCF(t) is not None : BCFs.append( sperm.getBCF(t) )
                else        : BCFs.append( 0.0 )
                if sperm.getMAD(t) is not None : MADs.append( sperm.getMAD(t) )
                else        : MADs.append( 0.0 )
                if sperm.getHeadLength(t) is not None: headLengths.append( sperm.getHeadLength(t) )
                else        : headLengths.append( 0.0 )
                if sperm.getHeadWidth(t) is not None : headWidths.append( sperm.getHeadWidth(t) )
                else        : headWidths.append( 0.0 )
                if sperm.getHeadAngle(t) is not None : headAngles.append( sperm.getHeadAngle(t) )
                else        : headAngles.append( 0.0 )
                if sperm.getArcLength(t) is not None : arcLengths.append( sperm.getArcLength(t) )
                else        : arcLengths.append( 0.0 )
                if sperm.getAsymmetry(t) is not None : asymmetries.append( sperm.getAsymmetry(t,True) )
                else        : asymmetries.append( 0.0 )
                if sperm.getTorque(t) is not None : torques.append( sperm.getTorque(t,True) )
                else        : torques.append( 0.0 )
                if sperm.getChangeInAngle(t) is not None : changesInAngles.append( sperm.getChangeInAngle(t) )
                else        : changesInAngles.append( 0.0 )
                id += 1
            # end for
            pc = ParallelCoordinates( QString('Time Step %d' % t), 255, )
            pc.addAxis( Axis('ID', int, spermIDs ) )
            pc.addAxis( Axis('UC', float, uncertainties) )
            pc.addAxis( Axis('VCL', float, VCLs) )
            pc.addAxis( Axis('VAP', float, VAPs) )
            pc.addAxis( Axis('VSL', float, VSLs) )
            pc.addAxis( Axis('WOB', float, WOBs) )
            pc.addAxis( Axis('LIN', float, LINs) )
            pc.addAxis( Axis('STR', float, STRs) )
            pc.addAxis( Axis('ALH', float, ALHs) )
            pc.addAxis( Axis('BCF', float, BCFs) )
            pc.addAxis( Axis('MAD', float, MADs) )
            pc.addAxis( Axis('HL', float, headLengths) )
            pc.addAxis( Axis('HW', float, headWidths)  )
            pc.addAxis( Axis('HA', float, headAngles)  )
            pc.addAxis( Axis('FTA', float, arcLengths) )
            pc.addAxis( Axis('FTC', float, changesInAngles) )
            pc.addAxis( Axis('FTT', float, torques) )
            pc.addAxis( Axis('FAS', float, asymmetries))
            tabs.addTab( pc, QString('T%d' % t) )
            #pc.captureScene( QString('pcsperm%d.png' % t) )
        # end for

        dialog = QDialog(self)
        dialog.setWindowTitle('Parallel Coordinates')
        dialog.setLayout( QGridLayout() )
        dialog.layout().addWidget(tabs)
        dialog.show()
        print('done rendering parallel coordinates...')

    # end def

    def showControlDialog(self):
        self.glyphControlDialog.show()
    # end def

# end class
        
def main():
    print('~o ~o ~o Welcome to PyCASA ~o ~o ~o')
    app = QApplication(sys.argv)
    app.setOrganizationName("OCCAM")
    app.setApplicationName("PyCASA~o")
    app.setWindowIcon(QIcon('icons/pycasa_icon.png'))
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
# end def 
    
if __name__ == '__main__':
    main() # run the main application window
