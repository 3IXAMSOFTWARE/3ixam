# Detect precompiled library directory
if(NOT DEFINED LIBDIR)
  # Path to a locally compiled libraries.
  set(LIBDIR_NAME ${CMAKE_SYSTEM_NAME}_${CMAKE_SYSTEM_PROCESSOR})
  string(TOLOWER ${LIBDIR_NAME} LIBDIR_NAME)
  set(LIBDIR_NATIVE_ABI ${CMAKE_SOURCE_DIR}/../lib/${LIBDIR_NAME})

  # Path to precompiled libraries with known CentOS 7 ABI.
  set(LIBDIR_CENTOS7_ABI ${CMAKE_SOURCE_DIR}/../lib/linux_centos7_x86_64)

  # Choose the best suitable libraries.
  if(EXISTS ${LIBDIR_NATIVE_ABI})
    set(LIBDIR ${LIBDIR_NATIVE_ABI})
    set(WITH_LIBC_MALLOC_HOOK_WORKAROUND True)
  elseif(EXISTS ${LIBDIR_CENTOS7_ABI})
    set(LIBDIR ${LIBDIR_CENTOS7_ABI})
    set(WITH_CXX11_ABI OFF)
    if(WITH_MEM_JEMALLOC)
      # jemalloc provides malloc hooks.
      set(WITH_LIBC_MALLOC_HOOK_WORKAROUND False)
    else()
      set(WITH_LIBC_MALLOC_HOOK_WORKAROUND True)
    endif()
  endif()

  # Avoid namespace pollustion.
  unset(LIBDIR_NATIVE_ABI)
  unset(LIBDIR_CENTOS7_ABI)
endif()