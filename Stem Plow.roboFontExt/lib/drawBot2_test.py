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
num = 100
fill(0,0,1)
stroke(0.7)
line(p1,p2)
line(p3,p4)
stroke(None)
for i in range(num+1):
    t = i/num
    p = calcQbezier(t, p1,p2,p3,p4)
    drawPoint(p,s=2)

fill(1,0,0)
for p in [p1,p2,p3,p4]:
    drawPoint(p)

newPage()
scale(3)
def splitQtwo(p1,h1,h2,p2, t=0.5):
    """divides ROBOFONT quadratic bezier paths (wich are strange, stored as pairs of two curves) into two, t factor here is only for having consistency between this version and cubic. This factor should be 0.5"""
    c = calcLine(.5,h1,h2)
    split_1 = splitQuadraticAtT(p1,h1,c,t)
    split_2 = splitQuadraticAtT(p2,h2,c,t)
    div1 = [split_1[0][0],split_1[0][1],split_1[1][1],split_1[1][2]]

    div2 = list(reversed([split_2[0][0],split_2[0][1],split_2[1][1],split_2[1][2]]))

    #print(f"c {p1}")
    #print(f"div {[div1,div2]}")
    return [div1,div2]

for curve in splitQtwo(p1,p2,p3,p4):
    p1,p2,p3,p4 = curve
    num = 100
    fill(0,0,1)
    stroke(0.7)
    line(p1,p2)
    line(p3,p4)
    stroke(None)
    for i in range(num+1):
        t = i/num
        p = calcQbezier(t, p1,p2,p3,p4)
        drawPoint(p,s=2)
    fill(1,0,0)
    # for p in [p1,p2,p3,p4]:
    #     drawPoint(p)
