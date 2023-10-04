

# <pep8 compliant>

import bpy


def funcRemoveModifiers(self,context):
    for ob in bpy.context.selected_objects:
        if ob.type == "MESH":
            for mod in ob.modifiers:
                ob.modifiers.remove(mod)

class RemoveModifiers(bpy.types.Operator):
    """Remove all mesh modifiers"""
    bl_idname = "mesh.remove_modifiers"
    bl_label = "Remove Modifiers"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (context.view_layer.objects.active is not None and
                context.view_layer.objects.active.type == 'MESH')


    def execute(self, context):
        funcRemoveModifiers(self,context)
        return {'FINISHED'}



