

#pragma once

#include "../BPy_StrokeShader.h"

#ifdef __cplusplus
extern "C" {
#endif

///////////////////////////////////////////////////////////////////////////////////////////

extern PyTypeObject CalligraphicShader_Type;

#define BPy_CalligraphicShader_Check(v) \
  (PyObject_IsInstance((PyObject *)v, (PyObject *)&CalligraphicShader_Type)

/*---------------------------Python BPy_CalligraphicShader structure definition----------*/
typedef struct {
  BPy_StrokeShader py_ss;
} BPy_CalligraphicShader;

///////////////////////////////////////////////////////////////////////////////////////////

#ifdef __cplusplus
}
#endif
