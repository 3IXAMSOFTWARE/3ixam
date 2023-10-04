
import bpy
from bpy.types import Header, Menu, Panel, Operator
from bl_ui.space_dopesheet import (
    DopesheetFilterPopoverBase,
    dopesheet_filter,
)
from bl_ui.space_toolsystem_common import (ToolSelectPanelHelper)
from bpy.props import (
    BoolProperty,
)

class GRAPH_HT_header(Header):
    bl_space_type = 'GRAPH_EDITOR'

    def draw(self, context):
        UI_UNITS_X = 3.5
        layout = self.layout
        
        layout.separator()
        row = layout.row()
        
        col = row.column()
        col.ui_units_x = UI_UNITS_X
        col.menu("GRAPH_MT_key", text="Keys", shape='TRAPEZOID')
        
        col = row.column()
        col.ui_units_x = UI_UNITS_X
        col.menu("GRAPH_MT_channel", shape='TRAPEZOIDR')
        
        col = row.column()
        col.ui_units_x = UI_UNITS_X
        col.menu("GRAPH_MT_marker", text="Bookmarks", shape='TRAPEZOID')
        
        col = row.column()
        col.ui_units_x = UI_UNITS_X
        col.menu("GRAPH_MT_select", text="Selection", shape='TRAPEZOIDR')
        
        col = row.column()
        col.ui_units_x = UI_UNITS_X
        col.menu("GRAPH_MT_help", shape='TRAPEZOID')

        # Now a exposed as a sub-space type
        # layout.prop(st, "mode", text="")

        # GRAPH_MT_editor_menus.draw_collapsible(context, layout)

        # row = layout.row(align=True)
        # row.prop(st, "use_normalization", icon='NORMALIZE_FCURVES', text="Normalize", toggle=True)
        # sub = row.row(align=True)
        # sub.active = st.use_normalization
        # sub.prop(st, "use_auto_normalization", icon='FILE_REFRESH', text="", toggle=True)

        # layout.separator_spacer()

        # dopesheet_filter(layout, context)

        # row = layout.row(align=True)
        # if st.has_ghost_curves:
        #     row.operator("graph.ghost_curves_clear", text="", icon='X')
        # else:
        #     row.operator("graph.ghost_curves_create", text="", icon='FCURVE_SNAPSHOT')

        # layout.popover(
        #     panel="GRAPH_PT_filters",
        #     text="",
        #     icon='FILTER',
        # )

        # layout.prop(st, "pivot_point", icon_only=True)

        # layout.prop(st, "auto_snap", text="")

        # row = layout.row(align=True)
        # row.prop(tool_settings, "use_proportional_fcurve", text="", icon_only=True)
        # sub = row.row(align=True)
        # sub.active = tool_settings.use_proportional_fcurve
        # sub.prop(tool_settings, "proportional_edit_falloff", text="", icon_only=True)

class GRAPH_MT_help(Menu):
    bl_label = "Help"

    def draw(self, context):
        layout = self.layout

        layout.operator(
            "wm.url_open", text="3IXAM Help",
        ).url = "https://www.3ixam.com/faq"
        layout.operator(
            "wm.url_open", text="3IXAM Tutorials",
        ).url = "https://tutorials.3ixam.com"

        layout.separator()

        layout.operator(
            "wm.url_open", text="ProAnimate Docs", icon='TIME',
        )#.url = "https://www.3ixam.com/"

        layout.separator()

        layout.operator(
            "wm.url_open", text="3IXAM Community",
        ).url = "https://www.3ixam.com/community"
        layout.operator(
            "wm.url_open", text="Support",
        ).url = "mailto:Support@3ixam.com"

