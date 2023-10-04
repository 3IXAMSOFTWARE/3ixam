import bpy
from bpy.types import Operator, Context

class CURVE_OT_fix_splines(bpy.types.Operator):
    bl_idname = "curve.fix_splines"
    bl_label = "Fix Splines after drawing them"

    
    def execute(self, context: Context):
        def select_first_spline(splines):
            first_spline = splines[0]
            for point in first_spline.bezier_points:
                point.select_control_point = True
        
        curve = context.active_object
        if curve.type!= "CURVE":
            return {'CANCELLED'}
        
        splines = curve.data.splines
        bpy.ops.curve.select_all(action='DESELECT')
        select_first_spline(splines)
        bpy.ops.curve.delete(type='VERT')
        return {'FINISHED'}
    
    
classes = (
    CURVE_OT_fix_splines,
)
