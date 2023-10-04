

# <pep8 compliant>
import bpy
from bpy.types import (
    Operator,
    Header,
    Menu,
    Panel,
    PropertyGroup
)
from bpy.props import EnumProperty, StringProperty, BoolProperty, IntProperty, FloatVectorProperty, FloatProperty, CollectionProperty
from bpy_extras.node_utils import find_node_input
from bpy.app.translations import (
    pgettext_iface as iface_,
    contexts as i18n_contexts,
)
import math
from bpy.app.translations import (
    pgettext_iface as iface_,
    contexts as i18n_contexts,
)

import nodeitems_utils
from nodeitems_utils import (
    NodeItem,
)

import nodeitems_builtins
import mathutils

from itertools import cycle as itertools_cycle

class NodeLink_Props(PropertyGroup):
    output_index: IntProperty(
        name='Index of the output node in the node_tree array'
    )
    output_name: StringProperty(
        name='Name of the output socket'
    )
    input_index: IntProperty(
        name='Index of the input node in the node_tree array'
    )
    input_name: StringProperty(
        name='Name of the input socket'
    )

node_property_types = (
    ('COLOR', 'Color', ''), 
    ('FLOAT', 'Float', ''), 
    ('VEC3', 'Vec3', ''))

class NodeValue_Props(PropertyGroup):
    socket_name: StringProperty(
        name='Socket name'
    )
    socket_type: EnumProperty(
        name='Type',
        items=node_property_types
    )
    color_prop: FloatVectorProperty(name='Color', size=4)
    float_prop: FloatProperty(name="Float", default=0.0)
    vec3_prop: FloatVectorProperty(name="Vector 3")

class Node_Props(PropertyGroup):
    node_index: IntProperty(
        name='Index in the node_tree array'
    )
    node_type: StringProperty(
        name='Type of this node',
        default='ShaderNodeBsdfPrincipled'
    )
    location_x: IntProperty(
        name='X location'
    )
    location_y: IntProperty(
        name='Y location'
    )
    select: BoolProperty(
        name='Select',
        default=True
    )
    active_node: BoolProperty(
        name='Active node',
        default=False
    )
    links: CollectionProperty(
        name='Links of this node',
        type=NodeLink_Props
    )
    prop_values: CollectionProperty(
        name='Values',
        type=NodeValue_Props
    )

def set_bsdf_diffuse_nodes_props(prop):
        diffuse = prop.nodes.add()
        output = prop.nodes.add()

        diffuse.node_index = 0
        diffuse.node_type = 'ShaderNodeBsdfDiffuse'
        diffuse.location_x = 100
        diffuse.location_y = 100
        diffuse.select = True
        diffuse.active_node = True

        link = diffuse.links.add()
        link.output_index = 0
        link.output_name = 'BSDF'
        link.input_index = 1
        link.input_name = 'Surface'

        output.node_index = 1
        output.node_type = 'ShaderNodeOutputMaterial'            
        output.location_x = 300
        output.location_y = 100
        output.select = False
        output.active_node = False

def set_bsdf_principled_nodes_props(prop):
        diffuse = prop.nodes.add()
        output = prop.nodes.add()

        diffuse.node_index = 0
        diffuse.node_type = 'ShaderNodeBsdfPrincipled'
        diffuse.location_x = 100
        diffuse.location_y = 100
        diffuse.select = True
        diffuse.active_node = True

        link = diffuse.links.add()
        link.output_index = 0
        link.output_name = 'BSDF'
        link.input_index = 1
        link.input_name = 'Surface'

        output.node_index = 1
        output.node_type = 'ShaderNodeOutputMaterial'            
        output.location_x = 350
        output.location_y = 100
        output.select = False
        output.active_node = False

def set_bsdf_emission_nodes_props(prop):
    emmision = prop.nodes.add()
    output = prop.nodes.add()

    emmision.node_index = 0
    emmision.node_type = 'ShaderNodeEmission'
    emmision.location_x = 100
    emmision.location_y = 100
    emmision.select = True
    emmision.active_node = True

    link = emmision.links.add()
    link.output_index = 0
    link.output_name = 'Emission'
    link.input_index = 1
    link.input_name = 'Surface'

    output.node_index = 1
    output.node_type = 'ShaderNodeOutputMaterial'            
    output.location_x = 350
    output.location_y = 100
    output.select = False
    output.active_node = False

def set_bsdf_glass_nodes_props(prop):
    glass = prop.nodes.add()
    output = prop.nodes.add()

    glass.node_index = 0
    glass.node_type = 'ShaderNodeBsdfGlass'
    glass.location_x = 100
    glass.location_y = 100
    glass.select = True
    glass.active_node = True

    link = glass.links.add()
    link.output_index = 0
    link.output_name = 'BSDF'
    link.input_index = 1
    link.input_name = 'Surface'

    output.node_index = 1
    output.node_type = 'ShaderNodeOutputMaterial'            
    output.location_x = 350
    output.location_y = 100
    output.select = False
    output.active_node = False

def set_bsdf_volume_nodes_props(prop):
    volume = prop.nodes.add()
    output = prop.nodes.add()

    volume.node_index = 0
    volume.node_type = 'ShaderNodeVolumePrincipled'
    volume.location_x = 100
    volume.location_y = 100
    volume.select = True
    volume.active_node = True

    link = volume.links.add()
    link.output_index = 0
    link.output_name = 'Volume'
    link.input_index = 1
    link.input_name = 'Volume'

    output.node_index = 1
    output.node_type = 'ShaderNodeOutputMaterial'            
    output.location_x = 350
    output.location_y = 100
    output.select = False
    output.active_node = False