class GRAPH_HT_tool_header(Header):
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'TOOL_HEADER'

    def draw(self, context):
        make_offset = lambda layout: layout.separator(factor=33)
        layout = self.layout
        tool_settings = context.tool_settings
        
        make_offset(layout)
        row = layout.row(align=True)
        row.icon_scale = 0.75

        row.operator("graph.handle_type", text="", icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle('ops.graph.handletype_manual')).type="FREE"
        row.separator()
        row.operator("graph.handle_type", text="", icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle('ops.graph.handletype_smooth')).type="ALIGNED"
        row.separator()
        row.operator("graph.handle_type", text="", icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle('ops.graph.handletype_vector')).type="VECTOR"
        row.separator()
        row.operator("graph.handle_type", text="", icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle('ops.graph.handletype_auto')).type="AUTO"
        row.separator()
        row.operator("graph.handle_type", text="", icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle('ops.graph.handletype_autoclamp')).type="AUTO_CLAMPED"
        row.separator(factor=3)

        row = layout.row(align=True)
        row.icon_scale = 0.75
        
        row.operator("graph.interpolation_type", text="", icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle('ops.graph.interpolation_linear')).type = "LINEAR"
        row.separator()
        row.operator("graph.interpolation_type", text="", icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle('ops.graph.interpolation_constant')).type = "CONSTANT"
        row.separator()
        row.operator("graph.interpolation_type", text="", icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle('ops.graph.interpolation_besier')).type = "BEZIER"
        row.separator(factor=3)

        row.operator("graph.pre_cycles_modifier_add", text="", icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle('ops.graph.post_circle'))
        row.separator()
        row.operator("graph.post_cycles_modifier_add", text="", icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle('ops.graph.pre_circle'))
        layout.separator_spacer()
        
        row = layout.row(align=True)
        row.icon_scale = 0.75

        row.operator("graph.pivot_point_togge", text="", icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle('ops.graph.pivot_bounds_custom'))
        layout.separator()

        row = layout.row(align=True)
        row.icon_scale = 0.75

        row.operator("graph.normalize_enable", text="", icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle('ops.graph.normalize_enabled'))
        row.separator()
        row.operator("graph.normalize_disable", text="", icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle('ops.graph.normalize_disabled'))
        layout.separator()
        
        layout.prop(tool_settings, "use_proportional_fcurve", text="", icon_only=True)
        layout.separator()
        layout.popover(
            panel="GRAPH_PT_filters",
            text="",
            icon='FILTER',
        )

class GRAPH_OT_pivot_point_toggle(Operator):
    bl_idname = "graph.pivot_point_togge"
    bl_label = "Toggle pivot point"

    def execute(self, context):
        st = context.space_data

        if st.pivot_point == "BOUNDING_BOX_CENTER":
            st.pivot_point = "INDIVIDUAL_ORIGINS"
        else:
            st.pivot_point = "BOUNDING_BOX_CENTER"

        return {'FINISHED'}

class GRAPH_OT_normalize_enable(Operator):
    bl_idname = "graph.normalize_enable"
    bl_label = "Enable graph normalization"

    def execute(self, context):
        st = context.space_data
        st.use_normalization = True

        return {'FINISHED'}

class GRAPH_OT_normalize_disable(Operator):
    bl_idname = "graph.normalize_disable"
    bl_label = "Disable graph normalization"

    def execute(self, context):
        st = context.space_data
        st.use_normalization = False

        return {'FINISHED'}


class GRAPH_PT_filters(DopesheetFilterPopoverBase, Panel):
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'HEADER'
    bl_label = "Filters"

    def draw(self, context):
        layout = self.layout

        DopesheetFilterPopoverBase.draw_search_filters(context, layout)
        layout.separator()
        DopesheetFilterPopoverBase.draw_standard_filters(context, layout)


class GRAPH_MT_editor_menus(Menu):
    bl_idname = "GRAPH_MT_editor_menus"
    bl_label = ""

    def draw(self, context):
        pass


