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

        # Reduce the height by 2 * inset. Threads start at inset
        # and end at height - inset.
        # so the thread
        heightThreads = height - (2 * inset)

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
        z: float = (heightThreads * t) + (threadHalfHeight * fadeScale) + inset
        r: float = radius + (threadDepth * fadeScale)
        # print(f"helix.func:  r={r:.3f} radius={radius:.3f} + (threadDepth={threadDepth:.3f} * fadeScale={fadeScale:.3f})")

        a: float = 2 * pi / (pitch / heightThreads) * t
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
    externalThreads: bool = True,
    diaMajorCutOffPitchDivisor: Union[float, None] = 8,
    diaMinorCutOffPitchDivisor: Union[float, None] = 4,
    threadOverlap: float = 0.0001,
    inset: float = 0,
    frac: float = 0.10,
) -> Tuple[cq.Solid, float]:
    """
    Create a thread helix which may be triangular or trapizodal.

    You can control the size and spacing of the threads using
    the various using the parameters.

    :param height: Height including top and bottom inset
    :param diaMajor: Diameter of threads its largest dimension
    :param pitch: Peek to Peek measurement of the threads in units default is mm
    :param angleDegs: Angle of the thread profile in degrees
    :param diaMajorCutOffPitchDivisor: is v in pitch/v to determine size of MajorCutOff
    typically None for nuts as there is overlap with the nut barrel
    :param diaMinorCutOffPitchDivisor: is v in pitch/v to determin size of MinorCutOff
    typically None for bolts so there is overlap with the stud
    :param threadOverlap: amount to increase alter dimensions so threads and core overlap
    and a manifold is created
    :param inset: number units in the z direction
    :param frac: percent of threads for fade in and fade out
    :returns: Solid representing the threads and float dept
    """

    # print(f"threadHelix:+ height={height:.3f} diaMajor={diaMajor:.3f} pitch={pitch:.3f} angleDegs={angleDegs:.3f} externalThreads={externalThreads}")
    # print(f"threadHelix: diaMajorCutOffPitchDivisor={diaMajorCutOffPitchDivisor} diaMinorCutOffPitchDivisor={diaMinorCutOffPitchDivisor}")
    # print(f"threadHelix: threadOverlap={threadOverlap:.3f} inset={inset:.3f} frac={frac:.3f}")

    angleRadians: float = radians(angleDegs)
    tanAngle: float = tan(angleRadians)
    diaMajorCutOff: float = (pitch / diaMajorCutOffPitchDivisor) if (
        diaMajorCutOffPitchDivisor is not None
    ) else 0
    diaMinorCutOff: float = (pitch / diaMinorCutOffPitchDivisor) if (
        diaMinorCutOffPitchDivisor is not None
    ) else 0
    # print(f"threadHelix: diaMajorCutOff={diaMajorCutOff:.3f} diaMinorCutOff={diaMinorCutOff:.3f}")
    diaMajorThreadHalfHeight: float = diaMajorCutOff / 2
    diaMinorThreadHalfHeight: float = (pitch - diaMinorCutOff) / 2
    # print(f"threadHelix: diaMajorThreadHalfHeight={diaMajorThreadHalfHeight:.3f} diaMinorThreadHalfHeight={diaMinorThreadHalfHeight:.3f} threadDepth={threadDepth:.3f}")
    diaMajorToTip: float = diaMajorThreadHalfHeight * tanAngle
    diaMinorToTip: float = diaMinorThreadHalfHeight * tanAngle
    # print(f"threadHelix: diaMajorToTip={diaMajorToTip:.3f} diaMinorToTip={diaMinorToTip:.3f}")
    threadDepth: float = diaMinorToTip - diaMajorToTip
    # print(f"threadHelix: threadDepth={threadDepth}")

    helixRadius: float
    td: float
    if externalThreads:
        # External threads
        helixRadius = (diaMajor / 2) - (threadDepth + threadOverlap)
        helixThreadHalfHeightAtRadius = (pitch - diaMinorCutOff) / 2
        helixThreadHalfHeightOppositeRadius = diaMajorCutOff / 2
        td = threadDepth + threadOverlap
    else:
        # Internal threads
        helixRadius = (diaMajor / 2) + threadOverlap
        helixThreadHalfHeightAtRadius = (pitch - diaMajorCutOff) / 2
        helixThreadHalfHeightOppositeRadius = diaMinorCutOff / 2
        td = -(threadDepth + threadOverlap)

    rv: cq.Solid = None

    # print(f"threadHelix: diaMajor={diaMajor:.3f} helixRadius={helixRadius:.3f} td={td:.3f}")

    wires: cq.Wire = []

    wires.append(
        cq.Workplane("XY")
        .parametricCurve(
            helix(
                helixRadius,
                0,
                -helixThreadHalfHeightAtRadius,
                pitch,
                height,
                inset,
                frac,
            )
        )
        .val()
    )
    # print(f"threadHelix: wires[0]={wires[0]}")
    # show(wires[0], "wires[0]")

    wires.append(
        cq.Workplane("XY")
        .parametricCurve(
            helix(
                helixRadius,
                0,
                +helixThreadHalfHeightAtRadius,
                pitch,
                height,
                inset,
                frac,
            )
        )
        .val()
    )
    # print(f"threadHelix: wires[1]={wires[1]}")
    # show(wires[1], "wires[1]")

    wires.append(
        cq.Workplane("XY")
        .parametricCurve(
            helix(
                helixRadius,
                td,
                -helixThreadHalfHeightOppositeRadius,
                pitch,
                height,
                inset,
                frac,
            )
        )
        .val()
    )
    # print(f"threadHelix: wires[2]={wires[2]}")
    # show(wires[2], "wires[2]")

    if diaMajorThreadHalfHeight > 0:
        # Add a four wire, bottom major
        wires.append(
            cq.Workplane("XY")
            .parametricCurve(
                helix(
                    helixRadius,
                    td,
                    +helixThreadHalfHeightOppositeRadius,
                    pitch,
                    height,
                    inset,
                    frac,
                )
            )
            .val()
        )
        # print(f"threadHelix: wires[3]={wires[3]}")
        # show(wires[3], "wires[3]")

    lenWires = len(wires)
    assert (lenWires == 3) or (lenWires == 4)
    # print(f"threadHelix: wires.len={len(wires)}")

    # Create the faces of the thread and then create a solid
    faces: cq.Faces = []
    faces.append(cq.Face.makeRuledSurface(wires[0], wires[1]))
    faces.append(cq.Face.makeRuledSurface(wires[-2], wires[-1]))
    faces.append(cq.Face.makeRuledSurface(wires[0], wires[2]))
    if lenWires == 4:
        faces.append(cq.Face.makeRuledSurface(wires[1], wires[-1]))
    sh = cq.Shell.makeShell(faces)
    rv = cq.Solid.makeSolid(sh)

    # print(f"threadHelix:- threadDepth={threadDepth} rv={rv}")
    # show(rv, "rv")

    return rv, threadDepth


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

boltThreads, threadDepth = threadHelix(
    height=boltHeight,
    diaMajor=boltDiameter,
    pitch=pitch,
    angleDegs=angleDegs,
    diaMajorCutOffPitchDivisor=majorPd * 1.1,
    diaMinorCutOffPitchDivisor=minorPd * 1.1,
    threadOverlap=threadOverlap,
    inset=inset,
    frac=0.1,
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

nutThreads, threadDepth = threadHelix(
    height=nutHeight,
    diaMajor=nutDiameter,
    pitch=pitch,
    angleDegs=angleDegs,
    externalThreads=False,
    diaMajorCutOffPitchDivisor=majorPd,
    diaMinorCutOffPitchDivisor=minorPd,
    threadOverlap=threadOverlap,
    inset=inset,
    frac=0.1,
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
