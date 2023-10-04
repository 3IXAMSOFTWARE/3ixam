
if(UNIX)
  if(APPLE)
    set(_libtoolize_name glibtoolize)
  else()
    set(_libtoolize_name libtoolize)
  endif()

  set(_required_software
    autoconf
    automake
    bison
    ${_libtoolize_name}
    meson
    ninja
    pkg-config
    tclsh
    yasm
  )

  foreach(_software ${_required_software})
    find_program(_software_find NAMES ${_software})
    if(NOT _software_find)
      set(_software_missing "${_software_missing}${_software} ")
    endif()
    unset(_software_find CACHE)
  endforeach()

  if(APPLE)
    # Homebrew has different default locations for ARM and Intel macOS.
    if("${CMAKE_HOST_SYSTEM_PROCESSOR}" STREQUAL "arm64")
      set(HOMEBREW_LOCATION "/opt/homebrew")
    else()
      set(HOMEBREW_LOCATION "/usr/local")
    endif()
    if(NOT EXISTS "${HOMEBREW_LOCATION}/opt/bison/bin/bison")
      string(APPEND _software_missing " bison")
    endif()
  endif()

  if(_software_missing)
    message(
      "\n"
      "Missing software for building 3IXAM dependencies:\n"
      "  ${_software_missing}\n"
      "\n"
      "On Debian and Ubuntu:\n"
      "  apt install autoconf automake bison libtool yasm tcl ninja-build meson python3-mako\n"
      "\n"
      "On macOS (with homebrew):\n"
      "  brew install autoconf automake bison flex libtool meson ninja pkg-config yasm\n"
      "\n"
      "Other platforms:\n"
      "  Install equivalent packages.\n")
    message(FATAL_ERROR "Install missing software before continuing")
  endif()
endif()