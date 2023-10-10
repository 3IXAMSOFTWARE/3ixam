/* SPDX-License-Identifier: GPL-2.0-or-later */

#include "BPy_IxamTextureShader.h"

#include "../../stroke/BasicStrokeShaders.h"

#ifdef __cplusplus
extern "C" {
#endif

#include "../../../../python/generic/py_capi_utils.h"

using namespace Freestyle;

///////////////////////////////////////////////////////////////////////////////////////////

//------------------------INSTANCE METHODS ----------------------------------

static char IxamTextureShader___doc__[] =
    "Class hierarchy: :class:`freestyle.types.StrokeShader` > :class:`IxamTextureShader`\n"
    "\n"
    "[Texture shader]\n"
    "\n"
    ".. method:: __init__(texture)\n"
    "\n"
    "   Builds a IxamTextureShader object.\n"
    "\n"
    "   :arg texture: A line style texture slot or a shader node tree to define\n"
    "       a set of textures.\n"
    "   :type texture: :class:`bpy.types.LineStyleTextureSlot` or\n"
    "       :class:`bpy.types.ShaderNodeTree`\n"
    "\n"
    ".. method:: shade(stroke)\n"
    "\n"
    "   Assigns a ixam texture slot to the stroke  shading in order to\n"
    "   simulate marks.\n"
    "\n"
    "   :arg stroke: A Stroke object.\n"
    "   :type stroke: :class:`freestyle.types.Stroke`\n";

static int IxamTextureShader___init__(BPy_IxamTextureShader *self,
                                         PyObject *args,
                                         PyObject *kwds)
{
  static const char *kwlist[] = {"texture", nullptr};
  PyObject *obj;
  MTex *_mtex;
  bNodeTree *_nodetree;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", (char **)kwlist, &obj)) {
    return -1;
  }
  _mtex = (MTex *)PyC_RNA_AsPointer(obj, "LineStyleTextureSlot");
  if (_mtex) {
    self->py_ss.ss = new StrokeShaders::IxamTextureShader(_mtex);
    return 0;
  }
  PyErr_Clear();
  _nodetree = (bNodeTree *)PyC_RNA_AsPointer(obj, "ShaderNodeTree");
  if (_nodetree) {
    self->py_ss.ss = new StrokeShaders::IxamTextureShader(_nodetree);
    return 0;
  }
  PyErr_Format(PyExc_TypeError,
               "expected either 'LineStyleTextureSlot' or 'ShaderNodeTree', "
               "found '%.200s' instead",
               Py_TYPE(obj)->tp_name);
  return -1;
}

/*-----------------------BPy_IxamTextureShader type definition ------------------------------*/

PyTypeObject IxamTextureShader_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0) "IxamTextureShader", /* tp_name */
    sizeof(BPy_IxamTextureShader),                         /* tp_basicsize */
    0,                                                        /* tp_itemsize */
    nullptr,                                                  /* tp_dealloc */
    0,                                                        /* tp_vectorcall_offset */
    nullptr,                                                  /* tp_getattr */
    nullptr,                                                  /* tp_setattr */
    nullptr,                                                  /* tp_reserved */
    nullptr,                                                  /* tp_repr */
    nullptr,                                                  /* tp_as_number */
    nullptr,                                                  /* tp_as_sequence */
    nullptr,                                                  /* tp_as_mapping */
    nullptr,                                                  /* tp_hash */
    nullptr,                                                  /* tp_call */
    nullptr,                                                  /* tp_str */
    nullptr,                                                  /* tp_getattro */
    nullptr,                                                  /* tp_setattro */
    nullptr,                                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,                 /* tp_flags */
    IxamTextureShader___doc__,                             /* tp_doc */
    nullptr,                                                  /* tp_traverse */
    nullptr,                                                  /* tp_clear */
    nullptr,                                                  /* tp_richcompare */
    0,                                                        /* tp_weaklistoffset */
    nullptr,                                                  /* tp_iter */
    nullptr,                                                  /* tp_iternext */
    nullptr,                                                  /* tp_methods */
    nullptr,                                                  /* tp_members */
    nullptr,                                                  /* tp_getset */
    &StrokeShader_Type,                                       /* tp_base */
    nullptr,                                                  /* tp_dict */
    nullptr,                                                  /* tp_descr_get */
    nullptr,                                                  /* tp_descr_set */
    0,                                                        /* tp_dictoffset */
    (initproc)IxamTextureShader___init__,                  /* tp_init */
    nullptr,                                                  /* tp_alloc */
    nullptr,                                                  /* tp_new */
};

///////////////////////////////////////////////////////////////////////////////////////////

#ifdef __cplusplus
}
#endif