def set_bsdf_skin_nodes_props(prop):
    skin = prop.nodes.add()
    output = prop.nodes.add()

    skin.node_index = 0
    skin.node_type = 'ShaderNodeBsdfPrincipled'
    skin.location_x = 100
    skin.location_y = 100
    skin.select = True
    skin.active_node = True

    subsurface = skin.prop_values.add()
    subsurface.socket_name = 'Subsurface'
    subsurface.socket_type = 'FLOAT'
    subsurface.float_prop = 0.1

    subsurface_color = skin.prop_values.add()
    subsurface_color.socket_name = 'Subsurface Color'
    subsurface_color.socket_type = 'COLOR'
    subsurface_color.color_prop = [1.0, 0.0, 0.0, 1.0]

    link = skin.links.add()
    link.output_index = 0
    link.output_name = 'BSDF'
    link.input_index = 1
    link.input_name = 'Surface'

    output.node_index = 1
    output.node_type = 'ShaderNodeOutputMaterial'            
    output.location_x = 350
    output.location_y = 100
    output.select = False
    output.active_node = False

class MATPRO_HT_header(Header):
    bl_space_type = 'MATPRO'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        snode = context.space_data
        overlay = snode.overlay
        snode_id = snode.id
        id_from = snode.id_from
        tool_settings = context.tool_settings
        is_compositor = snode.tree_type == 'CompositorNodeTree'

        # Now expanded via the 'ui_type'
        # layout.prop(snode, "tree_type", text="")

        if snode.tree_type == 'ShaderNodeTree':
            ob = context.object
            layout.separator()
            MATPRO_MT_editor_menus.draw_collapsible(context, layout)

        # elif snode.tree_type == 'TextureNodeTree':
        #     layout.prop(snode, "texture_type", text="")

        #     MATPRO_MT_editor_menus.draw_collapsible(context, layout)

        #     if snode_id:
        #         layout.prop(snode_id, "use_nodes")

        #     layout.separator_spacer()

        #     if id_from:
        #         if snode.texture_type == 'BRUSH':
        #             layout.template_ID(id_from, "texture", new="texture.new")
        #         else:
        #             layout.template_ID(id_from, "active_texture", new="texture.new")

        # elif snode.tree_type == 'CompositorNodeTree':

        #     MATPRO_MT_editor_menus.draw_collapsible(context, layout)

        #     if snode_id:
        #         layout.prop(snode_id, "use_nodes")

        # elif snode.tree_type == 'GeometryNodeTree':
        #     MATPRO_MT_editor_menus.draw_collapsible(context, layout)
        #     layout.separator_spacer()

        #     ob = context.object

        #     row = layout.row()
        #     if snode.pin:
        #         row.enabled = False
        #         row.template_ID(snode, "node_tree", new="node.new_geometry_node_group_assign")
        #     elif ob:
        #         active_modifier = ob.modifiers.active
        #         if active_modifier and active_modifier.type == 'NODES':
        #             if active_modifier.node_group:
        #                 row.template_ID(active_modifier, "node_group", new="object.geometry_node_tree_copy_assign")
        #             else:
        #                 row.template_ID(active_modifier, "node_group", new="node.new_geometry_node_group_assign")
        #         else:
        #             row.template_ID(snode, "node_tree", new="node.new_geometry_nodes_modifier")

        # else:
        #     # Custom node tree is edited as independent ID block
        #     MATPRO_MT_editor_menus.draw_collapsible(context, layout)

        #     layout.separator_spacer()

        #     layout.template_ID(snode, "node_tree", new="node.new_node_tree")

class MATPRO_MT_editor_menus(Menu):
    bl_idname = "MATPRO_MT_editor_menus"
    bl_label = ""
    bl_space_type = 'MATPRO'

    def draw(self, context):
        layout = self.layout

        mlayout = layout.row(align=True)
        button_scale = 4.1

        alternating_shape_gen = itertools_cycle(['TRAPEZOID', 'TRAPEZOIDR'])
        alternating_shape = lambda: next(alternating_shape_gen)

        def trapezoid_menu(*args, **kwargs):
            sub = mlayout.row(align=True)
            sub.ui_units_x = button_scale
            sub.menu(*args, shape=alternating_shape(), **kwargs)
            mlayout.separator(factor=2.0)

        trapezoid_menu("MATPRO_MT_create")
        trapezoid_menu("MATPRO_MT_edit")
        trapezoid_menu("MATPRO_MT_actions")
        trapezoid_menu("TOPBAR_MT_help")

class MATPRO_MT_create(Menu):
    bl_idname = "MATPRO_MT_create"
    bl_label = "Create"
    bl_space_type = 'MATPRO'

    def draw(self, context):
        layout = self.layout

        op = layout.operator("matpro.create_material")
        set_bsdf_diffuse_nodes_props(op)
        
        layout.operator("matpro.pbr_setup", text="PBR Setup")

        layout.separator()

        material_types = [['Universal Material', set_bsdf_principled_nodes_props], 
                          ['Emission Material', set_bsdf_emission_nodes_props], 
                          ['Glass Material', set_bsdf_glass_nodes_props], 
                          ['Volume Material', set_bsdf_volume_nodes_props],
                          ['Skin Material', set_bsdf_skin_nodes_props]]
        
        for el in material_types:
            mat = layout.operator("matpro.create_unassigned_material", text=el[0])
            el[1](mat)

        layout.separator()

        layout.operator("screen.matlib_show", text="Open Material Lib")

class MATPRO_MT_edit(Menu):
    bl_idname = "MATPRO_MT_edit"
    bl_label = "Edit"
    bl_space_type = 'MATPRO'

    def draw(self, context):
        layout = self.layout

        layout.operator("ed.undo", text="Undo")
        layout.operator("ed.redo", text="Redo")

        layout.separator()

        layout.operator("matpro.rename_material", text="Rename Material")
        layout.operator("matpro.material_duplicate", text="Duplicate Material")
        layout.operator("matpro.material_delete", text="Delete Material")

        layout.separator()

        layout.operator("node.nw_del_unused", text="Clear Unused")

