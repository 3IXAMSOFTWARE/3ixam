from bpy.types import Menu, Panel, UIList, WindowManager
from bl_ui.properties_grease_pencil_common import (
    GreasePencilSculptAdvancedPanel,
    GreasePencilDisplayPanel,
    GreasePencilBrushFalloff,
)
from bl_ui.properties_paint_common import (
    UnifiedPaintPanel,
    BrushSelectPanel,
    ClonePanel,
    TextureMaskPanel,
    ColorPalettePanel,
    StrokePanel,
    SmoothStrokePanel,
    FalloffPanel,
    DisplayPanel,
    brush_texture_settings,
    brush_mask_texture_settings,
    brush_settings,
    brush_settings_advanced,
    draw_color_settings,
)
from bl_ui.utils import PresetPanel
from bl_ui.space_toolsystem_common import (ToolDef, ToolSelectPanelHelper)
import bpy


class VIEW3D_MT_brush_context_menu(Menu):
    bl_label = "Brush Specials"

    def draw(self, context):
        layout = self.layout

        settings = UnifiedPaintPanel.paint_settings(context)
        brush = getattr(settings, "brush", None)

        # skip if no active brush
        if not brush:
            layout.label(text="No Brushes currently available", icon='INFO')
            return

        # brush paint modes
        layout.menu("VIEW3D_MT_brush_paint_modes")

        # brush tool

        if context.image_paint_object:
            layout.prop_menu_enum(brush, "image_tool")
        elif context.vertex_paint_object:
            layout.prop_menu_enum(brush, "vertex_tool")
        elif context.weight_paint_object:
            layout.prop_menu_enum(brush, "weight_tool")
        elif context.sculpt_object:
            layout.prop_menu_enum(brush, "sculpt_tool")
            layout.operator("brush.reset")
        elif context.tool_settings.curves_sculpt:
            layout.prop_menu_enum(brush, "curves_sculpt_tool")


class VIEW3D_MT_brush_gpencil_context_menu(Menu):
    bl_label = "Brush Specials"

    def draw(self, context):
        layout = self.layout
        ts = context.tool_settings

        settings = None
        if context.mode == 'PAINT_GPENCIL':
            settings = ts.gpencil_paint
        if context.mode == 'SCULPT_GPENCIL':
            settings = ts.gpencil_sculpt_paint
        elif context.mode == 'WEIGHT_GPENCIL':
            settings = ts.gpencil_weight_paint
        elif context.mode == 'VERTEX_GPENCIL':
            settings = ts.gpencil_vertex_paint

        brush = getattr(settings, "brush", None)
        # skip if no active brush
        if not brush:
            layout.label(text="No Brushes currently available", icon='INFO')
            return

        layout.operator("gpencil.brush_reset")
        layout.operator("gpencil.brush_reset_all")


class View3DPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'


# **************** standard tool clusters ******************

# Used by vertex & weight paint
def draw_vpaint_symmetry(layout, vpaint, obj):
    col = layout.column()
    row = col.row(heading="Mirror", align=True)
    row.prop(obj, "use_mesh_mirror_x", text="X", toggle=True)
    row.prop(obj, "use_mesh_mirror_y", text="Y", toggle=True)
    row.prop(obj, "use_mesh_mirror_z", text="Z", toggle=True)

    col = layout.column()
    col.active = not obj.data.use_mirror_vertex_groups
    col.prop(vpaint, "radial_symmetry", text="Radial")


# Most of these panels should not be visible in GP edit modes
def is_not_gpencil_edit_mode(context):
    is_gpmode = (
        context.active_object and
        context.active_object.mode in {'EDIT_GPENCIL', 'PAINT_GPENCIL', 'SCULPT_GPENCIL', 'WEIGHT_GPENCIL'}
    )
    return not is_gpmode


# ********** default tools for object mode ****************


class VIEW3D_PT_tools_object_options(View3DPanel, Panel):
    bl_category = "Tool"
    bl_context = ".objectmode"  # dot on purpose (access from topbar)
    bl_label = "Options"

    def draw(self, context):
        # layout = self.layout
        pass


class VIEW3D_PT_tools_object_options_transform(View3DPanel, Panel):
    bl_category = "Tool"
    bl_context = ".objectmode"  # dot on purpose (access from topbar)
    bl_label = "Transform"
    bl_parent_id = "VIEW3D_PT_tools_object_options"

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.tool_settings

        col = layout.column(heading="Affect Only", align=True)
        col.prop(tool_settings, "use_transform_data_origin", text="Origins")
        col.prop(tool_settings, "use_transform_pivot_point_align", text="Locations")
        col.prop(tool_settings, "use_transform_skip_children", text="Parents")


# ********** default tools for editmode_mesh ****************


class VIEW3D_PT_tools_meshedit_options(View3DPanel, Panel):
    bl_category = "Tool"
    bl_context = ".mesh_edit"  # dot on purpose (access from topbar)
    bl_label = "Options"
    bl_options = {'DEFAULT_CLOSED'}
    bl_ui_units_x = 12

    @classmethod
    def poll(cls, context):
        return context.active_object

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.tool_settings
        ob = context.active_object
        mesh = ob.data

        row = layout.row(align=True, heading="Transform")
        row.prop(tool_settings, "use_transform_correct_face_attributes")

        row = layout.row(align=True)
        row.active = tool_settings.use_transform_correct_face_attributes
        row.prop(tool_settings, "use_transform_correct_keep_connected")

        row = layout.row(align=True, heading="UVs")
        row.prop(tool_settings, "use_edge_path_live_unwrap")

        row = layout.row(heading="Mirror")
        sub = row.row(align=True)
        sub.prop(mesh, "use_mirror_x", text="X", toggle=True)
        sub.prop(mesh, "use_mirror_y", text="Y", toggle=True)
        sub.prop(mesh, "use_mirror_z", text="Z", toggle=True)

        row = layout.row(align=True)
        row.active = ob.data.use_mirror_x or ob.data.use_mirror_y or ob.data.use_mirror_z
        row.prop(mesh, "use_mirror_topology")


class VIEW3D_PT_tools_meshedit_options_automerge(View3DPanel, Panel):
    bl_category = "Tool"
    bl_context = ".mesh_edit"  # dot on purpose (access from topbar)
    bl_label = "Auto Merge"
    bl_parent_id = "VIEW3D_PT_tools_meshedit_options"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def draw_header(self, context):
        tool_settings = context.tool_settings

        self.layout.prop(tool_settings, "use_mesh_automerge", text="", toggle=False)

    def draw(self, context):
        layout = self.layout

        tool_settings = context.tool_settings

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.active = tool_settings.use_mesh_automerge
        col.prop(tool_settings, "use_mesh_automerge_and_split", toggle=False)
        col.prop(tool_settings, "double_threshold", text="Threshold")


# ********** default tools for editmode_armature ****************


class VIEW3D_PT_tools_armatureedit_options(View3DPanel, Panel):
    bl_category = "Tool"
    bl_context = ".armature_edit"  # dot on purpose (access from topbar)
    bl_label = "Options"

    def draw(self, context):
        arm = context.active_object.data

        self.layout.prop(arm, "use_mirror_x")


# ********** default tools for pose-mode ****************

class VIEW3D_PT_tools_posemode_options(View3DPanel, Panel):
    bl_category = "Tool"
    bl_context = ".posemode"  # dot on purpose (access from topbar)
    bl_label = "Pose Options"

    def draw(self, context):
        pose = context.active_object.pose
        layout = self.layout

        tool_settings = context.tool_settings

        layout.prop(pose, "use_auto_ik")
        layout.prop(pose, "use_mirror_x")
        col = layout.column()
        col.active = pose.use_mirror_x and not pose.use_auto_ik
        col.prop(pose, "use_mirror_relative")

        layout.label(text="Affect Only")
        layout.prop(tool_settings, "use_transform_pivot_point_align", text="Locations")

# ********** default tools for paint modes ****************


class TEXTURE_UL_texpaintslots(UIList):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        # mat = data

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon_value=item.icon_value)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="")


class View3DPaintPanel(View3DPanel, UnifiedPaintPanel):
    bl_category = "Tool"


class View3DPaintBrushPanel(View3DPaintPanel):
    @classmethod
    def poll(cls, context):
        mode = cls.get_brush_mode(context)
        return mode is not None


class VIEW3D_PT_tools_particlemode(Panel, View3DPaintPanel):
    bl_context = ".paint_common"  # dot on purpose (access from topbar)
    bl_label = "Particle Tool"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        settings = context.tool_settings.particle_edit
        return (settings and settings.brush and context.particle_edit_object)

    def draw(self, context):
        layout = self.layout

        settings = context.tool_settings.particle_edit
        brush = settings.brush
        tool = settings.tool

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        tool_context = ToolSelectPanelHelper.tool_active_from_context(context)

        if not tool_context:
            # If there is no active tool, then there can't be an active brush.
            tool = None

        if not tool_context.has_datablock:
            # tool.has_datablock is always true for tools that use brushes.
            tool = None

        if tool is not None:
            col = layout.column()
            col.prop(brush, "size", slider=True)
            if tool == 'ADD':
                col.prop(brush, "count")

                col = layout.column()
                col.prop(settings, "use_default_interpolate")
                col.prop(brush, "steps", slider=True)
                col.prop(settings, "default_key_count", slider=True)
            else:
                col.prop(brush, "strength", slider=True)

                if tool == 'LENGTH':
                    layout.row().prop(brush, "length_mode", expand=True)
                elif tool == 'PUFF':
                    layout.row().prop(brush, "puff_mode", expand=True)
                    layout.prop(brush, "use_puff_volume")
                elif tool == 'COMB':
                    col = layout.column(align=False, heading="Deflect Emitter")
                    row = col.row(align=True)
                    sub = row.row(align=True)
                    sub.prop(settings, "use_emitter_deflect", text="")
                    sub = sub.row(align=True)
                    sub.active = settings.use_emitter_deflect
                    sub.prop(settings, "emitter_distance", text="")


# TODO, move to space_view3d.py
class VIEW3D_PT_tools_brush_select(Panel, View3DPaintBrushPanel, BrushSelectPanel):
    bl_context = ".paint_common"
    bl_label = "Brushes"


# TODO, move to space_view3d.py
class VIEW3D_PT_tools_brush_settings(Panel, View3DPaintBrushPanel):
    bl_context = ".paint_common"
    bl_label = "Brush Settings"

    @classmethod
    def poll(cls, context):
        settings = cls.paint_settings(context)
        return settings and settings.brush is not None

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        settings = self.paint_settings(context)
        brush = settings.brush

        brush_settings(layout.column(), context, brush, popover=self.is_popover)


class VIEW3D_PT_tools_brush_settings_advanced(Panel, View3DPaintBrushPanel):
    bl_context = ".paint_common"
    bl_parent_id = "VIEW3D_PT_tools_brush_settings"
    bl_label = "Advanced"
    bl_options = {'DEFAULT_CLOSED'}
    bl_ui_units_x = 14

    @classmethod
    def poll(cls, context):
        mode = cls.get_brush_mode(context)
        return mode is not None and mode != 'SCULPT_CURVES'

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        settings = UnifiedPaintPanel.paint_settings(context)
        brush = settings.brush

        brush_settings_advanced(layout.column(), context, brush, self.is_popover)


class VIEW3D_PT_tools_brush_color(Panel, View3DPaintPanel):
    bl_context = ".paint_common"  # dot on purpose (access from topbar)
    bl_parent_id = "VIEW3D_PT_tools_brush_settings"
    bl_label = "Color Picker"

    @classmethod
    def poll(cls, context):
        settings = cls.paint_settings(context)
        brush = settings.brush

        if context.image_paint_object:
            capabilities = brush.image_paint_capabilities
            return capabilities.has_color
        elif context.vertex_paint_object:
            capabilities = brush.vertex_paint_capabilities
            return capabilities.has_color
        elif context.sculpt_object:
            capabilities = brush.sculpt_capabilities
            return capabilities.has_color

        return False

    def draw(self, context):
        layout = self.layout
        settings = self.paint_settings(context)
        brush = settings.brush

        draw_color_settings(context, layout, brush, color_type=not context.vertex_paint_object)


class VIEW3D_PT_tools_brush_swatches(Panel, View3DPaintPanel, ColorPalettePanel):
    bl_context = ".paint_common"
    bl_parent_id = "VIEW3D_PT_tools_brush_settings"
    bl_label = "Color Palette"
    bl_options = {'DEFAULT_CLOSED'}


class VIEW3D_PT_tools_brush_clone(Panel, View3DPaintPanel, ClonePanel):
    bl_context = ".paint_common"
    bl_parent_id = "VIEW3D_PT_tools_brush_settings"
    bl_label = "Clone from Paint Slot"
    bl_options = {'DEFAULT_CLOSED'}


class VIEW3D_MT_tools_projectpaint_uvlayer(Menu):
    bl_label = "Clone Layer"

    def draw(self, context):
        layout = self.layout

        for i, uv_layer in enumerate(context.active_object.data.uv_layers):
            props = layout.operator("wm.context_set_int", text=uv_layer.name, translate=False)
            props.data_path = "active_object.data.uv_layers.active_index"
            props.value = i


class SelectPaintSlotHelper:
    bl_category = "Tool"

    canvas_source_attr_name = "canvas_source"
    canvas_image_attr_name = "canvas_image"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        settings = context.tool_settings.image_paint
        mode_settings = self.get_mode_settings(context)

        ob = context.active_object

        layout.prop(mode_settings, self.canvas_source_attr_name, text="Mode")
        layout.separator()

        have_image = False

        match getattr(mode_settings, self.canvas_source_attr_name):
            case 'MATERIAL':
                if len(ob.material_slots) > 1:
                    layout.template_list(
                        "MATERIAL_UL_matslots", "layers",
                        ob, "material_slots",
                        ob, "active_material_index", rows=2,
                    )
                mat = ob.active_material
                if mat and mat.texture_paint_images:
                    row = layout.row()
                    row.template_list(
                        "TEXTURE_UL_texpaintslots", "",
                        mat, "texture_paint_slots",
                        mat, "paint_active_slot", rows=2,
                    )

                    if mat.texture_paint_slots:
                        slot = mat.texture_paint_slots[mat.paint_active_slot]
                    else:
                        slot = None

                    have_image = slot is not None
                else:
                    row = layout.row()

                    box = row.box()
                    box.label(text="No Textures")

                sub = row.column(align=True)
                sub.operator_menu_enum("paint.add_texture_paint_slot", "type", icon='ADD', text="")

            case 'IMAGE':
                mesh = ob.data
                uv_text = mesh.uv_layers.active.name if mesh.uv_layers.active else ""
                layout.template_ID(mode_settings, self.canvas_image_attr_name, new="image.new", open="image.open")
                if settings.missing_uvs:
                    layout.operator("paint.add_simple_uvs", icon='ADD', text="Add UVs")
                else:
                    layout.menu("VIEW3D_MT_tools_projectpaint_uvlayer", text=uv_text, translate=False)
                have_image = getattr(settings, self.canvas_image_attr_name) is not None

                self.draw_image_interpolation(layout=layout, mode_settings=mode_settings)

            case 'COLOR_ATTRIBUTE':
                mesh = ob.data

                row = layout.row()
                col = row.column()
                col.template_list(
                    "MESH_UL_color_attributes_selector",
                    "color_attributes",
                    mesh,
                    "color_attributes",
                    mesh.color_attributes,
                    "active_color_index",
                    rows=3,
                )

                col = row.column(align=True)
                col.operator("geometry.color_attribute_add", icon='ADD', text="")
                col.operator("geometry.color_attribute_remove", icon='REMOVE', text="")

        if settings.missing_uvs:
            layout.separator()
            split = layout.split()
            split.label(text="UV Map Needed", icon='INFO')
            split.operator("paint.add_simple_uvs", icon='ADD', text="Add Simple UVs")
        elif have_image:
            layout.separator()
            layout.operator("image.save_all_modified", text="Save All Images", icon='FILE_TICK')


