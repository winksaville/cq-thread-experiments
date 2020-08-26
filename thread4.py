# from: https://groups.google.com/g/cadquery/c/5kVRpECcxAU/m/7no7_ja6AAAJ
from math import atan, cos, degrees, pi, radians, sin, tan
from typing import Tuple, Union, cast

import cadquery as cq

from wing_utils import setCtx, show

setCtx(globals())


helixCount: int = 0


def helix(radius, threadDepth, threadHalfHeight, pitch, height, inset=0, frac=1e-1):
    def func(t):  # t is a value that starts a zero ends at 1

        global helixCount
        if t == 0:
            helixCount = 0

        # print(f"helix.func:+ {helixCount}: t={t:.4f} r={radius:.3f} t={threadDepth:.3f}  thh={threadHalfHeight:.3f} p={pitch:.3f} h={height:.3f} i={inset:.3f} f={frac:.3f}")
        fadeAngle: float

        if (frac > 0) and (t <= frac):
            # fadeAngle is 0 to 90deg allowing fadeScale to be 0 to 1 by using sin(fadeAngle)
            fadeAngle = +(pi / 2 * t / frac)
            # print(f"helix.func:  {helixCount}: t={t:.4f} fa={degrees(fadeAngle):.3f} FIRST {t:.4f} <= {frac:.3f} ")
        elif (frac == 0) or ((t > frac) and (t < 1 - frac)):
            # No fading set fadeAngle to 90deg so sin(fadeAngle) == 1
            fadeAngle = pi / 2
            # print(f"helix.func:  {helixCount}: t={t:.4f} fa={degrees(fadeAngle):.3f} MIDDL {t:.4f} > {frac:.3f} and {t:.4f} < {(1 - frac):.3f}")
        else:
            # fadeAngle is 90 to 0deg allowing fadeScale to be 1 to 0 by using sin(fadeAngle)
            fadeAngle = -((2 * pi) - (pi / 2 * (1 - t) / frac))
            # print(f"helix.func:  {helixCount}: t={t:.4f} fa={degrees(fadeAngle):.3f} LAST  {t:.4f} >= {frac:.3f} ")

        fadeScale: float = sin(fadeAngle)
        z: float = (height * t) + (threadHalfHeight * fadeScale) + inset
        r: float = radius + (threadDepth * fadeScale)
        # print(f"helix.func:  r={r:.3f} radius={radius:.3f} + (threadDepth={threadDepth:.3f} * fadeScale={fadeScale:.3f})")


        a: float = 2 * pi / (pitch / height) * t
        x: float = r * sin(-a)
        y: float = r * cos(a)

        # print(f"helix.func:- {helixCount}: t={t:.4f} r={r:.3f} a={degrees(a):.3f} fa={degrees(fadeAngle):.3f} fs={fadeScale:.3f} ({x:.3f}, {y:.3f}, {z:.3f})")
        helixCount += 1
        return x, y, z

    return func


