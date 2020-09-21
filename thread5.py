# from: https://groups.google.com/g/cadquery/c/5kVRpECcxAU/m/7no7_ja6AAAJ
from math import atan, cos, degrees, pi, radians, sin, tan
from typing import Tuple, cast

import cadquery as cq

from helicalthreads import HelicalThreads
from threads import ext_threads, int_threads
from wing_utils import (
    diffPts,
    perpendicular_distance_pt_to_line_2d,
    setCtx,
    show,
    translate_2d,
)

setCtx(globals())


# Clearance between internal threads and external threads.
# The external threads are horzitionally moved to create
# the clearance.
ext_clearance = 0.05

# Set to guarantee the thread and core overlap and a manifold is created
thread_overlap = 0.001

# Tolerance value for generating STL files
stlTolerance = 1e-3

# The separation between edges of a helix after on revolution.
pitch = 2

# The included angle of the "tip" of a thread
angle_degs = 90

# Adjust z by inset so threads are inset from the bottom and top
inset = pitch / 3

nominalMajorDia = 8
nutDiameter = nominalMajorDia
nutRadius = nutDiameter / 2
nutHeight = 10 + (2 * inset)
nutSpan = 12  # Nut circumference and distance between flats

boltDiameter = nominalMajorDia
boltRadius = boltDiameter / 2
boltHeight = 10 + (2 * inset)
boltHeadHeight = 4
boltWallThickness = 2  # amount substracted from bolt radius to hollow out the bolt
boltSpan = nutSpan

major_cutoff = pitch / 8
minor_cutoff = pitch / 4
taper_rpos = 0.1

ht = HelicalThreads(
    height=nutHeight,
    pitch=pitch,
    dia_major=nutDiameter,
    angle_degs=angle_degs,
    inset=inset,
    ext_clearance=ext_clearance,
    taper_rpos=taper_rpos,
    major_cutoff=major_cutoff,
    minor_cutoff=minor_cutoff,
    thread_overlap=thread_overlap,
)
print(f"ht={vars(ht)}")

boltThreads = ext_threads(ht)
# show(boltThreads, "botThreads-0")
# show(boltThreads.translate((radius * 4, 0, 0)), "botThreads+4")
# boltThreadsBb: cq.BoundBox = boltThreads.BoundingBox()
# print(f"bolthreadsBb={vars(boltThreadsBb)}")

boltCoreRadius = ht.ext_helix_radius
# print(f"boltCoreRadius={boltCoreRadius} boltRadius={boltRadius:.3f})


boltHead = (
    cq.Workplane("XY", origin=(0, 0, 0)).polygon(6, boltSpan).extrude(boltHeadHeight)
)
# show(boltHead, "boltHead-0")

boltCore = (
    cq.Workplane("XY", origin=(0, 0, boltHeadHeight))
    .circle(boltCoreRadius)
    .circle(boltCoreRadius - boltWallThickness)
    .extrude(boltHeight)
)
# show(boltCore, "boltCore-0")


print(f"bolt begin union boltHeadHeight={boltHeadHeight}")
bolt = boltHead.union(boltCore).union(
    boltThreads.move(cq.Location(cq.Vector(0, 0, boltHeadHeight)))
)
print("bolt end   union")
show(bolt, "bolt-0")

nutCore = (
    cq.Workplane("XY", origin=(0, 0, 0))
    .circle(nutRadius)
    .polygon(6, nutSpan)
    .extrude(nutHeight)
)
# show(nutCore, "nutCore-0")

nutThreads = int_threads(ht)
# show(nutThreads, "nutThreads-0")
# nutThreadsBb: cq.BoundBox = nutThreads.BoundingBox()
# print(f"nuthreadsBb={vars(nutThreadsBb)}")

print("nut begin union")
nut = nutCore.union(nutThreads)
print("nut end   union")
show(nut, "nut-0")

fname = f"bolt-dia_{boltDiameter:.3f}-p_{pitch:.3f}-a_{angle_degs:.3f}-h_{boltHeight:.3f}-mj_{major_cutoff}-mi_{minor_cutoff:.3f}-ec_{ext_clearance:.3f}-to_{thread_overlap:.4f}-tol_{stlTolerance:.3f}.stl"
cq.exporters.export(bolt, fname, tolerance=stlTolerance)
print(f"{fname}")

fname = f"nut-dia_{nutDiameter:.3f}-p_{pitch:.3f}-a_{angle_degs:.3f}-h_{nutHeight:.3f}-mj_{major_cutoff}-mi_{minor_cutoff:.3f}-ec_{ext_clearance:.3f}-to_{thread_overlap:.4f}-tol_{stlTolerance:.3f}.stl"
cq.exporters.export(nut, fname, tolerance=stlTolerance)
print(f"{fname}")
