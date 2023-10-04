
import bpy
from bpy.types import (
    Header,
    Menu,
    Panel,
)

from bl_ui.properties_grease_pencil_common import (
    GreasePencilLayerMasksPanel,
    GreasePencilLayerTransformPanel,
    GreasePencilLayerAdjustmentsPanel,
    GreasePencilLayerRelationsPanel,
    GreasePencilLayerDisplayPanel,
)

from rna_prop_ui import PropertyPanel

from bl_ui.space_toolsystem_common import (ToolSelectPanelHelper)

#######################################
# DopeSheet Filtering - Header Buttons

# used for DopeSheet, NLA, and Graph Editors


def dopesheet_filter(layout, context):
    dopesheet = context.space_data.dopesheet
    is_nla = context.area.type == 'NLA_EDITOR'

    row = layout.row(align=True)
    row.prop(dopesheet, "show_only_selected", text="")
    row.prop(dopesheet, "show_hidden", text="")

    if is_nla:
        row.prop(dopesheet, "show_missing_nla", text="")
    else:  # graph and dopesheet editors - F-Curves and drivers only
        row.prop(dopesheet, "show_only_errors", text="")

#######################################
# Dopesheet Filtering Popovers

# Generic Layout - Used as base for filtering popovers used in all animation editors
# Used for DopeSheet, NLA, and Graph Editors


class DopesheetFilterPopoverBase:
    bl_region_type = 'HEADER'
    bl_label = "Filters"

    # Generic = Affects all datatypes
    # XXX: Perhaps we want these to stay in the header instead, for easy/fast access
    @classmethod
    def draw_generic_filters(cls, context, layout):
        dopesheet = context.space_data.dopesheet
        is_nla = context.area.type == 'NLA_EDITOR'

        col = layout.column(align=True)
        col.prop(dopesheet, "show_only_selected", icon='NONE')
        col.prop(dopesheet, "show_hidden", icon='NONE')

        if is_nla:
            col.prop(dopesheet, "show_missing_nla", icon='NONE')
        else:  # graph and dopesheet editors - F-Curves and drivers only
            col.prop(dopesheet, "show_only_errors", icon='NONE')

    # Name/Membership Filters
    # XXX: Perhaps these should just stay in the headers (exclusively)?
    @classmethod
    def draw_search_filters(cls, context, layout, generic_filters_only=False):
        dopesheet = context.space_data.dopesheet
        is_nla = context.area.type == 'NLA_EDITOR'

        col = layout.column(align=True)
        if not is_nla:
            row = col.row(align=True)
            row.prop(dopesheet, "filter_fcurve_name", text="")
        else:
            row = col.row(align=True)
            row.prop(dopesheet, "filter_text", text="")

    # Standard = Present in all panels
    @classmethod
    def draw_standard_filters(cls, context, layout):
        dopesheet = context.space_data.dopesheet

        # datablock filters
        layout.label(text="Filter by Type:")
        flow = layout.grid_flow(row_major=True, columns=2, even_rows=False, align=False)

        # object types
        if bpy.data.cameras:
            flow.prop(dopesheet, "show_cameras", text="Cameras")
        if bpy.data.meshes:
            flow.prop(dopesheet, "show_meshes", text="Meshes")
        if bpy.data.materials:
            flow.prop(dopesheet, "show_materials", text="Materials")
        flow.prop(dopesheet, "show_transforms", text="Transforms")

class DOPESHEET_PT_animation(Panel):
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'HEADER'
    bl_label = "Animation"

    def draw(self, context):
        layout = self.layout

        layout.operator("action.new_empty", text="New Anim Clip")
        layout.operator("action.new", text="Duplicate Clip")
        layout.operator("action.unlink", text="Unlink Clip")

