"""
Problem: Robofont Quadratic Curves: They have 4 points, like cubic, so to do any math with them I need to devide one robofont Qcurve into actual two quadratic curves. It makes life much more complicated, because if I want to create analogic functions to those for Cubic Bezier Curves to work with those curves. For example I would like to be able to divide this curve with fontTools.misc.bezierTools.splitQuadraticAtT at any possible t-factor. I have two possibilites:
    one is to treat the curve like cubic and create special function that gets 4 control points
    the second is to loop over the whole glyph object and create analogic version, which will have proper dividion, that will treat quadratic curves normally
"""

from TMath_binary import *
scale(3)

def drawPoint(p,s=6):
    x,y = p
    oval(x-s/2,y-s/2,s,s)

# self_position = (80, 150)
# fill(None)
# stroke(1,0,1)
# drawPoint(self_position)
# stroke(None)
p1 = (42, 100)
p2 = (62, 224)
p3 = (314, 184)
p4 = (324, 98)
save()
pp = c = calcLine(.5,p2,p3)
fill(0)
drawPoint(pp)
restore()
# testdraw CB
num = 6
fill(0,0,1)
stroke(0.7)
line(p1,p2)
line(p3,p4)
stroke(None)
for i in range(num+1):
    t = i/num
    p = calcQbezier(t, p1,p2,p3,p4)
    drawPoint(p,s=2)




# newPage()
# scale(3)
# def calcQuadraticBezier(t,*pointList):
#         assert len(pointList) == 3 and isinstance(t, float)
#         p1x,p1y = pointList[0]
#         p2x,p2y = pointList[1]
#         p3x,p3y = pointList[2]
#         x = (1-t)**2*p1x + 2*(1-t)*t*p2x+t**2*p3x
#         y = (1-t)**2*p1y + 2*(1-t)*t*p2y+t**2*p3y
#         return x, y

# p1 = (42, 100)
# p2 = (62, 224)
# p3 = (314, 184)

# num = 17
# fill(0,0,1)
# stroke(0.7)
# line(p1,p2)
# line(p3,p2)
# stroke(None)
# for i in range(num+1):
#     t = i/num
#     p = calcQuadraticBezier(t, p1,p2,p3)
#     drawPoint(p,s=2)
