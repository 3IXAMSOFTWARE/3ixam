

#pragma once

bool BM_mesh_intersect_edges(
    BMesh *bm, char hflag, float dist, bool split_faces, GHash *r_targetmap);
