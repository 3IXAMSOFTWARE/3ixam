

/** \file
 * \ingroup edgeometry
 */

#pragma once

struct wmOperatorType;

namespace ixam::ed::geometry {

/* *** geometry_attributes.cc *** */
void GEOMETRY_OT_attribute_add(struct wmOperatorType *ot);
void GEOMETRY_OT_attribute_remove(struct wmOperatorType *ot);
void GEOMETRY_OT_color_attribute_add(struct wmOperatorType *ot);
void GEOMETRY_OT_color_attribute_remove(struct wmOperatorType *ot);
void GEOMETRY_OT_color_attribute_render_set(struct wmOperatorType *ot);
void GEOMETRY_OT_color_attribute_duplicate(struct wmOperatorType *ot);
void GEOMETRY_OT_attribute_convert(struct wmOperatorType *ot);

}  // namespace ixam::ed::geometry
