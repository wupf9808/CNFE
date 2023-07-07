# CNFE UDF

## Dependency

``` console
$ sudo apt install libmariadbd-dev libgmp-dev
```

## Build & run

``` console
$ mkdir build && cd build && cmake .. && make -j
```

Launch a mariadb instance, install the UDF and execute SQL.
Refer to `script/app.py`.
