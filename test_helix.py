#!/usr/bin/env python3
from math import isclose
from typing import Tuple

import pytest

from helix import helix

# Default abs_tol
defaultAt = 1e-6


def iscloseTuple(
    v1: Tuple[float, ...],
    v2: Tuple[float, ...],
    rel_tol: float = 1e-9,
    abs_tol: float = defaultAt,
) -> bool:
    # print(f"iscloseTuple: v1={v1} v2={v2}")
    return all(
        [isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol) for a, b in zip(v1, v2)]
    )


def test_all_0():
    f = helix(
        radius=0, pitch=0, height=0, threadDepth=0, threadHalfHeight=0, inset=0, frac=0,
    )
    assert iscloseTuple(f(-100), (0, 0, 0))
    assert iscloseTuple(f(-1), (0, 0, 0))
    assert iscloseTuple(f(0), (0, 0, 0))
    assert iscloseTuple(f(0.5), (0, 0, 0))
    assert iscloseTuple(f(1), (0, 0, 0))
    assert iscloseTuple(f(100), (0, 0, 0))


def test_radius_0():
    f = helix(
        radius=0,
        pitch=1,
        height=1,
        threadDepth=1,
        threadHalfHeight=1,
        inset=0.1,
        frac=0.1,
    )
    assert iscloseTuple(f(-100), (0, 0, -79.9))
    assert iscloseTuple(f(-1), (0, 0, -0.7))
    assert iscloseTuple(f(0), (0, 0, 0.1))
    assert iscloseTuple(f(0.5), (-0.587785, -0.809017, 1.5))
    assert iscloseTuple(f(1), (0, 0, 0.9))
    assert iscloseTuple(f(100), (0, 0, 80.1))


def test_pitch_0():
    f = helix(
        radius=1,
        pitch=0,
        height=1,
        threadDepth=1,
        threadHalfHeight=1,
        inset=0.1,
        frac=0.1,
    )
    assert iscloseTuple(f(-100), (0, 0, 0))
    assert iscloseTuple(f(-1), (0, 0, 0))
    assert iscloseTuple(f(0), (0, 0, 0))
    assert iscloseTuple(f(0.5), (0, 0, 0))
    assert iscloseTuple(f(1), (0, 0, 0))
    assert iscloseTuple(f(100), (0, 0, 0))


def test_height_0():
    f = helix(
        radius=1,
        pitch=1,
        height=0,
        threadDepth=1,
        threadHalfHeight=1,
        inset=0.1,
        frac=0.1,
    )
    assert iscloseTuple(f(-100), (0, 0, 0))
    assert iscloseTuple(f(-1), (0, 0, 0))
    assert iscloseTuple(f(0), (0, 0, 0))
    assert iscloseTuple(f(0.5), (0, 0, 0))
    assert iscloseTuple(f(1), (0, 0, 0))
    assert iscloseTuple(f(100), (0, 0, 0))


def test_threadDepth_0():
    f = helix(
        radius=1,
        pitch=1,
        height=1,
        threadDepth=0,
        threadHalfHeight=1,
        inset=0.1,
        frac=0.1,
    )
    assert iscloseTuple(f(-100), (0, 1, -79.9))
    assert iscloseTuple(f(-1), (-0.951057, 0.309017, -0.7))
    assert iscloseTuple(f(0), (0, 1, 0.1))
    assert iscloseTuple(f(0.5), (-0.5877853, -0.809017, 1.5))
    assert iscloseTuple(f(1), (0.951057, 0.309017, 0.9))
    assert iscloseTuple(f(100), (0, 1, 80.1))


def test_threadHalfHeight_0():
    f = helix(
        radius=1,
        pitch=1,
        height=1,
        threadDepth=1,
        threadHalfHeight=0,
        inset=0.1,
        frac=0.1,
    )
    assert iscloseTuple(f(-100), (0, 1, -79.9))
    assert iscloseTuple(f(-1), (-0.951057, 0.309017, -0.7))
    assert iscloseTuple(f(0), (0, 1, 0.1))
    assert iscloseTuple(f(0.5), (-1.175571, -1.618034, 0.5))
    assert iscloseTuple(f(1), (0.951057, 0.309017, 0.9))
    assert iscloseTuple(f(100), (0, 1, 80.1))


def test_inset_0():
    f = helix(
        radius=1,
        pitch=1,
        height=1,
        threadDepth=1,
        threadHalfHeight=1,
        inset=0,
        frac=0.1,
    )
    assert iscloseTuple(f(-100), (0, 1, -99.99999999))
    assert iscloseTuple(f(-1), (0, 0.9999999, -1))
    assert iscloseTuple(f(0), (0, 1, 0))
    assert iscloseTuple(f(0.5), (0, -2, 1.5))
    assert iscloseTuple(f(1), (0, 1, 1))
    assert iscloseTuple(f(100), (0, 1, 100))


def test_frac_0():
    f = helix(
        radius=1,
        pitch=1,
        height=1,
        threadDepth=1,
        threadHalfHeight=1,
        inset=0.1,
        frac=0,
    )
    assert iscloseTuple(f(-100), (0, 2, -78.9))
    assert iscloseTuple(f(-1), (-1.9021130, 0.618033988, 0.3))
    assert iscloseTuple(f(0), (0, 2, 1.1))
    assert iscloseTuple(f(0.5), (-1.1755705, -1.61803398, 1.5))
    assert iscloseTuple(f(1), (1.902113, 0.618033988, 1.9))
    assert iscloseTuple(f(100), (0, 2, 81.1))


def main():
    # For debugging, use `make t` or `pytest` to actually run the tests
    test_all_0()
    test_radius_0()
    test_pitch_0()
    test_height_0()
    test_threadDepth_0()
    test_threadHalfHeight_0()
    test_inset_0()
    test_frac_0()


if __name__ == "__main__":
    main()