class MATPRO_MT_actions(Menu):
    bl_idname = "MATPRO_MT_actions"
    bl_label = "Actions"
    bl_space_type = 'MATPRO'

    def draw(self, context):
        layout = self.layout

        prop = layout.operator("matpro.create_unassigned_material", text="Add Slot")
        set_bsdf_principled_nodes_props(prop)
        layout.menu("MATPRO_MT_remove", text="Remove")

        layout.separator()

        layout.operator("matpro.assign_material", text="Assign Material")
        layout.operator("uv.smart_project", text="AutoUV")
        layout.operator("view3d.materialutilities_select_by_material_name", text="Select by Material")
        layout.operator("view3d.materialutilities_replace_material", text="Replace by Material")
        layout.operator("matpro.merge_by_material", text="Merge by Material")

        layout.separator()

        mv = layout.operator("material.materialutilities_slot_move", text="Move Slot to First")
        mv.movement = 'TOP'
        mv2 = layout.operator("material.materialutilities_slot_move", text="Move Slot to Last")
        mv2.movement = 'BOTTOM'

def create_material(ob):
    has_materials = len(ob.data.materials) > 0
    mat = None

    if not has_materials:
        mat = bpy.data.materials.new(name='Material')
        ob.data.materials.append(mat)
    else:
        mat = bpy.data.materials.new(name='Material')
        slot = ob.active_material_index
        if ob.material_slots[slot].material is None:
            ob.material_slots[slot].material = mat
        else:
            ob.data.materials.append(mat)
            ob.active_material_index = len(ob.data.materials)-1

    return mat

class MATPRO_OT_create_material(Operator):
    """Tooltip"""
    bl_idname = "matpro.create_material"
    bl_label = "Create a simple material"
    bl_options = {'REGISTER', 'UNDO'}

    nodes: CollectionProperty(name='Nodes', type=Node_Props)
    
    @classmethod
    def poll(self, context):
        return context.space_data.type == 'MATPRO' and (context.active_object is not None) and not context.object.protect and context.active_object.type != 'EMPTY'

    def execute(self, context):
        ob = bpy.context.active_object

        mat = create_material(ob)
        mat.use_nodes = True

        # Remove default BSDF nodes
        tree = mat.node_tree
        for node in mat.node_tree.nodes:
            tree.nodes.remove(node)

        # Create nodes first
        node_indcies = {}
        for node in self.nodes:
            new = tree.nodes.new(node.node_type)
            new.location = (node.location_x, node.location_y)
            new.select = node.select
            if node.active_node:
                tree.nodes.active = new

            node_indcies[node.node_index] = new

        # Create links after
        for node in self.nodes:
            for link in node.links:
                tree.links.new(node_indcies[link.output_index].outputs[link.output_name], node_indcies[link.input_index].inputs[link.input_name])

        context.space_data.active_material = mat
            
        return {'FINISHED'}

class MATPRO_OT_PBR_setup(Operator):
    bl_idname = 'matpro.pbr_setup'
    bl_label = 'PBR Setup'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return context.space_data.type == 'MATPRO' and (context.active_object is not None) and not context.object.protect and context.active_object.type != 'EMPTY'

    def execute(self, context):
        ob = bpy.context.active_object
        
        mat = create_material(ob)
        mat.use_nodes = True

        tree = mat.node_tree
        for n in tree.nodes:
                n.select = False

        space = context.space_data
        space.node_tree = tree

        tree.nodes[0].select = True
        tree.nodes.active = tree.nodes[0]

        bpy.ops.node.nw_add_textures_for_principled('INVOKE_DEFAULT')

        context.space_data.active_material = mat

        return {'FINISHED'}
    
class MATPRO_OT_create_unassigned_material(Operator):
    bl_idname = 'matpro.create_unassigned_material'
    bl_label = 'Create a simple material'
    bl_options = {'REGISTER', 'UNDO'}

    nodes: CollectionProperty(name='Nodes', type=Node_Props)

    @classmethod
    def poll(self, context):
        return context.space_data.type == 'MATPRO'

    def execute(self, context):
        mat = bpy.data.materials.new("Material")
        mat.use_fake_user = True
        mat.use_nodes = True

        # Remove default BSDF nodes
        tree = mat.node_tree
        for node in mat.node_tree.nodes:
            tree.nodes.remove(node)
    
        # Create nodes first
        node_indcies = {}
        for node in self.nodes:
            new = tree.nodes.new(node.node_type)
            new.location = (node.location_x, node.location_y)
            new.select = node.select
            if node.active_node:
                tree.nodes.active = new

            # Set predefined properties
            for prop in node.prop_values:
                if prop.socket_type == 'COLOR':
                    new.inputs[prop.socket_name].default_value = prop.color_prop
                elif prop.socket_type == 'FLOAT':
                    new.inputs[prop.socket_name].default_value = prop.float_prop
                elif prop.soclet_type == 'VEC3':
                    new.inputs[prop.socket_name].default_value = prop.vec3_prop

            node_indcies[node.node_index] = new

        # Create links after
        for node in self.nodes:
            for link in node.links:
                tree.links.new(node_indcies[link.output_index].outputs[link.output_name], node_indcies[link.input_index].inputs[link.input_name])

        smatpro = context.space_data
        smatpro.active_material = mat
        
        zero_obj = bpy.data.objects.get('zeroObj')
        context.view_layer.objects.active = zero_obj
        zero_obj.active_material = mat

        return {'FINISHED'}
    

