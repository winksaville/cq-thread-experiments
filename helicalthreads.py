from copy import deepcopy
from dataclasses import dataclass
from math import degrees, radians, sin, tan
from typing import List

from taperable_helix import Helix, HelixLocation, helix


@dataclass
class HelicalThreadDim(Helix):
    """
    A set of dimensions used to represent helical threads.compute int_hexlix_radius, int_helixes,
    ext_helix_radius and ext_helixes. The helixes are an array of HelixLocations
    that define the helixes which from the threads. If minor_cutoff is 0 then the
    threads will be triangular and the length of the {int|ext}_helixes 3. if
    minor_cutoff > 0 then the threads will be trapezoids with the length of the
    {int|ext}_helixesarrays will be 4.

    You can control the size and spacing of the threads using
    the various using the parameters.
    """

    angle_degs: float = 45
    ext_clearance: float = 0.1
    major_cutoff: float = 0
    minor_cutoff: float = 0
    thread_overlap: float = 0.001


class HelicalThreads:
    """
    The helixes representing the internal threads, prefixed with 'int_' and
    the external threads, prefixed with 'ext_'
    """

    # The basic Dimensions of the helixes
    htd: HelicalThreadDim

    # The internal thread radius and an array of HelixLocation
    int_helix_radius: float
    int_helixes: List[HelixLocation]

    # The external thread radius and an array of HelixLocation
    ext_helix_radius: float
    ext_helixes: List[HelixLocation]

    def __init__(self, htd: HelicalThreadDim) -> None:
        self.htd = htd
        self.int_helix_radius = 0
        self.int_helixes = []
        self.ext_helix_radius = 0
        self.ext_helixes = []


