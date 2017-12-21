"""
Tests for the util module
"""

import numpy as np

from unittest import TestCase
import castepinputs.utils as utils


class TestUtils(TestCase):

    def test_abc_to_cell(self):

        abc = [1, 1, 1, 90.0, 90.0, 90.0]
        cell = utils.cell_abcs_to_vec(abc)
        cmp = cell == np.identity(3, dtype=np.float64)
        self.assertTrue(np.all(cmp))

        # Check a differnt cell
        abc = [1, 1, 1, 60.0, 60.0, 60.0]
        cell = utils.cell_abcs_to_vec(abc)
        for v in cell:
            self.assertEqual(np.dot(v, v), 1)

        # Check angles
        va, vb, vc = cell

        def get_ang(a, b):
            cos_alpha = (a.dot(b)) / (np.sqrt(a.dot(a)) * np.sqrt(b.dot(b)))
            return np.arccos(cos_alpha)

        self.assertEqual(get_ang(va, vb), np.pi/3)
        self.assertEqual(get_ang(vc, vb), np.pi/3)
        self.assertEqual(get_ang(va, vc), np.pi/3)