class MATPRO_OT_merge_by_material(Operator):
    bl_idname = 'matpro.merge_by_material'
    bl_label = 'Merge By Material'
    bl_description = 'Merge By Material'

    matorg: StringProperty(
        name = "Original",
        description = "Material to find and merge",
        maxlen = 63,
        )
    matrep: StringProperty(
        name="To merge",
        description = "Material that will be merged with the original",
        maxlen = 63,
        )
    all_objects: BoolProperty(
        name = "All Objects",
        description = "Replace for all objects in this ixam file (otherwise only selected objects)",
        default = True,
        )

    def copy_attributes(self, attributes, old_prop, new_prop):
        """copies the list of attributes from the old to the new prop if the attribute exists"""

        for attr in attributes:
            if hasattr(new_prop, attr):
                setattr(new_prop, attr, getattr(old_prop, attr))

    def copy_links(self, context, nodes_from, nodes_to, tree):
        """copies all links between the nodes in the nodes_from list to the nodes_to"""

        i = 0
        for node in nodes_from:
            node_from = nodes_from[i]
            node_to = nodes_to[i]

            for j, inp in enumerate(node_from.inputs):
                for link in inp.links:
                    result = -1
                    for idx, target in enumerate(nodes_from):
                        if target == link.from_node:
                            result = idx

                    if result != -1:
                        connected_node = nodes_to[result]
                        tree.links.new(connected_node.outputs[link.from_socket.name], node_to.inputs[j])

            i = i + 1

    def get_node_attributes(self, node):
        """returns a list of all propertie identifiers if they shoulnd't be ignored"""

        ignore_attributes = ("interface", "color_ramp", "color_mapping", "texture_mapping", "node_preview", "rna_type", "type", "dimensions", "inputs", "outputs", "internal_links", "select")

        attributes = []
        for attr in node.bl_rna.properties:
            if not attr.identifier in ignore_attributes and not attr.identifier.split("_")[0] == "bl":
                attributes.append(attr.identifier)

        return attributes

    def draw(self, context):
        layout = self.layout

        layout.prop_search(self, "matorg", bpy.data, "materials")
        layout.prop_search(self, "matrep", bpy.data, "materials")
        layout.separator()

        layout.prop(self, "all_objects", icon = "BLANK1")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        """Replace one material with another material"""

        mat_org = bpy.data.materials.get(self.matorg)
        mat_rep = bpy.data.materials.get(self.matrep)

        if mat_org != mat_rep and None not in (mat_org, mat_rep):
            # Store active object
            scn = bpy.context.scene

            if self.all_objects:
                objs = bpy.data.objects
            else:
                objs = bpy.context.selected_editable_objects

            for obj in objs:
                if obj.type == 'MESH':
                    match = False

                    for mat in obj.material_slots:
                        if mat.material == mat_org:
                            tree = mat.material.node_tree
                            for n in tree.nodes:
                                n.select = False

                            input_attributes = ("default_value", "name")
                            output_attributes = ("default_value", "name")

                            nodes_to = []

                            for node in mat_rep.node_tree.nodes:
                                copy = tree.nodes.new(type=node.rna_type.identifier)
                                node_attributes = self.get_node_attributes(node)
                                self.copy_attributes(node_attributes, node, copy)

                                for i, inp in enumerate(node.inputs):
                                    self.copy_attributes(input_attributes, inp, copy.inputs[i])

                                for i, out in enumerate(node.outputs):
                                    self.copy_attributes(output_attributes, out, copy.outputs[i])
                                    
                                nodes_to.append(copy)

                            self.copy_links(context, mat_rep.node_tree.nodes, nodes_to, tree)
                            
                            break

        return {'FINISHED'}

class MATPRO_OT_big_label(Operator):
    bl_idname = "matpro.big_label"
    bl_label = "Properties"
    bl_description = "Properties"

    def execute(self, context):
        return {'FINISHED'}
    
class MATPRO_PT_active_node_properties(Panel):
    bl_space_type = 'MATPRO'
    bl_region_type = 'EXECUTE'
    # bl_category = "Node"
    bl_label = "Properties"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return context.active_node is not None

    def draw(self, context):
        layout = self.layout
        node = context.active_node

        row = layout.row()
        row.alignment = 'CENTER'
        row.icon_scale = 1.2
        row.emboss = 'NONE'
        row.operator("matpro.big_label", text=node.name)
        layout.separator()

        # set "node" context pointer for the panel layout
        layout.context_pointer_set("node", node)

        if hasattr(node, "draw_buttons_ext"):
            node.draw_buttons_ext(context, layout)
        elif hasattr(node, "draw_buttons"):
            node.draw_buttons(context, layout)

        # XXX this could be filtered further to exclude socket types
        # which don't have meaningful input values (e.g. cycles shader)
        i = 0
        value_inputs = [socket for socket in node.inputs if self.show_socket_input(socket)]
        if value_inputs:
            layout.separator()
            for socket in value_inputs:
                row = layout.row()
                socket.draw(
                    context,
                    row,
                    node,
                    iface_(socket.label if socket.label else socket.name, socket.bl_rna.translation_context),
                )
                if socket.is_linked:
                    row.operator("matpro.select_linked_from", text="", icon="VIEWZOOM").socket_identifier = socket.identifier
                else:
                    op = row.operator("node.nw_add_texture", text="", icon="ADD")
                    op.selected_socket_index = i

                i = i + 1

    def show_socket_input(self, socket):
        return hasattr(socket, 'draw') and socket.enabled
    
class MATPRO_OT_preview_label(Operator):
    bl_idname = "matpro.preview_label"
    bl_label = "Preview"
    bl_description = "Preview"

    def execute(self, context):
        return {'FINISHED'}

class MATPRO_PT_preview(Panel):
    bl_idname = 'MATPRO_PT_preview'
    bl_label = "Preview"
    bl_space_type = 'MATPRO'
    bl_region_type = 'PREVIEW'
    bl_context = "material"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(self, context):
        return context.material is not None

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.alignment = 'CENTER'
        row.icon_scale = 1.5
        row.emboss = 'NONE'
        # row.operator("matpro.preview_label", text="Preview")

        layout.template_preview(context.material, show_buttons=False, show_resize=False)

class MATPRO_MT_remove(Menu):
    bl_label = 'Remove'
    bl_space_type = 'MATPRO'
    bl_region_type = 'HEADER'

    def draw(self, context):
        layout = self.layout
        
        layout.operator("object.material_slot_remove", text="Selected Slot", emboss=False)
        layout.operator("view3d.materialutilities_remove_all_material_slots", text="All Slots", emboss=False)

        layout.separator()

        layout.operator("matpro.remove_unused_slots", text="Unused Slots", emboss=False)

class MATPRO_OT_remove_unused_slots(Operator):
    bl_idname = "matpro.remove_unused_slots"
    bl_description = "Remove unused slots"
    bl_label = 'Remove unused slots'

    def execute(self, context):
        ob = context.active_object
        bpy.ops.object.material_slot_remove_unused({"object" : ob})

        return {'FINISHED'}
    
