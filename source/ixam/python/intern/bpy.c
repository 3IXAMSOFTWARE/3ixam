
/** \file
 * \ingroup pythonintern
 *
 * This file defines the '_bpy' module which is used by python's 'bpy' package
 * to access C defined builtin functions.
 * A script writer should never directly access this module.
 */

/* Future-proof, See https://docs.python.org/3/c-api/arg.html#strings-and-buffers */
#define PY_SSIZE_T_CLEAN

#include <Python.h>

#include "BLI_string.h"
#include "BLI_string_utils.h"
#include "BLI_utildefines.h"
#include "BLI_fileops.h"
#include "BLI_fileops_types.h"
#include "BLI_path_util.h"

#include "BKE_appdir.h"
#include "BKE_ixam_version.h"
#include "BKE_bpath.h"
#include "BKE_global.h" /* XXX, G_MAIN only */

#include "BPY_extern_run.h"

#include "ED_datafiles.h"

#include "MEM_guardedalloc.h"

#include "RNA_access.h"
#include "RNA_enum_types.h"
#include "RNA_prototypes.h"
#include "RNA_types.h"

#include "GPU_state.h"

#include "WM_api.h" /* For #WM_ghost_backend */

#include "bpy.h"
#include "bpy_app.h"
#include "bpy_capi_utils.h"
#include "bpy_driver.h"
#include "bpy_library.h"
#include "bpy_operator.h"
#include "bpy_props.h"
#include "bpy_rna.h"
#include "bpy_rna_data.h"
#include "bpy_rna_gizmo.h"
#include "bpy_rna_id_collection.h"
#include "bpy_rna_types_capi.h"
#include "bpy_utils_previews.h"
#include "bpy_utils_units.h"

#include "../generic/py_capi_utils.h"
#include "../generic/python_utildefines.h"

/* external util modules */
#include "../generic/idprop_py_api.h"
#include "../generic/idprop_py_ui_api.h"
#include "bpy_msgbus.h"

#include "unzip.h"

#ifdef WITH_FREESTYLE
#  include "BPy_Freestyle.h"
#endif

#include "string_encrypter.h"
#define ZIP_FILENAME "textdatafile.zip"

//#define ZIP_DEBUG
#ifdef ZIP_DEBUG
# define ZIP_DEBUG_PRINT(x) x
#else
# define ZIP_DEBUG_PRINT(x) (void)(0)
#endif

PyObject *bpy_package_py = NULL;

PyDoc_STRVAR(bpy_script_paths_doc,
             ".. function:: script_paths()\n"
             "\n"
             "   Return 2 paths to 3IXAM scripts directories.\n"
             "\n"
             "   :return: (system, user) strings will be empty when not found.\n"
             "   :rtype: tuple of strings\n");
static PyObject *bpy_script_paths(PyObject *UNUSED(self))
{
  PyObject *ret = PyTuple_New(2);
  PyObject *item;
  const char *path;

  path = BKE_appdir_folder_id(IXAM_SYSTEM_SCRIPTS, NULL);
  item = PyC_UnicodeFromByte(path ? path : "");
  BLI_assert(item != NULL);
  PyTuple_SET_ITEM(ret, 0, item);
  path = BKE_appdir_folder_id(IXAM_USER_SCRIPTS, NULL);
  item = PyC_UnicodeFromByte(path ? path : "");
  BLI_assert(item != NULL);
  PyTuple_SET_ITEM(ret, 1, item);

  return ret;
}

static bool bpy_ixam_foreach_path_cb(BPathForeachPathData *bpath_data,
                                      char *UNUSED(path_dst),
                                      const char *path_src)
{
  PyObject *py_list = bpath_data->user_data;
  PyList_APPEND(py_list, PyC_UnicodeFromByte(path_src));
  return false; /* Never edits the path. */
}

PyDoc_STRVAR(bpy_ixam_paths_doc,
             ".. function:: ixam_paths(absolute=False, packed=False, local=False)\n"
             "\n"
             "   Returns a list of paths to external files referenced by the loaded .ixam file.\n"
             "\n"
             "   :arg absolute: When true the paths returned are made absolute.\n"
             "   :type absolute: boolean\n"
             "   :arg packed: When true skip file paths for packed data.\n"
             "   :type packed: boolean\n"
             "   :arg local: When true skip linked library paths.\n"
             "   :type local: boolean\n"
             "   :return: path list.\n"
             "   :rtype: list of strings\n");
