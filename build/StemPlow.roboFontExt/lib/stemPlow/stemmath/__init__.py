from __future__ import division

import math
from dataclasses import dataclass
from numbers import Number
from typing import Any, Sequence

from fontParts.base import BaseSegment
from fontTools.misc.bezierTools import splitCubicAtT, splitQuadraticAtT
from icecream import ic

ACCURACY = 18


@dataclass
class SegmentInfo:
    type: str
    contour: Any
    index: int
    """
    artificaial segment class specially made for boolean version of calculateDetailsForNearestPointOnCurve
    """


def calculateDetailsForNearestPointOnCurve(cursorPosition, glyph):
    """
    Calculate details for the nearest point on a curve to the given cursor position within a glyph.
    Args:
        cursorPosition (tuple): A tuple (x, y) representing the cursor position.
        glyph (Glyph): A glyph object containing contours and segments.
    Returns:
        tuple: A tuple containing:
            - closestPoint (tuple): The coordinates (x, y) of the closest point on the curve.
            - contour_index (int): The index of the contour containing the closest point.
            - segment_index (int): The index of the segment containing the closest point.
            - t (float): The parameter t at which the closest point lies on the segment.
    """

    closestPointsRef = []

    for contour_index, contour in enumerate(glyph.contours):
        for segIndex, seg in enumerate(contour.segments):
            points = [contour.segments[segIndex - 1][-1]] + list(seg.points)

            if len(points) == 2:
                P1, P2 = points
                if P1.type == "line" and P2.type == "move":
                    continue
                P1, P2 = ((P1.x, P1.y), (P2.x, P2.y))
                closestPoint, contour_index, segment_index, _, t = getClosestInfo(
                    cursorPosition, seg, P1, P2
                )

            elif len(points) == 4:
                P1, P2, P3, P4 = points
                P1, P2, P3, P4 = (
                    (P1.x, P1.y),
                    (P2.x, P2.y),
                    (P3.x, P3.y),
                    (P4.x, P4.y),
                )
                closestPoint, contour_index, segment_index, _, t = getClosestInfo(
                    cursorPosition, seg, P1, P2, P3, P4
                )

            closestPointsRef.append((closestPoint, contour_index, segment_index, t))

    if not closestPointsRef:
        return None, None, None, None

    closestPointOnPathRef = min(
        closestPointsRef, key=lambda ref: lengthAB(cursorPosition, ref[0])
    )
    closestPoint, contour_index, segment_index, t = closestPointOnPathRef

    return closestPoint, contour_index, segment_index, t


def calculateDetailsForNearestPointOnCurveBoolean(cursorPosition, glyph):
    """
    This is a special version of calculateDetailsForNearestPointOnCurve to work with BooleanOperations.
    Calculate details for the nearest point on a curve to the given cursor position within a glyph.
    Args:
        cursorPosition (tuple): A tuple (x, y) representing the cursor position.
        glyph (Glyph): A glyph object containing contours and segments.
    Returns:
        tuple: A tuple containing:
            - closestPoint (tuple): The coordinates (x, y) of the closest point on the curve.
            - contour_index (int): The index of the contour containing the closest point.
            - segment_index (int): The index of the segment containing the closest point.
            - t (float): The parameter t at which the closest point lies on the segment.
    """

    def __appendPointRefs(points, closestPointsRef, contour, segIdx, contour_index):
        contour.index = contour_index
        seg = SegmentInfo(points[-1][0], contour, segIdx)
        if len(points) == 2:
            closestPoint, contour_index, segment_index, _, t = getClosestInfo(
                cursorPosition, seg, points[0][1], points[1][1]
            )
        elif len(points) == 4:
            closestPoint, contour_index, segment_index, _, t = getClosestInfo(
                cursorPosition,
                seg,
                points[0][1],
                points[1][1],
                points[2][1],
                points[3][1],
            )
        closestPointsRef.append((closestPoint, contour_index, segment_index, t))

    closestPointsRef = []

    for contour_index, contour in enumerate(glyph.contours):
        pointPenPoints = contour._points
        segIdx = 0
        lastCurvePoint = None
        for pointIdx, point in enumerate(pointPenPoints):
            segLength = None
            match point[0]:
                case "moveTo":
                    continue
                case "curve":
                    if pointIdx == 0:
                        lastCurvePoint = point
                        continue
                    elif not (len(pointPenPoints) - 1) - pointIdx:
                        points = [point, lastCurvePoint]
                        __appendPointRefs(
                            points, closestPointsRef, contour, segIdx, contour_index
                        )
                        continue
                    segLength = 4
                case "line":
                    if pointIdx == 0:
                        lastCurvePoint = point
                        continue
                    elif not (len(pointPenPoints) - 1) - pointIdx:
                        points = [pointPenPoints[pointIdx - 1], point]
                        __appendPointRefs(
                            points, closestPointsRef, contour, segIdx, contour_index
                        )
                        points = [point, lastCurvePoint]
                        __appendPointRefs(
                            points, closestPointsRef, contour, segIdx, contour_index
                        )
                        continue
                    segLength = 2
                case None:
                    if pointIdx != len(pointPenPoints) - 1:
                        continue
                    segLength = 3

            if not lastCurvePoint or (
                pointIdx != len(pointPenPoints) - 1 and point[0] is not None
            ):
                points = pointPenPoints[pointIdx + 1 - segLength : pointIdx + 1]
            else:
                points = pointPenPoints[pointIdx + 1 - segLength : pointIdx + 1] + [
                    lastCurvePoint
                ]

            if points[0][0] == "line" and points[1][0] == "move":
                return

            __appendPointRefs(points, closestPointsRef, contour, segIdx, contour_index)

    distances = [lengthAB(cursorPosition, ref[0]) for ref in closestPointsRef]

    if not distances:
        return None, None, None, None

    indexOfClosestPoint = distances.index(min(distances))
    closestPointOnPathRef = closestPointsRef[indexOfClosestPoint]
    closestPoint, contour_index, segment_index, t = closestPointOnPathRef

    return closestPoint, contour_index, segment_index, t


