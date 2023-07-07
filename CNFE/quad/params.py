import math
from collections import namedtuple

from gmpy2 import next_prime

from CNFE import lin

PublicParameter = namedtuple(
    "PublicParameter",
    [
        "ell",  # input size
        "m",  # protocol parameter
        "n",  # security parameter
        "t",  # security parameter
        "p_1",  # upper bound of the input data ( x_i \in x )
        "p_2",  # upper bound of the ( <x,y>+e )
        "q",  # the size of ciphertext domain
        "sd",  # standard deviation of discrete gaussian distribution, ( \alpha q )
        "lin",
    ],
)


class ParameterBuilder:
    def __init__(self, m, n, t) -> None:
        self.m = m
        self.n = n
        self.t = t
        self.lin_builder = lin.ParameterBuilder(m, n, t)

    def __call__(self, ell, p_1, p_2, q, log_alpha) -> PublicParameter:
        assert ell**2 * p_1**3 < p_2

        sd = q >> (-log_alpha)

        lin_ell = ell + 1
        lin_p_1 = next_prime(1 << math.ceil(math.log2(q**2)))
        lin_p_2 = next_prime(1 << math.ceil(math.log2(lin_ell * (lin_p_1**2))))

        lam = (lin_ell + self.t + 1) * (lin_p_2**2)
        lin_q = next_prime(1 << math.ceil(2 * math.log2(lam)))

        return PublicParameter(
            ell=ell,
            m=self.m,
            n=self.n,
            t=self.t,
            p_1=p_1,
            p_2=p_2,
            q=q,
            sd=sd,
            lin=self.lin_builder(
                ell=int(lin_ell),
                p_1=int(lin_p_1),
                p_2=int(lin_p_2),
                q=int(lin_q),
                log_alpha=math.floor(math.log2(sd) - 2 * math.log2(lam)),
            ),
        )


def PredefinedParameters(builder: ParameterBuilder):
    return [
        builder(2**10, 2**20 + 7, 2**81 + 17, 2**87 + 39, -81),
        builder(2**11, 2**20 + 7, 2**83 + 75, 2**89 + 29, -83),
        builder(2**12, 2**20 + 7, 2**85 + 171, 2**91 + 59, -85),
        builder(2**13, 2**20 + 7, 2**87 + 39, 2**93 + 105, -87),
        builder(2**14, 2**20 + 7, 2**89 + 29, 2**95 + 9, -89),
        builder(2**15, 2**20 + 7, 2**91 + 59, 2**97 + 105, -91),
        builder(2**16, 2**20 + 7, 2**93 + 105, 2**99 + 255, -93),
    ]
