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

## DEBUGGING SETTINGS:
if AppKit.NSUserName() == "rafalbuchner":
    __DEBUG__ = True
else:
    __DEBUG__ = False

if __DEBUG__:
    import traceback
def debugFunctionNestingChain(additionalData=""):
    if __DEBUG__:
        limit = 30
        stack = traceback.extract_stack(limit=limit)
        print("="*50)
        print(f"depth: {len(stack)}")
        for i, f in enumerate(stack):
            if i == len(stack)-1: 
                break
            print(f"{' '+'  '*i}{f.name} at {f.lineno:03d} ({additionalData})")
        print()
## DEBUGGING SETTINGS:

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
    extensionKeyStub + "measureAlways": False,
    extensionKeyStub + "useShortcutToMoveWhileAlways": True,
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

def getCurrentPosition(info):
    glyphView = info["glyphEditor"].getGlyphView()
    locationInView = glyphView._getMousePosition()
    cursorPosition = glyphView._converPointFromViewToGlyphSpace(locationInView)
    return (cursorPosition.x, cursorPosition.y)

class StemPlowSubscriber(subscriber.Subscriber):
    
    debug = __DEBUG__
    wantsMeasurements = False

    @property
    def performAnchoring(self):
        return self.useShortcutToMoveWhileAlways and self.measureAlways
    

    def build(self):
        self.stemPlowRuler = StemPlowRuler()

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

        self.oval_AnchorIndicatorLayer = self.fgBaseLayer.appendSymbolSublayer()
        # register for defaults change
        events.addObserver(
            self, "extensionDefaultsChanged", extensionID + ".defaultsChanged"
        )

        # go
        self.clearData()
        self.loadDefaults()

    def loadDefaults(self):
        # load
        self.stemPlowRuler.loadDefaults()

        self.triggerCharacter = internalGetDefault("triggerCharacter")
        self.measureAlways = bool(internalGetDefault("measureAlways"))
        self.useShortcutToMoveWhileAlways = bool(internalGetDefault("useShortcutToMoveWhileAlways"))
        self.measureAgainstComponents = bool(internalGetDefault("measureAgainstComponents"))
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
            cornerRadius=textSize*0.8,
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
        
        self.oval_AnchorIndicatorLayer.setImageSettings(dict(size=(self.measurementOvalSize+measurementLineSize*5,self.measurementOvalSize+measurementLineSize*5), fillColor=None,strokeColor=ovalColor, strokeWidth=measurementLineSize, name="oval"))

        if self.measureAlways:
            self.wantsMeasurements = True
        

        if self.performAnchoring:
            self.wantsMeasurements = False



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

    
    closestPointOnPath = None
    measurementValue1 = None
    measurementValue2 = None
    textBoxCenter1 = None
    textBoxCenter2 = None
    nearestP1 = None
    nearestP2 = None
    visibleP1 = False
    visibleP2 = False
    position = None

    def glyphEditorDidOpen(self, info):
        if self.measureAlways:
            self.showLayers()
        else:
            self.hideLayers()

        if self.performAnchoring:
            self.stemPlowRuler.anchorRulerWithoutCursor(info)

    def glyphEditorDidSetGlyph(self, info):
        if self.performAnchoring: 
            self.stemPlowRuler.anchorRulerWithoutCursor(info)
            
    def glyphEditorDidKeyDown(self, info):
        isTriggerCharPressed = info["deviceState"]["keyDownWithoutModifiers"] == self.triggerCharacter

        if isTriggerCharPressed and not self.measureAlways:
            self.wantsMeasurements = True
            self.showLayers()

        elif not isTriggerCharPressed and not self.measureAlways:
            self.wantsMeasurements = False

        if self.performAnchoring:
            if isTriggerCharPressed:
                self.wantsMeasurements = True
                self.showLayers()
                self.stemPlowRuler.unanchorRuler(info)
            else:
                self.wantsMeasurements = False

        # whenever user hits arrow keys it will execute code in glyphEditorDidMouseDrag
        if info["deviceState"]["keyDown"] in "": # arrow keys:
            self.glyphEditorDidMouseDrag(info)




    def glyphEditorDidKeyUp(self, info):
        isTriggerCharPressed = info["deviceState"]["keyDownWithoutModifiers"] == self.triggerCharacter
        if not self.measureAlways:
            self.hideLayers()
        else:
            # getting glyph and current mouse location
            if self.useShortcutToMoveWhileAlways and isTriggerCharPressed and not self.stemPlowRuler.anchored:
                self.stemPlowRuler.anchorRuler( info)
                self.updateText()
                self.updateLinesAndOvals()

        if self.performAnchoring:
            self.wantsMeasurements = False

    def glyphEditorDidMouseDrag(self, info):
        # if not self.wantsMeasurements and not self.stemPlowRuler.anchored:
        if not self.performAnchoring:
            return
        if not self.stemPlowRuler.anchored:
            return
        glyph = info["glyph"]

        (
            self.textBoxCenter1,
            self.measurementValue1,
            self.nearestP1,
            self.textBoxCenter2,
            self.measurementValue2,
            self.nearestP2,
            self.closestPointOnPath
        ) = self.stemPlowRuler.getThicknessData(None, glyph, self.stemPlowRuler.getGuidesAndAnchoredPoint)

        self.updateText()
        self.updateLinesAndOvals()

    def glyphEditorDidUndo(self, info):
        self.glyphEditorDidMouseDrag(info)
    

    def glyphEditorDidMouseDown(self, info):
        if not self.measureAlways:
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
        ) = self.stemPlowRuler.getThicknessData(cursorPosition, glyph, self.stemPlowRuler.getGuidesAndClosestPoint)

        self.updateText()
        self.updateLinesAndOvals()

    def glyphEditorWillOpen(self, info):
        if self.measureAlways:
            self.wantsMeasurements = True
            self.showLayers()

    def glyphEditorWantsContextualMenuItems(self, info):
        def _stemPlowGuide( sender):
            print("Create Stem Plow Guide – NotImplemented")

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
        self.oval_AnchorIndicatorLayer.setPosition((self.closestPointOnPath))

        # if self.performAnchoring:
        if self.useShortcutToMoveWhileAlways and self.stemPlowRuler.anchored:
            self.oval_AnchorIndicatorLayer.setVisible(True)
        else:
            self.oval_AnchorIndicatorLayer.setVisible(False)

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

    

