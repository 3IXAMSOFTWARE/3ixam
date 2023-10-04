# -*- coding: utf-8 -*-

# Contributed to by gabhead, Lell, Anfeo, meta-androcto

import bpy
from bpy.types import (
        Operator,
        )
from bpy.props import (
        EnumProperty,
        BoolProperty,
        )


class OBJECT_OT_mirror_tools(Operator):
    bl_idname = "object.mirror_tools"
    bl_label = "Mirror Operator"
    bl_description = "Mirror Object Tools"
    bl_options = {'REGISTER', 'UNDO'}

    # Mirror Axis:
    mirror_axis: EnumProperty(
            items=(
                ("X", "X", "Mirror along the X axis"),
                ("Y", "Y", "Mirror along the Y axis"),
                ("Z", "Z", "Mirror along the Z axis"),
                ("XY", "XY", "Mirror along the X and Y axis"),
                ("YZ", "YZ", "Mirror along the Y and Z axis"),
                ("ZX", "ZX", "Mirror along the Z and X axis")),
            name="Mirror Axis",
            description="Mirror selected items around one or more axes"
            )
            
    clone: BoolProperty(
            name="Clone",
            default=False,
            description="Copy selected object"
            )

    def draw(self, context):
        layout = self.layout    
        layout.grid_flow(columns=2, align=True).prop(self, "mirror_axis", expand=True)

        layout.separator()

        row3 = layout.row()
        row3.emboss = "NONE"

        layout.separator()

        layout.prop(self, 'clone', text="Copy")
            

    def execute(self, context):
        objects = context.selected_objects   
        collections = context.collection

        if self.clone: 
            for obj in objects:
                obj_copy = obj.copy()
                collections.objects.link(obj_copy)
                obj_copy.select_set(False)           

        if self.mirror_axis == 'X':
            bpy.ops.transform.mirror(constraint_axis=(True, False, False), orient_type='GLOBAL')
        elif self.mirror_axis == 'Y':
            bpy.ops.transform.mirror(constraint_axis=(False, True, False), orient_type='GLOBAL')
        elif self.mirror_axis == 'Z':
            bpy.ops.transform.mirror(constraint_axis=(False, False, True), orient_type='GLOBAL')
        elif self.mirror_axis == 'XY':
            bpy.ops.transform.mirror(constraint_axis=(True, True, False), orient_type='GLOBAL')
        elif self.mirror_axis == 'YZ':
            bpy.ops.transform.mirror(constraint_axis=(False, True, True), orient_type='GLOBAL')
        elif self.mirror_axis == 'ZX':
            bpy.ops.transform.mirror(constraint_axis=(True, False, True), orient_type='GLOBAL')            

        return {'FINISHED'}

    def invoke(self, context, event):
        self.clone = False
        return context.window_manager.invoke_props_popup(self, event)


classes = (
    OBJECT_OT_mirror_tools,
    )