class MATPRO_OT_material_duplicate(Operator):
    bl_idname = "matpro.material_duplicate"
    bl_description = "Duplicate an active material"
    bl_label = "Duplicate an active material"

    @classmethod
    def poll(self, context):
        return context.space_data.type == 'MATPRO' and context.space_data.active_material is not None

    def execute(self, context):
        mat = context.space_data.active_material
        copy = mat.copy()

        return {'FINISHED'}

class MATPRO_OT_material_delete(Operator):
    bl_idname = "matpro.material_delete"
    bl_description = "Delete active material"
    bl_label = "Delete active material"

    @classmethod
    def poll(self, context):
        space = context.space_data
        return space.type == 'MATPRO'

    def execute(self, context):
        smatpro = context.space_data
        material = smatpro.active_material

        if material is None:
            self.report({'WARNING'}, "No active material")
            return {'CANCELLED'}

        materials = bpy.data.materials
        if material.name not in materials:
            self.report({'WARNING'}, f"Unable to find material {material.name}")
            return {'CANCELLED'}
        
        smatpro.active_material = None
        material.use_fake_user = False
        materials.remove(material)
        
        return {'FINISHED'}


class MATPRO_MT_context_menu(Menu):
    bl_label = "Context Menu"

    def draw(self, context):
        layout = self.layout

        selected_nodes_len = len(context.selected_nodes)

        # If something is selected
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("matpro.duplicate_move")
        layout.operator("matpro.clipboard_copy", text="Copy")
        layout.operator("matpro.clipboard_paste", text="Paste")
        layout.operator("matpro.delete")
        layout.operator("matpro.delete_reconnect", text='Disolve') # Delete with reconnect

        layout.separator()

        layout.operator("matpro.hide_socket_toggle", text='Compact Mode') # Toggle hidden node sockets

        layout.separator()

        props = layout.operator('wm.call_panel', text='Add Label')
        props.name = "MATPRO_PT_label"
        props.keep_open = False

class MATPRO_PT_label(Panel):
    bl_space_type = 'MATPRO'
    bl_region_type = 'WINDOW'
    bl_label = "Add Label"

    @classmethod
    def poll(self, context):
        return context.active_node is not None

    def draw(self, context):
        layout = self.layout

        layout.label(text="Node Label")
        item = context.active_node
        if item:
            row = layout.row()
            row.prop(item, "label", text="")

class MATPRO_PT_palette_navbar(Panel):
    bl_label = "Palette Navigation"
    bl_space_type = 'MATPRO'
    bl_region_type = 'NAVIGATION_BAR'
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout    

        smatpro = context.space_data

        col = layout.vert_row()
        col.shape = 'TRAPEZOID'

        col.scale_x = 1.3
        col.scale_y = 1.1
        col.ui_units_y=30
        col.prop(smatpro, "palette_active_section", expand=True)

class MATPRO_PT_palette_input(Panel):
    bl_space_type = 'MATPRO'
    bl_region_type = 'TOOLS'
    bl_label = "Palette menu input"
    bl_options = {'HIDE_HEADER'}
    bl_context = "input"

    items = [
        NodeItem("ShaderNodeTexCoord"),
        NodeItem("ShaderNodeAttribute"),
        NodeItem("ShaderNodeLightPath"),
        NodeItem("ShaderNodeFresnel"),
        NodeItem("ShaderNodeLayerWeight"),
        NodeItem("ShaderNodeRGB"),
        NodeItem("ShaderNodeValue"),
        NodeItem("ShaderNodeTangent"),
        NodeItem("ShaderNodeNewGeometry"),
        NodeItem("ShaderNodeWireframe"),
        NodeItem("ShaderNodeBevel"),
        NodeItem("ShaderNodeAmbientOcclusion"),
        NodeItem("ShaderNodeObjectInfo"),
        NodeItem("ShaderNodeHairInfo"),
        NodeItem("ShaderNodePointInfo"),
        NodeItem("ShaderNodeVolumeInfo"),
        # NodeItem("ShaderNodeParticleInfo"),
        NodeItem("ShaderNodeCameraData"),
        NodeItem("ShaderNodeUVMap"),
        NodeItem("ShaderNodeVertexColor"),
        NodeItem("ShaderNodeUVAlongStroke", poll=nodeitems_builtins.line_style_shader_nodes_poll),
    ]
    
    def draw(self, context):
        layout = self.layout
        layout.shape = 'PREFS'
        layout.scale_y = 1.5

        for item in self.items:
            item.draw(item, layout, context)
        
class MATPRO_PT_palette_output(Panel):
    bl_space_type = 'MATPRO'
    bl_region_type = 'TOOLS'
    bl_label = "Palette menu output"
    bl_options = {'HIDE_HEADER'}
    bl_context = "output"
    
    items=[
        NodeItem("ShaderNodeOutputMaterial", poll=nodeitems_builtins.object_eevee_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeOutputLight", poll=nodeitems_builtins.object_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeOutputAOV"),
    ]

    def draw(self, context):
        layout = self.layout
        layout.shape = 'PREFS'
        layout.scale_y = 1.5

        for item in self.items:
            item.draw(item, layout, context)


