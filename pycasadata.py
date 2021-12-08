"""
    This module handles all of the sperm data down the video frames
"""

from PyQt4.QtCore import (Qt, QPointF, QString, QRegExp, QFile, QFileInfo, QIODevice, QTextStream)

from computation import (straightLineVelocity, smooth, hanning, average, averageVelocity, averagePosition,
                         averageVector, meanAngularDensity, averageArcLength, averageChangeInAngle,
                         averageAsymmetry, averageTorque, amplitudes, fitSpline, intersectPoints)

from geometry import (toVector, midpoint)

from glyphdesigns import (START_POSITION, MIDDLE_POSITION, END_POSITION, AVERAGE_POSITION, MIDPOINT_POSITION)

### Global Variables

CODEC = "UTF-8"

maxAsymmetry = 8000.0
maxTorque = 3500000.0
maxBCF = 30.0

FRAMES_PER_SECOND = 1.0
PIXEL_SCALE = 1.0
VISCOSITY_VALUE = 1.0


def convertToNMS(value):
    """
        Return value converted to nano meters per second  mu/sec.
    """
    global FRAMES_PER_SECOND, PIXEL_SCALE
    dt = 1.0 / FRAMES_PER_SECOND
    return (value * PIXEL_SCALE) / dt


def convertToNM(value):
    """
        Return value converted to nano meters.
    """
    global PIXELS_SCALE
    return value * PIXEL_SCALE


def convertToSeconds(frame):
    """
        Return frame number converted to second
    """
    global FRAMES_PER_SECOND
    dt = 1.0 / FRAMES_PER_SECOND
    return frame * dt


def convertFromSeconds(seconds):
    """
        Return seconds converted to the closest frame number
    """
    global FRAMES_PER_SECOND
    dt = 1.0 / FRAMES_PER_SECOND
    return int(seconds / dt)


def temporalRanges(start, end, step):
    """
        Return a list of tuples representing the temporal boundaries
    """
    temporal = []

    t1 = start
    t2 = start + step

    while t2 < end:
        temporal.append((t1, t2))
        t1 = t2
        t2 += step

    temporal.append((t1, end))

    return temporal


def convertToFrameRanges(temporal):
    frames = []

    for t in temporal:
        frames.append((convertFromSeconds(t[0]), convertFromSeconds(t[1])))

    return frames


def intFromQString(string):
    """
        Return a integer conversion of a QString object.
    """

    i, ok = string.toInt()

    if not ok:
        raise ValueError('ValueError converting : %s' % string)

    return i


def floatFromQString(string):
    """
        Return a floating point conversion of a QString object.
    """
    f, ok = string.toFloat()

    if not ok:
        raise ValueError('ValueError converting : %s' % string)

    return f


def doubleFromQString(string):
    """
        Return a double precision floating point conversion of a QString object.
    """

    d, ok = string.toDouble()

    if not ok:
        raise ValueError('ValueError converting : %s' % string)

    return d


class Frame:
    """
        Each Frame holds information about the head position and flagellum position
    """

    def __init__(self):
        self.frameID = 0.0
        self.centroid = QPointF(0.0, 0.0)
        self.head = [QPointF(0.0, 0.0)]
        self.length = 0.0
        self.centre = QPointF(0.0, 0.0)
        self.tilt = 0.0
        self.width = 0.0
        self.flagellum = [QPointF(0.0, 0.0)]
        self.capturedFlagellum = [QPointF(0.0, 0.0)]
        self.tCert = 0.0
        self.hCert = 0.0
        self.fCert = 0.0

    def setFrameID(self, frameID):
        self.frameID = frameID

    def getCentroid(self):
        return self.centroid

    def load(self, frameID, centroid, head, length, width, centre,
             tilt, capturedFlagellum, flagellum, tCert, hCert, fCert):
        self.frameID = frameID
        self.centroid = centroid
        self.head = head
        self.length = length
        self.centre = centre
        self.tilt = tilt
        self.width = width
        self.flagellum = flagellum
        self.capturedFlagellum = capturedFlagellum
        self.tCert = tCert
        self.hCert = hCert
        self.fCert = fCert

    def jsonObjectFormat(self):
        return '{ \"frameID\" : %d\n' \
               '  \"x\"       : %d\n' \
               '  \"y\"       : %d }' % (self.frameID, self.centroid.x(), self.centroid.y())

    def __cmp__(self, other):
        return cmp(self.frameID, other.frameID)

    def __repr__(self):
        return "Frame( id : %d, centroid : [%.2f,%.2f], \
                                certainty : %.2f, head size : %d, \
                                length : %.2f, width : %.2f \
                                certainty : %.2f, flagellum size : %d, certainty : %.2f)" \
               % (self.frameID, self.centroid.x(), self.centroid.y(), self.tCert,
                  len(self.head), self.length, self.width, self.hCert, len(self.flagellum), self.fCert)

    def __str__(self):
        return "Frame( id : %d, centroid : [%.2f,%.2f], \
                                certainty : %.2f, head size : %d, \
                                length : %.2f, width : %.2f \
                                certainty : %.2f, flagellum size : %d, certainty : %.2f)" \
               % (self.frameID, self.centroid.x(), self.centroid.y(), self.tCert,
                  len(self.head), self.length, self.width, self.hCert, len(self.flagellum), self.fCert)