def threadHelix(
    height: float,
    diaMajor: float,
    pitch: float = 1,
    angleDegs: float = 60,
    diaMajorCutOffPitchDivisor: Union[float, None] = 8,
    diaMinorCutOffPitchDivisor: Union[float, None] = 4,
    threadOverlap: float = 0,
    inset: float = 0,
    frac: float = 0.10,
) -> Tuple[cq.Solid, float]:
    """
    :param totalHeight: Height including top and bottom inset
    :param diaMajor: Diameter of threads its largest dimension
    :param pitch: Peek to Peek measurement of the threads in units default is mm
    :param angleDegs: Angle of the thread profile in degrees
    :param diaMajorCutOffPitchDivisor: is v in pitch/v to determine size of MajorCutOff
    typically None for nuts as there is overlap with the nut barrel
    :param diaMinorCutOffPitchDivisor: is v in pitch/v to determin size of MinorCutOff
    typically None for bolts so there is overlap with the stud
    :param threadOverlap: amount to increase threadDepth so core overlaps with threads
    :param inset: number units in the z direction
    :param frac: percent of threads for fade in and fade out
    :returns: Solid representing the threads and float dept
    """

    print(f"threadHelix:+ height={height:.3f} diaMajor={diaMajor:.3f} pitch={pitch:.3f} angleDegs={angleDegs:.3f}")
    print(f"threadHelix:  diaMajorCutOffPitchDivisor={diaMajorCutOffPitchDivisor} diaMinorCutOffPitchDivisor={diaMinorCutOffPitchDivisor}")
    print(f"threadHelix:  threadOverlap={threadOverlap:.3f} inset={inset:.3f} frac={frac:.3f}")

    angleRadians: float = radians(angleDegs)
    tanAngle: float = tan(angleRadians)
    diaMajorCutOff: float = (pitch / diaMajorCutOffPitchDivisor) if (diaMajorCutOffPitchDivisor is not None) else 0
    diaMinorCutOff: float = (pitch / diaMinorCutOffPitchDivisor) if (diaMinorCutOffPitchDivisor is not None) else 0
    diaMajorThreadHalfHeight: float = diaMajorCutOff / 2
    diaMinorThreadHalfHeight: float = (pitch - diaMinorCutOff) / 2
    print(f"threadHelix: angle={angleDegs:.3f} angleRadians={angleRadians:.3f} tanAngle={tanAngle:.3f} diaMajorCutOff={diaMajorCutOff:.3f} diaMinorCutOff={diaMinorCutOff:.3f} diaMajorThreadHalfHeight={diaMajorThreadHalfHeight:.3f} diaMinorThreadHalfHeight={diaMinorThreadHalfHeight:.3f}")

    diaMajorToTip: float = diaMajorThreadHalfHeight * tanAngle
    diaMinorToTip: float = diaMinorThreadHalfHeight * tanAngle
    threadDepth: float = diaMinorToTip - diaMajorToTip
    diaMinor: float = diaMajor - (threadDepth * 2)

    rv: cq.Solid = None

    # Adjust diaMinor by threadOverlap
    if diaMinor > threadOverlap:
        diaMinor -= (threadOverlap * 2)
    print(f"threadHelix: diaMajorToTip={diaMajorToTip:.3f} diaMinorToTip={diaMinorToTip:.3f} threadDepth={threadDepth:.3f} diaMinor={diaMinor:.3f}")

    if (diaMajorCutOff == 0) and (diaMinorCutOff == 0):
        # One major helix two minor helixes
        minor1 = (
            cq.Workplane("XY")
            .parametricCurve(helix(diaMinor / 2, 0, -diaMinorThreadHalfHeight, pitch, height, inset, frac))
            .val()
        )
        # print(f"minor1={minor1}")
        # show(minor1, "minor1")

        minor2 = (
            cq.Workplane("XY")
            .parametricCurve(helix(diaMinor / 2, 0, +diaMinorThreadHalfHeight, pitch, height, inset, frac))
            .val()
        )
        # print(f"minor2={minor2}")
        # show(minor2, "minor2")

        major1 = (
            cq.Workplane("XY")
            .parametricCurve(helix(diaMinor / 2, threadDepth + threadOverlap, 0, pitch, height, inset, frac))
            .val()
        )
        # print(f"major1={major1}")
        # show(major1, "major1")

        f1 = cq.Face.makeRuledSurface(minor1, minor2) # e1_bottom, e1_top)
        # show(f1, "f1")
        #f2 = cq.Face.makeRuledSurface(e2_bottom, e2_top)
        #show(f2, "f2")
        f3 = cq.Face.makeRuledSurface(minor1, major1) #e1_bottom, e2_bottom)
        # show(f3, "f3")
        f4 = cq.Face.makeRuledSurface(minor2, major1) #e1_top, e2_top)
        # show(f4, "f4")

        sh = cq.Shell.makeShell([f1, f3, f4])
        rv = cq.Solid.makeSolid(sh)
        # show(rv, "rv")

    elif diaMajorCutOff == 0:
        # One minor helix two major helixes
        pass

    elif diaMinorCutOff == 0:
        # One minor helix two major helixes
        pass

    else:
        # Two major and two  minor helixes
        # One major helix two minor helixes
        minor1 = (
            cq.Workplane("XY")
            .parametricCurve(helix(diaMinor / 2, 0, -diaMinorThreadHalfHeight, pitch, height, inset, frac))
            .val()
        )
        # print(f"minor1={minor1}")
        # show(minor1, "minor1")

        minor2 = (
            cq.Workplane("XY")
            .parametricCurve(helix(diaMinor / 2, 0, +diaMinorThreadHalfHeight, pitch, height, inset, frac))
            .val()
        )
        # print(f"minor2={minor2}")
        # show(minor2, "minor2")

        major1 = (
            cq.Workplane("XY")
            .parametricCurve(helix(diaMinor / 2, threadDepth + threadOverlap, -diaMajorThreadHalfHeight, pitch, height, inset, frac))
            .val()
        )
        # print(f"major1={major1}")
        # show(major1, "major1")

        major2 = (
            cq.Workplane("XY")
            .parametricCurve(helix(diaMinor / 2, threadDepth + threadOverlap, +diaMajorThreadHalfHeight, pitch, height, inset, frac))
            .val()
        )
        # print(f"major2={major2}")
        # show(major2, "major2")

        f1 = cq.Face.makeRuledSurface(minor1, minor2)
        # show(f1, "f1")
        f2 = cq.Face.makeRuledSurface(major1, major2)
        # show(f2, "f2")
        f3 = cq.Face.makeRuledSurface(minor1, major1)
        # show(f3, "f3")
        f4 = cq.Face.makeRuledSurface(minor2, major2)
        # show(f4, "f4")

        sh = cq.Shell.makeShell([f1, f2, f3, f4])
        rv = cq.Solid.makeSolid(sh)

    print(f"threadDepth={threadDepth}")
    # show(rv, "rv")

    return rv, threadDepth


