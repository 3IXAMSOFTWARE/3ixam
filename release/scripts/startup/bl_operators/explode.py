# -*- coding: utf-8 -*-

# Contributed to by gabhead, Lell, Anfeo, meta-androcto

import bpy
from bpy.types import (
        Operator
        )

from bpy.props import (
        BoolProperty,
        EnumProperty
        )


class OBJECT_OT_explode(Operator):
    bl_idname = "object.explode"
    bl_label = "Explode Operator"
    bl_description = "Attach/Deattach Objects Tools"
    bl_options = {'REGISTER', 'UNDO'}

    # separate_type:EnumProperty(
    #   name="Deattach Type",
    #   items=(
    #     ("SELECTED", "Selection", "Selection"),
    #     ("MATERIAL", "Material", "By Material"),  
    #     ("LOOSE", "Parts", "By Loose Parts") 
    #   ),
    #   description="Separate type"
    # )

    # attach: BoolProperty(
    #   name="Attach Mode",
    #   default=True,
    #   description="Attach/Deattach mode"
    #   )

    # def draw(self, context):
    #   layout = self.layout
    #   # layout.grid_flow(columns=1, align=True)
    #   layout.prop(self, "attach", toggle=True)
    #   if self.attach:
    #     layout.operator("object.join", text="Attach")
    #   else:
    #     # layout.grid_flow(columns=3, align=True).prop(self, "separate_type", expand=True)
    #     layout.operator("mesh.separate", text="Deattach").type = "LOOSE"

    def execute(self, context):
        if context.object is None:
          return {'CANCELLED'}
        
        for modif in context.object.modifiers:
          try:
            bpy.ops.object.modifier_apply(modifier = modif.name) 
          except:
            bpy.ops.object.modifier_remove(modifier = modif.name)

        need_mode_change = context.object.mode != "EDIT"
        mode = "OBJECT"
        type = "LOOSE"
        if need_mode_change:
          mode = context.object.mode
          bpy.ops.object.mode_set(mode="EDIT")
        else:
          type = "SELECTED"
        bpy.ops.mesh.separate(type=type)
        if need_mode_change:
          bpy.ops.object.mode_set(mode=mode)
        
        if not need_mode_change:
          bpy.ops.object.mode_set(mode='OBJECT')
          bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
          bpy.ops.object.mode_set(mode=mode)

        return {'FINISHED'}
    
    # def invoke(self, context, event):
    #     self.attach = True
    #     return context.window_manager.invoke_props_popup(self, event)


classes = (
    OBJECT_OT_explode,
    )