class Sperm:
    """
        The Sperm class holds all of the data about an individual sperm.
    """

    def __init__(self, beatCycleLength=1, fileName=None):

        self.clear()
        self.__myBeatCycleLength = beatCycleLength

        if fileName is not None:

            ok, msg = self.loadSperm(fileName)

            if not ok:
                print msg
                raise IOError('IOError opening : %s' % fileName)

    def clear(self):
        self.__myFrames = []

        self.__myBeatCycleLength = 1.0
        self.__myNumberOfGlyphs = 0

        # Kinematic measures
        self.__myVCLs = []
        self.__myVAPs = []
        self.__myVSLs = []
        self.__myALHs = []
        self.__myBCFs = []
        self.__myMADs = []

        # Head Mechanics
        self.__myHeadLengths = []
        self.__myHeadWidths = []
        self.__myHeadAngles = []

        # Flagellum Mechanics
        self.__myArcLengths = []
        self.__myChangesInAngles = []
        self.__myTorques = []
        self.__myAsymmetries = []

        self.__myHeadUncertainties = []
        self.__myFlagellumUncertainties = []

        # Positioning and Directions
        self.__myStartPositions = []
        self.__myMiddlePositions = []
        self.__myEndPositions = []
        self.__myAveragePositions = []
        self.__myMidPointPositions = []

        self.__myStartDirections = []
        self.__myMiddleDirections = []
        self.__myEndDirections = []
        self.__myAverageDirections = []
        self.__myMidPointDirections = []

    def __len__(self):
        return len(self.__myFrames)

    def __repr__(self):
        return ('Sperm( frames : %s, beatCycleLength : %s, positions %s ' %
                (len(self.__myFrames), self.__myBeatCycleLength, len(self.__myMidPointPositions)))

    def __str__(self):
        return ('Sperm( frames : %s, beatCycleLength : %s, positions %s ' %
                (len(self.__myFrames), self.__myBeatCycleLength, len(self.__myMidPointPositions)))

    def getBeatCycleLength(self):
        return self.__myBeatCycleLength

    def getNumberOfGlyphs(self):
        return self.__myNumberOfGlyphs

    def getParameters(self, index):

        global maxAsymmetry, maxTorque

        return [self.getHeadUncertainty(index), self.getFlagellumUncertainty(index),
                self.getVCL(index), self.getVAP(index), self.getVSL(index),
                self.getBCF(index), self.getALH(index), self.getMAD(index),
                self.getHeadAngle(index), self.getHeadLength(index), self.getHeadWidth(index),
                self.getArcLength(index),
                self.getChangeInAngle(index),
                self.getTorque(index) / maxTorque,
                self.getAsymmetry(index) / maxAsymmetry]

    def getSummaryParameters(self):

        global maxAsymmetry, maxTorque

        return [self.getAvgHeadUncertainty(), self.getAvgFlagellumUncertainty(),
                self.getAvgVCL(), self.getAvgVAP(), self.getAvgVSL(),
                self.getAvgBCF(), self.getAvgALH(), self.getAvgMAD(),
                self.getAvgHeadAngle(), self.getAvgHeadLength(), self.getAvgHeadWidth(),
                self.getAvgArcLength(),
                self.getAvgChangeInAngle(),
                self.getAvgTorques() / maxTorque,
                self.getAvgAsymmetry() / maxAsymmetry]

    def getCentroid(self, index):

        pos = None

        if 0 <= index < len(self.__myFrames):
            pos = self.__myFrames[index].getCentroid()

        return pos

    def getPosition(self, index, strategy):

        pos = None

        if (strategy is AVERAGE_POSITION) and (0 <= index < len(self.__myAveragePositions)):
            pos = self.__myAveragePositions[index]

        elif (strategy is START_POSITION) and (0 <= index < len(self.__myStartPositions)):
            pos = self.__myStartPositions[index]

        elif (strategy is END_POSITION) and (0 <= index < len(self.__myEndPositions)):
            pos = self.__myEndPositions[index]

        elif (strategy is MIDDLE_POSITION) and (0 <= index < len(self.__myMiddlePositions)):
            pos = self.__myMiddlePositions[index]

        elif (strategy is MIDPOINT_POSITION) and (0 <= index < len(self.__myMidPointPositions)):
            pos = self.__myMidPointPositions[index]

        return pos

    def getPositions(self, strategy):

        if strategy is AVERAGE_POSITION:
            return self.__myAveragePositions

        elif strategy is START_POSITION:
            return self.__myStartPositions

        elif strategy is END_POSITION:
            return self.__myEndPositions

        elif strategy is MIDDLE_POSITION:
            return self.__myMiddlePositions

        elif strategy is MIDPOINT_POSITION:
            return self.__myMidPointPositions

    def getDirection(self, index, strategy):

        directory = None

        if (strategy is AVERAGE_POSITION) and (0 <= index < len(self.__myAverageDirections)):
            directory = self.__myAverageDirections[index]

        elif (strategy is START_POSITION) and (0 <= index < len(self.__myStartDirections)):
            directory = self.__myStartDirections[index]

        elif (strategy is END_POSITION) and (0 <= index < len(self.__myEndDirections)):
            directory = self.__myEndDirections[index]

        elif (strategy is MIDDLE_POSITION) and (0 <= index < len(self.__myMiddleDirections)):
            directory = self.__myMiddleDirections[index]

        elif (strategy is MIDPOINT_POSITION) and (0 <= index < len(self.__myMidPointDirections)):
            directory = self.__myMidPointDirections[index]

        return directory

    def getDirections(self, strategy):

        if strategy is AVERAGE_POSITION:
            return self.__myAverageDirections

        elif strategy is START_POSITION:
            return self.__myStartDirections

        elif strategy is END_POSITION:
            return self.__myEndDirections

        elif strategy is MIDDLE_POSITION:
            return self.__myMiddleDirections

        elif strategy is MIDPOINT_POSITION:
            return self.__myMidPointDirections

    def getHeadUncertainty(self, index):

        uncertainty = None

        if 0 <= index < len(self.__myHeadUncertainties):
            uncertainty = self.__myHeadUncertainties[index]

        return uncertainty

    def getFlagellumUncertainty(self, index):

        uncertainty = None

        if 0 <= index < len(self.__myFlagellumUncertainties):
            uncertainty = self.__myFlagellumUncertainties[index]

        return uncertainty

    def getHeadUncertainties(self):
        return self.__myHeadUncertainties

    def getAvgHeadUncertainty(self):
        return average(self.__myHeadUncertainties)

    def getFlagellumUncertainties(self):
        return self.__myFlagellumUncertainties

    def getAvgFlagellumUncertainty(self):
        return average(self.__myFlagellumUncertainties)

    def getVCL(self, index):

        vcl = None

        if 0 <= index < len(self.__myVCLs):
            vcl = self.__myVCLs[index]

        return vcl

    def getVCLs(self):
        return self.__myVCLs

    def getAvgVCL(self):
        return average(self.__myVCLs)

    def getVAP(self, index):

        vap = None

        if 0 <= index < len(self.__myVAPs):
            vap = self.__myVAPs[index]

        return vap

    def getVAPs(self):
        return self.__myVAPs

    def getAvgVAP(self):
        return average(self.__myVAPs)

    def getVSL(self, index):

        vsl = None

        if 0 <= index < len(self.__myVSLs):
            vsl = self.__myVSLs[index]

        return vsl

    def getVSLs(self):
        return self.__myVSLs

    def getAvgVSL(self):
        return average(self.__myVSLs)

    def getWOB(self, index):

        wob = None

        if 0 <= index < len(self.__myVAPs) and index < len(self.__myVCLs):
            wob = self.__myVAPs[index] / self.__myVCLs[index]

        return wob

    def getWOBs(self):
        vap = self.__myVAPs
        vcl = self.__myVCLs
        size = len(vcl)
        return [vap[i] / vcl[i] for i in range(size)]

    def getAvgWOB(self):
        return average(self.getWOBs())

    def getLIN(self, index):

        lin = None

        if 0 <= index < len(self.__myVSLs) and index < len(self.__myVCLs):
            lin = self.__myVSLs[index] / self.__myVCLs[index]

        return lin

    def getLINs(self):

        vsl = self.__myVSLs
        vcl = self.__myVCLs
        size = len(vcl)

        return [vsl[i] / vcl[i] for i in range(size)]

    def getAvgLin(self):
        return average(self.getLINs())

    def getSTR(self, index):
        lin = None
        if 0 <= index < len(self.__myVSLs) and index < len(self.__myVAPs):
            lin = self.__myVSLs[index] / self.__myVAPs[index]
            
        return lin

    def getSTRs(self):
        vap = self.__myVAPs
        vsl = self.__myVSLs
        size = len(vsl)
        return [vsl[i] / vap[i] for i in range(size)]

    def getAvgSTR(self):
        return average(self.getSTRs())

    def getBCF(self, index):

        bcf = None

        if 0 <= index < len(self.__myBCFs):
            bcf = self.__myBCFs[index]

        return bcf

    def getBCFs(self):
        return self.__myBCFs

    def getAvgBCF(self):
        return average(self.__myBCFs)

    def getALH(self, index):

        alh = None

        if 0 <= index < len(self.__myALHs):
            alh = self.__myALHs[index]

        return alh

    def getALHs(self):
        return self.__myALHs

    def getAvgALH(self):
        return average(self.__myALHs)

    def getMAD(self, index):

        mad = None

        if 0 <= index < len(self.__myMADs):
            mad = self.__myMADs[index]

        return mad

    def getMADs(self):
        return self.__myMADs

    def getAvgMAD(self):
        return average(self.__myMADs)

    def getHeadAngle(self, index):

        angle = None

        if 0 <= index < len(self.__myHeadAngles):
            angle = self.__myHeadAngles[index]

        return angle

    def getHeadAngles(self):
        return self.__myHeadAngles

    def getAvgHeadAngle(self):
        return average(self.__myHeadAngles)

    def getHeadLength(self, index):

        length = None

        if 0 <= index < len(self.__myHeadLengths):
            length = self.__myHeadLengths[index]

        return length

    def getHeadLengths(self):
        return self.__myHeadLengths

    def getAvgHeadLength(self):
        return average(self.__myHeadLengths)

    def getHeadWidth(self, index):

        width = None

        if 0 <= index < len(self.__myHeadWidths):
            width = self.__myHeadWidths[index]

        return width

    def getHeadWidths(self):
        return self.__myHeadWidths

    def getAvgHeadWidth(self):
        return average(self.__myHeadWidths)

    def getArcLength(self, index):

        length = None

        if 0 <= index < len(self.__myArcLengths):
            length = self.__myArcLengths[index]

        return length

    def getArcLengths(self):
        return self.__myArcLengths

    def getAvgArcLength(self):
        return average(self.__myArcLengths)

    def getChangeInAngle(self, index):

        angle = None

        if 0 <= index < len(self.__myChangesInAngles):
            angle = self.__myChangesInAngles[index]

        return angle

    def getChangesInAngles(self):
        return self.__myChangesInAngles

    def getAvgChangeInAngle(self):
        return average(self.__myChangesInAngles)

    def getTorque(self, index, normalized=False):

        torque = None

        if 0 <= index < len(self.__myTorques):
            if not normalized:
                torque = self.__myTorques[index]
            else:
                scale = 1.0 / max(self.__myTorques)
                torque = self.__myTorques[index] * scale

        return torque

    def getTorques(self, normalized=False):

        if not normalized:
            return self.__myTorques
        else:
            scale = 1.0 / max(self.__myTorques)
            return [scale * value for value in self.__myTorques]

    def getAvgTorques(self, normalized=False):
        return average(self.getTorques(normalized))

    def getAsymmetry(self, index, normalized=False):

        asymmetry = None

        if 0 <= index < len(self.__myAsymmetries):
            if not normalized:
                asymmetry = self.__myAsymmetries[index]
            else:
                scale = 1.0 / max(self.__myAsymmetries)
                asymmetry = self.__myAsymmetries[index] * scale

        return asymmetry

    def getAsymmetries(self, normalized=False):

        if not normalized:

            return self.__myAsymmetries

        else:
            maxValue = max(self.__myAsymmetries)
            minValue = min(self.__myAsymmetries)
            maxMax = max([maxValue, abs(minValue)])
            scale = 1.0 / maxMax
            return [scale * value for value in self.__myAsymmetries]

    def getAvgAsymmetry(self, normalized=False):
        return average(self.getAsymmetries(normalized))

    def addFrame(self, frame):

        print "adding frame"

        if isinstance(frame, Frame):
            self.__myFrames.append(frame)
        else:
            raise TypeError('TypeError : object added must be of type Frame')

    def getFrame(self, i):

        if 0 <= i < len(self.__myFrames):
            return self.__myFrames[i]
        else:
            return None

    def loadSperm(self, filename):
        """
        This function loads the basic data captured about the sperms motion from file.
        Due to the format of the file the data is stored in intermediate data structures
        """

        exception = None

        # there will be certainty associated with the tracking, the head and the flagellu
        centroids = {}
        heads = {}
        capturedFlagella = {}
        flagella = {}
        tCerts = {}
        fCerts = {}
        hCerts = {}
        lengths = {}
        widths = {}
        centres = {}
        tilts = {}

        try:
            inFile = QFile(filename)
            if not inFile.open(QIODevice.ReadOnly):
                raise IOError('IOError opening : %s' % filename)
            stream = QTextStream(inFile)

            # set the codec to UTF-8
            stream.setCodec(CODEC)

            print "processing : %s" % filename

            # in the main loop active the subroutines when the tags are found

            while not stream.atEnd():
                line = self.__nomNomNom(stream)

                # it is a tag and some useful data follows
                if line.startsWith("["):

                    if QRegExp(r"\[HEADER\]", Qt.CaseInsensitive).exactMatch(line):
                        print "reading header info..."
                        self.__readHeader(stream)

                    elif QRegExp(r"\[CENTROID\]", Qt.CaseInsensitive).exactMatch(line):
                        print "reading centroids..."
                        self.__readCentroids(stream, centroids, tCerts)

                    elif QRegExp(r"\[HEADELLIPSE\]", Qt.CaseInsensitive).exactMatch(line):
                        print "reading head ellipses..."
                        self.__readEllipses(stream, lengths, widths, centres, tilts)

                    elif QRegExp(r"\[HEAD\]", Qt.CaseInsensitive).exactMatch(line) or \
                            QRegExp(r"\[HEADPOINTS\]", Qt.CaseInsensitive).exactMatch(line):
                        print "reading head points..."
                        self.__readFormatData(stream, heads, hCerts)

                    elif QRegExp(r"\[FLAGELLUM\]", Qt.CaseInsensitive).exactMatch(line):
                        print "reading flagella points..."
                        self.__readFormatData(stream, capturedFlagella, fCerts)
                        print "finished"

                    elif QRegExp(r"\[END\]", Qt.CaseInsensitive).exactMatch(line):
                        # print "early termination with [END] tag"
                        break

                    else:
                        print "this line shouldn't happen", line
                        # if it is not one of the above cases then there is something wrong
                        raise IOError('IOError reading from : %s' % filename)

            print "done..."

            print "fitting flagella with cubic spline"

            last_good_flagellum = []
            keySet = capturedFlagella.keys()

            for k in keySet:
                if len(capturedFlagella[k]) > 1:
                    fitted = fitSpline(capturedFlagella[k], 10.0, 3)
                    flagella[k] = fitted
                    #flagella[k] = catMullRomFit(flagella[k])
                    last_good_flagellum = fitted
                else:
                    flagella[k] = last_good_flagellum

            print "done fitting..."

            # Now we have all of the data stored in local Python structures
            # To make things easier we will transfer the data to custom Frame objects
            keys = centroids.keys()

            for k in keys:
            #print "current frame number %d " % (k)
            # actively ignore frames that have incomplete data
                if (k in centroids) and (k in heads) and (k in lengths) and (k in widths) and \
                        (k in centres) and (k in tilts) and (k in capturedFlagella) and (k in flagella) and \
                        (k in tCerts) and (k in hCerts) and (k in fCerts):

                    frame = Frame()
                    frame.load(k, centroids[k], heads[k], lengths[k], widths[k], centres[k],
                               tilts[k], capturedFlagella[k], flagella[k], tCerts[k], hCerts[k], fCerts[k])
                    self.__myFrames.append(frame)

            print "frames loaded..."

            print "computing mechanics measures"

            self.computeMeasures()

            print "done..."

        except (IOError, TypeError, ValueError, KeyError) as e:

            exception = e

            print "exception caught @ loadSperm, of type : ", type(e)

        except Exception as unexpected:

            exception = unexpected

            print "unexpected error caught @ loadSperm, of type : ", type(unexpected)

            raise unexpected

        finally:

            if exception is None:
                return True, "File : %s loaded successfully" % filename
            else:
                return False, "File : %s exception of type <%s> raised" % (filename, exception)

    def writeJSON(self, fileName):

        print 'writing JSON file...'

        print 'writing all computed data'
        output = open(fileName, 'w')

        output.write('var spermComputedData = [ \n')

        for index in range(self.getNumberOfGlyphs()):
            javaObj = "{ \"index\": %f,\n" \
                      "  \"x\"   : %f,\n" \
                      "  \"y\"   : %f,\n " \
                      "  \"vcl\" : %f,\n " \
                      "  \"vap\" : %f,\n " \
                      "  \"vsl\" : %f,\n " \
                      "  \"alh\" : %f,\n " \
                      "  \"bcf\" : %f,\n " \
                      "  \"mad\" : %f,\n " \
                      "  \"str\" : %f,\n " \
                      "  \"lin\" : %f,\n " \
                      "  \"wob\" : %f,\n " \
                      "  \"hl\"  : %f,\n " \
                      "  \"hw\"  : %f,\n " \
                      "  \"hr\"  : %f,\n " \
                      "  \"fta\" : %f,\n " \
                      "  \"ftc\" : %f,\n " \
                      "  \"ftt\" : %f,\n" \
                      "  \"fas\" : %f,\n " \
                      "  \"uh\"  : %f,\n " \
                      "  \"uf\"  : %f } " % (index,
                                             self.getPosition(index, strategy=MIDPOINT_POSITION).x(),
                                             self.getPosition(index, strategy=MIDPOINT_POSITION).y(),
                                             self.getVCL(index),
                                             self.getVAP(index),
                                             self.getVSL(index),
                                             self.getALH(index),
                                             self.getBCF(index),
                                             self.getMAD(index),
                                             self.getSTR(index),
                                             self.getLIN(index),
                                             self.getWOB(index),
                                             self.getHeadLength(index),
                                             self.getHeadWidth(index),
                                             self.getHeadAngle(index),
                                             self.getArcLength(index),
                                             self.getChangeInAngle(index),
                                             self.getTorque(index, normalized=True),
                                             self.getAsymmetry(index, normalized=True),
                                             self.getHeadUncertainty(index),
                                             self.getFlagellumUncertainty(index))

            if index < self.getNumberOfGlyphs() - 1:
                javaObj += ',\n'

            output.write(javaObj)

        output.write('];\n\n\n')

        print 'writing all frame data'

        output.write('var spermFrameData = [ \n')

        for (index, frame) in enumerate(self.__myFrames):

            javaObj = frame.jsonObjectFormat()

            if index < len(self.__myFrames) - 1:
                javaObj += ',\n'

            output.write(javaObj)

        output.write('];\n')
        output.close()

    def __nomNomNom(self, stream):
        """
            This helper method is private and is used to remove unwanted whitespaces and comments
        """

        line = stream.readLine()

        while not stream.atEnd() and (line.startsWith("#") or line.startsWith("%") or line.isEmpty()):
            line = stream.readLine()

        return line

    def __readHeader(self, stream):
        """
            This subroutine grabs the header information form the file
            so far this is just
        """

        line = self.__nomNomNom(stream)

        if QRegExp(r"SpermID").exactMatch(line):
            lst = line.split("=")
            self.__spermID = intFromQString(lst[1])

    def __readCentroids(self, stream, data, tracking):

        # eat everything between the tag and the data

        line = self.__nomNomNom(stream)

        while not line.isEmpty():
            lst = line.split(",")
            frameID = intFromQString(lst[0])
            tracked = floatFromQString(lst[1])
            xCoord = floatFromQString(lst[2])
            yCoord = floatFromQString(lst[3])
            # put the (frameID, Point) in a tuple to group them
            data[frameID] = QPointF(xCoord, yCoord)
            tracking[frameID] = tracked
            line = stream.readLine()

    def __readEllipses(self, stream, lengths, widths, centres, tilts):

        # eat everything between the tag and the data

        line = self.__nomNomNom(stream)

        while not line.isEmpty():
            lst = line.split(",")
            frameID = intFromQString(lst[0])
            length = floatFromQString(lst[1])
            width = floatFromQString(lst[2])
            xCoord = floatFromQString(lst[3])
            yCoord = floatFromQString(lst[4])
            tilt = floatFromQString(lst[5])

            lengths[frameID] = length
            widths[frameID] = width
            centres[frameID] = QPointF(xCoord, yCoord)
            tilts[frameID] = tilt

            line = stream.readLine()

    def __readFormatData(self, stream, data, certainty):

        # eat everything between the tag and the data

        line = self.__nomNomNom(stream)

        # process head information until we have none left
        while not line.isEmpty():
            
            #print line
            lst = line.split(",")
            frameID = intFromQString(lst[0])
            certain = floatFromQString(lst[1])
            nPoints = intFromQString(lst[2])
            
            points = []
            
            for i in xrange(nPoints):
                try:
                    xCoord = floatFromQString(lst[3 + 2 * i])
                    yCoord = floatFromQString(lst[3 + 2 * i + 1])
                    points.append(QPointF(xCoord, yCoord))
                except IndexError:
                    raise IndexError('IndexError <index out of bounds>')

            data[frameID] = points   # add points to the collection
            certainty[frameID] = certain  # add the certainty to the collection
            line = stream.readLine()    

    def getCentroids(self, start, end):
        if not (0 <= start < end):
            return []
            
        centroids = []
        for i in range(start, end):
            centroids.append(self.__myFrames[i].centroid)
            
        return centroids
    
    def getFlagella(self, start, end):
        if not (0 <= start < end):
            return []
            
        flagella = []
        for i in range(start, end):
            flagella.append(self.__myFrames[i].flagellum)
            
        return flagella
    
    def getHeadDimensions(self, start, end):
        if not (0 <= start < end):
            return []
            
        lengths = []
        widths = []
        for i in range(start, end):
            lengths.append(self.__myFrames[i].length)
            widths.append(self.__myFrames[i].width)
            
        return lengths, widths

    def getHeadUncertainties(self, start, end):
        if not (0 <= start < end):
            return []
            
        uncertainties = []
        # average the uncertainty for now
        for i in range(start, end):
            uncertainties.append(self.__myFrames[i].hCert)
            
        return uncertainties

    def getFlagellumUncertainties(self, start, end):
        if not (0 <= start < end):
            return []
            
        uncertainties = []
        # average the uncertainty for now
        for i in range(start, end):
            uncertainties.append(self.__myFrames[i].fCert)
            
        return uncertainties

    def testMeasures(self):
        global VISCOSITY_VALUE
    
        print('\n\t#### TEST MEASURES ####\n')
    
        N = len(self.__myFrames)
        w = 500
    
        # compute average parameters
        totalPath = self.getCentroids(0, N)
    
        print('number of frames  = %d' % N)
        print('total path length = %d' % len(totalPath))

        if len(totalPath) < w:
            w = len(totalPath) - 1

        avgPath = smooth(totalPath, hanning(w))
        ints = intersectPoints(totalPath, avgPath)
    
        print('total intersections = %d' % len(ints))
        amps = amplitudes(totalPath, avgPath)
        mad, angle = meanAngularDensity(totalPath)
    
        vcl = convertToNMS(averageVelocity(totalPath))
        vap = convertToNMS(averageVelocity(avgPath))
        vsl = convertToNMS(straightLineVelocity(totalPath))
    
        print('VCL : %f' % vcl)
        print('VAP : %f' % vap)
        print('VSL : %f' % vsl)
    
        bcf = 0.0
        if len(ints) > 0.0:
            bcf = len(ints) / convertToSeconds(N)
    
        alh = 0.0
        if len(amps) > 0:
            alh = max(amps)
    
        print('BCF : %f' % bcf)
        print('ALH : %f' % alh)
        print('MAD : %f' % mad)
    
        lens, widths = self.getHeadDimensions(0, N)
    
        averageLengths = convertToNM(average(lens))
        averageWidths = convertToNM(average(widths))
    
        print('head angle            : %f' % angle)
        print('head width            : %f' % averageWidths)
        print('head length           : %f' % averageLengths)
    
        # flagellum mechanics measures
        flagella = self.getFlagella(0, N)
        arcLength = convertToNM(averageArcLength(flagella))
        changesInAngles = averageChangeInAngle(totalPath, flagella)
        asymmetries = convertToNM(averageAsymmetry(totalPath, flagella))
        torques = convertToNMS(averageTorque(flagella, VISCOSITY_VALUE))
    
        print('arc length            : %f' % arcLength)
        print('change in angle       : %f' % changesInAngles)
        print('asymmetry             : %f' % asymmetries)
        print('torques               : %f' % torques)
    
        headUncertainty = average(self.getHeadUncertainties(0, N))
        flagellumUncertainty = average(self.getFlagellumUncertainties(0, N))
    
        print('head uncertainty      : %f' % headUncertainty)
        print('flagellum uncertainty : %f' % flagellumUncertainty)
    
        print('\n\t#######################\n')

    def computeMeasures(self):

        print "\n\n !!!!!!! COMPUTING MEASURES !!!!!!!!!!\n\n"
        global VISCOSITY_VALUE, maxBCF, maxTorque, maxAsymmetry

        # self.testMeasures()

        N = len(self.__myFrames)
        w = 500

        # compute average parameters
        totalPath = self.getCentroids(0, N)
        nFrames = len(totalPath)
        totalTime = convertToSeconds(nFrames)

        print "totalTime -- %s" % totalTime

        timeStep = 1.0

        if nFrames < w:
            w = nFrames - 1

        avgPath = smooth(totalPath, hanning(w))

        if totalTime > timeStep:

            temp = temporalRanges(0.0, totalTime, timeStep)

            glyphRanges = convertToFrameRanges(temp)
            print "glyph ranges -- %s" % glyphRanges

            self.__myNumberOfGlyphs = len(glyphRanges)

            for glyph in glyphRanges:

                start = glyph[0]
                end = glyph[1]

                # 1. Kinematic measures
                path = totalPath[start: end]
                avgP = avgPath[start: end]
                ints = intersectPoints(path, avgP)
                amps = amplitudes(path, avgP)

                # orientation and position
                middle = int(len(path) * 0.5)
                self.__myStartPositions.append(path[0])
                self.__myMiddlePositions.append(path[middle])
                self.__myEndPositions.append(path[-1])
                self.__myAveragePositions.append(averagePosition(path))
                self.__myMidPointPositions.append(midpoint(path[0], path[-1]))

                self.__myStartDirections.append(toVector(path[1] - path[0]))
                self.__myMiddleDirections.append(toVector(path[middle + 1] - path[middle]))
                self.__myEndDirections.append(toVector(path[-1] - path[-2]))
                self.__myAverageDirections.append(averageVector(path))
                self.__myMidPointDirections.append(toVector(path[-1] - path[0]))

                # velocities
                self.__myVCLs.append(convertToNMS(averageVelocity(path)))
                vsl = straightLineVelocity(path)

                self.__myVSLs.append(convertToNMS(vsl))

                self.__myVAPs.append(convertToNMS(averageVelocity(avgP)))
                self.__myBCFs.append(len(ints) - 1)

                # swim measures
                alh = 0.0

                if len(amps) > 0:
                    alh = max(amps)

                self.__myALHs.append(convertToNM(alh))
                mad, angle = meanAngularDensity(path)
                self.__myMADs.append(mad)
                self.__myHeadAngles.append(angle)

                # head mechanics measures
                lens, widths = self.getHeadDimensions(start, end)

                averageLengths = convertToNM(average(lens))
                averageWidths = convertToNM(average(widths))

                self.__myHeadLengths.append(averageLengths)
                self.__myHeadWidths.append(averageWidths)

                # flagellum mechanics measures
                flagella = self.getFlagella(start, end)
                self.__myArcLengths.append(convertToNM(averageArcLength(flagella)))
                self.__myChangesInAngles.append(averageChangeInAngle(path, flagella))
                self.__myAsymmetries.append(convertToNM(averageAsymmetry(path, flagella)))
                self.__myTorques.append(convertToNMS(averageTorque(flagella, VISCOSITY_VALUE)))

                # certainty
                headUncertainty = self.getHeadUncertainties(start, end)
                flagellumUncertainty = self.getFlagellumUncertainties(start, end)
                self.__myHeadUncertainties.append(average(headUncertainty))
                self.__myFlagellumUncertainties.append(average(flagellumUncertainty))


