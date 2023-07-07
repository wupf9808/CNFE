import math
from collections import namedtuple

from gmpy2 import next_prime

from CNFE import lin

PublicParameter = namedtuple("PublicParameter", ["ell", "d", "lin"])


class ParameterBuilder:
    def __init__(self, m, n, t) -> None:
        self.lin_builder = lin.ParameterBuilder(m, n, t)

    def __call__(self, ell, d, p_1, p_2, q, log_alpha) -> PublicParameter:
        return PublicParameter(
            ell=ell, d=d, lin=self.lin_builder(ell // d, p_1, p_2, q, log_alpha)
        )
