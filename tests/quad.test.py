import math
import os
import sys
from inspect import currentframe
from time import perf_counter_ns

from rich import print

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from CNFE import lin, quad
from CNFE.quad import Cipher
from CNFE.utils import RNG

SIGMA = 10


def base2(val):
    o = round(math.log2(val))
    r = val - (1 << o)
    if r > 0:
        r = f"+{r}"
    return f"2**{o}" + (str(r) if r else "")


def instance(param: quad.PublicParameter) -> int:
    ret = param._asdict()
    del ret["lin"]

    ret["p_1"] = base2(param.p_1)
    ret["p_2"] = base2(param.p_2)
    ret["q"] = base2(param.q)
    ret["lin.p_1"] = base2(param.lin.p_1)
    ret["lin.p_2"] = base2(param.lin.p_2)
    ret["lin.lam"] = base2(param.lin.lam)
    ret["lin.q"] = base2(param.lin.q)

    try:
        assert param.lin.ell < 2**20
        assert param.lin.ell * param.lin.n < 2**27
    except AssertionError:
        return ret

    print(param)
    print(currentframe().f_lineno, perf_counter_ns(), sep="\t")

    x = RNG.uniform(param.p_1, (param.ell,))
    print(currentframe().f_lineno, perf_counter_ns(), sep="\t")

    a = RNG.uniform(param.p_1, (param.ell, param.ell))
    print(currentframe().f_lineno, perf_counter_ns(), sep="\t")

    cipher = Cipher(param)
    print(currentframe().f_lineno, perf_counter_ns(), sep="\t")

    pk, msk = cipher.setup()
    print(currentframe().f_lineno, perf_counter_ns(), sep="\t")

    reg = cipher.datareg()
    print(currentframe().f_lineno, perf_counter_ns(), sep="\t")

    ct = cipher.encrypt(pk, x, reg)
    print(currentframe().f_lineno, perf_counter_ns(), sep="\t")

    sk = cipher.keygen(pk, msk, a, SIGMA, reg)
    print(currentframe().f_lineno, perf_counter_ns(), sep="\t")

    res = cipher.decrypt(a, ct, sk)
    print(currentframe().f_lineno, perf_counter_ns(), sep="\t")

    ret["expected"] = x @ a @ x
    ret["returned"] = res

    return ret


def get_nproc():
    mem_bytes = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")


if __name__ == "__main__":
    param = quad.PublicParameter(
        ell=16384,
        m=32,
        n=32,
        t=1024,
        p_1=1048583,
        p_2=618970019642690137449562141,
        q=39614081257132168796771975177,
        sd=64,
        lin=lin.PublicParameter(
            ell=16385,
            m=32,
            n=32,
            t=1024,
            p_1=1569275433846670190958947355801916604025588861116008628353,
            p_2=80695308690215893426747474125094121072803306025913234775958104891895238188026287332176417290004307232371974124148359197,
            lam=213376461852155336770555257303080249508632266314109061132680249976449191610164226288685830427889737303773757138989863694268441652931819682571627393674586561475045042544448465870818505149178048791326880516348371263414103937199246761317244076032,
            q=22764757236272150845448608801544890529699448070214573731542130224001885731721805946360208679001072341752808202824217284477494812905105397409989128551225758781216043560253652980086121317552684563986396549772842919559887665185494104910174738323915834363713045672574387360783297106750713554881423144392753679201516304384980639419833584098380232809470916520072049300631664767591769467222945129379105159685099673799496623780831236309234572873990107774355582238483953130135634240698698433297,
            sd=64,
        ),
    )

    print(instance(param))
