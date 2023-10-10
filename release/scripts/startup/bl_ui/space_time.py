# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
from bpy.types import Menu, Panel
from bpy.app.translations import contexts as i18n_contexts


# Header buttons for timeline header (play, etc.)
class TIME_HT_editor_buttons:

    @staticmethod
    def draw_header(context, layout):
        scene = context.scene
        tool_settings = context.tool_settings
        screen = context.screen

        layout.separator_spacer()

        row = layout.row(align=True)
        row.shape = 'ADVANCED'
        
        if not scene.use_preview_range:
            row.prop(scene, "frame_start", text="")
        else:
            row.prop(scene, "frame_preview_start", text="")
        row.separator()
        
        sub = row.column().absolute()
        sub.scale_x=1.5
        sub.prop(tool_settings, "use_keyframe_insert_auto", text="", icon="PANEL_CLOSE" if tool_settings.use_keyframe_insert_auto else "ADD")
        
        sub = row.column().absolute()
        sub.scale_x=1.5
        sub.operator("screen.frame_jump", text="", icon='PREV_KEYFRAME').end = False
        
        sub = row.column().absolute()
        sub.scale_x=1.5
        sub.operator("screen.keyframe_jump", text="", icon='REW').next = False
        
        sub = row.column().absolute()
        sub.scale_x=1.5
        sub.operator("screen.animation_play", text="", icon='FRAME_NEXT')
        
        sub = row.column().absolute()
        sub.scale_x=1.5
        sub.operator("screen.keyframe_jump", text="", icon='FF').next = True
        
        sub = row.column().absolute()
        sub.scale_x=1.5
        sub.operator("screen.frame_jump", text="", icon='NEXT_KEYFRAME').end = True

        row.separator()
        if not scene.use_preview_range:
            row.prop(scene, "frame_end", text="")
        else:
            row.prop(scene, "frame_preview_end", text="")

        layout.separator_spacer()


class TIME_MT_editor_menus(Menu):
    bl_idname = "TIME_MT_editor_menus"
    bl_label = ""

    def draw(self, context):
        layout = self.layout
        horizontal = (layout.direction == 'VERTICAL')
        st = context.space_data
        if horizontal:
            row = layout.row()
            sub = row.row(align=True)
        else:
            sub = layout

        sub.popover(
            panel="TIME_PT_playback",
            text="Playback",
        )
        sub.popover(
            panel="TIME_PT_keyframing_settings",
            text="Keying",
            text_ctxt=i18n_contexts.id_windowmanager,
        )

        # Add a separator to keep the popover button from aligning with the menu button.
        sub.separator(factor=0.4)

        if horizontal:
            sub = row.row(align=True)

        sub.menu("TIME_MT_view")
        if st.show_markers:
            sub.menu("TIME_MT_marker")


class TIME_MT_marker(Menu):
    bl_label = "Marker"

    def draw(self, context):
        layout = self.layout

        marker_menu_generic(layout, context)


class TIME_MT_view(Menu):
    bl_label = "View"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        st = context.space_data

        layout.prop(st, "show_region_hud")

        layout.separator()

        layout.prop(st, "show_seconds")
        layout.prop(st, "show_locked_time")

        layout.separator()

        layout.prop(st, "show_markers")

        layout.separator()

        layout.prop(scene, "show_keys_from_selected_only")
        layout.prop(st.dopesheet, "show_only_errors")

        layout.separator()

        layout.menu("TIME_MT_cache")

        layout.separator()

        # NOTE: "action" now, since timeline is in the dopesheet editor, instead of as own editor
        layout.operator("action.view_all")
        layout.operator("action.view_frame")

        layout.separator()

        layout.menu("INFO_MT_area")


class TIME_MT_cache(Menu):
    bl_label = "Cache"

    def draw(self, context):
        layout = self.layout

        st = context.space_data

        layout.prop(st, "show_cache")

        layout.separator()

        col = layout.column()
        col.enabled = st.show_cache
        col.prop(st, "cache_softbody")
        col.prop(st, "cache_particles")
        col.prop(st, "cache_cloth")
        col.prop(st, "cache_smoke")
        col.prop(st, "cache_dynamicpaint")
        col.prop(st, "cache_rigidbody")


