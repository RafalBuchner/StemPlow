import AppKit
import StemMath
from mojo import subscriber
from mojo import events
from mojo import tools
from mojo.extensions import (
    registerExtensionDefaults,
    getExtensionDefault,
    setExtensionDefault,
    removeExtensionDefault,
)

extensionID = "com.rafalbuchner.StemPlow"
extensionKeyStub = extensionID + "."


defaults = {
    extensionKeyStub + "triggerCharacter": "f",
    extensionKeyStub + "lineColor": (0, 0.3, 1, 0.8),
    extensionKeyStub + "ovalColor": (0, 0.3, 1, 0.8),
    extensionKeyStub + "textColor": (1, 1, 1, 0.8),
    extensionKeyStub + "mainColor": (0.1, 0.1, 0.2, 0.8),
    extensionKeyStub + "measurementOvalSize": 6,
    extensionKeyStub + "measurementLineSize": 1,
    extensionKeyStub + "measurementTextSize": 10,
    extensionKeyStub + "measureAgainstComponents": True,
    extensionKeyStub + "measureAgainstSideBearings": True,
}

registerExtensionDefaults(defaults)


def internalGetDefault(key):
    key = extensionKeyStub + key
    return getExtensionDefault(key)


def internalSetDefault(key, value):
    key = extensionKeyStub + key
    setExtensionDefault(key, value)


def nearestPointFromList(myPoint, points):
    def _sorter(point):
        return StemMath.lenghtAB(myPoint, point)

    points = sorted(points, key=_sorter)
    return points


