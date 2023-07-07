#ifndef __CNFE_H_
#define __CNFE_H_

#include "mysql.h"

#ifdef __cplusplus
extern "C" {
#endif

my_bool cnfe_lin_init(UDF_INIT *initid, UDF_ARGS *args, char *message);
void cnfe_lin_deinit(UDF_INIT *initid);
void cnfe_lin_reset(UDF_INIT *initid, UDF_ARGS *args, char *is_null,
                    char *error);
void cnfe_lin_clear(UDF_INIT *initid, char *is_null, char *error);
void cnfe_lin_add(UDF_INIT *initid, UDF_ARGS *args, char *is_null, char *error);
long long cnfe_lin(UDF_INIT *initid, UDF_ARGS *args, char *is_null,
                   char *error);

my_bool cnfe_quad_init(UDF_INIT *initid, UDF_ARGS *args, char *message);
void cnfe_quad_deinit(UDF_INIT *initid);
void cnfe_quad_reset(UDF_INIT *initid, UDF_ARGS *args, char *is_null,
                     char *error);
void cnfe_quad_clear(UDF_INIT *initid, char *is_null, char *error);
void cnfe_quad_add(UDF_INIT *initid, UDF_ARGS *args, char *is_null,
                   char *error);
long long cnfe_quad(UDF_INIT *initid, UDF_ARGS *args, char *is_null,
                    char *error);

#ifdef __cplusplus
}
#endif

#endif