class VIEW3D_PT_slots_projectpaint(SelectPaintSlotHelper, View3DPanel, Panel):
    bl_category = "Tool"
    bl_context = ".imagepaint"  # dot on purpose (access from topbar)
    bl_label = "Texture Slots"

    canvas_source_attr_name = "mode"
    canvas_image_attr_name = "canvas"

    @classmethod
    def poll(cls, context):
        brush = context.tool_settings.image_paint.brush
        return (brush is not None and context.active_object is not None)

    def get_mode_settings(self, context):
        return context.tool_settings.image_paint

    def draw_image_interpolation(self, layout, mode_settings):
        layout.prop(mode_settings, "interpolation", text="")


class VIEW3D_PT_slots_paint_canvas(SelectPaintSlotHelper, View3DPanel, Panel):
    bl_category = "Tool"
    bl_context = ".sculpt_mode"  # dot on purpose (access from topbar)
    bl_label = "Canvas"

    @classmethod
    def poll(cls, context):
        if not context.preferences.experimental.use_sculpt_texture_paint:
            return False

        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        tool = ToolSelectPanelHelper.tool_active_from_context(context)
        if tool is None:
            return False
        return tool.use_paint_canvas

    def get_mode_settings(self, context):
        return context.tool_settings.paint_mode

    def draw_image_interpolation(self, **kwargs):
        pass


class VIEW3D_PT_mask(View3DPanel, Panel):
    bl_category = "Tool"
    bl_context = ".imagepaint"  # dot on purpose (access from topbar)
    bl_label = "Masking"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        pass


# TODO, move to space_view3d.py
class VIEW3D_PT_stencil_projectpaint(View3DPanel, Panel):
    bl_category = "Tool"
    bl_context = ".imagepaint"  # dot on purpose (access from topbar)
    bl_label = "Stencil Mask"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "VIEW3D_PT_mask"
    bl_ui_units_x = 14

    @classmethod
    def poll(cls, context):
        brush = context.tool_settings.image_paint.brush
        ob = context.active_object
        return (brush is not None and ob is not None)

    def draw_header(self, context):
        ipaint = context.tool_settings.image_paint
        self.layout.prop(ipaint, "use_stencil_layer", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.tool_settings
        ipaint = tool_settings.image_paint
        ob = context.active_object
        mesh = ob.data

        col = layout.column()
        col.active = ipaint.use_stencil_layer

        col.label(text="Stencil Image")
        col.template_ID(ipaint, "stencil_image", new="image.new", open="image.open")

        stencil_text = mesh.uv_layer_stencil.name if mesh.uv_layer_stencil else ""

        col.separator()

        split = col.split()
        colsub = split.column()
        colsub.alignment = 'RIGHT'
        colsub.label(text="UV Layer")
        split.column().menu("VIEW3D_MT_tools_projectpaint_stencil", text=stencil_text, translate=False)

        col.separator()

        row = col.row(align=True)
        row.prop(ipaint, "stencil_color", text="Display Color")
        row.prop(ipaint, "invert_stencil", text="", icon='IMAGE_ALPHA')


# TODO, move to space_view3d.py
class VIEW3D_PT_tools_brush_display(Panel, View3DPaintBrushPanel, DisplayPanel):
    bl_context = ".paint_common"
    bl_parent_id = "VIEW3D_PT_tools_brush_settings"
    bl_label = "Cursor"
    bl_options = {'DEFAULT_CLOSED'}
    bl_ui_units_x = 12


# TODO, move to space_view3d.py
class VIEW3D_PT_tools_brush_texture(Panel, View3DPaintPanel):
    bl_context = ".paint_common"
    bl_parent_id = "VIEW3D_PT_tools_brush_settings"
    bl_label = "Texture"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if (
                (settings := cls.paint_settings(context)) and
                (brush := settings.brush)
        ):
            if context.sculpt_object or context.vertex_paint_object:
                return True
            elif context.image_paint_object:
                return (brush.image_tool == 'DRAW')
        return False

    def draw(self, context):
        layout = self.layout

        settings = self.paint_settings(context)
        brush = settings.brush
        tex_slot = brush.texture_slot

        col = layout.column()
        col.template_ID_preview(tex_slot, "texture", new="texture.new", rows=3, cols=8)

        brush_texture_settings(col, brush, context.sculpt_object)


# TODO, move to space_view3d.py
class VIEW3D_PT_tools_mask_texture(Panel, View3DPaintPanel, TextureMaskPanel):
    bl_category = "Tool"
    bl_context = ".imagepaint"  # dot on purpose (access from topbar)
    bl_parent_id = "VIEW3D_PT_tools_brush_settings"
    bl_label = "Texture Mask"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        settings = cls.paint_settings(context)
        return (settings and settings.brush and context.image_paint_object)

    def draw(self, context):
        layout = self.layout

        brush = context.tool_settings.image_paint.brush

        col = layout.column()
        mask_tex_slot = brush.mask_texture_slot

        col.template_ID_preview(mask_tex_slot, "texture", new="texture.new", rows=3, cols=8)

        brush_mask_texture_settings(col, brush)


# TODO, move to space_view3d.py
class VIEW3D_PT_tools_brush_stroke(Panel, View3DPaintPanel, StrokePanel):
    bl_context = ".paint_common"  # dot on purpose (access from topbar)
    bl_label = "Stroke"
    bl_parent_id = "VIEW3D_PT_tools_brush_settings"
    bl_options = {'DEFAULT_CLOSED'}


class VIEW3D_PT_tools_brush_stroke_smooth_stroke(Panel, View3DPaintPanel, SmoothStrokePanel):
    bl_context = ".paint_common"  # dot on purpose (access from topbar)
    bl_label = "Stabilize Stroke"
    bl_parent_id = "VIEW3D_PT_tools_brush_stroke"
    bl_options = {'DEFAULT_CLOSED'}


class VIEW3D_PT_tools_weight_gradient(Panel, View3DPaintPanel):
    # dont give context on purpose to not show this in the generic header toolsettings
    # this is added only in the gradient tool's ToolDef
    # bl_context = ".weightpaint" # dot on purpose (access from topbar)
    bl_label = "Falloff"
    bl_options = {'DEFAULT_CLOSED'}
    # also dont draw as an extra panel in the sidebar (already included in the Brush settings)
    bl_space_type = 'TOPBAR'
    bl_region_type = 'HEADER'

    @classmethod
    def poll(cls, context):
        # since we dont give context above, check mode here (to not show in other modes like sculpt)
        if context.mode != 'PAINT_WEIGHT':
            return False
        settings = context.tool_settings.weight_paint
        if settings is None:
            return False
        brush = settings.brush
        return brush is not None

    def draw(self, context):
        layout = self.layout
        settings = context.tool_settings.weight_paint
        brush = settings.brush

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(brush, "curve_preset", text="")

        if brush.curve_preset == 'CUSTOM':
            layout.template_curve_mapping(brush, "curve", brush=True)

            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator("brush.curve_preset", icon='SMOOTHCURVE', text="").shape = 'SMOOTH'
            row.operator("brush.curve_preset", icon='SPHERECURVE', text="").shape = 'ROUND'
            row.operator("brush.curve_preset", icon='ROOTCURVE', text="").shape = 'ROOT'
            row.operator("brush.curve_preset", icon='SHARPCURVE', text="").shape = 'SHARP'
            row.operator("brush.curve_preset", icon='LINCURVE', text="").shape = 'LINE'
            row.operator("brush.curve_preset", icon='NOCURVE', text="").shape = 'MAX'


# TODO, move to space_view3d.py
class VIEW3D_PT_tools_brush_falloff(Panel, View3DPaintPanel, FalloffPanel):
    bl_context = ".paint_common"  # dot on purpose (access from topbar)
    bl_parent_id = "VIEW3D_PT_tools_brush_settings"
    bl_label = "Falloff"
    bl_options = {'DEFAULT_CLOSED'}


class VIEW3D_PT_tools_brush_falloff_frontface(View3DPaintPanel, Panel):
    bl_context = ".imagepaint"  # dot on purpose (access from topbar)
    bl_label = "Front-Face Falloff"
    bl_parent_id = "VIEW3D_PT_tools_brush_falloff"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.weight_paint_object or context.vertex_paint_object)

    def draw_header(self, context):
        settings = self.paint_settings(context)
        brush = settings.brush

        self.layout.prop(brush, "use_frontface_falloff", text="")

    def draw(self, context):
        settings = self.paint_settings(context)
        brush = settings.brush

        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.active = brush.use_frontface_falloff
        layout.prop(brush, "falloff_angle", text="Angle")


class VIEW3D_PT_tools_brush_falloff_normal(View3DPaintPanel, Panel):
    bl_context = ".imagepaint"  # dot on purpose (access from topbar)
    bl_label = "Normal Falloff"
    bl_parent_id = "VIEW3D_PT_tools_brush_falloff"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.image_paint_object

    def draw_header(self, context):
        tool_settings = context.tool_settings
        ipaint = tool_settings.image_paint

        self.layout.prop(ipaint, "use_normal_falloff", text="")

    def draw(self, context):
        tool_settings = context.tool_settings
        ipaint = tool_settings.image_paint

        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.active = ipaint.use_normal_falloff
        layout.prop(ipaint, "normal_angle", text="Angle")


# TODO, move to space_view3d.py
class VIEW3D_PT_sculpt_dyntopo(Panel, View3DPaintPanel):
    bl_context = ".sculpt_mode"  # dot on purpose (access from topbar)
    bl_label = "Dyntopo"
    bl_options = {'DEFAULT_CLOSED'}
    bl_ui_units_x = 12

    @classmethod
    def poll(cls, context):
        paint_settings = cls.paint_settings(context)
        return (context.sculpt_object and context.tool_settings.sculpt and paint_settings)

    def draw_header(self, context):
        is_popover = self.is_popover
        layout = self.layout
        layout.operator(
            "sculpt.dynamic_topology_toggle",
            icon='CHECKBOX_HLT' if context.sculpt_object.use_dynamic_topology_sculpting else 'CHECKBOX_DEHLT',
            text="",
            emboss=is_popover,
        )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.tool_settings
        sculpt = tool_settings.sculpt
        settings = self.paint_settings(context)
        brush = settings.brush

        col = layout.column()
        col.active = context.sculpt_object.use_dynamic_topology_sculpting

        sub = col.column()
        sub.active = (brush and brush.sculpt_tool != 'MASK')
        if sculpt.detail_type_method in {'CONSTANT', 'MANUAL'}:
            row = sub.row(align=True)
            row.prop(sculpt, "constant_detail_resolution")
            props = row.operator("sculpt.sample_detail_size", text="", icon='EYEDROPPER')
            props.mode = 'DYNTOPO'
        elif (sculpt.detail_type_method == 'BRUSH'):
            sub.prop(sculpt, "detail_percent")
        else:
            sub.prop(sculpt, "detail_size")
        sub.prop(sculpt, "detail_refine_method", text="Refine Method")
        sub.prop(sculpt, "detail_type_method", text="Detailing")

        if sculpt.detail_type_method in {'CONSTANT', 'MANUAL'}:
            col.operator("sculpt.detail_flood_fill")

        col.prop(sculpt, "use_smooth_shading")


class VIEW3D_PT_sculpt_voxel_remesh(Panel, View3DPaintPanel):
    bl_context = ".sculpt_mode"  # dot on purpose (access from topbar)
    bl_label = "Remesh"
    bl_options = {'DEFAULT_CLOSED'}
    bl_ui_units_x = 12

    @classmethod
    def poll(cls, context):
        return (context.sculpt_object and context.tool_settings.sculpt)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        mesh = context.active_object.data
        row = col.row(align=True)
        row.prop(mesh, "remesh_voxel_size")
        props = row.operator("sculpt.sample_detail_size", text="", icon='EYEDROPPER')
        props.mode = 'VOXEL'
        col.prop(mesh, "remesh_voxel_adaptivity")
        col.prop(mesh, "use_remesh_fix_poles")

        col = layout.column(heading="Preserve", align=True)
        col.prop(mesh, "use_remesh_preserve_volume", text="Volume")
        col.prop(mesh, "use_remesh_preserve_paint_mask", text="Paint Mask")
        col.prop(mesh, "use_remesh_preserve_sculpt_face_sets", text="Face Sets")
        col.prop(mesh, "use_remesh_preserve_vertex_colors", text="Color Attributes")

        layout.operator("object.voxel_remesh", text="Remesh")


# TODO, move to space_view3d.py
class VIEW3D_PT_sculpt_options(Panel, View3DPaintPanel):
    bl_context = ".sculpt_mode"  # dot on purpose (access from topbar)
    bl_label = "Options"
    bl_options = {'DEFAULT_CLOSED'}
    bl_ui_units_x = 12

    @classmethod
    def poll(cls, context):
        return (context.sculpt_object and context.tool_settings.sculpt)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.tool_settings
        sculpt = tool_settings.sculpt

        col = layout.column(heading="Display", align=True)
        col.prop(sculpt, "show_low_resolution")
        col.prop(sculpt, "use_sculpt_delay_updates")
        col.prop(sculpt, "use_deform_only")


class VIEW3D_PT_sculpt_options_gravity(Panel, View3DPaintPanel):
    bl_context = ".sculpt_mode"  # dot on purpose (access from topbar)
    bl_parent_id = "VIEW3D_PT_sculpt_options"
    bl_label = "Gravity"

    @classmethod
    def poll(cls, context):
        return (context.sculpt_object and context.tool_settings.sculpt)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.tool_settings
        sculpt = tool_settings.sculpt
        capabilities = sculpt.brush.sculpt_capabilities

        col = layout.column()
        col.active = capabilities.has_gravity
        col.prop(sculpt, "gravity", slider=True, text="Factor")
        col.prop(sculpt, "gravity_object")


