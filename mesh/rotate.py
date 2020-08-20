'''
To rotate geometrical objects.
- Initial contribution by Gary Klindt
'''

from scipy.linalg import norm, det
import numpy as np


def rotateVector(vector, alpha, axis, eps=1e-8):
    """
    return a rotated vector by alpha around axis
    """
    vector = np.array(vector)
    axis = np.array(axis)
    if (norm(axis) < eps):
        return vector
    axis = axis / norm(axis)
    rota = rotationMatrix(alpha, axis)
    return np.dot(rota, vector)


def rotationMatrix(alpha, axis, eps=1e-8):
    """
    - return the rotation matrix, given axis and angle
    - not tested with negative angles. Expected a value from [0,pi] (arccos)
     """
    if abs(alpha) < eps:
        return np.diag([1, 1, 1])
    (a, b, c, d) = angleAxis2Quaternion(alpha, axis)
    res = np.zeros((3, 3))
    res[0, 0] = -1 + 2 * a * a + 2 * d * d
    res[1, 1] = -1 + 2 * b * b + 2 * d * d
    res[2, 2] = -1 + 2 * c * c + 2 * d * d
    res[0, 1] = 2 * (a * b - c * d)
    res[0, 2] = 2 * (a * c + b * d)
    res[1, 2] = 2 * (b * c - a * d)
    res[1, 0] = 2 * (a * b + c * d)
    res[2, 0] = 2 * (a * c - b * d)
    res[2, 1] = 2 * (b * c + a * d)
    if abs(det(res) - 1) > eps:
        raise RuntimeError("Rotation matrix det not equal to 1: det=", det(res))
    return res


def angleAxis2Quaternion(alpha, axis):
    """
    :param alpha: rotation angle,
    :param axis: np.array or list of shape 3
    """
    axis = np.array(axis)
    axis = axis / norm(axis)  # Make sure axis is normalized
    q4 = np.cos(alpha / 2)
    h = np.sin(alpha / 2)
    q1 = h * axis[0]
    q2 = h * axis[1]
    q3 = h * axis[2]
    return (q1, q2, q3, q4)