class SpermContainer:

    def __init__(self):
        self.clear()

    def isEmpty(self):
        return len(self.__mySperms) < 1

    def getFrameWidth(self):
        return self.__myFrameWidth

    def getFrameHeight(self):
        return self.__myFrameHeight

    def getFilename(self):
        return self.__myFileName

    def getNFrames(self):
        return self.__myNFrames

    def getPixelSize(self):
        global PIXEL_SCALE
        return PIXEL_SCALE

    def getFPS(self):
        global FRAMES_PER_SECOND
        return FRAMES_PER_SECOND

    def getMaxNumberOfGlyphs(self):
        if self.isEmpty():
            return 0
        return max([sperm.getNumberOfGlyphs() for sperm in self.__mySperms])

    def clear(self):
        # assign fresh objects to private data and old data will be garbage collected
        self.__myFrameWidth = 0
        self.__myFrameHeight = 0
        self.__myBeatCycles = 0
        self.__myNFrames = 0

        self.__myFileName = QString()

        self.__mySpermFiles = []
        self.__mySperms = []

    @staticmethod
    def formats():
        return "*.txt *.spm"

    def loadDataSet(self, filename):

        global FRAMES_PER_SECOND
        global PIXEL_SCALE
        global VISCOSITY_VALUE

        exception = None
        # we do not want to dirty the loaded data with a bad read
        tempSpermFiles = []
        tempSperms = []

        print 'loading data....'

        try:
            # try to open the file and read in the data
            inFile = QFile(filename)
            if not inFile.open(QIODevice.ReadOnly):
                print "There is an IOError in SpermContainer -- "
                raise IOError('IOError opening : %s' % filename)
            stream = QTextStream(inFile)
            # set the codec to UTF-8
            stream.setCodec(CODEC)

            nFiles = 0

            # iterate over the file
            while not stream.atEnd():

                line = self.__nomNomNom(stream)
                # print('processing line --- %s ' % line)
                # split the line on the choice of delimiter
                lst = line.split('=')
                tag = lst[0].trimmed()

                # if it's the number of files take note of it
                if QRegExp(r"nMaxSperms", Qt.CaseInsensitive).exactMatch(tag):
                    nFiles = intFromQString(lst[1])

                elif QRegExp(r"frameWidth", Qt.CaseInsensitive).exactMatch(tag):
                    self.__myFrameWidth = intFromQString(lst[1])

                elif QRegExp(r"frameHeight", Qt.CaseInsensitive).exactMatch(tag):
                    self.__myFrameHeight = intFromQString(lst[1])

                elif QRegExp(r"beatCycleLength", Qt.CaseInsensitive).exactMatch(tag):
                    self.__myBeatCycleLength = intFromQString(lst[1])

                elif QRegExp(r"FPS", Qt.CaseInsensitive).exactMatch(tag):
                    FRAMES_PER_SECOND = floatFromQString(lst[1])

                elif QRegExp(r"viscosity", Qt.CaseInsensitive).exactMatch(tag):
                    VISCOSITY_VALUE = floatFromQString(lst[1])

                elif QRegExp(r"nFrames", Qt.CaseInsensitive).exactMatch(tag):
                    self.__myNFrames = intFromQString(lst[1])

                elif QRegExp(r"pixelSize", Qt.CaseSensitive).exactMatch(tag):
                    PIXEL_SCALE = floatFromQString(lst[1])

                elif QRegExp(r"dataFile", Qt.CaseInsensitive).exactMatch(tag):
                    tempSpermFiles.append(lst[1])

            print('viscosity is : %s' % VISCOSITY_VALUE)

            print('nFiles : %d ' % nFiles)

            # if the number of lines read does not match the
            # expected number of lines then we have a problem

            if nFiles != len(tempSpermFiles):
                raise IOError('IOError <number of files read does not match header information in : %s' % filename)

            # make sure to close the header file before doing more processing
            inFile.close()

            # now read in the sperm files specified by in the header file
            # make sure to get the path to the local files from the header file

            filePath = QFileInfo(filename)
            filename = filePath.fileName()

            # iterate over the sperm files and load them into the container
            for pair in enumerate(tempSpermFiles):
                pathToFile = filePath.path().append("/").append(pair[1].trimmed())
                print "file %d : %s" % (pair[0] + 1, pathToFile)
                sperm = Sperm(self.__myBeatCycleLength, pathToFile)
                tempSperms.append(sperm)

            print('file : %s loaded successfully... number of sperms %d' % (filename, len(tempSperms)))

        except (IOError, TypeError, ValueError, KeyError) as e:

            exception = e

            print "exception caught @ loadSperm, of type : ", type(e)

        except Exception as unexpected:

            exception = unexpected

            print "unexpected error caught @ loadSperm, of type : ", type(unexpected)

            raise unexpected

        finally:

            if exception is None:

                # if everything has gone correctly we can replace the local data
                self.__myFileName = filename
                self.__mySpermFiles = tempSpermFiles
                self.__mySperms = tempSperms
                self.__computeMaxValues()

                print "Everything loaded successfully..."
                return True, "File : %s loaded successfully" % filename
            else:
                return False, "File : %s exception of type <%s> raised" % (filename, exception)

    def __computeMaxValues(self):
        # now determine if this sperm is the global maximum
        global maxTorque
        global maxAsymmetry

        #        def maxVector(vectors=None):
        #            if not vectors: vectors = []
        #            maxLength = 0.0
        #            for vec in vectors:
        #                if maxLength > vec.length(): maxLength = vec.length()
        #
        #

        for sperm in self.__mySperms:
            #displacement = maxVector(sperm.getDirections())

            torque = 0.0

            if len(sperm.getTorques()) > 0:
                torque = max(sperm.getTorques())

            asymmetry = 1.0

            if len(sperm.getAsymmetries()) > 0:
                if max(sperm.getAsymmetries()) > abs(min(sperm.getAsymmetries())):
                    asymmetry = max(sperm.getAsymmetries())
                else:
                    asymmetry = abs(min(sperm.getAsymmetries()))

            if asymmetry == 0.0:
                asymmetry = 1.0

            if maxAsymmetry < asymmetry:
                maxAsymmetry = asymmetry

            if maxTorque < torque:
                maxTorque = torque

        print('Max Asymmetry     : %f ' % maxAsymmetry)
        print('Max Torque        : %f ' % maxTorque)

    def __nomNomNom(self, stream):
        """
                This helper method is private and is used to conaveragee unwanted whitespaces and comments
            """
        line = stream.readLine()
        while not stream.atEnd() and (line.startsWith("#") or
                                      line.startsWith("%") or
                                      line.startsWith("[") or
                                      line.isEmpty()):
            line = stream.readLine()

        return line

    ### overloaded functions

    def __getitem__(self, item):
        return self.__mySperms[item]

    def __len__(self):
        return len(self.__mySperms)


def testLoad():
    print('running unit test on SpermContainer Data structures')

    testFile = QString("data/set2/set2_main.txt")

    print('using test file : %s ' % testFile)

    spermContainer = SpermContainer()
    ok, msg = spermContainer.loadDataSet(testFile)

    for (index, sperm) in enumerate(spermContainer):
        fileName = 'javaSperm%d.json' % index
        sperm.writeJSON(fileName)

    if ok:
        print('Yipee : %s ' % msg)
    else:
        print('Awwww : %s ' % msg)


def testRanges():
    global FRAMES_PER_SECOND

    FRAMES_PER_SECOND = 293.4

    temp = temporalRanges(0.0, 2.93, 1.0)

    print temp

    frames = convertToFrameRanges(temp)

    print frames

# the code for testing this module
if __name__ == '__main__':

    #testRanges()
    testLoad()