class MATPRO_PT_palette_shader(Panel):
    bl_space_type = 'MATPRO'
    bl_region_type = 'TOOLS'
    bl_label = "Palette menu shader"
    bl_options = {'HIDE_HEADER'}
    bl_context = "shader"

    items=[
        NodeItem("ShaderNodeMixShader", poll=nodeitems_builtins.eevee_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeAddShader", poll=nodeitems_builtins.eevee_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeBsdfDiffuse", poll=nodeitems_builtins.object_eevee_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeBsdfPrincipled", poll=nodeitems_builtins.object_eevee_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeBsdfGlossy", poll=nodeitems_builtins.object_eevee_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeBsdfTransparent", poll=nodeitems_builtins.object_eevee_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeBsdfRefraction", poll=nodeitems_builtins.object_eevee_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeBsdfGlass", poll=nodeitems_builtins.object_eevee_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeBsdfTranslucent", poll=nodeitems_builtins.object_eevee_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeBsdfAnisotropic", poll=nodeitems_builtins.object_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeBsdfVelvet", poll=nodeitems_builtins.object_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeBsdfToon", poll=nodeitems_builtins.object_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeSubsurfaceScattering", poll=nodeitems_builtins.object_eevee_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeEmission", poll=nodeitems_builtins.eevee_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeBsdfHair", poll=nodeitems_builtins.object_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeBackground", poll=nodeitems_builtins.world_shader_nodes_poll),
        NodeItem("ShaderNodeHoldout", poll=nodeitems_builtins.object_eevee_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeVolumeAbsorption", poll=nodeitems_builtins.eevee_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeVolumeScatter", poll=nodeitems_builtins.eevee_cycles_shader_nodes_poll),
        NodeItem("ShaderNodeVolumePrincipled"),
        NodeItem("ShaderNodeEeveeSpecular", poll=nodeitems_builtins.object_eevee_shader_nodes_poll),
        NodeItem("ShaderNodeBsdfHairPrincipled", poll=nodeitems_builtins.object_cycles_shader_nodes_poll)
    ]
    
    def draw(self, context):
        layout = self.layout
        layout.shape = 'PREFS'
        layout.scale_y = 1.5
 
        for item in self.items:
            item.draw(item, layout, context)


class MATPRO_PT_palette_texture(Panel):
    bl_space_type = 'MATPRO'
    bl_region_type = 'TOOLS'
    bl_label = "Palette menu texture"
    bl_options = {'HIDE_HEADER'}
    bl_context = "texture"

    items=[
        NodeItem("ShaderNodeTexImage"),
        NodeItem("ShaderNodeTexEnvironment"),
        NodeItem("ShaderNodeTexSky"),
        NodeItem("ShaderNodeTexNoise"),
        NodeItem("ShaderNodeTexWave"),
        NodeItem("ShaderNodeTexVoronoi"),
        NodeItem("ShaderNodeTexMusgrave"),
        NodeItem("ShaderNodeTexGradient"),
        NodeItem("ShaderNodeTexMagic"),
        NodeItem("ShaderNodeTexChecker"),
        NodeItem("ShaderNodeTexBrick"),
        NodeItem("ShaderNodeTexPointDensity"),
        NodeItem("ShaderNodeTexIES"),
        NodeItem("ShaderNodeTexWhiteNoise"),
    ]
    
    def draw(self, context):
        layout = self.layout
        layout.shape = 'PREFS'
        layout.scale_y = 1.5

        for item in self.items:
            item.draw(item, layout, context)
        
class MATPRO_PT_palette_color(Panel):
    bl_space_type = 'MATPRO'
    bl_region_type = 'TOOLS'
    bl_label = "Palette menu color"
    bl_options = {'HIDE_HEADER'}
    bl_context = "color"
    
    items=[
        NodeItem("ShaderNodeMix", label="Mix Color", settings={"data_type": "'RGBA'"}),
        NodeItem("ShaderNodeRGBCurve"),
        NodeItem("ShaderNodeInvert"),
        NodeItem("ShaderNodeLightFalloff"),
        NodeItem("ShaderNodeHueSaturation"),
        NodeItem("ShaderNodeGamma"),
        NodeItem("ShaderNodeBrightContrast"),
    ]

    def draw(self, context):
        layout = self.layout
        layout.shape = 'PREFS'
        layout.scale_y = 1.5

        for item in self.items:
            item.draw(item, layout, context)
        
class MATPRO_PT_palette_vector(Panel):
    bl_space_type = 'MATPRO'
    bl_region_type = 'TOOLS'
    bl_label = "Palette menu vector"
    bl_options = {'HIDE_HEADER'}
    bl_context = "vector"

    items=[
        NodeItem("ShaderNodeMapping"),
        NodeItem("ShaderNodeBump"),
        NodeItem("ShaderNodeDisplacement"),
        NodeItem("ShaderNodeVectorDisplacement"),
        NodeItem("ShaderNodeNormalMap"),
        NodeItem("ShaderNodeNormal"),
        NodeItem("ShaderNodeVectorCurve"),
        NodeItem("ShaderNodeVectorRotate"),
        NodeItem("ShaderNodeVectorTransform"),
    ]
    
    def draw(self, context):
        layout = self.layout
        layout.shape = 'PREFS'
        layout.scale_y = 1.5
  
        for item in self.items:
            item.draw(item, layout, context)
        
class MATPRO_PT_palette_converter(Panel):
    bl_space_type = 'MATPRO'
    bl_region_type = 'TOOLS'
    bl_label = "Palette menu converter"
    bl_options = {'HIDE_HEADER'}
    bl_context = "converter"
    
    items=[
        NodeItem("ShaderNodeMapRange"),
        NodeItem("ShaderNodeFloatCurve"),
        NodeItem("ShaderNodeClamp"),
        NodeItem("ShaderNodeMath"),
        NodeItem("ShaderNodeMix"),
        NodeItem("ShaderNodeValToRGB"),
        NodeItem("ShaderNodeRGBToBW"),
        NodeItem("ShaderNodeShaderToRGB", poll=nodeitems_builtins.object_eevee_shader_nodes_poll),
        NodeItem("ShaderNodeVectorMath"),
        NodeItem("ShaderNodeSeparateColor"),
        NodeItem("ShaderNodeCombineColor"),
        NodeItem("ShaderNodeSeparateXYZ"),
        NodeItem("ShaderNodeCombineXYZ"),
        NodeItem("ShaderNodeWavelength"),
        NodeItem("ShaderNodeBlackbody"),
    ]

    def draw(self, context):
        layout = self.layout
        layout.shape = 'PREFS'
        layout.scale_y = 1.5

        for item in self.items:
            item.draw(item, layout, context)


# Material List
class MATPRO_MT_matlist_context_menu(Menu):
    bl_label = "Material List Context Menu"
    
    @classmethod
    def poll(self, context):
        space = context.space_data
        region = context.region
        return space.type == 'MATPRO' and region.type == 'UI' 
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator("matpro.create_material", text="Create Material")
        
        row = layout.row()
        row.operator_context = 'EXEC_DEFAULT'
        row.operator("matpro.select_material", text="Edit Material")
        layout.operator("matpro.assign_material", text="Assign Material")

        layout.operator("matpro.rename_material", text="Rename Material")
        layout.operator("matpro.material_delete", text="Delete Material")


class MATPRO_OT_rename_mat(Operator):
    bl_label = "Rename Material"
    bl_idname = "matpro.rename_material"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Rename Material"

    @classmethod
    def poll(self, context):
        space = context.space_data
        return space.type == 'MATPRO'
    
    def execute(self, context):
        bpy.ops.wm.call_panel(name="MATPRO_PT_rename_mat", keep_open=False)
        return {'FINISHED'}

class MATPRO_PT_rename_mat(Panel):
    bl_space_type = 'MATPRO'
    bl_region_type = 'UI'
    bl_label = "Rename material"
    bl_options = {'HIDE_HEADER', 'INSTANCED'}
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        space = context.space_data
        mat = space.active_material
        
        if mat:
            row = layout.row()
            row.label(text="Material Name")
            row = layout.row(align=True)
            row.activate_init =True
            row.label(icon='NODE')
            row.prop(mat, "name", text="")
        else:
            layout.label(text="No active material")
        

class MATPRO_OT_assign_material(Operator):
    """Assign material from material list"""
    bl_label = "Assign Material"
    bl_idname = "matpro.assign_material"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(self, context):
        space = context.space_data
        return space.type == 'MATPRO' and context.active_object and context.active_object.type != 'EMPTY'
    
    def execute(self, context):
        smatpro = context.space_data
        active_material = smatpro.active_material
        types_that_support_material = {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META',
                                        'GPENCIL', 'VOLUME', 'CURVES', 'POINTCLOUD'}
        user_active_object = context.active_object
        
        if not active_material:
            self.report({'WARNING'}, "No active material to assign")
            return {'CANCELLED'}
        
        for obj in context.selected_objects:
            if obj.type not in types_that_support_material:
                continue
            context.view_layer.objects.active = obj
            
            if obj.mode == 'EDIT':
                ob_slots = obj.material_slots
                has_same_material_slot = False
                for slot in ob_slots:
                    if slot.material == active_material:
                        obj.active_material_index = slot.slot_index
                        has_same_material_slot = True
                        break
                
                if not has_same_material_slot:
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.material_slot_add()
                    bpy.ops.object.mode_set(mode='EDIT')
                    obj.active_material = active_material
                
                bpy.ops.object.material_slot_assign()
                
            else:
                obj.active_material = active_material
        
        context.view_layer.objects.active = user_active_object
        return {'FINISHED'}

class MATPRO_OT_select_material(Operator):
    """Select material from material list"""
    bl_label = "Select Material"
    bl_idname = "matpro.select_material"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}

    material_name: StringProperty(
            name='Material',
            default="",
            description="Material to select in MatPro"
            )

    @classmethod
    def poll(self, context):
        space = context.space_data
        return space.type == 'MATPRO'
    
    def modal(self, context, event):
        if event.type in {'LEFTMOUSE'}:
            if self._timer is not None:         
                # Double click
                self.cancel(context)
                context.area.tag_redraw() # weird but button is not updated without it because modal
                return self.edit_material(context)

        if event.type in {'TIMER'}:
            # Single click
            self.cancel(context)
            context.area.tag_redraw() # weird but button is not updated without it because modal
            return self.set_active_material(context)

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window = context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)   
    
    def execute(self, context):
        return self.edit_material(context)
    
    def edit_material(self, context):
        smatpro = context.space_data
        
        material = bpy.data.materials.get(self.material_name)
        if material is None:
            self.report({'WARNING'}, f"Unable to find material with name '{self.material_name}' to edit it.")
            return {'CANCELLED'}
        
        zero_obj = bpy.data.objects.get('zeroObj')
        if zero_obj is None:
            self.report({'DEBUG'}, f"Unable to find zeroObj.")
            return {'CANCELLED'}
        
        obj = context.active_object
        obj_exists = obj is not None
        current_mode = obj.mode if obj_exists else None
        
        if obj_exists:
            bpy.ops.object.mode_set(mode='OBJECT')
        context.view_layer.objects.active = zero_obj
        zero_obj.active_material = material
        smatpro.active_material = material
        if obj_exists:
            bpy.ops.object.mode_set(mode=current_mode)
        
        return {'FINISHED'} 

    def set_active_material(self, context):
        smatpro = context.space_data
        
        material = bpy.data.materials.get(self.material_name)
        if material is None:
            self.report({'WARNING'}, f"Unable to find material with name '{self.material_name}' to select it.")
            return {'CANCELLED'}
        
        smatpro.active_material = material
                
        return {'FINISHED'}
    

