# Simple smoke test for the solver
from core import simplex


def test_simple_problem():
    # maximize 3x + 5y
    # subject to
    # 1x + 0y <= 4
    # 0x + 2y <= 12
    # 3x + 2y <= 18
    c = [3, 5]
    A = [
        [1, 0],
        [0, 2],
        [3, 2],
    ]
    b = [4, 12, 18]
    sol, val = simplex.solve(c, A, b)
    print('test sol', sol, 'val', val)
    # Expected optimal value roughly 3*2 + 5*6 = 36 (x=2, y=6)
    assert abs(val - 36) < 1e-6


if __name__ == '__main__':
    test_simple_problem()
    print('OK')
