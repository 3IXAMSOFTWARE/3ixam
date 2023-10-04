import bpy
import sys
import subprocess
from bpy.types import Header, Menu, Panel

from bpy.app.translations import (
    pgettext_iface as iface_,
    contexts as i18n_contexts,
)


class TOPBAR_HT_upper_bar(Header):
    bl_space_type = 'TOPBAR'

    def draw(self, context):
        region = context.region

        if region.alignment == 'RIGHT':
            self.draw_right(context)
        else:
            self.draw_left(context)

    def draw_left(self, context):
        layout = self.layout

        window = context.window
        screen = context.screen

        TOPBAR_MT_editor_menus.draw_collapsible(context, layout)
        
        """
        layout.separator()
        
        if not screen.show_fullscreen:
            layout.template_ID_tabs(
                window, "workspace",
                new="workspace.add",
                menu="TOPBAR_MT_workspace_menu",
            )
        else:
            layout.operator(
                "screen.back_to_previous",
                icon='SCREEN_BACK',
                text="Back to Previous",
            )
        """

    def draw_right(self, context):
        layout = self.layout

        window = context.window
        screen = context.screen
        scene = window.scene

        """
        # If statusbar is hidden, still show messages at the top
        if not screen.show_statusbar:
            layout.template_reports_banner()
            layout.template_running_jobs()

        # Active workspace view-layer is retrieved through window, not through workspace.
        layout.template_ID(window, "scene", new="scene.new",
                           unlink="scene.delete")

        row = layout.row(align=True)
        row.template_search(
            window, "view_layer",
            scene, "view_layers",
            new="scene.view_layer_add",
            unlink="scene.view_layer_remove")

        """


class TOPBAR_PT_tool_settings_extra(Panel):
    """
    Popover panel for adding extra options that don't fit in the tool settings header
    """
    bl_idname = "TOPBAR_PT_tool_settings_extra"
    bl_region_type = 'HEADER'
    bl_space_type = 'TOPBAR'
    bl_label = "Extra Options"

    def draw(self, context):
        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        layout = self.layout

        # Get the active tool
        space_type, mode = ToolSelectPanelHelper._tool_key_from_context(
            context)
        cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)
        item, tool, _ = cls._tool_get_active(
            context, space_type, mode, with_icon=True)
        if item is None:
            return

        # Draw the extra settings
        item.draw_settings(context, layout, tool, extra=True)


