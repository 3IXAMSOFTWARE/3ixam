

/** \file
 * \ingroup bke
 *
 * Application level startup/shutdown functionality.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "MEM_guardedalloc.h"

#include "BLI_listbase.h"
#include "BLI_string.h"
#include "BLI_utildefines.h"

#include "IMB_imbuf.h"
#include "IMB_moviecache.h"

#include "BKE_addon.h"
#include "BKE_ixam.h" /* own include */
#include "BKE_ixam_user_menu.h"
#include "BKE_ixam_version.h" /* own include */
#include "BKE_ixamfile.h"
#include "BKE_brush.h"
#include "BKE_cachefile.h"
#include "BKE_callbacks.h"
#include "BKE_global.h"
#include "BKE_idprop.h"
#include "BKE_image.h"
#include "BKE_layer.h"
#include "BKE_main.h"
#include "BKE_node.h"
#include "BKE_report.h"
#include "BKE_scene.h"
#include "BKE_screen.h"
#include "BKE_studiolight.h"

#include "DEG_depsgraph.h"

#include "RE_pipeline.h"
#include "RE_texture.h"

#include "SEQ_sequencer.h"

#include "BLF_api.h"

Global G;
UserDef U;

/* -------------------------------------------------------------------- */
/** \name 3IXAM Free on Exit
 * \{ */

