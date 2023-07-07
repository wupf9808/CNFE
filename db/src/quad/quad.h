#pragma once

#include "../lin/lin.h"
#include "../types.hpp"

using mpz = mpz_class;

namespace CNFE {
namespace Quad {

struct PublicParameter {
    size_t ell;
    size_t m;
    size_t n;
    size_t t;
    mpz p_1;
    mpz p_2;
    mpz q;
    mpz sd;
    Lin::PublicParameter lin;
};

class DecryptSession {
    bool init;

    Lin::DecryptSession lin_session;
    PublicParameter param;

    Matrix a;
    Vector ct_c;

  public:
    DecryptSession();

    void clear();

    void add(unsigned long *lens, char **args);

    long long get_result();

    ~DecryptSession() {
        // 7. Call MyTest_deinit to free any used memory.
    }
};

} // namespace Quad
} // namespace CNFE
