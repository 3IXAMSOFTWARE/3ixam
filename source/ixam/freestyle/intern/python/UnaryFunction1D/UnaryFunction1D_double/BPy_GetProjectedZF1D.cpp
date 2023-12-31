/* SPDX-License-Identifier: GPL-2.0-or-later */


#include "BPy_GetProjectedZF1D.h"

#include "../../../view_map/Functions1D.h"
#include "../../BPy_Convert.h"
#include "../../BPy_IntegrationType.h"

#ifdef __cplusplus
extern "C" {
#endif

using namespace Freestyle;

///////////////////////////////////////////////////////////////////////////////////////////

//------------------------INSTANCE METHODS ----------------------------------

static char GetProjectedZF1D___doc__[] =
    "Class hierarchy: :class:`freestyle.types.UnaryFunction1D` > "
    ":class:`freestyle.types.UnaryFunction1DDouble` > :class:`GetProjectedZF1D`\n"
    "\n"
    ".. method:: __init__(integration_type=IntegrationType.MEAN)\n"
    "\n"
    "   Builds a GetProjectedZF1D object.\n"
    "\n"
    "   :arg integration_type: The integration method used to compute a single value\n"
    "      from a set of values. \n"
    "   :type integration_type: :class:`freestyle.types.IntegrationType`\n"
    "\n"
    ".. method:: __call__(inter)\n"
    "\n"
    "   Returns the projected Z 3D coordinate of an Interface1D.\n"
    "\n"
    "   :arg inter: An Interface1D object.\n"
    "   :type inter: :class:`freestyle.types.Interface1D`\n"
    "   :return: The projected Z 3D coordinate of an Interface1D.\n"
    "   :rtype: float\n";

static int GetProjectedZF1D___init__(BPy_GetProjectedZF1D *self, PyObject *args, PyObject *kwds)
{
  static const char *kwlist[] = {"integration_type", nullptr};
  PyObject *obj = nullptr;

  if (!PyArg_ParseTupleAndKeywords(
          args, kwds, "|O!", (char **)kwlist, &IntegrationType_Type, &obj)) {
    return -1;
  }
  IntegrationType t = (obj) ? IntegrationType_from_BPy_IntegrationType(obj) : MEAN;
  self->py_uf1D_double.uf1D_double = new Functions1D::GetProjectedZF1D(t);
  return 0;
}

/*-----------------------BPy_GetProjectedZF1D type definition ------------------------------*/

PyTypeObject GetProjectedZF1D_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0) "GetProjectedZF1D", /* tp_name */
    sizeof(BPy_GetProjectedZF1D),                         /* tp_basicsize */
    0,                                                    /* tp_itemsize */
    nullptr,                                              /* tp_dealloc */
    0,                                                    /* tp_vectorcall_offset */
    nullptr,                                              /* tp_getattr */
    nullptr,                                              /* tp_setattr */
    nullptr,                                              /* tp_reserved */
    nullptr,                                              /* tp_repr */
    nullptr,                                              /* tp_as_number */
    nullptr,                                              /* tp_as_sequence */
    nullptr,                                              /* tp_as_mapping */
    nullptr,                                              /* tp_hash */
    nullptr,                                              /* tp_call */
    nullptr,                                              /* tp_str */
    nullptr,                                              /* tp_getattro */
    nullptr,                                              /* tp_setattro */
    nullptr,                                              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,             /* tp_flags */
    GetProjectedZF1D___doc__,                             /* tp_doc */
    nullptr,                                              /* tp_traverse */
    nullptr,                                              /* tp_clear */
    nullptr,                                              /* tp_richcompare */
    0,                                                    /* tp_weaklistoffset */
    nullptr,                                              /* tp_iter */
    nullptr,                                              /* tp_iternext */
    nullptr,                                              /* tp_methods */
    nullptr,                                              /* tp_members */
    nullptr,                                              /* tp_getset */
    &UnaryFunction1DDouble_Type,                          /* tp_base */
    nullptr,                                              /* tp_dict */
    nullptr,                                              /* tp_descr_get */
    nullptr,                                              /* tp_descr_set */
    0,                                                    /* tp_dictoffset */
    (initproc)GetProjectedZF1D___init__,                  /* tp_init */
    nullptr,                                              /* tp_alloc */
    nullptr,                                              /* tp_new */
};

///////////////////////////////////////////////////////////////////////////////////////////

#ifdef __cplusplus
}
#endif
