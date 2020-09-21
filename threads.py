from dataclasses import dataclass
from math import atan, cos, degrees, pi, radians, sin, tan
from typing import List, Tuple, cast

import cadquery as cq
from taperable_helix import helix

from wing_utils import perpendicular_distance_pt_to_line_2d, setCtx, show

setCtx(globals())


helixCount: int = 0


@dataclass
class HelixLocation:
    radius: float
    horz_offset: float
    vert_offset: float


class ThreadDimensions:
    """
    Dimensions of thread
    """

    height: float
    pitch: float
    dia_major: float
    angle_degs: float
    external_threads: bool
    major_cutoff: float
    minor_cutoff: float
    thread_overlap: float
    inset: float
    taper_rpos: float

    angle_radians: float
    tan_hangle: float
    sin_hangle: float
    tip_to_major_cutoff: float
    tip_to_minor_cutoff: float
    thread_depth: float

    # thread_depth_plus_overlap: float
    thread_overlap_vert_adj: float
    thread_half_height_at_helix_radius: float
    thread_half_height_at_opposite_helix_radius: float

    int_helix_radius: float
    int_helixes: List[HelixLocation] = []

    ext_clearance: float
    ext_vert_adj: float
    ext_helix_radius: float
    ext_helixes: List[HelixLocation] = []

    def __init__(
        self,
        height: float,
        pitch: float,
        dia_major: float,
        angle_degs: float,
        external_threads: bool,
        major_cutoff: float,
        minor_cutoff: float,
        thread_overlap: float,
        inset: float,
        taper_rpos: float,
        ext_clearance: float,
    ) -> None:
        print(
            f"ThreadDimensions:+ height={height:.3f} dia_major={dia_major:.3f} pitch={pitch:.3f} angle_degs={angle_degs:.3f} external_threads={external_threads}"
        )
        print(
            f"ThreadDimensions: major_cutoff={major_cutoff} minor_cutoff={minor_cutoff}"
        )
        print(
            f"ThreadDimensions: thread_overlap={thread_overlap:.3f} inset={inset:.3f} taper_rpos={taper_rpos:.3f}"
        )

        self.height = height
        self.pitch = pitch
        self.dia_major = dia_major
        self.angle_degs = angle_degs
        self.external_threads = external_threads
        self.major_cutoff = major_cutoff
        self.minor_cutoff = minor_cutoff
        self.thread_overlap = thread_overlap
        self.inset = inset
        self.taper_rpos = taper_rpos
        self.ext_clearance = ext_clearance

        self.angle_radians = radians(angle_degs)
        self.tan_hangle = tan(self.angle_radians / 2)
        self.sin_hangle = sin(self.angle_radians / 2)
        self.major_cutoff = major_cutoff
        self.minor_cutoff = minor_cutoff
        self.tip_to_major_cutoff = ((pitch - self.major_cutoff) / 2) / self.tan_hangle
        self.tip_to_minor_cutoff = (self.minor_cutoff / 2) / self.tan_hangle
        print(
            f"ThreadDimensions: tip_to_major_cutoff={self.tip_to_major_cutoff:.3f} tip_to_minor_cutoff={self.tip_to_minor_cutoff:.3f}"
        )
        self.thread_depth = self.tip_to_major_cutoff - self.tip_to_minor_cutoff
        print(f"ThreadDimensions: thread_depth={self.thread_depth}")

        # Internal threads have helix thread at the dia_major side
        self.int_helix_radius = self.dia_major / 2
        print(f"self.int_helix_radius={self.int_helix_radius}")

        self.thread_overlap_vert_adj = self.thread_overlap * self.tan_hangle
        self.thread_half_height_at_helix_radius = (
            (pitch - self.major_cutoff) / 2
        ) + self.thread_overlap_vert_adj
        self.thread_half_height_at_opposite_helix_radius = self.minor_cutoff / 2
        print(
            f"thh_at_r={self.thread_half_height_at_helix_radius} thh_at_or={self.thread_half_height_at_opposite_helix_radius} td={self.thread_depth}"
        )

        self.int_helixes = []
        self.int_helixes.append(
            HelixLocation(
                radius=self.int_helix_radius + self.thread_overlap,
                horz_offset=0,
                vert_offset=-self.thread_half_height_at_helix_radius,
            )
        )
        self.int_helixes.append(
            HelixLocation(
                radius=self.int_helix_radius + self.thread_overlap,
                horz_offset=0,
                vert_offset=+self.thread_half_height_at_helix_radius,
            )
        )
        self.int_helixes.append(
            HelixLocation(
                radius=self.int_helix_radius,
                horz_offset=-self.thread_depth,
                vert_offset=+self.thread_half_height_at_opposite_helix_radius,
            )
        )
        if self.minor_cutoff > 0:
            self.int_helixes.append(
                HelixLocation(
                    radius=self.int_helix_radius,
                    horz_offset=-self.thread_depth,
                    vert_offset=-self.thread_half_height_at_opposite_helix_radius,
                )
            )

        # Use clearance to calcuate external_threads values
        h: float = self.ext_clearance / self.sin_hangle
        self.ext_vert_adj = (h - self.ext_clearance) * self.tan_hangle
        print(f"h={h} self.ext_vert_adj={self.ext_vert_adj}")

        # External threads have the helix on the minor side and
        # so we subtract the thread_depth and ext_clearance from dia_major/2
        self.ext_helix_radius = (dia_major / 2) - self.thread_depth - ext_clearance
        print(
            f"self.ext_helix_radius={self.ext_helix_radius} td={self.thread_depth} ec={self.ext_clearance}"
        )

        ext_thread_half_height_at_ext_helix_radius: float = (
            ((pitch - self.minor_cutoff) / 2)
            - self.ext_vert_adj
        )
        ext_thread_half_height_at_ext_helix_radius_plus_tova: float = (
            ext_thread_half_height_at_ext_helix_radius + self.thread_overlap_vert_adj
        )

        # When major cutoff becomes smaller than the exter_vert_adj then the
        # external thread will only be three points and we set
        # ext_thrad_half_height_at_opposite_ext_helix_radius # to 0 and
        # compute the thread depth. Under these circumstances the clearance
        # from the external tip to internal core will be close to ext_clearance
        # or greater. See test_threads.py or test_threads_new.py.
        ext_thread_half_height_at_opposite_ext_helix_radius: float = (self.major_cutoff / 2) - self.ext_vert_adj
        ext_thread_depth: float = self.thread_depth
        if ext_thread_half_height_at_opposite_ext_helix_radius < 0:
            ext_thread_half_height_at_opposite_ext_helix_radius = 0
            ext_thread_depth = ext_thread_half_height_at_ext_helix_radius / self.tan_hangle

        print(
            f"ext_thread_depth={ext_thread_depth} ext_thh_at_ehr={ext_thread_half_height_at_ext_helix_radius} ext_thh_at_ehr_plus_tovo={ext_thread_half_height_at_ext_helix_radius_plus_tova} ext_thh_at_oehr={ext_thread_half_height_at_opposite_ext_helix_radius}"
        )

        self.ext_helixes = []
        self.ext_helixes.append(
            HelixLocation(
                radius=self.ext_helix_radius - self.thread_overlap,
                horz_offset=0,
                vert_offset=-ext_thread_half_height_at_ext_helix_radius_plus_tova,
            )
        )
        self.ext_helixes.append(
            HelixLocation(
                radius=self.ext_helix_radius - self.thread_overlap,
                horz_offset=0,
                vert_offset=+ext_thread_half_height_at_ext_helix_radius_plus_tova,
            )
        )
        self.ext_helixes.append(
            HelixLocation(
                radius=self.ext_helix_radius,
                horz_offset=ext_thread_depth,
                vert_offset=+ext_thread_half_height_at_opposite_ext_helix_radius,
            )
        )
        if ext_thread_half_height_at_opposite_ext_helix_radius > 0: #self.major_cutoff > 0:
            self.ext_helixes.append(
                HelixLocation(
                    radius=self.ext_helix_radius,
                    horz_offset=ext_thread_depth,
                    vert_offset=-ext_thread_half_height_at_opposite_ext_helix_radius,
                )
            )