class StemPlow(subscriber.Subscriber):
    debug = True

    def build(self):
        window = self.getGlyphEditor()
        self.backgroundContainer = window.extensionContainer(
            identifier=extensionKeyStub + "background",
            location="background",
            clear=True,
        )
        self.foregroundContainer = window.extensionContainer(
            identifier=extensionKeyStub + "foreground",
            location="foreground",
            clear=True,
        )
        self.fgBaseLayer = self.foregroundContainer.appendBaseSublayer()
        self.bgBaseLayer = self.backgroundContainer.appendBaseSublayer()

        # text


        self.text1Layer = self.fgBaseLayer.appendTextLineSublayer(
            visible=False, name="measurementValue1"
        )
        self.text2Layer = self.fgBaseLayer.appendTextLineSublayer(
            visible=False, name="measurementValue2"
        )

        # geometry

        self.lineLayer   = self.bgBaseLayer.appendLineSublayer()
        self.oval_ALayer = self.bgBaseLayer.appendSymbolSublayer()
        self.oval_BLayer = self.fgBaseLayer.appendSymbolSublayer()
        self.oval_CLayer = self.bgBaseLayer.appendSymbolSublayer()

        # register for defaults change
        events.addObserver(
            self, "extensionDefaultsChanged", extensionID + ".defaultsChanged"
        )

        # go
        self.clearData()
        self.loadDefaults()

    def loadDefaults(self):
        # load

        self.triggerCharacter = internalGetDefault("triggerCharacter")
        self.measureAgainstComponents = internalGetDefault("measureAgainstComponents")
        self.measureAgainstSideBearings = internalGetDefault("measureAgainstSideBearings")
        self.measurementOvalSize = internalGetDefault("measurementOvalSize")
        measurementLineSize = internalGetDefault("measurementLineSize")
        textSize = internalGetDefault("measurementTextSize")
        lineColor = internalGetDefault("lineColor")
        ovalColor = internalGetDefault("ovalColor")
        textColor = internalGetDefault("textColor")
        mainColor = internalGetDefault("mainColor")
        # build
        lineAttributes = dict(strokeColor=lineColor, strokeWidth=measurementLineSize)
        textAttributes = dict(
            backgroundColor=mainColor,
            fillColor=textColor,
            padding=(6, 1),
            cornerRadius=5,
            horizontalAlignment="center",
            verticalAlignment="center",
            pointSize=textSize,
            weight="bold",
            figureStyle="tabular"
        )
        ovalAttributes = dict(size=(self.measurementOvalSize,self.measurementOvalSize), fillColor=ovalColor, name="oval")
        
        self.text1Layer.setPropertiesByName(textAttributes)
        self.text2Layer.setPropertiesByName(textAttributes)
        self.lineLayer.setPropertiesByName(lineAttributes)

        for oval in [self.oval_ALayer, self.oval_BLayer, self.oval_CLayer]:
            oval.setImageSettings(ovalAttributes)

    def destroy(self):
        self.backgroundContainer.clearSublayers()
        self.foregroundContainer.clearSublayers()
        events.removeObserver(self, extensionID + ".defaultsChanged")

    def hideLayers(self):
        self.backgroundContainer.setVisible(False)
        self.foregroundContainer.setVisible(False)
        self.clearData()

    def showLayers(self):
        self.backgroundContainer.setVisible(True)
        self.foregroundContainer.setVisible(True)

    # Events
    # ------

    def roboFontDidChangePreferences(self, info):
        self.loadDefaults()

    def extensionDefaultsChanged(self, event):
        self.loadDefaults()

    wantsMeasurements = False
    closestPointOnPath = None
    measurementValue1 = None
    measurementValue2 = None
    textBoxCenter1 = None
    textBoxCenter2 = None
    nearestP1 = None
    nearestP2 = None
    visibleP1 = False
    visibleP2 = False

    def glyphEditorDidKeyDown(self, info):
        deviceState = info["deviceState"]
        if deviceState["keyDownWithoutModifiers"] != self.triggerCharacter:
            self.wantsMeasurements = False
        else:
            self.wantsMeasurements = True
            self.showLayers()


    def glyphEditorDidKeyUp(self, info):
        self.hideLayers()
        self.wantsMeasurements = False

    def glyphEditorDidMouseDown(self, info):
        self.hideLayers()

    def glyphEditorDidMouseMove(self, info):
        if not self.wantsMeasurements:
            return
        glyph = info["glyph"]
        if len(glyph.contours) + len(glyph.components) == 0:
                return
        cursorPosition = tuple(info["locationInGlyph"])
        
        (
            self.textBoxCenter1,
            self.measurementValue1,
            self.nearestP1,
            self.textBoxCenter2,
            self.measurementValue2,
            self.nearestP2,
            self.closestPointOnPath
        ) = self.getThicknessData(cursorPosition, glyph)

        self.updateText()
        self.updateLinesAndOvals()

    def glyphEditorWantsContextualMenuItems(self, info):
        def _stemPlowGuide( sender):
            glyph = info["glyph"]
            if len(glyph.contours) + len(glyph.components) == 0:
                return
            
            cursorPosition = tuple(info["locationInGlyph"])
            
            closestPointsRef = []

            if cursorPosition is None:
                return

            for contour in glyph.contours:
                segs = contour.segments

                for seg in segs:
                    segIndex = segs.index(seg)

                    # rebuilding segment into system 2 points for line and 4 for curve (StemMath needs it):
                    points = [segs[segIndex-1][-1]] # 1adding last point from previous segment
                    for point in seg.points:
                        points.append(point) # 2 adding rest of points of the segment

                    if len(points) == 2:
                        P1,P2=points
                        P1,P2=((P1.x,P1.y),(P2.x,P2.y))
                        l1,l2 = StemMath.stemThicnkessGuidelines(cursorPosition,seg.type,P1,P2)



                    if len(points) == 4:
                        P1,P2,P3,P4=points
                        P1,P2,P3,P4=((P1.x,P1.y),(P2.x,P2.y),(P3.x,P3.y),(P4.x,P4.y))
                        l1, l2 = StemMath.stemThicnkessGuidelines(cursorPosition, seg.type, P1,P2,P3,P4)

                    closestPoint = l1[1]
                    closestPointsRef.append((closestPoint,l1,l2))

            distances = []

            for ref in closestPointsRef:
                point = ref[0]
                distance = StemMath.lenghtAB(cursorPosition,point)
                distances.append(distance)

            indexOfClosestPoint = distances.index(min(distances))
            closestPointOnPathRef = closestPointsRef[indexOfClosestPoint]
            closestPointOnPath, guideline1, guideline2 = closestPointOnPathRef

            angle1 = StemMath.angle(*guideline1)
            posX,posY = cursorPosition
            glyph.appendGuideline(closestPointOnPath,angle1)
            glyph.guidelines[-1].showMeasurements = 1

        myMenuItems = [
            ("Create Stem Plow Guide", _stemPlowGuide)
        ]
        info["itemDescriptions"].extend(myMenuItems)


    

    # layers updates
    # ----

    def clearData(self):
        self.wantsMeasurements = False
        self.measurementValue1 = None
        self.measurementValue2 = None
        self.textBoxCenter1 = None
        self.textBoxCenter2 = None
        self.nearestP1 = None
        self.nearestP2 = None

    def updateLinesAndOvals(self):
        self.lineLayer.setStartPoint(self.nearestP1)
        self.lineLayer.setEndPoint(self.nearestP2)
        self.oval_ALayer.setPosition((self.nearestP1))
        self.oval_BLayer.setPosition((self.closestPointOnPath))
        self.oval_CLayer.setPosition((self.nearestP2))

    def updateText(self):
        if round(self.measurementValue1) != 0 and self.textBoxCenter1 is not None:
            self.text1Layer.setVisible(True)
            self.text1Layer.setText(str(round(self.measurementValue1,2)))
            self.text1Layer.setPosition(self.textBoxCenter1)
        else:
            self.text1Layer.setVisible(False)

        if round(self.measurementValue2) != 0 and self.textBoxCenter2 is not None:
            self.text2Layer.setVisible(True)
            self.text2Layer.setText(str(round(self.measurementValue2,2)))
            self.text2Layer.setPosition(self.textBoxCenter2)
        else:
            self.text2Layer.setVisible(False)
    # calculations
    # ------------

    def getGuidesAndClosestPoint(self, cursorPosition, glyph):
        """returns 2 intersection lists"""
        closestPointsRef = []

        if cursorPosition != (-3000, -3000):  # if anchor exist
            for contour in glyph.contours:
                segs = contour.segments

                for segIndex, seg in enumerate(segs):
                    # rebuilding segment into system 2 points for line and 4 for curve (StemMath needs it):
                    points = [
                        segs[segIndex - 1][-1]
                    ]  # 1adding last point from previous segment

                    for point in seg.points:
                        points.append(point)  # 2 adding rest of points of the segment

                    if len(points) == 2:
                        P1, P2 = points

                        # making sure that extension doesn't take open segment of the contour into count
                        if P1.type == "line" and P2.type == "move":
                            continue

                        P1, P2 = ((P1.x, P1.y), (P2.x, P2.y))
                        l1, l2 = StemMath.stemThicnkessGuidelines(
                            cursorPosition, seg.type, P1, P2
                        )

                    if len(points) == 4:
                        P1, P2, P3, P4 = points
                        P1, P2, P3, P4 = (
                            (P1.x, P1.y),
                            (P2.x, P2.y),
                            (P3.x, P3.y),
                            (P4.x, P4.y),
                        )
                        l1, l2 = StemMath.stemThicnkessGuidelines(
                            cursorPosition, seg.type, P1, P2, P3, P4
                        )
                        #### TODO: Jesli seg.type == qcurve, to przerob to na StemMath.stemThicnkessGuidelines(cursorPosition,seg.type,P1,P2,P3), wtedy zmien funkcje z TMath na takie, co to będą czystsze jesli chodzi o adekwatnosc do Cubic

                    closestPoint = l1[1]
                    closestPointsRef.append((closestPoint, l1, l2))

            distances = []

            for ref in closestPointsRef:
                point = ref[0]
                distance = StemMath.lenghtAB(cursorPosition, point)
                distances.append(distance)

            indexOfClosestPoint = distances.index(min(distances))
            closestPointOnPathRef = closestPointsRef[indexOfClosestPoint]
            closestPointOnPath, guideline1, guideline2 = closestPointOnPathRef

            A1, B1 = guideline1
            A2, B2 = guideline2

            return guideline1, guideline2, closestPointOnPath

    def getThicknessData(self, position, glyph):
        if len(glyph.contours) == 0:
            return

        # position = (point.x, point.y)


        guideline1, guideline2, closestPointOnPath = self.getGuidesAndClosestPoint(
            position, glyph
        )

        textBoxCenter1 = None
        nearestP1 = closestPointOnPath
        thicknessValue1 = 0

        textBoxCenter2 = None
        nearestP2 = closestPointOnPath
        thicknessValue2 = 0

        # if StemMath.lenghtAB(position, closestPointOnPath) < 77:
        intersectionAB1 = tools.IntersectGlyphWithLine(glyph, guideline1, canHaveComponent=self.measureAgainstComponents, addSideBearings=self.measureAgainstSideBearings)
        intersectionAB2 = tools.IntersectGlyphWithLine(glyph, guideline2, canHaveComponent=self.measureAgainstComponents, addSideBearings=self.measureAgainstSideBearings)

        # system of if-statemens to hack the iteration through nearestPoints = nearestPointFromList(closestPointOnPath,intersectionAB) kind of lists
        if len(intersectionAB1) != 0:
            nearestPoints1 = nearestPointFromList(
                closestPointOnPath, intersectionAB1
            )
            if StemMath.lenghtAB(nearestPoints1[0], closestPointOnPath) < 2.5:
                # hack for guidelines going into space
                if len(nearestPoints1) == 1:
                    nearestP1 = nearestPoints1[0]

                else:
                    nearestP1 = nearestPoints1[1]
            else:
                nearestP1 = nearestPoints1[0]

            textBoxCenter1 = StemMath.calcLine(0.5, closestPointOnPath, nearestP1)
            thicknessValue1 = StemMath.lenghtAB(closestPointOnPath, nearestP1)

        # system of if-statemens to hack the iteration through nearestPoints = self.nearestPointFromList(closestPointOnPath,intersectionAB) kind of lists
        if len(intersectionAB2) != 0:
            nearestPoints2 = nearestPointFromList(
                closestPointOnPath, intersectionAB2
            )
            if StemMath.lenghtAB(nearestPoints2[0], closestPointOnPath) < 2.5:
                # hack for guidelines going into space
                if len(nearestPoints2) == 1:
                    nearestP2 = nearestPoints2[0]
                else:
                    nearestP2 = nearestPoints2[1]
            else:
                nearestP2 = nearestPoints2[0]

            textBoxCenter2 = StemMath.calcLine(0.5, closestPointOnPath, nearestP2)
            thicknessValue2 = StemMath.lenghtAB(closestPointOnPath, nearestP2)

        return (
            textBoxCenter1,
            thicknessValue1,
            nearestP1,
            textBoxCenter2,
            thicknessValue2,
            nearestP2,
            closestPointOnPath
        )


def main():
    if AppKit.NSUserName() == "rafalbuchner":
        for key in defaults.keys():
            removeExtensionDefault(key)
        registerExtensionDefaults(defaults)
    subscriber.registerGlyphEditorSubscriber(StemPlow)
