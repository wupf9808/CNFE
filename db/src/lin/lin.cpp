#include "lin.h"

namespace CNFE {
namespace Lin {

DecryptSession::DecryptSession() : init(false) {
    // 1. Call MyTest_init to allocate memory (just like a normal UDF).
}

void DecryptSession::clear() {
    // 3. Call MyTest_clear for the first row in each group.
    param = PublicParameter();
    init  = false;
}

void DecryptSession::add(unsigned long *lens, char **args) {
    // 4. Call MyTest_add for each row that belongs to the same group.
    auto id = *(int64_t *)args[0];

    if (!init) {
        param.ell = build_mpz(lens[5], args[5]).get_ui();
        param.m   = build_mpz(lens[6], args[6]).get_ui();
        param.n   = build_mpz(lens[7], args[7]).get_ui();
        param.t   = build_mpz(lens[8], args[8]).get_ui();
        param.p_1 = build_mpz(lens[9], args[9]);
        param.p_2 = build_mpz(lens[10], args[10]);
        param.lam = build_mpz(lens[11], args[11]);
        param.q   = build_mpz(lens[12], args[12]);
        param.sd  = build_mpz(lens[13], args[13]);

        ct_c0     = Vector(param.m);
        ct_c1     = Vector(param.ell + param.t + 1);
        sk_ky     = Vector(param.m);
        sk_yh     = Vector(param.ell + param.t + 1);

        init      = true;
    }

    if (id < param.m) {
        ct_c0(id) = build_mpz(lens[1], args[1]);
        sk_ky(id) = build_mpz(lens[3], args[3]);
    }
    ct_c1(id) = build_mpz(lens[2], args[2]);
    sk_yh(id) = build_mpz(lens[4], args[4]);
}

long long DecryptSession::get_result() {
    // 5. Call MyTest to get the result when the group changes or the last
    // row has been processed.
    mpz mu = ({
        mpz target = ((sk_yh.transpose() * ct_c1)(0) % param.q -
                      (sk_ky.transpose() * ct_c0)(0) % param.q + param.q) %
                     param.q;
        mpz coeff    = param.q / param.lam;
        mpz muest    = target / coeff;

        int mindelta = 0;
        mpz mindiff;
        mpz_abs(mindiff.get_mpz_t(), mpz(coeff * muest - target).get_mpz_t());

        for (int delta : {-1, 1}) {

            mpz diff;
            mpz_abs(diff.get_mpz_t(),
                    mpz(coeff * (muest + delta) - target).get_mpz_t());

            if (diff < mindiff) {
                mindiff  = diff;
                mindelta = delta;
            }
        }

        mpz r = muest + mindelta;
        mpz(muest + mindelta);
    });

    mu %= param.p_2;
    if (mu > (param.ell * param.p_1 * param.p_1) / 2 + param.p_2 / 2) {
        mu -= param.p_2;
    }

    return mu.get_si();
}

} // namespace Lin
} // namespace CNFE