class TOPBAR_PT_tool_fallback(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "Layers"
    bl_ui_units_x = 8

    def draw(self, context):
        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        layout = self.layout

        tool_settings = context.tool_settings
        ToolSelectPanelHelper.draw_fallback_tool_items(layout, context)
        if tool_settings.workspace_tool_type == 'FALLBACK':
            tool = context.tool
            ToolSelectPanelHelper.draw_active_tool_fallback(
                context, layout, tool)


class TOPBAR_PT_gpencil_layers(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "Layers"
    bl_ui_units_x = 14

    @classmethod
    def poll(cls, context):
        if context.gpencil_data is None:
            return False

        ob = context.object
        if ob is not None and ob.type == 'GPENCIL':
            return True

        return False

    def draw(self, context):
        layout = self.layout
        gpd = context.gpencil_data

        # Grease Pencil data...
        if (gpd is None) or (not gpd.layers):
            layout.operator("gpencil.layer_add", text="New Layer")
        else:
            self.draw_layers(context, layout, gpd)

    def draw_layers(self, context, layout, gpd):
        row = layout.row()

        col = row.column()
        layer_rows = 10
        col.template_list("GPENCIL_UL_layer", "", gpd, "layers", gpd.layers, "active_index",
                          rows=layer_rows, sort_reverse=True, sort_lock=True)

        gpl = context.active_gpencil_layer
        if gpl:
            srow = col.row(align=True)
            srow.prop(gpl, "blend_mode", text="Blend")

            srow = col.row(align=True)
            srow.prop(gpl, "opacity", text="Opacity", slider=True)
            srow.prop(gpl, "use_mask_layer", text="",
                      icon='MOD_MASK' if gpl.use_mask_layer else 'LAYER_ACTIVE')

            srow = col.row(align=True)
            srow.prop(gpl, "use_lights")

        col = row.column()

        sub = col.column(align=True)
        sub.operator("gpencil.layer_add", icon='ADD', text="")
        sub.operator("gpencil.layer_remove", icon='REMOVE', text="")

        gpl = context.active_gpencil_layer
        if gpl:
            sub.menu("GPENCIL_MT_layer_context_menu",
                     icon='DOWNARROW_HLT', text="")

            if len(gpd.layers) > 1:
                col.separator()

                sub = col.column(align=True)
                sub.operator("gpencil.layer_move",
                             icon='TRIA_UP', text="").type = 'UP'
                sub.operator("gpencil.layer_move",
                             icon='TRIA_DOWN', text="").type = 'DOWN'

                col.separator()

                sub = col.column(align=True)
                sub.operator("gpencil.layer_isolate", icon='HIDE_OFF',
                             text="").affect_visibility = True
                sub.operator("gpencil.layer_isolate", icon='LOCKED',
                             text="").affect_visibility = False


class TOPBAR_MT_editor_menus(Menu):
    bl_idname = "TOPBAR_MT_editor_menus"
    bl_label = ""

    def draw(self, context):
        from itertools import cycle as itertools_cycle

        layout = self.layout
        button_scale = 4.1

        alternating_shape_gen = itertools_cycle(['TRAPEZOID', 'TRAPEZOIDR'])
        alternating_shape = lambda: next(alternating_shape_gen)

        def trapezoid_menu(*args, **kwargs):
            sub = layout.row(align=True)
            sub.ui_units_x = button_scale
            sub.menu(*args, shape=alternating_shape(), **kwargs)
            layout.separator(factor=2.0)


        trapezoid_menu("TOPBAR_MT_file")
        trapezoid_menu("TOPBAR_MT_window")
        trapezoid_menu("TOPBAR_MT_materials")
        trapezoid_menu("TOPBAR_MT_object")
        trapezoid_menu("TOPBAR_MT_render")
        trapezoid_menu("TOPBAR_MT_help")

class TOPBAR_MT_ixam(Menu):
    bl_label = "3IXAM"

    def draw(self, _context):
        layout = self.layout
        
        layout.operator("wm.splash")
        layout.operator("wm.splash_about")

        layout.separator()

        layout.separator()
        layout.operator("screen.userpref_show", text="User Preferences")
        layout.menu("TOPBAR_MT_file_defaults")


class TOPBAR_MT_file_cleanup(Menu):
    bl_label = "Clean Up"

    def draw(self, _context):
        layout = self.layout
        layout.separator()

        op_props = layout.operator("outliner.orphans_purge", text="Unused Data-Blocks")
        op_props.do_local_ids = True
        op_props.do_linked_ids = True
        op_props.do_recursive = False
        op_props = layout.operator("outliner.orphans_purge", text="Recursive Unused Data-Blocks")
        op_props.do_local_ids = True
        op_props.do_linked_ids = True
        op_props.do_recursive = True

        layout.separator()
        op_props = layout.operator("outliner.orphans_purge", text="Unused Linked Data-Blocks")
        op_props.do_local_ids = False
        op_props.do_linked_ids = True
        op_props.do_recursive = False
        op_props = layout.operator("outliner.orphans_purge", text="Recursive Unused Linked Data-Blocks")
        op_props.do_local_ids = False
        op_props.do_linked_ids = True
        op_props.do_recursive = True

        layout.separator()
        op_props = layout.operator("outliner.orphans_purge", text="Unused Local Data-Blocks")
        op_props.do_local_ids = True
        op_props.do_linked_ids = False
        op_props.do_recursive = False
        op_props = layout.operator("outliner.orphans_purge", text="Recursive Unused Local Data-Blocks")
        op_props.do_local_ids = True
        op_props.do_linked_ids = False
        op_props.do_recursive = True


class TOPBAR_MT_file(Menu):
    bl_label = "File"

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_AREA'
        layout.operator(
            "wm.read_homefile", text="New")
        layout.operator("wm.revert_mainfile", text="Reset")
        layout.operator("wm.open_mainfile", text="Open")
        if bpy.app.debug_value == 555:
            layout.operator("wm.open_legacy", text="Open Legacy")
        layout.menu("TOPBAR_MT_file_open_recent", text="Open Recent")

        layout.separator()
        
        layout.operator("wm.append")

        layout.separator()

        layout.operator_context = 'EXEC_AREA' if context.ixam_data.is_saved else 'INVOKE_AREA'
        layout.operator("wm.save_mainfile", text="Save")

        layout.operator_context = 'INVOKE_AREA'
        layout.operator("wm.save_as_mainfile", text="Save As")

        layout.separator()

        layout.separator()

        layout.menu("TOPBAR_MT_file_import")
        layout.menu("TOPBAR_MT_file_export")


class TOPBAR_MT_file_new(Menu):
    bl_label = "New File"

    @staticmethod
    def app_template_paths():
        import os

        template_paths = bpy.utils.app_template_paths()

        # Expand template paths.

        # Use a set to avoid duplicate user/system templates.
        # This is a corner case, but users managed to do it! T76849.
        app_templates = set()
        for path in template_paths:
            for d in os.listdir(path):
                if d.startswith(("__", ".")):
                    continue
                template = os.path.join(path, d)
                if os.path.isdir(template):
                    app_templates.add(d)

        return sorted(app_templates)

    @staticmethod
    def draw_ex(layout, _context, *, use_splash=False, use_more=False):
        layout.operator_context = 'INVOKE_DEFAULT'

        # Limit number of templates in splash screen, spill over into more menu.
        paths = TOPBAR_MT_file_new.app_template_paths()
        splash_limit = 5

        icon = 'FILE_NEW'
        props = layout.operator(
            "wm.read_homefile", text="New Project", icon=icon)

        # if use_splash:
        #     icon = 'FILE_NEW'
        #     show_more = len(paths) > (splash_limit - 1)
        #     if show_more:
        #         paths = paths[:splash_limit - 2]
        # elif use_more:
        #     icon = 'FILE_NEW'
        #     paths = paths[splash_limit - 2:]
        #     show_more = False
        # else:
        #     icon = 'NONE'
        #     show_more = False

        # # Draw application templates.
        # if not use_more:
        #     props = layout.operator(
        #         "wm.read_homefile", text="General", icon=icon)
        #     props.app_template = ""

        # for d in paths:
        #     props = layout.operator(
        #         "wm.read_homefile",
        #         text=bpy.path.display_name(d),
        #         icon=icon,
        #     )
        #     props.app_template = d

        # layout.operator_context = 'EXEC_DEFAULT'

        # if show_more:
        #     layout.menu("TOPBAR_MT_templates_more", text="...")

    def draw(self, context):
        TOPBAR_MT_file_new.draw_ex(self.layout, context)


class TOPBAR_MT_file_recover(Menu):
    bl_label = "Recover"

    def draw(self, _context):
        layout = self.layout

        layout.operator("wm.recover_last_session", text="Last Session")
        layout.operator("wm.recover_auto_save", text="Auto Save...")


class TOPBAR_MT_file_defaults(Menu):
    bl_label = "Defaults"

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences

        layout.operator_context = 'INVOKE_AREA'

        if any(bpy.utils.app_template_paths()):
            app_template = prefs.app_template
        else:
            app_template = None

        if app_template:
            layout.label(
                text=iface_(bpy.path.display_name(app_template, has_ext=False),
                            i18n_contexts.id_workspace), translate=False)

        layout.operator("wm.save_homefile")
        if app_template:
            display_name = bpy.path.display_name(iface_(app_template))
            props = layout.operator("wm.read_factory_settings",
                                    text="Load Factory 3IXAM Settings")
            props.app_template = app_template
            props = layout.operator("wm.read_factory_settings",
                                    text=iface_("Load Factory %s Settings",
                                                i18n_contexts.operator_default) % display_name,
                                    translate=False)
            props.app_template = app_template
            props.use_factory_startup_app_template_only = True
            del display_name
        else:
            layout.operator("wm.read_factory_settings")

        layout.operator("wm.read_factory_userpref", text="Reset Interface")


# Include technical operators here which would otherwise have no way for users to access.
class TOPBAR_MT_ixam_system(Menu):
    bl_label = "System"

    def draw(self, _context):
        layout = self.layout

        layout.operator("wm.memory_statistics")
        layout.operator("wm.debug_menu")
        layout.operator_menu_enum("wm.redraw_timer", "type")

        layout.separator()

        layout.operator("screen.spacedata_cleanup")


class TOPBAR_MT_templates_more(Menu):
    bl_label = "Templates"

    def draw(self, context):
        bpy.types.TOPBAR_MT_file_new.draw_ex(
            self.layout, context, use_more=True)


class TOPBAR_MT_file_import(Menu):
    bl_idname = "TOPBAR_MT_file_import"
    bl_label = "Import"
    bl_owner_use_filter = False

    def draw(self, _context):
        if bpy.app.build_options.collada:
            self.layout.operator("wm.collada_import", text="Collada (.dae)")
        if bpy.app.build_options.alembic:
            self.layout.operator("wm.alembic_import", text="Alembic (.abc)")
        if bpy.app.build_options.io_wavefront_obj:
            self.layout.operator("wm.obj_import", text="Wavefront (.obj)")


class TOPBAR_MT_file_export(Menu):
    bl_idname = "TOPBAR_MT_file_export"
    bl_label = "Export"
    bl_owner_use_filter = False

    def draw(self, _context):
        if bpy.app.build_options.collada:
            self.layout.operator("wm.collada_export", text="Collada (.dae)")
        if bpy.app.build_options.alembic:
            self.layout.operator("wm.alembic_export", text="Alembic (.abc)")
        if bpy.app.build_options.io_wavefront_obj:
            self.layout.operator("wm.obj_export", text="Wavefront (.obj)")

class TOPBAR_MT_file_external_data(Menu):
    bl_label = "External Data"

    def draw(self, _context):
        layout = self.layout

        icon = 'CHECKBOX_HLT' if bpy.data.use_autopack else 'CHECKBOX_DEHLT'
        layout.operator("file.autopack_toggle", icon=icon)

        pack_all = layout.row()
        pack_all.operator("file.pack_all")
        pack_all.active = not bpy.data.use_autopack

        unpack_all = layout.row()
        unpack_all.operator("file.unpack_all")
        unpack_all.active = not bpy.data.use_autopack

        layout.separator()

        layout.operator("file.pack_libraries")
        layout.operator("file.unpack_libraries")

        layout.separator()

        layout.operator("file.make_paths_relative")
        layout.operator("file.make_paths_absolute")

        layout.separator()

        layout.operator("file.report_missing_files")
        layout.operator("file.find_missing_files")


class TOPBAR_MT_file_previews(Menu):
    bl_label = "Data Previews"

    def draw(self, _context):
        layout = self.layout

        layout.operator("wm.previews_ensure")
        layout.operator("wm.previews_batch_generate")

        layout.separator()

        layout.operator("wm.previews_clear")
        layout.operator("wm.previews_batch_clear")


class TOPBAR_MT_render(Menu):
    bl_label = "Rendering"

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render

        layout.operator("render.render", text="Render").use_viewport = True
        layout.operator("screen.render_show", text="Render Settings")
        
        layout.separator()

        layout.operator("object.camera_add", text="Add Camera")
        layout.operator("view3d.add_camera_to_view")
        layout.separator()

        layout.label(text="CrossPlatform Rendering")

        
class TOPBAR_MT_edit(Menu):
    bl_label = "Edit"

    def draw(self, context):
        layout = self.layout

        show_developer = context.preferences.view.show_developer_ui

        layout.operator("ed.undo")
        layout.operator("ed.redo")

        layout.separator()

        layout.menu("TOPBAR_MT_undo_history")

        layout.separator()

        layout.operator("screen.repeat_last")
        layout.operator("screen.repeat_history", text="Repeat History...")

        layout.separator()

        layout.operator("screen.redo_last", text="Adjust Last Operation...")

        layout.separator()

        layout.operator("wm.search_menu", text="Menu Search...", icon='VIEWZOOM')
        if show_developer:
            layout.operator("wm.search_operator", text="Operator Search...", icon='VIEWZOOM')

        layout.separator()

        # Mainly to expose shortcut since this depends on the context.
        props = layout.operator("wm.call_panel", text="Rename Active Item...")
        props.name = "TOPBAR_PT_name"
        props.keep_open = False

        layout.operator("wm.batch_rename", text="Batch Rename...")

        layout.separator()

        # Should move elsewhere (impacts outliner & 3D view).
        tool_settings = context.tool_settings
        layout.prop(tool_settings, "lock_object_mode")

        layout.separator()

        layout.operator("screen.userpref_show",
                        text="Preferences...", icon='PREFERENCES')


class VIEW3D_MT_object_apply(Menu):
    bl_label = "Apply"

    def draw(self, context):
        layout = self.layout
        
        props = layout.operator("object.transform_apply", text="Location")
        props.location, props.rotation, props.scale = True, False, False

        props = layout.operator("object.transform_apply", text="Rotation")
        props.location, props.rotation, props.scale = False, True, False

        props = layout.operator("object.transform_apply", text="Scale")
        props.location, props.rotation, props.scale = False, False, True

        props = layout.operator("object.transform_apply", text="All Transforms")
        props.location, props.rotation, props.scale = True, True, True


class TOPBAR_MT_object(Menu):
    bl_label = "Object"

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        if obj and obj.type == 'ARMATURE':
            layout.popover("VIEW3D_PT_rig_edit", text="Rig Parameters")
            layout.popover("VIEW3D_PT_joint_edit", text="Joint Parameters")
        layout.popover("VIEW3D_PT_parameters", text="Parameters")
        
        layout.separator()

        layout.popover("VIEW3D_PT_shading_settings", text="Shading")

        layout.separator()

        layout.operator("object.align_tools", text="Align")

        layout.separator()

        layout.operator("view3d.group", text="Group")
        layout.operator("view3d.ungroup", text="Ungroup")

        layout.separator()

        layout.operator("OBJECT_OT_disable_select", text="Lock")
        layout.operator("OBJECT_OT_enable_select", text="Unlock all")

        layout.separator()

        layout.operator("OBJECT_OT_hide_view_set", text="Hide")
        layout.operator("OBJECT_OT_hide_view_set", text="Hide (Isolate)").unselected=True
        layout.operator("OBJECT_OT_hide_view_clear", text="Unhide all")

        layout.separator()
        if context.mode == 'POSE':
            layout.menu("TOPBAR_MT_pose_transform")
        else:
            layout.menu("VIEW3D_MT_object_reset")
        layout.menu("VIEW3D_MT_object_apply")


class TOPBAR_MT_pose_transform(Menu):
    bl_label = "Reset"

    def draw(self, _context):
        layout = self.layout

        layout.operator("pose.loc_clear", text="Location")
        layout.operator("pose.rot_clear", text="Rotation")
        layout.operator("pose.scale_clear", text="Scale")
        layout.operator("pose.transforms_clear", text="All Transofrm")


class TOPBAR_MT_materials(Menu):
    bl_label = "Materials"

    def draw(self, context):
        layout = self.layout
        layout.operator("view3d.pro_material", text="Material Editor")
        layout.operator("SCREEN_OT_matlib_show", text="3IXAM Material Library")
        layout.operator("SCREEN_OT_uv_editor_show", text="3IXAM UV Editor")


class TOPBAR_MT_window(Menu):
    bl_label = "Window"

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.window_new_main", text="New Window")
        layout.operator("wm.new_instance")


class TOPBAR_MT_help(Menu):
    bl_label = "Help"

    def draw(self, context):
        layout = self.layout

        layout.operator(
            "wm.url_open", text="3IXAM Help",
        ).url = "https://www.3ixam.com/faq"
        layout.operator(
            "wm.url_open", text="3IXAM Tutorials",
        ).url = "https://tutorials.3ixam.com"
        layout.operator(
            "wm.url_open", text="3IXAM Library", icon='TIME',
        )#.url = "https://www.3ixam.com/"

        layout.separator()

        layout.operator(
            "wm.url_open", text="Shortcut Keyboard", icon='TIME',
        )#.url = "https://www.3ixam.com/"

        layout.separator()

        layout.operator(
            "wm.url_open", text="3IXAM Community",
        ).url = "https://www.3ixam.com/community"
        layout.operator(
            "wm.url_open", text="Support",
        ).url = "mailto:Support@3ixam.com"


class TOPBAR_MT_file_context_menu(Menu):
    bl_label = "File Context Menu"

    def draw(self, _context):
        layout = self.layout

        layout.operator_context = 'INVOKE_AREA'
        layout.menu("TOPBAR_MT_file_new", text="New", text_ctxt=i18n_contexts.id_windowmanager, icon='FILE_NEW')
        layout.operator("wm.open_mainfile", text="Open...", icon='FILE_FOLDER')

        layout.separator()

        layout.operator("wm.link", text="Link...", icon='LINK_IXAM')
        layout.operator("wm.append", text="Append...", icon='APPEND_IXAM')

        layout.separator()

        layout.menu("TOPBAR_MT_file_import", icon='IMPORT')
        layout.menu("TOPBAR_MT_file_export", icon='EXPORT')

        layout.separator()

        layout.operator("screen.userpref_show",
                        text="Preferences...", icon='PREFERENCES')


class TOPBAR_MT_workspace_menu(Menu):
    bl_label = "Workspace"

    def draw(self, _context):
        layout = self.layout

        layout.operator("workspace.duplicate",
                        text="Duplicate", icon='DUPLICATE')
        if len(bpy.data.workspaces) > 1:
            layout.operator("workspace.delete", text="Delete", icon='REMOVE')

        layout.separator()

        layout.operator("workspace.reorder_to_front",
                        text="Reorder to Front", icon='TRIA_LEFT_BAR')
        layout.operator("workspace.reorder_to_back",
                        text="Reorder to Back", icon='TRIA_RIGHT_BAR')

        layout.separator()

        # For key binding discoverability.
        props = layout.operator("screen.workspace_cycle",
                                text="Previous Workspace")
        props.direction = 'PREV'
        props = layout.operator(
            "screen.workspace_cycle", text="Next Workspace")
        props.direction = 'NEXT'


# Grease Pencil Object - Primitive curve
class TOPBAR_PT_gpencil_primitive(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "Primitives"

    def draw(self, context):
        settings = context.tool_settings.gpencil_sculpt

        layout = self.layout
        # Curve
        layout.template_curve_mapping(
            settings, "thickness_primitive_curve", brush=True)


# Only a popover
class TOPBAR_PT_name(Panel):
    bl_space_type = 'VIEW_3D'  # dummy
    bl_region_type = 'HEADER'
    bl_label = "Rename Active Item"
    bl_ui_units_x = 14

    def draw(self, context):
        layout = self.layout

        # Edit first editable button in popup
        def row_with_icon(layout, icon):
            row = layout.row()
            row.activate_init = True
            row.label(icon=icon)
            return row

        mode = context.mode
        space = context.space_data
        space_type = None if (space is None) else space.type
        found = False
        if space_type == 'SEQUENCE_EDITOR':
            layout.label(text="Sequence Strip Name")
            item = context.active_sequence_strip
            if item:
                row = row_with_icon(layout, 'SEQUENCE')
                row.prop(item, "name", text="")
                found = True
        elif space_type in ('NODE_EDITOR', 'MATPRO'):
            layout.label(text="Node Label")
            item = context.active_node
            if item:
                row = row_with_icon(layout, 'NODE')
                row.prop(item, "label", text="")
                found = True
        elif space_type == 'NLA_EDITOR':
            layout.label(text="NLA Strip Name")
            item = next(
                (strip for strip in context.selected_nla_strips if strip.active), None)
            if item:
                row = row_with_icon(layout, 'NLA')
                row.prop(item, "name", text="")
                found = True
        else:
            if mode == 'POSE' or (mode == 'WEIGHT_PAINT' and context.pose_object):
                layout.label(text="Joint Name")
                item = context.active_pose_bone
                if item:
                    row = row_with_icon(layout, 'BONE_DATA')
                    row.prop(item, "name", text="")
                    found = True
            elif mode == 'EDIT_ARMATURE':
                layout.label(text="Joint Name")
                item = context.active_bone
                if item:
                    row = row_with_icon(layout, 'ARMATURE_DATA')
                    row.prop(item, "name", text="")
                    found = True
            else:
                layout.label(text="Object Name")
                item = context.object
                if item:
                    row = row_with_icon(layout, 'OBJECT_DATA')
                    row.prop(item, "name", text="")
                    found = True

        if not found:
            row = row_with_icon(layout, 'ERROR')
            row.label(text="No active item")


class TOPBAR_PT_name_marker(Panel):
    bl_space_type = 'TOPBAR'  # dummy
    bl_region_type = 'HEADER'
    bl_label = "Rename Marker"
    bl_ui_units_x = 14

    @staticmethod
    def is_using_pose_markers(context):
        sd = context.space_data
        return (sd.type == 'DOPESHEET_EDITOR' and sd.mode in {'ACTION', 'SHAPEKEY'} and
                sd.show_pose_markers and sd.action)

    @staticmethod
    def get_selected_marker(context):
        if TOPBAR_PT_name_marker.is_using_pose_markers(context):
            markers = context.space_data.action.pose_markers
        else:
            markers = context.scene.timeline_markers

        for marker in markers:
            if marker.select:
                return marker
        return None

    @staticmethod
    def row_with_icon(layout, icon):
        row = layout.row()
        row.activate_init = True
        row.label(icon=icon)
        return row

    def draw(self, context):
        layout = self.layout

        layout.label(text="Marker Name")

        scene = context.scene
        if scene.tool_settings.lock_markers:
            row = self.row_with_icon(layout, 'ERROR')
            label = "Markers are locked"
            row.label(text=label)
            return

        marker = self.get_selected_marker(context)
        if marker is None:
            row = self.row_with_icon(layout, 'ERROR')
            row.label(text="No active marker")
            return

        icon = 'TIME'
        if marker.camera is not None:
            icon = 'CAMERA_DATA'
        elif self.is_using_pose_markers(context):
            icon = 'ARMATURE_DATA'
        row = self.row_with_icon(layout, icon)
        row.prop(marker, "name", text="")


class TOPBAR_PT_name_marker(Panel):
    bl_space_type = 'TOPBAR'
    bl_region_type = 'HEADER'
    bl_label = "Rename Marker"
    bl_ui_units_x = 14

    @staticmethod
    def is_using_pose_markers(context):
        sd = context.space_data
        return (sd.type == 'DOPESHEET_EDITOR' and sd.mode in {'ACTION', 'SHAPEKEY'} and
                sd.show_pose_markers and sd.action)

    @staticmethod
    def get_selected_marker(context):
        if TOPBAR_PT_name_marker.is_using_pose_markers(context):
            markers = context.space_data.action.pose_markers
        else:
            markers = context.scene.timeline_markers

        for marker in markers:
            if marker.select:
                return marker
        return None

    @staticmethod
    def row_with_icon(layout, icon):
        row = layout.row()
        row.activate_init = True
        row.label(icon=icon)
        return row

    def draw(self, context):
        layout = self.layout

        layout.label(text="Marker Name")

        scene = context.scene
        if scene.tool_settings.lock_markers:
            row = self.row_with_icon(layout, 'ERROR')
            label = "Markers are locked"
            row.label(text=label)
            return

        marker = self.get_selected_marker(context)
        if marker is None:
            row = self.row_with_icon(layout, 'ERROR')
            row.label(text="No active marker")
            return

        icon = 'TIME'
        if marker.camera is not None:
            icon = 'CAMERA_DATA'
        elif self.is_using_pose_markers(context):
            icon = 'ARMATURE_DATA'
        row = self.row_with_icon(layout, icon)
        row.prop(marker, "name", text="")


class RenderBackground(bpy.types.Operator):
    bl_idname = "render.render_background"
    bl_label = "Background Render"
    bl_description = "Render From The Commandline"
    bl_options = {'REGISTER'}

    is_quit: bpy.props.BoolProperty(name="Quit Ixam", default=True)
    items = [
        ('IMAGE', "Image", "", 1),
        ('ANIME', "Animation", "", 2),
    ]
    mode: bpy.props.EnumProperty(items=items, name="Mode", default='IMAGE')
    thread: bpy.props.IntProperty(name="Threads", default=2, min=1, max=16, soft_min=1, soft_max=16)

    def execute(self, context):
        ixam_path = bpy.data.filepath
        if (not ixam_path):
            self.report(type={'ERROR'}, message="Save File First")
            return {'CANCELLED'}
        if (self.mode == 'IMAGE'):
            subprocess.Popen([sys.argv[0], '-b', ixam_path, '-f', str(context.scene.frame_current), '-t', str(self.thread)])
        elif (self.mode == 'ANIME'):
            subprocess.Popen([sys.argv[0], '-b', ixam_path, '-a', '-t', str(self.thread)])
        if (self.is_quit):
            bpy.ops.wm.quit_ixam()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SetRenderResolutionPercentage(bpy.types.Operator):
    bl_idname = "render.set_render_resolution_percentage"
    bl_label = "Set Resolution"
    bl_description = "Percent of the size of the resolution"
    bl_options = {'REGISTER', 'UNDO'}

    size: bpy.props.IntProperty(name="Rendering size (%)", default=100, min=1, max=1000, soft_min=1, soft_max=1000, step=1)

    def execute(self, context):
        context.scene.render.resolution_percentage = self.size
        return {'FINISHED'}


class ToggleThreadsMode(bpy.types.Operator):
    bl_idname = "render.toggle_threads_mode"
    bl_label = "Set Threads"
    bl_description = "I will switch the number of threads in the CPU to be used for rendering"
    bl_options = {'REGISTER', 'UNDO'}

    threads: bpy.props.IntProperty(name="Number of threads", default=1, min=1, max=16, soft_min=1, soft_max=16, step=1)

    def execute(self, context):
        if (context.scene.render.threads_mode == 'AUTO'):
            context.scene.render.threads_mode = 'FIXED'
            context.scene.render.threads = self.threads
        else:
            context.scene.render.threads_mode = 'AUTO'
        return {'FINISHED'}

    def invoke(self, context, event):
        if (context.scene.render.threads_mode == 'AUTO'):
            self.threads = context.scene.render.threads
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)


class SetAllSubsurfRenderLevels(bpy.types.Operator):
    bl_idname = "render.set_all_subsurf_render_levels"
    bl_label = "Set Global Subsurf"
    bl_description = "Level of Subsurf to apply when rendering"
    bl_options = {'REGISTER', 'UNDO'}

    items = [
        ('ABSOLUTE', "Absolute value", "", 1),
        ('RELATIVE', "Relative value", "", 2),
    ]
    mode: bpy.props.EnumProperty(items=items, name="Mode")
    levels: bpy.props.IntProperty(name="Level", default=2, min=-20, max=20, soft_min=-20, soft_max=20, step=1)

    def execute(self, context):
        for obj in bpy.data.objects:
            if (obj.type != 'MESH' and obj.type != 'CURVE'):
                continue
            for mod in obj.modifiers:
                if (mod.type == 'SUBSURF'):
                    if (self.mode == 'ABSOLUTE'):
                        mod.render_levels = self.levels
                    elif (self.mode == 'RELATIVE'):
                        mod.render_levels += self.levels
                    else:
                        self.report(type={'ERROR'}, message="Setting value is invalid")
                        return {'CANCELLED'}
        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}


class SyncAllSubsurfRenderLevels(bpy.types.Operator):
    bl_idname = "render.sync_all_subsurf_render_levels"
    bl_label = "Sync All Subdivision Levels"
    bl_description = "sync_all_subsurf_render_levels"
    bl_options = {'REGISTER', 'UNDO'}

    level_offset: bpy.props.IntProperty(name="Sync Levels", default=0, min=-20, max=20, soft_min=-20, soft_max=20, step=1)

    def execute(self, context):
        for obj in bpy.data.objects:
            if (obj.type != 'MESH'):
                continue
            for mod in obj.modifiers:
                if (mod.type == 'SUBSURF'):
                    mod.render_levels = mod.levels + self.level_offset
        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

################
# Render Size
################


class RenderResolutionPercentageMenu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_render_resolution_percentage"
    bl_label = "Rendering size (%)"
    bl_description = "Setting is set to either rendered in what percent of the size of the resolution"

    def check(self, context):
        return True

    def draw(self, context):
        x = bpy.context.scene.render.resolution_x
        y = bpy.context.scene.render.resolution_y
        self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="10% (" + str(int(x * 0.1)) + "x" + str(int(y * 0.1)) + ")", icon="CAMERA_DATA").size = 10
        self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="20% (" + str(int(x * 0.2)) + "x" + str(int(y * 0.2)) + ")", icon="CAMERA_DATA").size = 20
        self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="30% (" + str(int(x * 0.3)) + "x" + str(int(y * 0.3)) + ")", icon="CAMERA_DATA").size = 30
        self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="40% (" + str(int(x * 0.4)) + "x" + str(int(y * 0.4)) + ")", icon="CAMERA_DATA").size = 40
        self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="50% (" + str(int(x * 0.5)) + "x" + str(int(y * 0.5)) + ")", icon="CAMERA_DATA").size = 50
        self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="60% (" + str(int(x * 0.6)) + "x" + str(int(y * 0.6)) + ")", icon="CAMERA_DATA").size = 60
        self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="70% (" + str(int(x * 0.7)) + "x" + str(int(y * 0.7)) + ")", icon="CAMERA_DATA").size = 70
        self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="80% (" + str(int(x * 0.8)) + "x" + str(int(y * 0.8)) + ")", icon="CAMERA_DATA").size = 80
        self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="90% (" + str(int(x * 0.9)) + "x" + str(int(y * 0.9)) + ")", icon="CAMERA_DATA").size = 90
        self.layout.separator()
        self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="100% (" + str(int(x)) + "x" + str(int(y)) + ")", icon="CAMERA_DATA").size = 100
        self.layout.separator()
        self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="150% (" + str(int(x * 1.5)) + "x" + str(int(y * 1.5)) + ")", icon="CAMERA_DATA").size = 150
        self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="200% (" + str(int(x * 2.0)) + "x" + str(int(y * 2.0)) + ")", icon="CAMERA_DATA").size = 200
        self.layout.operator(SetRenderResolutionPercentage.bl_idname, text="300% (" + str(int(x * 3.0)) + "x" + str(int(y * 3.0)) + ")", icon="CAMERA_DATA").size = 300


