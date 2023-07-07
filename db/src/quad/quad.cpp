#include "quad.h"
#include <cstdio>

namespace CNFE {
namespace Quad {

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
    if (id < param.ell + param.t + 2) {
        lin_session.add(lens, args);
    }

    if (!init) {
        param.ell = build_mpz(lens[16], args[16]).get_ui();
        param.m   = build_mpz(lens[17], args[17]).get_ui();
        param.n   = build_mpz(lens[18], args[18]).get_ui();
        param.t   = build_mpz(lens[19], args[19]).get_ui();
        param.p_1 = build_mpz(lens[20], args[20]);
        param.p_2 = build_mpz(lens[21], args[21]);
        param.q   = build_mpz(lens[22], args[22]);
        param.sd  = build_mpz(lens[23], args[23]);
        init      = true;

        a         = Matrix(param.ell, param.ell);
        ct_c      = Vector(param.ell);
    }

    if (id < param.ell) {
        ct_c(id) = build_mpz(lens[14], args[14]);
    }
    a(id / param.ell, id % param.ell) = build_mpz(lens[15], args[15]);
}

long long DecryptSession::get_result() {
    // 5. Call MyTest to get the result when the group changes or the last
    // row has been processed.
    mpz lin_res;
    mpz_set_si(lin_res.get_mpz_t(), lin_session.get_result());

    mpz cag = (ct_c.transpose() * a * ct_c)(0);
    mpz res = ((cag + lin_res) % param.q) % param.p_2;
    // if (res > param.q - param.p_2) {
    //     res -= param.q;
    // }

    return res.get_si();
}

} // namespace Quad
} // namespace CNFE