class GRAPH_MT_view(Menu):
    bl_label = "View"

    def draw(self, context):
        layout = self.layout

        st = context.space_data

        layout.prop(st, "show_region_ui")
        layout.prop(st, "show_region_hud")
        layout.separator()

        layout.prop(st, "use_realtime_update")
        layout.prop(st, "show_cursor")
        layout.prop(st, "show_sliders")
        layout.prop(st, "use_auto_merge_keyframes")

        if st.mode != 'DRIVERS':
            layout.separator()
            layout.prop(st, "show_markers")

        layout.separator()
        layout.prop(st, "use_beauty_drawing")

        layout.separator()

        layout.prop(st, "show_extrapolation")

        layout.prop(st, "show_handles")

        layout.prop(st, "use_only_selected_curves_handles")
        layout.prop(st, "use_only_selected_keyframe_handles")

        layout.prop(st, "show_seconds")
        layout.prop(st, "show_locked_time")

        layout.separator()
        layout.operator("anim.previewrange_set")
        layout.operator("anim.previewrange_clear")
        layout.operator("graph.previewrange_set")

        layout.separator()
        layout.operator("graph.view_all")
        layout.operator("graph.view_selected")
        layout.operator("graph.view_frame")

        # Add this to show key-binding (reverse action in dope-sheet).
        layout.separator()
        props = layout.operator("wm.context_set_enum", text="Toggle Dope Sheet")
        props.data_path = "area.type"
        props.value = 'DOPESHEET_EDITOR'

        layout.separator()
        layout.menu("INFO_MT_area")


class GRAPH_MT_select(Menu):
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        st = context.space_data

        layout.operator("graph.select_all", text="Select (All)").action = 'SELECT'
        layout.operator("graph.select_all", text="Select (Invert)").action = 'INVERT'
        layout.operator("graph.select_all", text="Select (None)").action = 'DESELECT'
        layout.operator("graph.select_linked", text="Select (Full Curve)")

        layout.separator()

        layout.operator("graph.select_more", text="Grow Selection")
        layout.operator("graph.select_less", text="Shrink Selection")

        layout.separator()

        layout.prop(st, "use_normalization", icon='NORMALIZE_FCURVES', text="Normalize", toggle=True)

class GRAPH_MT_marker(Menu):
    bl_label = "Marker"

    def draw(self, context):
        layout = self.layout

        layout.column()
        layout.operator("marker.add", text="Create Bookmark")
        layout.operator("marker.camera_bind", text="Bind Camera")
        layout.operator("marker.rename", text="Rename...")
        layout.operator("marker.duplicate", text="Copy Bookmark")

        layout.separator()

        tool_settings = context.tool_settings
        layout.prop(tool_settings, "lock_markers", text="Lock all Bookmarks")

        layout.separator()

        layout.operator("marker.select_all", text="Select (All)").action = 'SELECT'
        layout.operator("marker.select_all", text="Select (Invert)").action = 'INVERT'
        layout.operator("marker.select_all", text="Select (None)").action = 'DESELECT'
        
        layout.separator()

        layout.operator("marker.delete", text="Delete Bookmark")


class GRAPH_MT_channel(Menu):
    bl_label = "Channel"

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_CHANNELS'

        layout.menu("GRAPH_MT_channel_channel_move", text="Change Order")

        layout.separator()

        layout.menu("GRAPH_MT_channel_channels_group", text="Group")

        layout.separator()

        layout.operator("anim.channels_editable_toggle", text="Lock/Unlock Channel")
        layout.operator("anim.channels_setting_toggle", text="Mute/Unmute Channel").type = "MUTE"

        layout.separator()

        layout.operator("graph.hide", text="Hide").unselected = False
        layout.operator("graph.hide", text="Hide (Isolate)").unselected = True
        layout.operator("graph.reveal", text="UnHide")

        layout.separator()

        layout.operator("graph.pre_cycles_modifier_add", text="Pre-Cycle")
        layout.operator("graph.post_cycles_modifier_add", text="Post-Cycle")

        layout.separator()

        layout.operator("graph.bake", text="Freeze Channel")
        layout.operator("graph.unbake", text="UnFreeze (Rebuild)")

        layout.separator()

        layout.operator("anim.channels_delete", text="Delete Channel")

class GRAPH_OT_cycles_modifier_pre_add(Operator):
    bl_idname = "graph.pre_cycles_modifier_add"
    bl_label = "Add Pre-Cycles Modifier"
    bl_description = "Add Curve Pre-Cycles Modifier"

    @classmethod
    def poll(self, context):
        return bpy.ops.graph.fmodifier_add.poll()
    
    def execute(self, context):
        # op = bpy.ops.graph.fmodifier_add(type="CYCLES")
        # if 'FINISHED' in op:
        fcurves = context.active_object.animation_data.action.fcurves
        for fcurve in fcurves:
            if fcurve.select:
                modifiers = fcurve.modifiers

                if not len(modifiers):
                    modifier = modifiers.new('CYCLES')
                    modifier.mode_after = 'NONE'
                else:
                    for modifier in modifiers:
                        if modifier.mode_before == 'NONE':
                            modifier.mode_before = 'REPEAT'
                        else:
                            modifier.mode_before = 'NONE'
                        
        return {"FINISHED"}

