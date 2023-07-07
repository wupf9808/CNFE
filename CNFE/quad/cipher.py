import secrets
from collections import namedtuple
from typing import Tuple

import numpy as np

from CNFE import lin
from CNFE.quad.params import PublicParameter
from CNFE.utils import RNG

PK = namedtuple("PK", ["lin", "u"])
MSK = namedtuple("MSK", ["lin"])
REG = namedtuple("REG", ["lin"])
CT = namedtuple("CT", ["lin", "c"])
SK = namedtuple("SK", ["lin"])


class Cipher:
    def __init__(self, param: PublicParameter) -> None:
        self.param = param
        self.lin_cipher = lin.Cipher(param.lin)
        self.upper_bound = param.ell**2 * param.p_1**3

    def setup(self) -> Tuple[PK, MSK]:
        u = RNG.uniform(self.param.q, (self.param.ell,))
        pk, msk = self.lin_cipher.setup()
        return PK(lin=pk, u=u), MSK(lin=msk)

    def datareg(self) -> REG:
        return REG(lin=self.lin_cipher.datareg())

    def encrypt(self, pk: PK, x, reg: REG) -> CT:
        s = secrets.randbelow(self.param.q)

        # e = RNG.normal(self.param.sd, (self.param.ell,))
        # c = (s * pk.u + self.param.p_2 * e + x) % self.param.q
        c = (s * pk.u + x) % self.param.q

        lin_x = np.concatenate(((s**2,), s * c))
        lin_ct = self.lin_cipher.encrypt(pk.lin, lin_x, reg.lin)
        return CT(lin=lin_ct, c=c)

    def keygen(self, pk: PK, msk: MSK, a: np.matrix, sigma: int, reg: REG) -> SK:
        assert a.shape == (self.param.ell, self.param.ell)

        lin_y = (
            np.concatenate(((pk.u @ a @ pk.u,), -pk.u @ (a + a.transpose())))
            % self.param.q
        )
        return SK(lin=self.lin_cipher.keygen(msk.lin, lin_y, sigma, reg.lin))

    def decrypt(self, a: np.matrix, ct: CT, sk: SK) -> int:
        res = (ct.c @ a @ ct.c + self.lin_cipher.decrypt(ct.lin, sk.lin)) % self.param.q
        if res > self.param.q - self.param.p_2:
            res -= self.param.q
            return res

        # res %= self.param.p_2
        return res
