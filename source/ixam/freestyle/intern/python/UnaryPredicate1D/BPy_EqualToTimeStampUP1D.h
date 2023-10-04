

#pragma once

#include "../BPy_UnaryPredicate1D.h"

#ifdef __cplusplus
extern "C" {
#endif

///////////////////////////////////////////////////////////////////////////////////////////

extern PyTypeObject EqualToTimeStampUP1D_Type;

#define BPy_EqualToTimeStampUP1D_Check(v) \
  (PyObject_IsInstance((PyObject *)v, (PyObject *)&EqualToTimeStampUP1D_Type))

/*---------------------------Python BPy_EqualToTimeStampUP1D structure definition----------*/
typedef struct {
  BPy_UnaryPredicate1D py_up1D;
} BPy_EqualToTimeStampUP1D;

///////////////////////////////////////////////////////////////////////////////////////////

#ifdef __cplusplus
}
#endif
