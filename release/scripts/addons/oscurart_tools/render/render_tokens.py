

# <pep8 compliant>

import bpy
import os
from bpy.app.handlers import persistent

@persistent
def replaceTokens (dummy):
    global renpath
    tokens = {
    "$Scene":bpy.context.scene.name,
    "$File":os.path.basename(bpy.data.filepath).split(".")[0],
    "$ViewLayer":bpy.context.view_layer.name,
    "$Camera":bpy.context.scene.camera.name}
    
    renpath = bpy.context.scene.render.filepath
    
    bpy.context.scene.render.filepath = renpath.replace("$Scene",tokens["$Scene"]).replace("$File",tokens["$File"]).replace("$ViewLayer",tokens["$ViewLayer"]).replace("$Camera",tokens["$Camera"])
    print(bpy.context.scene.render.filepath)


@persistent
def restoreTokens (dummy):
    global renpath
    bpy.context.scene.render.filepath = renpath


# //RENDER/$Scene/$File/$ViewLayer/$Camera
