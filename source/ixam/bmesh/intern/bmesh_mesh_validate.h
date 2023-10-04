

#pragma once

/** \file
 * \ingroup bmesh
 */

/**
 * Check of this #BMesh is valid,
 * this function can be slow since its intended to help with debugging.
 *
 * \return true when the mesh is valid.
 */
bool BM_mesh_validate(BMesh *bm);