def getClosestInfo(
    cursorPoint: Sequence[Number], segment: BaseSegment, *points
) -> tuple[Sequence[Number], int, int, Sequence[Sequence[Number]], Number]:
    """
    Returns info about the closest point on the curve.
    """
    curve, (contour_index, segment_index, segPoints, curr_t) = (
        closestPointAndT_binaryIndexSearch_withSegments(cursorPoint, segment, *points)
    )
    closestPoint = calcSeg(curr_t, *curve)
    return closestPoint, contour_index, segment_index, segPoints, curr_t


def closestPointAndT_binaryIndexSearch_withSegments(
    pointOffCurve: Sequence[Number],
    segment: BaseSegment,
    *segPoints: Sequence[Sequence[Number]],
) -> tuple[
    Sequence[Sequence[Number]],
    tuple[int, int, Sequence[Sequence[Number]], Number],
]:

    curveDiv = ACCURACY
    points = segPoints
    curr_left_t = 0
    curr_mid_t = 0.5
    curr_right_t = 1

    for _ in range(12):
        LUT = getLut(segment.type, accuracy=ACCURACY, points=points)
        minimalDist = float("inf")

        for i in range(curveDiv + 1):
            t = i / curveDiv
            distance = lengthAB(pointOffCurve, LUT[(i, t)])

            if distance < minimalDist:
                minimalDist = distance
                best_t = t

        points1, points2 = splitSegAtT(segment.type, points, 0.5)

        if best_t >= 0.5:
            points = points2
            curr_left_t = curr_mid_t
            curr_mid_t = (curr_right_t + curr_mid_t) / 2
        else:
            points = points1
            curr_right_t = curr_mid_t
            curr_mid_t = (curr_left_t + curr_mid_t) / 2

    return points, (segment.contour.index, segment.index, segPoints, curr_mid_t)


def closestPointAndT_binaryIndexSearch(
    pointOffCurve: Sequence[Number],
    segType: str,
    *points: Sequence[Sequence[Number]],
) -> Sequence[Sequence[Number]]:
    """Returns the curve, which is segment cut from the given curve."""

    curveDiv = ACCURACY
    for _ in range(10):
        LUT = getLut(segType, accuracy=ACCURACY, points=points)
        minimalDist = float("inf")
        best_t = 0

        for i in range(curveDiv + 1):
            t = i / curveDiv
            distance = lengthAB(pointOffCurve, LUT[(i, t)])

            if distance < minimalDist:
                minimalDist = distance
                best_t = t

        points1, points2 = splitSegAtT(segType, points, 0.5)

        if best_t >= 0.5:
            points = points2
        else:
            points = points1

    return points


