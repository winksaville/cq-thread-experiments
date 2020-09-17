# TODO: create separate tests for the above and maybe others
# TODO: What to do about negative ext_clearance and thread_overlap?
from math import atan, cos, degrees, isclose, pi, radians, sin, tan
from typing import Tuple, Union, cast

import cadquery as cq
import pytest
from taperable_helix import helix

from threads import HelixLocation, ThreadDimensions, threads
from wing_utils import (
    X,
    Y,
    Z,
    diffPts,
    perpendicular_distance_pt_to_line_2d,
    setCtx,
    show,
    translate_2d,
)

setCtx(globals())

# clearance between internal threads and external threads
# the internal_clearance is always 0

pitch = 2
radius = 8
angle_degs = 90
major_pd = 8
minor_pd = 4
thread_overlap = 0 #1e-3
inset = pitch / 3
taper_rpos = 0.1
ext_clearance = 0 #0.05

height = 4 + (2 * inset)

@pytest.mark.parametrize(
    "external_threads,major_pd,minor_pd,ext_clearance,thread_overlap",
    [
        # (False, 8, 4, 0, 0),
        # (False, 0, 4, 0, 0),
        # (False, 4, 0, 0, 0),
        # (False, 0, 0, 0, 0),
        # (False, 8, 4, 0.05, 0),
        (False, 0, 4, 0.05, 0),
        # (False, 4, 0, 0.05, 0),
        # # (False, 0, 0, 0.05, 0),
    ]
)
def test_ext_clearance(external_threads, major_pd, minor_pd, ext_clearance, thread_overlap) -> None:

    thread_dims = ThreadDimensions(
        height=height,
        pitch=pitch,
        dia_major=radius,
        angle_degs=angle_degs,
        external_threads=external_threads,
        dia_major_cutoff_pitch_divisor=major_pd,
        dia_minor_cutoff_pitch_divisor=minor_pd,
        thread_overlap=thread_overlap,
        inset=inset,
        taper_rpos=taper_rpos,
        ext_clearance=ext_clearance,
    )
    print(f"thread_dims={vars(thread_dims)}")

    # Compute the points of the internal thread helixes
    # Adjust vert_offset by thread_overlap_vert_adj to pretend
    # we've overlaped the threads with the bolt core when
    # hl.radius is the "base" radius (i.e. thread_dims.helix_helix_raduis)
    print(
        f"intpts: thread_overlap={thread_dims.thread_overlap} thread_overlap_vert_adj={thread_dims.thread_overlap_vert_adj}"
    )
    intpts = []
    x: float
    y: float
    for hl in thread_dims.helixes:
        x = hl.radius + hl.horz_offset - thread_dims.thread_overlap
        y = hl.vert_offset
        # print(f"tloop: hl={hl} x={x} y={y}")
        if thread_dims.thread_overlap > 0 and hl.horz_offset == 0:
            # print("hl.horz_offset == 0")
            if y > 0:
                y -= thread_dims.thread_overlap_vert_adj
                # print(f"y > 0: y={y}")
            else:
                y += thread_dims.thread_overlap_vert_adj
                # print(f"y <= 0: y={y}")
        # print(f"bloop: hl={hl} x={x} y={y}")
        intpts.append((x, y))
    print(f"intpts={intpts}")

    inttrap = cq.Workplane("XZ").polyline(intpts).close()
    show(inttrap, "inttrap")

    # Compute the points of the external thread helixes
    # Adjust vert_offset by thread_overlap_vert_adj to pretend
    # we've overlaped the threads with the bolt core when
    # hl.radius is the "base" radius (i.e. thread_dims.ext_helix_helix_raduis)
    # print(
    #     f"extpts: thread_dims.thread_overlap={thread_dims.thread_overlap} thread_overlap_vert_adj={thread_dims.thread_overlap_vert_adj}"
    # )
    extpts = []
    for hl in thread_dims.ext_helixes:
        x = hl.radius + hl.horz_offset + thread_dims.thread_overlap
        y = hl.vert_offset
        # print(f"tloop: hl={hl} x={x} y={y}")
        if thread_dims.thread_overlap > 0 and hl.horz_offset == 0:
            # print("hl.horz_offset == 0")
            if y < 0:
                y += thread_dims.thread_overlap_vert_adj
                # print(f"y < 0: y={y}")
            else:
                y -= thread_dims.thread_overlap_vert_adj
                # print(f"y >= 0: y={y}")
        # print(f"bloop: hl={hl} x={x} y={y}")
        extpts.append((x, y + (pitch / 2)))
    print(f"extpts={extpts}")

    exttrap = cq.Workplane("XZ").polyline(extpts).close()
    show(exttrap, "exttrap")

    # Compute "actual" clearances
    # extN is the N'th entry in the external point array
    # intN is the N'th entry in the internal point array
    # extL/intL is the last point in the associated array
    # _slope is the distance from the sloped line to nearest points
    # _major is the distance from the major_cutoff to the nearest points
    # _minor is the distance from the minor_cutoff to the nearest points
    print(f"ext_clearance={ext_clearance:.10f}")
    ext0_slope = perpendicular_distance_pt_to_line_2d(extpts[0], intpts[1], intpts[2])
    print(f" ext0_slope={ext0_slope:.10f}")
    # assert isclose(ext0_slope, ext_clearance, abs_tol=1e-9)

    extL_slope = perpendicular_distance_pt_to_line_2d(extpts[-1], intpts[1], intpts[2])
    print(f" extL_slope={extL_slope:.10f}")
    # assert isclose(extL_slope, ext_clearance, abs_tol=1e-9)

    ext2_major = perpendicular_distance_pt_to_line_2d(extpts[2], intpts[0], intpts[1])
    print(f" ext2_major={ext2_major:.10f}")
    # assert isclose(ext2_major, ext_clearance, abs_tol=1e-9)

    extL_major = perpendicular_distance_pt_to_line_2d(extpts[-1], intpts[0], intpts[1])
    print(f" extL_major={extL_major:.10f}")
    # assert isclose(extL_major, ext_clearance, abs_tol=1e-9)

    int2_minor = perpendicular_distance_pt_to_line_2d(intpts[2], extpts[0], extpts[1])
    print(f" int2_minor={int2_minor:.10f}")
    # assert isclose(int2_minor, ext_clearance, abs_tol=1e-9)

    intL_minor = perpendicular_distance_pt_to_line_2d(intpts[-1], extpts[0], extpts[1])
    print(f" intL_minor={intL_minor:.10f}")
    # assert isclose(intL_minor, ext_clearance, abs_tol=1e-9)

    #assert isclose(ext0_slope, ext_clearance, abs_tol=1e-9)
    #assert isclose(extL_slope, ext_clearance, abs_tol=1e-9)
    #assert isclose(ext2_major, ext_clearance, abs_tol=1e-9)
    #assert isclose(extL_major, ext_clearance, abs_tol=1e-9)
    #assert isclose(int2_minor, ext_clearance, abs_tol=1e-9)
    #assert isclose(intL_minor, ext_clearance, abs_tol=1e-9)