def marker_menu_generic(layout, context):

    # layout.operator_context = 'EXEC_REGION_WIN'

    layout.column()
    layout.operator("marker.add", text="Add Marker")
    layout.operator("marker.duplicate", text="Duplicate Marker")

    if len(bpy.data.scenes) > 10:
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("marker.make_links_scene", text="Duplicate Marker to Scene...", icon='OUTLINER_OB_EMPTY')
    else:
        layout.operator_menu_enum("marker.make_links_scene", "scene", text="Duplicate Marker to Scene")

    layout.operator("marker.delete", text="Delete Marker")

    layout.separator()

    props = layout.operator("wm.call_panel", text="Rename Marker")
    props.name = "TOPBAR_PT_name_marker"
    props.keep_open = False
    layout.operator("marker.move", text="Move Marker")

    layout.separator()

    layout.menu('NLA_MT_marker_select')

    layout.separator()

    layout.operator("marker.camera_bind")

    layout.separator()

    layout.operator("screen.marker_jump", text="Jump to Next Marker").next = True
    layout.operator("screen.marker_jump", text="Jump to Previous Marker").next = False

    layout.separator()
    tool_settings = context.tool_settings
    layout.prop(tool_settings, "lock_markers")

###################################


class TimelinePanelButtons:
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'

    @staticmethod
    def has_timeline(context):
        return context.space_data.mode == 'TIMELINE'


class TIME_PT_playback(TimelinePanelButtons, Panel):
    bl_label = "Playback"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 11

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        screen = context.screen
        scene = context.scene

        layout.prop(scene, "sync_mode", text="Sync")
        col = layout.column(heading="Audio")
        col.prop(scene, "use_audio_scrub", text="Scrubbing")
        col.prop(scene, "use_audio", text="Mute")

        col = layout.column(heading="Playback")
        col.prop(scene, "lock_frame_selection_to_range", text="Limit to Frame Range")
        col.prop(screen, "use_follow", text="Follow Current Frame")

        col = layout.column(heading="Play In")
        col.prop(screen, "use_play_top_left_3d_editor", text="Active Editor")
        col.prop(screen, "use_play_3d_editors", text="3D Viewport")
        col.prop(screen, "use_play_animation_editors", text="Animation Editors")
        col.prop(screen, "use_play_image_editors", text="Image Editor")
        col.prop(screen, "use_play_properties_editors", text="Properties Editor")
        col.prop(screen, "use_play_clip_editors", text="Movie Clip Editor")
        col.prop(screen, "use_play_node_editors", text="Node Editors")
        col.prop(screen, "use_play_sequence_editors", text="Video Sequencer")

        col = layout.column(heading="Show")
        col.prop(scene, "show_subframe", text="Subframes")

        layout.separator()

        row = layout.row(align=True)
        row.operator("anim.start_frame_set")
        row.operator("anim.end_frame_set")


class TIME_PT_keyframing_settings(TimelinePanelButtons, Panel):
    bl_label = "Keyframing Settings"
    bl_options = {'HIDE_HEADER'}
    bl_region_type = 'HEADER'

    @classmethod
    def poll(cls, context):
        # only for timeline editor
        return cls.has_timeline(context)

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        tool_settings = context.tool_settings

        col = layout.column(align=True)
        col.label(text="Active Keying Set")
        row = col.row(align=True)
        row.prop_search(scene.keying_sets_all, "active", scene, "keying_sets_all", text="")
        row.operator("anim.keyframe_insert", text="", icon='KEY_HLT')
        row.operator("anim.keyframe_delete", text="", icon='KEY_DEHLT')

        col = layout.column(align=True)
        col.label(text="New Keyframe Type")
        col.prop(tool_settings, "keyframe_type", text="")

        layout.prop(tool_settings, "use_keyframe_cycle_aware")


class TIME_PT_auto_keyframing(TimelinePanelButtons, Panel):
    bl_label = "Auto Keyframing"
    bl_options = {'HIDE_HEADER'}
    bl_region_type = 'HEADER'
    bl_ui_units_x = 9

    @classmethod
    def poll(cls, context):
        # Only for timeline editor.
        return cls.has_timeline(context)

    def draw(self, context):
        layout = self.layout

        tool_settings = context.tool_settings
        prefs = context.preferences

        layout.active = tool_settings.use_keyframe_insert_auto

        layout.prop(tool_settings, "auto_keying_mode", expand=True)

        col = layout.column(align=True)
        col.prop(tool_settings, "use_keyframe_insert_keyingset", text="Only Active Keying Set", toggle=False)
        if not prefs.edit.use_keyframe_insert_available:
            col.prop(tool_settings, "use_record_with_nla", text="Layered Recording")


###################################

classes = (
    TIME_MT_editor_menus,
    TIME_MT_marker,
    TIME_MT_view,
    TIME_MT_cache,
    TIME_PT_playback,
    TIME_PT_keyframing_settings,
    TIME_PT_auto_keyframing
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
