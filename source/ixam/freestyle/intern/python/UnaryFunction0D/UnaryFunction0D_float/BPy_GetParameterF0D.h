

#pragma once

#include "../BPy_UnaryFunction0DFloat.h"

#ifdef __cplusplus
extern "C" {
#endif

///////////////////////////////////////////////////////////////////////////////////////////

extern PyTypeObject GetParameterF0D_Type;

#define BPy_GetParameterF0D_Check(v) \
  (PyObject_IsInstance((PyObject *)v, (PyObject *)&GetParameterF0D_Type))

/*---------------------------Python BPy_GetParameterF0D structure definition----------*/
typedef struct {
  BPy_UnaryFunction0DFloat py_uf0D_float;
} BPy_GetParameterF0D;

///////////////////////////////////////////////////////////////////////////////////////////

#ifdef __cplusplus
}
#endif
