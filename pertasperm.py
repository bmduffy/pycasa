'''
Created on 13 Mar 2012

@author: brian
'''

from __future__ import division # make sure that all division results in floating point numbers

from PyQt4.QtGui       import ( QMatrix )
from PyQt4.QtCore      import ( Qt, QObject, QPointF, QRegExp, QFile, QIODevice, QTextStream, QString )
from pycasadata        import ( CODEC, intFromQString, floatFromQString )
from random            import ( uniform  )
from geometry          import ( midpoint )
from math              import ( pi, sin  )
from copy              import ( deepcopy )  
from computation       import ( smooth, fitSpline )

class Sperm(QObject):
    '''
        The Sperm class holds all of the data about an individual sperm.
    '''
        
    def __init__(self, filename=None, parent=None):
        super(Sperm,self).__init__(parent)
        
        self.centroids = []; self.tcerts = []
        self.heads     = []; self.hcerts = []
        self.flagella  = []; self.fcerts = []
        self.lengths   = []; self.widths = [];
        self.centres   = []; self.tilts =  [];
        self.frameIDs  = []
        
        if filename is not None:
            ok, msg = self.loadSperm(filename)
            if not ok:
                print msg
                raise IOError, "IOError opening : %s " % (filename)
            # end if
        # end if
    # end def        
    def __len__(self):
        return len(self.frames)
    # end def
    
    def loadSperm( self, filename ):
        '''
            This function loads the basic data captured about the sperms motion from file.
            Due to the format of the file the data is stored in intermediate data structures
        '''
        exception = None
        
        try:
            infile = QFile(filename)
            if not infile.open(QIODevice.ReadOnly):
                raise IOError, "IOError opening : %s" % (filename)
            stream = QTextStream(infile)
            stream.setCodec( CODEC ) # set the codec to UTF-8
    
            print "processing : %s" % (filename)
            
            # in the main loop active the subroutines when the tags are found
            while not stream.atEnd():
                line = self.__nomNomNom(stream)
                if line.startsWith("["): # it is a tag and some useful data follows
                    if   QRegExp(r"\[HEADER\]", Qt.CaseInsensitive).exactMatch(line):
                        print "reading header info..."
                        self.__readHeader(stream)
                    elif QRegExp(r"\[CENTROID\]", Qt.CaseInsensitive).exactMatch(line):
                        print "reading centroids..."
                        self.__readCentroids(stream, self.frameIDs, self.centroids, self.tcerts)
                    elif QRegExp(r"\[HEADELLIPSE\]", Qt.CaseInsensitive).exactMatch(line):
                        print "reading head ellipses..."
                        self.__readEllipses(stream, self.lengths, self.widths, self.centres, self.tilts)
                    elif QRegExp(r"\[HEAD\]", Qt.CaseInsensitive).exactMatch(line) or \
                         QRegExp(r"\[HEADPOINTS\]", Qt.CaseInsensitive).exactMatch(line):
                        print "reading head points..."
                        self.__readFormatData(stream, self.heads, self.hcerts)
                    elif QRegExp(r"\[FLAGELLUM\]", Qt.CaseInsensitive).exactMatch(line):
                        print "reading flagella points..."
                        self.__readFormatData(stream, self.flagella, self.fcerts)
                        print "finished"
                    elif QRegExp(r"\[END\]", Qt.CaseInsensitive).exactMatch(line):
                        # print "early termination with [END] tag"
                        break
                else:
                    print "this line shouldn't happen", line
                    # if it is not one of the above cases then there is something wrong
                    raise IOError, "IOError reading from : %s " % (filename) 
            # end while
            print "done..."
        
            # fit a cubic spline to the flagella
            print "fitting flagella with cubic spline"
            last_good_flagellum = []
            N = len(self.flagella)
            for i in range(N):
                if len(self.flagella[i]) > 1:
                    self.flagella[i] = fitSpline(self.flagella[i], 10.0, 3)
                    last_good_flagellum = self.flagella[i]
                else:
                    self.flagella[i] = last_good_flagellum
                # end if
            # end for
            print "done fitting..."
            
            print "done..."
            
        except( IOError, IndexError, TypeError, ValueError, KeyError  ), e:
            exception = e
            print "exception caught @ loadSperm, of type : ", type(e)
        finally:
            if exception is None:
                return (True, "File : %s loaded successfully" % (filename) ) 
            else:
                return (False, "File : %s exception of type <%s> raised" % (filename, exception) ) 
            # end if
        # end except
    # end def
    
    def saveSperm( self, number, path ):
        exception = None
        outfile   = None
        filename = path + QString( "sperm%d.spm" % (number) )
        
        try:
            outfile = QFile(filename)
            if not outfile.open(QIODevice.WriteOnly):
                raise IOError, "IOError opening for writing: %s" % (filename)
            stream = QTextStream(outfile)
            stream.setCodec( CODEC ) # set the codec to UTF-8
            N = len(self.frameIDs)
            print "sperm : %d" % (number)
            stream << "[HEADER]\n"
            print "writing header..."
            stream << "SpermID = " << number << "\n\n"
            stream << "[CENTROID]\n"
            print "writing centroids..."
            for i in range(N):
                c = self.centroids[i] 
                stream << self.frameIDs[i] << "," << self.tcerts[i] << "," << c.x() << "," << c.y() << "\n" 
            # end 
            stream << "\n\n"
            
            stream << "[HEAD]\n"
            print "writing head information..."
            self.__saveFormatData(stream, self.frameIDs, self.heads, self.hcerts)
            stream << "\n\n"
            
            stream << "[HEADELLIPSE]\n"
            print "writing head ellipses..."
            for i in range(N):
                l = self.lengths[ i ]
                w = self.widths [ i ]
                c = self.centres[ i ]
                t = self.tilts  [ i ]
                stream << self.frameIDs[i] << "," << l << "," << w << "," \
                                           << c.x() << "," << c.y() << "," << t << "\n"
            # end for
            stream << "\n\n"

            stream << "[FLAGELLUM]\n"
            print "writing flagellum information..."
            self.__saveFormatData(stream, self.frameIDs, self.flagella, self.fcerts)
            print "finished writing file..."
            stream << "[END]\n"
        except( IOError, KeyError ), e:
            exception = e
            print "exception caught @ loadSperm, of type : ", type(e)
        finally:
            if exception is None:
                return (True, "File : %s loaded successfully" % (filename) ) 
            else:
                return (False, "File : %s exception of type <%s> raised" % (filename, exception) )
            # end if 
        # end try
    # def 

    def transform(self,  x,y, theta, scaling):
        T = QMatrix()
        T.translate(x, y)
        R = QMatrix()
        R.rotate(theta)
        S = QMatrix()
        S.scale(scaling, scaling)
        N = len(self.frameIDs)
        midPath = midpoint( self.centroids[0], self.centroids[-1])
        toO = QMatrix()
        toO.translate(-midPath.x(),-midPath.y())
        fromO = QMatrix()
        fromO.translate(midPath.x(),midPath.y())
        for i in range(N):
            self.centroids[i] = T.map(S.map(fromO.map(R.map(toO.map(self.centroids[i])))))
            self.centres[i]   = T.map(S.map(fromO.map(R.map(toO.map(self.centres[i])))))
            for hpt in self.heads[i]:
                hpt += T.map(S.map(fromO.map(R.map(toO.map(hpt)))))
            # end for
            for fpt in self.flagella[i]:
                fpt += T.map(S.map(fromO.map(R.map(toO.map(fpt)))))
            # end for
        # end for
    # end def
    
    def random(self, a, b):
        N = len(self.frameIDs)
        for i in range(N):
            self.centroids[i] += QPointF(uniform(a,b),uniform(a,b))
            self.centres[i]   += QPointF(uniform(a,b),uniform(a,b))
            for hpt in self.heads[i]:
                hpt += QPointF(uniform(a,b),uniform(a,b))
            # end for
            for fpt in self.flagella[i]:
                fpt += QPointF(uniform(a,b),uniform(a,b))
            # end for
        # end for
    # end def
    
    def curve(self, amplitude, frequency, start = 0.0):
        theta = start
        N = len(self.frameIDs)
        delta = (2.0 * pi)/float(N)
        curve = []
        while theta <= start + (2.0 * pi) :
            curve.append(amplitude*sin( theta * frequency ))
            theta += delta
        # end while
        for i in range(N):
            self.centroids[i] += QPointF(curve[i],curve[i])
            self.centres[i]   += QPointF(curve[i],curve[i])
            for hpt in self.heads[i]:
                hpt += QPointF(curve[i],curve[i])
            # end for
            for fpt in self.flagella[i]:
                fpt += QPointF(curve[i],curve[i])
            # end for
        # end for
    # end def
    
    def smoothed(self, window_len):
        self.centroids = smooth(self.centroids, window_len, 'tukey')
    # def
    
    #  eats up comments and white space but spits out useful data
    def __nomNomNom(self, stream):
        '''
            This helper method is private and is used to consume unwanted whitespaces and comments
        '''
        line = stream.readLine()
        while not stream.atEnd() and (line.startsWith("#") or line.startsWith("%") or line.isEmpty()):
            line = stream.readLine()
        # end while
        return line
    # end def
    
    def __readHeader(self, stream):
        '''
            This subroutine grabs the header information form the file
            so far this is just
        '''
        line = self.__nomNomNom(stream)
        if QRegExp(r"SpermID").exactMatch(line):
            lst = line.split("=")
            self.__spermID = intFromQString(lst[1])
        # end if
    # end def
    
    def __readCentroids(self, stream, frameIDs, data, tracking):
        # eat everything between the tag and the data
        line = self.__nomNomNom(stream)
        while not line.isEmpty():
            #  print line
            lst = line.split(",")
            frameID = intFromQString  ( lst[0] )
            tracked = floatFromQString( lst[1] )
            xcoord  = floatFromQString( lst[2] )
            ycoord  = floatFromQString( lst[3] )
            # put the (frameID, Point) in a tuple to group them
            frameIDs.append(frameID)
            data.append(QPointF(xcoord, ycoord))
            tracking.append(tracked)
            line = stream.readLine()
        # end while
    # end def
    
    def __readEllipses(self, stream,  lengths, widths, centres, tilts):
        # eat everything between the tag and the data
        line = self.__nomNomNom(stream)
        while not line.isEmpty():
            lst = line.split(",")
            length  = floatFromQString ( lst[1] )
            width   = floatFromQString ( lst[2] )
            xcoord  = floatFromQString ( lst[3] )
            ycoord  = floatFromQString ( lst[4] )
            tilt    = floatFromQString ( lst[5] )
            
            lengths.append( length )
            widths.append( width )
            centres.append( QPointF( xcoord, ycoord ) )
            tilts.append( tilt )
            
            line = stream.readLine()
        # end while 
    # end def
    
    def __readFormatData(self, stream, data, certainty):
        # eat everything between the tag and the data
        line = self.__nomNomNom(stream)
        # process head information until we have none left 
        while not line.isEmpty():
            # print line
            lst = line.split(",")
            certain = floatFromQString(lst[1])
            nPoints = intFromQString  (lst[2])
            points = []
            for i in xrange(nPoints):
                try:
                    xcoord = floatFromQString( lst[3 + 2*i]     )
                    ycoord = floatFromQString( lst[3 + 2*i + 1] )
                    points.append( QPointF(xcoord, ycoord) )
                except IndexError:
                    raise IndexError, "IndexError <index out of bounds>"
                # end try
            # end for
            data.append( points )   # points to the collection
            certainty.append( certain )  # add the certainty to the collection
            line = stream.readLine()
        # end while
    # end def
    
    def __saveFormatData(self, stream, frameIDs, data, certainty):
        N = len(frameIDs)
        for i in range(N):
            c = certainty[i]
            nPoints = len(data[i])
            stream << frameIDs[i] << "," << c << "," << nPoints
            for point in data[i]:
                stream << "," << point.x() << "," << point.y()
            # end for
            stream << "\n"
        # end for
        stream << "\n\n"
    # end def 