class StemPlowRuler:
    keyId = extensionKeyStub + "StemPlowRuler"
    anchored = False

    def clearAnchor(self):
        self.anchored = None

    def anchorRulerWithoutCursor(self, info):
        glyph = info["glyph"]
        if len(glyph.contours) > 0 and glyph.lib.get(self.keyId) is None:
            glyph.lib[self.keyId] = dict( 
                contour_index=0,
                segment_index=0,
                anchor_t=0
                )
        self.anchored = True

    def anchorRuler(self, info):
        glyph = info["glyph"]
        _, contour_index, segment_index, anchor_t = self.calculateDetailsForNearestPointOnCurve(getCurrentPosition(info), glyph)

        glyph.lib[self.keyId] = dict(
                contour_index=contour_index,
                segment_index=segment_index,
                anchor_t=anchor_t
            )

        self.anchored = True

    def unanchorRuler(self, info):
        glyph = info["glyph"]
        if self.keyId in glyph.lib.keys():
            del(glyph.lib[self.keyId])
        self.anchored = False

    def getGuidesAndAnchoredPoint(self, position, glyph):
        # position has to be there, but it will be set to None
        assert position is None, f"something wrong with placement of getGuidesAndAnchoredPoint method (position is {position})"
        if not self.keyId in glyph.lib.keys():
            self.anchored = False
            return
        contour_index = glyph.lib[self.keyId].get("contour_index")
        segment_index = glyph.lib[self.keyId].get("segment_index")
        anchor_t = glyph.lib[self.keyId].get("anchor_t")
        
        contour = glyph.contours[contour_index]
        segs = contour.segments
        seg = segs[segment_index]
        # rebuilding segment into system 2 points for line and 4 for curve (StemMath needs it):
        points = [
            segs[segment_index - 1][-1]
        ]  # 1adding last point from previous segment

        for point in seg.points:
            points.append(point)  # 2 adding rest of points of the segment

        if len(points) == 2:
            P1, P2 = points

            # # making sure that extension doesn't take open segment of the contour into count
            # if P1.type == "line" and P2.type == "move":
            #     continue

            P1, P2 = ((P1.x, P1.y), (P2.x, P2.y))
            guideline1, guideline2 = StemMath.calculateGuidesBasedOnT(
                anchor_t, seg.type, P1, P2
            )

        if len(points) == 4:
            P1, P2, P3, P4 = points
            P1, P2, P3, P4 = (
                (P1.x, P1.y),
                (P2.x, P2.y),
                (P3.x, P3.y),
                (P4.x, P4.y),
            )
            guideline1, guideline2 = StemMath.calculateGuidesBasedOnT(
                anchor_t, seg.type, P1, P2, P3, P4
            )
        onCurvePoint = guideline1[1]

        return guideline1, guideline2, onCurvePoint


    def calculateDetailsForNearestPointOnCurve(self, cursorPosition, glyph):
        # slow, only used for anchoring
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
                        closestPoint, contour_index, segment_index, _, t = StemMath.getClosestInfo(
                            cursorPosition, seg, P1, P2
                        )

                    if len(points) == 4:
                        P1, P2, P3, P4 = points
                        P1, P2, P3, P4 = (
                            (P1.x, P1.y),
                            (P2.x, P2.y),
                            (P3.x, P3.y),
                            (P4.x, P4.y),
                        )
                        closestPoint, contour_index, segment_index, _, t = StemMath.getClosestInfo(
                            cursorPosition, seg, P1, P2, P3, P4
                        )
                        #### TODO: Jesli seg.type == qcurve, to przerob to na StemMath.stemThicnkessGuidelines(cursorPosition,seg.type,P1,P2,P3), wtedy zmien funkcje z TMath na takie, co to będą czystsze jesli chodzi o adekwatnosc do Cubic

                    closestPointsRef.append((closestPoint, contour_index, segment_index, t))

            distances = []

            for ref in closestPointsRef:
                point = ref[0]
                distance = StemMath.lenghtAB(cursorPosition, point)
                distances.append(distance)

            indexOfClosestPoint = distances.index(min(distances))
            closestPointOnPathRef = closestPointsRef[indexOfClosestPoint]
            closestPoint, contour_index, segment_index, t = closestPointOnPathRef

            return closestPoint, contour_index, segment_index, t

    def loadDefaults(self):
        self.measureAgainstComponents = internalGetDefault("measureAgainstComponents")
        self.measureAgainstSideBearings = internalGetDefault("measureAgainstSideBearings")

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

    def getThicknessData(self, position, glyph, method):
        if len(glyph.contours) == 0:
            return

        # guideline1, guideline2, closestPointOnPath = self.getGuidesAndClosestPoint(
        #     position, glyph
        # )
        guideline1, guideline2, closestPointOnPath = method(
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
    # if AppKit.NSUserName() == "rafalbuchner":
    #     for key in defaults.keys():
    #         removeExtensionDefault(key)
    #     registerExtensionDefaults(defaults)
    subscriber.registerGlyphEditorSubscriber(StemPlowSubscriber)
