
set(INC
  .
  ../ixamkernel
  ../ixamlib
  ../ixamtranslation
  ../gpu
  ../imbuf
  ../makesdna
  ../makesrna
  ../../../intern/guardedalloc
)

set(INC_SYS
  ${FREETYPE_INCLUDE_DIRS}
)

set(SRC
  intern/blf.c
  intern/blf_default.c
  intern/blf_dir.c
  intern/blf_font.c
  intern/blf_font_default.c
  intern/blf_glyph.c
  intern/blf_thumbs.c
  intern/blf_util.c

  BLF_api.h
  intern/blf_internal.h
  intern/blf_internal_types.h
)

set(LIB
  bf_gpu
  bf_intern_guardedalloc

  ${FREETYPE_LIBRARIES} ${BROTLI_LIBRARIES}
)

if(WIN32)
  list(APPEND SRC
    intern/blf_font_win32_compat.c
  )
endif()

if(WITH_PYTHON)
  add_definitions(-DWITH_PYTHON)
  list(APPEND INC
    ../python
  )
endif()


ixam_add_lib(bf_ixamfont "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
