import StemMath
import math

def closestPointAndT_binaryIndexSearch_withSegments(pointOffCurve, segment, *segPoints):
    """Returns returns the curve, which is segment cutted from the given curve.
    it returns more info on curve than method closestPointAndT_binaryIndexSearch.
    Therefore it is heavier
    """
    curveDiv = 12

    lowerBound = 0
    upperBound = curveDiv - 1
    found = False
    count = 0
    points = segPoints
    curr_t = 1
    left_count = 0
    right_count = 0
    while found == False:
        if count == 10:
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
        
        print(curr_t)
        if t >= 0.5:
            points = points2
            # curr_t += 1 # you have to reanalize this!!!# TODO it should be completley different
            left_count +=1
        else:
            points = points1
            right_count +=1
            # curr_t -= 1 # you have to reanalize this!!!# TODO it should be completley different
    print(f"l:{left_count}, r:{right_count}\n",abs(right_count-left_count), math.pow(1,abs(right_count-left_count) ))

    #curr_t = 0.5 + math.pow(curr_t,0.5)
    return (points, (segment.contour.index, segment.index, segPoints, curr_t))

myGlyph = CurrentGlyph()
groupLayer = container.appendBaseSublayer(
    size=(1000, 1000)
)

############
# Drawing Line

g = CurrentGlyph()
print(g.contours[0].points)
A, B, C, D = g.contours[0].points[0].position, g.contours[0].points[1].position, g.contours[0].points[2].position, g.contours[0].points[3].position
points = (A, B, C, D)
pointsLine = (A, B)
lineLayer = groupLayer.appendLineSublayer(
    startPoint=A,
    endPoint=B,
    strokeWidth=1,
    strokeColor=(1, 0, 0, 1)
)

start = groupLayer.appendSymbolSublayer(
    position=(A[0]-1,A[1]),
)
start.setImageSettings(
    dict(
        name="rectangle",
        size=(2, 30),
        fillColor=(1, 0, 0, 1)
    )
)

end = groupLayer.appendSymbolSublayer(
    position=(B[0]+15,B[1]),
)
end.setImageSettings(
    dict(
        name="triangle",
        size=(30, 30),
        fillColor=(1, 0, 0, 1)
    )
)

# End Drawing
##########

# a layer for the glyph and the baseline

def interpolate_AB(A, B, t):
    def interpolation(v1, v2, t):
        vt = v1 * (1 - t) + v2 * t
        return vt
    ax, ay = A
    bx, by = B
    return interpolation(ax, bx, t), interpolation(ay, by, t)

segment = g.contours[0].segments[0]
print(segment.type)
t = 0.75
T = interpolate_AB(A, B, t)
pointOffCurve = T
_, info = closestPointAndT_binaryIndexSearch_withSegments(pointOffCurve, segment, *points)
contourIdx, segmentIdx, segPoints, curr_t = info

C = interpolate_AB(A,B,curr_t)#StemMath.calcLine(curr_t, pointsLine)
print(C, curr_t)
############
# Drawing T
T = groupLayer.appendSymbolSublayer(
    position=(pointOffCurve[0],pointOffCurve[1]-10),
)
T.setImageSettings(
    dict(
        name="oval",
        size=(14, 14),
        fillColor=(0, 1, 0.3, 0.5)
    )
)

c = groupLayer.appendSymbolSublayer(
    position=(C[0],C[1]+10),
)
c.setImageSettings(
    dict(
        name="oval",
        size=(14, 14),
        fillColor=(0, 0.3, 1, 0.5)
    )
)

