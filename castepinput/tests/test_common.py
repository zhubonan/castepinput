"""
Tests for the common module
"""

from __future__ import absolute_import
import numpy as np
import castepinput.common as common
import pytest


def test_block():
    b = common.Block(["1 1 1", "2 2 3 ", ""])
    expect = ["1 1 1", "2 2 3"]
    c = b.compact()
    assert c == expect
    assert b != expect

    b.compact(inplace=True)
    assert b == expect


def test_abc_to_cell():

    abc = [1, 1, 1, 90.0, 90.0, 90.0]
    cell = common.cell_abcs_to_vec(abc)
    assert np.all(cell == np.identity(3))

    # Check a differnt cell
    abc = [1, 1, 1, 60.0, 60.0, 60.0]
    cell = common.cell_abcs_to_vec(abc)
    for v in cell:
        assert np.dot(v, v) == 1

    # Check angles
    va, vb, vc = cell

    def get_ang(a, b):
        cos_alpha = (a.dot(b)) / (np.sqrt(a.dot(a)) * np.sqrt(b.dot(b)))
        return np.arccos(cos_alpha)

    assert get_ang(va, vb) == np.pi / 3
    assert get_ang(vc, vb) == np.pi / 3
    assert get_ang(va, vc) == np.pi / 3