# end class

if __name__ == '__main__':
    
    source = QString("/home/brian/Dropbox/python/pycasa/data/set2/set2_sperm1.txt")
    path = QString("/home/brian/Dropbox/python/pycasa/data/synthetic_multi_sperm/")
    template = Sperm(source)
    
    sp1 = deepcopy(template)
    sp1.transform(0.0,0.0,-90.0,1.0)
    sp1.saveSperm(1,path)
    
    sp2 = deepcopy(template)
    sp2.transform(50.0, -50.0, 45.0, 1.1 )
    sp2.saveSperm(2,path)
    
    sp3 = deepcopy(template)
    sp3.transform(-200.0,-60.0, 0.0, 1.3 )
    sp3.random(-0.4,0.4)
    sp3.saveSperm(3,path)
    
    sp4 = deepcopy(template)
    sp4.transform( -50.0, 30.0, -110.0, 1.1 )
    sp4.random(-0.5, 0.5)
    sp4.saveSperm(4,path)
    
    sp5 = deepcopy(template)
    sp5.transform( -230.0, -100.0, 180.0, 1.3 )
    sp5.curve(10.0, 0.5, 0.5)
    sp5.saveSperm(5,path)
    
    sp6 = deepcopy(template)
    sp6.transform( 20.0, -150.0, 10.0, 1.5 )
    sp6.smoothed(100)
    sp6.curve(15.0, 1.0, 0.25)
    sp6.saveSperm(6,path)
    
    sp7 = deepcopy(template)
    sp7.transform( -180.0, -140.0, 25.0, 1.8 )
    sp7.smoothed(50)
    sp7.curve(50.0, 0.5, 0.5)
    sp7.saveSperm(7,path)
    
    sp8 = deepcopy(template)
    sp8.transform( 60.0, -80.0, -35.0, 0.75 )
    sp8.curve(90, 0.5, 0.0)
    sp8.saveSperm(8,path)
    
    sp9 = deepcopy(template)
    sp9.transform( 100.0, -30.0, 0.0, 0.5 )
    sp9.curve(10.0, 1.0, 0.0)
    sp9.saveSperm(9,path)
    
    sp10 = deepcopy(template)
    sp10.transform( 250.0, 80.0, 0.0, 0.0 )
    sp10.saveSperm(10,path)
    
    sp11 = deepcopy(template)
    sp11.transform(-150.0,-60.0, 0.45, 1.2 )
    sp11.smoothed(200)
    sp11.curve(12.0, 2.0, 0.5)
    sp11.random(-0.1,0.1)
    sp11.saveSperm(11,path)
    
# end if
    