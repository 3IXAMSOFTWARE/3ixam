/* SPDX-License-Identifier: GPL-2.0-or-later */


#pragma once

#include "../BPy_StrokeShader.h"

#ifdef __cplusplus
extern "C" {
#endif

///////////////////////////////////////////////////////////////////////////////////////////

#include <Python.h>

extern PyTypeObject StrokeTextureStepShader_Type;

#define BPy_StrokeTextureStepShader_Check(v) \
  (PyObject_IsInstance((PyObject *)v, (PyObject *)&StrokeTextureStepShader_Type))

/*---------------------------Python BPy_StrokeTextureStepShader structure definition----------*/
typedef struct {
  BPy_StrokeShader py_ss;
} BPy_StrokeTextureStepShader;

///////////////////////////////////////////////////////////////////////////////////////////

#ifdef __cplusplus
}
#endif
