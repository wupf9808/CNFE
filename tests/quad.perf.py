import cProfile
import os
import pstats
import sys
from datetime import datetime

import numpy as np
from rich import print

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from CNFE.quad import Cipher, ParameterBuilder, PredefinedParameters
from CNFE.utils import RNG

FNAME = datetime.now().strftime("%Y%m%d-%H%M%S")


sigma = 10
parameters = PredefinedParameters(ParameterBuilder(m=1 << 5, n=1 << 6, t=1 << 10))

param = parameters[0]

x = RNG.uniform(param.p_1, (param.ell,))
a = np.ones((param.ell, param.ell), dtype=int)
true_result = x @ a @ x

REPEAT = 16

with cProfile.Profile() as pr:
    for _ in range(REPEAT):
        cipher = Cipher(param)
        pk, msk = cipher.setup()
        reg = cipher.datareg()
        ct = cipher.encrypt(pk, x, reg)
        sk = cipher.keygen(pk, msk, a, sigma, reg)
        res = cipher.decrypt(a, ct, sk)

pr.dump_stats(f"{FNAME}.quad.stat")

print("True Result :", true_result)
print("Query Result:", res)
print("Noise       :", res - true_result)

pstats.Stats(pr).sort_stats("tottime").print_stats(20)
