from mojo import subscriber
from mojo import events
from mojo.extensions import (
    registerExtensionDefaults,
    getExtensionDefault,
    setExtensionDefault,
    removeExtensionDefault
)
extensionID = "com.rafalbuchner.StemPlow"
extensionKeyStub = extensionID + "."


defaults = {
    extensionKeyStub + "triggerCharacter": "s",
    extensionKeyStub + "lineColor": (0, 0.3, 1, 0.8),
    extensionKeyStub + "ovalColor": (0, 0.3, 1, 0.8),
    extensionKeyStub + "textColor": (0, 0.3, 1, 0.8),
    extensionKeyStub + "mainColor": (0, 0.3, 1, 0.8),
    extensionKeyStub + "measurementOvalSize": 6,
    extensionKeyStub + "measurementLineSize": 1,
    extensionKeyStub + "measurementTextSize": 10,
}

registerExtensionDefaults(defaults)


def internalGetDefault(key):
    key = extensionKeyStub + key
    return getExtensionDefault(key)


def internalSetDefault(key, value):
    key = extensionKeyStub + key
    setExtensionDefault(key, value)

def nearestPointFromList(myPoint,points):

        def _sorter(point):
            return StemMath.lenghtAB(myPoint, point)

        points = sorted(points, key=_sorter)
        return points

