import AppKit  # type: ignore
from fontParts.world import RGlyph
from mojo import subscriber  # type: ignore
from mojo import events  # type: ignore
from mojo.extensions import (  # type: ignore
    registerExtensionDefaults,
    getExtensionDefault,
    setExtensionDefault,
)
from mojo.pens import DecomposePointPen  # type: ignore

try:
    import stemPlow.stemmath as StemMath
except ModuleNotFoundError:

    class StemPlowStartingSubscriber(subscriber.Subscriber):
        def roboFontDidFinishLaunching(self, info):
            from mojo.pipTools import installNeededPackages  # type: ignore

            print("initializing StemPlow")
            installNeededPackages(
                "StemPlow",
                [
                    dict(
                        packageName="bezier",
                        # importName="quicksilver"
                    )
                ],
            )
            print("finished initializing StemPlow")

    subscriber.registerRoboFontSubscriber(StemPlowStartingSubscriber)


import math

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
        print("=" * 50)
        print(f"depth: {len(stack)}")
        for i, f in enumerate(stack):
            if i == len(stack) - 1:
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
    extensionKeyStub + "ignoreOverlapsFlag": False,
    extensionKeyStub + "measureAgainstComponents": True,
    extensionKeyStub + "measureAgainstSideBearings": True,
    extensionKeyStub + "showLaserMeasureNames": True,
    extensionKeyStub + "measureAlways": False,
    extensionKeyStub + "useShortcutToMoveWhileAlways": False,
}

registerExtensionDefaults(defaults)


def formatNames(*args):
    return "\n".join(*args)


def internalGetDefault(key):
    key = extensionKeyStub + key
    return getExtensionDefault(key)


def internalSetDefault(key, value):
    key = extensionKeyStub + key
    setExtensionDefault(key, value)


def nearestPointFromList(myPoint, points):
    def _sorter(point):
        return StemMath.lengthAB(myPoint, point)

    points = sorted(points, key=_sorter)
    return points


def getCurrentPosition(info):
    glyphView = info["glyphEditor"].getGlyphView()
    locationInView = glyphView._getMousePosition()
    cursorPosition = glyphView._converPointFromViewToGlyphSpace(locationInView)
    return (cursorPosition.x, cursorPosition.y)


# FIXME cleanup those:


def copyOverlaplessGlyph(srcGlyph: RGlyph) -> RGlyph:
    # couldn't help myself with the name, and the comment about the name
    dstGlyph = RGlyph()
    dstPen = dstGlyph.getPointPen()
    srcGlyph.drawPoints(dstPen)
    dstGlyph.removeOverlap()

    dstGlyph.width = srcGlyph.width
    return dstGlyph


def copyDecomposedAndOverlaplessGlyph(srcGlyph: RGlyph) -> RGlyph:
    # couldn't help myself with the name, and the comment about the name
    dstGlyph = RGlyph()
    dstPen = dstGlyph.getPointPen()
    decomposePen = DecomposePointPen(srcGlyph.font, dstPen)
    srcGlyph.drawPoints(decomposePen)
    dstGlyph.removeOverlap()

    dstGlyph.width = srcGlyph.width
    return dstGlyph


def copyGlyphWithSidebearings(
    srcGlyph: RGlyph, offset: float, slantAngle: float | int
) -> RGlyph:
    dstGlyph = RGlyph()
    pen = dstGlyph.getPen()
    srcGlyph.draw(pen)
    offset = offset if slantAngle != 0 else 0
    x_offset = 5000 * math.tan(math.radians(slantAngle))

    pen.moveTo((x_offset + offset, -5000))
    pen.lineTo((-x_offset + offset, 5000))
    pen.endPath()
    pen.moveTo((srcGlyph.width + x_offset + offset, -5000))
    pen.lineTo((srcGlyph.width - x_offset + offset, 5000))
    pen.endPath()
    dstGlyph.width = srcGlyph.width
    return dstGlyph


