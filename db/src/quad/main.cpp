#include "cnfe.h"
#include "quad.h"

#include <cstdio>

my_bool cnfe_quad_init(UDF_INIT *initid, UDF_ARGS *args, char *message) {
    // To check the number of arguments to XXX().
    if (args->arg_count != 24) {
        sprintf(message, "Requries 24 arguments, got %d.", args->arg_count);
        return 1;
    }

    // To verify that the arguments are of a required type or, alternatively,
    // to tell MySQL to coerce arguments to the required types when the main
    // function is called.

    if (args->arg_type[0] != INT_RESULT) {
        sprintf(message, "args->arg_type[0] != INT_RESULT, got %d",
                args->arg_type[0]);
    }

    for (int i = 1; i < 24; i++) {
        if (args->arg_type[i] != STRING_RESULT) {
            sprintf(message, "args->arg_type[%d] != STRING_RESULT, got %d", i,
                    args->arg_type[i]);
        }
    }

    // To allocate any memory required by the main function.
    initid->ptr = reinterpret_cast<char *>(new CNFE::Quad::DecryptSession());

    // To specify the maximum length of the result.
    initid->max_length = 1;

    // To specify (for REAL functions) the maximum number of decimal places
    // in the result.

    // To specify whether the result can be NULL.
    initid->maybe_null = false;

    return 0;
}

void cnfe_quad_deinit(UDF_INIT *initid) {
    delete reinterpret_cast<CNFE::Quad::DecryptSession *>(initid->ptr);
}

void cnfe_quad_clear(UDF_INIT *initid, char *is_null, char *error) {
}

void cnfe_quad_add(UDF_INIT *initid, UDF_ARGS *args, char *is_null,
                   char *error) {
    reinterpret_cast<CNFE::Quad::DecryptSession *>(initid->ptr)
        ->add(args->lengths, args->args);
}

long long cnfe_quad(UDF_INIT *initid, UDF_ARGS *args, char *is_null,
                    char *error) {
    return reinterpret_cast<CNFE::Quad::DecryptSession *>(initid->ptr)
        ->get_result();
}
