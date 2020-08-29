#!/usr/bin/env python3
from math import isclose
from typing import Tuple

import pytest

from convergingHelix import convergingHelix as cHelix

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
    f = cHelix(
        radius=0,
        pitch=0,
        height=1,
        inset=0,
        cvrgFactor=0,
        horzOffset=0,
        vertOffset=0,
        firstT=0,
        lastT=0,
    )
    assert iscloseTuple(f(-100), (0, 0, 0))
    assert iscloseTuple(f(-1), (0, 0, 0))
    assert iscloseTuple(f(0), (0, 0, 0))
    assert iscloseTuple(f(0.5), (0, 0, 0))
    assert iscloseTuple(f(1), (0, 0, 0))
    assert iscloseTuple(f(100), (0, 0, 0))


def test_radius_0():
    f = cHelix(
        radius=0,
        pitch=1,
        height=1,
        inset=0.1,
        cvrgFactor=20,
        horzOffset=1,
        vertOffset=1,
        firstT=-100,
        lastT=100,
    )
    assert iscloseTuple(f(-100), (0, -1, -80.9))
    assert iscloseTuple(f(-1), (0.07461903, -0.02424519, -0.778459095))
    assert iscloseTuple(f(0), (0, 0, 0.1))
    assert iscloseTuple(f(0.5), (-0.023076346, -0.0317618581, 0.539259815))
    assert iscloseTuple(f(1), (0.07461903, 0.02424519, 0.978459095))
    assert iscloseTuple(f(100), (0, 0, 80.1))


def test_pitch_0():
    f = cHelix(
        radius=1,
        pitch=0,
        height=1,
        inset=0.1,
        cvrgFactor=20,
        horzOffset=1,
        vertOffset=1,
        firstT=-100,
        lastT=100,
    )
    assert iscloseTuple(f(-100), (0, 0, 0))
    assert iscloseTuple(f(-1), (0, 0, 0))
    assert iscloseTuple(f(0), (0, 0, 0))
    assert iscloseTuple(f(0.5), (0, 0, 0))
    assert iscloseTuple(f(1), (0, 0, 0))
    assert iscloseTuple(f(100), (0, 0, 0))


def test_height_0():
    f = cHelix(
        radius=1,
        pitch=1,
        height=0,
        inset=0.1,
        cvrgFactor=20,
        horzOffset=1,
        vertOffset=1,
        firstT=-100,
        lastT=100,
    )
    assert iscloseTuple(f(-100), (0, 0, 19.1))
    assert iscloseTuple(f(-1), (-0.8764374820, 0.2847718004, 0.221540904))
    assert iscloseTuple(f(0), (0, 1, 0.1))
    assert iscloseTuple(f(0.5), (0.610861593, 0.84077885252, 0.0392598157))
    assert iscloseTuple(f(1), (1.0256755505, 0.3332621883, -0.021540904))
    assert iscloseTuple(f(100), (0, 1, -19.9))


def test_horzOffset_0():
    f = cHelix(
        radius=1,
        pitch=1,
        height=1,
        inset=0.1,
        cvrgFactor=0.1,
        horzOffset=0,
        vertOffset=1,
        firstT=0,
        lastT=1,
    )
    assert iscloseTuple(f(0), (0, 1, 0.1))
    assert iscloseTuple(f(0.5), (-0.5877853, -0.809017, 1.5))
    assert iscloseTuple(f(1), (0.951057, 0.309017, 0.9))


def test_vertOffset_0():
    f = cHelix(
        radius=1,
        pitch=1,
        height=1,
        inset=0.1,
        cvrgFactor=0.1,
        horzOffset=1,
        vertOffset=0,
        firstT=0,
        lastT=1,
    )
    assert iscloseTuple(f(0), (0, 1, 0.1))
    assert iscloseTuple(f(0.5), (-1.175571, -1.618034, 0.5))
    assert iscloseTuple(f(1), (0.951057, 0.309017, 0.9))


def test_inset_0():
    f = cHelix(
        radius=1,
        pitch=1,
        height=1,
        inset=0,
        cvrgFactor=0.1,
        horzOffset=1,
        vertOffset=1,
        firstT=0,
        lastT=1,
    )
    assert iscloseTuple(f(0), (0, 1, 0))
    assert iscloseTuple(f(0.5), (0, -2, 1.5))
    assert iscloseTuple(f(1), (0, 1, 1))


def test_cvrgFactor_0():
    f = cHelix(
        radius=1,
        pitch=1,
        height=1,
        inset=0.1,
        cvrgFactor=0,
        horzOffset=1,
        vertOffset=1,
        firstT=0,
        lastT=1,
    )
    assert iscloseTuple(f(0), (0, 2, 1.1))
    assert iscloseTuple(f(0.5), (-1.1755705, -1.61803398, 1.5))
    assert iscloseTuple(f(1), (1.902113, 0.618033988, 1.9))


def main():
    # For debugging, use `make t` or `pytest` to actually run the tests
    test_all_0()
    test_radius_0()
    test_pitch_0()
    test_height_0()
    test_inset_0()
    test_cvrgFactor_0()
    test_horzOffset_0()
    test_vertOffset_0()


if __name__ == "__main__":
    main()