def copyDecomposedGlyph(srcGlyph: RGlyph) -> RGlyph:
    # couldn't help myself with the name, and the comment about the name
    dstGlyph = RGlyph()
    dstPen = dstGlyph.getPointPen()
    decomposePen = DecomposePointPen(srcGlyph.font, dstPen)
    srcGlyph.drawPoints(decomposePen)

    dstGlyph.width = srcGlyph.width
    return dstGlyph


def findMiddleOfTheGlyph(info):
    minx, miny, maxx, maxy = info["glyph"].bounds
    return ((maxx - minx) / 2 + minx, (maxy - miny) / 2 + miny)


class StemPlowSubscriber(subscriber.Subscriber):

    debug = __DEBUG__
    wantsMeasurements = False
    measureAlwaysVisible = True

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
        self.namedValues1Layer = self.fgBaseLayer.appendTextLineSublayer(
            visible=False, name="namedValue1"
        )
        self.text2Layer = self.fgBaseLayer.appendTextLineSublayer(
            visible=False, name="measurementValue2"
        )
        self.namedValues2Layer = self.fgBaseLayer.appendTextLineSublayer(
            visible=False, name="namedValue2"
        )

        # geometry

        self.lineLayer = self.bgBaseLayer.appendLineSublayer()
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

    def glyphEditorDidScale(self, info):
        # I think it causes flickering while scalling
        scale = info["scale"]
        self.stemPlowRuler.setScale(scale)
        self.updateText()

    def loadDefaults(self):
        # load
        self.stemPlowRuler.loadDefaults()

        self.triggerCharacter = internalGetDefault("triggerCharacter")
        self.measureAlways = bool(internalGetDefault("measureAlways"))
        self.useShortcutToMoveWhileAlways = bool(
            internalGetDefault("useShortcutToMoveWhileAlways")
        )
        self.ignoreOverlapsFlag = bool(internalGetDefault("ignoreOverlapsFlag"))
        self.measureAgainstComponents = bool(
            internalGetDefault("measureAgainstComponents")
        )
        self.showLaserMeasureNames = bool(internalGetDefault("showLaserMeasureNames"))
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
            cornerRadius=textSize * 0.8,
            horizontalAlignment="center",
            verticalAlignment="center",
            pointSize=textSize,
            weight="bold",
            figureStyle="tabular",
        )
        ovalAttributes = dict(
            size=(self.measurementOvalSize, self.measurementOvalSize),
            fillColor=ovalColor,
            name="oval",
        )

        self.lineLayer.setPropertiesByName(lineAttributes)
        self.text1Layer.setPropertiesByName(textAttributes)
        self.text2Layer.setPropertiesByName(textAttributes)
        self.namedValues1Layer.setPropertiesByName(textAttributes)
        self.namedValues2Layer.setPropertiesByName(textAttributes)
        self.namedValues1Layer.setOffset((0, -textSize - 5))
        self.namedValues2Layer.setOffset((0, -textSize - 5))
        self.namedValues1Layer.setVerticalAlignment("top")
        self.namedValues2Layer.setVerticalAlignment("top")

        for oval in [self.oval_ALayer, self.oval_BLayer, self.oval_CLayer]:
            oval.setImageSettings(ovalAttributes)

        self.oval_AnchorIndicatorLayer.setImageSettings(
            dict(
                size=(
                    self.measurementOvalSize + measurementLineSize * 5,
                    self.measurementOvalSize + measurementLineSize * 5,
                ),
                fillColor=None,
                strokeColor=ovalColor,
                strokeWidth=measurementLineSize,
                name="oval",
            )
        )

        if self.measureAlways:
            self.wantsMeasurements = True

        if self.performAnchoring:
            self.wantsMeasurements = False

        self.stemPlowRuler.loadNamedMeasurements(self.getFont())
        self.measureAlwaysVisible = self.measureAlways

    def destroy(self):
        self.backgroundContainer.clearSublayers()
        self.foregroundContainer.clearSublayers()
        events.removeObserver(self, extensionID + ".defaultsChanged")

    def clearLayers(self):
        self.backgroundContainer.clearSublayers()
        self.foregroundContainer.clearSublayers()

    def _hideLayers(self):
        self.backgroundContainer.setVisible(False)
        self.foregroundContainer.setVisible(False)

    def hideLayersAndClearData(self):
        self._hideLayers()
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

        # text gui updates
        if self.showLaserMeasureNames:
            self.stemPlowRuler.findNames()
        else:
            self.stemPlowRuler.clearNames()

        # it can catch an error, while self.measurementValue1 or self.measurementValue2 is None. I don't want to add another if statement inside of `self.updateText()`, and catching `self.measurementValue1 is None and self.measurementValue2 is None` seems to be stupid here
        self.updateText()

        # measurement updates
        if self.performAnchoring:
            if self.stemPlowRuler.anchored:
                self.wantsMeasurements = False
            else:
                self.stemPlowRuler.anchorRulerToGlyphWithoutCursor(
                    self.getGlyphEditor().getGlyph().asFontParts()
                )

        if self.measureAlways:
            self.showLayers()
        else:
            self.hideLayersAndClearData()

    closestPointOnPath = None
    measurementValue1 = 0
    measurementValue2 = 0
    textBoxCenter1 = None
    textBoxCenter2 = None
    nearestP1 = None
    nearestP2 = None
    visibleP1 = False
    visibleP2 = False
    position = None
    currentGlyphReference: str | None = None

    def glyphEditorDidOpen(self, info):
        if self.measureAlways:
            self.showLayers()
        else:
            self.hideLayersAndClearData()

        if self.performAnchoring:
            self.stemPlowRuler.anchorRulerToGlyphWithoutCursor(info["glyph"])

    def roboFontDidSwitchCurrentGlyph(self, info):
        if info["glyph"] is None:
            return

        if self.currentGlyphReference != info["glyph"].name:
            if self.performAnchoring:
                self.stemPlowRuler.anchorRuler(
                    info, findMiddleOfTheGlyph
                )  # setting anchor to be the middle of the bounds

                # refreshing drawing by reintroducing data and then updating layers:
                (
                    self.textBoxCenter1,
                    self.measurementValue1,
                    self.nearestP1,
                    self.textBoxCenter2,
                    self.measurementValue2,
                    self.nearestP2,
                    self.closestPointOnPath,
                ) = self.stemPlowRuler.getThicknessData(
                    dict(position=None),
                    info["glyph"],
                    self.stemPlowRuler.getGuidesAndAnchoredPoint,
                )

                self.updateText()
                self.updateLinesAndOvals()
            self.currentGlyphReference = info["glyph"].name

    def glyphEditorDidKeyDown(self, info):
        isTriggerCharPressed = (
            info["deviceState"]["keyDownWithoutModifiers"] == self.triggerCharacter
        )

        if isTriggerCharPressed and not self.measureAlways:
            self.wantsMeasurements = True
            self.showLayers()

        elif not isTriggerCharPressed and not self.measureAlways:
            self.wantsMeasurements = False

        elif self.measureAlways and isTriggerCharPressed and not self.performAnchoring:
            self.measureAlwaysVisible = not self.measureAlwaysVisible

            if self.measureAlwaysVisible:
                self.wantsMeasurements = True
                self.showLayers()
            else:
                self._hideLayers()
                self.wantsMeasurements = True

        if self.performAnchoring:
            if isTriggerCharPressed:
                self.wantsMeasurements = True
                self.showLayers()
                self.stemPlowRuler.unanchorRuler(info)
            else:
                self.wantsMeasurements = False

        # whenever user hits arrow keys it will execute code in glyphEditorDidMouseDrag
        if info["deviceState"]["keyDown"] in "":  # arrow keys:
            self.glyphEditorDidMouseDrag(info)

    def glyphEditorDidKeyUp(self, info):
        isTriggerCharPressed = (
            info["deviceState"]["keyDownWithoutModifiers"] == self.triggerCharacter
        )
        if not self.measureAlways:
            self.hideLayersAndClearData()
        else:
            # getting glyph and current mouse location
            if (
                self.useShortcutToMoveWhileAlways
                and isTriggerCharPressed
                and not self.stemPlowRuler.anchored
            ):
                self.stemPlowRuler.anchorRuler(info)
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
            self.closestPointOnPath,
        ) = self.stemPlowRuler.getThicknessData(
            dict(position=None), glyph, self.stemPlowRuler.getGuidesAndAnchoredPoint
        )

        self.updateText()
        self.updateLinesAndOvals()

    def glyphEditorDidUndo(self, info):
        self.glyphEditorDidMouseDrag(info)

    def glyphEditorDidMouseDown(self, info):
        if not self.measureAlways:
            self.hideLayersAndClearData()

    def glyphEditorDidMouseMove(self, info):
        if not self.wantsMeasurements:
            return

        glyph = info["glyph"]
        if len(glyph.contours) + len(glyph.components) == 0:
            return
        cursorPosition = tuple(info["locationInGlyph"])

        thicknessData = self.stemPlowRuler.getThicknessData(
            dict(position=cursorPosition),
            glyph,
            self.stemPlowRuler.getGuidesAndClosestPoint,
        )
        if thicknessData:
            (
                self.textBoxCenter1,
                self.measurementValue1,
                self.nearestP1,
                self.textBoxCenter2,
                self.measurementValue2,
                self.nearestP2,
                self.closestPointOnPath,
            ) = thicknessData

            self.updateText()
            self.updateLinesAndOvals()

    def glyphEditorWillOpen(self, info):
        if self.measureAlways:
            self.wantsMeasurements = True
            self.showLayers()

    def glyphEditorWantsContextualMenuItems(self, info):
        def _stemPlowGuide(sender):
            print("Create Stem Plow Guide – NotImplemented")

        myMenuItems = [("Create Stem Plow Guide", _stemPlowGuide)]
        info["itemDescriptions"].extend(myMenuItems)

    def fontMeasurementsChanged(self, info):
        self.stemPlowRuler.loadNamedMeasurements(self.getFont())

    # layers updates
    # ----

    def clearData(self):
        self.wantsMeasurements = False
        self.measurementValue1 = 0
        self.measurementValue2 = 0
        self.textBoxCenter1 = None
        self.textBoxCenter2 = None
        self.nearestP1 = None
        self.nearestP2 = None
        self.stemPlowRuler.anchored = False
        self.stemPlowRuler.currentNames1 = None
        self.stemPlowRuler.currentNames2 = None

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
        if self.showLaserMeasureNames:
            self.stemPlowRuler.findNames()
        else:
            self.stemPlowRuler.clearNames()

        roundingFloatValue = self.stemPlowRuler.getRoundingFloatValue()
        if round(self.measurementValue1) != 0 and self.textBoxCenter1 is not None:
            self.text1Layer.setVisible(True)
            self.text1Layer.setText(
                str(round(self.measurementValue1, roundingFloatValue))
            )
            self.text1Layer.setPosition(self.textBoxCenter1)

            ###
            if self.stemPlowRuler.currentNames1:
                self.namedValues1Layer.setText(
                    formatNames(self.stemPlowRuler.currentNames1)
                )
                self.namedValues1Layer.setPosition(self.textBoxCenter1)
                self.namedValues1Layer.setVisible(True)
            else:
                self.namedValues1Layer.setVisible(False)
        else:
            self.text1Layer.setVisible(False)
            self.namedValues1Layer.setVisible(False)

        if round(self.measurementValue2) != 0 and self.textBoxCenter2 is not None:
            self.text2Layer.setVisible(True)
            self.text2Layer.setText(
                str(round(self.measurementValue2, roundingFloatValue))
            )
            self.text2Layer.setPosition(self.textBoxCenter2)

            ###
            if self.stemPlowRuler.currentNames2:
                self.namedValues2Layer.setText(
                    formatNames(self.stemPlowRuler.currentNames2)
                )
                self.namedValues2Layer.setPosition(self.textBoxCenter2)
                self.namedValues2Layer.setVisible(True)
            else:
                self.namedValues2Layer.setVisible(False)
        else:
            self.text2Layer.setVisible(False)
            self.namedValues2Layer.setVisible(False)

    # Objects
    # -------

    def getFont(self):
        window = self.getGlyphEditor()
        glyph = window.getGlyph()
        # in single window mode glyph will
        # be None at start up, so hack around
        if glyph is None:
            font = window.document.getFont()
        else:
            font = glyph.font
        return font