class SimplifyRenderMenu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_render_simplify"
    bl_label = "Simplify Render"
    bl_description = "I simplified set of rendering"

    def draw(self, context):
        self.layout.prop(context.scene.render, "use_simplify")
        self.layout.separator()
        self.layout.prop(context.scene.render, "simplify_subdivision")
        self.layout.prop(context.scene.render, "simplify_shadow_samples")
        self.layout.prop(context.scene.render, "simplify_child_particles")
        self.layout.prop(context.scene.render, "simplify_ao_sss")
        self.layout.prop(context.scene.render, "use_simplify_triangulate")


class ShadeingMenu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_render_shadeing"
    bl_label = "Use shading"
    bl_description = "Shading on / off"

    def draw(self, context):
        self.layout.prop(context.scene.render, 'use_textures')
        self.layout.prop(context.scene.render, 'use_shadows')
        self.layout.prop(context.scene.render, 'use_sss')
        self.layout.prop(context.scene.render, 'use_envmaps')
        self.layout.prop(context.scene.render, 'use_raytrace')


class SubsurfMenu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_render_subsurf"
    bl_label = "Subsurf Level All"
    bl_description = "Subsurf subdivision level of all objects"

    def draw(self, context):
        operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="Subdivision + 1", icon="MOD_SUBSURF")
        operator.mode = 'RELATIVE'
        operator.levels = 1
        operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="Subdivision - 1", icon="MOD_SUBSURF")
        operator.mode = 'RELATIVE'
        operator.levels = -1
        self.layout.separator()
        operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="Subdivision = 0", icon="MOD_SUBSURF")
        operator.mode = 'ABSOLUTE'
        operator.levels = 0
        operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="Subdivision = 1", icon="MOD_SUBSURF")
        operator.mode = 'ABSOLUTE'
        operator.levels = 1
        operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="Subdivision = 2", icon="MOD_SUBSURF")
        operator.mode = 'ABSOLUTE'
        operator.levels = 2
        operator = self.layout.operator(SetAllSubsurfRenderLevels.bl_idname, text="Subdivision = 3", icon="MOD_SUBSURF")
        operator.mode = 'ABSOLUTE'
        operator.levels = 3
        self.layout.separator()
        self.layout.operator(SyncAllSubsurfRenderLevels.bl_idname, text="Sync Subsurf Render Levels", icon="MOD_SUBSURF")


