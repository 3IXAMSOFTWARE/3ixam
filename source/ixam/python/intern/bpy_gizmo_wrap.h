/* SPDX-License-Identifier: GPL-2.0-or-later */


#pragma once

struct wmGizmoGroupType;
struct wmGizmoType;

#ifdef __cplusplus
extern "C" {
#endif

/* Exposed to RNA/WM API. */
void BPY_RNA_gizmo_wrapper(struct wmGizmoType *gzt, void *userdata);
void BPY_RNA_gizmogroup_wrapper(struct wmGizmoGroupType *gzgt, void *userdata);

#ifdef __cplusplus
}
#endif
