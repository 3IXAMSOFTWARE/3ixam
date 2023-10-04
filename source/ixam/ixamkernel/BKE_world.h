
#pragma once

/** \file
 * \ingroup bke
 */

#ifdef __cplusplus
extern "C" {
#endif

struct Depsgraph;
struct Main;
struct World;

struct World *BKE_world_add(struct Main *bmain, const char *name);
void BKE_world_eval(struct Depsgraph *depsgraph, struct World *world);

#ifdef __cplusplus
}
#endif
