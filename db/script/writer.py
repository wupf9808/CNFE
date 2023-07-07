from binascii import hexlify
from itertools import zip_longest
from typing import Iterable

import gmpy2
import mariadb
import numpy as np


def put_mpz(val: int):
    if val is None:
        return None
    assert isinstance(val, int) or isinstance(val, gmpy2.mpz)
    return hexlify(gmpy2.to_binary(gmpy2.mpz(val))[2:]).decode("ascii")


class DBWriter:
    def __init__(self, prefix: str, connection: mariadb.Connection) -> None:
        self.conn = connection
        self.prefix = prefix

    def _create_table(self, table_name: str, key_type: str, columns):
        if not isinstance(columns, str):
            columns = ",".join(columns)

        cursor = self.conn.cursor()
        # cursor.execute(f"DROP TABLE IF EXISTS {self.prefix}_{table_name};")
        cursor.execute(
            f"""
            CREATE TABLE {self.prefix}_{table_name} (
                id {key_type},
                PRIMARY KEY (id),
                {columns}
            );
            """
        )

    def _insert_values(self, table_name: str, values: Iterable[tuple]):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO {name} VALUES {value};".format(
                name=f"{self.prefix}_{table_name}",
                value=",".join(
                    f"({','.join(str(x) for x in value_tuple)})"
                    for value_tuple in values
                ),
            )
        )

    def dump_data(self, table_name: str, values: np.array):
        self._create_table(table_name, "INT UNSIGNED", "value BIGINT UNSIGNED")
        self._insert_values(table_name, enumerate(values))

    def dump_message(self, table_name: str, **kwargs):
        self._create_table(
            table_name,
            "INT UNSIGNED",
            (f"{key} TINYBLOB NULL" for key in kwargs.keys()),
        )

        self._insert_values(
            table_name,
            (
                [f"'{idx}'", *(f"UNHEX('{put_mpz(x)}')" for x in vals)]
                for idx, vals in enumerate(zip_longest(*kwargs.values()))
            ),
        )
