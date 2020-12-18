import math
from decimal import localcontext, Decimal, ROUND_HALF_UP


def surface_with_3_points_v1(p1, p2, p3):
    b = (p1[2] / (1 - p1[0] / p3[0]) + p2[2] / (p2[0] / p1[0] - 1) - p3[2] / (p3[0] / p1[0] - 1) -
         p1[2] / (1 - p1[0] / p2[0])) / (p1[1] / (1 - p1[0] / p3[0]) + p2[1] / (p2[0] / p1[0] - 1) -
                                         p3[1] / (p3[0] / p1[0] - 1) - p1[1] / (1 - p1[0] / p2[0]))
    c = ((p1[2] - b * p1[1]) / p1[0] - (p3[2] - b * p3[1]) / p3[0]) / (1 / p1[0] - 1 / p3[0])
    a = (p1[2] - b * p1[1] - c) / p1[0]
    return a, b, c


def det_of_matrix(matrix):
    if len(matrix) == 2:
        return matrix[0][0] * matrix[1][1] - matrix[1][0] * matrix[0][1]
    elif len(matrix) == 1:
        return matrix[0][0]
    elif len(matrix) > 2:
        score = 0
        for i in range(len(matrix)):
            tm = list(col[1:] for col in matrix if matrix.index(col) != i)
            score += matrix[i][0] * det_of_matrix(tm) * (-1) ** i
        return score
    else:
        raise ValueError('matrix too short')


def normalize_vector(v):
    return [v[0] / (v[0] ** 2 + v[1] ** 2 + v[2] ** 2) ** 0.5, v[1] / (v[0] ** 2 + v[1] ** 2 + v[2] ** 2) ** 0.5,
            v[2] / (v[0] ** 2 + v[1] ** 2 + v[2] ** 2) ** 0.5]


def cross_product(v1, v2):
    return [v1[1] * v2[2] - v1[2] * v2[1], v1[2] * v2[0] - v1[0] * v2[2], v1[0] * v2[1] - v1[1] * v2[0]]

def dot_product(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]


def tetrahedron_volume(p1, p2, p3, p4):
    ab = [p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]]
    ac = [p1[0] - p3[0], p1[1] - p3[1], p1[2] - p3[2]]
    ad = [p1[0] - p4[0], p1[1] - p4[1], p1[2] - p4[2]]
    return abs(sum(dot_product(ad, cross_product(ab, ac)))) / 6


def point_in_pyramid(pyramid, p):
    for face in range(4):
        if face != 3:
            ab = [pyramid[face + 1][0] - pyramid[0][0], pyramid[face + 1][1] - pyramid[0][1], pyramid[face + 1][2] -
                  pyramid[0][2]]
            ac = [pyramid[face + 2][0] - pyramid[0][0], pyramid[face + 2][1] - pyramid[0][1], pyramid[face + 2][2] -
                  pyramid[0][2]]
        else:
            ab = [pyramid[face + 1][0] - pyramid[0][0], pyramid[face + 1][1] - pyramid[0][1], pyramid[face + 1][2] -
                  pyramid[0][2]]
            ac = [pyramid[1][0] - pyramid[0][0], pyramid[1][1] - pyramid[0][1], pyramid[1][2] -
                  pyramid[0][2]]
        print(ab, ac)
        ab, ac = normalize_vector(ab), normalize_vector(ac)
        cp = cross_product(ab , ac)
        print('normalized ab, ac: ', ab, ac)
        print(cp)
        print(dot_product(p, cp))


def rhu(n, d=0):
    with localcontext() as ctx:
        ctx.rounding = ROUND_HALF_UP
        if not d:
            after_comma = len(str(n).split('.')[1]) - 1
        else:
            after_comma = d + 1
        score = float(Decimal(n * 10 ** after_comma).to_integral_value()) / 10 ** after_comma
        if score.is_integer():
            return int(score)
        else:
            return score


def scientific_format(n, digits):
    n = float(n)
    return n.__format__('.' + str(digits) + 'E')