# Popover for Dopesheet Editor(s) - Dopesheet, Action, Shapekey, GPencil, Mask, etc.
class DOPESHEET_PT_filters(DopesheetFilterPopoverBase, Panel):
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'HEADER'
    bl_label = "Filters"

    def draw(self, context):
        layout = self.layout

        dopesheet = context.space_data.dopesheet
        ds_mode = context.space_data.mode

        layout.prop(dopesheet, "show_summary", text="Summary")

        DopesheetFilterPopoverBase.draw_generic_filters(context, layout)

        if ds_mode in {'DOPESHEET', 'ACTION', 'GPENCIL'}:
            layout.separator()
            generic_filters_only = ds_mode != 'DOPESHEET'
            DopesheetFilterPopoverBase.draw_search_filters(context, layout,
                                                           generic_filters_only=generic_filters_only)

        if ds_mode == 'DOPESHEET':
            layout.separator()
            DopesheetFilterPopoverBase.draw_standard_filters(context, layout)


#######################################
# DopeSheet Editor - General/Standard UI

class DOPESHEET_HT_header(Header):
    bl_space_type = 'DOPESHEET_EDITOR'

    def draw(self, context):
        layout = self.layout

        st = context.space_data

        layout.template_header()

        if st.mode == 'TIMELINE':
            from bl_ui.space_time import (
                # TIME_MT_editor_menus,
                TIME_HT_editor_buttons,
            )
            # TIME_MT_editor_menus.draw_collapsible(context, layout)
            TIME_HT_editor_buttons.draw_header(context, layout)
        else:
            UI_UNITS_X = 4
            row = layout.row()
            
            col = row.column()
            col.ui_units_x = UI_UNITS_X
            col.menu("DOPESHEET_MT_key", text="Keys", shape='TRAPEZOID')
                        
            col = row.column()
            col.ui_units_x = UI_UNITS_X
            col.menu("DOPESHEET_MT_channel", shape='TRAPEZOIDR')
            
            col = row.column()
            col.ui_units_x = UI_UNITS_X
            col.menu("DOPESHEET_MT_marker", text="Bookmarks", shape='TRAPEZOID')
            
            col = row.column()
            col.ui_units_x = UI_UNITS_X
            col.menu("DOPESHEET_MT_select", text="Selection", shape='TRAPEZOIDR')

            col = row.column()
            col.ui_units_x = UI_UNITS_X
            col.menu("DOPESHEET_MT_help", shape='TRAPEZOID')
            row.separator()
            
            if st.mode == 'ACTION':
                row = layout.row(align=True)
                col = row.column()
                col.icon_scale = 0.75
                col.template_ID(st, "action", icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle('ops.graph.clip_list'), show_description=False)
                row.separator()
                
                col = row.column()
                col.prop(context.scene.animname, "name", text="")
                row.separator()
                
                col = row.column()
                col.icon_scale = 0.75
                col.popover(
                    panel="DOPESHEET_PT_animation",
                    text="",
                    icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle('ops.graph.pivot_individual_custom'),
                )
            
            # layout.menu("DOPESHEET_MT_view")
            # if st.show_markers:
            #     layout.menu("DOPESHEET_MT_marker")

            # if st.mode == 'DOPESHEET' or (st.mode == 'ACTION' and st.action is not None):
            # elif st.mode == 'GPENCIL':
            #     layout.menu("DOPESHEET_MT_gpencil_channel")

            # if st.mode != 'GPENCIL':
            #     layout.menu("DOPESHEET_MT_key")
            # else:
            #     layout.menu("DOPESHEET_MT_gpencil_key")

            # DOPESHEET_MT_editor_menus.draw_collapsible(context, layout)
            # DOPESHEET_HT_editor_buttons.draw_header(context, layout)

def animname_set(self, value):
    obj = bpy.context.active_object
    
    if obj is not None:
        animdata = obj.animation_data
        if animdata is not None:
            action = animdata.action
            if action is not None:
                action.name = value

def animname_get(self):
    obj = bpy.context.active_object
    
    if obj is not None:
        animdata = obj.animation_data
        if animdata is not None:
            action = animdata.action
            if action is not None:
                return action.name
        
    return "AnimationName"

