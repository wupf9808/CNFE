import os
import sys

import mariadb
from rich import print
from writer import DBWriter, put_mpz

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from CNFE.lin import (
    DataOwner,
    KeyCurator,
    ParameterBuilder,
    PredefinedParameters,
    PublicParameter,
    User,
)
from CNFE.utils import RNG

SESSION_NAME = "sidxyz"

# - data        (idx:int, val:bigint)
# - query       (idx:int, val:bigint)
# - parameter
#       (name:str, value:mpz)
# - ct
#   - lin
#       - c0    (idx:int, val:mpz)   m
#       - c1    (idx:int, val:mpz)   ell+t+1
#   - quad
#       - c     (idx:int, val:mpz)   ell
# - sk
#   - lin
#       - ky    (idx:int, val:mpz)   m
#       - yhat  (idx:int, val:mpz)   ell+t+1
#   - quad
#       - *


def dump_parameter(self: DBWriter, table_name: str, param: PublicParameter):
    cursor = self.conn.cursor()
    # cursor.execute(f"DROP TABLE IF EXISTS {self.prefix}_{table_name};")
    cursor.execute(
        f"""CREATE TABLE {self.prefix}_{table_name} (
                ell TINYBLOB,
                m   TINYBLOB,
                n   TINYBLOB,
                t   TINYBLOB,
                p_1 TINYBLOB,
                p_2 TINYBLOB,
                lam TINYBLOB,
                q   TINYBLOB,
                sd  TINYBLOB
        );"""
    )

    cursor.execute(
        "INSERT INTO {name} ({columns}) VALUES ({values});".format(
            name=f"{self.prefix}_{table_name}",
            columns=",".join(param._asdict().keys()),
            values=",".join(
                f"UNHEX('{put_mpz(val)}')" for val in param._asdict().values()
            ),
        )
    )


if __name__ == "__main__":
    # generate parameters
    sigma = 10
    param = PredefinedParameters(ParameterBuilder(m=1 << 5, n=1 << 6, t=1 << 10))[0]

    # generate user input
    x = RNG.uniform(param.p_1, (param.ell,))
    y = RNG.uniform(param.p_1, (param.ell,))
    true_result = x @ y

    key_curator = KeyCurator(param, sigma)
    data_owner = DataOwner(param, key_curator.pubkey)

    reg = key_curator.register()
    ct = data_owner.encrypt(x, reg)
    sk = key_curator.keygen(y, reg)

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
        writer.dump_data("query", y)
        writer.dump_message("ct", c0=ct.c0, c1=ct.c1)
        writer.dump_message("sk", ky=sk.ky, yhat=sk.yhat)

        with connection.cursor() as cursor:
            cursor.execute("DROP FUNCTION IF EXISTS cnfe_lin;")
            connection.commit()

            cursor.execute(
                "CREATE AGGREGATE FUNCTION cnfe_lin RETURNS INTEGER SONAME 'libcnfe-dec.so';"
            )
            cursor.execute(
                """
                SELECT cnfe_lin(
                    ct.id,
                    ct.c0,
                    ct.c1,
                    sk.ky,
                    sk.yhat,
                    param.ell,
                    param.m,
                    param.n,
                    param.t,
                    param.p_1,
                    param.p_2,
                    param.lam,
                    param.q,
                    param.sd
                )
                FROM sidxyz_ct AS ct, sidxyz_sk AS sk, sidxyz_param AS param
                WHERE ct.id = sk.id;
                """
            )
            print(cursor.fetchall())
