from dataclasses import dataclass
from math import degrees, radians, sin, tan
from typing import List


@dataclass
class HelixLocation:
    radius: float
    horz_offset: float
    vert_offset: float


class HelicalThreads:
    """
    Given a set of dimensions compute int_hexlix_radius, int_helixes,
    ext_helix_radius and ext_helixes. The helixes are an array of HelixLocations
    that define the helixes which from the threads. If minor_cutoff is 0 then the
    threads will be triangular and the length of the {int|ext}_helixes 3. if
    minor_cutoff > 0 then the threads will be trapezoids with the length of the
    {int|ext}_helixesarrays will be 4.

    You can control the size and spacing of the threads using
    the various using the parameters.
    """

    height: float
    pitch: float
    dia_major: float
    angle_degs: float
    inset: float
    ext_clearance: float
    taper_out_rpos: float
    taper_in_rpos: float
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
        taper_out_rpos: float,
        taper_in_rpos: float,
        major_cutoff: float,
        minor_cutoff: float,
        thread_overlap: float,
    ) -> None:
        """
        :param height: Height including top and bottom inset
        :param pitch: Peek to Peek measurement of the threads in units default is mm
        :param dia_major: Diameter of threads its largest dimension
        :param angle_degs: Angle of the thread profile in degrees
        :param inset: Size to inset the top and bottom of the height of the threads
        :param ext_clearance: Size to reduce the radius (dia_major / 2) of the external threads
        :param taper_out_rpos: is a decimal fraction such that (taper_out_rpos
            * t_range) defines the t value where tapering out from first_t ends.
            A ValueError exception is raised if taper_out_rpos < 0 or > 1 or
            taper_out_rpos > taper_in_rpos.
        :param taper_in_rpos: is a decimal fraction such that (taper_in_rpos
            * t_range) defines the t value where tapering in begins. The tapering
            out ends at t = last_t.
            A ValueError exception is raised if taper_out_rpos < 0 or > 1 or
            taper_out_rpos > taper_in_rpos.
        :param major_cutoff: Size of flat area at major diameter
        :param major_cutoff: Size of flat area at minor diameter
        :param thread_overlap: Size to increase dimensions so threads and core overlap
            and a manifold is created
        """
        # print(
        #     f"ThreadDimensions:+ height={height:.3f} pitch={pitch:.3f} dia_major={dia_major:.3f} angle_degs={angle_degs:.3f}"
        # )
        # print(
        #     f"ThreadDimensions: inset={inset:.3f} ext_clearance={ext_clearance} taper_rpos={taper_rpos:.3f}"
        # )
        # print(
        #     f"ThreadDimensions: major_cutoff={major_cutoff} minor_cutoff={minor_cutoff} thread_overlap={thread_overlap:.3f} "
        # )

        self.height = height
        self.pitch = pitch
        self.dia_major = dia_major
        self.angle_degs = angle_degs
        self.major_cutoff = major_cutoff
        self.minor_cutoff = minor_cutoff
        self.thread_overlap = thread_overlap
        self.inset = inset
        self.taper_out_rpos = taper_out_rpos
        self.taper_in_rpos = taper_in_rpos
        self.ext_clearance = ext_clearance

        angle_radians: float = radians(angle_degs)
        tan_hangle: float = tan(angle_radians / 2)
        sin_hangle: float = sin(angle_radians / 2)
        tip_to_major_cutoff: float = ((pitch - self.major_cutoff) / 2) / tan_hangle
        tip_to_minor_cutoff: float = (self.minor_cutoff / 2) / tan_hangle
        # print(
        #     f"ThreadDimensions: tip_to_major_cutoff={tip_to_major_cutoff:.3f} tip_to_minor_cutoff={tip_to_minor_cutoff:.3f}"
        # )
        int_thread_depth: float = tip_to_major_cutoff - tip_to_minor_cutoff
        print(f"ThreadDimensions: int_thread_depth={int_thread_depth}")

        # Internal threads have helix thread at the dia_major side
        self.int_helix_radius = self.dia_major / 2
        # print(f"self.int_helix_radius={self.int_helix_radius}")

        thread_overlap_vert_adj: float = self.thread_overlap * tan_hangle
        thread_half_height_at_helix_radius: float = (
            (pitch - self.major_cutoff) / 2
        ) + thread_overlap_vert_adj
        thread_half_height_at_opposite_helix_radius: float = self.minor_cutoff / 2
        # print(
        #     f"thh_at_r={thread_half_height_at_helix_radius} thh_at_or={thread_half_height_at_opposite_helix_radius} td={int_thread_depth}"
        # )

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
        # print(f"h={h} ext_vert_adj={ext_vert_adj}")

        # External threads have the helix on the minor side and
        # so we subtract the int_thread_depth and ext_clearance from dia_major/2
        self.ext_helix_radius = (dia_major / 2) - int_thread_depth - ext_clearance
        # print(
        #     f"self.ext_helix_radius={self.ext_helix_radius} td={int_thread_depth} ec={self.ext_clearance}"
        # )

        ext_thread_half_height_at_ext_helix_radius: float = (
            ((pitch - self.minor_cutoff) / 2) - ext_vert_adj
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
            self.major_cutoff / 2
        ) - ext_vert_adj
        ext_thread_depth: float = int_thread_depth
        if ext_thread_half_height_at_opposite_ext_helix_radius < 0:
            ext_thread_half_height_at_opposite_ext_helix_radius = 0
            ext_thread_depth = ext_thread_half_height_at_ext_helix_radius / tan_hangle

        # print(
        #     f"ext_thread_depth={ext_thread_depth} ext_thh_at_ehr={ext_thread_half_height_at_ext_helix_radius} ext_thh_at_ehr_plus_tovo={ext_thread_half_height_at_ext_helix_radius_plus_tova} ext_thh_at_oehr={ext_thread_half_height_at_opposite_ext_helix_radius}"
        # )

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
        if ext_thread_half_height_at_opposite_ext_helix_radius > 0:
            self.ext_helixes.append(
                HelixLocation(
                    radius=self.ext_helix_radius,
                    horz_offset=ext_thread_depth,
                    vert_offset=-ext_thread_half_height_at_opposite_ext_helix_radius,
                )
            )
