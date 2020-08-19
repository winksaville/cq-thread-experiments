# from: https://groups.google.com/g/cadquery/c/5kVRpECcxAU/m/7no7_ja6AAAJ
from math import cos, pi, sin
from typing import cast

import cadquery as cq

from wing_utils import setCtx, show

setCtx(globals())


def helix(r0, r_eps, p, h, depth=0, frac=1e-1):
    def func(t):

        if t > frac and t < 1 - frac:
            z = h * t + depth
            r = r0 + r_eps
        elif t <= frac:
            z = h * t + depth * sin(pi / 2 * t / frac)
            r = r0 + r_eps * sin(pi / 2 * t / frac)
        else:
            z = h * t - depth * sin(2 * pi - pi / 2 * (1 - t) / frac)
            r = r0 - r_eps * sin(2 * pi - pi / 2 * (1 - t) / frac)

        x = r * sin(-2 * pi / (p / h) * t)
        y = r * cos(2 * pi / (p / h) * t)

        return x, y, z

    return func


def thread(radius, pitch, height, depth, radius_eps, aspect=10):

    e1_bottom = (
        cq.Workplane("XY")
        .parametricCurve(helix(radius, 0, pitch, height, -depth))
        .val()
    )
    e1_top = (
        cq.Workplane("XY").parametricCurve(helix(radius, 0, pitch, height, depth)).val()
    )

    e2_bottom = (
        cq.Workplane("XY")
        .parametricCurve(helix(radius, radius_eps, pitch, height, -depth / aspect))
        .val()
    )
    e2_top = (
        cq.Workplane("XY")
        .parametricCurve(helix(radius, radius_eps, pitch, height, depth / aspect))
        .val()
    )

    f1 = cq.Face.makeRuledSurface(e1_bottom, e1_top)
    f2 = cq.Face.makeRuledSurface(e2_bottom, e2_top)
    f3 = cq.Face.makeRuledSurface(e1_bottom, e2_bottom)
    f4 = cq.Face.makeRuledSurface(e1_top, e2_top)

    sh = cq.Shell.makeShell([f1, f2, f3, f4])
    rv = cq.Solid.makeSolid(sh)

    return rv

pitch = 2
depth = pitch / 4 # Adjust z by depth so threads are inset from the bottom?
threadOverlap = 0.001
radius_eps = 0.5 + threadOverlap # "width" of the thread?
#eps = 0.01 #1e-3
stlTolerance = 1e-3

nominalMajDia = 8
nutAdjustment = 0
nutDiameter = nominalMajDia - nutAdjustment
nutRadius = nutDiameter / 2
nutHeight = 4 # Nut height
nutSpan = 12 # Nut circumference and distance between flats

boltAdjustment = 0.1
boltDiameter = nominalMajDia - boltAdjustment
boltRadius = (boltDiameter / 2) - radius_eps
boltHeight = 10
boltWallThickness = 2 # amount substracted from bolt radius to hollow out the bolt



boltShaft = (
    cq.Workplane("XY", origin=(0, 0, -depth))
    .circle(boltRadius)
    .circle(boltRadius - boltWallThickness)
    .extrude(boltHeight + 1.75 * depth)
)
#show(boltShaft.translate((radius * 4, 0, 0)), "boltShaft+4")
show(boltShaft, "boltShaft-0")
boltShaftBb: cq.BoundBox = cast(cq.Shape, boltShaft.val()).BoundingBox()
print(f"boltShaftBb={vars(boltShaftBb)}")

boltThreads = thread(boltRadius - threadOverlap, pitch, boltHeight, depth, radius_eps)
boltThreadsBb: cq.BoundBox = boltThreads.BoundingBox()
print(f"boltThreadsBb={vars(boltThreadsBb)}")
#show(boltThreads.translate((radius * 4, 0, 0)), "botThreads+4")
show(boltThreads, "botThreads-0")

bolt = boltShaft.union(boltThreads)
#show(bolt.translate((radius * 4, 0, 0)), "bolt+4")
show(bolt, "bolt-0")

nutCore = (
    cq.Workplane("XY", origin=(0, 0, -depth))
    .circle(nutRadius)
    .polygon(6, nutSpan)
    .extrude(nutHeight + 1.75 * depth)
)
#show(nutCore.translate((-radius * 4, 0, 0)), "nutCore-4")
show(nutCore, "nutCore-0")

nutThreads = thread(nutRadius + threadOverlap, pitch, nutHeight, depth, -radius_eps)
nutThreadsBb: cq.BoundBox = nutThreads.BoundingBox()
print(f"nutThreadsBb={vars(nutThreadsBb)}")
#show(nutThreads.translate((-radius * 4, 0, 0)), "nutThreads-4")
show(nutThreads, "nutThreads-0")

nut = nutCore.union(nutThreads)
#show(nut.translate((-radius * 4, 0, 0)), "nut-4")
show(nut, "nut-0")


fname = f"bolt-dia_{boltDiameter:.3f}-pitch_{pitch:.3f}-depth_{depth:.3f}-height_{boltHeight:.3f}-tol_{stlTolerance:.3f}.stl"
cq.exporters.export(bolt, fname, tolerance=stlTolerance)

fname = f"nut-dia_{nutDiameter:.3f}-pitch_{pitch:.3f}-depth_{depth:.3f}-height_{nutHeight:.3f}-tol_{stlTolerance:.3f}.stl"
cq.exporters.export(nut, fname, tolerance=stlTolerance)
