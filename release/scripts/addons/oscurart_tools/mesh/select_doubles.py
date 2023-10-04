

# <pep8 compliant>

import bpy

from mathutils import Vector
from bpy.types import Operator
from bpy.props import (
        IntProperty,
        BoolProperty,
        FloatProperty,
        EnumProperty,
        )
import os
import bmesh

C = bpy.context
D = bpy.data



def SelDoubles(self, context, distance):
    obj = bpy.context.object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    double = bmesh.ops.find_doubles(bm, verts=bm.verts, dist=distance)

    bpy.ops.mesh.select_all(action = 'DESELECT')

    for vertice in double['targetmap']:
        vertice.select = True

    # Switch to vertex select
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')

    # Show the updates in the viewport
    bmesh.update_edit_mesh(me, False)

class SelectDoubles(Operator):
    """Selects duplicated vertex without merge them"""
    bl_idname = "mesh.select_doubles"
    bl_label = "Select Doubles"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (context.view_layer.objects.active is not None and
                context.view_layer.objects.active.type == 'MESH' and
                context.view_layer.objects.active.mode == "EDIT")

    distance : bpy.props.FloatProperty(
        default=.0001,
        name="Distance")

    def execute(self, context):
        SelDoubles(self, context,self.distance)
        return {'FINISHED'}



