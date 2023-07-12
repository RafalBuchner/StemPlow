##########################################################################################
#
#	Stem Plow 1.0
#	Visualisation tool for stem thickness
#
#	Commercial license. Not to be given to other people.
#
#	Copyright 2018 by Rafal Buchner.
#	Twitter: @rafalbuchner
#   email: hello@rafalbuchner.com
#
##########################################################################################
import os
from AppKit import NSImage
from mojo.events import EditingTool, installTool
from mojo.tools import IntersectGlyphWithLine
from mojo.UI import UpdateCurrentGlyphView
from mojo.extensions import ExtensionBundle
from mojo.drawingTools import *
import StemMath
from Cocoa import (NSFont, NSFontAttributeName,
    NSColor, NSForegroundColorAttributeName)


bundle = ExtensionBundle("StemPlow")
toolbar_icon = bundle.getResourceImage("StemPlow-icon",ext='pdf')

def drawPoint(p,s=10,color=(0.6,0.2,0.5)):
    x,y=p
    fill(*color)
    stroke(None)
    oval(x-s/2,y-s/2,s,s)

class StemPlowTool(EditingTool):

    def setup(self):
        print("SETUP")
        container = self.extensionContainer(
            identifier="com.rafal.drawsStuff",
            location="foreground",
            clear=True)

        self.merzGuide1 = container.appendLineSublayer(
           startPoint=(0, 0),
           endPoint=(0, 0),
           strokeWidth=1,
           strokeColor=(1, 0, 0, 1)
        )
        self.merzGuide2 = container.appendLineSublayer(
           startPoint=(0, 0),
           endPoint=(0, 0),
           strokeWidth=1,
           strokeColor=(0, 0, 1, 1)
        )

    def mouseMoved(self, point):
        x, y = point.x, point.y
        self.merzGuide1.setStartPoint((x, y))

    def additionContextualMenuItems(self):
        return [
            ("add Stem Plow Guideline", self.stemPlowGuide),
        ]

    def stemPlowGuide(self, sender):
        pass

    def getToolbarIcon(self):
        return toolbar_icon

installTool(StemPlowTool())
