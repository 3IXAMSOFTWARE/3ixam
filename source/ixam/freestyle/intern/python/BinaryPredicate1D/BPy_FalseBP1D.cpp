

#include "BPy_FalseBP1D.h"

#ifdef __cplusplus
extern "C" {
#endif

using namespace Freestyle;

///////////////////////////////////////////////////////////////////////////////////////////

//------------------------INSTANCE METHODS ----------------------------------

static char FalseBP1D___doc__[] =
    "Class hierarchy: :class:`freestyle.types.BinaryPredicate1D` > :class:`FalseBP1D`\n"
    "\n"
    ".. method:: __call__(inter1, inter2)\n"
    "\n"
    "   Always returns false.\n"
    "\n"
    "   :arg inter1: The first Interface1D object.\n"
    "   :type inter1: :class:`freestyle.types.Interface1D`\n"
    "   :arg inter2: The second Interface1D object.\n"
    "   :type inter2: :class:`freestyle.types.Interface1D`\n"
    "   :return: False.\n"
    "   :rtype: bool\n";

static int FalseBP1D___init__(BPy_FalseBP1D *self, PyObject *args, PyObject *kwds)
{
  static const char *kwlist[] = {nullptr};

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "", (char **)kwlist)) {
    return -1;
  }
  self->py_bp1D.bp1D = new Predicates1D::FalseBP1D();
  return 0;
}

/*-----------------------BPy_FalseBP1D type definition ------------------------------*/
PyTypeObject FalseBP1D_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0) "FalseBP1D", /* tp_name */
    sizeof(BPy_FalseBP1D),                         /* tp_basicsize */
    0,                                             /* tp_itemsize */
    nullptr,                                       /* tp_dealloc */
    0,                                             /* tp_vectorcall_offset */
    nullptr,                                       /* tp_getattr */
    nullptr,                                       /* tp_setattr */
    nullptr,                                       /* tp_reserved */
    nullptr,                                       /* tp_repr */
    nullptr,                                       /* tp_as_number */
    nullptr,                                       /* tp_as_sequence */
    nullptr,                                       /* tp_as_mapping */
    nullptr,                                       /* tp_hash */
    nullptr,                                       /* tp_call */
    nullptr,                                       /* tp_str */
    nullptr,                                       /* tp_getattro */
    nullptr,                                       /* tp_setattro */
    nullptr,                                       /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,      /* tp_flags */
    FalseBP1D___doc__,                             /* tp_doc */
    nullptr,                                       /* tp_traverse */
    nullptr,                                       /* tp_clear */
    nullptr,                                       /* tp_richcompare */
    0,                                             /* tp_weaklistoffset */
    nullptr,                                       /* tp_iter */
    nullptr,                                       /* tp_iternext */
    nullptr,                                       /* tp_methods */
    nullptr,                                       /* tp_members */
    nullptr,                                       /* tp_getset */
    &BinaryPredicate1D_Type,                       /* tp_base */
    nullptr,                                       /* tp_dict */
    nullptr,                                       /* tp_descr_get */
    nullptr,                                       /* tp_descr_set */
    0,                                             /* tp_dictoffset */
    (initproc)FalseBP1D___init__,                  /* tp_init */
    nullptr,                                       /* tp_alloc */
    nullptr,                                       /* tp_new */
};

///////////////////////////////////////////////////////////////////////////////////////////

#ifdef __cplusplus
}
#endif