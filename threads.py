from math import atan, cos, degrees, pi, radians, sin, tan
from typing import Tuple, Union, cast

import cadquery as cq
from taperable_helix import helix

from wing_utils import setCtx, show

setCtx(globals())


helixCount: int = 0


def threads(
    height: float,
    diaMajor: float,
    pitch: float = 1,
    angleDegs: float = 60,
    externalThreads: bool = True,
    diaMajorCutOffPitchDivisor: Union[float, None] = 8,
    diaMinorCutOffPitchDivisor: Union[float, None] = 4,
    threadOverlap: float = 0.0001,
    inset: float = 0,
    taper_rpos: float = 0.10,
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
    :param taper_rpos: percent of threads which are tapered at the ends
    :returns: Solid representing the threads and float dept
    """

    # print(f"threads:+ height={height:.3f} diaMajor={diaMajor:.3f} pitch={pitch:.3f} angleDegs={angleDegs:.3f} externalThreads={externalThreads}")
    # print(f"threads: diaMajorCutOffPitchDivisor={diaMajorCutOffPitchDivisor} diaMinorCutOffPitchDivisor={diaMinorCutOffPitchDivisor}")
    # print(f"threads: threadOverlap={threadOverlap:.3f} inset={inset:.3f} taper_rpos={taper_rpos:.3f}")

    angleRadians: float = radians(angleDegs)
    tanAngle: float = tan(angleRadians)
    diaMajorCutOff: float = (pitch / diaMajorCutOffPitchDivisor) if (
        diaMajorCutOffPitchDivisor is not None
    ) else 0
    diaMinorCutOff: float = (pitch / diaMinorCutOffPitchDivisor) if (
        diaMinorCutOffPitchDivisor is not None
    ) else 0
    # print(f"threads: diaMajorCutOff={diaMajorCutOff:.3f} diaMinorCutOff={diaMinorCutOff:.3f}")
    diaMajorThreadHalfHeight: float = diaMajorCutOff / 2
    diaMinorThreadHalfHeight: float = (pitch - diaMinorCutOff) / 2
    # print(f"threads: diaMajorThreadHalfHeight={diaMajorThreadHalfHeight:.3f} diaMinorThreadHalfHeight={diaMinorThreadHalfHeight:.3f} threadDepth={threadDepth:.3f}")
    diaMajorToTip: float = diaMajorThreadHalfHeight * tanAngle
    diaMinorToTip: float = diaMinorThreadHalfHeight * tanAngle
    # print(f"threads: diaMajorToTip={diaMajorToTip:.3f} diaMinorToTip={diaMinorToTip:.3f}")
    threadDepth: float = diaMinorToTip - diaMajorToTip
    # print(f"threads: threadDepth={threadDepth}")

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

    # print(f"threads: diaMajor={diaMajor:.3f} helixRadius={helixRadius:.3f} td={td:.3f}")

    wires: cq.Wire = []

    wires.append(
        cq.Workplane("XY")
        .parametricCurve(
            helix(
                helixRadius,
                pitch,
                height,
                taper_rpos,
                inset,
                0,
                -helixThreadHalfHeightAtRadius,
            )
        )
        .val()
    )
    # print(f"threads: wires[0]={wires[0]}")
    # show(wires[0], "wires[0]")

    wires.append(
        cq.Workplane("XY")
        .parametricCurve(
            helix(
                helixRadius,
                pitch,
                height,
                taper_rpos,
                inset,
                0,
                +helixThreadHalfHeightAtRadius,
            )
        )
        .val()
    )
    # print(f"threads: wires[1]={wires[1]}")
    # show(wires[1], "wires[1]")

    wires.append(
        cq.Workplane("XY")
        .parametricCurve(
            helix(
                helixRadius,
                pitch,
                height,
                taper_rpos,
                inset,
                td,
                -helixThreadHalfHeightOppositeRadius,
            )
        )
        .val()
    )
    # print(f"threads: wires[2]={wires[2]}")
    # show(wires[2], "wires[2]")

    if diaMajorThreadHalfHeight > 0:
        # Add a four wire, bottom major
        wires.append(
            cq.Workplane("XY")
            .parametricCurve(
                helix(
                    helixRadius,
                    pitch,
                    height,
                    taper_rpos,
                    inset,
                    td,
                    +helixThreadHalfHeightOppositeRadius,
                )
            )
            .val()
        )
        # print(f"threads: wires[3]={wires[3]}")
        # show(wires[3], "wires[3]")

    lenWires = len(wires)
    assert (lenWires == 3) or (lenWires == 4)
    # print(f"threads: wires.len={len(wires)}")

    # Create the faces of the thread and then create a solid
    faces: cq.Faces = []
    faces.append(cq.Face.makeRuledSurface(wires[0], wires[1]))
    faces.append(cq.Face.makeRuledSurface(wires[-2], wires[-1]))
    faces.append(cq.Face.makeRuledSurface(wires[0], wires[2]))
    if lenWires == 4:
        faces.append(cq.Face.makeRuledSurface(wires[1], wires[-1]))
    sh = cq.Shell.makeShell(faces)
    rv = cq.Solid.makeSolid(sh)

    # print(f"threads:- threadDepth={threadDepth} rv={rv}")
    # show(rv, "rv")

    return rv, threadDepth
