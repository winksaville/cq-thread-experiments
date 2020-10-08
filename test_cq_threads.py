#!/usr/bin/env python3
# TODO: What to do about negative parameters such as ext_clearance and thread_overlap?
import sys
from math import isclose
from typing import Tuple, cast

import cadquery as cq
import pytest
from helical_thread import HelicalThread, ThreadHelixes, helical_thread

from utils import (
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
major_cutoff = pitch / 8
minor_cutoff = pitch / 4
thread_overlap = 0  # 1e-3
inset = 0  # pitch / 3
taper_in_rpos = 0.1
taper_out_rpos = 0.9
ext_clearance = 0  # 0.05

height = 4 + (2 * inset)


def isclose_or_gt(v1, v2, abs_tol=1e-9) -> bool:
    """v1 is close to or greater than v2"""
    return isclose(v1, v2, abs_tol=abs_tol) or (v1 > v2)


@pytest.mark.parametrize(
    "major_cutoff,minor_cutoff,ext_clearance,thread_overlap",
    [
        (0, 0, 0, 0),
        (0, 0, 0, 0.001),
        (0, 0, 0.05, 0),
        (0, 0, 0.05, 0.001),
        (0, pitch / 4, 0, 0),
        (0, pitch / 4, 0, 0.001),
        (0, pitch / 4, 0.05, 0),
        (0, pitch / 4, 0.05, 0.001),
        (pitch / 8, 0, 0, 0),
        (pitch / 8, 0, 0, 0.001),
        (pitch / 8, 0, 0.05, 0),
        (pitch / 8, 0, 0.05, 0.001),
        (pitch / 8, pitch / 4, 0, 0),
        (pitch / 8, pitch / 4, 0, 0.001),
        (pitch / 8, pitch / 4, 0.05, 0),
        (pitch / 8, pitch / 4, 0.05, 0.001),
    ],
)
def test_ext_clearance(
    major_cutoff, minor_cutoff, ext_clearance, thread_overlap
) -> None:

    ht = HelicalThread(
        height=height,
        pitch=pitch,
        radius=radius,
        angle_degs=angle_degs,
        major_cutoff=major_cutoff,
        minor_cutoff=minor_cutoff,
        thread_overlap=thread_overlap,
        inset_offset=inset,
        taper_in_rpos=taper_in_rpos,
        taper_out_rpos=taper_out_rpos,
        ext_clearance=ext_clearance,
    )
    ths: ThreadHelixes = helical_thread(ht)
    print(f"ths={vars(ths)}")

    # Compute the points of the internal thread helixes
    intpts = []
    x: float
    y: float
    for hl in ths.int_helixes:
        # print(f"tloop: hl={hl}")
        x = hl.radius + hl.horz_offset
        y = hl.vert_offset
        intpts.append((x, y))
    #print(f"intpts={inttpts}")

    # Compute the points of the external thread helixes
    extpts = []
    for hl in ths.ext_helixes:
        # print(f"tloop: hl={hl} x={x} y={y}")
        x = hl.radius + hl.horz_offset
        y = hl.vert_offset
        # Add pitch / 2 to Y so this is next to internal helix
        extpts.append((x, y + (ths.ht.pitch / 2)))
    #print(f"extpts={extpts}")

    # Generate a third set of points which is the next internal set
    # So we can look at cleareances on both sides of every pair
    nxipts = [(x, y + ths.ht.pitch) for x, y in intpts]

    # We will do 2 sets of internal/external pairs so we can
    # validate the perpendicular distances of all edges.
    for i in range(0, 2):

        print(f"intpts={intpts}")
        print(f"extpts={extpts}")
        print(f"nxipts={nxipts}")
        print(f"{i}  ht.thread_overlap={ht.thread_overlap}")

        show(cq.Workplane("XZ").polyline(intpts).close(), f"int{i}")
        show(cq.Workplane("XZ").polyline(extpts).close(), f"ext{i}")

        # extN is the N'th entry in the external point array
        # intN is the N'th entry in the internal point array
        # nxi  is the NeXt Interal points

        # Compute "actual" clearances
        # extL/intL is the last point in the associated array
        # _slope is the distance from the sloped line to nearest points
        # _major is the distance from the major_cutoff to the nearest points
        # _minor is the distance from the minor_cutoff to the nearest points
        print(f"{i} ext_clearance={ext_clearance:.10f}")
        ext0_slope = perpendicular_distance_pt_to_line_2d(
            extpts[0], intpts[1], intpts[2]
        )
        print(f"{i}  ext0_slope={ext0_slope:.10f} {extpts[0]} {intpts[1]} {intpts[2]}")
        assert isclose(ext0_slope, ext_clearance, abs_tol=1e-9)

        # Display a circle at each ext thread vertix so we see it
        for j, (x, y) in enumerate(extpts):
            show(cq.Workplane("XZ", origin=(x, 0, y)).circle(0.01), f"e{j}{i}")

        dist_extL_to_slope = perpendicular_distance_pt_to_line_2d(
            extpts[-1], intpts[1], intpts[2]
        )
        print(f"{i}  dist_extL_to_slope={dist_extL_to_slope:.10f} {extpts[-1]} {intpts[1]} {intpts[2]}")
        assert isclose(dist_extL_to_slope, ext_clearance, abs_tol=1e-9)

        dist_ext2_to_major = perpendicular_distance_pt_to_line_2d(
            extpts[2], intpts[0], intpts[1]
        )
        print(f"{i}  dist_ext2_to_major={dist_ext2_to_major:.10f} {extpts[2]} {intpts[0]} {intpts[1]}")
        assert isclose_or_gt(
            dist_ext2_to_major, ext_clearance + ht.thread_overlap, abs_tol=1e-9
        )

        dist_extL_to_major = perpendicular_distance_pt_to_line_2d(
            extpts[-1], intpts[0], intpts[1]
        )
        print(f"{i}  dist_extL_to_major={dist_extL_to_major:.10f} {extpts[-1]} {intpts[0]} {intpts[1]}")
        assert isclose_or_gt(
            dist_ext2_to_major, ext_clearance + ht.thread_overlap, abs_tol=1e-9
        )

        dist_int2_to_minor = perpendicular_distance_pt_to_line_2d(
            intpts[2], extpts[0], extpts[1]
        )
        print(f"{i}  dist_int2_to_minor={dist_int2_to_minor:.10f} {intpts[2]} {extpts[0]} {extpts[1]}")
        assert isclose(dist_int2_to_minor, ext_clearance + ht.thread_overlap, abs_tol=1e-9)

        dist_intL_to_minor = perpendicular_distance_pt_to_line_2d(
            intpts[-1], extpts[0], extpts[1]
        )
        print(f"{i}  dist_intL_to_minor={dist_intL_to_minor:.10f} {intpts[-1]} {extpts[0]} {extpts[1]}")
        assert isclose(dist_intL_to_minor, ext_clearance + ht.thread_overlap, abs_tol=1e-9)

        dist_ext1_to_slope = perpendicular_distance_pt_to_line_2d(
            extpts[1], nxipts[0], nxipts[-1]
        )
        print(f"{i}  dist_ext1_to_slope={dist_ext1_to_slope:.10f} {extpts[1]} {nxipts[0]} {nxipts[-1]}")
        assert isclose(dist_ext1_to_slope, ext_clearance, abs_tol=1e-9)

        dist_ext2_to_slope = perpendicular_distance_pt_to_line_2d(
            extpts[2], nxipts[0], nxipts[-1]
        )
        print(f"{i}  dist_ext2_to_slope={dist_ext2_to_slope:.10f} {extpts[2]} {nxipts[0]} {nxipts[-1]}")
        assert isclose(dist_ext2_to_slope, ext_clearance, abs_tol=1e-9)

        # The current nxipts become intpts then compute new extpts and nxipts
        intpts = nxipts
        extpts = [(x, y + pitch) for x, y in extpts]
        nxipts = [(x, y + pitch) for x, y in nxipts]


if __name__ == "__main__" or "cq_editor" in sys.modules:
    test_ext_clearance(0, 0, 0, 0)
    test_ext_clearance(0, 0, 0, 0.001)
    test_ext_clearance(0, 0, 0.05, 0)
    test_ext_clearance(0, 0, 0.05, 0.001)

    test_ext_clearance(0, pitch / 4, 0, 0)
    test_ext_clearance(0, pitch / 4, 0, 0.001)
    test_ext_clearance(0, pitch / 4, 0.05, 0)
    test_ext_clearance(0, pitch / 4, 0.05, 0.001)

    test_ext_clearance(pitch / 8, 0, 0, 0)
    test_ext_clearance(pitch / 8, 0, 0, 0.001)
    test_ext_clearance(pitch / 8, 0, 0.05, 0)
    test_ext_clearance(pitch / 8, 0, 0.05, 0.001)

    test_ext_clearance(pitch / 8, pitch / 4, 0, 0)
    test_ext_clearance(pitch / 8, pitch / 4, 0, 0.001)
    test_ext_clearance(pitch / 8, pitch / 4, 0.05, 0)
    test_ext_clearance(pitch / 8, pitch / 4, 0.05, 0.001)