pitch = 1
angleDegs = 60
inset = pitch / 4  # Adjust z by inset so threads are inset from the bottom?
threadOverlap = 0  # Set to something like 0.001 if non-manifold
stlTolerance = 1e-3

nominalMajorDia = 8
nutAdjustment = 0
nutDiameter = nominalMajorDia - nutAdjustment
nutRadius = nutDiameter / 2
nutHeight = 4  # Nut height
nutSpan = 12  # Nut circumference and distance between flats

boltAdjustment = 0.1
boltDiameter = nominalMajorDia - boltAdjustment
boltRadius = (boltDiameter / 2)
boltHeight = 10
boltWallThickness = 2  # amount substracted from bolt radius to hollow out the bolt

majorPd=8
minorPd=4

boltThreads, threadDepth = threadHelix(
    boltHeight, boltDiameter, pitch=pitch, angleDegs=60, diaMajorCutOffPitchDivisor=minorPd, diaMinorCutOffPitchDivisor=minorPd, inset=inset, frac=0.1,
)
print(f"threadDepth={threadDepth}")
boltThreadsBb: cq.BoundBox = boltThreads.BoundingBox()
print(f"boltThreadsBb={vars(boltThreadsBb)}")
# show(boltThreads.translate((radius * 4, 0, 0)), "botThreads+4")
# show(boltThreads, "botThreads-0")


boltCoreRadius = boltRadius - threadDepth + 0.001
print(f"boltCoreRadius={boltCoreRadius} boltRadius={boltRadius:.3f} threadDepth={threadDepth}")

boltCore = (
    cq.Workplane("XY", origin=(0, 0, 0))
    .circle(boltCoreRadius)
    .circle(boltCoreRadius - boltWallThickness)
    .extrude(boltHeight + (2 * inset))
)
boltCoreBb: cq.BoundBox = cast(cq.Shape, boltCore.val()).BoundingBox()
print(f"boltCoreBb={vars(boltCoreBb)}")
# show(boltCore.translate((radius * 4, 0, 0)), "boltCore+4")
# show(boltCore, "boltCore-0")

bolt = boltCore.union(boltThreads)
# show(bolt.translate((radius * 4, 0, 0)), "bolt+4")
show(bolt, "bolt-0")
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
print("begin export")
fname = f"bolt-dia_{boltDiameter:.3f}-pitch_{pitch:.3f}-depth_{threadDepth:.3f}-height_{boltHeight:.3f}-mjPd_{majorPd}-miPd_{minorPd:}-to_{threadOverlap:.4f}-tol_{stlTolerance:.3f}.stl"
cq.exporters.export(bolt, fname, tolerance=stlTolerance)
print("done  export")
#
# fname = f"nut-dia_{nutDiameter:.3f}-pitch_{pitch:.3f}-depth_{threadDepth:.3f}-height_{nutHeight:.3f}-mjPd_{majorPd}-miPd_{minorPd}-to_{threadOverlap:.4f}-tol_{stlTolerance:.3f}.stl"
# cq.exporters.export(nut, fname, tolerance=stlTolerance)