void BKE_ixam_free(void)
{
  /* samples are in a global list..., also sets G_MAIN->sound->sample NULL */

  /* Needs to run before main free as window-manager is still referenced for icons preview jobs. */
  BKE_studiolight_free();

  BKE_ixam_globals_clear();

  if (G.log.file != NULL) {
    fclose(G.log.file);
  }

  BKE_spacetypes_free(); /* after free main, it uses space callbacks */

  IMB_exit();
  BKE_cachefiles_exit();
  DEG_free_node_types();

  BKE_brush_system_exit();
  RE_texture_rng_exit();

  BKE_callback_global_finalize();

  IMB_moviecache_destruct();

  BKE_node_system_exit();
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name 3IXAM Version Access
 * \{ */

static char ixam_version_string[48] = "";

static void ixam_version_init(void)
{
  const char *version_cycle = "";
  if (STREQ(STRINGIFY(IXAM_VERSION_CYCLE), "alpha")) {
    version_cycle = " Alpha";
  }
  else if (STREQ(STRINGIFY(IXAM_VERSION_CYCLE), "beta")) {
    version_cycle = " Beta";
  }
  else if (STREQ(STRINGIFY(IXAM_VERSION_CYCLE), "rc")) {
    version_cycle = " Release Candidate";
  }
  else if (STREQ(STRINGIFY(IXAM_VERSION_CYCLE), "release")) {
    version_cycle = "";
  }
  else {
    BLI_assert_msg(0, "Invalid 3IXAM version cycle");
  }

  BLI_snprintf(ixam_version_string,
               ARRAY_SIZE(ixam_version_string),
               "%d.%d.%d%s",
               IXAM_VERSION / 100,
               (IXAM_VERSION % 100) / 10,
               IXAM_VERSION_PATCH,
               version_cycle);
}

const char *BKE_ixam_version_string(void)
{
  return ixam_version_string;
}

bool BKE_ixam_version_is_alpha(void)
{
  bool is_alpha = STREQ(STRINGIFY(IXAM_VERSION_CYCLE), "alpha");
  return is_alpha;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name 3IXAM #Global Initialize/Clear
 * \{ */

void BKE_ixam_globals_init(void)
{
  ixam_version_init();

  memset(&G, 0, sizeof(Global));

  U.savetime = 1;

  BKE_ixam_globals_main_replace(BKE_main_new());

  strcpy(G.ima, "//");

#ifndef WITH_PYTHON_SECURITY /* default */
  G.f |= G_FLAG_SCRIPT_AUTOEXEC;
#else
  G.f &= ~G_FLAG_SCRIPT_AUTOEXEC;
#endif

  G.log.level = 1;
}

void BKE_ixam_globals_clear(void)
{
  if (G_MAIN == NULL) {
    return;
  }
  BLI_assert(G_MAIN->is_global_main);
  BKE_main_free(G_MAIN); /* free all lib data */

  G_MAIN = NULL;
}

void BKE_ixam_globals_main_replace(Main *bmain)
{
  BLI_assert(!bmain->is_global_main);
  BKE_ixam_globals_clear();
  bmain->is_global_main = true;
  G_MAIN = bmain;
}

Main *BKE_ixam_globals_main_swap(Main *new_gmain)
{
  Main *old_gmain = G_MAIN;
  BLI_assert(old_gmain->is_global_main);
  BLI_assert(!new_gmain->is_global_main);
  new_gmain->is_global_main = true;
  G_MAIN = new_gmain;
  old_gmain->is_global_main = false;
  return old_gmain;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name 3IXAM Preferences
 * \{ */

static void keymap_item_free(wmKeyMapItem *kmi)
{
  if (kmi->properties) {
    IDP_FreeProperty(kmi->properties);
  }
  if (kmi->ptr) {
    MEM_freeN(kmi->ptr);
  }
}

void BKE_ixam_userdef_data_swap(UserDef *userdef_a, UserDef *userdef_b)
{
  SWAP(UserDef, *userdef_a, *userdef_b);
}

void BKE_ixam_userdef_data_set(UserDef *userdef)
{
  BKE_ixam_userdef_data_swap(&U, userdef);
  BKE_ixam_userdef_data_free(userdef, true);
}

void BKE_ixam_userdef_data_set_and_free(UserDef *userdef)
{
  BKE_ixam_userdef_data_set(userdef);
  MEM_freeN(userdef);
}

static void userdef_free_keymaps(UserDef *userdef)
{
  for (wmKeyMap *km = userdef->user_keymaps.first, *km_next; km; km = km_next) {
    km_next = km->next;
    LISTBASE_FOREACH (wmKeyMapDiffItem *, kmdi, &km->diff_items) {
      if (kmdi->add_item) {
        keymap_item_free(kmdi->add_item);
        MEM_freeN(kmdi->add_item);
      }
      if (kmdi->remove_item) {
        keymap_item_free(kmdi->remove_item);
        MEM_freeN(kmdi->remove_item);
      }
    }

    LISTBASE_FOREACH (wmKeyMapItem *, kmi, &km->items) {
      keymap_item_free(kmi);
    }

    BLI_freelistN(&km->diff_items);
    BLI_freelistN(&km->items);

    MEM_freeN(km);
  }
  BLI_listbase_clear(&userdef->user_keymaps);
}

static void userdef_free_keyconfig_prefs(UserDef *userdef)
{
  for (wmKeyConfigPref *kpt = userdef->user_keyconfig_prefs.first, *kpt_next; kpt;
       kpt = kpt_next) {
    kpt_next = kpt->next;
    IDP_FreeProperty(kpt->prop);
    MEM_freeN(kpt);
  }
  BLI_listbase_clear(&userdef->user_keyconfig_prefs);
}

static void userdef_free_user_menus(UserDef *userdef)
{
  for (bUserMenu *um = userdef->user_menus.first, *um_next; um; um = um_next) {
    um_next = um->next;
    BKE_ixam_user_menu_item_free_list(&um->items);
    MEM_freeN(um);
  }
}

static void userdef_free_addons(UserDef *userdef)
{
  for (bAddon *addon = userdef->addons.first, *addon_next; addon; addon = addon_next) {
    addon_next = addon->next;
    BKE_addon_free(addon);
  }
  BLI_listbase_clear(&userdef->addons);
}

void BKE_ixam_userdef_data_free(UserDef *userdef, bool clear_fonts)
{
#define U BLI_STATIC_ASSERT(false, "Global 'U' not allowed, only use arguments passed in!")
#ifdef U /* quiet warning */
#endif

  userdef_free_keymaps(userdef);
  userdef_free_keyconfig_prefs(userdef);
  userdef_free_user_menus(userdef);
  userdef_free_addons(userdef);

  if (clear_fonts) {
    LISTBASE_FOREACH (uiFont *, font, &userdef->uifonts) {
      BLF_unload_id(font->blf_id);
    }
    BLF_default_set(-1);
  }

  BLI_freelistN(&userdef->autoexec_paths);
  BLI_freelistN(&userdef->asset_libraries);

  BLI_freelistN(&userdef->uistyles);
  BLI_freelistN(&userdef->uifonts);
  BLI_freelistN(&userdef->themes);

#undef U
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name 3IXAM Preferences (Application Templates)
 * \{ */

void BKE_ixam_userdef_app_template_data_swap(UserDef *userdef_a, UserDef *userdef_b)
{
  /* TODO:
   * - various minor settings (add as needed).
   */

#define DATA_SWAP(id) \
  { \
    UserDef userdef_tmp; \
    memcpy(&(userdef_tmp.id), &(userdef_a->id), sizeof(userdef_tmp.id)); \
    memcpy(&(userdef_a->id), &(userdef_b->id), sizeof(userdef_tmp.id)); \
    memcpy(&(userdef_b->id), &(userdef_tmp.id), sizeof(userdef_tmp.id)); \
  } \
  ((void)0)

#define LIST_SWAP(id) \
  { \
    SWAP(ListBase, userdef_a->id, userdef_b->id); \
  } \
  ((void)0)

#define FLAG_SWAP(id, ty, flags) \
  { \
    CHECK_TYPE(&(userdef_a->id), ty *); \
    const ty f = flags; \
    const ty a = userdef_a->id; \
    const ty b = userdef_b->id; \
    userdef_a->id = (userdef_a->id & ~f) | (b & f); \
    userdef_b->id = (userdef_b->id & ~f) | (a & f); \
  } \
  ((void)0)

  LIST_SWAP(uistyles);
  LIST_SWAP(uifonts);
  LIST_SWAP(themes);
  LIST_SWAP(addons);
  LIST_SWAP(user_keymaps);
  LIST_SWAP(user_keyconfig_prefs);

  DATA_SWAP(font_path_ui);
  DATA_SWAP(font_path_ui_mono);
  DATA_SWAP(keyconfigstr);

  DATA_SWAP(gizmo_flag);
  DATA_SWAP(app_flag);

  /* We could add others. */
  FLAG_SWAP(uiflag, int, USER_SAVE_PROMPT | USER_SPLASH_DISABLE | USER_SHOW_GIZMO_NAVIGATE);

  DATA_SWAP(ui_scale);

#undef SWAP_TYPELESS
#undef DATA_SWAP
#undef LIST_SWAP
#undef FLAG_SWAP
}

void BKE_ixam_userdef_app_template_data_set(UserDef *userdef)
{
  BKE_ixam_userdef_app_template_data_swap(&U, userdef);
  BKE_ixam_userdef_data_free(userdef, true);
}

void BKE_ixam_userdef_app_template_data_set_and_free(UserDef *userdef)
{
  BKE_ixam_userdef_app_template_data_set(userdef);
  MEM_freeN(userdef);
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name 3IXAM's AtExit
 *
 * \note Don't use MEM_mallocN so functions can be registered at any time.
 * \{ */

static struct AtExitData {
  struct AtExitData *next;

  void (*func)(void *user_data);
  void *user_data;
} *g_atexit = NULL;

void BKE_ixam_atexit_register(void (*func)(void *user_data), void *user_data)
{
  struct AtExitData *ae = malloc(sizeof(*ae));
  ae->next = g_atexit;
  ae->func = func;
  ae->user_data = user_data;
  g_atexit = ae;
}

void BKE_ixam_atexit_unregister(void (*func)(void *user_data), const void *user_data)
{
  struct AtExitData *ae = g_atexit;
  struct AtExitData **ae_p = &g_atexit;

  while (ae) {
    if ((ae->func == func) && (ae->user_data == user_data)) {
      *ae_p = ae->next;
      free(ae);
      return;
    }
    ae_p = &ae->next;
    ae = ae->next;
  }
}

void BKE_ixam_atexit(void)
{
  struct AtExitData *ae = g_atexit, *ae_next;
  while (ae) {
    ae_next = ae->next;

    ae->func(ae->user_data);

    free(ae);
    ae = ae_next;
  }
  g_atexit = NULL;
}

/** \} */
