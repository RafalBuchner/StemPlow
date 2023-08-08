import ezui
from mojo.events import postEvent


from stemPlow.StemPlowSubscriber import (
    internalGetDefault,
    internalSetDefault,
    extensionID
)

class _StemPlowSettingsWindowController(ezui.WindowController):

    def build(self):
        content = """
        = TwoColumnForm

        : Measure:
        [ ] against Components                      @measureAgainstComponents
        :
        [ ] against SideBearings                    @measureAgainstSideBearings
        :
        [ ] display Named Values from Laser Measure @showLaserMeasureNames
        :
        [ ] always                                  @measureAlways
        : Trigger behaviour:
        [ ] anchor guide to the outline             @useShortcutToMoveWhileAlways


        ---

        : Trigger Character:
        [__]                                        @triggerCharacter

        ---

        : Text Size:
        [_123_](±)                                @measurementTextSize

        : Text Color:
        * ColorWell                                 @textColor

        ---
        : Oval Size:
        [_123_](±)                                @measurementOvalSize

        : Line Size:
        [_123_](±)                                @measurementLineSize

        : Base Color:
        * ColorWell                                 @mainColor

        : Line Color:
        * ColorWell                                 @lineColor

        : Oval Color:
        * ColorWell                                 @ovalColor

        """
        colorWellWidth = 100
        colorWellHeight = 20
        numberEntryWidth = 75
        descriptionData = dict(
            content=dict(
                titleColumnWidth=125,
                itemColumnWidth=265
            ),
            measureAgainstComponents=dict(
                value=internalGetDefault("measureAgainstComponents")
            ),
            measureAgainstSideBearings=dict(
                value=internalGetDefault("measureAgainstSideBearings")
            ),
            showLaserMeasureNames=dict(
                value=internalGetDefault("showLaserMeasureNames")
            ),
            measureAlways=dict(
                value=internalGetDefault("measureAlways")
            ),
            useShortcutToMoveWhileAlways=dict(
                value=internalGetDefault("useShortcutToMoveWhileAlways")
            ),
            triggerCharacter=dict(
                width=20,
                value=internalGetDefault("triggerCharacter")
            ),
            measurementTextSize=dict(
                width=numberEntryWidth,
                valueType="number",
                value=internalGetDefault("measurementTextSize")
            ),
            textColor=dict(
                width=colorWellWidth,
                height=colorWellHeight,
                color=tuple(internalGetDefault("textColor"))
            ),
            measurementLineSize=dict(
                width=numberEntryWidth,
                valueType="number",
                value=internalGetDefault("measurementLineSize")
            ),
            measurementOvalSize=dict(
                width=numberEntryWidth,
                valueType="number",
                value=internalGetDefault("measurementOvalSize")
            ),

            mainColor=dict(
                width=colorWellWidth,
                height=colorWellHeight,
                color=tuple(internalGetDefault("mainColor"))
            ),
            lineColor=dict(
                width=colorWellWidth,
                height=colorWellHeight,
                color=tuple(internalGetDefault("lineColor"))
            ),
            ovalColor=dict(
                width=colorWellWidth,
                height=colorWellHeight,
                color=tuple(internalGetDefault("ovalColor"))
            )
        )
        self.w = ezui.EZWindow(
            title="Stem Plow Settings",
            content=content,
            descriptionData=descriptionData,
            controller=self
        )
        self.initialUiSetting()

    def initialUiSetting(self):
        measureAlways = self.w.getItem("measureAlways")
        useShortcutToMoveWhileAlways = self.w.getItem("useShortcutToMoveWhileAlways")
        if measureAlways.get():
            useShortcutToMoveWhileAlways.enable(True)
        else:
            useShortcutToMoveWhileAlways.enable(False)

    def started(self):
        self.w.open()

    def measureAgainstComponentsCallback(self, sender):
        self.mainCallback(sender)

    def measureAlwaysCallback(self, sender):
        useShortcutToMoveWhileAlways = self.w.getItem("useShortcutToMoveWhileAlways")
        if sender.get():
            useShortcutToMoveWhileAlways.enable(True)
        else:
            useShortcutToMoveWhileAlways.enable(False)
        self.mainCallback(sender)

    def useShortcutToMoveWhileAlwaysCallback(self, sender):
        self.mainCallback(sender)

    def measureAgainstSideBearingsCallback(self, sender):
        self.mainCallback(sender)

    def showLaserMeasureNamesCallback(self, sender):
        self.mainCallback(sender)

    def triggerCharacterCallback(self, sender):
        self.mainCallback(sender)

    def measurementTextSizeCallback(self, sender):
        self.mainCallback(sender)

    def textColorCallback(self, sender):
        self.mainCallback(sender)

    def measurementLineSizeCallback(self, sender):
        self.mainCallback(sender)

    def measurementOvalSizeCallback(self, sender):
        self.mainCallback(sender)

    def mainColorCallback(self, sender):
        self.mainCallback(sender)

    def lineColorCallback(self, sender):
        self.mainCallback(sender)

    def ovalColorCallback(self, sender):
        self.mainCallback(sender)

    def mainCallback(self, sender):
        key = sender.identifier
        value = sender.get()

        existing = internalGetDefault(key)

        if existing == value:
            return
        if key == "triggerCharacter":
            if len(sender.get()) != 1:
                return
        internalSetDefault(key, value)
        postEvent(
            extensionID + ".defaultsChanged"
        )



note = """
The settings window is only available in
RoboFont 4.2+
""".strip()

def StemPlowSettingsWindowController(*args, **kwargs):
    from mojo import roboFont

    version = roboFont.version
    versionMajor, versionMinor = version.split(".", 1)
    versionMinor = versionMinor.split(".")[0]
    versionMajor = "".join([i for i in versionMajor if i in "0123456789"])
    versionMinor = "".join([i for i in versionMinor if i in "0123456789"])
    versionMajor = int(versionMajor)
    versionMinor = int(versionMinor)
    if versionMajor == 4 and versionMinor < 2:
        print(note)
    else:
        _StemPlowSettingsWindowController(*args, **kwargs)

if __name__ == "__main__":
    StemPlowSettingsWindowController()
