# TODO: create separate tests for the above and maybe others
# TODO: What to do about negative ext_clearance and thread_overlap?

from math import atan, cos, degrees, isclose, pi, radians, sin, tan
from typing import Tuple, Union, cast

import cadquery as cq
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
ext_clearance = 0.05

# Set to guarantee the thread and core overlap and a manifold is created
thread_overlap = 1e-3

# Tolerance value for generating STL files
stlTolerance = 1e-3

# The separation between edges of a helix after on revolution.
pitch = 2

# The included angle of the "tip" of a thread
angle_degs = 90

# Adjust z by inset so threads are inset from the bottom and top
inset = pitch / 3

nominalMajorDia = 8
nutDiameter = nominalMajorDia
nutHeight = 4 + (2 * inset)

majorPd = 8  # None
minorPd = 4  # None
taper_rpos = 0.1


def test_ext_clearance():

    #     ext_clearance=0.0000000000
    #  ext0_slope=0.0000000000
    # Traceback (most recent call last):
    #   File "test_threads.py", line 157, in <module>
    #     test_ext_clearance()
    #   File "test_threads.py", line 133, in test_ext_clearance
    #     assert isclose(ext0_slope, ext_clearance)
    # AssertionError
    #
    # Above AssertionError with:
    #    ext_clearance = 0
    #    thread_overlap = 0
    #    angle_degs = 30 # AssertionError, why?

    # Local values
    ext_clearance = 0.5
    thread_overlap = 0.001
    angle_degs = 40

    thread_dims = ThreadDimensions(
        height=nutHeight,
        pitch=pitch,
        dia_major=nutDiameter,
        angle_degs=angle_degs,
        external_threads=False,
        dia_major_cutoff_pitch_divisor=majorPd,
        dia_minor_cutoff_pitch_divisor=minorPd,
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
    print(f"intpts: thread_overlap={thread_dims.thread_overlap} thread_overlap_vert_adj={thread_dims.thread_overlap_vert_adj}")
    intpts = []
    for hl in thread_dims.helixes:
        x: float = hl.radius + hl.horz_offset - thread_dims.thread_overlap
        y: float = hl.vert_offset
        print(f"tloop: hl={hl} x={x} y={y}")
        if thread_dims.thread_overlap > 0 and hl.horz_offset == 0:
            print("hl.horz_offset == 0")
            if y > 0:
                y -= thread_dims.thread_overlap_vert_adj
                print(f"y > 0: y={y}")
            else:
                y += thread_dims.thread_overlap_vert_adj
                print(f"y <= 0: y={y}")
        print(f"bloop: hl={hl} x={x} y={y}")
        intpts.append((x, y))
    print(f"intpts={intpts}")

    inttrap = cq.Workplane("XZ").polyline(intpts).close()
    show(inttrap, "inttrap")

    # Compute the points of the external thread helixes
    # Adjust vert_offset by thread_overlap_vert_adj to pretend
    # we've overlaped the threads with the bolt core when
    # hl.radius is the "base" radius (i.e. thread_dims.ext_helix_helix_raduis)
    print(f"extpts: thread_dims.thread_overlap={thread_dims.thread_overlap} thread_overlap_vert_adj={thread_dims.thread_overlap_vert_adj}")
    extpts = []
    for hl in thread_dims.ext_helixes:
        pt: Tuple[float, float]
        x: float = hl.radius + hl.horz_offset + thread_dims.thread_overlap
        y: float = hl.vert_offset
        print(f"tloop: hl={hl} x={x} y={y}")
        if thread_dims.thread_overlap > 0 and hl.horz_offset == 0:
            print("hl.horz_offset == 0")
            if y < 0:
                y += thread_dims.thread_overlap_vert_adj
                print(f"y < 0: y={y}")
            else:
                y -= thread_dims.thread_overlap_vert_adj
                print(f"y >= 0: y={y}")
        print(f"bloop: hl={hl} x={x} y={y}")
        extpts.append((x, y + (pitch / 2)))
    print(f"extpts={extpts}")

    exttrap = cq.Workplane("XZ").polyline(extpts).close()
    show(exttrap, "exttrap")

    # Compute "actual" clearances
    print(f"ext_clearance={ext_clearance:.10f}")
    ext0_slope = perpendicular_distance_pt_to_line_2d(extpts[0], intpts[1], intpts[2])
    print(f" ext0_slope={ext0_slope:.10f}")
    assert isclose(ext0_slope, ext_clearance)

    ext3_slope = perpendicular_distance_pt_to_line_2d(extpts[3], intpts[1], intpts[2])
    print(f" ext3_slope={ext3_slope:.10f}")
    assert isclose(ext3_slope, ext_clearance)

    ext0_major = perpendicular_distance_pt_to_line_2d(extpts[2], intpts[0], intpts[1])
    print(f" ext0_major={ext0_major:.10f}")
    assert isclose(ext0_major, ext_clearance)

    ext1_major = perpendicular_distance_pt_to_line_2d(extpts[3], intpts[0], intpts[1])
    print(f" ext1_major={ext1_major:.10f}")
    assert isclose(ext1_major, ext_clearance)

    ext2_minor = perpendicular_distance_pt_to_line_2d(extpts[0], intpts[2], intpts[3])
    print(f" ext2_minor={ext2_minor:.10f}")
    assert isclose(ext2_minor, ext_clearance)

    ext3_minor = perpendicular_distance_pt_to_line_2d(extpts[1], intpts[2], intpts[3])
    print(f" ext3_minor={ext3_minor:.10f}")
    assert isclose(ext3_minor, ext_clearance)


if __name__ == "__main__" or "show_object" in globals():
    test_ext_clearance()