class MATPRO_PT_material_list(Panel):
    bl_space_type = 'MATPRO'
    bl_region_type = 'UI'
    bl_label = "Material list"
    bl_options = {'HIDE_HEADER'}
    bl_category = "Tool"
    
    
    def draw(self, context):
        class FakeMaterial:
            name=""
        
        class AddMaterial:
            name=""
        
        MATERIAL_SIZE = 4
        MATERIAL_SIZE_EST = int(MATERIAL_SIZE * 20 * context.preferences.system.ui_scale)
        MATERIALS_IN_ROW = context.region.width // MATERIAL_SIZE_EST
        
        # this region is too small
        if MATERIALS_IN_ROW == 0:
            return
        
        smatpro = context.space_data
        
        materials_blacklist = {'Dots Stroke'}
        materials = [mat for mat in bpy.data.materials if mat.name not in materials_blacklist]
        materials_len = len(materials) + 1
        
        layout = self.layout
                
        box = layout.box()
        row = None
        
        # create new material button
        materials.append(AddMaterial())
        
        # number of fake materials to add, so it's dividible by MATERIALS_IN_ROW
        fake_materials_to_add = (MATERIALS_IN_ROW - materials_len % MATERIALS_IN_ROW) % MATERIALS_IN_ROW
        for _ in range(fake_materials_to_add):
            materials.append(FakeMaterial())
        
        for idx, mat in enumerate(materials):
            is_active_material = (mat == smatpro.active_material)
            
            if idx % MATERIALS_IN_ROW == 0:
                row = box.row()
                row.alignment = 'LEFT'
            
            col = row.column()
            col.alignment = 'LEFT'
            col.ui_units_x = MATERIAL_SIZE
            col.scale_y = MATERIAL_SIZE
            col.icon_scale = 2
            
            if isinstance(mat, FakeMaterial):
                col.emboss = 'NONE'
                col.label(text="")
            elif isinstance(mat, AddMaterial):
                prop = col.operator("matpro.create_material", text="", icon='ADD')
                set_bsdf_diffuse_nodes_props(prop)
            else:
                mat.id_data.preview_ensure()
                prop = col.matlist_operator("matpro.select_material",
                                    text = "", 
                                    icon_value = mat.preview.icon_id,
                                    shape = 'PREFS' if is_active_material else 'ROUNDBOX',
                                    material = mat,
                                    )
                prop.material_name = mat.name