class RenderToolsMenu(bpy.types.Operator):
    bl_idname = "render.render_tools"
    bl_label = "Render Settings"
    bl_description = "Pop up Render Settings"
    COMPAT_ENGINES = {'IXAM_RENDER', 'IXAM_EEVEE', 'IXAM_WORKBENCH', 'CYCLES'}
    def draw(self, context):
        # Cycles
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        scene = context.scene
        cscene = scene.cycles        
        rd = scene.render

        self.layout.label(text="Render Settings")
        self.layout.separator()

        self.layout.label(text="Render Engine")
        self.layout.prop(rd, "engine", text="")
        self.layout.separator()

        self.layout.operator("render.render", text="Render Image").use_viewport = True
        self.layout.operator("render.render", text="Render Animation")
        self.layout.separator()
        self.layout.prop(context.scene.render, 'resolution_x', text="Resolution X")
        self.layout.prop(context.scene.render, 'resolution_y', text="Resolution Y")
        self.layout.prop(context.scene.render, "resolution_percentage", text="Render Resolution")
        self.layout.menu(RenderResolutionPercentageMenu.bl_idname, text="Resolution Presets")
        self.layout.prop_menu_enum(context.scene.render.image_settings, 'file_format', text="File Format")
        self.layout.separator()
        self.layout.menu(AnimateRenderMenu.bl_idname, text="Animation")
        self.layout.separator()
        self.layout.prop(context.scene.world.light_settings, 'use_ambient_occlusion', text="Use AO")
        self.layout.prop(context.scene.world.light_settings, "ao_factor", text="AO Factor")
        self.layout.separator()
        self.layout.label(text="Samples:")
        self.layout.prop(cscene, "samples", text="Render")
        self.layout.prop(cscene, "preview_samples", text="Preview")
        self.layout.separator()
        self.layout.prop(context.scene.render, 'use_freestyle', text="Use Freestyle")
        self.layout.separator()
        self.layout.menu(SimplifyRenderMenu.bl_idname)
        self.layout.menu(SubsurfMenu.bl_idname)
        self.layout.separator()
        self.layout.operator(ToggleThreadsMode.bl_idname, text='Set Threads')
        self.layout.operator(RenderBackground.bl_idname)
        
        rd = context.scene.render   
        self.layout.separator()
        self.layout.label(text="Output Path")
        self.layout.prop(rd, "filepath", text="")
        self.layout.prop(scene, "camera", text="Camera")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=250)

