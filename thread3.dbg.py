# from: https://groups.google.com/g/cadquery/c/5kVRpECcxAU/m/7no7_ja6AAAJ
from math import cos, degrees, pi, sin
from typing import cast

import cadquery as cq

from wing_utils import setCtx, show

setCtx(globals())


helixCount: int = 0


def helix(radius, threadDepth, pitch, height, inset=0, frac=1e-1):
    def func(t):  # t is a value that starts a zero ends at 1

        global helixCount
        if t == 0:
            helixCount = 0

        print(
            f"helix.func:+ {helixCount}: t={t:.4f} r={radius} t={threadDepth} p={pitch} h={height} i={inset} f={frac}"
        )
        fadeAngle: float

        if (frac > 0) and (t <= frac):
            # fadeAngle is 0 to 90deg allowing fadeScale to be 0 to 1 by using sin(fadeAngle)
            fadeAngle = pi / 2 * t / frac
            print(
                f"helix.func:  {helixCount}: t={t:.4f} fa={degrees(fadeAngle):.3f} FIRST {t:.4f} <= {frac:.3f} "
            )
        elif (frac == 0) or ((t > frac) and (t < 1 - frac)):
            # fadeAngle is 90deg allowing fadeScale making 1 using sin(90) == 1
            fadeAngle = pi / 2
            print(
                f"helix.func:  {helixCount}: t={t:.4f} fa={degrees(fadeAngle):.3f} MIDDL {t:.4f} > {frac:.3f} and {t:.4f} < {(1 - frac):.3f}"
            )
        else:
            # fadeAngle is 90 to 0deg allowing fadeScale to be 1 to 0 by using sin(fadeAngle)
            fadeAngle = -(2 * pi - pi / 2 * (1 - t) / frac)
            print(
                f"helix.func:  {helixCount}: t={t:.4f} fa={degrees(fadeAngle):.3f} LAST  {t:.4f} >= {frac:.3f} "
            )

        fadeScale: float = sin(fadeAngle)
        z: float = (height * t) + (inset * fadeScale)
        r: float = radius + (threadDepth * fadeScale)

        a: float = 2 * pi / (pitch / height) * t
        x: float = r * sin(-a)
        y: float = r * cos(a)

        print(
            f"helix.func:- {helixCount}: t={t:.4f} r={r:.3f} a={degrees(a):.3f} fa={degrees(fadeAngle):.3f} fs={fadeScale:.3f} ({x:.3f}, {y:.3f}, {z:.3f})"
        )
        helixCount += 1
        return x, y, z

    return func


def thread(radius, threadDepth, pitch, height, inset, aspect=10):

    e1_bottom = (
        cq.Workplane("XY")
        .parametricCurve(helix(radius, 0, pitch, height, -inset))
        .val()
    )
    # print(f"e1_bottom={e1_bottom}")
    show(e1_bottom, "e1_bottom")

    e1_top = (
        cq.Workplane("XY").parametricCurve(helix(radius, 0, pitch, height, inset)).val()
    )
    # show(e1_top, "e1_top")

    e2_bottom = (
        cq.Workplane("XY")
        .parametricCurve(helix(radius, threadDepth, pitch, height, -inset / aspect))
        .val()
    )
    # show(e2_bottom, "e2_bottom")

    e2_top = (
        cq.Workplane("XY")
        .parametricCurve(helix(radius, threadDepth, pitch, height, inset / aspect))
        .val()
    )
    # show(e2_top, "e2_top")

    f1 = cq.Face.makeRuledSurface(e1_bottom, e1_top)
    f2 = cq.Face.makeRuledSurface(e2_bottom, e2_top)
    f3 = cq.Face.makeRuledSurface(e1_bottom, e2_bottom)
    f4 = cq.Face.makeRuledSurface(e1_top, e2_top)

    sh = cq.Shell.makeShell([f1, f2, f3, f4])
    rv = cq.Solid.makeSolid(sh)

    return rv


pitch = 2
inset = pitch / 4  # Adjust z by inset so threads are inset from the bottom?
threadOverlap = 0.001
threadDepth = 0.5 + threadOverlap  # "width" of the thread?
stlTolerance = 1e-3

nominalMajDia = 8
nutAdjustment = 0
nutDiameter = nominalMajDia - nutAdjustment
nutRadius = nutDiameter / 2
nutHeight = 4  # Nut height
nutSpan = 12  # Nut circumference and distance between flats

boltAdjustment = 0.1
boltDiameter = nominalMajDia - boltAdjustment
boltRadius = (boltDiameter / 2) - threadDepth
boltHeight = 10
boltWallThickness = 2  # amount substracted from bolt radius to hollow out the bolt


# boltShaft = (
#     cq.Workplane("XY", origin=(0, 0, -inset))
#     .circle(boltRadius)
#     .circle(boltRadius - boltWallThickness)
#     .extrude(boltHeight + 1.75 * inset)
# )
# boltShaftBb: cq.BoundBox = cast(cq.Shape, boltShaft.val()).BoundingBox()
# print(f"boltShaftBb={vars(boltShaftBb)}")
# # show(boltShaft.translate((radius * 4, 0, 0)), "boltShaft+4")
# # show(boltShaft, "boltShaft-0")

boltThreads = thread(boltRadius - threadOverlap, threadDepth, pitch, boltHeight, -inset)
# boltThreadsBb: cq.BoundBox = boltThreads.BoundingBox()
# print(f"boltThreadsBb={vars(boltThreadsBb)}")
# show(boltThreads.translate((radius * 4, 0, 0)), "botThreads+4")
# show(boltThreads, "botThreads-0")

# bolt = boltShaft.union(boltThreads)
# # show(bolt.translate((radius * 4, 0, 0)), "bolt+4")
# show(bolt, "bolt-0")
#
# nutCore = (
#     cq.Workplane("XY", origin=(0, 0, -inset))
#     .circle(nutRadius)
#     .polygon(6, nutSpan)
#     .extrude(nutHeight + 1.75 * inset)
# )
# # show(nutCore.translate((-radius * 4, 0, 0)), "nutCore-4")
# # show(nutCore, "nutCore-0")
#
# nutThreads = thread(nutRadius + threadOverlap, -threadDepth, pitch, nutHeight, inset)
# nutThreadsBb: cq.BoundBox = nutThreads.BoundingBox()
# print(f"nutThreadsBb={vars(nutThreadsBb)}")
# # show(nutThreads.translate((-radius * 4, 0, 0)), "nutThreads-4")
# # show(nutThreads, "nutThreads-0")
# #
# nut = nutCore.union(nutThreads)
# # show(nut.translate((-radius * 4, 0, 0)), "nut-4")
# show(nut, "nut-0")
#
#
# fname = f"bolt-dia_{boltDiameter:.3f}-pitch_{pitch:.3f}-depth_{threadDepth:.3f}-height_{boltHeight:.3f}-tol_{stlTolerance:.3f}.stl"
# cq.exporters.export(bolt, fname, tolerance=stlTolerance)
#
# fname = f"nut-dia_{nutDiameter:.3f}-pitch_{pitch:.3f}-depth_{threadDepth:.3f}-height_{nutHeight:.3f}-tol_{stlTolerance:.3f}.stl"
# cq.exporters.export(nut, fname, tolerance=stlTolerance)
