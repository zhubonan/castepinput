"""
Utility module
"""
from math import sin, cos, pi, sqrt

import numpy as np


class Block(list):
    """
    Blocks in CASTEP inputs files
    """

    def __repr__(self):
        r = super(Block, self).__repr__()
        return "Block(" + r + ")"


def cell_abcs_to_vec(abcs):
    """
    Convert fractional cell format to vectors.
    The result a vector is along [1, 0, 0] and the normal of a,b plane
    is along [0, 0, 1] direction.

    :param abcs: a list of [a, b, c, alpha, beta, gamma]
    """

    a, b, c, alpha, beta, gamma = abcs

    # In case of orthorhobic cell - avoid rounding errors
    e = 2 * np.spacing(90, dtype=np.float64)

    if abs(abs(alpha) - 90) < e:
        cos_alpha = 0.0
    else:
        cos_alpha = cos(alpha * pi / 180)

    if abs(abs(beta) - 90) < e:
        cos_beta = 0.0
    else:
        cos_beta = cos(alpha * pi / 180)

    if abs(gamma - 90) < e:
        cos_gamma = 0.0
        sin_gamma = 1.0
    elif abs(gamma + 90) < e:
        cos_gamma = 0.0
        sin_gamma = -1.0
    else:
        cos_gamma = cos(gamma * pi / 180)
        sin_gamma = sin(gamma * pi / 180)

    va = a * np.array([1, 0, 0])
    vb = b * np.array([cos_gamma, sin_gamma, 0])
    cx = cos_beta
    cy = (cos_alpha - cos_beta * cos_gamma) / sin_gamma
    cz = sqrt(1. - cx * cx - cy * cy)
    vc = c * np.array([cx, cy, cz])

    cell = np.vstack([va, vb, vc])
    return cell
