##########################################################################################
#
#	Stem Plow 1.0
#	Visualisation tool for stem thickness
#
#	Commercial license. Not to be given to other people.
#
#	Copyright 2018 by Rafal Buchner.
#	Twitter: @rafalbuchner
#   email: rafalbuchner@gmail.com
#
##########################################################################################
import os
from AppKit import NSImage
from mojo.events import EditingTool, installTool
from mojo.tools import IntersectGlyphWithLine
from mojo.UI import UpdateCurrentGlyphView
from mojo.extensions import ExtensionBundle
from mojo.drawingTools import *
import TMath_binary
from Cocoa import (NSFont, NSFontAttributeName,
    NSColor, NSForegroundColorAttributeName)


bundle = ExtensionBundle("Stem Plow")
toolbar_icon = bundle.getResourceImage("StemPlow-icon",ext='pdf')

def drawPoint(p,s=10,color=(0.6,0.2,0.5)):
    x,y=p
    fill(*color)
    stroke(None)
    oval(x-s/2,y-s/2,s,s)

class StemPlowTool(EditingTool):

    def setup(self):
        self.position = None
        self.closestPointOnPath = None
        self.isThickness1 = None
        self.isThickness2 = None
        self.view = self.getNSView()

    def mouseMoved(self, point):
        self.position = point
        self.position = (self.position.x,self.position.y)
        UpdateCurrentGlyphView()

    def drawBackground(self, scale):
        # scale = 1/scale

        self.g= self.getGlyph()
        if self.position:
            thickness1 = 0
            thickness2 = 0


            guideline1, guideline2, self.closestPointOnPath = self.keyDownDraw()
            if TMath_binary.lenghtAB(self.position,self.closestPointOnPath) < 77:
                intersectionAB1 = IntersectGlyphWithLine(self.g, guideline1)
                intersectionAB2 = IntersectGlyphWithLine(self.g, guideline2)


                font("Monaco", 10*(scale))
                strokeWidth(2*(scale))


                # system of if-statemens to hack the iteration through nearestPoints = self.nearestPointFromList(self.closestPointOnPath,intersectionAB) kind of lists
                if len(intersectionAB1) != 0:
                    nearestPoints1 = self.nearestPointFromList(self.closestPointOnPath,intersectionAB1)
                    if TMath_binary.lenghtAB(nearestPoints1[0],self.closestPointOnPath) < 2.5 :

                        # hack for guidelines going into space
                        if len(nearestPoints1) == 1:
                            self.nearestP1 = nearestPoints1[0]

                        else:
                            self.nearestP1 = nearestPoints1[1]
                    else:
                        self.nearestP1 = nearestPoints1[0]

                    centre1 = TMath_binary.calcLine(.5,self.closestPointOnPath,self.nearestP1)
                    thickness1 = TMath_binary.lenghtAB(self.closestPointOnPath,self.nearestP1)
                    thicknessLine1 = (self.closestPointOnPath,self.nearestP1)

                    fill(0.1,0.2,0.3,.95)

                    lineDash(10*(scale))
                    stroke(1,0,0)
                    line(*thicknessLine1)

                # system of if-statemens to hack the iteration through nearestPoints = self.nearestPointFromList(self.closestPointOnPath,intersectionAB) kind of lists
                if len(intersectionAB2) != 0:
                    nearestPoints2 = self.nearestPointFromList(self.closestPointOnPath,intersectionAB2)
                    if TMath_binary.lenghtAB(nearestPoints2[0],self.closestPointOnPath) < 2.5 :

                        # hack for guidelines going into space
                        if len(nearestPoints2) == 1:
                            self.nearestP2 = nearestPoints2[0]
                        else:
                            self.nearestP2 = nearestPoints2[1]
                    else:
                        self.nearestP2 = nearestPoints2[0]

                    centre2 = TMath_binary.calcLine(.5,self.closestPointOnPath,self.nearestP2)
                    thickness2 = TMath_binary.lenghtAB(self.closestPointOnPath,self.nearestP2)
                    thicknessLine2 = (self.closestPointOnPath,self.nearestP2)

                    fill(0.1,0.2,0.3,.95)

                    lineDash(10*(scale))
                    stroke(0,0,1)
                    line(*thicknessLine2)

                self.isThickness1 = False

                if round(thickness1) != 0 or round(thickness2) != 0:
                    ####
                    font1 = NSFont.fontWithName_size_("Monaco", 10.0)
                    color1 = NSColor.whiteColor()
                    bcColor = NSColor.grayColor()
                    attr = {
                            NSFontAttributeName: font1,
                            NSForegroundColorAttributeName: color1
                        }
                if round(thickness1) != 0:
                    self.isThickness1 = True

                    #drawTextBox(centre1,str(round(thickness1,2)),34*(scale),18*(scale),4*(scale))


                    #help(self.view.drawTextInRect)
                    # Copy it to the other measurement
                    self.view._drawTextInRect(str(round(thickness1,2)),
                    attr, centre1, yOffset=0, xOffset=0, drawBackground=True, position="center", backgroundColor=bcColor)
                    #                        inputText,              attributes, pos, yOffset=0, xOffset=0, drawBackground=False, position="center", backgroundColor=None

                self.isThickness2 = False
                if round(thickness2) != 0:

                    self.isThickness2 = True
                    self.view._drawTextInRect(str(round(thickness2,2)),
                    attr, centre2, yOffset=0, xOffset=0, drawBackground=True, position="center", backgroundColor=bcColor)
                    #drawTextBox(centre2,str(round(thickness2,2)),34*(scale),18*(scale),4*(scale))



            # drawPoint(self.position,s=6*(scale))
    def draw(self,scale):
        if TMath_binary.lenghtAB(self.position,self.closestPointOnPath) < 77 and self.closestPointOnPath != None:
            drawPoint(self.closestPointOnPath,s=7*(scale),color=(1,.4,0))

            if self.isThickness1:
                drawPoint(self.nearestP1,s=7*(scale),color=(1,0,0))

            if self.isThickness2:
                drawPoint(self.nearestP2,s=7*(scale),color=(0,0,1))

    def getToolbarTip(self):
        return "Stem Plow tool"

    def keyDownDraw(self):
        """returns 2 intersection lists"""
        closestPointsRef = []

        if self.position != (-3000,-3000): # if anchor exist

            for contour in self.g.contours:
                segs = contour.segments

                for segIndex, seg in enumerate(segs):

                    # rebuilding segment into system 2 points for line and 4 for curve (TMath_binary needs it):
                    points = [segs[segIndex-1][-1]] # 1adding last point from previous segment
                    for point in seg.points:
                        points.append(point) # 2 adding rest of points of the segment

                    if len(points) == 2:
                        P1,P2=points

                        # making sure that extension doesn't take open segment of the contour into count
                        if P1.type == "line" and P2.type == "move":
                            continue

                        P1,P2=((P1.x,P1.y),(P2.x,P2.y))
                        l1,l2 = TMath_binary.stemThicnkessGuidelines(self.position,seg.type,P1,P2)


                    if len(points) == 4:
                        P1,P2,P3,P4=points
                        P1,P2,P3,P4=((P1.x,P1.y),(P2.x,P2.y),(P3.x,P3.y),(P4.x,P4.y))
                        l1,l2 = TMath_binary.stemThicnkessGuidelines(self.position,seg.type,P1,P2,P3,P4)


                    closestPoint = l1[1]
                    closestPointsRef.append((closestPoint,l1,l2))

            distances = []

            for ref in closestPointsRef:
                point = ref[0]
                distance = TMath_binary.lenghtAB(self.position,point)
                distances.append(distance)

            indexOfClosestPoint = distances.index(min(distances))
            closestPointOnPathRef = closestPointsRef[indexOfClosestPoint]
            closestPointOnPath, guideline1, guideline2 = closestPointOnPathRef

            A1,B1 = guideline1
            A2,B2 = guideline2

            return guideline1,guideline2, closestPointOnPath

    def nearestPointFromList(self,myPoint,points):

        def _sorter(point):
            return TMath_binary.lenghtAB(myPoint, point)

        points = sorted(points, key=_sorter)
        return points

    def additionContextualMenuItems(self):
        return [
            ("add Stem Plow Guideline", self.stemPlowGuide),
        ]

    def stemPlowGuide(self, sender):
        bundle = ExtensionBundle("Stem Plow")
        #print(bundle.get("StemPlow-icon"))
        self.g = self.getGlyph()
        closestPointsRef = []

        if self.position != (-3000,-3000): # if anchor exist

            for contour in self.g.contours:
                segs = contour.segments

                for seg in segs:
                    segIndex = segs.index(seg)

                    # rebuilding segment into system 2 points for line and 4 for curve (TMath_binary needs it):
                    points = [segs[segIndex-1][-1]] # 1adding last point from previous segment
                    for point in seg.points:
                        points.append(point) # 2 adding rest of points of the segment

                    if len(points) == 2:
                        P1,P2=points
                        P1,P2=((P1.x,P1.y),(P2.x,P2.y))
                        l1,l2 = TMath_binary.stemThicnkessGuidelines(self.position,seg.type,P1,P2)



                    if len(points) == 4:
                        P1,P2,P3,P4=points
                        P1,P2,P3,P4=((P1.x,P1.y),(P2.x,P2.y),(P3.x,P3.y),(P4.x,P4.y))
                        l1,l2 = TMath_binary.stemThicnkessGuidelines(self.position,seg.type,P1,P2,P3,P4)

                    closestPoint = l1[1]
                    closestPointsRef.append((closestPoint,l1,l2))

            distances = []

            for ref in closestPointsRef:
                point = ref[0]
                distance = TMath_binary.lenghtAB(self.position,point)
                distances.append(distance)

            indexOfClosestPoint = distances.index(min(distances))
            closestPointOnPathRef = closestPointsRef[indexOfClosestPoint]
            closestPointOnPath, guideline1, guideline2 = closestPointOnPathRef

            angle1 = TMath_binary.angle(*guideline1)
            posX,posY = self.position
            self.g.appendGuideline(closestPointOnPath,angle1)
            self.g.guidelines[-1].showMeasurements = 1

    def getToolbarIcon(self):
        return toolbar_icon

installTool(StemPlowTool())