class GRAPH_OT_cycles_modifier_post_add(Operator):
    bl_idname = "graph.post_cycles_modifier_add"
    bl_label = "Add Post-Cycles Modifier"
    bl_description = "Add Curve Post-Cycles Modifier"

    @classmethod
    def poll(self, context):
        return bpy.ops.graph.fmodifier_add.poll()
    
    def execute(self, context):
        fcurves = context.active_object.animation_data.action.fcurves
        for fcurve in fcurves:
            if fcurve.select:
                modifiers = fcurve.modifiers

                if not len(modifiers):
                    modifier = modifiers.new('CYCLES')
                    modifier.mode_before = 'NONE'
                else:
                    for modifier in modifiers:
                        if modifier.mode_after == 'NONE':
                            modifier.mode_after = 'REPEAT'
                        else:
                            modifier.mode_after = 'NONE'

        return {"FINISHED"}

class GRAPH_MT_channel_channels_group(Menu):
    bl_label = "Group"

    def draw(self, context):
        layout = self.layout

        layout.operator("anim.channels_group", text="Group")
        layout.operator("anim.channels_ungroup", text="UnGroup")

class GRAPH_MT_channel_channel_move(Menu):
    bl_label = "Channel Move"

    def draw(self, context):
        layout = self.layout

        layout.operator("anim.channels_move", text="Move to First").direction = "TOP"
        layout.operator("anim.channels_move", text="Move Up").direction = "UP"
        layout.operator("anim.channels_move", text="Move Down").direction = "DOWN"
        layout.operator("anim.channels_move", text="Move to Last").direction = "BOTTOM"

class GRAPH_MT_key(Menu):
    bl_label = "Key"

    def draw(self, _context):
        layout = self.layout

        layout.operator("transform.translate", text="Move")
        layout.operator("transform.rotate", text="Rotate")
        layout.operator("transform.resize", text="Scale")
        layout.operator("graph.breakdown", text="Breakdown")
        layout.operator("graph.smooth", text="Smooth")

        layout.separator()

        layout.operator("graph.keyframe_insert", text="Add New Key on Curve").type = 'SEL'
        layout.operator("graph.keyframe_insert", text="Add New Key on Curve").type = 'ALL'

        layout.separator()

        layout.menu("GRAPH_MT_key_snap", text="Align")

        layout.separator()

        layout.operator("graph.copy", text="Copy Selected")
        layout.operator("graph.paste", text="Paste at Pointer")
        layout.operator("graph.paste", text="Paste Inverted").flipped = True
        layout.operator("graph.duplicate_move", text="Duplicate Selected")
        layout.operator("graph.delete", text="Delete Selected")

        layout.separator()

        layout.menu("GRAPH_MT_key_handle_type", text="Handle Mode")

        layout.separator()

        layout.menu("GRAPH_MT_key_interpolation", text="Interpolation")
        layout.menu("GRAPH_MT_key_extrapolation", text="Extrapolation")

        layout.separator()

        layout.operator("graph.sample", text="Sample Keyframes")
        layout.operator("graph.decimate", text="Simplify (in %)").mode = 'RATIO'

        layout.separator()

        layout.menu("GRAPH_MT_key_mirror", text="Mirror\Swap")

class GRAPH_MT_key_interpolation(Menu):
    bl_label = "Interpolation"

    def draw(self, context):
        layout = self.layout

        layout.operator("graph.interpolation_type", text="Linear").type = "LINEAR"
        layout.operator("graph.interpolation_type", text="Constant").type = "CONSTANT"
        layout.operator("graph.interpolation_type", text="Bezier").type = "BEZIER"

class GRAPH_MT_key_extrapolation(Menu):
    bl_label = "Extrapolation"

    def draw(self, context):
        layout = self.layout

        layout.operator("graph.extrapolation_type", text="Linear").type = "LINEAR"
        layout.operator("graph.extrapolation_type", text="Constant").type = "CONSTANT"

