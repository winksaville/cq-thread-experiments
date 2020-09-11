from math import atan, cos, degrees, pi, radians, sin, tan
from typing import Tuple, Union, cast

import cadquery as cq
from taperable_helix import helix

from wing_utils import perpendicular_distance_pt_to_line_2d, setCtx, show

setCtx(globals())


helixCount: int = 0


class ThreadDimensions:
    """
    Dimensions of thread
    """

    height: float
    pitch: float
    dia_major: float
    angle_degs: float
    external_threads: bool
    dia_major_cutoff_pitch_divisor: Union[float, None]
    dia_minor_cutoff_pitch_divisor: Union[float, None]
    thread_overlap: float
    inset: float
    taper_rpos: float

    angle_radians: float
    tan_angle: float
    dia_major_cutoff: float
    dia_minor_cutoff: float
    dia_major_thread_half_height: float
    dia_minor_thread_half_height: float
    tip_to_dia_major: float
    tip_to_dia_minor: float
    thread_depth: float

    helix_radius: float
    thread_depth_plus_overlap: float
    thread_half_height_at_helix_radius: float
    thread_half_height_at_opposite_helix_radius: float

    def __init__(
        self,
        height: float,
        pitch: float,
        dia_major: float,
        angle_degs: float,
        external_threads: bool,
        dia_major_cutoff_pitch_divisor: Union[float, None],
        dia_minor_cutoff_pitch_divisor: Union[float, None],
        thread_overlap: float,
        inset: float,
        taper_rpos: float,
    ) -> None:
        # print(f"ThreadDimensions:+ height={height:.3f} dia_major={dia_major:.3f} pitch={pitch:.3f} angle_degs={angle_degs:.3f} external_threads={external_threads}")
        # print(f"ThreadDimensions: dia_major_cutoff_pitch_divisor={dia_major_cutoff_pitch_divisor} dia_minor_cutoff_pitch_divisor={dia_minor_cutoff_pitch_divisor}")
        # print(f"ThreadDimensions: thread_overlap={thread_overlap:.3f} inset={inset:.3f} taper_rpos={taper_rpos:.3f}")

        self.height = height
        self.pitch = pitch
        self.dia_major = dia_major
        self.angle_degs = angle_degs
        self.external_threads = external_threads
        self.dia_major_cutoff_pitch_divisor = dia_major_cutoff_pitch_divisor
        self.dia_minor_cutoff_pitch_divisor = dia_minor_cutoff_pitch_divisor
        self.thread_overlap = thread_overlap
        self.inset = inset
        self.taper_rpos = taper_rpos

        self.angle_radians = radians(angle_degs)
        self.tan_angle = tan(self.angle_radians)
        self.dia_major_cutoff = (
            (pitch / dia_major_cutoff_pitch_divisor)
            if (dia_major_cutoff_pitch_divisor is not None)
            else 0
        )
        self.dia_minor_cutoff = (
            (pitch / dia_minor_cutoff_pitch_divisor)
            if (dia_minor_cutoff_pitch_divisor is not None)
            else 0
        )
        self.dia_major_thread_half_height: float = self.dia_major_cutoff / 2
        self.dia_minor_thread_half_height: float = (pitch - self.dia_minor_cutoff) / 2
        # print(f"ThreadDimensions: dia_majorThreadHalfHeight={dia_majorThreadHalfHeight:.3f} diaMinorThreadHalfHeight={diaMinorThreadHalfHeight:.3f} threadDepth={threadDepth:.3f}")
        self.tip_to_dia_major: float = self.dia_major_thread_half_height * self.tan_angle
        self.tip_to_dia_minor: float = self.dia_minor_thread_half_height * self.tan_angle
        # print(f"ThreadDimensions: dia_majorToTip={dia_majorToTip:.3f} diaMinorToTip={diaMinorToTip:.3f}")
        self.thread_depth: float = self.tip_to_dia_minor - self.tip_to_dia_major
        # print(f"ThreadDimensions: threadDepth={threadDepth}")

        if external_threads:
            # External threads
            self.helix_radius = (dia_major / 2) - (self.thread_depth + thread_overlap)
            self.thread_half_height_at_helix_radius = (
                pitch - self.dia_minor_cutoff
            ) / 2
            self.thread_half_height_at_opposite_helix_radius = self.dia_major_cutoff / 2
            self.thread_depth_plus_overlap = self.thread_depth + thread_overlap
        else:
            # Internal threads
            self.helix_radius = (dia_major / 2) + thread_overlap
            self.thread_half_height_at_helix_radius = (
                pitch - self.dia_major_cutoff
            ) / 2
            self.thread_half_height_at_opposite_helix_radius = self.dia_minor_cutoff / 2
            self.thread_depth_plus_overlap = -(self.thread_depth + thread_overlap)

        # print(f"ThreadDimensions: threadDepth={threadDepth}")


def threads(
    height: float,
    pitch: float,
    dia_major: float,
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

    td = ThreadDimensions(
        height,
        pitch,
        dia_major,
        angle_degs,
        external_threads,
        dia_major_cutoff_pitch_divisor,
        dia_minor_cutoff_pitch_divisor,
        thread_overlap,
        inset,
        taper_rpos,
    )
    print(f"td={vars(td)}")

    wires: cq.Wire = []

    wires.append(
        cq.Workplane("XY")
        .parametricCurve(
            helix(
                td.helix_radius,
                pitch,
                height,
                taper_rpos,
                inset,
                0,
                -td.thread_half_height_at_helix_radius,
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
                td.helix_radius,
                pitch,
                height,
                taper_rpos,
                inset,
                0,
                +td.thread_half_height_at_helix_radius,
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
                td.helix_radius,
                pitch,
                height,
                taper_rpos,
                inset,
                td.thread_depth_plus_overlap,
                -td.thread_half_height_at_opposite_helix_radius,
            )
        )
        .val()
    )
    # print(f"threads: wires[2]={wires[2]}")
    # show(wires[2], "wires[2]")

    if td.dia_major_cutoff > 0:
        # Add a fourth wire, bottom major
        wires.append(
            cq.Workplane("XY")
            .parametricCurve(
                helix(
                    td.helix_radius,
                    pitch,
                    height,
                    taper_rpos,
                    inset,
                    td.thread_depth_plus_overlap,
                    +td.thread_half_height_at_opposite_helix_radius,
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
    sh: cq.Shell = cq.Shell.makeShell(faces)
    rv: cq.Solid = cq.Solid.makeSolid(sh)

    # print(f"threads:- threadDepth={threadDepth} rv={rv}")
    # show(rv, "rv")

    return rv, td.thread_depth
