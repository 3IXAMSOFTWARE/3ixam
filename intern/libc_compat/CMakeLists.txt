# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2015 Blender Foundation. All rights reserved.


set(INC
  .
)

set(INC_SYS
)

set(SRC
  libc_compat.c
)

set(LIB
)

add_c_flag(-ffast-math)

ixam_add_lib(bf_intern_libc_compat "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

if(WITH_LIBC_MALLOC_HOOK_WORKAROUND)
  target_compile_definitions(bf_intern_libc_compat
    PRIVATE WITH_LIBC_MALLOC_HOOK_WORKAROUND
  )
endif()