def calculateGuidesBasedOnT(
    t: float, segType: str, *points: Sequence[Sequence[Number]]
) -> tuple[
    Sequence[Sequence[Number]],
    Sequence[Sequence[Number]],
]:
    """
    Calculate guidelines for stem thickness.
    Returns two lines, each line has two points.
    Each point is represented as a tuple with x, y values.
    """

    closestPoint = calcSeg(t, *points)
    guide1, guide2 = getPerpendicularLineToTangent(segType, t, *points)

    def translate_guide(guide, offset):
        return [(x + offset[0], y + offset[1]) for x, y in guide]

    guide1 = translate_guide(guide1, closestPoint)
    guide2 = translate_guide(guide2, closestPoint)

    return guide1, guide2


def stemThicknessGuidelines(
    cursorPoint: Sequence[Number],
    segType: str,
    *points: Sequence[Sequence[Number]],
) -> tuple[
    Sequence[Sequence[Number]],
    Sequence[Sequence[Number]],
]:
    """
    Calculate guidelines for stem thickness.
    Returns two lines, each line has two points.
    Each point is represented as a tuple with x, y values.
    """
    curveChopped = closestPointAndT_binaryIndexSearch(cursorPoint, segType, *points)
    return calculateGuidesBasedOnT(0.5, segType, *curveChopped)


def getLut(
    segType: str, points: Sequence[Sequence[Number]], accuracy: int = 12
) -> dict[tuple[int, Number], Sequence[Number]]:
    """Returns Look Up Table, which contains pointsOnPath for calcBezier/calcLine,
    if getT=True then returns table with points and their factors"""
    lut_table = {}

    for i in range(accuracy + 1):
        t = i / accuracy

        if len(points) == 4:
            if segType == "qcurve":
                calc = calcQbezier(t, *points)
            else:
                calc = calcBezier(t, *points)
        elif len(points) == 2:
            calc = calcLine(t, *points)
        else:
            raise ValueError("Invalid number of points for the given segment type")

        lut_table[(i, t)] = calc

    return lut_table


def sortPointsDistances(
    myPoint: Sequence[Number], points: Sequence[Sequence[Number]]
) -> Sequence[Sequence[Number]]:
    def _sorter(point):
        return lengthAB(myPoint, point)

    points = sorted(points, key=_sorter)
    return points


def bs(searchFor, array):
    lowerBound = 0
    upperBound = len(array) - 1
    found = False

    while found == False and lowerBound <= upperBound:
        midpoint = (lowerBound + upperBound) // 2

        if array[midpoint] == searchFor:
            found = True
            return midpoint

        elif array[midpoint] < searchFor:
            lowerBound = midpoint + 1
        elif array[midpoint] >= searchFor:
            upperBound = midpoint - 1

    raise AssertionError("The value wasn't found in the array")


def splitSegAtT(
    segType: str, points: Sequence[Sequence[Number]], t: Number
) -> Sequence[Sequence[Sequence[Number]]]:
    assert isinstance(t, float), "splitSegAtT ERROR: t is not a float"

    if len(points) == 2:
        a, b = points
        segments = splitLineAtT(a, b, t)
    elif len(points) == 4:
        a, b, c, d = points
        if segType == "qcurve":
            segments = splitQatT(a, b, c, d, t)
        else:
            segments = splitCubicAtT(a, b, c, d, t)
    else:
        raise ValueError("Invalid number of points for the given segment type")

    return segments


def splitQatT(
    p1: Sequence[Number],
    h1: Sequence[Number],
    h2: Sequence[Number],
    p2: Sequence[Number],
    t: Number,
) -> Sequence[Sequence[Sequence[Number]]]:
    """
    Divides quadratic bezier paths into two at the given t factor.
    """
    c = calcLine(0.5, h1, h2)
    split_1 = splitQuadraticAtT(p1, h1, c, t)
    split_2 = splitQuadraticAtT(p2, h2, c, t)
    div1 = [split_1[0][0], split_1[0][1], split_1[1][1], split_1[1][2]]
    div2 = [split_2[1][2], split_2[1][1], split_2[0][1], split_2[0][0]]
    return [div1, div2]


