#pragma once

#include "Eigen/Core"
#include "gmpxx.h"

namespace CNFE {

using Matrix = Eigen::Matrix<mpz_class, Eigen::Dynamic, Eigen::Dynamic>;
using Vector = Eigen::Vector<mpz_class, Eigen::Dynamic>;

static mpz_class build_mpz(unsigned long len, char *buf) {
    if (len) {
        mpz_class ret;
        mpz_import(ret.get_mpz_t(), len, -1, sizeof(char), 0, 0, buf);
        return ret;
    } else {
        return mpz_class(0);
    }
}

} // namespace CNFE