class AnimateRenderMenu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_render_animate_menu"
    bl_label = "Animation"
    bl_description = "Set Frames & Animation Length"

    def draw(self, context):
        self.layout.separator()
        self.layout.prop(context.scene, 'frame_start', text="Start Frame")
        self.layout.prop(context.scene, 'frame_end', text="End Frame")
        self.layout.prop(context.scene, 'frame_step', text="Frame Step")
        self.layout.prop(context.scene.render, 'fps', text="FPS")


class IMAGE_PT_RenderSettingsPanel(bpy.types.Panel):
    """Render Settings Panel"""
    bl_label = "Render settings"
    bl_category = 'Render'
    COMPAT_ENGINES = {'IXAM_RENDER', 'IXAM_EEVEE', 'IXAM_WORKBENCH', 'CYCLES'}

    def draw(self, context):
        # Cycles
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        scene = context.scene
        cscene = scene.cycles

        rd = scene.render
        self.layout.prop(rd, "engine", text="Render Engine")

        self.layout.label(text="Render Settings")

        self.layout.label(text="Render Settings")
        self.layout.separator()
        self.layout.operator("render.render", text="Render Image").use_viewport = True
        self.layout.operator("render.render", text="Render Animation",)
        self.layout.separator()
        self.layout.prop(context.scene.render, 'resolution_x', text="Resolution X")
        self.layout.prop(context.scene.render, 'resolution_y', text="Resolution Y")
        self.layout.prop(context.scene.render, "resolution_percentage", text="Render Resolution")
        self.layout.menu(RenderResolutionPercentageMenu.bl_idname, text="Resolution Presets")
        self.layout.prop_menu_enum(context.scene.render.image_settings, 'file_format', text="File Format")
        self.layout.separator()
        self.layout.menu(AnimateRenderMenu.bl_idname, text="Animation")
        self.layout.separator()
        self.layout.prop(context.scene.world.light_settings, 'use_ambient_occlusion', text="Use AO")
        self.layout.prop(context.scene.world.light_settings, "ao_factor", text="AO Factor")
        self.layout.separator()
        self.layout.label(text="Samples:")
        self.layout.prop(cscene, "samples", text="Render")
        self.layout.prop(cscene, "preview_samples", text="Preview")
        self.layout.separator()
        self.layout.prop(context.scene.render, 'use_freestyle', text="Use Freestyle")
        self.layout.separator()
        self.layout.menu(SimplifyRenderMenu.bl_idname)
        self.layout.menu(SubsurfMenu.bl_idname)
        self.layout.separator()
        self.layout.operator(ToggleThreadsMode.bl_idname, text='Set Threads')
        self.layout.operator(RenderBackground.bl_idname)


    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=250)

