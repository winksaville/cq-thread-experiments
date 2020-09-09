# from: https://groups.google.com/g/cadquery/c/5kVRpECcxAU/m/7no7_ja6AAAJ
from math import atan, cos, degrees, pi, radians, sin, tan
from typing import Tuple, Union, cast

import cadquery as cq
from taperable_helix import helix

from threads import threads
from wing_utils import setCtx, show

setCtx(globals())


pitch = 2
angleDegs = 45
inset = pitch / 3  # Adjust z by inset so threads are inset from the bottom
threadOverlap = (
    1e-3  # Set to guarantee the thread and core overlap and a manifold is created
)
stlTolerance = 1e-3

nominalMajorDia = 8
nutAdjustment = 0
nutDiameter = nominalMajorDia - nutAdjustment
nutRadius = nutDiameter / 2
nutHeight = 4 + (2 * inset)
nutSpan = 12  # Nut circumference and distance between flats

boltAdjustment = 0.15
boltDiameter = nominalMajorDia - boltAdjustment
boltRadius = boltDiameter / 2
boltHeight = 10 + (2 * inset)
boltHeadHeight = 4
boltWallThickness = 2  # amount substracted from bolt radius to hollow out the bolt
boltSpan = nutSpan

majorPd = 8  # None
minorPd = 4  # None

boltThreads, threadDepth = threads(
    height=boltHeight,
    diaMajor=boltDiameter,
    pitch=pitch,
    angleDegs=angleDegs,
    diaMajorCutOffPitchDivisor=majorPd * 1.1,
    diaMinorCutOffPitchDivisor=minorPd * 1.1,
    threadOverlap=threadOverlap,
    inset=inset,
    taper_rpos=0.1,
)
# print(f"threadDepth={threadDepth}")
boltThreadsBb: cq.BoundBox = boltThreads.BoundingBox()
# print(f"boltThreadsBb={vars(boltThreadsBb)}")
# show(boltThreads, "botThreads-0")
# show(boltThreads.translate((radius * 4, 0, 0)), "botThreads+4")


boltCoreRadius = boltRadius - threadDepth
# print(f"boltCoreRadius={boltCoreRadius} boltRadius={boltRadius:.3f} threadDepth={threadDepth}")


boltHead = (
    cq.Workplane("XY", origin=(0, 0, 0)).polygon(6, boltSpan).extrude(boltHeadHeight)
)
boltHeadBb: cq.BoundBox = cast(cq.Shape, boltHead.val()).BoundingBox()
# print(f"boltHeadBb={vars(boltHeadBb)}")
# show(boltHead, "boltHead-0")

boltCore = (
    cq.Workplane("XY", origin=(0, 0, boltHeadHeight))
    .circle(boltCoreRadius)
    .circle(boltCoreRadius - boltWallThickness)
    .extrude(boltHeight)
)
boltCoreBb: cq.BoundBox = cast(cq.Shape, boltCore.val()).BoundingBox()
# print(f"boltCoreBb={vars(boltCoreBb)}")
# show(boltCore, "boltCore-0")


# print("bolt begin union")
bolt = boltHead.union(boltCore).union(
    boltThreads.move(cq.Location(cq.Vector(0, 0, boltHeadHeight)))
)
# print("bolt end   union")
# show(bolt, "bolt-0")

nutCore = (
    cq.Workplane("XY", origin=(0, 0, 0))
    .circle(nutRadius)
    .polygon(6, nutSpan)
    .extrude(nutHeight)
)
nutCoreBb: cq.BoundBox = nutCore.val().BoundingBox()
# print(f"nutCoreBb={vars(nutCoreBb)}")
# show(nutCore, "nutCore-0")

nutThreads, threadDepth = threads(
    height=nutHeight,
    diaMajor=nutDiameter,
    pitch=pitch,
    angleDegs=angleDegs,
    externalThreads=False,
    diaMajorCutOffPitchDivisor=majorPd,
    diaMinorCutOffPitchDivisor=minorPd,
    threadOverlap=threadOverlap,
    inset=inset,
    taper_rpos=0.1,
)
nutThreadsBb: cq.BoundBox = nutThreads.BoundingBox()
# print(f"nutThreadsBb={vars(nutThreadsBb)}")
# show(nutThreads, "nutThreads-0")

# print("nut begin union")
nut = nutCore.union(nutThreads)
# print("nut end   union")
# show(nut, "nut-0")


fname = f"bolt-dia_{boltDiameter:.3f}-adj_{boltAdjustment:.3f}-p_{pitch:.3f}-a_{angleDegs:.3f}-td_{threadDepth:.3f}-h_{boltHeight:.3f}-mjPd_{majorPd}-miPd_{minorPd:}-to_{threadOverlap:.4f}-tol_{stlTolerance:.3f}.stl"
cq.exporters.export(bolt, fname, tolerance=stlTolerance)
print(f"{fname}")

fname = f"nut-dia_{nutDiameter:.3f}-adj_{nutAdjustment:.3f}-p_{pitch:.3f}-a_{angleDegs:.3f}-td_{threadDepth:.3f}-h_{nutHeight:.3f}-mjPd_{majorPd}-miPd_{minorPd}-to_{threadOverlap:.4f}-tol_{stlTolerance:.3f}.stl"
cq.exporters.export(nut, fname, tolerance=stlTolerance)
print(f"{fname}")
