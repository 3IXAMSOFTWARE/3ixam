

/** \file
 * \ingroup bke
 */

#include "DNA_scene_types.h"
#include "DNA_sequence_types.h"

#include "BKE_scene.h"

#include "SEQ_select.h"
#include "SEQ_sequencer.h"

Sequence *SEQ_select_active_get(Scene *scene)
{
  Editing *ed = SEQ_editing_get(scene);

  if (ed == NULL) {
    return NULL;
  }

  return ed->act_seq;
}

void SEQ_select_active_set(Scene *scene, Sequence *seq)
{
  Editing *ed = SEQ_editing_get(scene);

  if (ed == NULL) {
    return;
  }

  ed->act_seq = seq;
}

bool SEQ_select_active_get_pair(Scene *scene, Sequence **r_seq_act, Sequence **r_seq_other)
{
  Editing *ed = SEQ_editing_get(scene);

  *r_seq_act = SEQ_select_active_get(scene);

  if (*r_seq_act == NULL) {
    return false;
  }

  Sequence *seq;

  *r_seq_other = NULL;

  for (seq = ed->seqbasep->first; seq; seq = seq->next) {
    if (seq->flag & SELECT && (seq != (*r_seq_act))) {
      if (*r_seq_other) {
        return false;
      }

      *r_seq_other = seq;
    }
  }

  return (*r_seq_other != NULL);
}
