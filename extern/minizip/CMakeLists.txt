

set(INC
  .
)

set(INC_SYS

)

set(SRC
	crypt.h
	ioapi.c
	ioapi.h
	miniunz.c
	minizip.c
	mztools.c
	mztools.h
	unzip.c
	zip.c
)

if(WIN32)
	list(APPEND SRC 
	iowin32.h
	iowin32.c
	)
endif()

set(LIB
)

ixam_add_lib(extern_minizip "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")