def helical_threads(htd: HelicalThreadDim) -> HelicalThreads:
    """
    Given HelicalThreadDim compute the internal and external
    threads and return HelicaThreads.
    """
    # print(
    #     f"helical_threads:+ height={height:.3f} pitch={pitch:.3f} angle_degs={angle_degs:.3f}"
    # )
    # print(
    #     f"helical_threads: inset={inset:.3f} ext_clearance={ext_clearance} taper_rpos={taper_rpos:.3f}"
    # )
    # print(
    #     f"helical_threads: major_cutoff={major_cutoff} minor_cutoff={minor_cutoff} thread_overlap={thread_overlap:.3f} "
    # )
    # print(
    #     f"helical_threads: first_t={first_t} last_t={last_t} "
    # )

    result: HelicalThreads = HelicalThreads(htd)

    angle_radians: float = radians(htd.angle_degs)
    tan_hangle: float = tan(angle_radians / 2)
    sin_hangle: float = sin(angle_radians / 2)
    tip_to_major_cutoff: float = ((htd.pitch - htd.major_cutoff) / 2) / tan_hangle
    tip_to_minor_cutoff: float = (htd.minor_cutoff / 2) / tan_hangle
    # print(
    #     f"helical_threads: tip_to_major_cutoff={tip_to_major_cutoff:.3f} tip_to_minor_cutoff={tip_to_minor_cutoff:.3f}"
    # )
    int_thread_depth: float = tip_to_major_cutoff - tip_to_minor_cutoff
    # print(f"helical_threads: int_thread_depth={int_thread_depth}")

    thread_overlap_vert_adj: float = htd.thread_overlap * tan_hangle
    thread_half_height_at_helix_radius: float = (
        (htd.pitch - htd.major_cutoff) / 2
    ) + thread_overlap_vert_adj
    thread_half_height_at_opposite_helix_radius: float = htd.minor_cutoff / 2
    # print(
    #     f"thh_at_r={thread_half_height_at_helix_radius} thh_at_or={thread_half_height_at_opposite_helix_radius} td={int_thread_depth}"
    # )

    # Internal threads have helix thread radisu
    result.int_helix_radius = htd.radius
    result.int_helixes = []

    # print(f"result.int_helix_radius={result.int_helix_radius}")
    hl = HelixLocation(
        radius=result.int_helix_radius + htd.thread_overlap,
        horz_offset=0,
        vert_offset=-thread_half_height_at_helix_radius,
    )
    result.int_helixes.append(hl)

    hl = HelixLocation(
        radius=result.int_helix_radius + htd.thread_overlap,
        horz_offset=0,
        vert_offset=+thread_half_height_at_helix_radius,
    )
    result.int_helixes.append(hl)

    hl = HelixLocation(
        radius=result.int_helix_radius,
        horz_offset=-int_thread_depth,
        vert_offset=+thread_half_height_at_opposite_helix_radius,
    )
    result.int_helixes.append(hl)

    if htd.minor_cutoff > 0:
        hl = HelixLocation(
            radius=result.int_helix_radius,
            horz_offset=-int_thread_depth,
            vert_offset=-thread_half_height_at_opposite_helix_radius,
        )
        result.int_helixes.append(hl)

    # Use ext_clearance to calcuate external thread values

    # hyp is the hypothense of the trinagle formed by a radial
    # line, the tip of the internal thread and the tip of the
    # external thread.
    hyp: float = htd.ext_clearance / sin_hangle

    # ext_vert_adj is the amount to ajdust verticaly the helix
    ext_vert_adj: float = (hyp - htd.ext_clearance) * tan_hangle
    # print(f"hyp={hyp} ext_vert_adj={ext_vert_adj}")

    # External threads have the helix on the minor side and
    # so we subtract the int_thread_depth and ext_clearance from htd.radius
    result.ext_helix_radius = htd.radius - int_thread_depth - htd.ext_clearance
    # print(
    #     f"result.ext_helix_radius={htd.ext_helix_radius} td={int_thread_depth} ec={htd.ext_clearance}"
    # )

    ext_thread_half_height_at_ext_helix_radius: float = (
        ((htd.pitch - htd.minor_cutoff) / 2) - ext_vert_adj
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
    ext_thread_half_height_at_opposite_ext_helix_radius: float = (
        htd.major_cutoff / 2
    ) - ext_vert_adj
    ext_thread_depth: float = int_thread_depth
    if ext_thread_half_height_at_opposite_ext_helix_radius < 0:
        ext_thread_half_height_at_opposite_ext_helix_radius = 0
        ext_thread_depth = ext_thread_half_height_at_ext_helix_radius / tan_hangle

    # print(
    #     f"ext_thread_depth={ext_thread_depth} ext_thh_at_ehr={ext_thread_half_height_at_ext_helix_radius} ext_thh_at_ehr_plus_tovo={ext_thread_half_height_at_ext_helix_radius_plus_tova} ext_thh_at_oehr={ext_thread_half_height_at_opposite_ext_helix_radius}"
    # )

    result.ext_helixes = []
    hl = HelixLocation(
        radius=result.ext_helix_radius - htd.thread_overlap,
        horz_offset=0,
        vert_offset=-ext_thread_half_height_at_ext_helix_radius_plus_tova,
    )
    result.ext_helixes.append(hl)

    hl = HelixLocation(
        radius=result.ext_helix_radius - htd.thread_overlap,
        horz_offset=0,
        vert_offset=+ext_thread_half_height_at_ext_helix_radius_plus_tova,
    )
    result.ext_helixes.append(hl)

    hl = HelixLocation(
        radius=result.ext_helix_radius,
        horz_offset=ext_thread_depth,
        vert_offset=+ext_thread_half_height_at_opposite_ext_helix_radius,
    )
    result.ext_helixes.append(hl)

    if ext_thread_half_height_at_opposite_ext_helix_radius > 0:
        hl = HelixLocation(
            radius=result.ext_helix_radius,
            horz_offset=ext_thread_depth,
            vert_offset=-ext_thread_half_height_at_opposite_ext_helix_radius,
        )
        result.ext_helixes.append(hl)

    return result
