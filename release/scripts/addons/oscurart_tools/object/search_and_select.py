

# <pep8 compliant>

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty
from bpy.props import StringProperty

# ------------------------ SEARCH AND SELECT ------------------------


class SearchAndSelectOt(bpy.types.Operator):
    """Search and select objects, by name"""
    bl_idname = "object.search_and_select_osc"
    bl_label = "Search And Select"
    bl_options = {"REGISTER", "UNDO"}

    keyword : StringProperty(name="Keyword", default="Type Here")
    start : BoolProperty(name="Start With", default=True)
    count : BoolProperty(name="Contain", default=True)
    end : BoolProperty(name="End", default=True)

    def execute(self, context):
        for objeto in bpy.context.scene.objects:
            variableNombre = self.keyword
            if self.start:
                if objeto.name.startswith(variableNombre):
                    objeto.select_set(True)
            if self.count:
                if objeto.name.count(variableNombre):
                    objeto.select_set(True)
            if self.end:
                if objeto.name.count(variableNombre):
                    objeto.select_set(True)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.keyword = "Type Here"
        self.start = True
        self.count = True
        self.end = True
        return context.window_manager.invoke_props_dialog(self)
    


