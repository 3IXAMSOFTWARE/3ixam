# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2013 Blender Foundation. All rights reserved.


set(INC
  .
)

set(INC_SYS

)

set(SRC
  wcwidth.c

  wcwidth.h
)

set(LIB
)

ixam_add_lib(extern_wcwidth "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