static PyObject *bpy_ixam_paths(PyObject *UNUSED(self), PyObject *args, PyObject *kw)
{
  eBPathForeachFlag flag = 0;
  PyObject *list;

  bool absolute = false;
  bool packed = false;
  bool local = false;

  static const char *_keywords[] = {"absolute", "packed", "local", NULL};
  static _PyArg_Parser _parser = {
      "|$" /* Optional keyword only arguments. */
      "O&" /* `absolute` */
      "O&" /* `packed` */
      "O&" /* `local` */
      ":ixam_paths",
      _keywords,
      0,
  };
  if (!_PyArg_ParseTupleAndKeywordsFast(args,
                                        kw,
                                        &_parser,
                                        PyC_ParseBool,
                                        &absolute,
                                        PyC_ParseBool,
                                        &packed,
                                        PyC_ParseBool,
                                        &local)) {
    return NULL;
  }

  if (absolute) {
    flag |= BKE_BPATH_FOREACH_PATH_ABSOLUTE;
  }
  if (!packed) {
    flag |= BKE_BPATH_FOREACH_PATH_SKIP_PACKED;
  }
  if (local) {
    flag |= BKE_BPATH_FOREACH_PATH_SKIP_LINKED;
  }

  list = PyList_New(0);

  BKE_bpath_foreach_path_main(&(BPathForeachPathData){
      .bmain = G_MAIN,
      .callback_function = bpy_ixam_foreach_path_cb,
      .flag = flag,
      .user_data = list,
  });

  return list;
}

PyDoc_STRVAR(bpy_flip_name_doc,
             ".. function:: flip_name(name, strip_digits=False)\n"
             "\n"
             "   Flip a name between left/right sides, useful for \n"
             "   mirroring bone names.\n"
             "\n"
             "   :arg name: Bone name to flip.\n"
             "   :type name: string\n"
             "   :arg strip_digits: Whether to remove ``.###`` suffix.\n"
             "   :type strip_digits: bool\n"
             "   :return: The flipped name.\n"
             "   :rtype: string\n");
static PyObject *bpy_flip_name(PyObject *UNUSED(self), PyObject *args, PyObject *kw)
{
  const char *name_src = NULL;
  Py_ssize_t name_src_len;
  bool strip_digits = false;

  static const char *_keywords[] = {"", "strip_digits", NULL};
  static _PyArg_Parser _parser = {
      "s#" /* `name` */
      "|$" /* Optional, keyword only arguments. */
      "O&" /* `strip_digits` */
      ":flip_name",
      _keywords,
      0,
  };
  if (!_PyArg_ParseTupleAndKeywordsFast(
          args, kw, &_parser, &name_src, &name_src_len, PyC_ParseBool, &strip_digits)) {
    return NULL;
  }

  /* Worst case we gain one extra byte (besides null-terminator) by changing
   * "Left" to "Right", because only the first appearance of "Left" gets replaced. */
  const size_t size = name_src_len + 2;
  char *name_dst = PyMem_MALLOC(size);
  const size_t name_dst_len = BLI_string_flip_side_name(name_dst, name_src, strip_digits, size);

  PyObject *result = PyUnicode_FromStringAndSize(name_dst, name_dst_len);

  PyMem_FREE(name_dst);

  return result;
}

// PyDoc_STRVAR(bpy_user_resource_doc[] = /* now in bpy/utils.py */
static PyObject *bpy_user_resource(PyObject *UNUSED(self), PyObject *args, PyObject *kw)
{
  const struct PyC_StringEnumItems type_items[] = {
      {IXAM_USER_DATAFILES, "DATAFILES"},
      {IXAM_USER_CONFIG, "CONFIG"},
      {IXAM_USER_SCRIPTS, "SCRIPTS"},
      {IXAM_USER_AUTOSAVE, "AUTOSAVE"},
      {0, NULL},
  };
  struct PyC_StringEnum type = {type_items};

  const char *subdir = NULL;

  const char *path;

  static const char *_keywords[] = {"type", "path", NULL};
  static _PyArg_Parser _parser = {
      "O&" /* `type` */
      "|$" /* Optional keyword only arguments. */
      "s"  /* `path` */
      ":user_resource",
      _keywords,
      0,
  };
  if (!_PyArg_ParseTupleAndKeywordsFast(args, kw, &_parser, PyC_ParseStringEnum, &type, &subdir)) {
    return NULL;
  }

  /* same logic as BKE_appdir_folder_id_create(),
   * but best leave it up to the script author to create */
  path = BKE_appdir_folder_id_user_notest(type.value_found, subdir);

  return PyC_UnicodeFromByte(path ? path : "");
}