class StemPlow(subscriber.Subscriber):
    debug = True

    def build(self):
        window = self.getGlyphEditor()
        self.activeContainer = window.extensionContainer(
            identifier=extensionKeyStub + "background",
            location="background",
            clear=True,
        )
        self.textContainer = window.extensionContainer(
            identifier=extensionKeyStub + "foreground",
            location="foreground",
            clear=True,
        )

        # text

        self.textBaseLayer = self.textContainer.appendBaseSublayer(visible=True)

        self.text1Layer = self.textBaseLayer.appendTextLineSublayer(
            visible=False, name="measurement1"
        )
        self.text2Layer = self.textBaseLayer.appendTextLineSublayer(
            visible=False, name="measurement2"
        )

        # outline

        self.lineBaseLayer = self.activeContainer.appendBaseSublayer(visible=False)
        self.lineLayer = self.lineBaseLayer.appendLineSublayer()
        self.oval_ALayer = self.lineBaseLayer.appendOvalSublayer()
        self.oval_BLayer = self.lineBaseLayer.appendOvalSublayer()
        self.oval_CLayer = self.lineBaseLayer.appendOvalSublayer()

        # register for defaults change
        events.addObserver(
            self, "extensionDefaultsChanged", extensionID + ".defaultsChanged"
        )

        # go
        self.clearText()
        self.loadDefaults()

    def loadDefaults(self):
        # load

        self.triggerCharacter = internalGetDefault("triggerCharacter")
        measurementOvalSize = internalGetDefault("measurementOvalSize")
        measurementLineSize = internalGetDefault("measurementLineSize")
        textSize = internalGetDefault("measurementTextSize")
        lineColor = internalGetDefault("mainColor")
        ovalColor = internalGetDefault("mainColor")
        textColor = internalGetDefault("textColor")
        mainColor = internalGetDefault("mainColor")

        # build
        lineAttributes = dict(strokeColor=lineColor, strokeWidth=measurementLineSize)
        textAttributes = dict(
            backgroundColor=mainColor,
            fillColor=textColor,
            padding=(6, 3),
            cornerRadius=5,
            horizontalAlignment="center",
            verticalAlignment="center",
            pointSize=textSize,
            font="Menlo",
        )
        ovalAttributes = dict(size=(measurementOvalSize,measurementOvalSize), fillColor=ovalColor)

        # populate
        self.text1Layer.setPropertiesByName(textAttributes)
        self.text2Layer.setPropertiesByName(textAttributes)
        self.lineLayer.setPropertiesByName(lineAttributes)
        for oval in [self.oval_ALayer, self.oval_BLayer, self.oval_CLayer]:
            print(ovalAttributes)
            oval.setPropertiesByName(ovalAttributes) ####

    def destroy(self):
        self.activeContainer.clearSublayers()
        self.textContainer.clearSublayers()
        events.removeObserver(self, extensionID + ".defaultsChanged")

    def hideLayers(self):
        self.activeContainer.setVisible(False)
        self.textContainer.setVisible(False)
        self.clearText()

    # Events
    # ------

    def roboFontDidChangePreferences(self, info):
        self.loadDefaults()

    def extensionDefaultsChanged(self, event):
        self.loadDefaults()

    # def glyphEditorDidSetGlyph(self, info):
    #     self.g = info["glyph"]

    wantsMeasurements = False
    measurement1 = None
    measurement2 = None

    def glyphEditorDidKeyDown(self, info):
        deviceState = info["deviceState"]
        if deviceState["keyDownWithoutModifiers"] != self.triggerCharacter:
            self.wantsMeasurements = False
        else:
            self.wantsMeasurements = True

    def glyphEditorDidKeyUp(self, info):
        self.hideLayers()
        # setCursorMode(None)

    def glyphEditorDidMouseDown(self, info):
        self.hideLayers()
        # setCursorMode(None)

    def glyphEditorDidMouseMove(self, info):
        if not self.wantsMeasurements:
            return
        self.selectionMeasurementsTextLayer.setVisible(False)
        glyph = info["glyph"]
        position = tuple(info["locationInGlyph"])
        print(f"position {position}")

    # layers updates
    # ----

    def clearText(self):
        self.measurement1 = None
        self.measurement2 = None

    def updateLines(self):
        NotImplemented

    def updateText(self):
        NotImplemented
        # cursorOffset = 7
        # textBlockOffset = 5
        # if self.currentDisplayFocalPoint is not None:
        #     x, y = self.currentDisplayFocalPoint
        #     x += cursorOffset
        #     y -= cursorOffset
        #     self.textBaseLayer.setPosition((x, y))
        # displayOrder = [
        #     ("measurements", self.currentMeasurements, self.measurementsTextLayer, formatWidthHeightString),
        #     ("names", self.currentNames, self.namesTextLayer, formatNames),
        #     ("selection", self.currentSelectionMeasurements, self.selectionMeasurementsTextLayer, formatWidthHeightString),
        #     ("selectionNames", self.currentSelectionNames, self.selectionNamesTextLayer, formatNames)
        # ]
        # position = (
        #     dict(
        #         point="left",
        #         relative="super"
        #     ),
        #     dict(
        #         point="top",
        #         relative="super"
        #     )
        # )
        # visible = []
        # hidden = []
        # for (name, contents, layer, formatter) in displayOrder:
        #     if not contents:
        #         hidden.append(layer)
        #         continue
        #     layer.setText(
        #         formatter(*contents)
        #     )
        #     x = dict(position[0])
        #     y = dict(position[1])
        #     layer.setPosition((x, y))
        #     visible.append(layer)
        #     position[0]["relative"] = name
        #     position[1]["relative"] = name
        #     position[1]["relativePoint"] = "bottom"
        #     position[1]["offset"] = -textBlockOffset
        # for layer in hidden:
        #     layer.setVisible(False)
        # for layer in visible:
        #     layer.setVisible(True)
        # if not self.textContainer.getVisible():
        #     self.textContainer.setVisible(True)

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

        position = (point.x, point.y)

        center1 = None
        nearestP1 = position
        thicknessValue1 = 0

        center2 = None
        nearestP2 = position
        thicknessValue2 = 0

        guideline1, guideline2, closestPointOnPath = self.keyDownDraw()
        if StemMath.lenghtAB(position,closestPointOnPath) < 77:
            intersectionAB1 = IntersectGlyphWithLine(glyph, guideline1)
            intersectionAB2 = IntersectGlyphWithLine(glyph, guideline2)

            # system of if-statemens to hack the iteration through nearestPoints = nearestPointFromList(closestPointOnPath,intersectionAB) kind of lists
            if len(intersectionAB1) != 0:
                nearestPoints1 = nearestPointFromList(closestPointOnPath,intersectionAB1)
                if StemMath.lenghtAB(nearestPoints1[0],closestPointOnPath) < 2.5 :

                    # hack for guidelines going into space
                    if len(nearestPoints1) == 1:
                        nearestP1 = nearestPoints1[0]

                    else:
                        nearestP1 = nearestPoints1[1]
                else:
                    nearestP1 = nearestPoints1[0]

                center1 = StemMath.calcLine(.5,closestPointOnPath,nearestP1)
                thicknessValue1 = StemMath.lenghtAB(closestPointOnPath,nearestP1)
       

            # system of if-statemens to hack the iteration through nearestPoints = self.nearestPointFromList(closestPointOnPath,intersectionAB) kind of lists
            if len(intersectionAB2) != 0:
                nearestPoints2 = nearestPointFromList(closestPointOnPath,intersectionAB2)
                if StemMath.lenghtAB(nearestPoints2[0],closestPointOnPath) < 2.5 :

                    # hack for guidelines going into space
                    if len(nearestPoints2) == 1:
                        nearestP2 = nearestPoints2[0]
                    else:
                        nearestP2 = nearestPoints2[1]
                else:
                    nearestP2 = nearestPoints2[0]

                center2 = StemMath.calcLine(.5,closestPointOnPath,nearestP2)
                thicknessValue2 = StemMath.lenghtAB(closestPointOnPath,nearestP2)

        return center1, thicknesValue1, nearestP1, center2, thicknesValue2, nearestP2
if __name__ == "__main__":
    print("STEMPLOW init")
    subscriber.registerGlyphEditorSubscriber(StemPlow)
