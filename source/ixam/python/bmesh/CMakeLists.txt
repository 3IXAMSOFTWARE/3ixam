# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# ***** END GPL LICENSE BLOCK *****

set(INC
  .
  ../../ixamkernel
  ../../ixamlib
  ../../bmesh
  ../../depsgraph
  ../../makesdna
  ../../../../intern/guardedalloc
)

set(INC_SYS
  ${PYTHON_INCLUDE_DIRS}
)

set(SRC
  bmesh_py_api.c
  bmesh_py_geometry.c
  bmesh_py_ops.c
  bmesh_py_ops_call.c
  bmesh_py_types.c
  bmesh_py_types_customdata.c
  bmesh_py_types_meshdata.c
  bmesh_py_types_select.c
  bmesh_py_utils.c

  bmesh_py_api.h
  bmesh_py_geometry.h
  bmesh_py_ops.h
  bmesh_py_ops_call.h
  bmesh_py_types.h
  bmesh_py_types_customdata.h
  bmesh_py_types_meshdata.h
  bmesh_py_types_select.h
  bmesh_py_utils.h
)

set(LIB
  bf_ixamkernel
  bf_ixamlib
  bf_python_mathutils

  ${PYTHON_LINKFLAGS}
  ${PYTHON_LIBRARIES}
)

if(WITH_FREESTYLE)
  add_definitions(-DWITH_FREESTYLE)
endif()

if(WITH_GMP)
  add_definitions(-DWITH_GMP)
endif()

ixam_add_lib(bf_python_bmesh "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