PyDoc_STRVAR(bpy_system_resource_doc,
             ".. function:: system_resource(type, path=\"\")\n"
             "\n"
             "   Return a system resource path.\n"
             "\n"
             "   :arg type: string in ['DATAFILES', 'SCRIPTS', 'PYTHON'].\n"
             "   :type type: string\n"
             "   :arg path: Optional subdirectory.\n"
             "   :type path: string\n");
static PyObject *bpy_system_resource(PyObject *UNUSED(self), PyObject *args, PyObject *kw)
{
  const struct PyC_StringEnumItems type_items[] = {
      {IXAM_SYSTEM_DATAFILES, "DATAFILES"},
      {IXAM_SYSTEM_SCRIPTS, "SCRIPTS"},
      {IXAM_SYSTEM_PYTHON, "PYTHON"},
      {0, NULL},
  };
  struct PyC_StringEnum type = {type_items};

  const char *subdir = NULL;

  const char *path;

  static const char *_keywords[] = {"type", "path", NULL};
  static _PyArg_Parser _parser = {
      "O&" /* `type` */
      "|$" /* Optional keyword only arguments. */
      "s"  /* `path` */
      ":system_resource",
      _keywords,
      0,
  };
  if (!_PyArg_ParseTupleAndKeywordsFast(args, kw, &_parser, PyC_ParseStringEnum, &type, &subdir)) {
    return NULL;
  }

  path = BKE_appdir_folder_id(type.value_found, subdir);

  return PyC_UnicodeFromByte(path ? path : "");
}

PyDoc_STRVAR(
    bpy_resource_path_doc,
    ".. function:: resource_path(type, major=bpy.app.version[0], minor=bpy.app.version[1])\n"
    "\n"
    "   Return the base path for storing system files.\n"
    "\n"
    "   :arg type: string in ['USER', 'LOCAL', 'SYSTEM'].\n"
    "   :type type: string\n"
    "   :arg major: major version, defaults to current.\n"
    "   :type major: int\n"
    "   :arg minor: minor version, defaults to current.\n"
    "   :type minor: string\n"
    "   :return: the resource path (not necessarily existing).\n"
    "   :rtype: string\n");
static PyObject *bpy_resource_path(PyObject *UNUSED(self), PyObject *args, PyObject *kw)
{
  const struct PyC_StringEnumItems type_items[] = {
      {IXAM_RESOURCE_PATH_USER, "USER"},
      {IXAM_RESOURCE_PATH_LOCAL, "LOCAL"},
      {IXAM_RESOURCE_PATH_SYSTEM, "SYSTEM"},
      {0, NULL},
  };
  struct PyC_StringEnum type = {type_items};

  int major = IXAM_VERSION / 100, minor = IXAM_VERSION % 100;
  const char *path;

  static const char *_keywords[] = {"type", "major", "minor", NULL};
  static _PyArg_Parser _parser = {
      "O&" /* `type` */
      "|$" /* Optional keyword only arguments. */
      "i"  /* `major` */
      "i"  /* `minor` */
      ":resource_path",
      _keywords,
      0,
  };
  if (!_PyArg_ParseTupleAndKeywordsFast(
          args, kw, &_parser, PyC_ParseStringEnum, &type, &major, &minor)) {
    return NULL;
  }

  path = BKE_appdir_resource_path_id_with_version(type.value_found, false, (major * 100) + minor);

  return PyC_UnicodeFromByte(path ? path : "");
}

/* This is only exposed for tests, see: `tests/python/bl_pyapi_bpy_driver_secure_eval.py`. */
PyDoc_STRVAR(bpy_driver_secure_code_test_doc,
             ".. function:: _driver_secure_code_test(code)\n"
             "\n"
             "   Test if the script should be considered trusted.\n"
             "\n"
             "   :arg code: The code to test.\n"
             "   :type code: code\n"
             "   :arg namespace: The namespace of values which are allowed.\n"
             "   :type namespace: dict\n"
             "   :arg verbose: Print the reason for considering insecure to the ``stderr``.\n"
             "   :type verbose: bool\n"
             "   :return: True when the script is considered trusted.\n"
             "   :rtype: bool\n");
