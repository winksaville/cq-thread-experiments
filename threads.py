from math import atan, cos, degrees, pi, radians, sin, tan
from typing import Tuple, Union, cast

import cadquery as cq
from taperable_helix import helix

from wing_utils import setCtx, show

setCtx(globals())


helixCount: int = 0


def threads(
    height: float,
    dia_major: float,
    pitch: float = 1,
    angle_degs: float = 60,
    external_threads: bool = True,
    dia_major_cutoff_pitch_divisor: Union[float, None] = 8,
    dia_minor_cutoff_pitch_divisor: Union[float, None] = 4,
    thread_overlap: float = 0.0001,
    inset: float = 0,
    taper_rpos: float = 0.10,
) -> Tuple[cq.Solid, float]:
    """
    Create a thread helix which may be triangular or trapizodal.

    You can control the size and spacing of the threads using
    the various using the parameters.

    :param height: Height including top and bottom inset
    :param dia_major: Diameter of threads its largest dimension
    :param pitch: Peek to Peek measurement of the threads in units default is mm
    :param angle_degs: Angle of the thread profile in degrees
    :param dia_major_cutoff_pitch_divisor: is v in pitch/v to determine size of MajorCutOff
        typically None for nuts as there is overlap with the nut barrel
    :param dia_minor_cutoff_pitch_divisor: is v in pitch/v to determin size of MinorCutOff
        typically None for bolts so there is overlap with the stud
    :param thread_overlap: amount to increase alter dimensions so threads and core overlap
        and a manifold is created
    :param inset: number units in the z direction
    :param taper_rpos: percent of threads which are tapered at the ends
    :returns: Solid representing the threads and float dept
    """

    # print(f"threads:+ height={height:.3f} dia_major={dia_major:.3f} pitch={pitch:.3f} angle_degs={angle_degs:.3f} external_threads={external_threads}")
    # print(f"threads: dia_major_cutoff_pitch_divisor={dia_major_cutoff_pitch_divisor} dia_minor_cutoff_pitch_divisor={dia_minor_cutoff_pitch_divisor}")
    # print(f"threads: thread_overlap={thread_overlap:.3f} inset={inset:.3f} taper_rpos={taper_rpos:.3f}")

    angle_radians: float = radians(angle_degs)
    tan_angle: float = tan(angle_radians)
    dia_major_cutoff: float = (pitch / dia_major_cutoff_pitch_divisor) if (
        dia_major_cutoff_pitch_divisor is not None
    ) else 0
    dia_minor_cutoff: float = (pitch / dia_minor_cutoff_pitch_divisor) if (
        dia_minor_cutoff_pitch_divisor is not None
    ) else 0
    # print(f"threads: dia_majorCutOff={dia_majorCutOff:.3f} diaMinorCutOff={diaMinorCutOff:.3f}")
    dia_major_thread_half_height: float = dia_major_cutoff / 2
    dia_minor_thread_half_height: float = (pitch - dia_minor_cutoff) / 2
    # print(f"threads: dia_majorThreadHalfHeight={dia_majorThreadHalfHeight:.3f} diaMinorThreadHalfHeight={diaMinorThreadHalfHeight:.3f} threadDepth={threadDepth:.3f}")
    tip_to_dia_major: float = dia_major_thread_half_height * tan_angle
    tip_to_dia_minor: float = dia_minor_thread_half_height * tan_angle
    # print(f"threads: dia_majorToTip={dia_majorToTip:.3f} diaMinorToTip={diaMinorToTip:.3f}")
    thread_depth: float = tip_to_dia_minor - tip_to_dia_major
    # print(f"threads: threadDepth={threadDepth}")

    helix_radius: float
    td: float
    if external_threads:
        # External threads
        helix_radius = (dia_major / 2) - (thread_depth + thread_overlap)
        thread_half_height_at_helix_radius = (pitch - dia_minor_cutoff) / 2
        thread_half_height_at_opposite_helix_radius = dia_major_cutoff / 2
        td = thread_depth + thread_overlap
    else:
        # Internal threads
        helix_radius = (dia_major / 2) + thread_overlap
        thread_half_height_at_helix_radius = (pitch - dia_major_cutoff) / 2
        thread_half_height_at_opposite_helix_radius = dia_minor_cutoff / 2
        td = -(thread_depth + thread_overlap)

    rv: cq.Solid = None

    # print(f"threads: dia_major={dia_major:.3f} helix_radius={helix_radius:.3f} td={td:.3f}")

    wires: cq.Wire = []

    wires.append(
        cq.Workplane("XY")
        .parametricCurve(
            helix(
                helix_radius,
                pitch,
                height,
                taper_rpos,
                inset,
                0,
                -thread_half_height_at_helix_radius,
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
                helix_radius,
                pitch,
                height,
                taper_rpos,
                inset,
                0,
                +thread_half_height_at_helix_radius,
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
                helix_radius,
                pitch,
                height,
                taper_rpos,
                inset,
                td,
                -thread_half_height_at_opposite_helix_radius,
            )
        )
        .val()
    )
    # print(f"threads: wires[2]={wires[2]}")
    # show(wires[2], "wires[2]")

    if dia_major_thread_half_height > 0:
        # Add a four wire, bottom major
        wires.append(
            cq.Workplane("XY")
            .parametricCurve(
                helix(
                    helix_radius,
                    pitch,
                    height,
                    taper_rpos,
                    inset,
                    td,
                    +thread_half_height_at_opposite_helix_radius,
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

    return rv, thread_depth
