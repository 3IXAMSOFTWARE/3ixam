/* SPDX-License-Identifier: GPL-2.0-or-later */


#pragma once

#include "../BPy_BinaryPredicate1D.h"

#ifdef __cplusplus
extern "C" {
#endif

///////////////////////////////////////////////////////////////////////////////////////////

extern PyTypeObject TrueBP1D_Type;

#define BPy_TrueBP1D_Check(v) (PyObject_IsInstance((PyObject *)v, (PyObject *)&TrueBP1D_Type))

/*---------------------------Python BPy_TrueBP1D structure definition----------*/
typedef struct {
  BPy_BinaryPredicate1D py_bp1D;
} BPy_TrueBP1D;

///////////////////////////////////////////////////////////////////////////////////////////

#ifdef __cplusplus
}
#endif
