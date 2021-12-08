
import sys

from PyQt4.QtGui import ( QApplication, QMainWindow, QFileDialog, QIcon, QMenu, QAction, QMessageBox, QDesktopWidget,
                          QKeySequence, QPixmap, QGraphicsView, QGraphicsScene, QPainter, QSlider, QDockWidget,
                          QGraphicsPixmapItem, QHBoxLayout, QPushButton, QSpinBox, QDialog, QPen )

from PyQt4.QtCore import ( SIGNAL, SLOT, QString, QFileInfo, Qt, pyqtSlot )

from pycasadata import (SpermContainer)

from glyphview import (PolyLine)

#noinspection PyOldStyleClasses
class VideoDialog(QDialog):

    def __init__(self, parent=None):
        super(VideoDialog,self).__init__(parent)
        self.__myFrameSlider  = QSlider(Qt.Horizontal, self)
        self.__myPlayButton   = QPushButton( QString('play'), self)
        self.__myFrameSpinBox = QSpinBox(self)


        self.connect( self.__myFrameSlider,  SIGNAL("sliderMoved(int)"),
                      self.__myFrameSpinBox, SLOT  ("setValue(int)")     )

        self.connect( self.__myFrameSpinBox, SIGNAL("valueChanged(int)"),
                      self.__myFrameSlider, SLOT  ("setValue(int)") )

        layout = QHBoxLayout()
        layout.addWidget( self.__myPlayButton   )
        layout.addWidget( self.__myFrameSlider  )
        layout.addWidget( self.__myFrameSpinBox )

        self.setLayout(layout)
    # end def

    def setNumberOfFrames(self, value):
        self.__myFrameSlider.setMaximum( value )
        self.__myFrameSpinBox.setMaximum( value )
    # end def

    def frameSlider(self):
        return self.__myFrameSlider
    # end def

    def playButton(self):
        return self.__myPlayButton
    # end def

    def frameSpinBox(self):
        return self.__myFrameSpinBox
    # end def

# end class