# TODO, move to space_view3d.py
class VIEW3D_PT_sculpt_symmetry(Panel, View3DPaintPanel):
    bl_context = ".sculpt_mode"  # dot on purpose (access from topbar)
    bl_label = "Symmetry"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (
            (context.sculpt_object and context.tool_settings.sculpt) and
            # When used in the tool header, this is explicitly included next to the XYZ symmetry buttons.
            (context.region.type != 'TOOL_HEADER')
        )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        sculpt = context.tool_settings.sculpt

        row = layout.row(align=True, heading="Mirror")
        mesh = context.object.data
        row.prop(mesh, "use_mirror_x", text="X", toggle=True)
        row.prop(mesh, "use_mirror_y", text="Y", toggle=True)
        row.prop(mesh, "use_mirror_z", text="Z", toggle=True)

        row = layout.row(align=True, heading="Lock")
        row.prop(sculpt, "lock_x", text="X", toggle=True)
        row.prop(sculpt, "lock_y", text="Y", toggle=True)
        row.prop(sculpt, "lock_z", text="Z", toggle=True)

        row = layout.row(align=True, heading="Tiling")
        row.prop(sculpt, "tile_x", text="X", toggle=True)
        row.prop(sculpt, "tile_y", text="Y", toggle=True)
        row.prop(sculpt, "tile_z", text="Z", toggle=True)

        layout.prop(sculpt, "use_symmetry_feather", text="Feather")
        layout.prop(sculpt, "radial_symmetry", text="Radial")
        layout.prop(sculpt, "tile_offset", text="Tile Offset")

        layout.separator()

        layout.prop(sculpt, "symmetrize_direction")
        layout.operator("sculpt.symmetrize")


class VIEW3D_PT_sculpt_symmetry_for_topbar(Panel):
    bl_space_type = 'TOPBAR'
    bl_region_type = 'HEADER'
    bl_label = "Symmetry"

    draw = VIEW3D_PT_sculpt_symmetry.draw


class VIEW3D_PT_curves_sculpt_symmetry(Panel, View3DPaintPanel):
    bl_context = ".curves_sculpt"  # dot on purpose (access from topbar)
    bl_label = "Symmetry"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'CURVES'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        curves = context.object.data

        row = layout.row(align=True, heading="Mirror")
        row.prop(curves, "use_mirror_x", text="X", toggle=True)
        row.prop(curves, "use_mirror_y", text="Y", toggle=True)
        row.prop(curves, "use_mirror_z", text="Z", toggle=True)


class VIEW3D_PT_curves_sculpt_symmetry_for_topbar(Panel):
    bl_space_type = 'TOPBAR'
    bl_region_type = 'HEADER'
    bl_label = "Symmetry"

    draw = VIEW3D_PT_curves_sculpt_symmetry.draw


# ********** default tools for weight-paint ****************


# TODO, move to space_view3d.py
class VIEW3D_PT_tools_weightpaint_symmetry(Panel, View3DPaintPanel):
    bl_context = ".weightpaint"
    bl_options = {'DEFAULT_CLOSED'}
    bl_label = "Symmetry"

    @classmethod
    def poll(cls, context):
        # When used in the tool header, this is explicitly included next to the XYZ symmetry buttons.
        return (context.region.type != 'TOOL_HEADER')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.tool_settings
        wpaint = tool_settings.weight_paint
        mesh = context.object.data

        layout.prop(mesh, 'use_mirror_vertex_groups')

        draw_vpaint_symmetry(layout, wpaint, context.object)

        row = layout.row()
        row.active = mesh.use_mirror_vertex_groups
        row.prop(mesh, "use_mirror_topology")


class VIEW3D_PT_tools_weightpaint_symmetry_for_topbar(Panel):
    bl_space_type = 'TOPBAR'
    bl_region_type = 'HEADER'
    bl_label = "Symmetry"

    draw = VIEW3D_PT_tools_weightpaint_symmetry.draw


# TODO, move to space_view3d.py
class VIEW3D_PT_tools_weightpaint_options(Panel, View3DPaintPanel):
    bl_context = ".weightpaint"
    bl_label = "Options"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.tool_settings
        wpaint = tool_settings.weight_paint

        col = layout.column()

        col.prop(tool_settings, "use_auto_normalize", text="Auto Normalize")
        col.prop(tool_settings, "use_lock_relative", text="Lock-Relative")
        col.prop(tool_settings, "use_multipaint", text="Multi-Paint")

        col.prop(wpaint, "use_group_restrict")


# ********** default tools for vertex-paint ****************


# TODO, move to space_view3d.py
class VIEW3D_PT_tools_vertexpaint_options(Panel, View3DPaintPanel):
    bl_context = ".vertexpaint"  # dot on purpose (access from topbar)
    bl_label = "Options"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, _context):
        # This is currently unused, since there aren't any Vertex Paint mode specific options.
        return False

    def draw(self, _context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False


# TODO, move to space_view3d.py
class VIEW3D_PT_tools_vertexpaint_symmetry(Panel, View3DPaintPanel):
    bl_context = ".vertexpaint"  # dot on purpose (access from topbar)
    bl_options = {'DEFAULT_CLOSED'}
    bl_label = "Symmetry"

    @classmethod
    def poll(cls, context):
        # When used in the tool header, this is explicitly included next to the XYZ symmetry buttons.
        return (context.region.type != 'TOOL_HEADER')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.tool_settings
        vpaint = tool_settings.vertex_paint

        draw_vpaint_symmetry(layout, vpaint, context.object)


class VIEW3D_PT_tools_vertexpaint_symmetry_for_topbar(Panel):
    bl_space_type = 'TOPBAR'
    bl_region_type = 'HEADER'
    bl_label = "Symmetry"

    draw = VIEW3D_PT_tools_vertexpaint_symmetry.draw


# ********** default tools for texture-paint ****************


# TODO, move to space_view3d.py
class VIEW3D_PT_tools_imagepaint_options_external(Panel, View3DPaintPanel):
    bl_context = ".imagepaint"  # dot on purpose (access from topbar)
    bl_label = "External"
    bl_parent_id = "VIEW3D_PT_tools_imagepaint_options"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.tool_settings
        ipaint = tool_settings.image_paint

        layout.prop(ipaint, "screen_grab_size", text="Screen Grab Size")

        layout.separator()

        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
        col = flow.column()
        col.operator("image.project_edit", text="Quick Edit")
        col = flow.column()
        col.operator("image.project_apply", text="Apply")
        col = flow.column()
        col.operator("paint.project_image", text="Apply Camera Image")


# TODO, move to space_view3d.py
class VIEW3D_PT_tools_imagepaint_symmetry(Panel, View3DPaintPanel):
    bl_context = ".imagepaint"  # dot on purpose (access from topbar)
    bl_label = "Symmetry"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        # When used in the tool header, this is explicitly included next to the XYZ symmetry buttons.
        return (context.region.type != 'TOOL_HEADER')

    def draw(self, context):
        layout = self.layout

        split = layout.split()

        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text="Mirror")

        col = split.column()

        row = col.row(align=True)
        mesh = context.object.data
        row.prop(mesh, "use_mirror_x", text="X", toggle=True)
        row.prop(mesh, "use_mirror_y", text="Y", toggle=True)
        row.prop(mesh, "use_mirror_z", text="Z", toggle=True)


# TODO, move to space_view3d.py
class VIEW3D_PT_tools_imagepaint_options(View3DPaintPanel, Panel):
    bl_context = ".imagepaint"  # dot on purpose (access from topbar)
    bl_label = "Options"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        brush = context.tool_settings.image_paint.brush
        return (brush is not None)

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.tool_settings
        ipaint = tool_settings.image_paint

        layout.prop(ipaint, "seam_bleed")
        layout.prop(ipaint, "dither", slider=True)

        col = layout.column()
        col.prop(ipaint, "use_occlude")
        col.prop(ipaint, "use_backface_culling", text="Backface Culling")


class VIEW3D_PT_tools_imagepaint_options_cavity(View3DPaintPanel, Panel):
    bl_context = ".imagepaint"  # dot on purpose (access from topbar)
    bl_label = "Cavity Mask"
    bl_parent_id = "VIEW3D_PT_mask"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        tool_settings = context.tool_settings
        ipaint = tool_settings.image_paint

        self.layout.prop(ipaint, "use_cavity", text="")

    def draw(self, context):
        layout = self.layout

        tool_settings = context.tool_settings
        ipaint = tool_settings.image_paint

        layout.active = ipaint.use_cavity

        layout.template_curve_mapping(ipaint, "cavity_curve", brush=True,
                                      use_negative_slope=True)


