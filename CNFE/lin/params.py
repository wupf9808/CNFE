import math
from collections import namedtuple

PublicParameter = namedtuple(
    "PublicParameter",
    [
        "ell",  # input size
        "m",  # protocol parameter
        "n",  # security parameter
        "t",  # security parameter
        "p_1",  # upper bound of the input data ( x_i \in x )
        "p_2",  # upper bound of the ( <x,y>+e )
        "lam",  # upper bound of ( <x_hat,y_hat>+e ), (l+t+1)*(p_2)^2
        "q",  # the size of ciphertext domain
        "sd",  # standard deviation of discrete gaussian distribution, ( \alpha q )
    ],
)


class ParameterBuilder:
    def __init__(self, m, n, t) -> None:
        self.m = m
        self.n = n
        self.t = t

    def __call__(self, ell, p_1, p_2, q, log_alpha) -> PublicParameter:
        lam = 1 << math.ceil(math.log2((ell + self.t + 1) * p_2**2))

        assert ell * p_1**2 < p_2
        assert (ell + self.t + 1) * p_2**2 <= lam
        assert lam < q

        return PublicParameter(
            ell=ell,
            m=self.m,
            n=self.n,
            t=self.t,
            p_1=p_1,
            p_2=p_2,
            lam=lam,
            q=q,
            sd=q >> (-log_alpha),
        )


def PredefinedParameters(builder: ParameterBuilder):
    return [
        builder(2**10, 1031, 2**31 - 1, 2**160 + 7, -154),
        builder(2**12, 1031, 2**33 + 17, 2**172 + 105, -166),
        builder(2**14, 1031, 2**35 + 53, 2**184 + 27, -178),
        builder(2**16, 1031, 2**37 + 9, 2**196 + 21, -190),
        builder(2**18, 1031, 2**39 + 23, 2**208 + 375, -202),
        builder(2**20, 1031, 2**41 + 27, 2**220 + 217, -214),
    ]
