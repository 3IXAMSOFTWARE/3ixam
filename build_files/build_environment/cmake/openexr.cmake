
if(WIN32)
  set(OPENEXR_CMAKE_CXX_STANDARD_LIBRARIES "kernel32${LIBEXT} user32${LIBEXT} gdi32${LIBEXT} winspool${LIBEXT} shell32${LIBEXT} ole32${LIBEXT} oleaut32${LIBEXT} uuid${LIBEXT} comdlg32${LIBEXT} advapi32${LIBEXT} psapi${LIBEXT}")
  set(OPENEXR_EXTRA_ARGS
    -DCMAKE_CXX_STANDARD_LIBRARIES=${OPENEXR_CMAKE_CXX_STANDARD_LIBRARIES}
  )
else()
  set(OPENEXR_EXTRA_ARGS
  )
endif()

set(OPENEXR_EXTRA_ARGS
  ${OPENEXR_EXTRA_ARGS}
  -DZLIB_LIBRARY=${LIBDIR}/zlib/lib/${ZLIB_LIBRARY}
  -DZLIB_INCLUDE_DIR=${LIBDIR}/zlib/include/
  -DBUILD_TESTING=OFF
  -DOPENEXR_BUILD_BOTH_STATIC_SHARED=OFF
  -DBUILD_SHARED_LIBS=OFF
  -DOPENEXR_INSTALL_TOOLS=OFF
  -DOPENEXR_INSTALL_EXAMPLES=OFF
  -DImath_DIR=${LIBDIR}/imath/lib/cmake/Imath
  -DOPENEXR_LIB_SUFFIX=${OPENEXR_VERSION_BUILD_POSTFIX}
)

ExternalProject_Add(external_openexr
  URL file://${PACKAGE_DIR}/${OPENEXR_FILE}
  DOWNLOAD_DIR ${DOWNLOAD_DIR}
  URL_HASH ${OPENEXR_HASH_TYPE}=${OPENEXR_HASH}
  PREFIX ${BUILD_DIR}/openexr
  CMAKE_ARGS -DCMAKE_INSTALL_PREFIX=${LIBDIR}/openexr ${DEFAULT_CMAKE_FLAGS} ${OPENEXR_EXTRA_ARGS}
  INSTALL_DIR ${LIBDIR}/openexr
)

if(WIN32)
  ExternalProject_Add_Step(external_openexr after_install
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${LIBDIR}/openexr/lib ${HARVEST_TARGET}/openexr/lib
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${LIBDIR}/openexr/include ${HARVEST_TARGET}/openexr/include
    DEPENDEES install
  )
endif()

add_dependencies(
  external_openexr
  external_zlib
)