class StemPlowRuler:
    keyId = extensionKeyStub + "StemPlowRuler"
    anchored = False
    scale = None
    currentNames1 = None
    currentNames2 = None

    def getRoundingFloatValue(self):
        # used for scaling
        # roundingFloatValue = 2 # use when glyphEditorDidScale is disabled
        roundingFloatValue = None

        scale = self.scale
        if scale is not None:
            if scale >= 0 and scale < 3:
                roundingFloatValue = None
            elif scale >= 3 and scale < 5:
                roundingFloatValue = 1
            elif scale >= 5 and scale < 7:
                roundingFloatValue = 2
            elif scale >= 7:
                roundingFloatValue = 3
        return roundingFloatValue

    def setScale(self, value):
        self.scale = value

    def clearAnchor(self):
        self.anchored = None

    def anchorRulerToGlyphWithoutCursor(self, glyph):
        if glyph.lib.get(self.keyId) is None:
            glyph.lib[self.keyId] = dict(contour_index=0, segment_index=0, anchor_t=0)
        self.anchored = True

    def anchorRuler(self, info, referencePointMethod=getCurrentPosition):
        glyph = info["glyph"]
        if len(glyph.contours) == 0:
            # for glyphs with only components
            glyph = copyDecomposedAndOverlaplessGlyph(glyph)

        _, contour_index, segment_index, anchor_t = (
            self.calculateDetailsForNearestPointOnCurve(
                referencePointMethod(info), glyph
            )
        )
        if None in (contour_index, segment_index, anchor_t):
            if self.keyId in glyph.lib.keys():
                del glyph.lib[self.keyId]
            self.anchored = False
            return
        glyph.lib[self.keyId] = dict(
            contour_index=contour_index, segment_index=segment_index, anchor_t=anchor_t
        )

        self.anchored = True

    def unanchorRuler(self, info):
        glyph = info["glyph"]
        if self.keyId in glyph.lib.keys():
            del glyph.lib[self.keyId]
        self.anchored = False

    def getGuidesAndAnchoredPoint(self, data, glyph):
        # position has to be there, but it will be set to None
        assert (
            data.get("position", None) is None
        ), f"something wrong with placement of getGuidesAndAnchoredPoint method (position is {position})"
        if not self.keyId in glyph.lib.keys():
            self.anchorRuler(dict(glyph=glyph), findMiddleOfTheGlyph)

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

        if cursorPosition != (-7000, -7000):  # if anchor exist
            return StemMath.calculateDetailsForNearestPointOnCurve(
                cursorPosition, glyph
            )

    def loadDefaults(self):
        self.ignoreOverlapsFlag = internalGetDefault("ignoreOverlapsFlag")
        self.measureAgainstComponents = internalGetDefault("measureAgainstComponents")
        self.measureAgainstSideBearings = internalGetDefault(
            "measureAgainstSideBearings"
        )

    def getGuidesAndClosestPoint(self, data, glyph):
        """returns 2 intersection lists"""
        closestPointsRef = []

        if data["position"] != (-7000, -7000):  # if anchor exist
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
                        l1, l2 = StemMath.stemThicknessGuidelines(
                            data["position"], seg.type, P1, P2
                        )

                    if len(points) == 4:
                        P1, P2, P3, P4 = points
                        P1, P2, P3, P4 = (
                            (P1.x, P1.y),
                            (P2.x, P2.y),
                            (P3.x, P3.y),
                            (P4.x, P4.y),
                        )
                        l1, l2 = StemMath.stemThicknessGuidelines(
                            data["position"], seg.type, P1, P2, P3, P4
                        )
                        #### TODO: Jesli seg.type == qcurve, to przerob to na StemMath.stemThicknessGuidelines(data["position"],seg.type,P1,P2,P3), wtedy zmien funkcje z TMath na takie, co to będą czystsze jesli chodzi o adekwatnosc do Cubic

                    closestPoint = l1[1]
                    closestPointsRef.append((closestPoint, l1, l2))

            distances = []

            for ref in closestPointsRef:
                point = ref[0]
                distance = StemMath.lengthAB(data["position"], point)
                distances.append(distance)

            indexOfClosestPoint = distances.index(min(distances))
            closestPointOnPathRef = closestPointsRef[indexOfClosestPoint]
            closestPointOnPath, guideline1, guideline2 = closestPointOnPathRef

            A1, B1 = guideline1
            A2, B2 = guideline2

            return guideline1, guideline2, closestPointOnPath

    currentMeasurement1 = None
    currentMeasurement2 = None

    def getThicknessData(self, data, glyph, method):
        italicSlangAngle = (
            glyph.font.info.italicAngle
            if glyph.font.info.italicAngle is not None
            else 0
        )

        italicSlantOffset = (
            glyph.font.lib.get("com.typemytype.robofont.italicSlantOffset", 0)
            if italicSlangAngle
            else 0
        )
        if len(glyph.contours) == 0:
            glyph = copyDecomposedGlyph(glyph)

        if self.ignoreOverlapsFlag and not self.measureAgainstComponents:
            glyph = copyOverlaplessGlyph(glyph)
        elif not self.ignoreOverlapsFlag and self.measureAgainstComponents:
            glyph = copyDecomposedGlyph(glyph)
        elif self.ignoreOverlapsFlag and self.measureAgainstComponents:
            glyph = copyDecomposedAndOverlaplessGlyph(glyph)

        if self.measureAgainstSideBearings:
            glyph = copyGlyphWithSidebearings(
                glyph, italicSlantOffset, italicSlangAngle
            )

        guideline1, guideline2, closestPointOnPath = method(data, glyph)

        textBoxCenter1 = None
        nearestP1 = closestPointOnPath
        thicknessValue1 = 0

        textBoxCenter2 = None
        nearestP2 = closestPointOnPath
        thicknessValue2 = 0

        intersectionAB1 = StemMath.find_intersectionsForDefconGlyph(
            glyph.naked(), *guideline1
        )
        intersectionAB2 = StemMath.find_intersectionsForDefconGlyph(
            glyph.naked(),
            *guideline2,
            # canHaveComponent=self.measureAgainstComponents,
            # addSideBearings=self.measureAgainstSideBearings,
        )

        # system of if-statemens to hack the iteration through nearestPoints = nearestPointFromList(closestPointOnPath,intersectionAB) kind of lists
        if len(intersectionAB1) != 0:
            nearestPoints1 = nearestPointFromList(closestPointOnPath, intersectionAB1)
            if StemMath.lengthAB(nearestPoints1[0], closestPointOnPath) < 2.5:
                # hack for guidelines going into space
                if len(nearestPoints1) == 1:
                    nearestP1 = nearestPoints1[0]

                else:
                    nearestP1 = nearestPoints1[1]
            else:
                nearestP1 = nearestPoints1[0]

            textBoxCenter1 = StemMath.calcLine(0.5, closestPointOnPath, nearestP1)
            thicknessValue1 = StemMath.lengthAB(closestPointOnPath, nearestP1)

        # system of if-statemens to hack the iteration through nearestPoints = self.nearestPointFromList(closestPointOnPath,intersectionAB) kind of lists
        if len(intersectionAB2) != 0:
            nearestPoints2 = nearestPointFromList(closestPointOnPath, intersectionAB2)
            if StemMath.lengthAB(nearestPoints2[0], closestPointOnPath) < 2.5:
                # hack for guidelines going into space
                if len(nearestPoints2) == 1:
                    nearestP2 = nearestPoints2[0]
                else:
                    nearestP2 = nearestPoints2[1]
            else:
                nearestP2 = nearestPoints2[0]

            textBoxCenter2 = StemMath.calcLine(0.5, closestPointOnPath, nearestP2)
            thicknessValue2 = StemMath.lengthAB(closestPointOnPath, nearestP2)

        ################
        # Named Values
        self.currentMeasurement1 = thicknessValue1
        self.currentMeasurement2 = thicknessValue2

        return (
            textBoxCenter1,
            thicknessValue1,
            nearestP1,
            textBoxCenter2,
            thicknessValue2,
            nearestP2,
            closestPointOnPath,
        )

    def clearNames(self):
        self.currentNames1 = None
        self.currentNames2 = None

    def findNames(self):
        self.clearNames()
        if self.currentMeasurement1 is None or self.currentMeasurement2 is None:
            return
        m1 = round(self.currentMeasurement1)
        names = self.namedWidthMeasurements1.get(m1, [])
        names += self.namedHeightMeasurements1.get(m1, [])
        if names:
            self.currentNames1 = names

        m2 = round(self.currentMeasurement2)
        names = self.namedWidthMeasurements2.get(m2, [])
        names += self.namedHeightMeasurements2.get(m2, [])
        if names:
            self.currentNames2 = names

    def loadNamedMeasurements(self, font):
        libKey = "com.typesupply.LaserMeasure.measurements"
        stored = font.lib.get(libKey, {})
        self.namedWidthMeasurements1 = {}
        self.namedWidthMeasurements2 = {}
        self.namedHeightMeasurements1 = {}
        self.namedHeightMeasurements2 = {}
        for name, data in stored.items():
            width = data.get("width")
            height = data.get("height")
            key = None
            location1 = None
            location2 = None

            if width is not None:
                location1 = self.namedWidthMeasurements1
                location2 = self.namedWidthMeasurements2
                key = width
                name = f"W: {name}"

            elif height is not None:
                location1 = self.namedHeightMeasurements1
                location2 = self.namedHeightMeasurements2
                key = height
                name = f"H: {name}"

            if location1 is not None:
                if key not in location1:
                    location1[key] = []
                location1[key].append(name)

            if location2 is not None:
                if key not in location2:
                    location2[key] = []
                location2[key].append(name)

        dicts = [
            self.namedWidthMeasurements1,
            self.namedWidthMeasurements2,
            self.namedHeightMeasurements1,
            self.namedHeightMeasurements2,
        ]
        for d in dicts:
            for d, v in d.items():
                v.sort()


try:
    key = "com.typesupply.LaserMeasure.measurementsChanged"
    subscriber.registerSubscriberEvent(
        subscriberEventName=key,
        methodName="fontMeasurementsChanged",
        lowLevelEventNames=[key],
        dispatcher="roboFont",
        delay=0.1,
    )
except AssertionError:
    pass


def main():
    from mojo.extensions import removeExtensionDefault

    subscriber.registerGlyphEditorSubscriber(StemPlowSubscriber)

    if AppKit.NSUserName() == "rafalbuchner":
        for key in defaults.keys():
            (key)
        registerExtensionDefaults(defaults)
