

# <pep8 compliant>

import bpy
from bpy.types import Operator



class reloadImages (Operator):
    """Reloads all bitmaps in the scene"""
    bl_idname = "image.reload_images_osc"
    bl_label = "Reload Images"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for imgs in bpy.data.images:
            imgs.reload()
        return {'FINISHED'}


