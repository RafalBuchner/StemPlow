
from mojo import subscriber
from mojo import events

extensionID = "com.rafalbuchner.StemPlow"
extensionKeyStub = extensionID + "."


defaults = {
    extensionKeyStub + "triggerCharacter" : "s",
    extensionKeyStub + "lineColor" : (0, 0.3, 1, 0.8),
    extensionKeyStub + "ovalColor" : (0, 0.3, 1, 0.8),
    extensionKeyStub + "textColor" : (0, 0.3, 1, 0.8),
    extensionKeyStub + "measurementOvalSize" : 6,
    extensionKeyStub + "measurementLineSize" : 1,
    extensionKeyStub + "measurementTextSize" : 12,
}

registerExtensionDefaults(defaults)

def internalGetDefault(key):
    key = extensionKeyStub + key
    return getExtensionDefault(key)

def internalSetDefault(key, value):
    key = extensionKeyStub + key
    setExtensionDefault(key, value)


class StemPlow(subscriber.Subscriber):
    debug = True

    def build(self):
        window = self.getGlyphEditor()
        self.activeContainer = window.extensionContainer(
            identifier=extensionKeyStub + "background",
            location="background",
            clear=True
        )
        self.textContainer = window.extensionContainer(
            identifier=extensionKeyStub + "foreground",
            location="foreground",
            clear=True
        )

        # text
        
        self.textBaseLayer = self.textContainer.appendBaseSublayer(
            visible=True
        )
        
        self.textLayer = self.textBaseLayer.appendTextLineSublayer(
            visible=False,
            name="measurements"
        )

        # outline

        self.lineBaseLayer = self.activeContainer.appendBaseSublayer(
            visible=False
        )
        self.lineLayer = self.outlineBaseLayer.appendLineSublayer()
        self.oval_ALayer = self.outlineBaseLayer.appendOvalSublayer()
        self.oval_BLayer = self.outlineBaseLayer.appendOvalSublayer()
        self.oval_CLayer = self.outlineBaseLayer.appendOvalSublayer()

        # register for defaults change
        events.addObserver(
            self,
            "extensionDefaultsChanged",
            extensionID + ".defaultsChanged"
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
        lineColor = internalGetDefault("lineColor")
        ovalColor = internalGetDefault("ovalColor")
        textColor = internalGetDefault("textColor")

        
        # build
        lineAttributes = dict(
            strokeColor=lineColor,
            strokeWidth=measurementLineSize
        )
        textAttributes = dict(
            backgroundColor=mainColor,
            fillColor=textColor,
            padding=(6, 3),
            cornerRadius=5,
            horizontalAlignment="center",
            verticalAlignment="center",
            pointSize=textSize,
            font="Menlo"
        )
        ovalAttributes = dict(
            size=measurementOvalSize,
           fillColor=ovalColor
           )
        
        
        selectionNamesTextAttributes = dict(selectionMeasurementsTextAttributes)
        # populate
        self.textLayer.setPropertiesByName(textAttributes)
        self.lineLayer.setPropertiesByName(lineAttributes)
        for oval in [self.oval_ALayer,
                        self.oval_BLayer,
                        self.oval_CLayer]:
            oval.setPropertiesByName(ovalAttributes)


    def destroy(self):
        self.activeContainer.clearSublayers()
        self.textContainer.clearSublayers()
        events.removeObserver(
            self,
            extensionID + ".defaultsChanged"
        )

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


    def glyphEditorDidSetGlyph(self, info):
        self.g = info["glyph"]

    def glyphEditorDidKeyDown(self, info):
        NotImplemented

    def glyphEditorDidKeyUp(self, info):
        self.hideLayers()
        # setCursorMode(None)

    def glyphEditorDidMouseDown(self, info):
        self.hideLayers()
        # setCursorMode(None)

    def glyphEditorDidMouseMove(self, info):
        NotImplemented

    # Text
    # ----

    def clearText(self):
        self.measurement1 = None
        self.measurement2 = None

    def updateText(self):
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

if __name__ == '__main__':
    subscriber.registerGlyphEditorSubscriber(StemPlow)