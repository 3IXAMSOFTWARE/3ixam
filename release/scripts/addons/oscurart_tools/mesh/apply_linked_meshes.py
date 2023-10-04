

# <pep8 compliant>

import bpy



def applyLRTEx(self, context):
    actObj = bpy.context.active_object
    actObjMatrixWorld = actObj.matrix_world.copy()
    bpy.ops.object.select_linked(extend=False, type="OBDATA")
    linkedObjects = bpy.context.selected_objects
    linkedObjects.remove(actObj)

    for vert in actObj.data.vertices:
        vert.co = actObjMatrixWorld @ vert.co
        actObj.location = (0,0,0)
        actObj.rotation_euler = (0,0,0)
        actObj.scale = (1,1,1)

    for ob in linkedObjects:     
        ob.matrix_world = ob.matrix_world @ actObj.matrix_world.inverted()


class ApplyLRT(bpy.types.Operator):
    """Apply LRT with linked mesh data"""
    bl_idname = "mesh.apply_linked_meshes"
    bl_label = "Apply LRT with linked meshes"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (context.view_layer.objects.active is not None and
                context.view_layer.objects.active.type == 'MESH')

    def execute(self, context):
        applyLRTEx(self, context)
        return {'FINISHED'}
    
  