def splitLineAtT(
    a: Sequence[Number],
    b: Sequence[Number],
    t: Number,
) -> Sequence[Sequence[Sequence[Number]]]:
    """Splits line into two at given t-factor (where 1>t>0)"""
    assert 0 <= t <= 1, "t must be between 0 and 1"

    if a == b:
        return [(a, b), (a, b)]

    A = calcLine(t, a, b)
    return [(a, A), (A, b)]


def calcSeg(t: Number, *points: Sequence[Sequence[Number]]) -> Sequence[Number]:
    assert isinstance(t, Number), "calcSeg ERROR: t is not a number"
    if len(points) == 2:
        return calcLine(t, *points)
    elif len(points) == 4:
        return calcBezier(t, *points)
    else:
        raise ValueError("Invalid number of points for the given segment type")


def lengthAB(A: Sequence[Number], B: Sequence[Number]) -> Number:
    """Returns distance value between two points: A and B"""
    ax, ay = A
    bx, by = B
    return math.hypot(bx - ax, by - ay)


def rotatePoint(
    P: Sequence[Number], angle: Number, originPoint: Sequence[Number]
) -> Sequence[Number]:
    """Rotates x/y around x_orig/y_orig by angle and returns result as [x,y]."""
    alfa = math.radians(angle)
    px, py = P
    originPointX, originPointY = originPoint

    cos_alfa = math.cos(alfa)
    sin_alfa = math.sin(alfa)

    x = (px - originPointX) * cos_alfa - (py - originPointY) * sin_alfa + originPointX
    y = (px - originPointX) * sin_alfa + (py - originPointY) * cos_alfa + originPointY

    return x, y


def angle(A: Sequence[Number], B: Sequence[Number]) -> Number:
    """Returns the angle between line AB and the x-axis."""
    ax, ay = A
    bx, by = B
    xDiff = bx - ax
    yDiff = by - ay

    if xDiff == 0:
        return 90 if yDiff != 0 else 0

    return math.degrees(math.atan2(yDiff, xDiff))


def calcBezier(t: Number, *pointList: Sequence[Sequence[Number]]) -> Sequence[Number]:
    """Returns coordinates for factor called 't' (from 0 to 1) based on cubic bezier formula."""
    assert len(pointList) == 4 and isinstance(t, Number)
    p1x, p1y = pointList[0]
    p2x, p2y = pointList[1]
    p3x, p3y = pointList[2]
    p4x, p4y = pointList[3]

    one_minus_t = 1 - t
    one_minus_t_squared = one_minus_t**2
    one_minus_t_cubed = one_minus_t**3
    t_squared = t**2
    t_cubed = t**3

    x = (
        p1x * one_minus_t_cubed
        + p2x * 3 * t * one_minus_t_squared
        + p3x * 3 * t_squared * one_minus_t
        + p4x * t_cubed
    )
    y = (
        p1y * one_minus_t_cubed
        + p2y * 3 * t * one_minus_t_squared
        + p3y * 3 * t_squared * one_minus_t
        + p4y * t_cubed
    )

    return x, y


def calcQbezier(t: Number, *pointList: Sequence[Sequence[Number]]) -> Sequence[Number]:
    """Returns coordinates for factor called 't' (from 0 to 1) based on Quadratic Bezier formula."""

    assert len(pointList) == 4 and isinstance(t, Number)
    p1, h1, h2, p2 = pointList
    c = calcLine(0.5, h1, h2)

    if t <= 0.5:
        t_segment = t * 2
        return calcQuadraticBezier(t_segment, p1, h1, c)
    else:
        t_segment = (t - 0.5) * 2
        return calcQuadraticBezier(t_segment, p2, h2, c)


def calcQuadraticBezier(
    t: float, *pointList: Sequence[Sequence[Number]]
) -> Sequence[Number]:
    """Returns coordinates for factor called 't' (from 0 to 1) based on Quadratic Bezier formula."""
    assert len(pointList) == 3 and isinstance(t, Number)
    p1x, p1y = pointList[0]
    p2x, p2y = pointList[1]
    p3x, p3y = pointList[2]

    x = (1 - t) ** 2 * p1x + 2 * (1 - t) * t * p2x + t**2 * p3x
    y = (1 - t) ** 2 * p1y + 2 * (1 - t) * t * p2y + t**2 * p3y

    return x, y


