import ezui
from mojo.events import postEvent


from StemPlowSubscriber import (
    internalGetDefault,
    internalSetDefault,
    extensionID
)

# print(extensionID,
# internalGetDefault("measureAgainsComponents"),
# internalGetDefault("measureAgainsSideBearings"),
# internalGetDefault("triggerCharacter"),
# internalGetDefault("measurementTextSize"),
# internalGetDefault("textColor"),
# internalGetDefault("measurementLineSize"),
# internalGetDefault("measurementOvalSize"),
# internalGetDefault("mainColor"),
# internalGetDefault("lineColor"),
# internalGetDefault("ovalColor") )

class _StemPlowSettingsWindowController(ezui.WindowController):

    def build(self):
        content = """
        = TwoColumnForm

        : Measure:
        [ ] against Components                      @measureAgainsComponents
        :
        [ ] against SideBearings                    @measureAgainsSideBearings
        :
        [ ] always                                  @measureAlways

        ---

        : Trigger Character:
        [__]                                        @triggerCharacter

        ---

        : Text Size:
        [__] points                                 @measurementTextSize

        : Text Color:
        * ColorWell                                 @textColor

        ---
        : Oval Size:
        [__]                                        @measurementOvalSize

        : Line Size:
        [__]                                        @measurementLineSize

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
            measureAgainsComponents=dict(
                value=internalGetDefault("measureAgainsComponents")
            ),
            measureAgainsSideBearings=dict(
                value=internalGetDefault("measureAgainsSideBearings")
            ),
            measureAlways=dict(
                value=internalGetDefault("measureAlways")
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

    def started(self):
        self.w.open()

    def measureAgainsComponentsCallback(self, sender):
        self.mainCallback(sender)

    def measureAlwaysCallback(self, sender):
        self.mainCallback(sender)

    def measureAgainsSideBearingsCallback(self, sender):
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
        print(">> contentCallback", sender)
        key = sender.identifier
        value = sender.get()
        print(value)
        # for key, value in sender.getItemValues().items():
        existing = internalGetDefault(key)
        
        if existing == value:
            return
        if key == "triggerCharacter":
            if len(sender.get()) != 1:
                print(len(sender.get()))
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