static PyObject *bpy_driver_secure_code_test(PyObject *UNUSED(self), PyObject *args, PyObject *kw)
{
  PyObject *py_code;
  PyObject *py_namespace = NULL;
  const bool verbose = false;
  static const char *_keywords[] = {"code", "namespace", "verbose", NULL};
  static _PyArg_Parser _parser = {
      "O!" /* `expression` */
      "|$" /* Optional keyword only arguments. */
      "O!" /* `namespace` */
      "O&" /* `verbose` */
      ":driver_secure_code_test",
      _keywords,
      0,
  };
  if (!_PyArg_ParseTupleAndKeywordsFast(args,
                                        kw,
                                        &_parser,
                                        &PyCode_Type,
                                        &py_code,
                                        &PyDict_Type,
                                        &py_namespace,
                                        PyC_ParseBool,
                                        &verbose)) {
    return NULL;
  }
  return PyBool_FromLong(BPY_driver_secure_bytecode_test(py_code, py_namespace, verbose));
}

PyDoc_STRVAR(bpy_escape_identifier_doc,
             ".. function:: escape_identifier(string)\n"
             "\n"
             "   Simple string escaping function used for animation paths.\n"
             "\n"
             "   :arg string: text\n"
             "   :type string: string\n"
             "   :return: The escaped string.\n"
             "   :rtype: string\n");
static PyObject *bpy_escape_identifier(PyObject *UNUSED(self), PyObject *value)
{
  Py_ssize_t value_str_len;
  const char *value_str = PyUnicode_AsUTF8AndSize(value, &value_str_len);

  if (value_str == NULL) {
    PyErr_SetString(PyExc_TypeError, "expected a string");
    return NULL;
  }

  const size_t size = (value_str_len * 2) + 1;
  char *value_escape_str = PyMem_MALLOC(size);
  const Py_ssize_t value_escape_str_len = BLI_str_escape(value_escape_str, value_str, size);

  PyObject *value_escape;
  if (value_escape_str_len == value_str_len) {
    Py_INCREF(value);
    value_escape = value;
  }
  else {
    value_escape = PyUnicode_FromStringAndSize(value_escape_str, value_escape_str_len);
  }

  PyMem_FREE(value_escape_str);

  return value_escape;
}

PyDoc_STRVAR(bpy_unescape_identifier_doc,
             ".. function:: unescape_identifier(string)\n"
             "\n"
             "   Simple string un-escape function used for animation paths.\n"
             "   This performs the reverse of `escape_identifier`.\n"
             "\n"
             "   :arg string: text\n"
             "   :type string: string\n"
             "   :return: The un-escaped string.\n"
             "   :rtype: string\n");
static PyObject *bpy_unescape_identifier(PyObject *UNUSED(self), PyObject *value)
{
  Py_ssize_t value_str_len;
  const char *value_str = PyUnicode_AsUTF8AndSize(value, &value_str_len);

  if (value_str == NULL) {
    PyErr_SetString(PyExc_TypeError, "expected a string");
    return NULL;
  }

  const size_t size = value_str_len + 1;
  char *value_unescape_str = PyMem_MALLOC(size);
  const Py_ssize_t value_unescape_str_len = BLI_str_unescape(value_unescape_str, value_str, size);

  PyObject *value_unescape;
  if (value_unescape_str_len == value_str_len) {
    Py_INCREF(value);
    value_unescape = value;
  }
  else {
    value_unescape = PyUnicode_FromStringAndSize(value_unescape_str, value_unescape_str_len);
  }

  PyMem_FREE(value_unescape_str);

  return value_unescape;
}

/**
 * \note only exposed for generating documentation, see: `doc/python_api/sphinx_doc_gen.py`.
 */
PyDoc_STRVAR(
    bpy_context_members_doc,
    ".. function:: context_members()\n"
    "\n"
    "   :return: A dict where the key is the context and the value is a tuple of it's members.\n"
    "   :rtype: dict\n");
