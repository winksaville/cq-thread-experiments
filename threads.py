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
    inset: float
    ext_clearance: float
    taper_rpos: float
    major_cutoff: float
    minor_cutoff: float
    thread_overlap: float

    int_helix_radius: float
    int_helixes: List[HelixLocation] = []

    ext_helix_radius: float
    ext_helixes: List[HelixLocation] = []

    def __init__(
        self,
        height: float,
        pitch: float,
        dia_major: float,
        angle_degs: float,
        inset: float,
        ext_clearance: float,
        taper_rpos: float,
        major_cutoff: float,
        minor_cutoff: float,
        thread_overlap: float,
    ) -> None:
        print(
            f"ThreadDimensions:+ height={height:.3f} dia_major={dia_major:.3f} pitch={pitch:.3f} angle_degs={angle_degs:.3f}"
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
        self.major_cutoff = major_cutoff
        self.minor_cutoff = minor_cutoff
        self.thread_overlap = thread_overlap
        self.inset = inset
        self.taper_rpos = taper_rpos
        self.ext_clearance = ext_clearance

        angle_radians: float = radians(angle_degs)
        tan_hangle: float = tan(angle_radians / 2)
        sin_hangle: float = sin(angle_radians / 2)
        tip_to_major_cutoff: float = ((pitch - self.major_cutoff) / 2) / tan_hangle
        tip_to_minor_cutoff: float = (self.minor_cutoff / 2) / tan_hangle
        print(
            f"ThreadDimensions: tip_to_major_cutoff={tip_to_major_cutoff:.3f} tip_to_minor_cutoff={tip_to_minor_cutoff:.3f}"
        )
        int_thread_depth: float = tip_to_major_cutoff - tip_to_minor_cutoff
        print(f"ThreadDimensions: int_thread_depth={int_thread_depth}")

        # Internal threads have helix thread at the dia_major side
        self.int_helix_radius = self.dia_major / 2
        print(f"self.int_helix_radius={self.int_helix_radius}")

        thread_overlap_vert_adj: float = self.thread_overlap * tan_hangle
        thread_half_height_at_helix_radius: float = (
            (pitch - self.major_cutoff) / 2
        ) + thread_overlap_vert_adj
        thread_half_height_at_opposite_helix_radius: float = self.minor_cutoff / 2
        print(
            f"thh_at_r={thread_half_height_at_helix_radius} thh_at_or={thread_half_height_at_opposite_helix_radius} td={int_thread_depth}"
        )

        self.int_helixes = []
        self.int_helixes.append(
            HelixLocation(
                radius=self.int_helix_radius + self.thread_overlap,
                horz_offset=0,
                vert_offset=-thread_half_height_at_helix_radius,
            )
        )
        self.int_helixes.append(
            HelixLocation(
                radius=self.int_helix_radius + self.thread_overlap,
                horz_offset=0,
                vert_offset=+thread_half_height_at_helix_radius,
            )
        )
        self.int_helixes.append(
            HelixLocation(
                radius=self.int_helix_radius,
                horz_offset=-int_thread_depth,
                vert_offset=+thread_half_height_at_opposite_helix_radius,
            )
        )
        if self.minor_cutoff > 0:
            self.int_helixes.append(
                HelixLocation(
                    radius=self.int_helix_radius,
                    horz_offset=-int_thread_depth,
                    vert_offset=-thread_half_height_at_opposite_helix_radius,
                )
            )

        # Use ext_clearance to calcuate external thread values
        h: float = self.ext_clearance / sin_hangle
        ext_vert_adj: float = (h - self.ext_clearance) * tan_hangle
        print(f"h={h} ext_vert_adj={ext_vert_adj}")

        # External threads have the helix on the minor side and
        # so we subtract the int_thread_depth and ext_clearance from dia_major/2
        self.ext_helix_radius = (dia_major / 2) - int_thread_depth - ext_clearance
        print(
            f"self.ext_helix_radius={self.ext_helix_radius} td={int_thread_depth} ec={self.ext_clearance}"
        )

        ext_thread_half_height_at_ext_helix_radius: float = (
            ((pitch - self.minor_cutoff) / 2)
            - ext_vert_adj
        )
        ext_thread_half_height_at_ext_helix_radius_plus_tova: float = (
            ext_thread_half_height_at_ext_helix_radius + thread_overlap_vert_adj
        )

        # When major cutoff becomes smaller than the exter_vert_adj then the
        # external thread will only be three points and we set
        # ext_thrad_half_height_at_opposite_ext_helix_radius # to 0 and
        # compute the thread depth. Under these circumstances the clearance
        # from the external tip to internal core will be close to ext_clearance
        # or greater. See test_threads.py or test_threads_new.py.
        ext_thread_half_height_at_opposite_ext_helix_radius: float = (self.major_cutoff / 2) - ext_vert_adj
        ext_thread_depth: float = int_thread_depth
        if ext_thread_half_height_at_opposite_ext_helix_radius < 0:
            ext_thread_half_height_at_opposite_ext_helix_radius = 0
            ext_thread_depth = ext_thread_half_height_at_ext_helix_radius / tan_hangle

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


def _threads(external_threads: bool, td: ThreadDimensions) -> cq.Solid:
    """
    Create a thread helix which may be triangular or trapizodal.

    You can control the size and spacing of the threads using
    the various parameters to ThreadDimensions.

    :returns: Solid representing the threads and float dept
    """

    # print(f"_threads: external_threads={external_threads} td={vars(td)}")

    helix_locations: List[HelixLocation] = td.int_helixes if (
        not external_threads
    ) else td.ext_helixes

    wires: cq.Wire = [
        (
            cq.Workplane("XY")
            .parametricCurve(
                helix(
                    radius=hl.radius,
                    pitch=td.pitch,
                    height=td.height,
                    taper_rpos=td.taper_rpos,
                    inset_offset=td.inset,
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

    # show(rv, "rv")

    return rv


def int_threads(td: ThreadDimensions) -> cq.Solid:
    """
    Create internal threads which may be triangular or trapizodal.

    You can control the size and spacing of the threads using
    the various parameters to ThreadDimensions.

    :param td: ThreadDimensions
    :returns: Solid representing the threads and float dept
    """
    return _threads(False, td)


def ext_threads(td: ThreadDimensions) -> cq.Solid:
    """
    Create external threads which may be triangular or trapizodal.

    You can control the size and spacing of the threads using
    the various parameters to ThreadDimensions.

    :param td: ThreadDimensions
    :returns: Solid representing the threads and float dept
    """
    return _threads(True, td)

