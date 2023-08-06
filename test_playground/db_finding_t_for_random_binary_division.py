import drawBot as bot
import StemMath
import math
def dp(p):
    x, y = p
    s = 10
    r = s/2
    oval(x-r,y-r,s,s)
def dx(p):
    # a   c #
    #   p   #
    # d   b #
    x, y = p
    s = 10
    r = s/2
    x+=r
    y+=r
    a = (x-s,y)
    b = (x,y-s)
    c = (x-s,y-s)
    d = (x,y)
    line(a,b)
    line(c,d)
    
def drawSeg(points):
    if len(points) == 2:
        bot.line(*points)
    else:
        fill(None)
        a,b,c,d = points
        bot.newPath()
        bot.moveTo(a)
        bot.curveTo(b,c,d)
        bot.drawPath()
def drawSeg_and_Point(pointOffCurve, segPoints):
    ############
    # Drawing Line
    bot.stroke(0)
    if len(segPoints) == 2:
        bot.line(*segPoints)
    else:
        fill(None)
        a,b,c,d = segPoints
        bot.newPath()
        bot.moveTo(a)
        bot.curveTo(b,c,d)
        bot.drawPath()
    bot.stroke(1,0,0)
    bot.fill(1,1,0)
    dp(pointOffCurve)
    # End Drawing
    ##########
def calcSeg(t, *points):
    assert isinstance(t, float) or isinstance(t, int) , "calcSeg ERROR: t is not a float"

    if len(points) == 2:
        a, b = points
        point = StemMath.calcLine(t, a, b)
    if len(points) == 4:
        a, b, c, d = points
        point = StemMath.calcBezier(t, a, b, c, d)

    return point
def closestPointAndT_binaryIndexSearch_withSegments(pointOffCurve, segment, *segPoints):

    curveDiv = 12

    lowerBound = 0
    upperBound = curveDiv - 1
    found = False
    count = 0
    points = segPoints
    left_count = 0
    right_count = 0
    curr_left_t = 0
    curr_mid_t = 0.5
    next_mid_t = curr_mid_t
    curr_right_t = 1
    while found == False:
        
        if count == 12:
            break
        count += 1
        LUT = StemMath.getLut(segment.type, curveDiv, *points)
        minimalDist = 20000

        for i in range(curveDiv + 1):
            n = (i, i / curveDiv)
            distance = StemMath.lenghtAB(pointOffCurve, LUT[n])

            if distance < minimalDist:
                minimalDist = distance
                t = n[1]

        
        points1, points2 = StemMath.splitSegAtT(segment.type, points, 0.5)

        if t >= 0.5:
            # right side choosen
            points = points2
            left_count +=1 #?
            next_left_t = curr_mid_t
            next_right_t = curr_right_t
            next_mid_t = (next_right_t - next_left_t) * 0.5 + curr_mid_t
        else:
            # left side choosen
            points = points1
            right_count +=1 #?
            next_left_t = curr_left_t
            next_right_t = curr_mid_t
            next_mid_t = StemMath.interpolation(next_right_t, next_left_t, 0.5)

        bot.newPage(1000,500) #bot
        with savedState():
            bot.translate(0,-500)
            oncurve_lookint = calcSeg(curr_mid_t, *segPoints)
            bot.fill(None)
            bot.stroke(1,0.5,0)
            line(oncurve_lookint, pointOffCurve)
            bot.stroke(0)
            drawSeg_and_Point(pointOffCurve, segPoints)
            bot.strokeWidth(4)
            
            bot.stroke(1,0.5,0)
            
            
            dx(oncurve_lookint)
            
             
            bot.stroke(1,0,0)
            drawSeg(points1)
            bot.stroke(0,0,1)
            drawSeg(points2)
            bot.fill(0)
            bot.stroke(None)
            txt = bot.FormattedString(f"(step: {count:02d}) l:{left_count} | r:{right_count}\n{' '*11}", font="Menlo", fontSize=20)
            txt.append(f"l {curr_left_t}", fill=(1, 0, 0))
            txt.append(f" | ", fill=(0, 0, 0))
            txt.append(f"m {curr_mid_t}", fill=(.7))
            txt.append(f" | ", fill=(0, 0, 0))
            txt.append(f"r {curr_right_t}\n{' '*11}", fill=(0, 0, 1))
            txt.append(f"nl {next_left_t}", fill=(1, 0, 0))
            txt.append(f" | ", fill=(0, 0, 0))
            txt.append(f"nm {next_mid_t}", fill=(.7))
            txt.append(f" | ", fill=(0, 0, 0))
            txt.append(f"nr {next_right_t}\n{' '*11}", fill=(0, 0, 1))
            txt.append(f"t for step {count}: {next_mid_t}", fill=(0, 0, 0))
            bot.text(txt,(20,950))
            
        
        # combine it later with previous if statement
        # now it is here just because of drawbot functions
        curr_left_t = next_left_t
        curr_mid_t = next_mid_t
        curr_right_t = next_right_t
    return (points, (segment.contour.index, segment.index, segPoints, curr_mid_t))




# a layer for the glyph and the baseline

g = CurrentGlyph()
A, B, C, D = g.contours[0].points[0].position, g.contours[0].points[1].position, g.contours[0].points[2].position, g.contours[0].points[3].position
points = (A, B, C, D)
pointsLine = (A, B)

segment = g.contours[0].segments[0]

t = 0.2
T = calcSeg(t, *points)
pointOffCurve = (700, 800)
closestPointAndT_binaryIndexSearch_withSegments(pointOffCurve, segment, *points)

saveImage("test.mp4")



