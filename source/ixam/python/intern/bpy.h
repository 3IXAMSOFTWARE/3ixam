/* SPDX-License-Identifier: GPL-2.0-or-later */


#pragma once

#ifdef __cplusplus
extern "C" {
#endif

struct bContext;

/** Creates the `bpy` module and adds it to `sys.modules` for importing. */
void BPy_init_modules(struct bContext *C);
void BPy_init_post(struct bContext *C);

extern PyObject *bpy_package_py;

/* bpy_interface_atexit.c */

void BPY_atexit_register(void);
void BPY_atexit_unregister(void);

extern struct CLG_LogRef *BPY_LOG_CONTEXT;
extern struct CLG_LogRef *BPY_LOG_RNA;
extern struct CLG_LogRef *BPY_LOG_INTERFACE;

#ifdef __cplusplus
}
#endif