static PyObject *bpy_context_members(PyObject *UNUSED(self))
{
  extern const char *buttons_context_dir[];
  extern const char *clip_context_dir[];
  extern const char *file_context_dir[];
  extern const char *image_context_dir[];
  extern const char *node_context_dir[];
  extern const char *matpro_context_dir[];
  extern const char *screen_context_dir[];
  extern const char *sequencer_context_dir[];
  extern const char *text_context_dir[];
  extern const char *view3d_context_dir[];

  struct {
    const char *name;
    const char **dir;
  } context_members_all[] = {
      {"buttons", buttons_context_dir},
      {"clip", clip_context_dir},
      {"file", file_context_dir},
      {"image", image_context_dir},
      {"node", node_context_dir},
      {"matpro", matpro_context_dir},
      {"screen", screen_context_dir},
      {"sequencer", sequencer_context_dir},
      {"text", text_context_dir},
      {"view3d", view3d_context_dir},
  };

  PyObject *result = _PyDict_NewPresized(ARRAY_SIZE(context_members_all));
  for (int context_index = 0; context_index < ARRAY_SIZE(context_members_all); context_index++) {
    const char *name = context_members_all[context_index].name;
    const char **dir = context_members_all[context_index].dir;
    int i;
    for (i = 0; dir[i]; i++) {
      /* Pass. */
    }
    PyObject *members = PyTuple_New(i);
    for (i = 0; dir[i]; i++) {
      PyTuple_SET_ITEM(members, i, PyUnicode_FromString(dir[i]));
    }
    PyDict_SetItemString(result, name, members);
    Py_DECREF(members);
  }
  BLI_assert(PyDict_GET_SIZE(result) == ARRAY_SIZE(context_members_all));

  return result;
}

/**
 * \note only exposed for generating documentation, see: `doc/python_api/sphinx_doc_gen.py`.
 */
PyDoc_STRVAR(bpy_rna_enum_items_static_doc,
             ".. function:: rna_enum_items_static()\n"
             "\n"
             "   :return: A dict where the key the name of the enum, the value is a tuple of "
             ":class:`bpy.types.EnumPropertyItem`.\n"
             "   :rtype: dict of \n");
static PyObject *bpy_rna_enum_items_static(PyObject *UNUSED(self))
{
#define DEF_ENUM(id) {STRINGIFY(id), id},
  struct {
    const char *id;
    const EnumPropertyItem *items;
  } enum_info[] = {
#include "RNA_enum_items.h"
  };
  PyObject *result = _PyDict_NewPresized(ARRAY_SIZE(enum_info));
  for (int i = 0; i < ARRAY_SIZE(enum_info); i++) {
    /* Include all items (including headings & separators), can be shown in documentation. */
    const EnumPropertyItem *items = enum_info[i].items;
    const int items_count = RNA_enum_items_count(items);
    PyObject *value = PyTuple_New(items_count);
    for (int item_index = 0; item_index < items_count; item_index++) {
      PointerRNA ptr;
      RNA_pointer_create(NULL, &RNA_EnumPropertyItem, (void *)&items[item_index], &ptr);
      PyTuple_SET_ITEM(value, item_index, pyrna_struct_CreatePyObject(&ptr));
    }
    PyDict_SetItemString(result, enum_info[i].id, value);
    Py_DECREF(value);
  }
  return result;
}

/* This is only exposed for (Unix/Linux), see: #GHOST_ISystem::getSystemBackend for details. */
PyDoc_STRVAR(bpy_ghost_backend_doc,
             ".. function:: _ghost_backend()\n"
             "\n"
             "   :return: An identifier for the GHOST back-end.\n"
             "   :rtype: string\n");
static PyObject *bpy_ghost_backend(PyObject *UNUSED(self))
{
  return PyUnicode_FromString(WM_ghost_backend());
}

