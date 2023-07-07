import os
import sys

import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from CNFE.lin import DataOwner, KeyCurator, PublicParameter, User
from CNFE.utils import RNG


def test(param: PublicParameter, sigma: int, x: np.array, y: np.array):
    # KeyCurator: setup
    key_curator = KeyCurator(param, sigma)
    data_owner = DataOwner(param, key_curator.pubkey)
    user = User(param)

    # KeyCurator: registration
    reg = key_curator.register()

    # DataOwner: encrypt
    ct = data_owner.encrypt(x, reg)

    # User: query
    sk = key_curator.keygen(y, reg)
    res = user.query(ct, sk)

    return res


if __name__ == "__main__":
    from CNFE.lin import ParameterBuilder, PredefinedParameters

    sigma = 10
    parameters = PredefinedParameters(ParameterBuilder(m=1 << 5, n=1 << 6, t=1 << 10))

    param = parameters[0]

    # user input
    x = RNG.uniform(param.p_1, (param.ell,))
    y = RNG.uniform(param.p_1, (param.ell,))
    true_result = x @ y
    res = test(param, sigma, x, y)

    # print output
    print("True Result :", true_result)
    print("Query Result:", res)
    print("Noise       :", res - true_result)
