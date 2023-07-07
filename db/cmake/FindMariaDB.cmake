# https://github.com/babelouest/hoel/blob/master/cmake-modules/FindMariaDB.cmake
#
# FindMariaDB.cmake
#
# Try to find the include directory

if(CMAKE_SIZEOF_VOID_P EQUAL 8)
  set(PFILES $ENV{ProgramW6432})
else()
  set(PFILES $ENV{ProgramFiles})
endif()

if(NOT MARIADB_INCLUDE_DIR)
  if(WIN32)
    find_path(MARIADB_INCLUDE_DIR mysql.h $ENV{MARIADB_INCLUDE_DIR}
              $ENV{MARIADB_DIR}/include $ENV{MARIADB_DIR}/include/mariadb
              ${PFILES}/MariaDB/*/include)
  else()
    find_path(MARIADB_BIN_DIR mariadb_config $ENV{MARIADB_DIR}/bin
              ${MARIADB_DIR}/bin)
    if(MARIADB_BIN_DIR)
      exec_program(
        ${MARIADB_BIN_DIR}/mariadb_config ARGS
        "--include"
        OUTPUT_VARIABLE MARIADB_INCLUDE_DIR)
      add_definitions(${MARIADB_INCLUDE_DIR})
    else()
      find_path(MARIADB_INCLUDE_DIR mysql.h $ENV{MARIADB_INCLUDE_DIR}
                $ENV{MARIADB_DIR}/include $ENV{MARIADB_DIR}/include/mariadb)
    endif()
  endif()
endif()

if(MARIADB_INCLUDE_DIR)
  message(STATUS "Found MariaDB includes: ${MARIADB_INCLUDE_DIR}")
endif()

if(NOT MARIADB_LIBRARY_DIR)
  if(WIN32)
    # Try to find mariadb client libraries
    find_path(
      MARIADB_LIBRARY_DIR
      ${MARIADB_CLIENT_FILENAME}
      $ENV{MARIADB_LIBRARY}
      ${PFILES}/MariaDB/*/lib
      $ENV{MARIADB_DIR}/lib/mariadb
      $ENV{MARIADB_DIR}/lib
      $ENV{MARIADB_DIR}/libmariadb)

    if(MARIADB_LIBRARY)
      get_filename_component(MARIADB_LIBRARY_DIR ${MARIADB_LIBRARY} PATH)
    endif()

  else()
    find_path(MARIADB_BIN_DIR mariadb_config $ENV{MARIADB_DIR}/bin
              ${MARIADB_DIR}/bin)
    if(MARIADB_BIN_DIR)
      exec_program(
        ${MARIADB_BIN_DIR}/mariadb_config ARGS
        "--libs"
        OUTPUT_VARIABLE MARIADB_LIBRARY_DIR)
      # since we use the static library we need the directory part only
      string(SUBSTRING ${MARIADB_LIBRARY_DIR} 2 -1 MARIADB_LIBRARY_DIR)
      string(FIND ${MARIADB_LIBRARY_DIR} " -l" MY_LENGTH)
      string(SUBSTRING ${MARIADB_LIBRARY_DIR} 0 ${MY_LENGTH}
                       MARIADB_LIBRARY_DIR)
    endif()
  endif()
endif()

if(MARIADB_LIBRARY_DIR AND MARIADB_INCLUDE_DIR)
  message(STATUS "Found MariaDB libraries: ${MARIADB_LIBRARY_DIR}")
  set(MARIADB_FOUND TRUE)
else()
  message(
    STATUS
      "MariaDB not found. Includes: ${MARIADB_INCLUDE_DIR}, Libs: ${MARIADB_LIBRARY_DIR}"
  )
endif()
