

/** \file
 * \ingroup edgeometry
 */

#include "WM_api.h"

#include "ED_geometry.h"

#include "geometry_intern.hh"

/**************************** registration **********************************/

void ED_operatortypes_geometry(void)
{
  using namespace ixam::ed::geometry;

  WM_operatortype_append(GEOMETRY_OT_attribute_add);
  WM_operatortype_append(GEOMETRY_OT_attribute_remove);
  WM_operatortype_append(GEOMETRY_OT_color_attribute_add);
  WM_operatortype_append(GEOMETRY_OT_color_attribute_remove);
  WM_operatortype_append(GEOMETRY_OT_color_attribute_render_set);
  WM_operatortype_append(GEOMETRY_OT_color_attribute_duplicate);
  WM_operatortype_append(GEOMETRY_OT_attribute_convert);
}