class GRAPH_MT_key_mirror(Menu):
    bl_label = "Mirror/Swap"

    def draw(self, context):
        layout = self.layout

        layout.operator("graph.mirror", text="by Pointer/Timing").type = "CFRA"
        layout.operator("graph.mirror", text="by Pointer/Values").type = "VALUE"
        layout.operator("graph.mirror", text="by Start Frame/Values").type = "XAXIS"
        layout.operator("graph.mirror", text="by Start/Timing").type = "YAXIS"
        layout.operator("graph.mirror", text="by Bookmark/Timing").type = "MARKER"

class GRAPH_MT_key_handle_type(Menu):
    bl_label = "Handle Type"

    def draw(self, context):
        layout = self.layout

        layout.operator("graph.handle_type", text="Manual", icon="NONE").type="FREE"
        layout.operator("graph.handle_type", text="Smooth", icon="NONE").type="ALIGNED"
        layout.operator("graph.handle_type", text="Vector", icon="NONE").type="VECTOR"
        layout.operator("graph.handle_type", text="Auto", icon="NONE").type="AUTO"
        layout.operator("graph.handle_type", text="Auto (Clamp)", icon="NONE").type="AUTO_CLAMPED"

class GRAPH_MT_key_transform(Menu):
    bl_label = "Transform"

    def draw(self, _context):
        layout = self.layout

        layout.operator("transform.translate", text="Move")
        layout.operator("transform.transform", text="Extend").mode = 'TIME_EXTEND'
        layout.operator("transform.rotate", text="Rotate")
        layout.operator("transform.resize", text="Scale")


class GRAPH_MT_key_snap(Menu):
    bl_label = "Snap"

    def draw(self, _context):
        layout = self.layout

        layout.operator("graph.snap", text="To nearest frame").type = 'NEAREST_FRAME'
        layout.operator("graph.snap", text="To pointer value").type = 'VALUE'
        layout.operator("graph.snap", text="To nearest second").type = 'NEAREST_SECOND'
        layout.operator("graph.snap", text="To nearest bookmark").type = 'NEAREST_MARKER'
        layout.operator("graph.frame_jump", text="Pointer to key")

class GRAPH_MT_slider(Menu):
    bl_label = "Slider Operators"

    def draw(self, _context):
        layout = self.layout

        layout.operator("graph.breakdown", text="Breakdown")
        layout.operator("graph.blend_to_neighbor", text="Blend to Neighbor")
        layout.operator("graph.blend_to_default", text="Blend to Default Value")


