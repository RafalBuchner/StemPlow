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

def nearestPointFromList(myPoint,points):

        def _sorter(point):
            return StemMath.lenghtAB(myPoint, point)

        points = sorted(points, key=_sorter)
        return points

class StemPlowTool(EditingTool):
    distanceTreshold = 77
    textBoxSize = (42,12)
    ovalSize = (6, 6)
    redColor = (1, 0, 0, .7)
    blueColor = (0, 0, 1, .7)
    hidePosition = (-10000, -10000)
    def setup(self):
        print("SETUP")
        fg_container = self.extensionContainer(
            identifier="com.rafal.drawsStuff",
            location="foreground",
            clear=True)
        # fg_container = self.extensionContainer(
        #     identifier="com.rafal.drawsStuff",
        #     location="background",
        #     clear=True)

        self.merzGuide1 = fg_container.appendLineSublayer(
           startPoint=self.hidePosition,
           endPoint=self.hidePosition,
           strokeWidth=1,
           strokeColor=self.redColor
        )
        self.merzText1 = fg_container.appendTextBoxSublayer(
           position=self.hidePosition,
           size=self.textBoxSize,
           font="Menlo",
           backgroundColor=self.redColor,
           pointSize=10,
           fillColor=(1, 1, 1, 1),
           alignment="center"
        )
        self.merzGuide2 = fg_container.appendLineSublayer(
           startPoint=self.hidePosition,
           endPoint=self.hidePosition,
           strokeWidth=1,
           strokeColor=self.blueColor
        )
        self.merzText2 = fg_container.appendTextBoxSublayer(
           position=self.hidePosition,
           size=self.textBoxSize,
           font="Menlo",
           backgroundColor=self.blueColor,
           pointSize=10,
           fillColor=(1, 1, 1, 1)
        )
        self.merzOval1 = fg_container.appendOvalSublayer(
           position=self.hidePosition,
           size=self.ovalSize,
           fillColor=self.redColor
        )
        self.merzOval2 = fg_container.appendOvalSublayer(
           position=self.hidePosition,
           size=self.ovalSize,
           fillColor=self.blueColor
        )
        self.merzOvalHit = fg_container.appendOvalSublayer(
           position=self.hidePosition,
           size=self.ovalSize,
           fillColor=(0, 0, 0, .3)
        )
        self.merzText1.setCornerRadius(4)
        self.merzText1.setHorizontalAlignment("center")
        self.merzText2.setCornerRadius(4)
        self.merzText2.setHorizontalAlignment("center")

    def mouseDragged(self, point, delta):
        self.mouseMoved(point)

    def mouseMoved(self, point):
        if len(self.g.contours) == 0:
            return

        self.position = (point.x, point.y)

        thickness1 = 0
        thickness2 = 0

        guideline1, guideline2, closestPointOnPath = self.keyDownDraw()
        if StemMath.lenghtAB(self.position,closestPointOnPath) < 77:
            intersectionAB1 = IntersectGlyphWithLine(self.g, guideline1)
            intersectionAB2 = IntersectGlyphWithLine(self.g, guideline2)

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
                thickness1 = StemMath.lenghtAB(closestPointOnPath,nearestP1)
                thicknessLine1 = (closestPointOnPath,nearestP1)

                

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
                thickness2 = StemMath.lenghtAB(closestPointOnPath,nearestP2)
                thicknessLine2 = (closestPointOnPath,nearestP2)

                a,b = thicknessLine2
                self.merzGuide2.setStartPoint(a)
                self.merzGuide2.setEndPoint(b)

            if round(thickness1) != 0 or round(thickness2) != 0:
                x,y = closestPointOnPath
                x -= self.ovalSize[0]/2
                y -= self.ovalSize[1]/2
                self.merzOvalHit.setPosition((x,y))
                self.merzOvalHit.setVisible(True)
            else:
                self.merzOvalHit.setVisible(False)

            # draw text boxes and intersection indicators
            if round(thickness1) != 0:
                self.merzText1.setVisible(True)
                self.merzOval1.setVisible(True)
                self.merzGuide1.setVisible(True)
                txt = str(round(thickness1,2))
                x,y = center1
                x -= self.textBoxSize[0]/2
                y -= self.textBoxSize[1]/2
                self.merzText1.setPosition((x,y))
                self.merzText1.setText(txt)
                x,y = nearestP1
                x -= self.ovalSize[0]/2
                y -= self.ovalSize[1]/2
                self.merzOval1.setPosition((x,y))

                a,b = thicknessLine1
                self.merzGuide1.setStartPoint(a)
                self.merzGuide1.setEndPoint(b)
                
                

            else:
                self.merzText1.setVisible(False)
                self.merzOval1.setVisible(False)
                self.merzGuide1.setVisible(False)

            if round(thickness2) != 0:
                self.merzText2.setVisible(True)
                self.merzOval2.setVisible(True)
                self.merzGuide2.setVisible(True)
                txt = str(round(thickness2,2))
                x,y = center2
                x -= self.textBoxSize[0]/2
                y -= self.textBoxSize[1]/2
                self.merzText2.setPosition((x,y))
                self.merzText2.setText(txt)
                x,y = nearestP2
                x -= self.ovalSize[0]/2
                y -= self.ovalSize[1]/2
                self.merzOval2.setPosition((x,y))

                a,b = thicknessLine2
                self.merzGuide2.setStartPoint(a)
                self.merzGuide2.setEndPoint(b)
                
            else:
                self.merzText2.setVisible(False)
                self.merzOval2.setVisible(False)
                self.merzGuide2.setVisible(False)

        else:
            self.merzOvalHit.setVisible(False)
            self.merzText1.setVisible(False)
            self.merzOval1.setVisible(False)
            self.merzText2.setVisible(False)
            self.merzOval2.setVisible(False)
            self.merzGuide1.setVisible(False)
            self.merzGuide1.setVisible(False)
            self.merzGuide2.setVisible(False)
            self.merzGuide2.setVisible(False)
                




    def keyDownDraw(self):
        """returns 2 intersection lists"""
        closestPointsRef = []

        if self.position != (-3000,-3000): # if anchor exist

            for contour in self.g.contours:
                segs = contour.segments

                for segIndex, seg in enumerate(segs):

                    # rebuilding segment into system 2 points for line and 4 for curve (StemMath needs it):
                    points = [segs[segIndex-1][-1]] # 1adding last point from previous segment

                    for point in seg.points:
                        points.append(point) # 2 adding rest of points of the segment

                    if len(points) == 2:
                        P1,P2=points

                        # making sure that extension doesn't take open segment of the contour into count
                        if P1.type == "line" and P2.type == "move":
                            continue

                        P1,P2=((P1.x,P1.y),(P2.x,P2.y))
                        l1,l2 = StemMath.stemThicnkessGuidelines(self.position,seg.type,P1,P2)


                    if len(points) == 4:
                        P1,P2,P3,P4=points
                        P1,P2,P3,P4=((P1.x,P1.y),(P2.x,P2.y),(P3.x,P3.y),(P4.x,P4.y))
                        l1,l2 = StemMath.stemThicnkessGuidelines(self.position,seg.type,P1,P2,P3,P4)
                        #### TODO: Jesli seg.type == qcurve, to przerob to na StemMath.stemThicnkessGuidelines(self.position,seg.type,P1,P2,P3), wtedy zmien funkcje z TMath na takie, co to będą czystsze jesli chodzi o adekwatnosc do Cubic


                    closestPoint = l1[1]
                    closestPointsRef.append((closestPoint,l1,l2))

            distances = []

            for ref in closestPointsRef:
                point = ref[0]
                distance = StemMath.lenghtAB(self.position,point)
                distances.append(distance)

            indexOfClosestPoint = distances.index(min(distances))
            closestPointOnPathRef = closestPointsRef[indexOfClosestPoint]
            closestPointOnPath, guideline1, guideline2 = closestPointOnPathRef

            A1,B1 = guideline1
            A2,B2 = guideline2

            return guideline1,guideline2, closestPointOnPath
    

    def currentGlyphChanged(self):
        print("currentGlyphChanged")
        self._assignGlyph()

    def becomeActive(self):
        print("becomeActive")
        self._assignGlyph()

    def _assignGlyph(self):
        self.g = self.getGlyph()

    def additionContextualMenuItems(self):
        return [
            ("add Stem Plow Guideline", self.stemPlowGuide),
        ]

    def stemPlowGuide(self, sender):
        pass

    def getToolbarIcon(self):
        return toolbar_icon

installTool(StemPlowTool())
