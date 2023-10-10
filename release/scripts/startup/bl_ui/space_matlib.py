

# <pep8 compliant>
import bpy
from bpy.types import (
    Operator,
    Header,
    Menu,
    Panel,
)
from bpy.props import EnumProperty
from bpy_extras.node_utils import find_node_input
import math

class MATLIB_PT_main(Panel):
    bl_space_type = 'MATLIB'
    bl_region_type = 'WINDOW'
    bl_label = "Main"
    bl_options = {'INSTANCED'}

# Wood          Concrete                        Paints            Glass         Leather  Metal Custom
# Wood, Timber, Concrete, Brick, Plaster, Tile, Car Paint, Plastic Glass, Water, Leather, Metal

    group_name = ["Paints", "Metals", "Concrete", "Wood", "Glass", "Leather"]
    minimum_group_row = 2
    maximum_group_row = 5
    max_material_in_column = 10

    def draw(self, context):
        layout = self.layout
        space = context.space_data

        from collections import defaultdict
        mat_groups = defaultdict(list)

        for mat in bpy.data.materials:
            mat_groups[mat.group].append(mat)
    
        main_layout = layout.row()
    
        max_row_width = 0
        max_height = 0

        for i, group_name in enumerate(self.group_name, 1):
            main_layout.separator()
            sub = main_layout.column()
            sub.separator()

            header = sub.row()
            header.emboss = "NONE"
            header.icon_scale = 1.3
            header.enabled = False
            header.operator("matlib.mat_label", text=group_name)

            sub.separator(factor = 3.0)

            height = 0
            if mat_groups[i]:
                hex_layout = sub.hex_flow(columns=1, align=True)
                hex_layout.scale_y = 3.5
                hex_layout.icon_scale = 2.7

                mat_len = len(mat_groups[i])
                mat_in_row = min(self.maximum_group_row, max(self.minimum_group_row, math.floor(mat_len / self.max_material_in_column)))
                max_row_width = max(max_row_width, mat_in_row)

                for idx, mat in enumerate(mat_groups[i]):
                    if idx % mat_in_row == 0 and idx != 0:
                        hex_layout.split()     
                        height += 1    
                    hex_layout.material_operator(mat, icon_value=hex_layout.icon(mat))   

            max_height = max(max_height, height)            
        
        main_layout.separator()

        space.groups_len = len(self.group_name)
        space.group_width = max_row_width * 4
        space.group_height = max_height


class MATLIB_OT_material_label(Operator):
    bl_idname = "matlib.mat_label"
    bl_label = "Material"
    bl_description = "Material Group"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        return {'FINISHED'}


def panel_node_draw(layout, id_data, output_type, input_name):
    if not id_data.use_nodes:
        layout.operator("cycles.use_shading_nodes", icon='NODETREE')
        return False

    ntree = id_data.node_tree

    node = ntree.get_output_node('PHOTOREALISTIC')
    if node:
        input = find_node_input(node, input_name)
        if input:
            layout.template_node_view(ntree, node, input)
        else:
            layout.label(text="Incompatible output node")
    else:
        layout.label(text="No output node")

    return True

class MATLIB_PT_preferences(Panel):
    bl_space_type = 'MATLIB'
    bl_region_type = 'TOOLS'
    bl_label = "Material Parameters"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        space = context.space_data
        active_obj = context.active_object

        active_material_space = space.active_material
        active_material_object = active_obj.active_material if active_obj else None
        active_material = active_material_space or active_material_object

        layout.use_property_split = True
        
        sub = layout.row()
        sub.label(text="Material Parameters")
        sub.separator()
        if active_material_space:
            sub.operator("OBJECT_OT_matlib_clear_active_material", text="", icon="X", emboss=False)

        row = layout.column()
        row.enabled = False
        
        if active_material is None:
            row.label(text="No active material")
            return

        row.label(text=active_material.name)
        row.shape = 'PREFS'
        if not panel_node_draw(row, active_material, 'OUTPUT_MATERIAL', 'Surface'):
            row.prop(active_material, "diffuse_color")

classes = (
    MATLIB_OT_material_label,
    MATLIB_PT_main,
    MATLIB_PT_preferences,
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