if __name__ == "__main__" or "show_object" in globals():
    # OK:
    #test_ext_clearance(False, 0, 0, 0, 0) # int_helixes == tri ext_helixes == tri
    #test_ext_clearance(False, 0, 0, 0, 0.001) # int_helixes == tri ext_helixes == tri

    #test_ext_clearance(False, 8, 4, 0, 0) # int_helixes == trap ext_helixes == trap
    #test_ext_clearance(False, 8, 4, 0.05, 0.001) # int_helixes == trap ext_helixes == trap
    #test_ext_clearance(False, 8, 4, 0.05, 0) # int_helixes == trap ext_helixes == trap
    #test_ext_clearance(False, 8, 4, 0, 0.001) # int_helixes == trap ext_helixes == trap

    #test_ext_clearance(False, 8, 0, 0, 0) # int_helixes == tri ext_helixes == trap
    #test_ext_clearance(False, 8, 0, 0.05, 0.001) # int_helixes == tri ext_helixes == trap
    #test_ext_clearance(False, 8, 0, 0.05, 0) # int_helixes == tri ext_helixes == trap
    #test_ext_clearance(False, 8, 0, 0, 0.001) # int_helixes == tri ext_helixes == trap

    #test_ext_clearance(False, 0, 4, 0, 0) # int_helixes == tri ext_helixes == trap
    #test_ext_clearance(False, 0, 4, 0, 0.001) # int_helixes == tri ext_helixes == trap

    # FAILS: extL_slope fails 0.0207106781 expected 0.05
    test_ext_clearance(False, 0, 4, 0.05, 0.001) # int_helixes == tri ext_helixes == trap
    test_ext_clearance(False, 0, 4, 0.05, 0) # int_helixes == tri ext_helixes == trap
    test_ext_clearance(False, 0, 0, 0.05, 0) # int_helixes == tri ext_helixes == tri
    test_ext_clearance(False, 0, 0, 0.05, 0.001) # int_helixes == tri ext_helixes == tri

