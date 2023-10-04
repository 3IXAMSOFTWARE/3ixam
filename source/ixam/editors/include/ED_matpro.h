

/** \file
 * \ingroup editors
 */

#pragma once


#ifdef __cplusplus
extern "C" {
#endif

struct ID;
struct Main;
struct Scene;
struct ScrArea;
struct SpaceMatPro;
struct Tex;
struct View2D;
struct bContext;
struct bNode;
struct bNodeSocket;
struct bNodeSocketType;
struct bNodeTree;
struct bNodeTreeType;
struct bNodeType;

typedef enum {
  NODE_TOP_MP = 1,
  NODE_BOTTOM_MP = 2,
  NODE_LEFT_MP = 4,
  NODE_RIGHT_MP = 8,
} NodeBorderMatPro;

#define MATPRO_GRID_STEP_SIZE U.widget_unit /* Based on the grid nodes snap to. */
#define MATPRO_EDGE_PAN_INSIDE_PAD 2
#define MATPRO_EDGE_PAN_OUTSIDE_PAD 0 /* Disable clamping for node panning, use whole screen. */
#define MATPRO_EDGE_PAN_SPEED_RAMP 1
#define MATPRO_EDGE_PAN_MAX_SPEED 26 /* In UI units per second, slower than default. */
#define MATPRO_EDGE_PAN_DELAY 0.5f
#define MATPRO_EDGE_PAN_ZOOM_INFLUENCE 0.5f

/* space_matpro.cc */

void ED_matpro_cursor_location_get(const struct SpaceMatPro *smatpro, float value[2]);
void ED_matpro_cursor_location_set(struct SpaceMatPro *smatpro, const float value[2]);

int ED_matpro_tree_path_length(struct SpaceMatPro *smatpro);
void ED_matpro_tree_path_get(struct SpaceMatPro *smatpro, char *value);

void ED_matpro_tree_start(struct SpaceMatPro *smatpro,
                          struct bNodeTree *ntree,
                          struct ID *id,
                          struct ID *from);
void ED_matpro_tree_push(struct SpaceMatPro *smatpro,
                         struct bNodeTree *ntree,
                         struct bNode *gnode);
void ED_matpro_tree_pop(struct SpaceMatPro *smatpro);
int ED_matpro_tree_depth(struct SpaceMatPro *smatpro);
struct bNodeTree *ED_matpro_tree_get(struct SpaceMatPro *smatpro, int level);

void ED_matpro_set_active_viewer_key(struct SpaceMatPro *smatpro);

/* drawnode.cc */

void ED_matpro_init_butfuncs(void);
void ED_matpro_sample_set(const float col[4]);
void ED_matpro_draw_snap(
    struct View2D *v2d, const float cent[2], float size, NodeBorderMatPro border, unsigned int pos);

/* node_draw.cc */

/**
 * Draw a single node socket at default size.
 * \note this is only called from external code, internally #node_socket_draw_nested() is used for
 *       optimized drawing of multiple/all sockets of a node.
 */
void ED_matpro_socket_draw(struct bNodeSocket *sock,
                           const struct rcti *rect,
                           float color[4],
                           float scale);
void ED_matpro_tree_update(const struct bContext *C);
void ED_matpro_tag_update_id(struct ID *id);

float ED_matpro_grid_size(void);

/* node_edit.cc */

void ED_matpro_set_tree_type(struct SpaceMatPro *smatpro, struct bNodeTreeType *typeinfo);
bool ED_matpro_is_compositor(struct SpaceMatPro *smatpro);
bool ED_matpro_is_shader(struct SpaceMatPro *smatpro);
bool ED_matpro_is_texture(struct SpaceMatPro *smatpro);
bool ED_matpro_is_geometry(struct SpaceMatPro *smatpro);

/**
 * Assumes nothing being done in ntree yet, sets the default in/out node.
 * Called from shading buttons or header.
 */
void ED_matpro_shader_default(const struct bContext *C, struct ID *id);
/**
 * Assumes nothing being done in ntree yet, sets the default in/out node.
 * Called from shading buttons or header.
 */
void ED_matpro_composit_default(const struct bContext *C, struct Scene *scene);
/**
 * Assumes nothing being done in ntree yet, sets the default in/out node.
 * Called from shading buttons or header.
 */
void ED_matpro_texture_default(const struct bContext *C, struct Tex *tex);
void ED_matpro_post_apply_transform(struct bContext *C, struct bNodeTree *ntree);
void ED_matpro_set_active(struct Main *bmain,
                          struct SpaceMatPro *smatpro,
                          struct bNodeTree *ntree,
                          struct bNode *node,
                          bool *r_active_texture_changed);

/**
 * Call after one or more node trees have been changed and tagged accordingly.
 *
 * This function will make sure that other parts of 3IXAM update accordingly. For example, if the
 * node group interface changed, parent node groups have to be updated as well.
 *
 * Additionally, this will send notifiers and tag the depsgraph based on the changes. Depsgraph
 * relation updates have to be triggered by the caller.
 *
 * \param C: Context if available. This can be null.
 * \param bmain: Main whose data-blocks should be updated based on the changes.
 * \param ntree: Under some circumstances the caller knows that only one node tree has
 *   changed since the last update. In this case the function may be able to skip scanning #bmain
 *   for other things that have to be changed. It may still scan #bmain if the interface of the
 *   node tree has changed.
 */
void ED_matpro_tree_propagate_change(const struct bContext *C,
                                     struct Main *bmain,
                                     struct bNodeTree *ntree);

/**
 * \param scene_owner: is the owner of the job,
 * we don't use it for anything else currently so could also be a void pointer,
 * but for now keep it an 'Scene' for consistency.
 *
 * \note only call from spaces `refresh` callbacks, not direct! - use with care.
 */
void ED_matpro_composite_job(const struct bContext *C,
                             struct bNodeTree *nodetree,
                             struct Scene *scene_owner);

/* node_ops.cc */

void ED_operatormacros_matpro(void);

/* node_view.cc */

/**
 * Returns mouse position in image space.
 */
bool ED_space_matpro_get_position(struct Main *bmain,
                                  struct SpaceMatPro *smatpro,
                                  struct ARegion *region,
                                  const int mval[2],
                                  float fpos[2]);
/**
 * Returns color in linear space, matching #ED_space_image_color_sample().
 * And here we've got recursion in the comments tips...
 */
bool ED_space_matpro_color_sample(struct Main *bmain,
                                  struct SpaceMatPro *smatpro,
                                  struct ARegion *region,
                                  const int mval[2],
                                  float r_col[3]);

#ifdef __cplusplus
}
#endif

#ifdef __cplusplus

/* node_relationships.cc */

namespace ixam::ed::space_matpro {

void node_insert_on_link_flags_set(SpaceMatPro &smatpro, const ARegion &region);
/**
 * Assumes link with #NODE_LINKFLAG_HILITE set.
 */
void node_insert_on_link_flags(Main &bmain, SpaceMatPro &smatpro);
void node_insert_on_link_flags_clear(bNodeTree &node_tree);

}  // namespace ixam::ed::space_matpro

#endif
