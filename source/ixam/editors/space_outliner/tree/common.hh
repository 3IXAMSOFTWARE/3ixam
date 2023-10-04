

#pragma once

struct ListBase;

namespace ixam::ed::outliner {

const char *outliner_idcode_to_plural(short idcode);

void outliner_make_object_parent_hierarchy(ListBase *lb);
bool outliner_animdata_test(const struct AnimData *adt);

}  // namespace ixam::ed::outliner