class GRAPH_MT_view_pie(Menu):
    bl_label = "View"

    def draw(self, _context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator("graph.view_all")
        pie.operator("graph.view_selected", icon='ZOOM_SELECTED')
        pie.operator("graph.view_frame")


class GRAPH_MT_delete(Menu):
    bl_label = "Delete"

    def draw(self, _context):
        layout = self.layout

        layout.operator("graph.delete")

        layout.separator()

        layout.operator("graph.clean").channels = False
        layout.operator("graph.clean", text="Clean Channels").channels = True


class GRAPH_MT_context_menu(Menu):
    bl_label = "Wave Context Menu"

    def draw(self, _context):
        layout = self.layout

        layout.operator_context = 'INVOKE_DEFAULT'

        layout.operator("ed.undo")
        layout.operator("graph.view_selected", text="Frame Selected")
        layout.operator("graph.view_all", text="Frame All")

        layout.separator()

        layout.operator("transform.translate", text="Move")
        layout.operator("transform.rotate", text="Rotate")
        layout.operator("transform.resize", text="Scale")

        layout.separator()

        layout.operator("graph.keyframe_insert", text="Add New Key on Curve").type = 'SEL'

        layout.separator()

        layout.operator("graph.duplicate_move", text="Duplicate Selected")
        layout.operator("graph.copy", text="Copy Selected")
        layout.operator("graph.paste", text="Paste at Pointer")
        layout.operator("graph.paste", text="Paste Inverted").flipped = True
        layout.operator("graph.delete", text="Delete Selected")

        layout.separator()

        layout.menu("GRAPH_MT_key_handle_type", text="Handle Mode")
        layout.menu("GRAPH_MT_key_interpolation", text="Interpolation")

        layout.separator()

        layout.menu("GRAPH_MT_key_snap", text="Align")
        layout.menu("GRAPH_MT_key_mirror", text="Mirror\Swap")


class GRAPH_MT_pivot_pie(Menu):
    bl_label = "Pivot Point"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.prop_enum(context.space_data, "pivot_point", value='BOUNDING_BOX_CENTER')
        pie.prop_enum(context.space_data, "pivot_point", value='CURSOR')
        pie.prop_enum(context.space_data, "pivot_point", value='INDIVIDUAL_ORIGINS')


class GRAPH_MT_snap_pie(Menu):
    bl_label = "Snap"

    def draw(self, _context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("graph.snap", text="Selection to Current Frame").type = 'CFRA'
        pie.operator("graph.snap", text="Selection to Cursor Value").type = 'VALUE'
        pie.operator("graph.snap", text="Selection to Nearest Frame").type = 'NEAREST_FRAME'
        pie.operator("graph.snap", text="Selection to Nearest Second").type = 'NEAREST_SECOND'
        pie.operator("graph.snap", text="Selection to Nearest Marker").type = 'NEAREST_MARKER'
        pie.operator("graph.snap", text="Flatten Handles").type = 'HORIZONTAL'
        pie.operator("graph.frame_jump", text="Cursor to Selection")
        pie.operator("graph.snap_cursor_value", text="Cursor Value to Selection")


class GRAPH_MT_channel_context_menu(Menu):
    bl_label = "F-Curve Channel Context Menu"

    def draw(self, context):
        layout = self.layout
        st = context.space_data

        layout.separator()
        layout.operator("anim.channels_setting_enable", text="Mute Channels").type = 'MUTE'
        layout.operator("anim.channels_setting_disable", text="Unmute Channels").type = 'MUTE'
        layout.separator()
        layout.operator("anim.channels_setting_enable", text="Protect Channels").type = 'PROTECT'
        layout.operator("anim.channels_setting_disable", text="Unprotect Channels").type = 'PROTECT'

        layout.separator()
        layout.operator("anim.channels_group")
        layout.operator("anim.channels_ungroup")

        layout.separator()
        layout.operator("anim.channels_editable_toggle")
        layout.operator_menu_enum("graph.extrapolation_type", "type", text="Extrapolation Mode")

        layout.separator()
        layout.operator("graph.hide", text="Hide Selected Curves").unselected = False
        layout.operator("graph.hide", text="Hide Unselected Curves").unselected = True
        layout.operator("graph.reveal")

        layout.separator()
        layout.operator("anim.channels_expand")
        layout.operator("anim.channels_collapse")

        layout.separator()
        layout.operator_menu_enum("anim.channels_move", "direction", text="Move...")

        layout.separator()

        layout.operator("anim.channels_delete")
        if st.mode == 'DRIVERS':
            layout.operator("graph.driver_delete_invalid")


classes = (
    GRAPH_HT_header,
    GRAPH_MT_editor_menus,
    GRAPH_MT_view,
    GRAPH_MT_select,
    GRAPH_MT_marker,
    GRAPH_MT_channel,
    GRAPH_MT_key,
    GRAPH_MT_key_transform,
    GRAPH_MT_key_snap,
    GRAPH_MT_slider,
    GRAPH_MT_delete,
    GRAPH_MT_context_menu,
    GRAPH_MT_channel_context_menu,
    GRAPH_MT_pivot_pie,
    GRAPH_MT_snap_pie,
    GRAPH_MT_view_pie,
    GRAPH_PT_filters,
    GRAPH_HT_tool_header,
    GRAPH_MT_key_handle_type,
    GRAPH_MT_key_interpolation,
    GRAPH_MT_key_extrapolation,
    GRAPH_MT_key_mirror,
    GRAPH_MT_channel_channel_move,
    GRAPH_MT_channel_channels_group,
    GRAPH_MT_help,
    GRAPH_OT_normalize_enable,
    GRAPH_OT_normalize_disable,
    GRAPH_OT_pivot_point_toggle,
    GRAPH_OT_cycles_modifier_post_add,
    GRAPH_OT_cycles_modifier_pre_add,
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)