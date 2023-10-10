/* SPDX-License-Identifier: GPL-2.0-or-later */

#pragma once

#include "../BPy_StrokeShader.h"

#ifdef __cplusplus
extern "C" {
#endif

///////////////////////////////////////////////////////////////////////////////////////////

#include <Python.h>

extern PyTypeObject IxamTextureShader_Type;

#define BPy_IxamTextureShader_Check(v) \
  (PyObject_IsInstance((PyObject *)v, (PyObject *)&IxamTextureShader_Type))

/*---------------------------Python BPy_IxamTextureShader structure definition-----------*/
typedef struct {
  BPy_StrokeShader py_ss;
} BPy_IxamTextureShader;

///////////////////////////////////////////////////////////////////////////////////////////

#ifdef __cplusplus
}
#endif
