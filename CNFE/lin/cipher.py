from collections import namedtuple
from typing import Tuple

import numpy as np

from CNFE.lin.params import PublicParameter
from CNFE.utils import RNG

PK = namedtuple("PK", ["A", "U"])
MSK = namedtuple("MSK", ["Z"])
REG = namedtuple("REG", ["r"])
CT = namedtuple("CT", ["c0", "c1"])
SK = namedtuple("SK", ["ky", "yhat"])


class Cipher:
    def __init__(self, param: PublicParameter) -> None:
        self.param = param
        self.ext_len = self.param.ell + self.param.t + 1

    def setup(self) -> Tuple[PK, MSK]:
        A = RNG.uniform(self.param.q, (self.param.m, self.param.n))
        Z = RNG.normal(self.param.sd, (self.ext_len, self.param.m))
        U = Z @ A
        return (PK(A, U), MSK(Z))

    def datareg(self) -> REG:
        r = RNG.uniform(self.param.p_2, (self.param.t,))
        return REG(r=r)

    def encrypt(self, pk: PK, x, reg: REG) -> CT:
        assert x.shape == (self.param.ell,)

        s = RNG.uniform(self.param.q, (self.param.n,))
        e0 = RNG.normal(self.param.sd, (self.param.m,))
        e1 = RNG.normal(self.param.sd, (self.ext_len,))

        xhat = np.concatenate((x, reg.r, (1,)))

        c0 = (pk.A @ s + e0) % self.param.q
        assert c0.shape == (self.param.m,)

        c1 = (pk.U @ s + e1 + (self.param.q // self.param.lam) * xhat) % self.param.q
        assert c1.shape == (self.ext_len,)

        return CT(c0=c0, c1=c1)

    def keygen(self, msk: MSK, y, reg: REG, sigma=None, e=None) -> SK:
        assert y.shape == (self.param.ell,)

        if e is None:
            e = RNG.sample_noise(sigma)
        v = RNG.uniform(self.param.p_2, (self.param.t,))

        yhat = np.concatenate(
            (y, self.param.p_2 - v, (((reg.r @ v) + e) % self.param.p_2,))
        )

        ky = yhat.transpose() @ msk.Z
        assert ky.shape == (self.param.m,)
        return SK(ky=ky, yhat=yhat)

    def decrypt(self, ct: CT, sk: SK) -> int:
        target = ((sk.yhat @ ct.c1) - (sk.ky @ ct.c0)) % self.param.q
        coeff = self.param.q // self.param.lam

        mu = target // coeff + np.array([-1, 0, 1, 2], dtype=object)
        mu = mu[np.argmin(np.abs(coeff * mu - target))]
        res = mu % self.param.p_2

        if res > (self.param.ell * self.param.p_1**2 + self.param.p_2) >> 1:
            res -= self.param.p_2

        return res
