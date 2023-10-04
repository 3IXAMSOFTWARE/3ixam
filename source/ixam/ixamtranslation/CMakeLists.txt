
set(INC
  .
  ../ixamkernel
  ../ixamlib
  ../imbuf
  ../makesdna
  ../makesrna
  ../../../intern/guardedalloc
  ../../../intern/locale
)

set(INC_SYS
)

set(SRC
  intern/blt_lang.c
  intern/blt_translation.c

  BLT_lang.h
  BLT_translation.h
)

set(LIB
  bf_ixamkernel
  bf_ixamlib
)

if(WITH_INTERNATIONAL)
  add_definitions(-DWITH_INTERNATIONAL)
  list(APPEND LIB
    bf_intern_locale
  )
endif()

if(WITH_PYTHON)
  add_definitions(-DWITH_PYTHON)
  list(APPEND INC
    ../python
  )
endif()

if(WIN32 OR APPLE)
  if(WITH_INPUT_IME)
    add_definitions(-DWITH_INPUT_IME)
  endif()
endif()

ixam_add_lib(bf_ixamtranslation "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

if(WITH_INTERNATIONAL)
  add_subdirectory(msgfmt)
endif()
