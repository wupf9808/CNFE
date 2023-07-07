from collections import namedtuple
from secrets import randbelow

from CNFE import lin
from CNFE.mife.params import PublicParameter
from CNFE.utils import RNG

PP = namedtuple("PP", ["pk"])
MSK = namedtuple("MSK", ["msk", "r"])
SK = namedtuple("SK", ["sk_i", "s"])


class Cipher:
    def __init__(self, param: PublicParameter) -> None:
        self.param = param
        self.cipher = lin.Cipher(param.lin)

    def setup(self, d: int):
        pps = []
        msks = []

        for i in range(d):
            pk, msk = self.cipher.setup()
            r = self.cipher.datareg()
            pps.append(PP(pk))
            msks.append(MSK(msk, r))

        return pps, msks

    def encrypt(self, pp: PP, msk: MSK, x):
        return self.cipher.encrypt(pp.pk, x, msk.r)

    def keygen(self, d: int, msk: MSK, y_vec, e: int):
        s_i = RNG.uniform(self.param.lin.p_2, (d,))
        e_i = RNG.normal(self.param.lin.sd, (d,))

        j = randbelow(d)
        e_i[j] = e

        sk = [
            self.cipher.keygen(_msk.msk, _y, _msk.r, e=int(_s + _e))
            for _msk, _y, _s, _e in zip(msk, y_vec, s_i, e_i)
        ]
        s = s_i.sum() + e_i.sum() - e_i[j]
        return SK(sk, s)

    def decrypt(self, ct_vec, sk: SK):
        assert len(ct_vec) == len(sk.sk_i)
        res = sum(self.cipher.decrypt(c, k) for c, k in zip(ct_vec, sk.sk_i))
        res -= sk.s
        res %= self.param.lin.p_2
        return res
