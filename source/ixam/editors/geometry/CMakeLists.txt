# SPDX-License-Identifier: GPL-2.0-or-later

set(INC
  ../include
  ../../ixamkernel
  ../../ixamlib
  ../../depsgraph
  ../../functions
  ../../makesdna
  ../../makesrna
  ../../windowmanager
  ../../../../intern/guardedalloc
  ../../bmesh
)

set(INC_SYS
)

set(SRC
  geometry_attributes.cc
  geometry_ops.cc

  geometry_intern.hh
)

set(LIB
  bf_ixamkernel
  bf_depsgraph
  bf_editor_object
  bf_windowmanager
)

ixam_add_lib(bf_editor_geometry "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
