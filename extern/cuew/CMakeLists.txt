# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2006 Blender Foundation. All rights reserved.


set(INC
  .
  include
)

set(INC_SYS

)

set(SRC
  src/cuew.c

  include/cuew.h
)

set(LIB
)

ixam_add_lib(extern_cuew "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
