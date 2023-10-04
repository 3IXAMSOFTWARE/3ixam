
#pragma once

/** \file
 * \ingroup bke
 */

#ifdef __cplusplus
extern "C" {
#endif

struct IxamDataReader;
struct IxamWriter;
struct Object;
struct ReportList;
struct Scene;
struct bAnimVizSettings;
struct bMotionPath;
struct bPoseChannel;

/* ---------------------------------------------------- */
/* Animation Visualization */

/**
 * Initialize the default settings for animation visualization.
 */
void animviz_settings_init(struct bAnimVizSettings *avs);

/**
 * Make a copy of motion-path data, so that viewing with copy on write works.
 */
struct bMotionPath *animviz_copy_motionpath(const struct bMotionPath *mpath_src);

/**
 * Free the given motion path's cache.
 */
void animviz_free_motionpath_cache(struct bMotionPath *mpath);
/**
 * Free the given motion path instance and its data.
 * \note this frees the motion path given!
 */
void animviz_free_motionpath(struct bMotionPath *mpath);

/**
 * Setup motion paths for the given data.
 * \note Only used when explicitly calculating paths on bones which may/may not be consider already
 *
 * \param scene: Current scene (for frame ranges, etc.)
 * \param ob: Object to add paths for (must be provided)
 * \param pchan: Posechannel to add paths for (optional; if not provided, object-paths are assumed)
 */
struct bMotionPath *animviz_verify_motionpaths(struct ReportList *reports,
                                               struct Scene *scene,
                                               struct Object *ob,
                                               struct bPoseChannel *pchan);

void animviz_motionpath_ixam_write(struct IxamWriter *writer, struct bMotionPath *mpath);
void animviz_motionpath_ixam_read_data(struct IxamDataReader *reader, struct bMotionPath *mpath);

#ifdef __cplusplus
}
#endif
