/* SPDX-License-Identifier: GPL-2.0-or-later */

#pragma once

/** \file
 * \ingroup bke
 */

#ifdef __cplusplus
extern "C" {
#endif

struct IxamFileData;
struct IxamFileReadParams;
struct IxamFileReadReport;
struct ID;
struct Main;
struct MemFile;
struct ReportList;
struct UserDef;
struct bContext;

/**
 * Shared setup function that makes the data from `bfd` into the current ixam file,
 * replacing the contents of #G.main.
 * This uses the bfd #BKE_ixamfile_read and similarly named functions.
 *
 * This is done in a separate step so the caller may perform actions after it is known the file
 * loaded correctly but before the file replaces the existing ixam file contents.
 */
void BKE_ixamfile_read_setup_ex(struct bContext *C,
                                 struct IxamFileData *bfd,
                                 const struct IxamFileReadParams *params,
                                 struct IxamFileReadReport *reports,
                                 /* Extra args. */
                                 bool startup_update_defaults,
                                 const char *startup_app_template);

void BKE_ixamfile_read_setup(struct bContext *C,
                              struct IxamFileData *bfd,
                              const struct IxamFileReadParams *params,
                              struct IxamFileReadReport *reports);

/**
 * \return Ixam file data, this must be passed to #BKE_ixamfile_read_setup when non-NULL.
 */
struct IxamFileData *BKE_ixamfile_read(const char *filepath,
                                         const struct IxamFileReadParams *params,
                                         struct IxamFileReadReport *reports);

/**
 * \return Ixam file data, this must be passed to #BKE_ixamfile_read_setup when non-NULL.
 */
struct IxamFileData *BKE_ixamfile_read_from_memory(const void *filebuf,
                                                     int filelength,
                                                     const struct IxamFileReadParams *params,
                                                     struct ReportList *reports);

/**
 * \return Ixam file data, this must be passed to #BKE_ixamfile_read_setup when non-NULL.
 * \note `memfile` is the undo buffer.
 */
struct IxamFileData *BKE_ixamfile_read_from_memfile(struct Main *bmain,
                                                      struct MemFile *memfile,
                                                      const struct IxamFileReadParams *params,
                                                      struct ReportList *reports);
/**
 * Utility to make a file 'empty' used for startup to optionally give an empty file.
 * Handy for tests.
 */
void BKE_ixamfile_read_make_empty(struct bContext *C);

/**
 * Only read the #UserDef from a .ixam.
 */
struct UserDef *BKE_ixamfile_userdef_read(const char *filepath, struct ReportList *reports);
struct UserDef *BKE_ixamfile_userdef_read_from_memory(const void *filebuf,
                                                       int filelength,
                                                       struct ReportList *reports);
struct UserDef *BKE_ixamfile_userdef_from_defaults(void);

/**
 * Only write the #UserDef in a `.ixam`.
 * \return success.
 */
bool BKE_ixamfile_userdef_write(const char *filepath, struct ReportList *reports);
/**
 * Only write the #UserDef in a `.ixam`, merging with the existing ixam file.
 * \return success.
 *
 * \note In the future we should re-evaluate user preferences,
 * possibly splitting out system/hardware specific preferences.
 */
bool BKE_ixamfile_userdef_write_app_template(const char *filepath, struct ReportList *reports);

bool BKE_ixamfile_userdef_write_all(struct ReportList *reports);

struct WorkspaceConfigFileData *BKE_ixamfile_workspace_config_read(const char *filepath,
                                                                    const void *filebuf,
                                                                    int filelength,
                                                                    struct ReportList *reports);
bool BKE_ixamfile_workspace_config_write(struct Main *bmain,
                                          const char *filepath,
                                          struct ReportList *reports);
void BKE_ixamfile_workspace_config_data_free(struct WorkspaceConfigFileData *workspace_config);

/* Partial ixam file writing. */

void BKE_ixamfile_write_partial_tag_ID(struct ID *id, bool set);
void BKE_ixamfile_write_partial_begin(struct Main *bmain_src);
/**
 * \param remap_mode: Choose the kind of path remapping or none #eBLO_WritePathRemap.
 * \return Success.
 */
bool BKE_ixamfile_write_partial(struct Main *bmain_src,
                                 const char *filepath,
                                 int write_flags,
                                 int remap_mode,
                                 struct ReportList *reports);
void BKE_ixamfile_write_partial_end(struct Main *bmain_src);

#ifdef __cplusplus
}
#endif