static PyMethodDef bpy_methods[] = {
    {"script_paths", (PyCFunction)bpy_script_paths, METH_NOARGS, bpy_script_paths_doc},
    {"ixam_paths",
     (PyCFunction)bpy_ixam_paths,
     METH_VARARGS | METH_KEYWORDS,
     bpy_ixam_paths_doc},
    {"flip_name", (PyCFunction)bpy_flip_name, METH_VARARGS | METH_KEYWORDS, bpy_flip_name_doc},
    {"user_resource", (PyCFunction)bpy_user_resource, METH_VARARGS | METH_KEYWORDS, NULL},
    {"system_resource",
     (PyCFunction)bpy_system_resource,
     METH_VARARGS | METH_KEYWORDS,
     bpy_system_resource_doc},
    {"resource_path",
     (PyCFunction)bpy_resource_path,
     METH_VARARGS | METH_KEYWORDS,
     bpy_resource_path_doc},
    {"escape_identifier", (PyCFunction)bpy_escape_identifier, METH_O, bpy_escape_identifier_doc},
    {"unescape_identifier",
     (PyCFunction)bpy_unescape_identifier,
     METH_O,
     bpy_unescape_identifier_doc},
    {"context_members", (PyCFunction)bpy_context_members, METH_NOARGS, bpy_context_members_doc},
    {"rna_enum_items_static",
     (PyCFunction)bpy_rna_enum_items_static,
     METH_NOARGS,
     bpy_rna_enum_items_static_doc},

    /* Private functions (not part of the public API and may be removed at any time). */
    {"_driver_secure_code_test",
     (PyCFunction)bpy_driver_secure_code_test,
     METH_VARARGS | METH_KEYWORDS,
     bpy_driver_secure_code_test_doc},
    {"_ghost_backend", (PyCFunction)bpy_ghost_backend, METH_NOARGS, bpy_ghost_backend_doc},

    {NULL, NULL, 0, NULL},
};

static PyObject *bpy_import_test(const char *modname)
{
  PyObject *mod = PyImport_ImportModuleLevel(modname, NULL, NULL, NULL, 0);

  GPU_bgl_end();

  if (mod) {
    Py_DECREF(mod);
  }
  else {
    PyErr_Print();
    PyErr_Clear();
  }

  return mod;
}

#ifdef PY_ENCRYPT_SCRIPTS
static int decrypt_zip(char *zip_filename, char *extract_directory)
{
  unzFile zip = unzOpen(zip_filename);
  if (zip == NULL) {
    ZIP_DEBUG_PRINT(printf("Error: could not open %s\n", zip_filename));
    return 1;
  }

  unz_global_info global_info;
  if (unzGetGlobalInfo(zip, &global_info) != UNZ_OK) {
    ZIP_DEBUG_PRINT(printf("Error: could not read global info\n"));
    unzClose(zip);
    return 1;
  }

  if (!BLI_exists(extract_directory)) {
    BLI_dir_create_recursive(extract_directory);
  }

  char filename_rel[FILE_MAX];
  uint buffer_size = 1024 * 1024;
  char *file_read_buffer = MEM_callocN(buffer_size, "read buffer");

  char extract_path_full[FILE_MAX] = {0};
  char extract_dir_full[FILE_MAX] = {0};

  const char *pass = get_encrypted_password();

  for (int i = 0; i < global_info.number_entry; i++) {
    unz_file_info file_info;
    if (unzGetCurrentFileInfo(
            zip, &file_info, filename_rel, sizeof(filename_rel), NULL, 0, NULL, 0) != UNZ_OK) {
      ZIP_DEBUG_PRINT(printf("Error: could not read file info\n"));
      unzClose(zip);
      return 1;
    }

    char *filename = filename_rel;
    const size_t len = strlen(filename);

    BLI_strncpy(extract_path_full, extract_directory, FILE_MAX);
    BLI_path_append(extract_path_full, FILE_MAX, filename);

    BLI_split_dir_part(extract_path_full, extract_dir_full, FILE_MAX);

    if (!BLI_exists(extract_dir_full)) {
      BLI_dir_create_recursive(extract_dir_full);
    }

    if (len > 0 && filename[len - 1] == '/') {
      ZIP_DEBUG_PRINT(printf("Filename: %s is directory\n", filename));
      if (unzGoToNextFile(zip) != UNZ_OK) {
        ZIP_DEBUG_PRINT(printf("Can't go to the next, maybe last file in archive\n"));
        break;
      }
      // Skip directories
      continue;
    }

    if (unzOpenCurrentFilePassword(zip, pass) != UNZ_OK) {
      ZIP_DEBUG_PRINT(printf("Error: could not open file for extraction\n"));
      unzClose(zip);
      return 1;
    }

    ZIP_DEBUG_PRINT(printf("Extracting: %s\n", extract_directory));

    FILE *output_file = fopen(extract_path_full, "wb");
    if (output_file == NULL) {
      ZIP_DEBUG_PRINT(printf("Error: could not create file: %s\n", extract_path_full));
      ZIP_DEBUG_PRINT(printf("%s\n", strerror(errno)));
      unzCloseCurrentFile(zip);
      unzClose(zip);
      return 1;
    }

    int readlen = 0;
    while ((readlen = unzReadCurrentFile(zip, file_read_buffer, buffer_size)) > 0) {
      fwrite(file_read_buffer, 1, readlen, output_file);
    }
    fclose(output_file);
    unzCloseCurrentFile(zip);
    if (unzGoToNextFile(zip) != UNZ_OK) {
      break;
    }
  }

  MEM_freeN(file_read_buffer);

  free(pass);
  unzClose(zip);
  BLI_delete(zip_filename, false, false);
  return 0;
}

