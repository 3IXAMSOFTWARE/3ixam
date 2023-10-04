
set(BOOST_ADDRESS_MODEL 64)
if(IXAM_PLATFORM_ARM)
  set(BOOST_ARCHITECTURE arm)
else()
  set(BOOST_ARCHITECTURE x86)
endif()

if(WIN32)
  if(MSVC_VERSION GREATER_EQUAL 1920) # 2019
    set(BOOST_TOOLSET toolset=msvc-14.2)
    set(BOOST_COMPILER_STRING -vc142)
  else() # 2017
    set(BOOST_TOOLSET toolset=msvc-14.1)
    set(BOOST_COMPILER_STRING -vc141)
  endif()
endif()

set(DEFAULT_BOOST_FLAGS
  -DBoost_COMPILER:STRING=${BOOST_COMPILER_STRING}
  -DBoost_USE_MULTITHREADED=ON
  -DBoost_USE_STATIC_LIBS=ON
  -DBoost_USE_STATIC_RUNTIME=OFF
  -DBOOST_ROOT=${LIBDIR}/boost
  -DBoost_NO_SYSTEM_PATHS=ON
  -DBoost_NO_BOOST_CMAKE=ON
  -DBoost_ADDITIONAL_VERSIONS=${BOOST_VERSION_SHORT}
  -DBOOST_LIBRARYDIR=${LIBDIR}/boost/lib/
)