class DOPESHEET_PG_animation_name(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.animname = bpy.props.PointerProperty(
            type=cls,
            )
        cls.name = bpy.props.StringProperty(default="AnimationName",
                                        set=animname_set,
                                        get=animname_get)
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.animname

# Header for "normal" dopesheet editor modes (e.g. Dope Sheet, Action, Shape Keys, etc.)
class DOPESHEET_HT_editor_buttons:

    @staticmethod
    def draw_header(context, layout):
        st = context.space_data
        tool_settings = context.tool_settings

        if st.mode in {'ACTION', 'SHAPEKEY'}:
            # TODO: These buttons need some tidying up -
            # Probably by using a popover, and bypassing the template_id() here
            row = layout.row(align=True)
            row.operator("action.layer_prev", text="", icon='TRIA_DOWN')
            row.operator("action.layer_next", text="", icon='TRIA_UP')

            row = layout.row(align=True)
            row.operator("action.push_down", text="Push Down", icon='NLA_PUSHDOWN')
            row.operator("action.stash", text="Stash", icon='FREEZE')

            layout.separator_spacer()

            layout.template_ID(st, "action", new="action.new", unlink="action.unlink")

        # Layer management
        if st.mode == 'GPENCIL':
            ob = context.active_object
            selected = st.dopesheet.show_only_selected
            enable_but = selected and ob is not None and ob.type == 'GPENCIL'

            row = layout.row(align=True)
            row.enabled = enable_but
            row.operator("gpencil.layer_add", icon='ADD', text="")
            row.operator("gpencil.layer_remove", icon='REMOVE', text="")
            row.menu("GPENCIL_MT_layer_context_menu", icon='DOWNARROW_HLT', text="")

            row = layout.row(align=True)
            row.enabled = enable_but
            row.operator("gpencil.layer_move", icon='TRIA_UP', text="").type = 'UP'
            row.operator("gpencil.layer_move", icon='TRIA_DOWN', text="").type = 'DOWN'

            row = layout.row(align=True)
            row.enabled = enable_but
            row.operator("gpencil.layer_isolate", icon='RESTRICT_VIEW_ON', text="").affect_visibility = True
            row.operator("gpencil.layer_isolate", icon='LOCKED', text="").affect_visibility = False

        layout.separator_spacer()

        if st.mode == 'DOPESHEET':
            dopesheet_filter(layout, context)
        elif st.mode == 'ACTION':
            dopesheet_filter(layout, context)
        elif st.mode == 'GPENCIL':
            row = layout.row(align=True)
            row.prop(st.dopesheet, "show_only_selected", text="")
            row.prop(st.dopesheet, "show_hidden", text="")

        layout.popover(
            panel="DOPESHEET_PT_filters",
            text="",
            icon='FILTER',
        )

        # Grease Pencil mode doesn't need snapping, as it's frame-aligned only
        if st.mode != 'GPENCIL':
            layout.prop(st, "auto_snap", text="")

        row = layout.row(align=True)
        row.prop(tool_settings, "use_proportional_action", text="", icon_only=True)
        sub = row.row(align=True)
        sub.active = tool_settings.use_proportional_action
        sub.prop(tool_settings, "proportional_edit_falloff", text="", icon_only=True)


class DOPESHEET_MT_editor_menus(Menu):
    bl_idname = "DOPESHEET_MT_editor_menus"
    bl_label = ""

    def draw(self, context):
        layout = self.layout
        st = context.space_data

        layout.menu("DOPESHEET_MT_view")
        layout.menu("DOPESHEET_MT_select")
        if st.show_markers:
            layout.menu("DOPESHEET_MT_marker")

        if st.mode == 'DOPESHEET' or (st.mode == 'ACTION' and st.action is not None):
            layout.menu("DOPESHEET_MT_channel")
        elif st.mode == 'GPENCIL':
            layout.menu("DOPESHEET_MT_gpencil_channel")

        if st.mode != 'GPENCIL':
            layout.menu("DOPESHEET_MT_key")
        else:
            layout.menu("DOPESHEET_MT_gpencil_key")


class DOPESHEET_MT_view(Menu):
    bl_label = "View"

    def draw(self, context):
        layout = self.layout

        st = context.space_data

        layout.prop(st, "show_region_ui")
        layout.prop(st, "show_region_hud")

        layout.separator()

        layout.prop(st.dopesheet, "use_multi_word_filter", text="Multi-Word Match Search")

        layout.separator()

        layout.prop(st, "use_realtime_update")

        # Sliders are always shown in the Shape Key Editor regardless of this setting.
        col = layout.column()
        col.active = context.space_data.mode != 'SHAPEKEY'
        col.prop(st, "show_sliders")

        layout.prop(st, "show_interpolation")
        layout.prop(st, "show_extremes")
        layout.prop(st, "use_auto_merge_keyframes")

        layout.separator()
        layout.prop(st, "show_markers")

        layout.separator()
        layout.prop(st, "show_seconds")
        layout.prop(st, "show_locked_time")

        layout.separator()
        layout.operator("anim.previewrange_set")
        layout.operator("anim.previewrange_clear")
        layout.operator("action.previewrange_set")

        layout.separator()
        layout.operator("action.view_all")
        layout.operator("action.view_selected")
        layout.operator("action.view_frame")

        # Add this to show key-binding (reverse action in dope-sheet).
        layout.separator()
        props = layout.operator("wm.context_set_enum", text="Toggle Graph Editor", icon='GRAPH')
        props.data_path = "area.type"
        props.value = 'GRAPH_EDITOR'

        layout.separator()
        layout.menu("INFO_MT_area")


class DOPESHEET_MT_view_pie(Menu):
    bl_label = "View"

    def draw(self, _context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator("action.view_all")
        pie.operator("action.view_selected", icon='ZOOM_SELECTED')
        pie.operator("action.view_frame")


class DOPESHEET_MT_select(Menu):
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout

        layout.operator("action.select_all", text="Select (All)").action = 'SELECT'
        layout.operator("action.select_all", text="Select (Invert)").action = 'INVERT'
        layout.operator("action.select_all", text="Select (None)").action = 'DESELECT'
        layout.operator("action.select_linked", text="Select (Full Curve)")

        if context.space_data.mode != 'GPENCIL':
            layout.separator()
            layout.operator("action.select_more", text="Grow Selection")
            layout.operator("action.select_less", text="Shrink Selection")


class DOPESHEET_MT_marker(Menu):
    bl_label = "Marker"

    def draw(self, context):
        layout = self.layout

        layout.column()

        layout.operator("marker.add", text="Create Bookmark")

        layout.separator()

        layout.operator("marker.move", text="Move Bookmark")
        layout.operator("marker.camera_bind", text="Bind Camera")
        props = layout.operator("marker.rename", text="Rename...")
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

#######################################
# Keyframe Editing


class DOPESHEET_MT_channel(Menu):
    bl_label = "Channel"

    def draw(self, _context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_CHANNELS'

        layout.menu("DOPESHEET_MT_move", text="Change Order...")
        layout.menu("DOPESHEET_MT_group", text="Group Channels")

        layout.separator()

        layout.operator("anim.channels_editable_toggle", text="Lock/Unlock Channel")
        layout.operator("anim.channels_setting_toggle", text="Mute/UnMute Channel")

        layout.separator()

        layout.operator("graph.hide", text="Hide").unselected = False
        layout.operator("graph.hide", text="Hide (isolate)").unselected = True
        layout.operator("graph.reveal", text="UnHide")

        layout.separator()

        layout.operator("graph.pre_cycles_modifier_add", text="Pre-Cycle")
        layout.operator("graph.post_cycles_modifier_add", text="Post-Cycle")

        layout.separator()

        layout.operator("anim.channels_delete", text="Delete Channel")

class DOPESHEET_MT_move(Menu):
    bl_label = "Group Channels"

    def draw(self, context):
        layout = self.layout

        layout.operator("anim.channels_move", text="Move to First").direction = "TOP"
        layout.operator("anim.channels_move", text="Move Up").direction = "UP"
        layout.operator("anim.channels_move", text="Move Down").direction = "DOWN"
        layout.operator("anim.channels_move", text="Move to Last").direction = "BOTTOM"

class DOPESHEET_MT_group(Menu):
    bl_label = "Group Channels"

    def draw(self, context):
        layout = self.layout

        layout.operator("anim.channels_group", text="Group")
        layout.operator("anim.channels_ungroup", text="Ungroup")

class DOPESHEET_MT_key(Menu):
    bl_label = "Key"

    def draw(self, context):
        layout = self.layout
        st = context.space_data

        layout.operator("transform.transform", text="Move").mode = 'TIME_TRANSLATE'
        layout.operator("transform.transform", text="Scale").mode = 'TIME_SCALE'
        layout.operator("transform.transform", text="Pinch").mode = 'TIME_SLIDE'

        layout.separator()

        layout.operator("action.keyframe_insert", text="Add New Key").type = "SEL"

        layout.separator()

        layout.menu("DOPESHEET_MT_key_snap", text="Align")

        layout.separator()

        layout.operator("action.copy", text="Copy Selected")
        layout.operator("action.paste", text="Paste at Pointer")
        layout.operator("action.paste", text="Paste Inverted").flipped = True
        layout.operator("action.duplicate_move", text="Duplicate Selected")
        layout.operator("action.delete", text="Delete Selected")

        layout.separator()

        if st.mode != 'GPENCIL':
            layout.menu("DOPESHEET_MT_handle_type", text="Handle Mode")

            layout.separator()

        if st.mode != 'GPENCIL':
            layout.operator_menu_enum("action.interpolation_type", "type", text="Interpolation")
        layout.menu("DOPESHEET_MT_extrapolation_type", text="Extrapolation Mode")

        layout.separator()

        st = context.space_data
        layout.prop(st, "show_seconds", text="Show Frame/Seconds")

        layout.separator()

        layout.operator("action.sample", text="Sample Keyframes")
        layout.operator("action.clean", text="Clean Keyframes").channels = True

        layout.separator()

        layout.menu("DOPESHEET_MT_mirror", text="Mirror\Swap")

class DOPESHEET_MT_key_snap(Menu):
    bl_label = "Snap"

    def draw(self, _context):
        layout = self.layout

        layout.operator("action.snap", text="To pointer frame").type = 'CFRA'
        layout.operator("action.snap", text="To nearest frame").type = 'NEAREST_FRAME'
        layout.operator("action.snap", text="To nearest second").type = 'NEAREST_SECOND'
        layout.operator("action.snap", text="To nearest bookmark").type = 'NEAREST_MARKER'

class DOPESHEET_MT_handle_type(Menu):
    bl_label = "Snap"

    def draw(self, context):
        layout = self.layout
        st = context.space_data

        if st.mode != 'GPENCIL':
            layout.operator("action.handle_type", text="Manual").type = 'FREE'
            layout.operator("action.handle_type", text="Smooth").type = 'ALIGNED'
            layout.operator("action.handle_type", text="Vector").type = 'VECTOR'
            layout.operator("action.handle_type", text="Auto").type = 'AUTO'
            layout.operator("action.handle_type", text="Auto (Clamp)").type = 'AUTO_CLAMPED'

class DOPESHEET_MT_extrapolation_type(Menu):
    bl_label = "Snap"

    def draw(self, context):
        layout = self.layout

        is_graph_editor = context.area.type == 'GRAPH_EDITOR'
        
        if is_graph_editor:
            layout.operator("graph.extrapolation_type", text="Linear").type = 'LINEAR'
            layout.operator("graph.extrapolation_type", text="Constant").type = 'CONSTANT'
        else:
            layout.operator("action.extrapolation_type", text="Linear").type = 'LINEAR'
            layout.operator("action.extrapolation_type", text="Constant").type = 'CONSTANT'

class DOPESHEET_MT_mirror(Menu):
    bl_label = "Snap"

    def draw(self, _context):
        layout = self.layout

        layout.operator("action.mirror", text="by Pointer/Timing").type = 'CFRA'
        layout.operator("action.mirror", text="by Start/Timing").type = 'XAXIS'
        layout.operator("action.mirror", text="by Bookmark/Timing").type = 'MARKER'

class DOPESHEET_MT_key_transform(Menu):
    bl_label = "Transform"

    def draw(self, _context):
        layout = self.layout

        layout.operator("transform.transform", text="Move").mode = 'TIME_TRANSLATE'
        layout.operator("transform.transform", text="Extend").mode = 'TIME_EXTEND'
        layout.operator("transform.transform", text="Slide").mode = 'TIME_SLIDE'
        layout.operator("transform.transform", text="Scale").mode = 'TIME_SCALE'

class DOPESHEET_MT_help(Menu):
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

class DopesheetActionPanelBase:
    bl_region_type = 'UI'
    bl_label = "Action"

    @classmethod
    def draw_generic_panel(cls, _context, layout, action):
        layout.label(text=action.name, icon='ACTION')

        layout.prop(action, "use_frame_range")

        col = layout.column()
        col.active = action.use_frame_range

        row = col.row(align=True)
        row.prop(action, "frame_start", text="Start")
        row.prop(action, "frame_end", text="End")

        col.prop(action, "use_cyclic")


class DOPESHEET_PT_custom_props_action(PropertyPanel, Panel):
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_category = "Action"
    bl_region_type = 'UI'
    bl_context = 'data'
    _context_path = "active_action"
    _property_type = bpy.types.Action

    @classmethod
    def poll(cls, context):
        return bool(context.active_action)


class DOPESHEET_PT_action(DopesheetActionPanelBase, Panel):
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_category = "Action"

    @classmethod
    def poll(cls, context):
        return bool(context.active_action)

    def draw(self, context):
        action = context.active_action
        self.draw_generic_panel(context, self.layout, action)


#######################################
# Grease Pencil Editing

class DOPESHEET_MT_gpencil_channel(Menu):
    bl_label = "Channel"

    def draw(self, _context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_CHANNELS'

        layout.operator("anim.channels_delete")

        layout.separator()
        layout.operator("anim.channels_setting_toggle")
        layout.operator("anim.channels_setting_enable")
        layout.operator("anim.channels_setting_disable")

        layout.separator()
        layout.operator("anim.channels_editable_toggle")

        # XXX: to be enabled when these are ready for use!
        # layout.separator()
        # layout.operator("anim.channels_expand")
        # layout.operator("anim.channels_collapse")

        layout.separator()
        layout.operator_menu_enum("anim.channels_move", "direction", text="Move...")


class DOPESHEET_MT_gpencil_key(Menu):
    bl_label = "Key"

    def draw(self, _context):
        layout = self.layout

        layout.menu("DOPESHEET_MT_key_transform", text="Transform")
        layout.operator_menu_enum("action.snap", "type", text="Snap")
        layout.operator_menu_enum("action.mirror", "type", text="Mirror")

        layout.separator()
        layout.operator("action.keyframe_insert")

        layout.separator()
        layout.operator("action.delete")
        layout.operator("gpencil.interpolate_reverse")

        layout.separator()
        layout.operator("action.keyframe_type", text="Keyframe Type")


class DOPESHEET_MT_delete(Menu):
    bl_label = "Delete"

    def draw(self, _context):
        layout = self.layout

        layout.operator("action.delete")

        layout.separator()

        layout.operator("action.clean").channels = False
        layout.operator("action.clean", text="Clean Channels").channels = True


class DOPESHEET_MT_context_menu(Menu):
    bl_label = "Keys Context Menu"

    @classmethod
    def poll(self, context):
        return context.space_data.type != 'GRAPH_EDITOR'

    def draw(self, context):
        layout = self.layout
        st = context.space_data

        layout.operator_context = 'INVOKE_DEFAULT'

        layout.operator("ed.undo", text="Undo")
        layout.operator("action.view_selected", text="Frame Selected")
        layout.operator("action.view_all", text="Frame All")

        layout.separator()

        layout.operator("transform.transform", text="Move").mode = 'TIME_TRANSLATE'
        layout.operator("transform.transform", text="Scale").mode = 'TIME_SCALE'
        layout.operator("transform.transform", text="Pinch").mode = 'TIME_SLIDE'

        layout.separator()

        layout.operator("action.keyframe_insert", text="Add New Key").type = "SEL"

        layout.separator()

        layout.operator("action.duplicate_move", text="Duplicate Selected")
        layout.operator("action.copy", text="Copy Selected")
        layout.operator("action.paste", text="Paste at Pointer")
        layout.operator("action.paste", text="Paste Inverted").flipped = True
        layout.operator("action.delete", text="Delete Selected")

        layout.separator()

        if st.mode != 'GPENCIL':
            layout.menu("DOPESHEET_MT_handle_type", text="Handle Mode")
            layout.operator_menu_enum("action.interpolation_type", "type", text="Interpolation")

        layout.separator()

        layout.menu("DOPESHEET_MT_key_snap", text="Align")
        layout.menu("DOPESHEET_MT_mirror", text="Mirror\Swap")


class DOPESHEET_MT_channel_context_menu(Menu):
    bl_label = "Channel Context Menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("ed.undo")
        if context.area.type == 'GRAPH_EDITOR':
            layout.operator("graph.view_selected", text="Frame Selected")
            layout.operator("graph.view_all", text="Frame All")
        else:
            layout.operator("action.view_selected", text="Frame Selected")
            layout.operator("action.view_all", text="Frame All")

        layout.separator()

        layout.operator("anim.channels_expand_toggle", text="Expand\Collapse")
        layout.menu("GRAPH_MT_channel_channel_move", text="Change Order")

        layout.separator()

        layout.menu("GRAPH_MT_channel_channels_group", text="Group")

        layout.separator()

        layout.operator("anim.channels_editable_toggle", text="Lock/Unlock Channel")
        layout.operator("anim.channels_setting_toggle", text="Mute/UnMute Channel").type = "MUTE"

        layout.separator()

        layout.operator("anim.channels_delete", text="Delete Channel")

class DOPESHEET_MT_snap_pie(Menu):
    bl_label = "Snap"

    def draw(self, _context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("action.snap", text="Selection to Current Frame").type = 'CFRA'
        pie.operator("action.snap", text="Selection to Nearest Frame").type = 'NEAREST_FRAME'
        pie.operator("action.snap", text="Selection to Nearest Second").type = 'NEAREST_SECOND'
        pie.operator("action.snap", text="Selection to Nearest Marker").type = 'NEAREST_MARKER'


class LayersDopeSheetPanel:
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_category = "View"

    @classmethod
    def poll(cls, context):
        st = context.space_data
        ob = context.object
        if st.mode != 'GPENCIL' or ob is None or ob.type != 'GPENCIL':
            return False

        gpd = ob.data
        gpl = gpd.layers.active
        if gpl:
            return True

        return False


class DOPESHEET_PT_gpencil_mode(LayersDopeSheetPanel, Panel):
    # bl_space_type = 'DOPESHEET_EDITOR'
    # bl_region_type = 'UI'
    # bl_category = "View"
    bl_label = "Layer"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        ob = context.object
        gpd = ob.data
        gpl = gpd.layers.active
        if gpl:
            row = layout.row(align=True)
            row.prop(gpl, "blend_mode", text="Blend")

            row = layout.row(align=True)
            row.prop(gpl, "opacity", text="Opacity", slider=True)

            row = layout.row(align=True)
            row.prop(gpl, "use_lights")


class DOPESHEET_PT_gpencil_layer_masks(LayersDopeSheetPanel, GreasePencilLayerMasksPanel, Panel):
    bl_label = "Masks"
    bl_parent_id = 'DOPESHEET_PT_gpencil_mode'
    bl_options = {'DEFAULT_CLOSED'}


class DOPESHEET_PT_gpencil_layer_transform(LayersDopeSheetPanel, GreasePencilLayerTransformPanel, Panel):
    bl_label = "Transform"
    bl_parent_id = 'DOPESHEET_PT_gpencil_mode'
    bl_options = {'DEFAULT_CLOSED'}


class DOPESHEET_PT_gpencil_layer_adjustments(LayersDopeSheetPanel, GreasePencilLayerAdjustmentsPanel, Panel):
    bl_label = "Adjustments"
    bl_parent_id = 'DOPESHEET_PT_gpencil_mode'
    bl_options = {'DEFAULT_CLOSED'}


class DOPESHEET_PT_gpencil_layer_relations(LayersDopeSheetPanel, GreasePencilLayerRelationsPanel, Panel):
    bl_label = "Relations"
    bl_parent_id = 'DOPESHEET_PT_gpencil_mode'
    bl_options = {'DEFAULT_CLOSED'}


class DOPESHEET_PT_gpencil_layer_display(LayersDopeSheetPanel, GreasePencilLayerDisplayPanel, Panel):
    bl_label = "Display"
    bl_parent_id = 'DOPESHEET_PT_gpencil_mode'
    bl_options = {'DEFAULT_CLOSED'}
    
class DOPESHEET_PT_navigation_bar(Panel):
    bl_label = "Dopesheet navigation"
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'NAVIGATION_BAR'
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        space = context.space_data
        
        row = layout.vert_row()
        row.separator(factor=1.2)
        row.shape = 'TRAPEZOID'
        row.ui_units_y = 10
        row.prop(space, "ui_mode", expand=True)


classes = (
    DOPESHEET_HT_header,
    DOPESHEET_MT_editor_menus,
    DOPESHEET_MT_view,
    DOPESHEET_MT_select,
    DOPESHEET_MT_marker,
    DOPESHEET_MT_channel,
    DOPESHEET_MT_key,
    DOPESHEET_MT_help,
    DOPESHEET_MT_key_transform,
    DOPESHEET_MT_gpencil_channel,
    DOPESHEET_MT_gpencil_key,
    DOPESHEET_MT_delete,
    DOPESHEET_MT_context_menu,
    DOPESHEET_MT_channel_context_menu,
    DOPESHEET_MT_snap_pie,
    DOPESHEET_MT_view_pie,
    DOPESHEET_PT_filters,
    DOPESHEET_MT_key_snap,
    DOPESHEET_MT_handle_type,
    DOPESHEET_MT_extrapolation_type,
    DOPESHEET_MT_mirror,
    DOPESHEET_MT_group,
    DOPESHEET_MT_move,
    DOPESHEET_PG_animation_name,
    # DOPESHEET_PT_action,
    # DOPESHEET_PT_gpencil_mode,
    # DOPESHEET_PT_gpencil_layer_masks,
    # DOPESHEET_PT_gpencil_layer_transform,
    # DOPESHEET_PT_gpencil_layer_adjustments,
    # DOPESHEET_PT_gpencil_layer_relations,
    # DOPESHEET_PT_gpencil_layer_display,
    # DOPESHEET_PT_custom_props_action,
    DOPESHEET_PT_navigation_bar,
    DOPESHEET_PT_animation,
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
