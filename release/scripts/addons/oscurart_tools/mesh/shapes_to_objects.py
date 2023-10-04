

# <pep8 compliant>

import bpy
from bpy.types import Operator
from bpy.props import (
            BoolProperty,
            FloatProperty,
            )
import math



class ShapeToObjects(Operator):
    """It creates a new object for every shapekey in the selected object, ideal to export to other 3D software Apps"""
    bl_idname = "object.shape_key_to_objects_osc"
    bl_label = "Shapes To Objects"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (context.view_layer.objects.active is not None and
                context.view_layer.objects.active.type in
                {'MESH', 'SURFACE', 'CURVE'})

    def execute(self, context):
        OBJACT = bpy.context.view_layer.objects.active
        has_keys = hasattr(getattr(OBJACT.data, "shape_keys", None), "key_blocks")
        if has_keys:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            for SHAPE in OBJACT.data.shape_keys.key_blocks[:]:
                print(SHAPE.name)
                bpy.ops.object.shape_key_clear()
                SHAPE.value = 1
                OBJACT_eval = OBJACT.evaluated_get(depsgraph)
                mesh = bpy.data.meshes.new_from_object(OBJACT_eval)
                object = bpy.data.objects.new(SHAPE.name, mesh)
                bpy.context.scene.collection.objects.link(object)
        else:
            self.report({'INFO'}, message="Active object doesn't have shape keys")
            return {'CANCELLED'}

        return {'FINISHED'}
