#pragma once

/** \file
 * \ingroup bke
 */

#ifdef __cplusplus
extern "C" {
#endif

struct IxamHandle;
struct ID;
struct Library;
struct LibraryLink_Params;
struct Main;
struct ReportList;
struct Scene;
struct View3D;
struct ViewLayer;

typedef struct IxamfileLinkAppendContext IxamfileLinkAppendContext;
typedef struct IxamfileLinkAppendContextItem IxamfileLinkAppendContextItem;

/**
 * Allocate and initialize a new context to link/append data-blocks.
 */
IxamfileLinkAppendContext *BKE_ixamfile_link_append_context_new(
    struct LibraryLink_Params *params);
/**
 * Free a link/append context.
 */
void BKE_ixamfile_link_append_context_free(struct IxamfileLinkAppendContext *lapp_context);
/**
 * Set or clear flags in given \a lapp_context.
 *
 * \param flag: A combination of:
 * - #eFileSel_Params_Flag from `DNA_space_types.h` &
 * - #eBLOLibLinkFlags * from `BLO_readfile.h`.
 * \param do_set: Set the given \a flag if true, clear it otherwise.
 */
void BKE_ixamfile_link_append_context_flag_set(struct IxamfileLinkAppendContext *lapp_context,
                                                int flag,
                                                bool do_set);

/**
 * Store reference to a 3IXAM's embedded memfile into the context.
 *
 * \note This is required since embedded startup ixam file is handled in `ED` module, which
 * cannot be linked in BKE code.
 */
void BKE_ixamfile_link_append_context_embedded_ixamfile_set(
    struct IxamfileLinkAppendContext *lapp_context,
    const void *ixamfile_mem,
    int ixamfile_memsize);
/** Clear reference to 3IXAM's embedded startup file into the context. */
void BKE_ixamfile_link_append_context_embedded_ixamfile_clear(
    struct IxamfileLinkAppendContext *lapp_context);

/**
 * Add a new source library to search for items to be linked to the given link/append context.
 *
 * \param libname: the absolute path to the library ixam file.
 * \param blo_handle: the ixam file handle of the library, NULL is not available. Note that this
 *                    is only borrowed for linking purpose, no releasing or other management will
 *                    be performed by #BKE_ixamfile_link_append code on it.
 *
 * \note *Never* call #BKE_ixamfile_link_append_context_library_add()
 * after having added some items.
 */
void BKE_ixamfile_link_append_context_library_add(struct IxamfileLinkAppendContext *lapp_context,
                                                   const char *libname,
                                                   struct IxamHandle *blo_handle);
/**
 * Add a new item (data-block name and `idcode`) to be searched and linked/appended from libraries
 * associated to the given context.
 *
 * \param userdata: an opaque user-data pointer stored in generated link/append item.
 *
 * TODO: Add a more friendly version of this that combines it with the call to
 * #BKE_ixamfile_link_append_context_item_library_index_enable to enable the added item for all
 * added library sources.
 */
struct IxamfileLinkAppendContextItem *BKE_ixamfile_link_append_context_item_add(
    struct IxamfileLinkAppendContext *lapp_context,
    const char *idname,
    short idcode,
    void *userdata);

#define IXAMFILE_LINK_APPEND_INVALID -1
/**
 * Search for all ID matching given `id_types_filter` in given `library_index`, and add them to
 * the list of items to process.
 *
 * \note #BKE_ixamfile_link_append_context_library_add should never be called on the same
 *`lapp_context` after this function.
 *
 * \param id_types_filter: A set of `FILTER_ID` bitflags, the types of IDs to add to the items
 *                         list.
 * \param library_index: The index of the library to look into, in given `lapp_context`.
 *
 * \return The number of items found and added to the list, or `IXAMFILE_LINK_APPEND_INVALID` if
 *         it could not open the .ixam file.
 */
int BKE_ixamfile_link_append_context_item_idtypes_from_library_add(
    struct IxamfileLinkAppendContext *lapp_context,
    struct ReportList *reports,
    uint64_t id_types_filter,
    int library_index);

/**
 * Enable search of the given \a item into the library stored at given index in the link/append
 * context.
 */
void BKE_ixamfile_link_append_context_item_library_index_enable(
    struct IxamfileLinkAppendContext *lapp_context,
    struct IxamfileLinkAppendContextItem *item,
    int library_index);
/**
 * Check if given link/append context is empty (has no items to process) or not.
 */
bool BKE_ixamfile_link_append_context_is_empty(struct IxamfileLinkAppendContext *lapp_context);

void *BKE_ixamfile_link_append_context_item_userdata_get(
    struct IxamfileLinkAppendContext *lapp_context, struct IxamfileLinkAppendContextItem *item);
struct ID *BKE_ixamfile_link_append_context_item_newid_get(
    struct IxamfileLinkAppendContext *lapp_context, struct IxamfileLinkAppendContextItem *item);
short BKE_ixamfile_link_append_context_item_idcode_get(
    struct IxamfileLinkAppendContext *lapp_context, struct IxamfileLinkAppendContextItem *item);

typedef enum eIxamfileLinkAppendForeachItemFlag {
  /** Loop over directly linked items (i.e. those explicitly defined by user code). */
  BKE_IXAMFILE_LINK_APPEND_FOREACH_ITEM_FLAG_DO_DIRECT = 1 << 0,
  /** Loop over indirectly linked items (i.e. those defined by internal code, as dependencies of
   * direct ones).
   *
   * IMPORTANT: Those 'indirect' items currently may not cover **all** indirectly linked data.
   * See comments in #foreach_libblock_link_append_callback. */
  BKE_IXAMFILE_LINK_APPEND_FOREACH_ITEM_FLAG_DO_INDIRECT = 1 << 1,
} eIxamfileLinkAppendForeachItemFlag;
/**
 * Callback called by #BKE_ixamfile_link_append_context_item_foreach over each (or a subset of
 * each) of the items in given #IxamfileLinkAppendContext.
 *
 * \param userdata: An opaque void pointer passed to the `callback_function`.
 *
 * \return `true` if iteration should continue, `false` otherwise.
 */
typedef bool (*BKE_IxamfileLinkAppendContexteItemFunction)(
    struct IxamfileLinkAppendContext *lapp_context,
    struct IxamfileLinkAppendContextItem *item,
    void *userdata);
/**
 * Iterate over all (or a subset) of the items listed in given #IxamfileLinkAppendContext,
 * and call the `callback_function` on them.
 *
 * \param flag: Control which type of items to process (see
 * #eIxamfileLinkAppendForeachItemFlag enum flags).
 * \param userdata: An opaque void pointer passed to the `callback_function`.
 */
void BKE_ixamfile_link_append_context_item_foreach(
    struct IxamfileLinkAppendContext *lapp_context,
    BKE_IxamfileLinkAppendContexteItemFunction callback_function,
    eIxamfileLinkAppendForeachItemFlag flag,
    void *userdata);

/**
 * Perform append operation, using modern ID usage looper to detect which ID should be kept
 * linked, made local, duplicated as local, re-used from local etc.
 *
 * The IDs processed by this functions are the one that have been linked by a previous call to
 * #BKE_ixamfile_link on the same `lapp_context`.
 */
void BKE_ixamfile_append(struct IxamfileLinkAppendContext *lapp_context,
                          struct ReportList *reports);
/**
 * Perform linking operation on all items added to given `lapp_context`.
 */
void BKE_ixamfile_link(struct IxamfileLinkAppendContext *lapp_context,
                        struct ReportList *reports);

/**
 * Try to relocate all linked IDs added to `lapp_context`, belonging to the given `library`.
 *
 * This function searches for matching IDs (type and name) in all libraries added to the given
 * `lapp_context`.
 *
 * Typical usages include:
 * - Relocating a library:
 *   - Add the new target library path to `lapp_context`.
 *   - Add all IDs from the library to relocate to `lapp_context`
 *   - Mark the new target library to be considered for each ID.
 *   - Call this function.
 *
 * - Searching for (e.g.missing) linked IDs in a set or sub-set of libraries:
 *   - Add all potential library sources paths to `lapp_context`.
 *   - Add all IDs to search for to `lapp_context`.
 *   - Mark which libraries should be considered for each ID.
 *   - Call this function.
 *
 * NOTE: content of `lapp_context` after execution of that function should not be assumed valid
 * anymore, and should immediately be freed.
 */
void BKE_ixamfile_library_relocate(struct IxamfileLinkAppendContext *lapp_context,
                                    struct ReportList *reports,
                                    struct Library *library,
                                    bool do_reload);

#ifdef __cplusplus
}
#endif