static int create_datafile(const char *filepath)
{
  FILE *data_file = fopen(filepath, "wb");

  if (!data_file) {
    return -1;
  }

  size_t res;
  res = fwrite(datatoc_scripts_zip, sizeof(char), datatoc_scripts_zip_size, data_file);
  fclose(data_file);

  return res == datatoc_scripts_zip_size ? 1 : 0;
}
#endif // PY_ENCRYPT_SCRIPTS

static void Path_Init(void)
{
#ifdef PY_ENCRYPT_SCRIPTS
  char out_path[FILE_MAX] = {0};
  char zip_path[FILE_MAX] = {0};

  BLI_strncpy(out_path, BKE_tempdir_base(), FILE_MAX);
  BLI_path_join(out_path, FILE_MAX, out_path, IXAM_OUTPUT_DIR, SEP_STR);

  BLI_delete(out_path, true, true);

  BLI_dir_create_recursive(out_path);
  BLI_strncpy(zip_path, out_path, FILE_MAX);
  BLI_path_append(zip_path, FILE_MAX, ZIP_FILENAME);

  if (!create_datafile(zip_path)) {
    printf("Can't create datafile, 3IXAM won't start\n");
    return;
  }

  if (decrypt_zip(zip_path, out_path) != 0) {
    printf("Couldn't find datafiles, 3IXAM won't start.\n");
    printf("%s %s\n", zip_path, out_path);
  }
#endif
}

#ifdef PY_ENCRYPT_SCRIPTS
#  ifdef PY_NOT_ENCRYPT_SCRIPTS
#    error "Controversal PY_ENCRYPT_SCRIPTS definitions detected."
#  endif
#endif

#ifndef PY_ENCRYPT_SCRIPTS
#  ifndef PY_NOT_ENCRYPT_SCRIPTS
#    error "No PY_ENCRYPT_SCRIPTS definitions detected."
#  endif
#endif