classes = (
    # TOPBAR_HT_upper_bar,
    TOPBAR_MT_file_context_menu,
    #TOPBAR_MT_workspace_menu,
    TOPBAR_MT_editor_menus,
    TOPBAR_MT_ixam,
    TOPBAR_MT_ixam_system,
    TOPBAR_MT_file,
    TOPBAR_MT_file_new,
    TOPBAR_MT_file_recover,
    TOPBAR_MT_file_defaults,
    TOPBAR_MT_templates_more,
    TOPBAR_MT_file_import,
    TOPBAR_MT_file_export,
    TOPBAR_MT_file_external_data,
    TOPBAR_MT_file_cleanup,
    TOPBAR_MT_file_previews,
    TOPBAR_MT_edit,
    TOPBAR_MT_render,
    TOPBAR_MT_window,
    TOPBAR_MT_materials,
    TOPBAR_MT_pose_transform,
    TOPBAR_MT_object,
    VIEW3D_MT_object_apply,
    TOPBAR_MT_help,
    #TOPBAR_PT_tool_fallback,
    # TOPBAR_PT_tool_settings_extra,
    #TOPBAR_PT_gpencil_layers,
    #TOPBAR_PT_gpencil_primitive,
    TOPBAR_PT_name,

    RenderBackground,
    SetRenderResolutionPercentage,
    ToggleThreadsMode,
    SetAllSubsurfRenderLevels,
    SyncAllSubsurfRenderLevels,
    RenderResolutionPercentageMenu,
    SimplifyRenderMenu,
    ShadeingMenu,
    SubsurfMenu,
    RenderToolsMenu,
    AnimateRenderMenu,
    # IMAGE_PT_RenderSettingsPanel
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