def calcLine(t: float, *pointList: Sequence[Sequence[Number]]) -> Sequence[Number]:
    """Returns coordinates for factor called 't' (from 0 to 1) based on linear interpolation."""
    assert len(pointList) == 2 and isinstance(t, Number)

    p1, p2 = pointList
    return interpolation(p1[0], p2[0], t), interpolation(p1[1], p2[1], t)


def interpolation(v1, v2, t):
    """One-dimensional linear interpolation."""
    return v1 * (1 - t) + v2 * t


def derivativeBezier(
    t: float, *pointList: Sequence[Sequence[Number]]
) -> Sequence[Number]:
    """Calculates derivative values for given control points and current t-factor."""
    p1x, p1y = pointList[0]
    p2x, p2y = pointList[1]
    p3x, p3y = pointList[2]
    p4x, p4y = pointList[3]

    one_minus_t = 1 - t
    one_minus_t_squared = one_minus_t**2
    t_squared = t**2

    summaX = (
        -3 * p1x * one_minus_t_squared
        + p2x * (3 * one_minus_t_squared - 6 * one_minus_t * t)
        + p3x * (6 * one_minus_t * t - 3 * t_squared)
        + 3 * p4x * t_squared
    )
    summaY = (
        -3 * p1y * one_minus_t_squared
        + p2y * (3 * one_minus_t_squared - 6 * one_minus_t * t)
        + p3y * (6 * one_minus_t * t - 3 * t_squared)
        + 3 * p4y * t_squared
    )

    return summaX, summaY


def derivativeQBezier(
    t: float, *pointList: Sequence[Sequence[Number]]
) -> Sequence[Number]:
    def derivativeQuadraticBezier(
        t: float, p1: Sequence[Number], p2: Sequence[Number], p3: Sequence[Number]
    ) -> Sequence[Number]:
        """Calculates derivative values for given control points and current t-factor"""
        p1x, p1y = p1
        p2x, p2y = p2
        p3x, p3y = p3

        summaX = 2 * (1 - t) * (p2x - p1x) + 2 * t * (p3x - p2x)
        summaY = 2 * (1 - t) * (p2y - p1y) + 2 * t * (p3y - p2y)

        return summaX, summaY

    assert len(pointList) == 4 and isinstance(t, Number)
    p1, h1, h2, p2 = pointList
    c = calcLine(0.5, h1, h2)
    t_segment = t * 2 if t <= 0.5 else (t - 0.5) * 2
    return (
        derivativeQuadraticBezier(t_segment, p1, h1, c)
        if t <= 0.5
        else derivativeQuadraticBezier(t_segment, p2, h2, c)
    )


def calculateTangentAngle(
    segType: str, t: float, *points: Sequence[Sequence[Number]]
) -> Number:
    """Calculates tangent angle for curve's/lines's current t-factor"""
    if len(points) == 4:
        if segType == "qcurve":
            xB, yB = derivativeQBezier(t, *points)
        else:
            xB, yB = derivativeBezier(t, *points)
    elif len(points) == 2:
        xB, yB = points[-1]
    else:
        raise ValueError("Invalid number of points for the given segment type")

    return angle((0, 0), (xB, yB))


def getPerpendicularLineToTangent(
    segType: str, t: float, *points: Sequence[Sequence[Number]]
) -> tuple[Sequence[Sequence[Number]], Sequence[Sequence[Number]]]:
    """Calculates 2 perpendicular lines to curve's/line's tangent angle with current t-factor.
    Returns two lines, each line has two points.
    Each point is represented as a tuple with x, y values.
    Lines starting point is at 0,0 of canvas.
    """

    if t == 0:
        t = 0.001  # Avoid division by zero in calculateTangentAngle

    if len(points) == 4:
        tanAngle = calculateTangentAngle(segType, t, *points)
    elif len(points) == 2:
        A, B = points
        xa, ya = A
        xb, yb = B
        tanAngle = angle(A, B)

        if (ya - yb) == 0 and xa != xb:  # Horizontal line
            tanAngle = 0
        elif (xa - xb) == 0 and ya != yb:  # Vertical line
            tanAngle = 90
    else:
        raise ValueError("Invalid number of points for the given segment type")

    tanPx1, tanPy1 = rotatePoint((0, 1000), tanAngle, (0, 0))  # One line
    tanPx2, tanPy2 = rotatePoint((0, 1000), tanAngle - 180, (0, 0))  # Second line

    return ((tanPx1, tanPy1), (0, 0)), ((0, 0), (tanPx2, tanPy2))