# Tabs

class MATPRO_OT_close_tab(Operator):
    """Close tab in Pro Material"""
    bl_label = "Close Tab"
    bl_idname = "matpro.close_tab"
    bl_options = {'REGISTER', 'UNDO'}

    tab_index: IntProperty(
        name = "Tab Index",
        default = 0,
    )
    
    @classmethod
    def poll(self, context):
        space = context.space_data
        return space.type == 'MATPRO'
    
    def execute(self, context):
        tab_index = self.tab_index
        obj = context.active_object
        if not obj:
            self.report({'WARNING'}, "No active object to close tab")
            return {'CANCELLED'}

        if context.mode != 'OBJECT':
            self.report({'WARNING'}, "Unable to remove material slot in Edit Mode")
            return {'FINISHED'}
        
        mat_slots = obj.material_slots
        
        if tab_index < 0 or tab_index >= len(mat_slots):
            self.report({'WARNING'}, f"Wrong tab index: {tab_index}")
            return {'CANCELLED'}
        
        obj.active_material_index = tab_index
        bpy.ops.object.material_slot_remove()
        
        return {'FINISHED'}

class MATPRO_OT_select_tab(Operator):
    """Select tab in Pro Materials"""
    bl_label = "Select Tab"
    bl_idname = "matpro.select_tab"
    bl_options = {'REGISTER', 'UNDO'}
    
    tab_index: IntProperty(
        name = "Tab Index",
        default = 0,
    )
    
    @classmethod
    def poll(self, context):
        space = context.space_data
        return space.type == 'MATPRO'
    
    def execute(self, context):
        tab_index = self.tab_index
        obj = context.active_object
        
        if not obj:
            self.report({'WARNING'}, "No active object to select tab")
            return {'CANCELLED'}
        
        mat_slots = obj.material_slots
        
        if tab_index < 0 or tab_index >= len(mat_slots):
            self.report({'WARNING'}, f"Wrong tab index: {tab_index}")
            return {'CANCELLED'}

        obj.active_material_index = tab_index
        return {'FINISHED'}
        

class MATPRO_HT_tabs(Header):
    bl_label = "Tabs Panel"
    bl_space_type = 'MATPRO'
    bl_region_type = 'TOOL_HEADER'
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        if not obj:
            return
        
        mat_slots = obj.material_slots
        mat_slots_len = len(mat_slots)
        
        row = layout.row()
        
        if mat_slots:
            row.separator()
        
        for idx, slot in enumerate(mat_slots):
            material = slot.material
            material_name = material.name if material else "Empty Slot"
            col = row.column()
            col.scale_y = 1.15
            col.ui_units_x = 6
            prop = col.tab("matpro.select_tab", text=material_name[:15], shape='TRAPEZOIDR', tab_type='MATPRO', tab_index=idx)
            prop.tab_index = idx
            if idx < mat_slots_len - 1:
                row.separator()

        sub = layout.row(align=True)
        sub.scale_y = 1.1
        
        if mat_slots:
            sub.separator()
        
        if not obj.protect:
            op = sub.operator("matpro.create_material", text="", icon='PLUS', emboss=False)
            set_bsdf_diffuse_nodes_props(op)
        

classes = (
    NodeLink_Props,
    NodeValue_Props,
    Node_Props,
    MATPRO_HT_header,
    MATPRO_MT_editor_menus,
    MATPRO_MT_edit,
    MATPRO_MT_actions,
    MATPRO_MT_create,
    MATPRO_OT_big_label,
    MATPRO_OT_preview_label,
    MATPRO_PT_preview,
    MATPRO_PT_active_node_properties,
    MATPRO_PT_palette_navbar,
    MATPRO_PT_palette_input,
    MATPRO_PT_palette_output,
    MATPRO_PT_palette_shader,
    MATPRO_PT_palette_texture,
    MATPRO_PT_palette_color,
    MATPRO_PT_palette_vector,
    MATPRO_PT_palette_converter,
    MATPRO_OT_create_material,
    MATPRO_MT_remove,
    MATPRO_OT_PBR_setup,
    MATPRO_PT_material_list,
    MATPRO_OT_select_material,
    MATPRO_MT_matlist_context_menu,
    MATPRO_HT_tabs, 
    MATPRO_OT_remove_unused_slots,
    MATPRO_MT_context_menu,
    MATPRO_OT_merge_by_material,
    MATPRO_OT_close_tab,
    MATPRO_OT_select_tab,
    MATPRO_OT_assign_material,
    MATPRO_PT_label,
    MATPRO_OT_material_duplicate,
    MATPRO_OT_material_delete,
    MATPRO_OT_create_unassigned_material,
    MATPRO_OT_rename_mat,
    MATPRO_PT_rename_mat
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
