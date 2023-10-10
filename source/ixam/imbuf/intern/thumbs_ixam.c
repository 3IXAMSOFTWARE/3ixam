/* SPDX-License-Identifier: GPL-2.0-or-later */


#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "BLI_linklist.h"
#include "BLI_listbase.h" /* Needed due to import of BLO_readfile.h */
#include "BLI_utildefines.h"

#include "BLO_ixam_defs.h"
#include "BLO_readfile.h"

#include "BKE_icons.h"
#include "BKE_idtype.h"
#include "BKE_main.h"

#include "DNA_ID.h" /* For preview images... */

#include "IMB_imbuf.h"
#include "IMB_imbuf_types.h"
#include "IMB_thumbs.h"

#include "MEM_guardedalloc.h"

/* NOTE: we should handle all previews for a same group at once, would avoid reopening
 * `.ixam` file for each and every ID. However, this adds some complexity,
 * so keep it for later. */
static ImBuf *imb_thumb_load_from_ixam_id(const char *ixam_path,
                                           const char *ixam_group,
                                           const char *ixam_id)
{
  ImBuf *ima = NULL;
  IxamFileReadReport bf_reports = {.reports = NULL};

  struct IxamHandle *libfiledata = BLO_ixamhandle_from_file(ixam_path, &bf_reports);
  if (libfiledata == NULL) {
    return NULL;
  }

  int idcode = BKE_idtype_idcode_from_name(ixam_group);
  PreviewImage *preview = BLO_ixamhandle_get_preview_for_id(libfiledata, idcode, ixam_id);
  BLO_ixamhandle_close(libfiledata);

  if (preview) {
    ima = BKE_previewimg_to_imbuf(preview, ICON_SIZE_PREVIEW);
    BKE_previewimg_freefunc(preview);
  }
  return ima;
}

static ImBuf *imb_thumb_load_from_ixamfile(const char *ixam_path)
{
  IxamThumbnail *data = BLO_thumbnail_from_file(ixam_path);
  ImBuf *ima = BKE_main_thumbnail_to_imbuf(NULL, data);

  if (data) {
    MEM_freeN(data);
  }
  return ima;
}

ImBuf *IMB_thumb_load_ixam(const char *ixam_path, const char *ixam_group, const char *ixam_id)
{
  if (ixam_group && ixam_id) {
    return imb_thumb_load_from_ixam_id(ixam_path, ixam_group, ixam_id);
  }
  return imb_thumb_load_from_ixamfile(ixam_path);
}
