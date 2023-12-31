/* SPDX-License-Identifier: GPL-2.0-or-later */


#include "BPy_GetOccludeeF1D.h"

#include "../../../view_map/Functions1D.h"
#include "../../BPy_Convert.h"
#include "../../BPy_IntegrationType.h"

#ifdef __cplusplus
extern "C" {
#endif

using namespace Freestyle;

///////////////////////////////////////////////////////////////////////////////////////////

//------------------------INSTANCE METHODS ----------------------------------

static char GetOccludeeF1D___doc__[] =
    "Class hierarchy: :class:`freestyle.types.UnaryFunction1D` > "
    ":class:`freestyle.types.UnaryFunction1DVectorViewShape` > :class:`GetOccludeeF1D`\n"
    "\n"
    ".. method:: __init__()\n"
    "\n"
    "   Builds a GetOccludeeF1D object.\n"
    "\n"
    ".. method:: __call__(inter)\n"
    "\n"
    "   Returns a list of occluded shapes covered by this Interface1D.\n"
    "\n"
    "   :arg inter: An Interface1D object.\n"
    "   :type inter: :class:`freestyle.types.Interface1D`\n"
    "   :return: A list of occluded shapes covered by the Interface1D.\n"
    "   :rtype: list of :class:`freestyle.types.ViewShape` objects\n";

static int GetOccludeeF1D___init__(BPy_GetOccludeeF1D *self, PyObject *args, PyObject *kwds)
{
  static const char *kwlist[] = {nullptr};

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "", (char **)kwlist)) {
    return -1;
  }
  self->py_uf1D_vectorviewshape.uf1D_vectorviewshape = new Functions1D::GetOccludeeF1D();
  return 0;
}

/*-----------------------BPy_GetOccludeeF1D type definition ------------------------------*/

PyTypeObject GetOccludeeF1D_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0) "GetOccludeeF1D", /* tp_name */
    sizeof(BPy_GetOccludeeF1D),                         /* tp_basicsize */
    0,                                                  /* tp_itemsize */
    nullptr,                                            /* tp_dealloc */
    0,                                                  /* tp_vectorcall_offset */
    nullptr,                                            /* tp_getattr */
    nullptr,                                            /* tp_setattr */
    nullptr,                                            /* tp_reserved */
    nullptr,                                            /* tp_repr */
    nullptr,                                            /* tp_as_number */
    nullptr,                                            /* tp_as_sequence */
    nullptr,                                            /* tp_as_mapping */
    nullptr,                                            /* tp_hash */
    nullptr,                                            /* tp_call */
    nullptr,                                            /* tp_str */
    nullptr,                                            /* tp_getattro */
    nullptr,                                            /* tp_setattro */
    nullptr,                                            /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,           /* tp_flags */
    GetOccludeeF1D___doc__,                             /* tp_doc */
    nullptr,                                            /* tp_traverse */
    nullptr,                                            /* tp_clear */
    nullptr,                                            /* tp_richcompare */
    0,                                                  /* tp_weaklistoffset */
    nullptr,                                            /* tp_iter */
    nullptr,                                            /* tp_iternext */
    nullptr,                                            /* tp_methods */
    nullptr,                                            /* tp_members */
    nullptr,                                            /* tp_getset */
    &UnaryFunction1DVectorViewShape_Type,               /* tp_base */
    nullptr,                                            /* tp_dict */
    nullptr,                                            /* tp_descr_get */
    nullptr,                                            /* tp_descr_set */
    0,                                                  /* tp_dictoffset */
    (initproc)GetOccludeeF1D___init__,                  /* tp_init */
    nullptr,                                            /* tp_alloc */
    nullptr,                                            /* tp_new */
};

///////////////////////////////////////////////////////////////////////////////////////////

#ifdef __cplusplus
}
#endif
