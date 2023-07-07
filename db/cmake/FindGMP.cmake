# Try to find the GNU Multiple Precision Arithmetic Library (GMP) See
# http://gmplib.org/

if(GMP_INCLUDES AND GMP_LIBRARIES)
  set(GMP_FIND_QUIETLY TRUE)
endif()

find_path(
  GMP_INCLUDES
  NAMES gmp.h
  PATHS $ENV{GMPDIR} ${INCLUDE_INSTALL_DIR})

find_path(
  GMPXX_INCLUDES
  NAMES gmpxx.h
  PATHS $ENV{GMPDIR} ${INCLUDE_INSTALL_DIR})

find_library(GMP_LIBRARIES gmp PATHS $ENV{GMPDIR} ${LIB_INSTALL_DIR})

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(GMP DEFAULT_MSG GMP_INCLUDES GMPXX_INCLUDES
                                  GMP_LIBRARIES)
mark_as_advanced(GMP_INCLUDES GMPXX_INCLUDES GMP_LIBRARIES)

message(STATUS "Found GMP includes: ${GMP_INCLUDES}")
message(STATUS "Found GMP libraries: ${GMP_LIBRARIES}")
message(STATUS "Found GMPXX includes: ${GMPXX_INCLUDES}")
