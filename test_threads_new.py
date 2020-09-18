# TODO: top slope of external thread is not parallel to bottom slope of internal thread
# TODO: Shouldn't need the "compensation" code except for thread_overlap
# TODO: What to do about negative parameters such as ext_clearance and thread_overlap?
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
external_threads = False
major_pd = 8
minor_pd = 4
thread_overlap = 0 #1e-3
inset = 0 #pitch / 3
taper_rpos = 0.1
ext_clearance = 0 #0.05

height = 4 + (2 * inset)

@pytest.mark.parametrize(
    "major_pd,minor_pd,ext_clearance,thread_overlap",
    [
        # (8, 4, 0, 0),
        # (0, 4, 0, 0),
        # (4, 0, 0, 0),
        # (0, 0, 0, 0),
        # (8, 4, 0.05, 0),
        # (0, 4, 0.05, 0),
        # (4, 0, 0.05, 0),
        # (0, 0, 0.05, 0),
    ]
)
def test_ext_clearance(major_pd, minor_pd, ext_clearance, thread_overlap) -> None:

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
    intpts = []
    x: float
    y: float
    for hl in thread_dims.helixes:
        # print(f"tloop: hl={hl}")
        if False:
            # TODO: This should work, compensation should be handled else where
            x = hl.radius + hl.horz_offset
            y = hl.vert_offset
        else:
            # Adjust vert_offset by thread_overlap_vert_adj to pretend
            # we've overlaped the threads with the bolt core when
            # hl.radius is the "base" radius (i.e. thread_dims.helix_helix_raduis)
            x = hl.radius + hl.horz_offset - thread_dims.thread_overlap
            y = hl.vert_offset
            # print(f"current   Y: y={y}")
            if thread_dims.thread_overlap > 0 and hl.horz_offset == 0:
                # print("hl.horz_offset == 0")
                if y > 0:
                    y -= thread_dims.thread_overlap_vert_adj
                    # print(f"y > 0: y={y}")
                else:
                    y += thread_dims.thread_overlap_vert_adj
                    # print(f"y <= 0: y={y}")
            # print(f"corrected Y: y={y}")
        intpts.append((x, y))

    # Compute the points of the external thread helixes
    extpts = []
    for hl in thread_dims.ext_helixes:
        # print(f"tloop: hl={hl} x={x} y={y}")
        if False:
            # TODO: This should work, compensation should be handled else where
            x = hl.radius + hl.horz_offset
            y = hl.vert_offset
        else:
            # Adjust vert_offset by thread_overlap_vert_adj to pretend
            # we've overlaped the threads with the bolt core when
            # hl.radius is the "base" radius (i.e. thread_dims.ext_helix_helix_raduis)
            x = hl.radius + hl.horz_offset + thread_dims.thread_overlap
            y = hl.vert_offset
            # print(f"current   Y: y={y}")
            if thread_dims.thread_overlap > 0 and hl.horz_offset == 0:
                # print("hl.horz_offset == 0")
                if y < 0:
                    y += thread_dims.thread_overlap_vert_adj
                    # print(f"y < 0: y={y}")
                else:
                    y -= thread_dims.thread_overlap_vert_adj
                    # print(f"y >= 0: y={y}")
            # print(f"corrected Y: y={y}")
        extpts.append((x, y + (pitch / 2)))
        #extpts.append((x, y))
    print(f"extpts={extpts}")

    # exttrap = cq.Workplane("XZ").polyline(extpts).close()
    # show(exttrap, "exttrap")

    # Generate a third set of points which is the next internal set
    # So we can look at cleareances on both sides of ever pair
    nxipts = [(x, y + pitch) for x, y in intpts]

    first_idx: int = 0
    last_idx: int = 4
    for i in range(first_idx, last_idx+1):
        show(cq.Workplane("XZ").polyline(intpts).close(), f"int{i}")
        show(cq.Workplane("XZ").polyline(extpts).close(), f"ext{i}")

        print(f"intpts={intpts}")
        print(f"extpts={extpts}")
        print(f"nxipts={nxipts}")

        # extN is the N'th entry in the external point array
        # intN is the N'th entry in the internal point array
        # nxi  is the NeXt Interal points

        # Compute "actual" clearances
        # extL/intL is the last point in the associated array
        # _slope is the distance from the sloped line to nearest points
        # _major is the distance from the major_cutoff to the nearest points
        # _minor is the distance from the minor_cutoff to the nearest points
        print(f"{i} ext_clearance={ext_clearance:.10f}")
        ext0_slope = perpendicular_distance_pt_to_line_2d(extpts[0], intpts[1], intpts[2])
        print(f"{i}  ext0_slope={ext0_slope:.10f} {extpts[0]} {intpts[1]} {intpts[2]}")
        # assert isclose(ext0_slope, ext_clearance, abs_tol=1e-9)

        extL_slope = perpendicular_distance_pt_to_line_2d(extpts[-1], intpts[1], intpts[2])
        print(f"{i}  extL_slope={extL_slope:.10f} {extpts[-1]} {intpts[1]} {intpts[2]}")
        # assert isclose(extL_slope, ext_clearance, abs_tol=1e-9)

        ext2_major = perpendicular_distance_pt_to_line_2d(extpts[2], intpts[0], intpts[1])
        print(f"{i}  ext2_major={ext2_major:.10f} {extpts[2]} {intpts[0]} {intpts[1]}")
        # assert isclose(ext2_major, ext_clearance, abs_tol=1e-9)

        extL_major = perpendicular_distance_pt_to_line_2d(extpts[-1], intpts[0], intpts[1])
        print(f"{i}  extL_major={extL_major:.10f} {extpts[-1]} {intpts[0]} {intpts[1]}")
        # assert isclose(extL_major, ext_clearance, abs_tol=1e-9)

        int2_minor = perpendicular_distance_pt_to_line_2d(intpts[2], extpts[0], extpts[1])
        print(f"{i}  int2_minor={int2_minor:.10f} {intpts[2]} {extpts[0]} {extpts[1]}")
        # assert isclose(int2_minor, ext_clearance, abs_tol=1e-9)

        intL_minor = perpendicular_distance_pt_to_line_2d(intpts[-1], extpts[0], extpts[1])
        print(f"{i}  intL_minor={intL_minor:.10f} {intpts[-1]} {extpts[0]} {extpts[1]}")
        # assert isclose(intL_minor, ext_clearance, abs_tol=1e-9)

        ext1_slope = perpendicular_distance_pt_to_line_2d(extpts[1], nxipts[0], nxipts[-1])
        print(f"{i}  ext1_slope={ext1_slope:.10f} {extpts[1]} {nxipts[0]} {nxipts[-1]}")
        # assert isclose(ext1_slope, ext_clearance, abs_tol=1e-9)

        ext2_slope = perpendicular_distance_pt_to_line_2d(extpts[2], nxipts[0], nxipts[-1])
        print(f"{i}  ext2_slope={ext2_slope:.10f} {extpts[2]} {nxipts[0]} {nxipts[-1]}")
        # assert isclose(ext2_slope, ext_clearance, abs_tol=1e-9)

        # Copy the current nxipts and then compute new extpts and nxipts
        intpts = nxipts.copy()
        extpts = [(x, y + pitch) for x, y in extpts]
        nxipts = [(x, y + pitch) for x, y in nxipts]

        # The asserts together so they can manually be easily enabled/disabled
        assert isclose(ext0_slope, ext_clearance, abs_tol=1e-9)
        assert isclose(extL_slope, ext_clearance, abs_tol=1e-9)
        assert isclose(ext2_major, ext_clearance, abs_tol=1e-9)
        assert isclose(extL_major, ext_clearance, abs_tol=1e-9)
        assert isclose(int2_minor, ext_clearance, abs_tol=1e-9)
        assert isclose(intL_minor, ext_clearance, abs_tol=1e-9)
        assert isclose(ext1_slope, ext_clearance, abs_tol=1e-9)
        assert isclose(ext2_slope, ext_clearance, abs_tol=1e-9)

