/* SPDX-License-Identifier: GPL-2.0-or-later */


#include "BPy_ExternalContourUP1D.h"

#ifdef __cplusplus
extern "C" {
#endif

using namespace Freestyle;

///////////////////////////////////////////////////////////////////////////////////////////

//------------------------INSTANCE METHODS ----------------------------------

static char ExternalContourUP1D___doc__[] =
    "Class hierarchy: :class:`freestyle.types.UnaryPredicate1D` > :class:`ExternalContourUP1D`\n"
    "\n"
    ".. method:: __call__(inter)\n"
    "\n"
    "   Returns true if the Interface1D is an external contour.  An\n"
    "   Interface1D is an external contour if it is bordered by no shape on\n"
    "   one of its sides.\n"
    "\n"
    "   :arg inter: An Interface1D object.\n"
    "   :type inter: :class:`freestyle.types.Interface1D`\n"
    "   :return: True if the Interface1D is an external contour, false\n"
    "      otherwise.\n"
    "   :rtype: bool\n";

static int ExternalContourUP1D___init__(BPy_ExternalContourUP1D *self,
                                        PyObject *args,
                                        PyObject *kwds)
{
  static const char *kwlist[] = {nullptr};

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "", (char **)kwlist)) {
    return -1;
  }
  self->py_up1D.up1D = new Predicates1D::ExternalContourUP1D();
  return 0;
}

/*-----------------------BPy_ExternalContourUP1D type definition ------------------------------*/

PyTypeObject ExternalContourUP1D_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0) "ExternalContourUP1D", /* tp_name */
    sizeof(BPy_ExternalContourUP1D),                         /* tp_basicsize */
    0,                                                       /* tp_itemsize */
    nullptr,                                                 /* tp_dealloc */
    0,                                                       /* tp_vectorcall_offset */
    nullptr,                                                 /* tp_getattr */
    nullptr,                                                 /* tp_setattr */
    nullptr,                                                 /* tp_reserved */
    nullptr,                                                 /* tp_repr */
    nullptr,                                                 /* tp_as_number */
    nullptr,                                                 /* tp_as_sequence */
    nullptr,                                                 /* tp_as_mapping */
    nullptr,                                                 /* tp_hash */
    nullptr,                                                 /* tp_call */
    nullptr,                                                 /* tp_str */
    nullptr,                                                 /* tp_getattro */
    nullptr,                                                 /* tp_setattro */
    nullptr,                                                 /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,                /* tp_flags */
    ExternalContourUP1D___doc__,                             /* tp_doc */
    nullptr,                                                 /* tp_traverse */
    nullptr,                                                 /* tp_clear */
    nullptr,                                                 /* tp_richcompare */
    0,                                                       /* tp_weaklistoffset */
    nullptr,                                                 /* tp_iter */
    nullptr,                                                 /* tp_iternext */
    nullptr,                                                 /* tp_methods */
    nullptr,                                                 /* tp_members */
    nullptr,                                                 /* tp_getset */
    &UnaryPredicate1D_Type,                                  /* tp_base */
    nullptr,                                                 /* tp_dict */
    nullptr,                                                 /* tp_descr_get */
    nullptr,                                                 /* tp_descr_set */
    0,                                                       /* tp_dictoffset */
    (initproc)ExternalContourUP1D___init__,                  /* tp_init */
    nullptr,                                                 /* tp_alloc */
    nullptr,                                                 /* tp_new */
};

///////////////////////////////////////////////////////////////////////////////////////////

#ifdef __cplusplus
}
#endif
