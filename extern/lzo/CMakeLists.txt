# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2006 Blender Foundation. All rights reserved.


remove_strict_flags()

set(INC

)

set(INC_SYS

)

set(SRC
  minilzo/minilzo.c

  minilzo/lzoconf.h
  minilzo/lzodefs.h
  minilzo/minilzo.h
)

set(LIB
)

ixam_add_lib(extern_minilzo "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
