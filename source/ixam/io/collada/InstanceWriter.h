

#pragma once

#include "COLLADASWBindMaterial.h"

#include "DNA_object_types.h"

class InstanceWriter {
 protected:
  void add_material_bindings(COLLADASW::BindMaterial &bind_material,
                             Object *ob,
                             bool active_uv_only);
};