def threads(
    height: float,
    pitch: float,
    dia_major: float,
    angle_degs: float = 60,
    external_threads: bool = True,
    major_cutoff: float = 8,
    minor_cutoff: float = 4,
    thread_overlap: float = 0.0001,
    inset: float = 0,
    taper_rpos: float = 0.10,
    ext_clearance: float = 0,
) -> cq.Solid:
    """
    Create a thread helix which may be triangular or trapizodal.

    You can control the size and spacing of the threads using
    the various using the parameters.

    :param height: Height including top and bottom inset
    :param dia_major: Diameter of threads its largest dimension
    :param pitch: Peek to Peek measurement of the threads in units default is mm
    :param angle_degs: Angle of the thread profile in degrees
    :param major_cutoff: is v in pitch/v to determine size of MajorCutOff
        0 for no MajorCutOff
    :param minor_cutoff: is v in pitch/v to determin size of MinorCutOff
        0 for no MinorCutOff
    :param thread_overlap: amount to increase alter dimensions so threads and core overlap
        and a manifold is created
    :param inset: number units in the z direction
    :param taper_rpos: percent of threads which are tapered at the ends
    :returns: Solid representing the threads and float dept
    """

    # print(f"threads:+ height={height:.3f} dia_major={dia_major:.3f} pitch={pitch:.3f} angle_degs={angle_degs:.3f} external_threads={external_threads}")
    # print(f"threads: major_cutoff={major_cutoff} minor_cutoff={minor_cutoff}")
    # print(f"threads: thread_overlap={thread_overlap:.3f} inset={inset:.3f} taper_rpos={taper_rpos:.3f}")

    td = ThreadDimensions(
        height,
        pitch,
        dia_major,
        angle_degs,
        external_threads,
        major_cutoff,
        minor_cutoff,
        thread_overlap,
        inset,
        taper_rpos,
        ext_clearance=ext_clearance,
    )
    # print(f"td={vars(td)}")

    helix_locations: List[HelixLocation] = td.int_helixes if (
        not external_threads
    ) else td.ext_helixes

    wires: cq.Wire = [
        (
            cq.Workplane("XY")
            .parametricCurve(
                helix(
                    radius=hl.radius,
                    pitch=pitch,
                    height=height,
                    taper_rpos=taper_rpos,
                    inset_offset=inset,
                    horz_offset=hl.horz_offset,
                    vert_offset=hl.vert_offset,
                )
            )
            .val()
        )
        for hl in helix_locations
    ]

    lenWires = len(wires)
    assert (lenWires == 3) or (lenWires == 4)
    # print(f"threads: wires.len={len(wires)}")

    # Create the faces of the thread
    faces: cq.Faces = []
    faces.append(cq.Face.makeRuledSurface(wires[0], wires[1]))
    faces.append(cq.Face.makeRuledSurface(wires[1], wires[2]))
    if lenWires == 4:
        faces.append(cq.Face.makeRuledSurface(wires[2], wires[3]))
    faces.append(cq.Face.makeRuledSurface(wires[-1], wires[0]))

    # TODO: if taper_rpos == 0 we need to create end faces

    # Create the solid
    sh: cq.Shell = cq.Shell.makeShell(faces)
    rv: cq.Solid = cq.Solid.makeSolid(sh)

    print(f"threads:- thread_depth={td.thread_depth} rv={rv}")
    # show(rv, "rv")

    return rv
