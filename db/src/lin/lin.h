#pragma once

#include "../types.hpp"

using mpz = mpz_class;

namespace CNFE {
namespace Lin {

struct PublicParameter {
    size_t ell;
    size_t m;
    size_t n;
    size_t t;
    mpz p_1;
    mpz p_2;
    mpz lam;
    mpz q;
    mpz sd;
};

class DecryptSession {
    bool init;

    PublicParameter param;

    Vector ct_c0;
    Vector ct_c1;
    Vector sk_ky;
    Vector sk_yh;

  public:
    DecryptSession();

    void clear();

    void add(unsigned long *lens, char **args);

    long long get_result();

    ~DecryptSession() {
        // 7. Call MyTest_deinit to free any used memory.
    }
};

} // namespace Lin
} // namespace CNFE