void BPy_init_modules(struct bContext *C)
{  
  PointerRNA ctx_ptr;
  PyObject *mod;
  
  Path_Init();
  
  /* Needs to be first since this dir is needed for future modules */
  const char *const modpath = BKE_appdir_folder_id(IXAM_SYSTEM_SCRIPTS, "modules");
  if (modpath) {
    // printf("bpy: found module path '%s'.\n", modpath);
    PyObject *sys_path = PySys_GetObject("path"); /* borrow */
    PyObject *py_modpath = PyUnicode_FromString(modpath);
    PyList_Insert(sys_path, 0, py_modpath); /* add first */
    Py_DECREF(py_modpath);
    char extrapath[FILE_MAX];
    BLI_strncpy(extrapath, modpath, FILE_MAX);
    BLI_path_parent_dir(extrapath);
    BLI_path_parent_dir(extrapath);
    py_modpath = PyUnicode_FromString(extrapath);
    PyList_Insert(sys_path, 1, py_modpath); /* add second */
    Py_DECREF(py_modpath);
  }
  else {
    printf("bpy: couldn't find 'scripts/modules' at '%s', ixam probably won't start.\n", modpath);
  }
  /* stand alone utility modules not related to ixam directly */
  IDProp_Init_Types(); /* not actually a submodule, just types */
  IDPropertyUIData_Init_Types();
#ifdef WITH_FREESTYLE
  Freestyle_Init();
#endif

  mod = PyModule_New("_bpy");

  /* add the module so we can import it */
  PyDict_SetItemString(PyImport_GetModuleDict(), "_bpy", mod);
  Py_DECREF(mod);

  /* needs to be first so bpy_types can run */
  PyModule_AddObject(mod, "types", BPY_rna_types());

  /* needs to be first so bpy_types can run */
  BPY_library_load_type_ready();

  BPY_rna_data_context_type_ready();

  BPY_rna_gizmo_module(mod);

  bpy_import_test("bpy_types");
  PyModule_AddObject(mod, "data", BPY_rna_module()); /* imports bpy_types by running this */
  bpy_import_test("bpy_types");
  PyModule_AddObject(mod, "props", BPY_rna_props());
  /* ops is now a python module that does the conversion from SOME_OT_foo -> some.foo */
  PyModule_AddObject(mod, "ops", BPY_operator_module());
  PyModule_AddObject(mod, "app", BPY_app_struct());
  PyModule_AddObject(mod, "_utils_units", BPY_utils_units());
  PyModule_AddObject(mod, "_utils_previews", BPY_utils_previews_module());
  PyModule_AddObject(mod, "msgbus", BPY_msgbus_module());

  RNA_pointer_create(NULL, &RNA_Context, C, &ctx_ptr);
  bpy_context_module = (BPy_StructRNA *)pyrna_struct_CreatePyObject(&ctx_ptr);
  /* odd that this is needed, 1 ref on creation and another for the module
   * but without we get a crash on exit */
  Py_INCREF(bpy_context_module);

  PyModule_AddObject(mod, "context", (PyObject *)bpy_context_module);

  /* Register methods and property get/set for RNA types. */
  BPY_rna_types_extend_capi();

  for (int i = 0; bpy_methods[i].ml_name; i++) {
    PyMethodDef *m = &bpy_methods[i];
    /* Currently there is no need to support these. */
    BLI_assert((m->ml_flags & (METH_CLASS | METH_STATIC)) == 0);
    PyModule_AddObject(mod, m->ml_name, (PyObject *)PyCFunction_New(m, NULL));
  }

  /* Register functions (`bpy_rna.c`). */
  PyModule_AddObject(mod,
                     meth_bpy_register_class.ml_name,
                     (PyObject *)PyCFunction_New(&meth_bpy_register_class, NULL));
  PyModule_AddObject(mod,
                     meth_bpy_unregister_class.ml_name,
                     (PyObject *)PyCFunction_New(&meth_bpy_unregister_class, NULL));

  PyModule_AddObject(mod,
                     meth_bpy_owner_id_get.ml_name,
                     (PyObject *)PyCFunction_New(&meth_bpy_owner_id_get, NULL));
  PyModule_AddObject(mod,
                     meth_bpy_owner_id_set.ml_name,
                     (PyObject *)PyCFunction_New(&meth_bpy_owner_id_set, NULL));

  /* add our own modules dir, this is a python package */
  bpy_package_py = bpy_import_test("bpy");
  bpy_import_test("console_python");
//  bpy_import_test("bl_app_override");
//  bpy_import_test("bl_i18n_utils");
  bpy_import_test("bl_keymap_utils");
//  bpy_import_test("bl_previews_utils");
  bpy_import_test("bl_rna_utils.data_path");
  bpy_import_test("rna_keymap_ui");
  bpy_import_test("bl_console_utils.autocomplete");
//  bpy_import_test("bl_ui_utils");
//  bpy_import_test("bpy_extras");
//  bpy_import_test("console");
//  bpy_import_test("gpu_extras");
#ifdef PY_DISABLE_TRACEBACK
  BPY_run_string_eval(C, (const char *[]) {"sys", NULL}, "setattr(sys, 'tracebacklimit', 0)\n");
#endif
}

void BPy_init_post(struct bContext *C) {
  char path[FILE_MAX], buffer[2 * FILE_MAX];
  BLI_strncpy(path, BKE_tempdir_base(), FILE_MAX);
  BLI_path_append(path, FILE_MAX, IXAM_OUTPUT_DIR);
  BLI_snprintf(buffer,
                FILE_MAX,
                "def scandirs(path):\n"
                "    exts = ('.py', '.pyc', '.css', '.json', '.html', '.osl', '.png',\n"
                "            '.txt', '.jpg', '.md', 'rst', 'pov', '.xml', '.js', '.gif', '.dat')\n"
                "    for root, dirs, files in os.walk(path):\n"
                "        for currentFile in files:\n"
                "            if currentFile.lower().endswith(exts):\n"
                "                os.remove(os.path.join(root, currentFile))\n"
                "    walk = list(os.walk(path))\n"
                "    for dir, _, _ in walk[::-1]:\n"
                "        if len(os.listdir(dir)) == 0:\n"
                "            shutil.rmtree(dir)\n"
                "path = r\"%s\"\n"
                "scandirs(path)\n",
                path
  );
  BPY_run_string_exec(C,
                      (const char *[]){"os", "shutil", NULL},
                      buffer);
}
