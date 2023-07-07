import os
import sys

import mariadb
from rich import print
from writer import DBWriter, put_mpz
import numpy as np


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from CNFE.quad import (
    DataOwner,
    KeyCurator,
    ParameterBuilder,
    PredefinedParameters,
    PublicParameter,
    User,
)
from CNFE.utils import RNG

SESSION_NAME = "sid123"

# - data        (idx:int, val:bigint)   ell
# - query       (idx:int, val:bigint)   ell * ell
# - parameter
#       (name:str, value:mpz)
# - ct
#   - lin
#       - c0    (idx:int, val:mpz)      m
#       - c1    (idx:int, val:mpz)      (ell+1)+t+1
#   - quad
#       - c     (idx:int, val:mpz)      ell
# - sk
#   - lin
#       - ky    (idx:int, val:mpz)      m
#       - yhat  (idx:int, val:mpz)      (ell+1)+t+1
#   - quad
#       - *


def dump_parameter(self: DBWriter, table_name: str, param: PublicParameter):
    cursor = self.conn.cursor()
    # cursor.execute(f"DROP TABLE IF EXISTS {self.prefix}_{table_name};")
    cursor.execute(
        f"""CREATE TABLE {self.prefix}_{table_name} (
                ell     TINYBLOB,
                m       TINYBLOB,
                n       TINYBLOB,
                t       TINYBLOB,
                p_1     TINYBLOB,
                p_2     TINYBLOB,
                q       TINYBLOB,
                sd      TINYBLOB,
                lin_ell TINYBLOB,
                lin_m   TINYBLOB,
                lin_n   TINYBLOB,
                lin_t   TINYBLOB,
                lin_p_1 TINYBLOB,
                lin_p_2 TINYBLOB,
                lin_lam TINYBLOB,
                lin_q   TINYBLOB,
                lin_sd  TINYBLOB
        );"""
    )

    param_dict = {
        "ell": put_mpz(param.ell),
        "m": put_mpz(param.m),
        "n": put_mpz(param.n),
        "t": put_mpz(param.t),
        "p_1": put_mpz(param.p_1),
        "p_2": put_mpz(param.p_2),
        "q": put_mpz(param.q),
        "sd": put_mpz(param.sd),
        "lin_ell": put_mpz(param.lin.ell),
        "lin_m": put_mpz(param.lin.m),
        "lin_n": put_mpz(param.lin.n),
        "lin_t": put_mpz(param.lin.t),
        "lin_p_1": put_mpz(param.lin.p_1),
        "lin_p_2": put_mpz(param.lin.p_2),
        "lin_lam": put_mpz(param.lin.lam),
        "lin_q": put_mpz(param.lin.q),
        "lin_sd": put_mpz(param.lin.sd),
    }

    cursor.execute(
        "INSERT INTO {name} ({columns}) VALUES ({values});".format(
            name=f"{self.prefix}_{table_name}",
            columns=",".join(param_dict.keys()),
            values=",".join(f"UNHEX('{val}')" for val in param_dict.values()),
        )
    )


if __name__ == "__main__":
    # generate parameters
    sigma = 10
    param = PredefinedParameters(ParameterBuilder(m=1 << 5, n=1 << 6, t=1 << 2))[0]

    # generate user input
    x = RNG.uniform(param.p_1, (param.ell,))
    a = np.ones((param.ell, param.ell), dtype=int)
    true_result = x @ a @ x

    key_curator = KeyCurator(param, sigma)
    data_owner = DataOwner(param, key_curator.pubkey)

    reg = key_curator.register()
    ct = data_owner.encrypt(x, reg)
    sk = key_curator.keygen(a, reg)

    # connect to MariaDB platform
    with mariadb.connect(
        user="root",
        password="tVKnm2sZRZ8FYB5CHM3p",
        host="127.0.0.1",
        port=3306,
        database="cnfe",
    ) as connection:
        connection: mariadb.Connection

        with connection.cursor() as cursor:
            cursor.execute("SET GLOBAL general_log=1;")
            cursor.execute("SET GLOBAL log_warnings=9;")
            cursor.execute("SET GLOBAL log_output='FILE';")
            cursor.execute("SET GLOBAL general_log_file='/var/log/mysql/mysql.log';")

            cursor.execute("SHOW FULL TABLES;")
            for tbl, _ in cursor.fetchall():
                cursor.execute(f"DROP TABLE IF EXISTS {tbl};")

        writer = DBWriter(SESSION_NAME, connection)
        dump_parameter(writer, "param", param)
        writer.dump_data("data", x)
        writer.dump_data("query", np.ravel(a))
        writer.dump_message("ct", lin_c0=ct.lin.c0, lin_c1=ct.lin.c1, quad_c=ct.c)
        writer.dump_message("sk", lin_ky=sk.lin.ky, lin_yhat=sk.lin.yhat)

        with connection.cursor() as cursor:
            cursor.execute("DROP FUNCTION IF EXISTS cnfe_quad;")
            connection.commit()

            cursor.execute(
                "CREATE AGGREGATE FUNCTION cnfe_quad RETURNS INTEGER SONAME 'libcnfe-dec.so';"
            )
            cursor.execute(
                f"""
                SELECT cnfe_quad(
                    query.id,
                    ct.lin_c0,
                    ct.lin_c1,
                    sk.lin_ky,
                    sk.lin_yhat,
                    param.lin_ell,
                    param.lin_m,
                    param.lin_n,
                    param.lin_t,
                    param.lin_p_1,
                    param.lin_p_2,
                    param.lin_lam,
                    param.lin_q,
                    param.lin_sd,
                    ct.quad_c,
                    query.value,
                    param.ell,
                    param.m,
                    param.n,
                    param.t,
                    param.p_1,
                    param.p_2,
                    param.q,
                    param.sd
                )
                FROM
                    {SESSION_NAME}_param AS param,
                    {SESSION_NAME}_query AS query
                    LEFT JOIN {SESSION_NAME}_ct AS ct
                        ON query.id = ct.id
                    LEFT JOIN {SESSION_NAME}_sk AS sk
                        ON query.id = sk.id
                ORDER BY
                    query.id;
                """
            )
            print(cursor.fetchall())