#noinspection PyOldStyleClasses
class MainWindow(QMainWindow):

    def __init__(self, parent=None):

        super(MainWindow,self).__init__(parent)

        self.center()
        self.setWindowTitle('Image Browser')
        self.statusBar().showMessage('Ready...', 5000)

        self.__mySpermContainer = SpermContainer()
        self.__myVideoFrames = []
        self.__myCurrentFrame = QGraphicsPixmapItem()

        self.__myView = QGraphicsView(self)

        self.__myVideoDialog = VideoDialog(self)
        self.__myControlDock = QDockWidget( QString('Video Controls'), self )
        self.__myControlDock.setWidget( self.__myVideoDialog )

        self.setupView()

        self.createMenus()

        self.setCentralWidget( self.__myView )
        self.addDockWidget( Qt.BottomDockWidgetArea, self.__myControlDock )
    # end def

    def setupView(self):

        self.__myView.setRenderHint(QPainter.Antialiasing)
        self.__myView.setRenderHint(QPainter.TextAntialiasing)
        self.__myView.setScene( QGraphicsScene() )
        self.resize(800,600)

        self.connect( self.__myVideoDialog.frameSlider(), SIGNAL("sliderMoved(int)"),
                      self, SLOT("slideFrame(int)") )

        self.connect( self.__myVideoDialog.frameSpinBox(), SIGNAL("sliderMoved(int)"),
                      self, SLOT("slideFrame(int)") )
    # end def

    def createMenus(self):
        """
            This function creates all menus, tool bars and actions for the main window widget
        """

        fileOpenImageSequenceAction   = self.createAction( "&Open Image Sequence",
                                                            self.openImageSequence,
                                                            "Ctrl+I",
                                                             None,
                                                            "Load a sequence of images")

        fileOpenAction = self.createAction("&Open Sperm Data",
                                            self.openFile,
                                            QKeySequence.Open,
                                            None,
                                            "Open a sperm file")

        fileCloseAction  = self.createAction( "&Close",
                                              self.closeFile,
                                              QKeySequence.Close,
                                              None,
                                              "Close the current sperm file")

        fileControlAction = self.createAction( "&Control Dialog",
                                               self.showControlDialog,
                                               "Ctrl+D",
                                                None,
                                                "Open the control dialog")
        fileQuitAction   = self.createAction( "&Quit",
                                              self.close,
                                              "Ctrl+Q",
                                              None,
                                              "Quit image browser application" )

        # create menus
        fileMenu = self.menuBar().addMenu("&File")

        # add actions to menus
        self.addActions(fileMenu,  ( fileOpenAction,
                                     fileOpenImageSequenceAction,
                                     fileControlAction,
                                     fileCloseAction,
                                     None,
                                     fileQuitAction ) )
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

        self.statusBar().showMessage('opening file...', 5000)

        path  = QFileInfo( self.__mySpermContainer.getFilename() ).path() \
                if not self.__mySpermContainer.getFilename().isEmpty() else "."

        fName = QFileDialog.getOpenFileName(None, 'Load a sperm file from disk', path,
                                                  'Sperm file (%s)' % self.__mySpermContainer.formats())
        if not fName.isEmpty():
            try:
                ok, msg = self.__mySpermContainer.loadDataSet(fName)
                self.statusBar().showMessage(msg, 5000)
            except (IOError, OSError) as e:
                QMessageBox.warning( None, 'File Load Error', unicode(e))
    # end def

    def showControlDialog(self):
        self.__myControlDock.show()
    # end def

    @staticmethod
    def formats():
        return '*.png'
    # end def

    def openImageSequence(self):
        """
            Read in a sequence of video frames from disk...
        """

        self.statusBar().showMessage('opening image sequence...', 5000)

        # grab a list of video frames from disk, stored in a QStringList
        videoFrameNames = QFileDialog.getOpenFileNames( None,
                                                        'load video sequence',
                                                        '.',
                                                        'Image file (%s)' % self.formats())

        # make sure we have read something in before proceeding
        if not videoFrameNames.isEmpty():

            # if there are old video frames, discard them.
            if len(self.__myVideoFrames):   self.__myVideoFrames = []

            self.__myView.scene().clear()

            # now load the image data from file
            try:
                for frameName in videoFrameNames:
                    print( 'loading frame : %s' % frameName )
                    frame = QPixmap()
                    ok = frame.load( frameName )
                    if ok:  self.__myVideoFrames.append( frame )
                # end for

                # add the frame to the scene
                self.__myVideoDialog.setNumberOfFrames( len(self.__myVideoFrames)-1 )
                self.__myView.scene().addItem( QGraphicsPixmapItem(self.__myVideoFrames[ 0 ] ) )

                # add the polygon representing the flagellum to the scene
                if not self.__mySpermContainer.isEmpty():
                    for sperm in self.__mySpermContainer:
                        frame = sperm.getFrame( 0 )
                        flagellum = PolyLine( frame.capturedFlagellum )
                        flagellum.setPen( QPen( Qt.red, 2.0 ) )
                        self.__myView.scene().addItem( flagellum )
                    # end for
                # end if

            except (IOError, OSError) as e:
                QMessageBox.warning( None, 'File Load Error', unicode(e) )
        # end if

    # end def

    @pyqtSlot(int)
    def slideFrame(self, value):

        listOfItems = self.__myView.scene().items()
        nItems = len(listOfItems)
        #print( 'number of items : %d' % nItems )
        if len(self.__myVideoFrames) != 0:
            listOfItems[nItems-1].setPixmap( self.__myVideoFrames[ value ] )
        # end if

        if not self.__mySpermContainer.isEmpty():

            if nItems > 1:
                for i, sperm in enumerate(self.__mySpermContainer):
                    frame = sperm.getFrame( value )
                    listOfItems[ i ].setPolyLine( frame.capturedFlagellum )
                # end for
            else:
                for i, sperm in enumerate(self.__mySpermContainer):
                    frame = sperm.getFrame( value )
                    flagellum = PolyLine( frame.capturedFlagellum )
                    flagellum.setPen( QPen( Qt.red, 2.0 ) )
                    self.__myView.scene().addItem( flagellum )
            # end for
        # end if

    # end def

    def closeFile(self):
        self.statusBar().showMessage('closing file...', 5000)
        if not self.okToContinue('Are you sure you want to close this file?'):
            return
    # end def

    def closeEvent(self, event):
        """
            Re-implement the closeEvent so if the user accidentally clicks close
            they have an option to cancel the close event
        """
        if self.okToContinue('Are you sure you want to close image browser?'):
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
        return True
        # end def


# end class

def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("OCCAM")
    app.setApplicationName("Image Browser")
    app.setWindowIcon(QIcon('icons/imgbrowser.png'))
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
# end def

if __name__ == '__main__':
    main() # run the main application window