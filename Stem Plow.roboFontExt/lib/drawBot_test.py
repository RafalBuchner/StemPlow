from TMath_binary import *
scale(3)

def drawPoint(p,s=6):
    x,y = p
    oval(x-s/2,y-s/2,s,s)

self_position = (80, 150)
fill(None)
stroke(1,0,1)
drawPoint(self_position)
stroke(None)
p1 = (42, 100)
p2 = (62, 224)
p3 = (314, 184)
p4 = (324, 98)
save()
pp = (203.0, 204.0)
fill(0)
drawPoint(pp)
restore()
# testdraw CB
num = 100
fill(0,0,1)
for i in range(num+1):
    t = i/num
    p = calcQbezier(t, p1,p2,p3,p4)
    drawPoint(p,s=2)

fill(1,0,0)
for p in [p1,p2,p3,p4]:
    drawPoint(p)

seg_type = "qcurve"
lines = stemThicnkessGuidelines(self_position,seg_type,p1,p2,p3,p4)
stroke(1,0,0,0.3)
line(*lines[0])
line(*lines[1])




calcQbezier(t,*pointList)