if __name__ == "__main__" or "show_object" in globals():
    # OK:
    test_ext_clearance(0, 0, 0, 0) # int_helixes == tri ext_helixes == tri
    #test_ext_clearance(0, 0, 0, 0.001) # int_helixes == tri ext_helixes == tri
    #test_ext_clearance(0, 0, 0.05, 0) # int_helixes == tri ext_helixes == tri
    #test_ext_clearance(0, 0, 0.05, 0.001) # int_helixes == tri ext_helixes == tri

    test_ext_clearance(0, 4, 0, 0) # int_helixes == trap ext_helixes == trap
    #test_ext_clearance(0, 4, 0, 0.001) # int_helixes == trap ext_helixes == trap
    #test_ext_clearance(0, 4, 0.05, 0) # int_helixes == trap ext_helixes == trap
    #test_ext_clearance(0, 4, 0.05, 0.001) # int_helixes == trap ext_helixes == trap

    test_ext_clearance(8, 0, 0, 0) # int_helixes == trap ext_helixes == trap
    #test_ext_clearance(8, 0, 0, 0.001) # int_helixes == trap ext_helixes == trap
    #test_ext_clearance(8, 0, 0.05, 0) # int_helixes == trap ext_helixes == trap
    #test_ext_clearance(8, 0, 0.05, 0.001) # int_helixes == trap ext_helixes == trap

    test_ext_clearance(8, 4, 0, 0) # int_helixes == trap ext_helixes == trap
    #test_ext_clearance(8, 4, 0, 0.001) # int_helixes == trap ext_helixes == trap
    #test_ext_clearance(8, 4, 0.05, 0) # int_helixes == trap ext_helixes == trap
    #test_ext_clearance(8, 4, 0.05, 0.001) # int_helixes == trap ext_helixes == trap