# TODO, move to space_view3d.py
class VIEW3D_PT_imagepaint_options(View3DPaintPanel):
    bl_label = "Options"

    @classmethod
    def poll(cls, _context):
        # This is currently unused, since there aren't any Vertex Paint mode specific options.
        return False
        # return (context.image_paint_object and context.tool_settings.image_paint)

    def draw(self, _context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False


class VIEW3D_MT_tools_projectpaint_stencil(Menu):
    bl_label = "Mask Layer"

    def draw(self, context):
        layout = self.layout
        for i, uv_layer in enumerate(context.active_object.data.uv_layers):
            props = layout.operator("wm.context_set_int", text=uv_layer.name, translate=False)
            props.data_path = "active_object.data.uv_layer_stencil_index"
            props.value = i


# TODO, move to space_view3d.py
class VIEW3D_PT_tools_particlemode_options(View3DPanel, Panel):
    """Default tools for particle mode"""
    bl_category = "Tool"
    bl_context = ".particlemode"
    bl_label = "Options"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        pe = context.tool_settings.particle_edit
        ob = pe.object

        layout.prop(pe, "type", text="Editing Type")

        ptcache = None

        if pe.type == 'PARTICLES':
            if ob.particle_systems:
                if len(ob.particle_systems) > 1:
                    layout.template_list("UI_UL_list", "particle_systems", ob, "particle_systems",
                                         ob.particle_systems, "active_index", rows=2, maxrows=3)

                ptcache = ob.particle_systems.active.point_cache
        else:
            for md in ob.modifiers:
                if md.type == pe.type:
                    ptcache = md.point_cache

        if ptcache and len(ptcache.point_caches) > 1:
            layout.template_list("UI_UL_list", "particles_point_caches", ptcache, "point_caches",
                                 ptcache.point_caches, "active_index", rows=2, maxrows=3)

        if not pe.is_editable:
            layout.label(text="Point cache must be baked")
            layout.label(text="in memory to enable editing!")

        col = layout.column(align=True)
        col.active = pe.is_editable

        if not pe.is_hair:
            col.prop(pe, "use_auto_velocity", text="Auto-Velocity")
            col.separator()

        sub = col.column(align=True, heading="Mirror")
        sub.prop(ob.data, "use_mirror_x")
        if pe.tool == 'ADD':
            sub.prop(ob.data, "use_mirror_topology")
        col.separator()

        sub = col.column(align=True, heading="Preserve")
        sub.prop(pe, "use_preserve_length", text="Strand Lengths")
        sub.prop(pe, "use_preserve_root", text="Root Positions")


class VIEW3D_PT_tools_particlemode_options_shapecut(View3DPanel, Panel):
    """Default tools for particle mode"""
    bl_category = "Tool"
    bl_parent_id = "VIEW3D_PT_tools_particlemode_options"
    bl_label = "Cut Particles to Shape"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        pe = context.tool_settings.particle_edit

        layout.prop(pe, "shape_object")
        layout.operator("particle.shape_cut", text="Cut")


class VIEW3D_PT_tools_particlemode_options_display(View3DPanel, Panel):
    """Default tools for particle mode"""
    bl_category = "Tool"
    bl_parent_id = "VIEW3D_PT_tools_particlemode_options"
    bl_label = "Viewport Display"

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        pe = context.tool_settings.particle_edit

        col = layout.column()
        col.active = pe.is_editable
        col.prop(pe, "display_step", text="Path Steps")
        if pe.is_hair:
            col.prop(pe, "show_particles", text="Children")
        else:
            if pe.type == 'PARTICLES':
                col.prop(pe, "show_particles", text="Particles")
            col = layout.column(align=False, heading="Fade Time")
            row = col.row(align=True)
            sub = row.row(align=True)
            sub.prop(pe, "use_fade_time", text="")
            sub = sub.row(align=True)
            sub.active = pe.use_fade_time
            sub.prop(pe, "fade_frames", slider=True, text="")


# ********** grease pencil object tool panels ****************

# Grease Pencil drawing brushes

def tool_use_brush(context):
    from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
    tool = ToolSelectPanelHelper.tool_active_from_context(context)
    if tool and tool.has_datablock is False:
        return False

    return True


class GreasePencilPaintPanel:
    bl_context = ".greasepencil_paint"
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        if context.space_data.type in {'VIEW_3D', 'PROPERTIES'}:
            if context.gpencil_data is None:
                return False

            # Hide for tools not using bruhses
            if tool_use_brush(context) is False:
                return False

            gpd = context.gpencil_data
            return bool(gpd.is_stroke_paint_mode)
        else:
            return True


class VIEW3D_PT_tools_grease_pencil_brush_select(Panel, View3DPanel, GreasePencilPaintPanel):
    bl_label = "Brushes"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.scene.tool_settings
        gpencil_paint = tool_settings.gpencil_paint

        row = layout.row()
        row.column().template_ID_preview(gpencil_paint, "brush", new="brush.add_gpencil", rows=3, cols=8)

        col = row.column()
        col.menu("VIEW3D_MT_brush_gpencil_context_menu", icon='DOWNARROW_HLT', text="")

        if context.mode == 'PAINT_GPENCIL':
            brush = tool_settings.gpencil_paint.brush
            if brush is not None:
                col.prop(brush, "use_custom_icon", toggle=True, icon='FILE_IMAGE', text="")

                if brush.use_custom_icon:
                    layout.row().prop(brush, "icon_filepath", text="")


class VIEW3D_PT_tools_grease_pencil_brush_settings(Panel, View3DPanel, GreasePencilPaintPanel):
    bl_label = "Brush Settings"
    bl_options = {'DEFAULT_CLOSED'}

    # What is the point of brush presets? Seems to serve the exact same purpose as brushes themselves??
    def draw_header_preset(self, _context):
        VIEW3D_PT_gpencil_brush_presets.draw_panel_header(self.layout)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.scene.tool_settings
        gpencil_paint = tool_settings.gpencil_paint

        brush = gpencil_paint.brush

        if brush is not None:
            gp_settings = brush.gpencil_settings

            if brush.gpencil_tool in {'DRAW', 'FILL'}:
                row = layout.row(align=True)
                row_mat = row.row()
                if gp_settings.use_material_pin:
                    row_mat.template_ID(gp_settings, "material", live_icon=True)
                else:
                    row_mat.template_ID(context.active_object, "active_material", live_icon=True)
                    row_mat.enabled = False  # will otherwise allow changing material in active slot

                row.prop(gp_settings, "use_material_pin", text="")

            if not self.is_popover:
                from bl_ui.properties_paint_common import (
                    brush_basic_gpencil_paint_settings,
                )
                brush_basic_gpencil_paint_settings(layout, context, brush, compact=False)


class VIEW3D_PT_tools_grease_pencil_brush_advanced(View3DPanel, Panel):
    bl_context = ".greasepencil_paint"
    bl_label = "Advanced"
    bl_parent_id = 'VIEW3D_PT_tools_grease_pencil_brush_settings'
    bl_category = "Tool"
    bl_options = {'DEFAULT_CLOSED'}
    bl_ui_units_x = 13

    @classmethod
    def poll(cls, context):
        brush = context.tool_settings.gpencil_paint.brush
        return brush is not None and brush.gpencil_tool not in {'ERASE', 'TINT'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.scene.tool_settings
        gpencil_paint = tool_settings.gpencil_paint
        brush = gpencil_paint.brush
        gp_settings = brush.gpencil_settings

        col = layout.column(align=True)
        if brush is not None:
            if brush.gpencil_tool != 'FILL':
                col.prop(gp_settings, "input_samples")
                col.separator()

                col.prop(gp_settings, "active_smooth_factor")
                col.separator()

                col.prop(gp_settings, "angle", slider=True)
                col.prop(gp_settings, "angle_factor", text="Factor", slider=True)

                ob = context.object
                ma = None
                if ob and brush.gpencil_settings.use_material_pin is False:
                    ma = ob.active_material
                elif brush.gpencil_settings.material:
                    ma = brush.gpencil_settings.material

                col.separator()
                col.prop(gp_settings, "hardness", slider=True)
                subcol = col.column(align=True)
                if ma and ma.grease_pencil.mode == 'LINE':
                    subcol.enabled = False
                subcol.prop(gp_settings, "aspect")

            elif brush.gpencil_tool == 'FILL':
                row = col.row(align=True)
                row.prop(gp_settings, "fill_draw_mode", text="Boundary")
                row.prop(
                    gp_settings,
                    "show_fill_boundary",
                    icon='HIDE_OFF' if gp_settings.show_fill_boundary else 'HIDE_ON',
                    text="",
                )

                col.separator()
                row = col.row(align=True)
                row.prop(gp_settings, "fill_layer_mode", text="Layers")

                col.separator()
                col.prop(gp_settings, "fill_simplify_level", text="Simplify")
                if gp_settings.fill_draw_mode != 'STROKE':
                    col = layout.column(align=False, heading="Ignore Transparent")
                    col.use_property_decorate = False
                    row = col.row(align=True)
                    sub = row.row(align=True)
                    sub.prop(gp_settings, "show_fill", text="")
                    sub = sub.row(align=True)
                    sub.active = gp_settings.show_fill
                    sub.prop(gp_settings, "fill_threshold", text="")

                col.separator()
                row = col.row(align=True)
                row.prop(gp_settings, "use_fill_limit")


class VIEW3D_PT_tools_grease_pencil_brush_stroke(Panel, View3DPanel):
    bl_context = ".greasepencil_paint"
    bl_parent_id = 'VIEW3D_PT_tools_grease_pencil_brush_settings'
    bl_label = "Stroke"
    bl_category = "Tool"
    bl_options = {'DEFAULT_CLOSED'}
    bl_ui_units_x = 12

    @classmethod
    def poll(cls, context):
        brush = context.tool_settings.gpencil_paint.brush
        return brush is not None and brush.gpencil_tool == 'DRAW'

    def draw(self, _context):
        # layout = self.layout
        pass


class VIEW3D_PT_tools_grease_pencil_brush_stabilizer(Panel, View3DPanel):
    bl_context = ".greasepencil_paint"
    bl_parent_id = 'VIEW3D_PT_tools_grease_pencil_brush_stroke'
    bl_label = "Stabilize Stroke"
    bl_category = "Tool"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        brush = context.tool_settings.gpencil_paint.brush
        return brush is not None and brush.gpencil_tool == 'DRAW'

    def draw_header(self, context):
        if self.is_popover:
            return

        brush = context.tool_settings.gpencil_paint.brush
        gp_settings = brush.gpencil_settings
        self.layout.prop(gp_settings, "use_settings_stabilizer", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        brush = context.tool_settings.gpencil_paint.brush
        gp_settings = brush.gpencil_settings

        if self.is_popover:
            row = layout.row()
            row.prop(gp_settings, "use_settings_stabilizer", text="")
            row.label(text=self.bl_label)

        col = layout.column()
        col.active = gp_settings.use_settings_stabilizer

        col.prop(brush, "smooth_stroke_radius", text="Radius", slider=True)
        col.prop(brush, "smooth_stroke_factor", text="Factor", slider=True)


class VIEW3D_PT_tools_grease_pencil_brush_post_processing(View3DPanel, Panel):
    bl_context = ".greasepencil_paint"
    bl_parent_id = 'VIEW3D_PT_tools_grease_pencil_brush_stroke'
    bl_label = "Post-Processing"
    bl_category = "Tool"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        brush = context.tool_settings.gpencil_paint.brush
        return brush is not None and brush.gpencil_tool not in {'ERASE', 'FILL', 'TINT'}

    def draw_header(self, context):
        if self.is_popover:
            return

        brush = context.tool_settings.gpencil_paint.brush
        gp_settings = brush.gpencil_settings
        self.layout.prop(gp_settings, "use_settings_postprocess", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        brush = context.tool_settings.gpencil_paint.brush
        gp_settings = brush.gpencil_settings

        if self.is_popover:
            row = layout.row()
            row.prop(gp_settings, "use_settings_postprocess", text="")
            row.label(text=self.bl_label)

        col = layout.column()
        col.active = gp_settings.use_settings_postprocess

        col1 = col.column(align=True)
        col1.prop(gp_settings, "pen_smooth_factor")
        col1.prop(gp_settings, "pen_smooth_steps")

        col1 = col.column(align=True)
        col1.prop(gp_settings, "pen_subdivision_steps")

        col1 = col.column(align=True)
        col1.prop(gp_settings, "simplify_factor")

        col1 = col.column(align=True)
        col1.prop(gp_settings, "use_trim")

        col.separator()

        row = col.row(heading="Outline", align=True)
        row.prop(gp_settings, "use_settings_outline", text="")
        row2 = row.row(align=True)
        row2.enabled = gp_settings.use_settings_outline
        row2.prop(gp_settings, "material_alt", text="")

        row2 = col.row(align=True)
        row2.enabled = gp_settings.use_settings_outline
        row2.prop(gp_settings, "outline_thickness_factor")


class VIEW3D_PT_tools_grease_pencil_brush_random(View3DPanel, Panel):
    bl_context = ".greasepencil_paint"
    bl_parent_id = 'VIEW3D_PT_tools_grease_pencil_brush_stroke'
    bl_label = "Randomize"
    bl_category = "Tool"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        brush = context.tool_settings.gpencil_paint.brush
        return brush is not None and brush.gpencil_tool not in {'ERASE', 'FILL', 'TINT'}

    def draw_header(self, context):
        if self.is_popover:
            return

        brush = context.tool_settings.gpencil_paint.brush
        gp_settings = brush.gpencil_settings
        self.layout.prop(gp_settings, "use_settings_random", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.tool_settings
        brush = tool_settings.gpencil_paint.brush
        mode = tool_settings.gpencil_paint.color_mode
        gp_settings = brush.gpencil_settings

        if self.is_popover:
            row = layout.row()
            row.prop(gp_settings, "use_settings_random", text="")
            row.label(text=self.bl_label)

        col = layout.column()
        col.enabled = gp_settings.use_settings_random

        row = col.row(align=True)
        row.prop(gp_settings, "random_pressure", text="Radius", slider=True)
        row.prop(gp_settings, "use_stroke_random_radius", text="", icon='GP_SELECT_STROKES')
        row.prop(gp_settings, "use_random_press_radius", text="", icon='STYLUS_PRESSURE')
        if gp_settings.use_random_press_radius and self.is_popover is False:
            col.template_curve_mapping(gp_settings, "curve_random_pressure", brush=True,
                                       use_negative_slope=True)

        row = col.row(align=True)
        row.prop(gp_settings, "random_strength", text="Strength", slider=True)
        row.prop(gp_settings, "use_stroke_random_strength", text="", icon='GP_SELECT_STROKES')
        row.prop(gp_settings, "use_random_press_strength", text="", icon='STYLUS_PRESSURE')
        if gp_settings.use_random_press_strength and self.is_popover is False:
            col.template_curve_mapping(gp_settings, "curve_random_strength", brush=True,
                                       use_negative_slope=True)

        row = col.row(align=True)
        row.prop(gp_settings, "uv_random", text="UV", slider=True)
        row.prop(gp_settings, "use_stroke_random_uv", text="", icon='GP_SELECT_STROKES')
        row.prop(gp_settings, "use_random_press_uv", text="", icon='STYLUS_PRESSURE')
        if gp_settings.use_random_press_uv and self.is_popover is False:
            col.template_curve_mapping(gp_settings, "curve_random_uv", brush=True,
                                       use_negative_slope=True)

        col.separator()

        col1 = col.column(align=True)
        col1.enabled = mode == 'VERTEXCOLOR' and gp_settings.use_settings_random
        row = col1.row(align=True)
        row.prop(gp_settings, "random_hue_factor", slider=True)
        row.prop(gp_settings, "use_stroke_random_hue", text="", icon='GP_SELECT_STROKES')
        row.prop(gp_settings, "use_random_press_hue", text="", icon='STYLUS_PRESSURE')
        if gp_settings.use_random_press_hue and self.is_popover is False:
            col1.template_curve_mapping(gp_settings, "curve_random_hue", brush=True,
                                        use_negative_slope=True)

        row = col1.row(align=True)
        row.prop(gp_settings, "random_saturation_factor", slider=True)
        row.prop(gp_settings, "use_stroke_random_sat", text="", icon='GP_SELECT_STROKES')
        row.prop(gp_settings, "use_random_press_sat", text="", icon='STYLUS_PRESSURE')
        if gp_settings.use_random_press_sat and self.is_popover is False:
            col1.template_curve_mapping(gp_settings, "curve_random_saturation", brush=True,
                                        use_negative_slope=True)

        row = col1.row(align=True)
        row.prop(gp_settings, "random_value_factor", slider=True)
        row.prop(gp_settings, "use_stroke_random_val", text="", icon='GP_SELECT_STROKES')
        row.prop(gp_settings, "use_random_press_val", text="", icon='STYLUS_PRESSURE')
        if gp_settings.use_random_press_val and self.is_popover is False:
            col1.template_curve_mapping(gp_settings, "curve_random_value", brush=True,
                                        use_negative_slope=True)

        col.separator()

        row = col.row(align=True)
        row.prop(gp_settings, "pen_jitter", slider=True)
        row.prop(gp_settings, "use_jitter_pressure", text="", icon='STYLUS_PRESSURE')
        if gp_settings.use_jitter_pressure and self.is_popover is False:
            col.template_curve_mapping(gp_settings, "curve_jitter", brush=True,
                                       use_negative_slope=True)


class VIEW3D_PT_tools_grease_pencil_brush_paint_falloff(GreasePencilBrushFalloff, Panel, View3DPaintPanel):
    bl_context = ".greasepencil_paint"
    bl_label = "Falloff"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        ts = context.tool_settings
        settings = ts.gpencil_paint
        brush = settings.brush
        if brush is None:
            return False

        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        tool = ToolSelectPanelHelper.tool_active_from_context(context)
        if tool and tool.idname != 'builtin_brush.Tint':
            return False

        gptool = brush.gpencil_tool

        return (settings and settings.brush and settings.brush.curve and gptool == 'TINT')


class VIEW3D_PT_tools_grease_pencil_brush_gap_closure(View3DPanel, Panel):
    bl_context = ".greasepencil_paint"
    bl_parent_id = 'VIEW3D_PT_tools_grease_pencil_brush_advanced'
    bl_label = "Gap Closure"
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        brush = context.tool_settings.gpencil_paint.brush
        return brush is not None and brush.gpencil_tool == 'FILL'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.tool_settings
        brush = tool_settings.gpencil_paint.brush
        gp_settings = brush.gpencil_settings

        col = layout.column()

        col.prop(gp_settings, "extend_stroke_factor", text="Size")
        row = col.row(align=True)
        row.prop(gp_settings, "fill_extend_mode", text="Mode")
        row = col.row(align=True)
        row.prop(gp_settings, "show_fill_extend", text="Visual Aids")

        if gp_settings.fill_extend_mode == 'EXTEND':
            row = col.row(align=True)
            row.prop(gp_settings, "use_collide_strokes")


# Grease Pencil stroke sculpting tools
class GreasePencilSculptPanel:
    bl_context = ".greasepencil_sculpt"
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        if context.space_data.type in {'VIEW_3D', 'PROPERTIES'}:
            if context.gpencil_data is None:
                return False

            gpd = context.gpencil_data
            return bool(gpd.is_stroke_sculpt_mode)
        else:
            return True


class VIEW3D_PT_tools_grease_pencil_sculpt_select(Panel, View3DPanel, GreasePencilSculptPanel):
    bl_label = "Brushes"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.scene.tool_settings
        gpencil_paint = tool_settings.gpencil_sculpt_paint

        row = layout.row()
        row.column().template_ID_preview(gpencil_paint, "brush", new="brush.add_gpencil", rows=3, cols=8)

        col = row.column()
        col.menu("VIEW3D_MT_brush_gpencil_context_menu", icon='DOWNARROW_HLT', text="")

        if context.mode == 'SCULPT_GPENCIL':
            brush = tool_settings.gpencil_sculpt_paint.brush
            if brush is not None:
                col.prop(brush, "use_custom_icon", toggle=True, icon='FILE_IMAGE', text="")

                if (brush.use_custom_icon):
                    layout.row().prop(brush, "icon_filepath", text="")


class VIEW3D_PT_tools_grease_pencil_sculpt_settings(Panel, View3DPanel, GreasePencilSculptPanel):
    bl_label = "Brush Settings"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.scene.tool_settings
        settings = tool_settings.gpencil_sculpt_paint
        brush = settings.brush

        if not self.is_popover:
            from bl_ui.properties_paint_common import (
                brush_basic_gpencil_sculpt_settings,
            )
            brush_basic_gpencil_sculpt_settings(layout, context, brush)


class VIEW3D_PT_tools_grease_pencil_brush_sculpt_falloff(GreasePencilBrushFalloff, Panel, View3DPaintPanel):
    bl_context = ".greasepencil_sculpt"
    bl_label = "Falloff"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        ts = context.tool_settings
        settings = ts.gpencil_sculpt_paint
        return (settings and settings.brush and settings.brush.curve)


class VIEW3D_PT_tools_grease_pencil_sculpt_brush_advanced(GreasePencilSculptAdvancedPanel, View3DPanel, Panel):
    bl_context = ".greasepencil_sculpt"
    bl_label = "Advanced"
    bl_parent_id = 'VIEW3D_PT_tools_grease_pencil_sculpt_settings'
    bl_category = "Tool"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        brush = context.tool_settings.gpencil_sculpt_paint.brush
        if brush is None:
            return False

        tool = brush.gpencil_sculpt_tool
        return tool != 'CLONE'


class VIEW3D_PT_tools_grease_pencil_sculpt_brush_popover(GreasePencilSculptAdvancedPanel, View3DPanel, Panel):
    bl_context = ".greasepencil_sculpt"
    bl_label = "Brush"
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        if context.region.type != 'TOOL_HEADER':
            return False

        brush = context.tool_settings.gpencil_sculpt_paint.brush
        if brush is None:
            return False

        tool = brush.gpencil_sculpt_tool
        return tool != 'CLONE'


# Grease Pencil weight painting tools
class GreasePencilWeightPanel:
    bl_context = ".greasepencil_weight"
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        if context.space_data.type in {'VIEW_3D', 'PROPERTIES'}:
            if context.gpencil_data is None:
                return False

            gpd = context.gpencil_data
            return bool(gpd.is_stroke_weight_mode)
        else:
            return True


class VIEW3D_PT_tools_grease_pencil_weight_paint_select(View3DPanel, Panel, GreasePencilWeightPanel):
    bl_label = "Brushes"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.scene.tool_settings
        gpencil_paint = tool_settings.gpencil_weight_paint

        row = layout.row()
        row.column().template_ID_preview(gpencil_paint, "brush", new="brush.add_gpencil", rows=3, cols=8)

        col = row.column()
        col.menu("VIEW3D_MT_brush_gpencil_context_menu", icon='DOWNARROW_HLT', text="")

        if context.mode == 'WEIGHT_GPENCIL':
            brush = tool_settings.gpencil_weight_paint.brush
            if brush is not None:
                col.prop(brush, "use_custom_icon", toggle=True, icon='FILE_IMAGE', text="")

                if (brush.use_custom_icon):
                    layout.row().prop(brush, "icon_filepath", text="")


class VIEW3D_PT_tools_grease_pencil_weight_paint_settings(Panel, View3DPanel, GreasePencilWeightPanel):
    bl_label = "Brush Settings"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.scene.tool_settings
        settings = tool_settings.gpencil_weight_paint
        brush = settings.brush

        if not self.is_popover:
            from bl_ui.properties_paint_common import (
                brush_basic_gpencil_weight_settings,
            )
            brush_basic_gpencil_weight_settings(layout, context, brush)


class VIEW3D_PT_tools_grease_pencil_brush_weight_falloff(GreasePencilBrushFalloff, Panel, View3DPaintPanel):
    bl_context = ".greasepencil_weight"
    bl_label = "Falloff"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        ts = context.tool_settings
        settings = ts.gpencil_weight_paint
        brush = settings.brush
        return (brush and brush.curve)


# Grease Pencil vertex painting tools
class GreasePencilVertexPanel:
    bl_context = ".greasepencil_vertex"
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        if context.space_data.type in {'VIEW_3D', 'PROPERTIES'}:
            if context.gpencil_data is None:
                return False

            gpd = context.gpencil_data
            return bool(gpd.is_stroke_vertex_mode)
        else:
            return True


class VIEW3D_PT_tools_grease_pencil_vertex_paint_select(View3DPanel, Panel, GreasePencilVertexPanel):
    bl_label = "Brushes"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.scene.tool_settings
        gpencil_paint = tool_settings.gpencil_vertex_paint

        row = layout.row()
        row.column().template_ID_preview(gpencil_paint, "brush", new="brush.add_gpencil", rows=3, cols=8)

        col = row.column()
        col.menu("VIEW3D_MT_brush_gpencil_context_menu", icon='DOWNARROW_HLT', text="")

        if context.mode == 'VERTEX_GPENCIL':
            brush = tool_settings.gpencil_vertex_paint.brush
            if brush is not None:
                col.prop(brush, "use_custom_icon", toggle=True, icon='FILE_IMAGE', text="")

                if (brush.use_custom_icon):
                    layout.row().prop(brush, "icon_filepath", text="")


class VIEW3D_PT_tools_grease_pencil_vertex_paint_settings(Panel, View3DPanel, GreasePencilVertexPanel):
    bl_label = "Brush Settings"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        tool_settings = context.scene.tool_settings
        settings = tool_settings.gpencil_vertex_paint
        brush = settings.brush

        if not self.is_popover:
            from bl_ui.properties_paint_common import (
                brush_basic_gpencil_vertex_settings,
            )
            brush_basic_gpencil_vertex_settings(layout, context, brush)


class VIEW3D_PT_tools_grease_pencil_brush_vertex_color(View3DPanel, Panel):
    bl_context = ".greasepencil_vertex"
    bl_label = "Color"
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        ob = context.object
        ts = context.tool_settings
        settings = ts.gpencil_vertex_paint
        brush = settings.brush

        if ob is None or brush is None:
            return False

        if context.region.type == 'TOOL_HEADER' or brush.gpencil_vertex_tool in {'BLUR', 'AVERAGE', 'SMEAR'}:
            return False

        return True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        ts = context.tool_settings
        settings = ts.gpencil_vertex_paint
        brush = settings.brush

        col = layout.column()

        col.template_color_picker(brush, "color", value_slider=True)

        sub_row = col.row(align=True)
        sub_row.prop(brush, "color", text="")
        sub_row.prop(brush, "secondary_color", text="")

        sub_row.operator("gpencil.tint_flip", icon='FILE_REFRESH', text="")


class VIEW3D_PT_tools_grease_pencil_brush_vertex_falloff(GreasePencilBrushFalloff, Panel, View3DPaintPanel):
    bl_context = ".greasepencil_vertex"
    bl_label = "Falloff"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        ts = context.tool_settings
        settings = ts.gpencil_vertex_paint
        return (settings and settings.brush and settings.brush.curve)


class VIEW3D_PT_tools_grease_pencil_brush_vertex_palette(View3DPanel, Panel):
    bl_context = ".greasepencil_vertex"
    bl_label = "Palette"
    bl_category = "Tool"
    bl_parent_id = 'VIEW3D_PT_tools_grease_pencil_brush_vertex_color'

    @classmethod
    def poll(cls, context):
        ob = context.object
        ts = context.tool_settings
        settings = ts.gpencil_vertex_paint
        brush = settings.brush

        if ob is None or brush is None:
            return False

        if brush.gpencil_vertex_tool in {'BLUR', 'AVERAGE', 'SMEAR'}:
            return False

        return True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        ts = context.tool_settings
        settings = ts.gpencil_vertex_paint

        col = layout.column()

        row = col.row(align=True)
        row.template_ID(settings, "palette", new="palette.new")
        if settings.palette:
            col.template_palette(settings, "palette", color=True)


class VIEW3D_PT_tools_grease_pencil_brush_mixcolor(View3DPanel, Panel):
    bl_context = ".greasepencil_paint"
    bl_label = "Color"
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        ob = context.object
        ts = context.tool_settings
        settings = ts.gpencil_paint
        brush = settings.brush

        if ob is None or brush is None:
            return False

        if context.region.type == 'TOOL_HEADER':
            return False

        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        tool = ToolSelectPanelHelper.tool_active_from_context(context)
        if tool and tool.idname in {'builtin.cutter', 'builtin.eyedropper', 'builtin.interpolate'}:
            return False

        if brush.gpencil_tool == 'TINT':
            return True

        if brush.gpencil_tool not in {'DRAW', 'FILL'}:
            return False

        return True

    def draw(self, context):
        layout = self.layout
        ts = context.tool_settings
        settings = ts.gpencil_paint
        brush = settings.brush
        gp_settings = brush.gpencil_settings

        if brush.gpencil_tool != 'TINT':
            row = layout.row()
            row.prop(settings, "color_mode", expand=True)

        layout.use_property_split = True
        layout.use_property_decorate = False
        col = layout.column()
        col.enabled = settings.color_mode == 'VERTEXCOLOR' or brush.gpencil_tool == 'TINT'

        col.template_color_picker(brush, "color", value_slider=True)

        sub_row = col.row(align=True)
        sub_row.prop(brush, "color", text="")
        sub_row.prop(brush, "secondary_color", text="")

        sub_row.operator("gpencil.tint_flip", icon='FILE_REFRESH', text="")

        if brush.gpencil_tool in {'DRAW', 'FILL'}:
            col.prop(gp_settings, "vertex_mode", text="Mode")
            col.prop(gp_settings, "vertex_color_factor", slider=True, text="Mix Factor")

        if brush.gpencil_tool == 'TINT':
            col.prop(gp_settings, "vertex_mode", text="Mode")


class VIEW3D_PT_tools_grease_pencil_brush_mix_palette(View3DPanel, Panel):
    bl_context = ".greasepencil_paint"
    bl_label = "Palette"
    bl_category = "Tool"
    bl_parent_id = 'VIEW3D_PT_tools_grease_pencil_brush_mixcolor'

    @classmethod
    def poll(cls, context):
        ob = context.object
        ts = context.tool_settings
        settings = ts.gpencil_paint
        brush = settings.brush

        if ob is None or brush is None:
            return False

        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        tool = ToolSelectPanelHelper.tool_active_from_context(context)
        if tool and tool.idname in {'builtin.cutter', 'builtin.eyedropper', 'builtin.interpolate'}:
            return False

        if brush.gpencil_tool == 'TINT':
            return True

        if brush.gpencil_tool not in {'DRAW', 'FILL'}:
            return False

        return True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        ts = context.tool_settings
        settings = ts.gpencil_paint
        brush = settings.brush

        col = layout.column()
        col.enabled = settings.color_mode == 'VERTEXCOLOR' or brush.gpencil_tool == 'TINT'

        row = col.row(align=True)
        row.template_ID(settings, "palette", new="palette.new")
        if settings.palette:
            col.template_palette(settings, "palette", color=True)


# Grease Pencil Brush Appearance (one for each mode)
class VIEW3D_PT_tools_grease_pencil_paint_appearance(GreasePencilDisplayPanel, Panel, View3DPanel):
    bl_context = ".greasepencil_paint"
    bl_parent_id = 'VIEW3D_PT_tools_grease_pencil_brush_settings'
    bl_label = "Cursor"
    bl_category = "Tool"
    bl_ui_units_x = 15


class VIEW3D_PT_tools_grease_pencil_sculpt_appearance(GreasePencilDisplayPanel, Panel, View3DPanel):
    bl_context = ".greasepencil_sculpt"
    bl_parent_id = 'VIEW3D_PT_tools_grease_pencil_sculpt_settings'
    bl_label = "Cursor"
    bl_category = "Tool"


class VIEW3D_PT_tools_grease_pencil_weight_appearance(GreasePencilDisplayPanel, Panel, View3DPanel):
    bl_context = ".greasepencil_weight"
    bl_parent_id = 'VIEW3D_PT_tools_grease_pencil_weight_paint_settings'
    bl_category = "Tool"
    bl_label = "Cursor"


class VIEW3D_PT_tools_grease_pencil_vertex_appearance(GreasePencilDisplayPanel, Panel, View3DPanel):
    bl_context = ".greasepencil_vertex"
    bl_parent_id = 'VIEW3D_PT_tools_grease_pencil_vertex_paint_settings'
    bl_category = "Tool"
    bl_label = "Cursor"

class VIEW3D_PT_work_in_progress(Panel, View3DPanel):
    bl_label = "Available in the PRO version"
    bl_region_type = 'HEADER'
    bl_options = {'INSTANCED'}
    bl_ui_units_x = 8

    def draw(self, context):
        layout = self.layout
        layout.label(text="Available in the PRO version")

class VIEW3D_PT_gpencil_brush_presets(Panel, PresetPanel):
    """Brush settings"""
    bl_label = "Brush Presets"
    preset_subdir = "gpencil_brush"
    preset_operator = "script.execute_preset"
    preset_add_operator = "scene.gpencil_brush_preset_add"

class _defs_pro_menu:
    @ToolDef.from_fn
    def pro_light():
        return dict(
            idname="VIEW3D_MT_ProLight",
            label=" PRO\nLIGHT",
            type="Menu",
            # icon="ops.transform.transform",
            # description="Available in the PRO version"
        )
    @ToolDef.from_fn
    def motion_capture():
        return dict(
            idname="VIEW3D_PT_work_in_progress",
            label=" MOTION\nCAPTURE",
            type="Panel",
            # icon="ops.transform.transform",
            description="Available in the PRO version"
        )
    @ToolDef.from_fn
    def mimic_capture():
        return dict(
            idname="VIEW3D_PT_work_in_progress",
            label="   MIMIC\nCAPTURE",
            type="Panel",
            # icon="ops.transform.transform",
            description="Available in the PRO version"
        )
    @ToolDef.from_fn
    def drafts():
        return dict(
            idname="VIEW3D_PT_work_in_progress",
            label="DRAFTS",
            type="Panel",
            # icon="ops.transform.transform",
            description="Available in the PRO version"
        )
    @ToolDef.from_fn
    def pro_camera():
        return dict(
            idname="RENDER_PT_menu_camera",
            label="   Pro\nCamera",
            type="Panel",
            # icon="ops.transform.transform",
            description="Available in the PRO version"
        )
    @ToolDef.from_fn
    def pro_shapes():
        return dict(
            idname="VIEW3D_MT_2d",
            label="   PRO\nSHAPES",
            type="Menu",
        )
    
    @ToolDef.from_fn
    def pro_matlab():
        return dict(
            idname="view3d.pro_material",
            label="   Pro\nMatlab",
            type="Operator",
            # icon="ops.transform.transform",
        )
    @ToolDef.from_fn
    def pro_render():
        return dict(
            idname="VIEW3D_PT_work_in_progress",
            label="   PRO\nRENDER",
            type="Panel",
            # icon="ops.transform.transform",
            description="Available in the PRO version"
        )
    @ToolDef.from_fn
    def stream_rendering():
        return dict(
            idname="render.opengl_dialog",
            label="   Stream\n Rendering",
            type="Operator",
            # icon="ops.transform.transform",
        )
    @ToolDef.from_fn
    def vr_hands():
        return dict(
            idname="VIEW3D_OT_vr_hands",
            label="    VR\nHands",
            type="Operator",
            # icon="ops.transform.transform",
            description="Open VR Hands"
        )

    @ToolDef.from_fn
    def themes():
        return dict(
            idname="VIEW3D_PT_work_in_progress",
            label="THEMES",
            type="Panel",
            # icon="ops.transform.transform",
            description="Available in the PRO version"
        )
    @ToolDef.from_fn
    def physics():
        return dict(
            idname="PHYSICS_PT_add",
            label=" Physics",
            type="Panel",
            # icon="ops.transform.transform",
            description="Available in the PRO version",
            align='RIGHT'
        )
    @ToolDef.from_fn
    def ar_export():
        return dict(
            idname="wm.export_usdz",
            label=" AR",
            type="Operator",
            # icon="ops.transform.transform",
            description="Export AR",
            align='RIGHT',
        )
    @ToolDef.from_fn
    def ai_help():
        return dict(
            idname="VIEW3D_PT_work_in_progress",
            label="AI",
            type="Panel",
            # icon="ops.transform.transform",
            description="Available in the PRO version"
        )
    @ToolDef.from_fn
    def upcoming_features():
        return dict(
            idname="wm.url_open",
            label="Upcoming\n  Features",
            properties = {"url": "https://www.3ixam.com/"},
            type="Operator",
            description="Details of upcoming features"
        )

class _defs_transform:

    @ToolDef.from_fn
    def translate():
        return dict(
            idname="view3d.move_with_wait",
            label="Move",
            icon="ops.transform.transform",
            keymap="3D View Tool: Translate, Rotate"
        )

    @ToolDef.from_fn
    def rotate():
        return dict(
            idname="view3d.rotate_with_wait",
            label="Rotate",
            icon="ops.transform.rotate",
            keymap="3D View Tool: Translate, Rotate",
        )

    @ToolDef.from_fn
    def scale():
        return dict(
            idname="view3d.zoom_with_wait",
            label="Scale",
            icon="ops.transform.zoom_tool",
            keymap="3D View Tool: Translate, Rotate",
        )

class VIEW3D_PT_pro_menu(ToolSelectPanelHelper, Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'PRO_MENU'
    bl_label = "Pro Menu"
    bl_options = {'HIDE_HEADER'}
    tool_fallback_id = "view3d.move_with_wait"

    _tools = {
        None: [
            None,
            None,
            _defs_pro_menu.pro_camera,
            _defs_pro_menu.pro_matlab,
            None,
            _defs_pro_menu.stream_rendering,
            None,
            _defs_pro_menu.physics,
            _defs_pro_menu.ar_export,
            None,
            # _defs_pro_menu.upcoming_features,
            None,
            ]
    }
    @classmethod
    def tools_from_context(cls, context):
        for item in cls._tools[None]:
            if not (type(item) is ToolDef) and callable(item):
                yield from item(context)
            else:
                yield item

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D')

    @classmethod
    def icon_scale(self):
        return 1.0

    @classmethod
    def vertical_scale(self):
        #prefs = bpy.context.preferences.system
        return 3.5# * (prefs.dpi * prefs.pixel_size / 72)

    @classmethod
    def button_shape(self):
        return 'PRO_HEX'

    @classmethod
    def align(self):
        hand_type = bpy.context.preferences.view.hand_type

        return 'LEFT' if hand_type == 'HAND_RIGHT' else 'RIGHT'

    @classmethod
    def tools_all(cls):
        yield from cls._tools.items()


class VIEW3D_PT_hud(ToolSelectPanelHelper, Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HUD'
    bl_label = "HUD" 
    bl_options = {'HIDE_HEADER'}

    keymap_prefix = "3D View Tool:"

    last_rotation = None
    last_location = None
    last_scale = None
    last_operation = 0
    last_operator = 0

    tool_fallback_id = "view3d.move_with_wait"

    _tools = {
        None: [
            _defs_transform.scale,
            _defs_transform.translate,
            _defs_transform.rotate,
            ]
    }

    @classmethod
    def tools_from_context(cls, context):
        for item in cls._tools[None]:
            if not (type(item) is ToolDef) and callable(item):
                yield from item(context)
            else:
                yield item
    @classmethod
    def tools_all(cls):
        yield from cls._tools.items()

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D'

    def draw(self, context):
        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        layout = self.layout        
        row = layout.row()
        #row.alignment = 'RIGHT'

        col = row.column()

        col.separator(factor=3)

        coords = col.row()
        #coords.alignment = 'RIGHT'

        ob = context.object
        if ob is None:
            if "zeroObj" in bpy.data.objects:
                ob = bpy.data.objects['zeroObj']
            else:
                ob = bpy.data.objects.new('zeroObj',bpy.data.meshes.new('zeroMesh'))
                bpy.data.collections['Viewport'].objects.link(ob)
                #If object links with collection it appears in list of objects 
                #TODO: find way to delete or another way to set tools
                #context.collection.objects.link(ob)

        tool_check = context.workspace.tools.from_space_view3d_mode(context.mode)
        if tool_check is None:
            return

        tool = tool_check.idname

        if  VIEW3D_PT_hud.last_operator != tool:
            if tool == 'builtin.rotate':
                VIEW3D_PT_hud.last_operation = 3
            elif tool == 'builtin.scale' or VIEW3D_PT_hud.last_operation == 2:
                VIEW3D_PT_hud.last_operation = 2
            else:
                VIEW3D_PT_hud.last_operation = 1
            
        VIEW3D_PT_hud.last_operator = tool

        if VIEW3D_PT_hud.last_rotation != ob.rotation_euler:
            VIEW3D_PT_hud.last_operation = 3
        if VIEW3D_PT_hud.last_scale != ob.scale:
            VIEW3D_PT_hud.last_operation = 2
        if VIEW3D_PT_hud.last_location != ob.location:
            VIEW3D_PT_hud.last_operation = 1

        VIEW3D_PT_hud.last_location = ob.location.copy()
        VIEW3D_PT_hud.last_rotation = ob.rotation_euler.copy()
        VIEW3D_PT_hud.last_scale = ob.scale.copy()

        if VIEW3D_PT_hud.last_operation == 3:
            coords.prop(ob, 'rotation_euler', text="", shape = "RHOMBOID")
        elif VIEW3D_PT_hud.last_operation == 2:
            coords.prop(ob, 'scale', text="", shape = "RHOMBOID")
        else:
            coords.prop(ob, 'location', text="", shape = "RHOMBOID")
        
        tool_active_id = getattr(
            ToolSelectPanelHelper._tool_active_from_context(context, context.space_data.type),
            "idname", None,
        )

        row.separator()
        col = row.column()

        tools = col.row()
        tools.scale_y = 2
        tools.scale_x = 1.5
        tools.icon_scale = 1.3
        #tools.alignment = 'CENTER'
        tools.operator_context = 'INVOKE_DEFAULT'

        for item in self.tools_from_context(context):
            is_active = (item.idname == tool_active_id)    
            icon_value = ToolSelectPanelHelper._icon_value_from_icon_handle(item.icon)
            tools.operator(
                "wm.tool_set_by_id",
                text="",
                depress=is_active,
                icon_value=icon_value,
                shape='RHOMBOID'
            ).name = item.idname

class VIEW3D_PT_pivot(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "Pivot Point" 
    bl_options = {'HIDE_HEADER', 'INSTANCED'}
    bl_ui_units_x = 4

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        mode = context.mode

        layout.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='BOUNDING_BOX_CENTER')
        layout.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='INDIVIDUAL_ORIGINS')
        layout.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='MEDIAN_POINT')
        layout.prop_enum(context.scene.tool_settings, "transform_pivot_point", value='ACTIVE_ELEMENT')

class VIEW3D_PT_header(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "HEADER" 
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        tool_settings = context.tool_settings

        setattr(context.area, "show_menus", True)

        topbar = layout.row()
        topbar.alignment = 'LEFT'

        topbar.menu_image(menu="TOPBAR_MT_ixam", text="")
        topbar.separator()

        left_menu = topbar.column(align = True)
        left_menu.alignment = 'LEFT'

        menu_header = left_menu.row(align = True)
        sub = menu_header.row(align=True)
        sub.alignment = 'LEFT'
        sub.menu_contents("TOPBAR_MT_editor_menus")

        left_menu.separator(factor=3.5)

        shortcuts = left_menu.row()
        shortcuts.scale_x = 1.3
        shortcuts.alignment = 'LEFT'
        shortcuts.emboss = 'NONE'
        shortcuts.icon_scale = 1.3
        shortcuts.operator("wm.save_mainfile", text="", icon='FILE_TICK')
        shortcuts.popover("VIEW3D_PT_snapping", text="", icon='SNAP_TRANSLATION')
        shortcuts.popover("VIEW3D_PT_snapping_rot", text="", icon='SNAP_ROTATION')
        shortcuts.popover("VIEW3D_PT_adjust_pivot", text="", icon="WORLD_AXIS")
        # shortcuts.operator("builtin.blank_operator", text="", icon='MOD_OFFSET')
        shortcuts.operator("object.mirror_tools", text="", icon='MOD_MIRROR')
        shortcuts.operator("object.align_tools", text="", icon='ALIGN_OBJECTS')
        shortcuts.operator("object.explode", text="", icon='MOD_EXPLODE')
        shortcuts.operator("ed.undo", text="", icon='UNDO') 
        shortcuts.operator("ed.redo", text="", icon='REDO')

        topbar.separator_spacer()

        right_menu = topbar.row(align=True)
        right_menu.emboss = 'NORMAL'
        right_menu.icon_scale = 1

        orient_slot = scene.transform_orientation_slots[0]
        sub = right_menu.row()
        sub.scale_x = 0.7
        sub.label(text="", icon='WORLD_AXIS')
        sub.prop(orient_slot, "type", text="")

        sub = right_menu.row()
        sub.scale_x = 0.7
        
        # Sub layouts only needed because of icon_scale scaling text size also
        sub_icon = sub.row()
        sub_icon.scale_x = 1.2
        sub_icon.icon_scale = 1.6
        sub_icon.label(text="", icon="WORLD_AXIS")
        
        sub.popover("VIEW3D_PT_pivot", text = self.get_pivot_center_name(context=context))

        sub = right_menu.row()
        sub.scale_x = 0.7
        
        sub_icon = sub.row()
        sub_icon.scale_x = 1.2
        sub_icon.icon_scale = 1.6
        sub_icon.label(text="", icon="POLYFORM")
        
        depress = context.mode in {'EDIT_MESH', 'EDIT_CURVE', 'EDIT_ARMATURE', 'POSE'}
        sub.popover("VIEW3D_PT_polyform", text = "Poly Form", depress=depress)

        search_menu = right_menu.row()
        search_menu.scale_x = 0.35
        # split = search_menu.split(factor=0.7)       
        search_menu.search()
        logo_3ixam = right_menu.row()

        logo_3ixam.scale_x = 2.5
        logo_3ixam.scale_y = 0.5
        logo_3ixam.icon_scale = 4.5
        icon = 'LOGO_3IXAM_BLACK' if bpy.context.preferences.current_theme == 'Light' else 'LOGO_3IXAM'
        logo_3ixam.operator("builtin.blank_operator", text="", icon=icon, emboss = False, depress = True)
        
    def get_pivot_center_name(self, context):
        scene = context.scene
        pivot_point_type = scene.tool_settings.transform_pivot_point
        pivot_point_names = {
            "BOUNDING_BOX_CENTER" : "Contain",
            "CURSOR" : "3D Cursor",
            "INDIVIDUAL_ORIGINS" : "Individual",
            "MEDIAN_POINT" : "Median",
            "ACTIVE_ELEMENT" : "Active",
        }
        return pivot_point_names.get(pivot_point_type, None)


class VIEW3D_PT_adjust_pivot(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "PIVOT" 
    bl_options = {'HIDE_HEADER', 'INSTANCED'}
    bl_ui_units_x = 5

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Adjust Pivot")

        layout.separator()

        tool_settings = context.tool_settings
        layout.prop(tool_settings, "use_transform_data_origin", text="Affect Pivot only", toggle=1)

        layout.separator()

        layout.label(text="Alignment")

        layout.separator()
        layout.operator("object.origin_set",
                        text="Center To Object").type = 'ORIGIN_GEOMETRY'


class VIEW3D_PT_polyform(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "PIVOT" 
    bl_options = {'HIDE_HEADER', 'INSTANCED'}
    bl_ui_units_x = 12

    op_name_to_flag_mapping = {
        'EXTRUDE_STANDART': 1,
        'EXTRUDE_INDIV': 2,
        'EXTRUDE_MANIFOLD': 3,
        'BEVEL': 4,
        'SLIDE': 5,
        'KNIFE': 6,
        'LOOPCUT': 7,
        'INSET': 8,
    }

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D'

    def op_shape(self, context, operator_name):
        is_highlighted = (self.op_name_to_flag_mapping[operator_name] == context.space_data.polyform_ui_highlight_flag)

        return 'PREFS' if is_highlighted else 'ROUNDBOX'

    def draw(self, context):
        layout = self.layout
        active_object = context.active_object

        layout.label(text="Selection")

        if active_object:
            if active_object.type == 'MESH':
                sub = layout.row()
                sub.emboss = "NONE"
                vert, edge, face = bpy.context.scene.tool_settings.mesh_select_mode if context.mode == 'EDIT_MESH' else (False, False, False)
                grid = sub.grid_flow(columns=3)
                
                mode = grid.column(align=True)
                mode.icon_scale = 1.5 if vert else 1.0
                mode.operator("mesh.select_mode", text="", icon='VERTEXSEL', depress = vert).type = 'VERT'
                mode = grid.column(align=True)
                mode.icon_scale = 1.5 if edge else 1.0
                mode.operator("mesh.select_mode", text="", icon='EDGESEL', depress = edge).type = 'EDGE'
                mode = grid.column(align=True)
                mode.icon_scale = 1.5 if face else 1.0
                mode.operator("mesh.select_mode", text="", icon='FACESEL', depress = face).type = 'FACE'

                if vert:
                    layout.label(text="Edit Vertices")
                    sub = layout.row()

                    col = sub.column()
                    col.operator("mesh.split")

                    col.operator("mesh.extrude_vertices_move", text="Extrude", shape=self.op_shape(context, 'EXTRUDE_INDIV'))

                    prop = col.operator("mesh.bevel", text="Bevel", shape=self.op_shape(context, 'BEVEL'))
                    prop.affect = 'VERTICES'
                    prop.popover = True
                    col.operator("mesh.dissolve_verts", text="Dissolve")
                    col.operator("mesh.delete", text="Delete").type = 'VERT' 

                    col = sub.column()
                    col.operator("mesh.merge", text="Merge").type = "CENTER"
                    col.operator("mesh.vert_connect", text="Connect")
                    col.operator("transform.vert_slide", text="Slide", shape=self.op_shape(context, 'SLIDE'))
                    col.operator("mesh.knife_tool", text="Knife", shape=self.op_shape(context, 'KNIFE'))
                    col.operator("mesh.loopcut", shape=self.op_shape(context, 'LOOPCUT'))
                elif edge:
                    layout.label(text="Edit Edges")

                    sub = layout.row()
                    col = sub.column()
                    col.operator("mesh.subdivide", text="Subdivide").popover = True

                    col.operator("mesh.extrude_edges_move", text="Extrude", shape=self.op_shape(context, 'EXTRUDE_INDIV'))

                    prop = col.operator("mesh.bevel", text="Bevel", shape=self.op_shape(context, 'BEVEL'))
                    prop.affect = 'EDGES'
                    prop.popover = True
                    col.operator("transform.edge_slide", text="Slide", shape=self.op_shape(context, 'SLIDE'))
                    col.operator("mesh.unsubdivide", text="Un-Subdivide") 
                    col.operator("mesh.split")                   

                    col = sub.column()
                    
                    col.operator("mesh.merge", text="Merge").type = "CENTER"
                    col.operator("mesh.bridge_edge_loops", text="Bridge")
                    col.operator("mesh.knife_tool", text="Knife", shape=self.op_shape(context, 'KNIFE'))
                    col.operator("mesh.loopcut", shape=self.op_shape(context, 'LOOPCUT'))
                    col.operator("mesh.dissolve_edges", text="Dissolve")
                    col.operator("mesh.delete", text="Delete").type = 'EDGE' 

                elif face:
                    layout.label(text="Edit Faces")

                    sub = layout.row()
                    col = sub.column()
                    col.operator("mesh.subdivide", text="Subdivide").popover = True
                    col.operator("mesh.wireframe", text="Outline").popover = True

                    col.operator("view3d.edit_mesh_extrude_move_normal", text="Extrude Standart", shape=self.op_shape(context, 'EXTRUDE_STANDART'))
                    col.operator("mesh.extrude_faces_move", text="Extrude Individual", shape=self.op_shape(context, 'EXTRUDE_INDIV'))
                    col.operator("view3d.edit_mesh_extrude_manifold_normal", text="Extrude Custom", shape=self.op_shape(context, 'EXTRUDE_MANIFOLD'))
                    
                    prop = col.operator("mesh.bevel", text="Bevel", shape=self.op_shape(context, 'BEVEL'))
                    prop.affect = 'EDGES'
                    prop.popover = True
                    col.operator("mesh.poke", text="Poke")
                    col.operator("mesh.dissolve_faces", text="Dissolve")

                    col = sub.column()
                    col.operator("mesh.inset", text="Inset", shape=self.op_shape(context, 'INSET')).popover = True
                    col.operator("mesh.quads_convert_to_tris", text="Triangulate")
                    col.operator("mesh.tris_convert_to_quads", text="Tris to Quads")
                    col.operator("mesh.unsubdivide", text="Un-Subdivide") 
                    col.operator("mesh.split")  
                    col.operator("mesh.knife_tool", text="Knife", shape=self.op_shape(context, 'KNIFE'))
                    col.operator("mesh.loopcut", shape=self.op_shape(context, 'LOOPCUT'))
                    col.operator("mesh.delete", text="Delete").type = 'FACE' 


            elif active_object.type == 'CURVE' :
                sub = layout.row()
                sub.emboss = "NONE"
                mode = sub.column(align=True)
                mode.icon_scale = (1.5 if context.mode == 'EDIT_CURVE' else 1.0)

                mode_vertexsel = mode.operator("object.mode_set", text="", icon='VERTEXSEL')
                mode_vertexsel.mode = 'EDIT'
                mode_vertexsel.toggle = True

                if context.mode == 'EDIT_CURVE':

                    layout.label(text="Edit Curve")

                    sub = layout.row()
                    col1 = sub.column()

                    col1.operator("curve.delete", text="Remove").type = 'VERT'
                    col1.operator("curve.extrude_move", text="Extrude", shape=self.op_shape(context, 'EXTRUDE_STANDART'))

            elif active_object.type == 'ARMATURE':
                sub = layout.row()
                sub.emboss = "NONE"
                edit_mode = active_object.mode == 'EDIT'
                pose_mode = active_object.mode == 'POSE'
                grid = sub.grid_flow(columns=2)
                
                mode = grid.column(align=True)
                mode.icon_scale = 1.5 if edit_mode else 1.0
                prop = mode.operator("object.mode_set", text="", icon='BONE_DATA', depress = edit_mode)
                prop.toggle_without_prev = True
                prop.mode = 'EDIT'
                # prop.toggle = True

                mode = grid.column(align=True)
                mode.icon_scale = 1.5 if pose_mode else 1.0
                prop = mode.operator("object.mode_set", text="", icon='ARMATURE_DATA', depress = pose_mode)
                prop.toggle_without_prev = True
                prop.mode = 'POSE'
                # prop.toggle = True

                if edit_mode:
                    layout.label(text="Joints Edit")
                    sub = layout.row()

                    col = sub.column()
                    col.operator("armature.bone_primitive_add", text="Add Simple Joint")
                    col.operator("transform.transform", text="Roll Joint").mode = 'BONE_ROLL'

                    col = sub.column()
                    col.operator("armature.extrude_move", text="Extrude Joint")
                    col.operator("armature.dissolve", text="Remove and Collapse")
                elif pose_mode:
                    layout.label(text="Animate")

        # Proportional Editing
        show_proportional_edit = True
        if active_object and active_object.type == 'ARMATURE': show_proportional_edit = False

        if show_proportional_edit:
            tool_settings = context.tool_settings
            enable_proportional_edit = (context.mode == 'EDIT_MESH' or context.mode == 'EDIT_CURVE')

            layout.separator()
            sub = layout.row(align=True)
            sub.enabled = enable_proportional_edit
            sub.prop(
                tool_settings,
                "use_proportional_edit",
                text="Soft Selection",
                # shape='PREFS',
                emboss = False,
                icon='PROP_ON' if tool_settings.use_proportional_edit else 'PROP_OFF'
            )
            
            if tool_settings.use_proportional_edit:
                sub = layout.column(align=True)
                sub.enabled = enable_proportional_edit
                sub.prop(
                    tool_settings,
                    "proportional_edit_falloff",
                    text=""
                )
                sub.prop(
                    tool_settings,
                    "proportional_size",
                    text=""
                )

class VIEW3D_PT_viewport_configuration(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'VIEWBAR'
    bl_label = "Viewport Configuration" 
    bl_options = {"INSTANCED"}

    def draw(self, context):
        layout = self.layout

        viewport_configuration = layout.row()
        viewport_configuration.emboss = "NONE"
        viewport_configuration.icon_scale = 1.5
        sub = viewport_configuration.column()
        sub.scale_y = 1.3
        sub.operator("screen.region_quadview", text="", icon="QUADVIEW_0").type = 0
        sub.operator("screen.region_quadview", text="", icon="QUADVIEW_1").type = 1
        sub.operator("screen.region_quadview", text="", icon="QUADVIEW_2").type = 2
        sub.operator("screen.region_quadview", text="", icon="QUADVIEW_3").type = 3
        sub = viewport_configuration.column()
        sub.scale_y = 1.3
        sub.operator("screen.region_quadview", text="", icon="QUADVIEW_4").type = 4
        sub.operator("screen.region_quadview", text="", icon="QUADVIEW_5").type = 5
        sub.operator("screen.region_quadview", text="", icon="QUADVIEW_6").type = 6
        sub.operator("screen.region_quadview", text="", icon="QUADVIEW_7").type = 7 
        sub = viewport_configuration.column()
        sub.scale_y = 1.3
        sub.operator("screen.region_quadview", text="", icon="QUADVIEW_8").type = 8 
        sub.operator("screen.region_quadview", text="", icon="QUADVIEW_9").type = 9 
        sub.operator("screen.region_quadview", text="", icon="QUADVIEW_10").type = 10 
        sub.operator("screen.region_quadview", text="", icon="QUADVIEW_11").type = 11 


class VIEW3D_PT_view_bar(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'VIEWBAR'
    bl_label = "VIEWBAR" 
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.ui_units_x = 16

        row.separator(factor=9)

        viewport = row.row()
        viewport.scale_y = 3.4
        viewport.ui_units_x = 2.3

        viewport.viewport_configuration(panel="VIEW3D_PT_viewport_configuration")

        sub = row.column()
        sub.ui_units_x=3.5
        sub.label(text="Poly Info")

        faces = "0"
        verts = "0"
        objects = "0"
        for stat in bpy.context.scene.statistics(bpy.context.view_layer).split(" | "):
            if stat.startswith("Faces:"):
                faces = stat[6:]
            if stat.startswith("Verts:"):
                verts = stat[6:]
            if stat.startswith("Objects:"):
                objects = stat[8:]

        # sub = sub.column()
        # sub.scale_y = 0.35
        # sub.label(text=f"Polys:  {faces}")
        # sub.label(text=f"Verts:  {verts}")
        # sub.label(text=f"Objects:  {objects}")

        sub = sub.column()
        sub.scale_y = 0.35

        row = sub.row()
        col = row.column()
        col.alignment = 'LEFT'
        col.label(text="Polys:")

        col = row.column()
        col.alignment = 'RIGHT'
        col.label(text=f"{faces}")

        row = sub.row()
        col = row.column()
        col.alignment = 'LEFT'
        col.label(text="Verts:")

        col = row.column()
        col.alignment = 'RIGHT'
        col.label(text=f"{verts}")

        row = sub.row()
        col = row.column()
        col.alignment = 'LEFT'
        col.label(text="Objects:")

        col = row.column()
        col.alignment = 'RIGHT'
        col.label(text=f"{objects}")

class VIEW3D_MT_ProLight(Menu):
    bl_label = "PRO\nLIGHT"
    bl_ui_units_x = 1

    def draw(self, context):
        layout = self.layout
        layout.scale_y = 2
        layout.operator_context = "INVOKE_REGION_WIN"

        point_light = layout.operator("view3d.point_light", text="Point Light", icon="LIGHT_POINT")
        sun_light = layout.operator("view3d.sun_light", text="Sun Light", icon="LIGHT_SUN")

class VIEW3D_MT_skelet(Menu):
    bl_label = "Skelet"
    bl_ui_units_x = 1

    def draw(self, context):
        layout = self.layout
        layout.scale_y = 2
        layout.icon_scale = 1.5

        layout.operator("object.armature_basic_human_metarig_add", text="", icon="ARMATURE_DATA")
        layout.operator("object.armature_add", text="", icon="BONE_DATA")

class VIEW3D_MT_forces(Menu):
    bl_label = "2D"
    bl_ui_units_x = 1

    def draw(self, context):
        get_icon_value = ToolSelectPanelHelper._icon_value_from_icon_handle

        layout = self.layout
        layout.scale_y = 2
        layout.icon_scale = 1.5

        layout.operator_context = "INVOKE_REGION_WIN"

        prop = self.layout.operator("object.empty_add", text="", icon_value=get_icon_value("ops.mesh.primitive_dummy_simple"))
        prop.type = "PLAIN_AXES"

        prop = layout.operator("object.effector_add", text="", icon_value=get_icon_value("ops.mesh.primitive_dummy_wind"))
        prop.type = "WIND"

        prop = layout.operator("object.effector_add", text="", icon_value=get_icon_value("ops.mesh.primitive_dummy_force"))
        prop.type = "FORCE"

        prop = layout.operator("object.effector_add", text="", icon_value=get_icon_value("ops.mesh.primitive_dummy_turbidity"))
        prop.type = "TURBULENCE"


class VIEW3D_MT_2d(Menu):
    bl_label = "2D"
    bl_ui_units_x = 1

    def draw(self, context):
        get_icon_value = ToolSelectPanelHelper._icon_value_from_icon_handle
        
        layout = self.layout
        layout.scale_y = 2
        layout.icon_scale = 1.5

        layout.operator_context = "INVOKE_REGION_WIN"

        oper = layout.operator("simple.add", text="", icon_value=get_icon_value("ops.mesh.primitive_shapes_add_point"))
        oper.Simple_Type = "Point"
        oper.use_cyclic_u = False

        oper6 = self.layout.operator("simple.add", text="", icon_value=get_icon_value("ops.mesh.primitive_shapes_add_line"))
        oper6.Simple_Type = "Line"
        oper6.use_cyclic_u = False
        oper6.shape = '3D'

        oper = layout.operator("simple.add", text="", icon_value=get_icon_value("ops.mesh.primitive_shapes_add_curve"))
        oper.Simple_Type = "Arc"
        oper.use_cyclic_u = False
        oper.shape = '3D'

        oper = layout.operator("simple.add", text="", icon_value=get_icon_value("ops.mesh.primitive_shapes_add_rectangle"))
        oper.Simple_Type = "Rectangle"
        oper.use_cyclic_u = True
        oper.shape = '3D'

        oper = layout.operator("simple.add", text="", icon_value=get_icon_value("ops.mesh.primitive_shapes_add_circle"))
        oper.Simple_Type = "Circle"
        oper.use_cyclic_u = True
        oper.shape = '3D'

        oper = layout.operator("simple.add", text="", icon_value=get_icon_value("ops.mesh.primitive_shapes_add_hexagon"))
        oper.Simple_Type = "Polygon"
        oper.use_cyclic_u = True 
        oper.shape = '3D'

        layout.operator("curve.draw", text="", icon_value=get_icon_value("ops.mesh.draw_spline"))

        layout.operator("object.text_add", text="", icon_value=get_icon_value("ops.mesh.primitive_shapes_add_text"))

class VIEW3D_MT_selection(Menu):
    bl_label = "Selection"
    bl_ui_units_x = 1

    def draw(self, context):
        from .space_toolsystem_common import ToolSelectPanelHelper as TSPH
        icon_value_from_name = TSPH._icon_value_from_icon_handle
        layout = self.layout
        layout.scale_y = 2
        layout.icon_scale = 1.6

        layout.operator_context = "INVOKE_DEFAULT"

        props = layout.operator("wm.tool_set_by_id", text="", icon_value=icon_value_from_name("ops.generic.select_box"))
        props.name = 'builtin.select_box'
        props = layout.operator("wm.tool_set_by_id", text="", icon_value=icon_value_from_name("ops.generic.select_circle"))
        props.name = 'builtin.select_circle'
        props = layout.operator("wm.tool_set_by_id", text="", icon_value=icon_value_from_name("ops.generic.select_lasso"))
        props.name = 'builtin.select_lasso'


def sep(layout, factor:int):
    for i in range(factor):
        layout.separator()


class VIEW3D_PT_shading_settings(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Shading Settings" 
    bl_options = {'INSTANCED'}
    bl_ui_units_x = 13

    @classmethod
    def poll(cls, context):
        object = context.object
        object_data = getattr(object, "data", None)
        has_polygons = hasattr(object_data, "polygons")
        
        correct_space_type = (context.space_data.type == 'VIEW_3D')
        
        return correct_space_type and object_data and has_polygons

    def draw(self, context):
        layout = self.layout
        if context.active_object == None:
            return
        if context.active_object.data == None:
            return
        obj_data = context.active_object.data

        poly_use_smooth = [0] * len(obj_data.polygons)
        obj_data.polygons.foreach_get("use_smooth", poly_use_smooth)
        
        auto_smooth = obj_data.use_auto_smooth
        use_smooth = all(poly_use_smooth)

        row = layout.row(align=True)
        row.operator("OBJECT_OT_shade_flat", text="Harden Normals", depress=(not use_smooth))
        row.operator("OBJECT_OT_shade_smooth", text="Smooth Normals", depress=(use_smooth and not auto_smooth))

        if context.active_object.type != "ARMATURE":

            row = layout.row(align=True)
            row.operator("OBJECT_OT_shade_smooth", text="Use Angle Limit", depress=auto_smooth).use_auto_smooth = True
            sub = row.row(align=True)
            sub.enabled = auto_smooth
            sub.prop(obj_data, "auto_smooth_angle", text="")

        layout.separator()

        layout.operator("mesh.customdata_custom_splitnormals_clear", text="Clean Normals")


class VIEW3D_PT_parameters(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Parameters" 
    bl_options = {'INSTANCED'}
    bl_ui_units_x = 15

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D' and context.object and not context.object.protect

    def draw(self, context):
        layout = self.layout
        active_object = context.view_layer.objects.active
        if active_object == None:
            return
        panel = layout.column() 

        panel.label(text="Parameters")
        panel.emboss = 'NONE'
        panel.label(text=active_object.name)

        panel.separator()

        panel.emboss = 'NORMAL'
        row = panel.row(align=True)
        row.label(text="Position")
        row.prop(active_object, "location", text="", emboss=False)

        row = panel.row(align=True)
        row.label(text="Rotation")
        row.prop(active_object, "rotation_euler", text="", emboss=False)

        row = panel.row(align=True)
        row.label(text="Scale")
        row.prop(active_object, "scale", text="", emboss=False)

        row = panel.row(align=True)
        row.dimensions_panel()
        
        panel.emboss = 'NONE'
        panel.separator()

        if active_object.type == 'LIGHT':
            light = active_object.data
            panel.emboss = 'NORMAL'
                    
            sub = panel.column()
            sub.use_property_split = True
            sub.label(text="Light Settings")    
            sub.row().prop(light, "type")


            col = sub.column()
            col.prop(light, "color")
            col.prop(light, "energy")

            col.separator()

            if light.type in {'POINT', 'SPOT'}:
                col.prop(light, "shadow_soft_size", text="Radius")
            elif light.type == 'SUN':
                col.prop(light, "angle")
            elif light.type == 'AREA':
                col.prop(light, "shape")

                sub = col.column(align=True)

                if light.shape in {'SQUARE', 'DISK'}:
                    sub.prop(light, "size")
                elif light.shape in {'RECTANGLE', 'ELLIPSE'}:
                    sub.prop(light, "size", text="Size X")
                    sub.prop(light, "size_y", text="Y")
        elif active_object.type == 'FONT':
            font = active_object.data
            panel.emboss = 'NORMAL'
                    
            sub = panel.column()
            sub.shape = 'PREFS'
            sub.label(text="Font Settings")    
            sub.prop(font, "body", text="Text")
            sub.template_ID(font, "font", text="Font", open="font.open", unlink="font.unlink")
        elif active_object.type == 'CURVE':
            from bpy.types import Curve

            curve = active_object.data
            is_curve = type(curve) is Curve
            panel.emboss = 'NORMAL'

            sub = panel.column()
            sub.shape = 'PREFS'
            sub.label(text="Curve Settings")   
            if is_curve:
                row = sub.row()
                row.prop(curve, "dimensions", expand=True) 
                
                if curve.dimensions == '2D':
                    sub = sub.column()
                    sub.prop(curve, "fill_mode")

                sub.label(text="Extrude")
                sub.prop(curve, "offset")

                sub2 = sub.column()
                sub2.active = (curve.bevel_mode != 'OBJECT')
                sub2.prop(curve, "extrude")

                sub.prop(curve, "taper_object")
                sub.prop(curve, "taper_radius_mode")

                sub2 = sub.column()
                sub2.active = curve.taper_object is not None
                sub2.prop(curve, "use_map_taper")

                sub.label(text="Bevel")
                sub.prop(curve, "bevel_mode", expand=True)
                sub.use_property_split = True

                col = sub.column()
                if curve.bevel_mode == 'OBJECT':
                    col.prop(curve, "bevel_object", text="Object")
                else:
                    col.prop(curve, "bevel_depth", text="Depth")
                    col.prop(curve, "bevel_resolution", text="Resolution")
                col.prop(curve, "use_fill_caps")

                if curve.bevel_mode == 'PROFILE':
                    col.template_curveprofile(curve, "bevel_profile")
        
        if context.engine == "CYCLES":
            layout.label(text="Render Visibility")
            col = layout.grid_flow(row_major=True, columns=2)

            col.prop(active_object, "visible_camera", text="Camera")
            col.prop(active_object, "visible_diffuse", text="Diffuse")
            col.prop(active_object, "visible_glossy", text="Glossy")
            col.prop(active_object, "visible_transmission", text="Transmission")
            col.prop(active_object, "visible_volume_scatter", text="Volume Scatter")

            if active_object.type != 'LIGHT':
                sub = col.column()
                sub.prop(active_object, "visible_shadow", text="Shadow")


class VIEW3D_PT_folders(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Folders" 
    bl_options = {'INSTANCED', 'HIDE_HEADER'}
    bl_ui_units_x = 11

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D'

    def draw(self, context):
        layout = self.layout
        header = layout.row()

        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        hex_icon =  ToolSelectPanelHelper._icon_value_from_icon_handle('ops.folders')

        collection = context.scene.collection

        header.label(text='', icon_value=hex_icon)
        header.outliner_folder(collection)

        layout.emboss = "NONE"
        box = layout.box()
        
        if len(collection.objects) > 0 :
            coll_box = box.box()
            coll_box.emboss = "NORMAL"

            for obj in collection.objects:
                sub = coll_box.row()
                sub.separator()
                sub.outliner_object(obj)

        layout.emboss = "NONE"
        for coll in bpy.data.collections:
            if not coll.protect:
                coll_box = box.box()

                coll_box.emboss = "NORMAL"
                coll_header = coll_box.row()
                coll_header.label(text='', icon_value=hex_icon)
                coll_header.outliner_folder(coll)

                for obj in coll.all_objects:
                    sub = coll_box.row()
                    sub.separator()
                    sub.outliner_object(obj)


class VIEW3D_PT_modifiers(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Folders" 
    bl_options = {'INSTANCED', 'HIDE_HEADER'}
    bl_ui_units_x = 15

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D' and context.object and context.object.type != 'ARMATURE' and not context.object.protect

    def draw(self, context):
        layout = self.layout
        sub = layout.row()
        sub.operator_menu_enum("object.modifier_add_without_physics", "type", text='DEFORMERS')

        sub = layout.column(align=True)
        sub.shape = "PREFS"
        sub.template_modifiers_panel()


class VIEW3D_PT_constraints(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Folders" 
    bl_options = {'INSTANCED', 'HIDE_HEADER'}
    bl_ui_units_x = 15

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D' and context.object and not context.object.protect

    def draw(self, context):
        layout = self.layout
        sub = layout.row()
        sub.operator_menu_enum("object.constraint_add", "type", text='CONSTRAINTS')

        sub = layout.column(align=True)
        sub.shape = "PREFS"
        sub.template_constraints_panel(use_bone_constraints=False)


class VIEW3D_PT_animation(Panel):
    #Draw from C 
    bl_space_type = "VIEW_3D"
    bl_region_type = "HEADER"
    bl_label = "ANIMATION" 
    bl_options = {"HIDE_HEADER"}


    @classmethod
    def poll(cls, context):
        return context.region.draw_flag & (1 << 0)

    def draw(self, context):
        tool_settings = context.tool_settings
        layout = self.layout
        layout.separator(factor=0.3)

        row_player = layout.row(align=True)
        row_bar = layout.row()
        row_bar.emboss = "NONE"
        row_bar.prop(context.scene, "frame_start")
        sub = row_bar.row(align=True)
        sub.emboss = "NORMAL"
        sub.anim_bar()
        row_bar.prop(context.scene, "frame_end")

        row_player.separator_spacer()
        row_player.emboss = "NONE"
        row_player.icon_scale = 1.15
        row_player.scale_y = 1.15
        row_player.scale_x = 1.2
        sub = row_player.row(align=True)
        sub.icon_scale = 1.5
        sep(sub, 3)
        sub.prop(tool_settings, "use_keyframe_insert_auto", text="", toggle=True, icon="PANEL_CLOSE" if tool_settings.use_keyframe_insert_auto else "ADD")

        sep(row_player, 5)
        row_player.operator("screen.frame_jump", text="", icon="PREV_KEYFRAME").end = False

        sep(row_player, 4)
        row_player.operator("screen.keyframe_jump", text="", icon="REW").next = False

        sep(row_player, 4)
        sub = row_player.row(align=True)
        sub.icon_scale = 1.4
        sub.operator("screen.animation_play", text="", icon="FRAME_NEXT") #FRAME_NEXT

        sep(row_player, 4)
        row_player.operator("screen.keyframe_jump", text="", icon="FF").next = True

        sep(row_player, 4)
        row_player.operator("screen.frame_jump", text="", icon="NEXT_KEYFRAME").end = True
        row_player.separator_spacer()


classes = (
    VIEW3D_PT_hud,
    VIEW3D_PT_header,
    VIEW3D_PT_view_bar,
    VIEW3D_PT_adjust_pivot,
    VIEW3D_PT_polyform,
    VIEW3D_PT_viewport_configuration,
    VIEW3D_PT_animation,
    VIEW3D_PT_shading_settings,
    VIEW3D_PT_parameters,
    VIEW3D_PT_pro_menu,
    VIEW3D_PT_folders,
    VIEW3D_PT_modifiers,
    VIEW3D_PT_constraints,
    VIEW3D_MT_2d,
    VIEW3D_MT_skelet,
    VIEW3D_MT_selection,
    VIEW3D_MT_ProLight,
    VIEW3D_PT_work_in_progress,
    VIEW3D_PT_pivot,
    VIEW3D_MT_forces,
)

tmp_classes = (
    VIEW3D_MT_brush_context_menu,
    VIEW3D_MT_brush_gpencil_context_menu,
    VIEW3D_PT_tools_object_options,
    VIEW3D_PT_tools_object_options_transform,
    VIEW3D_PT_tools_meshedit_options,
    VIEW3D_PT_tools_meshedit_options_automerge,
    VIEW3D_PT_tools_armatureedit_options,
    VIEW3D_PT_tools_posemode_options,

    VIEW3D_PT_slots_projectpaint,
    VIEW3D_PT_slots_paint_canvas,
    VIEW3D_PT_tools_brush_select,
    VIEW3D_PT_tools_brush_settings,
    VIEW3D_PT_tools_brush_color,
    VIEW3D_PT_tools_brush_swatches,
    VIEW3D_PT_tools_brush_settings_advanced,
    VIEW3D_PT_tools_brush_clone,
    TEXTURE_UL_texpaintslots,
    VIEW3D_MT_tools_projectpaint_uvlayer,
    VIEW3D_PT_tools_brush_texture,
    VIEW3D_PT_tools_mask_texture,
    VIEW3D_PT_tools_brush_stroke,
    VIEW3D_PT_tools_brush_stroke_smooth_stroke,
    VIEW3D_PT_tools_brush_falloff,
    VIEW3D_PT_tools_brush_falloff_frontface,
    VIEW3D_PT_tools_brush_falloff_normal,
    VIEW3D_PT_tools_brush_display,
    VIEW3D_PT_tools_weight_gradient,

    VIEW3D_PT_sculpt_dyntopo,
    VIEW3D_PT_sculpt_voxel_remesh,
    VIEW3D_PT_sculpt_symmetry,
    VIEW3D_PT_sculpt_symmetry_for_topbar,
    VIEW3D_PT_sculpt_options,
    VIEW3D_PT_sculpt_options_gravity,

    VIEW3D_PT_curves_sculpt_symmetry,
    VIEW3D_PT_curves_sculpt_symmetry_for_topbar,

    VIEW3D_PT_tools_weightpaint_symmetry,
    VIEW3D_PT_tools_weightpaint_symmetry_for_topbar,
    VIEW3D_PT_tools_weightpaint_options,

    VIEW3D_PT_tools_vertexpaint_symmetry,
    VIEW3D_PT_tools_vertexpaint_symmetry_for_topbar,
    VIEW3D_PT_tools_vertexpaint_options,

    VIEW3D_PT_mask,
    VIEW3D_PT_stencil_projectpaint,
    VIEW3D_PT_tools_imagepaint_options_cavity,

    VIEW3D_PT_tools_imagepaint_symmetry,
    VIEW3D_PT_tools_imagepaint_options,

    VIEW3D_PT_tools_imagepaint_options_external,
    VIEW3D_MT_tools_projectpaint_stencil,

    VIEW3D_PT_tools_particlemode,
    VIEW3D_PT_tools_particlemode_options,
    VIEW3D_PT_tools_particlemode_options_shapecut,
    VIEW3D_PT_tools_particlemode_options_display,

    VIEW3D_PT_gpencil_brush_presets,
    VIEW3D_PT_tools_grease_pencil_brush_select,
    VIEW3D_PT_tools_grease_pencil_brush_settings,
    VIEW3D_PT_tools_grease_pencil_brush_advanced,
    VIEW3D_PT_tools_grease_pencil_brush_stroke,
    VIEW3D_PT_tools_grease_pencil_brush_post_processing,
    VIEW3D_PT_tools_grease_pencil_brush_random,
    VIEW3D_PT_tools_grease_pencil_brush_stabilizer,
    VIEW3D_PT_tools_grease_pencil_brush_gap_closure,
    VIEW3D_PT_tools_grease_pencil_paint_appearance,
    VIEW3D_PT_tools_grease_pencil_sculpt_select,
    VIEW3D_PT_tools_grease_pencil_sculpt_settings,
    VIEW3D_PT_tools_grease_pencil_sculpt_brush_advanced,
    VIEW3D_PT_tools_grease_pencil_sculpt_brush_popover,
    VIEW3D_PT_tools_grease_pencil_sculpt_appearance,
    VIEW3D_PT_tools_grease_pencil_weight_paint_select,
    VIEW3D_PT_tools_grease_pencil_weight_paint_settings,
    VIEW3D_PT_tools_grease_pencil_weight_appearance,
    VIEW3D_PT_tools_grease_pencil_vertex_paint_select,
    VIEW3D_PT_tools_grease_pencil_vertex_paint_settings,
    VIEW3D_PT_tools_grease_pencil_vertex_appearance,
    VIEW3D_PT_tools_grease_pencil_brush_mixcolor,
    VIEW3D_PT_tools_grease_pencil_brush_mix_palette,

    VIEW3D_PT_tools_grease_pencil_brush_paint_falloff,
    VIEW3D_PT_tools_grease_pencil_brush_sculpt_falloff,
    VIEW3D_PT_tools_grease_pencil_brush_weight_falloff,
    VIEW3D_PT_tools_grease_pencil_brush_vertex_color,
    VIEW3D_PT_tools_grease_pencil_brush_vertex_palette,
    VIEW3D_PT_tools_grease_pencil_brush_vertex_falloff,
)


if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
