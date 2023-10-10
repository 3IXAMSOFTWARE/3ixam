# SPDX-License-Identifier: GPL-2.0-or-later


# <pep8 compliant>
import bpy
from bpy.types import (
    Header,
    Menu,
    Panel,
)
from bpy.app.translations import (
    contexts as i18n_contexts,
    pgettext_iface as iface_,
    pgettext_tip as tip_,
)
from bpy.props import FloatVectorProperty, PointerProperty


# -----------------------------------------------------------------------------
# Main Header

class USERPREF_HT_header(Header):
    bl_space_type = 'PREFERENCES'

    @staticmethod
    def draw_buttons(layout, context):
        return
        prefs = context.preferences

        layout.operator_context = 'EXEC_AREA'

        if prefs.use_preferences_save and (not bpy.app.use_userpref_skip_save_on_exit):
            pass
        else:
            # Show '*' to let users know the preferences have been modified.
            layout.operator(
                "wm.save_userpref",
                text=iface_("Save Preferences") + (" *" if prefs.is_dirty else ""),
                translate=False,
            )

    def draw(self, context):
        return
        layout = self.layout
        layout.operator_context = 'EXEC_AREA'

        layout.template_header()

        USERPREF_MT_editor_menus.draw_collapsible(context, layout)

        layout.separator_spacer()

        self.draw_buttons(layout, context)


# -----------------------------------------------------------------------------
# Main Navigation Bar

class USERPREF_PT_navigation_bar(Panel):
    bl_label = "Preferences Navigation"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'NAVIGATION_BAR'
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout

        prefs = context.preferences

        col = layout.vert_row()
        col.shape = 'TRAPEZOID'

        col.scale_x = 1.3
        col.scale_y = 1.1
        col.ui_units_y=30
        col.prop(prefs, "active_section", expand=True)


class USERPREF_MT_editor_menus(Menu):
    bl_idname = "USERPREF_MT_editor_menus"
    bl_label = ""

    def draw(self, _context):
        return
        layout = self.layout
        layout.menu("USERPREF_MT_view")
        layout.menu("USERPREF_MT_save_load", text="Preferences")


class USERPREF_MT_view(Menu):
    bl_label = "View"

    def draw(self, _context):
        return
        layout = self.layout

        layout.menu("INFO_MT_area")


class USERPREF_MT_save_load(Menu):
    bl_label = "Save & Load"

    def draw(self, context):
        return
        layout = self.layout

        prefs = context.preferences

        row = layout.row()
        row.active = not bpy.app.use_userpref_skip_save_on_exit
        row.prop(prefs, "use_preferences_save", text="Auto-Save Preferences", shape='PREFS')

        layout.separator()

        layout.operator_context = 'EXEC_AREA'
        if prefs.use_preferences_save:
            layout.operator("wm.save_userpref", text="Save Preferences")
        sub_revert = layout.column(align=True)
        sub_revert.active = prefs.is_dirty
        sub_revert.operator("wm.read_userpref", text="Revert to Saved Preferences")

        layout.operator_context = 'INVOKE_AREA'
        layout.operator("wm.read_factory_userpref", text="Load Factory Preferences")


class USERPREF_PT_save_preferences(Panel):
    bl_label = "Save Preferences"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'EXECUTE'
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        # Hide when header is visible
        for region in context.area.regions:
            if region.type == 'HEADER' and region.height <= 1:
                return True

        return False

    def draw(self, context):
        return
        layout = self.layout.row()
        layout.operator_context = 'EXEC_AREA'

        layout.menu("USERPREF_MT_save_load", text="", icon='COLLAPSEMENU')

        USERPREF_HT_header.draw_buttons(layout, context)


# -----------------------------------------------------------------------------
# Min-In Helpers

# Panel mix-in.
class CenterAlignMixIn:
    """
    Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a ``draw_centered(context, layout)`` function.
    """
    bl_options = {'HIDE_HEADER'}

    def header(self, layout):
        # col = layout.column()
        row = layout.row(align=True)
        rc = row.column()
        rc.alignment = 'LEFT'
        rc.fixed_size = True
        rc.label()

        rc = row.column()
        rc.fixed_size = True

        rc.label(text=self.bl_label, shape='PREFS')
        return row

    def draw(self, context):
        layout = self.layout
        width = context.region.width
        ui_scale = context.preferences.system.ui_scale

        is_wide = width > (350 * ui_scale)

        # layout.use_property_split = True
        # layout.use_property_decorate = False

        # row = layout.row()
        # col = row.column()
        # col.ui_units_x = 25

        self.header(layout)
        self.draw_centered(context, layout)

        # if is_wide:
        #     row.label() 
        #     row.label() 
        return
        # No horizontal margin if region is rather small.
        is_wide = width > (350 * ui_scale)

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
 
        row = layout.row()
        if is_wide:
            row.label()  # Needed so col below is centered.

        col = row.column()
        col.ui_units_x = 50

        # Implemented by sub-classes.
        self.draw_centered(context, col)

        if is_wide:
            row.label()  # Needed so col above is centered.


# -----------------------------------------------------------------------------
# Interface Panels

class ScenePrefPanel:
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "scene_preferences"


class USERPREF_PT_saveload_ixam(ScenePrefPanel, CenterAlignMixIn, Panel):
    bl_label = "General"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        paths = prefs.filepaths
        view = prefs.view
        
        row = layout.row(align=True)

        col = row.column()
        col.fixed_size = True

        col.prop(view, "use_save_prompt", shape='PREFS', text="")
        col.prop(view, "use_play_intro", shape='PREFS', text="")
        col.prop(paths, "use_file_compression", shape='PREFS', text="")

        col = row.column()
        col.alignment = 'LEFT'
        col.fixed_size = True

        col.label(text="Save Prompt")
        col.label(text="Play Intro Sound")
        col.label(text="Compress File")
        col.label(text="File Preview Type")
        col.label(text="Save Versions")
        col.label(text="Recent Files")

        row.separator(factor=4.0)
        col = row.column()

        col.alignment = 'LEFT'
        col.fixed_size = True

        col.label()
        col.label()
        
        col.prop(paths, "file_preview_type", shape='PREFS', text="")
        col.prop(paths, "save_version", shape='PREFS', text="")
        
        row = col.row()
        row.alignment = 'LEFT'
        row.label(text="Levels:")
        row.prop(paths, "recent_files", shape='PREFS', text="")

        layout.separator(shape= "PREFS")


class USERPREF_PT_saveload_autosave(ScenePrefPanel, CenterAlignMixIn, Panel):
    bl_label = "Auto Backup"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        paths = prefs.filepaths
        view = prefs.view

        row = layout.row(align=True)
        col = row.column()
        col.fixed_size = True

        col.prop(paths, "use_auto_save_temporary_files", text="", shape='PREFS')

        col = row.column()
        col.alignment = 'LEFT'
        col.fixed_size = True

        col.label(text="Enabled")
        col.label(text="Number of files")
        col.label(text="Backup Interval (minutes)")
        col.label(text="Auto Backup File Name")

        row.separator(factor=4.0)
        col = row.column()

        col.alignment = 'LEFT'
        col.fixed_size = True

        col.active = paths.use_auto_save_temporary_files

        col.label()
        col.prop(paths, "autobackup_count", text="", shape='PREFS')
        col.prop(paths, "auto_save_time", text="", shape='PREFS')
        col.prop(paths, "autobackup_directory", text="", shape='PREFS')

        layout.separator(shape= "PREFS")

class USERPREF_PT_scene_units(ScenePrefPanel, CenterAlignMixIn, Panel):
    bl_label = "Unit Setup"

    def draw_centered(self, context, layout):
        unit = context.scene.unit_settings

        row = layout.row(align=True)
        col = row.column()
        col.fixed_size = True
        col.alignment = 'LEFT'

        col.label()
        # col.prop(paths, "use_auto_save_temporary_files", text="", shape='PREFS')

        col = row.column()
        col.alignment = 'LEFT'
        col.fixed_size = True

        col.label(text="Unit System")
        col.label(text="Units")

        row.separator(factor=4.0)
        col = row.column()

        col.prop(unit, "system",  text="", shape='PREFS')
        col.prop(unit, "length_unit", text="", shape='PREFS')

        col.alignment = 'LEFT'
        col.fixed_size = True



class USERPREF_PT_interface_translation(ScenePrefPanel, CenterAlignMixIn, Panel):
    bl_label = "Translation"
    bl_translation_context = i18n_contexts.id_windowmanager

    @classmethod
    def poll(cls, _context):
        return bpy.app.build_options.international

    def draw_centered(self, context, layout):
        prefs = context.preferences
        view = prefs.view

        layout.prop(view, "language", shape='PREFS')

        col = layout.column(heading="Affect")
        col.active = (bpy.app.translations.locale != 'en_US')
        col.prop(view, "use_translate_tooltips", text="Tooltips", shape='PREFS')
        col.prop(view, "use_translate_interface", text="Interface", shape='PREFS')
        col.prop(view, "use_translate_new_dataname", text="New Data", shape='PREFS')


class USERPREF_PT_interface_editors(ScenePrefPanel, CenterAlignMixIn, Panel):
    bl_label = "Editors"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        view = prefs.view
        system = prefs.system

        col = layout.column()
        col.prop(system, "use_region_overlap", shape='PREFS')
        col.prop(view, "show_navigate_ui", shape='PREFS')
        col.prop(view, "color_picker_type", shape='PREFS')
        col.row().prop(view, "header_align", shape='PREFS')
        col.prop(view, "factor_display_type", shape='PREFS')


class USERPREF_PT_interface_temporary_windows(ScenePrefPanel, CenterAlignMixIn, Panel):
    bl_label = "Temporary Editors"
    bl_parent_id = "USERPREF_PT_interface_editors"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_centered(self, context, layout):
        prefs = context.preferences
        view = prefs.view

        col = layout.column()
        col.prop(view, "render_display_type", text="Render In", shape='PREFS')
        col.prop(view, "filebrowser_display_type", text="File Browser", shape='PREFS')


class USERPREF_PT_interface_statusbar(ScenePrefPanel, CenterAlignMixIn, Panel):
    bl_label = "Status Bar"
    bl_parent_id = "USERPREF_PT_interface_editors"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_centered(self, context, layout):
        prefs = context.preferences
        view = prefs.view

        col = layout.column(heading="Show")
        col.prop(view, "show_statusbar_stats", text="Scene Statistics", shape='PREFS')
        col.prop(view, "show_statusbar_memory", text="System Memory", shape='PREFS')
        col.prop(view, "show_statusbar_vram", text="Video Memory", shape='PREFS')
        col.prop(view, "show_statusbar_version", text="3IXAM Version", shape='PREFS')


class USERPREF_PT_interface_menus(ScenePrefPanel, Panel):
    bl_label = "Menus"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        pass


class USERPREF_PT_interface_menus_mouse_over(ScenePrefPanel, CenterAlignMixIn, Panel):
    bl_label = "Open on Mouse Over"
    bl_parent_id = "USERPREF_PT_interface_menus"

    def draw_header(self, context):
        prefs = context.preferences
        view = prefs.view

        self.layout.prop(view, "use_mouse_over_open", text="", shape='PREFS')

    def draw_centered(self, context, layout):
        prefs = context.preferences
        view = prefs.view

        layout.active = view.use_mouse_over_open

        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=False)

        flow.prop(view, "open_toplevel_delay", text="Top Level", shape='PREFS')
        flow.prop(view, "open_sublevel_delay", text="Sub Level", shape='PREFS')


class USERPREF_PT_interface_menus_pie(ScenePrefPanel, CenterAlignMixIn, Panel):
    bl_label = "Pie Menus"
    bl_parent_id = "USERPREF_PT_interface_menus"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        view = prefs.view

        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=False)

        flow.prop(view, "pie_animation_timeout", shape='PREFS')
        flow.prop(view, "pie_tap_timeout", shape='PREFS')
        flow.prop(view, "pie_initial_timeout", shape='PREFS')
        flow.prop(view, "pie_menu_radius", shape='PREFS')
        flow.prop(view, "pie_menu_threshold", shape='PREFS')
        flow.prop(view, "pie_menu_confirm", shape='PREFS')

# -----------------------------------------------------------------------------
# Interface Panels

class InterfacePanel:
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "interface"
    bl_options = {'HIDE_HEADER'}


class USERPREF_PT_interface_screen(InterfacePanel, CenterAlignMixIn, Panel):
    bl_label = "Screen"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        theme = prefs.themes[0]
        ui = theme.user_interface
        view = prefs.view

        row = layout.row(align=True)
        col = row.column()
        col.alignment = 'LEFT'

        col.label()
        col.prop(view, "show_tooltips", text="", shape='PREFS')
        col.label()
        col.label()

        col = row.column()
        col.alignment = 'LEFT'

        col.label(text="Line Thickness")
        col.label(text="Tooltips")
        col.label(text="Hand type")

        row.separator(factor=4.0)
        col = row.column()
        col.alignment = 'LEFT'

        col.prop(view, "ui_line_width", text="", shape='PREFS')
        col.label()
        col.prop(view, "hand_type", text="", shape='PREFS')

        layout.separator(shape= "PREFS")
        # sub = col.column()
        # sub.active = view.show_tooltips
        # sub.prop(view, "show_tooltips_python", shape='PREFS')

class USERPREF_PT_interface_language(InterfacePanel, CenterAlignMixIn, Panel):
    bl_label = "Language"
    
    def draw(self, context):
        layout = self.layout
        prefs = context.preferences
        view = prefs.view

        row = self.header(layout)

        row.separator(factor=4.0)

        col = row.column()
        col.alignment = 'LEFT'
        col.prop(view, "language", shape='PREFS', text="")
    
        row.separator(factor=4.0)

        layout.separator(shape= "PREFS")

def colorset_background_get(self):
    theme = bpy.context.preferences.themes[0]
    ui = theme.user_interface

    back_default = theme.view_3d.space.gradients.high_gradient[:3]
    return back_default

def colorset_buttons_get(self):
    theme = bpy.context.preferences.themes[0]
    ui = theme.user_interface

    buttons_default = ui.wcol_menu.inner[:3]
    return buttons_default

def colorset_selected_get(self):
    theme = bpy.context.preferences.themes[0]
    ui = theme.user_interface

    selected_default = ui.wcol_menu.inner_sel[:3]
    return selected_default

def colorset_text_get(self):
    theme = bpy.context.preferences.themes[0]
    ui = theme.user_interface

    text_default = ui.text_color[:3]
    return text_default

def colorset_background_set(self, value):
    color4d = (value[0], value[1], value[2], 1.0)
    color3d = (value[0], value[1], value[2])

    prefs = bpy.context.preferences
    theme = prefs.themes[0]
    ui = theme.user_interface

    spaces = [theme.graph_editor.space, theme.dopesheet_editor.space, theme.nla_editor.space, 
              theme.image_editor.space, theme.sequence_editor.space, theme.text_editor.space, theme.node_editor.space, 
              theme.properties.space, theme.outliner.space, theme.preferences.space, theme.info.space, theme.file_browser.space, 
              theme.console.space, theme.clip_editor.space, theme.topbar.space, theme.statusbar.space,
              theme.spreadsheet.space, theme.render.space, theme.matpro.space, theme.matlib.space
              ]
    
    for space in spaces:
        space.back = color3d
        space.header = color4d
        space.button = color4d
        space.navigation_bar = color4d
        space.execution_buts = color4d
        space.panelcolors.header = color4d
        space.panelcolors.back = color4d
        space.panelcolors.sub_back = color4d
        
    space_lists = [theme.graph_editor.space_list, theme.dopesheet_editor.space_list, theme.nla_editor.space_list, 
                   theme.sequence_editor.space_list, theme.node_editor.space_list, 
                   theme.clip_editor.space_list,
                   theme.spreadsheet.space_list, theme.matpro.space_list]
    
    for space_list in space_lists:
        space_list.list = color3d

    scrubs = [theme.graph_editor, theme.dopesheet_editor, theme.nla_editor, 
              theme.sequence_editor,
              theme.clip_editor
              ]
    
    for scrub in scrubs:
        scrub.time_scrub_background = color4d

    theme.view_3d.space.gradients.high_gradient = color3d
    theme.view_3d.space.gradients.gradient = color3d

def colorset_buttons_set(self, value):
    color4d = (value[0], value[1], value[2], 1.0)

    prefs = bpy.context.preferences
    theme = prefs.themes[0]
    ui = theme.user_interface

    # ui.wcol_animbar, ui.wcol_state
    widgets = [ui.wcol_box, ui.wcol_list_item, ui.wcol_menu, ui.wcol_menu_back,
             ui.wcol_num, ui.wcol_numslider, ui.wcol_option, ui.wcol_pie_menu,
             ui.wcol_prefs_regular, ui.wcol_progress, ui.wcol_pulldown, ui.wcol_radio,
             ui.wcol_regular, ui.wcol_scroll, ui.wcol_tab, ui.wcol_text,
             ui.wcol_toggle, ui.wcol_tool, ui.wcol_toolbar_item, ui.wcol_toolbar_item_pro, 
             ui.wcol_tooltip, ui.wcol_vert_trapezoid, ui.wcol_view_item]
    
    for widget in widgets:
        widget.inner = color4d


def colorset_selected_set(self, value):
    color4d = (value[0], value[1], value[2], 1.0)

    prefs = bpy.context.preferences
    theme = prefs.themes[0]
    ui = theme.user_interface

    # ui.wcol_animbar, ui.wcol_state
    widgets = [ui.wcol_box, ui.wcol_list_item, ui.wcol_menu, ui.wcol_menu_back,
             ui.wcol_num, ui.wcol_numslider, ui.wcol_option, ui.wcol_pie_menu,
             ui.wcol_prefs_regular, ui.wcol_progress, ui.wcol_pulldown, ui.wcol_radio,
             ui.wcol_regular, ui.wcol_scroll, ui.wcol_tab, ui.wcol_text,
             ui.wcol_toggle, ui.wcol_tool, ui.wcol_toolbar_item, ui.wcol_toolbar_item_pro, 
             ui.wcol_tooltip, ui.wcol_vert_trapezoid, ui.wcol_view_item]
    
    for widget in widgets:
        widget.inner_sel = color4d

def colorset_text_set(self, value):
    color4d = (value[0], value[1], value[2], 1.0)
    color3d = (value[0], value[1], value[2])

    prefs = bpy.context.preferences
    theme = prefs.themes[0]
    ui = theme.user_interface

    ui.text_color = color3d

    spaces = [theme.graph_editor.space, theme.dopesheet_editor.space, theme.nla_editor.space, 
              theme.image_editor.space, theme.sequence_editor.space, theme.text_editor.space, theme.node_editor.space, 
              theme.properties.space, theme.outliner.space, theme.preferences.space, theme.info.space, theme.file_browser.space, 
              theme.console.space, theme.clip_editor.space, theme.topbar.space, theme.statusbar.space,
              theme.spreadsheet.space, theme.render.space, theme.matpro.space, theme.matlib.space
              ]
    
    for space in spaces:
        space.title = color3d

class USERPREF_PG_colorsets(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        theme = bpy.context.preferences.themes[0]
        ui = theme.user_interface

        back_default = theme.view_3d.space.gradients.high_gradient[:3]
        buttons_default = ui.wcol_menu.inner[:3]
        selected_default = ui.wcol_menu.inner_sel[:3]
        text_default = ui.text_color[:3]

        bpy.types.Scene.colorset = PointerProperty(
            type=cls,
            )
        #Add in the properties you want      
        cls.background = FloatVectorProperty(subtype='COLOR', 
                                        default=[back_default[0],back_default[1],back_default[2]],
                                        set=colorset_background_set,
                                        get=colorset_background_get)
        cls.selected = FloatVectorProperty(subtype='COLOR', 
                                        default=[selected_default[0],selected_default[1],selected_default[2]],
                                        set=colorset_selected_set,
                                        get=colorset_selected_get)
        cls.buttons = FloatVectorProperty(subtype='COLOR', 
                                        default=[buttons_default[0],buttons_default[1],buttons_default[2]],
                                        set=colorset_buttons_set,
                                        get=colorset_buttons_get)
        cls.text = FloatVectorProperty(subtype='COLOR', 
                                        default=[text_default[0],text_default[1],text_default[2]],
                                        set=colorset_text_set,
                                        get=colorset_text_get)
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.colorset

class USERPREF_PT_interface_themes(InterfacePanel, CenterAlignMixIn, Panel):
    bl_label = "Themes"
    
    def draw_centered(self, context, layout):
        prefs = context.preferences
        theme = prefs.themes[0]
        ui = theme.user_interface
    
        row = layout.row(align=True)
        row.menu("USERPREF_MT_interface_theme_presets", text=USERPREF_MT_interface_theme_presets.bl_label, shape='PREFS')
        row.operator("wm.interface_theme_preset_add", text="Save Theme", shape='PREFS')
        row.operator("wm.interface_theme_preset_add", text="Remove Theme", shape='PREFS').remove_active = True

        row = layout.row()

        col = row.column()
        col.alignment = 'LEFT'

        col.label(text="Line Color")
        col.label(text="Text Color")
        col.label(text="Background Color")
        col.label(text="Buttons Color")
        col.label(text="Selection Color")
        
        row.separator(factor=4.0)
        col = row.column()
        col.alignment = 'LEFT'

        col.prop(ui, "line_color",  text="", shape='PREFS')
        col.prop(context.scene.colorset, "text",  text="", shape='PREFS')
        col.prop(context.scene.colorset, "background", text="", shape='PREFS')
        col.prop(context.scene.colorset, "buttons", text="", shape='PREFS')
        col.prop(context.scene.colorset, "selected", text="", shape='PREFS')

class USERPREF_PT_interface_text(InterfacePanel, CenterAlignMixIn, Panel):
    bl_label = "Text"
    
    def draw_centered(self, context, layout):
        layout = self.layout
        prefs = context.preferences
        view = prefs.view
        theme = prefs.themes[0]
        ui = theme.user_interface


        row = layout.row(align=True)
        col = row.column()
        col.alignment = 'LEFT'
        col.fixed_size = True
        col.label()

        col = row.column()
        col.alignment = 'LEFT'

        col.label(text="Text Thickness")

        row.separator(factor=4.0)
        col = row.column()
        col.alignment = 'LEFT'

        col.prop(view, "font_weight", text="", shape='PREFS')

        layout.separator(shape= "PREFS")
        
# -----------------------------------------------------------------------------
# Editing Panels

class EditingPanel:
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "editing"


class USERPREF_PT_edit_objects(EditingPanel, Panel):
    bl_label = "Objects"

    def draw(self, context):
        pass


class USERPREF_PT_edit_objects_new(EditingPanel, CenterAlignMixIn, Panel):
    bl_label = "New Objects"
    bl_parent_id = "USERPREF_PT_edit_objects"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        edit = prefs.edit

        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=False)

        flow.prop(edit, "material_link", text="Link Materials To", shape='PREFS')
        flow.prop(edit, "object_align", text="Align To", shape='PREFS')
        flow.prop(edit, "use_enter_edit_mode", text="Enter Edit Mode", shape='PREFS')
        flow.prop(edit, "collection_instance_empty_size", text="Instance Empty Size", shape='PREFS')


class USERPREF_PT_edit_objects_duplicate_data(EditingPanel, CenterAlignMixIn, Panel):
    bl_label = "Duplicate Data"
    bl_parent_id = "USERPREF_PT_edit_objects"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        edit = prefs.edit

        layout.use_property_split = False

        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=True)

        col = flow.column()
        col.prop(edit, "use_duplicate_action", text="Action", shape='PREFS')
        col.prop(edit, "use_duplicate_armature", text="Rig", shape='PREFS')
        col.prop(edit, "use_duplicate_camera", text="Camera", shape='PREFS')
        col.prop(edit, "use_duplicate_curve", text="Curve", shape='PREFS')
        # col.prop(edit, "use_duplicate_fcurve", text="F-Curve", shape='PREFS')  # Not implemented.
        col.prop(edit, "use_duplicate_grease_pencil", text="Grease Pencil", shape='PREFS')
        if hasattr(edit, "use_duplicate_hair"):
            col.prop(edit, "use_duplicate_hair", text="Hair", shape='PREFS')

        col = flow.column()
        col.prop(edit, "use_duplicate_lattice", text="Lattice", shape='PREFS')
        col.prop(edit, "use_duplicate_light", text="Light", shape='PREFS')
        col.prop(edit, "use_duplicate_lightprobe", text="Light Probe", shape='PREFS')
        col.prop(edit, "use_duplicate_material", text="Material", shape='PREFS')
        col.prop(edit, "use_duplicate_mesh", text="Mesh", shape='PREFS')
        col.prop(edit, "use_duplicate_metaball", text="Metaball", shape='PREFS')

        col = flow.column()
        col.prop(edit, "use_duplicate_particle", text="Particle", shape='PREFS')
        if hasattr(edit, "use_duplicate_pointcloud"):
            col.prop(edit, "use_duplicate_pointcloud", text="Point Cloud", shape='PREFS')
        col.prop(edit, "use_duplicate_speaker", text="Speaker", shape='PREFS')
        col.prop(edit, "use_duplicate_surface", text="Surface", shape='PREFS')
        col.prop(edit, "use_duplicate_text", text="Text", shape='PREFS')
        # col.prop(edit, "use_duplicate_texture", text="Texture", shape='PREFS')  # Not implemented.
        col.prop(edit, "use_duplicate_volume", text="Volume", shape='PREFS')


class USERPREF_PT_edit_cursor(EditingPanel, CenterAlignMixIn, Panel):
    bl_label = "3D Cursor"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        edit = prefs.edit

        col = layout.column()
        col.prop(edit, "use_mouse_depth_cursor", shape='PREFS')
        col.prop(edit, "use_cursor_lock_adjust", shape='PREFS')


class USERPREF_PT_edit_gpencil(EditingPanel, CenterAlignMixIn, Panel):
    bl_label = "Grease Pencil"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_centered(self, context, layout):
        prefs = context.preferences
        edit = prefs.edit

        col = layout.column(heading="Distance")
        col.prop(edit, "grease_pencil_manhattan_distance", text="Manhattan", shape='PREFS')
        col.prop(edit, "grease_pencil_euclidean_distance", text="Euclidean", shape='PREFS')


class USERPREF_PT_edit_annotations(EditingPanel, CenterAlignMixIn, Panel):
    bl_label = "Annotations"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        edit = prefs.edit

        col = layout.column()
        col.prop(edit, "grease_pencil_default_color", text="Default Color", shape='PREFS')
        col.prop(edit, "grease_pencil_eraser_radius", text="Eraser Radius", shape='PREFS')


class USERPREF_PT_edit_weight_paint(EditingPanel, CenterAlignMixIn, Panel):
    bl_label = "Weight Paint"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_centered(self, context, layout):
        prefs = context.preferences
        view = prefs.view

        layout.use_property_split = False

        layout.prop(view, "use_weight_color_range", text="Use Custom Colors", shape='PREFS')

        col = layout.column()
        col.active = view.use_weight_color_range
        col.template_color_ramp(view, "weight_color_range", expand=True)


class USERPREF_PT_edit_text_editor(EditingPanel, CenterAlignMixIn, Panel):
    bl_label = "Text Editor"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_centered(self, context, layout):
        prefs = context.preferences
        edit = prefs.edit

        layout.prop(edit, "use_text_edit_auto_close", shape='PREFS')


class USERPREF_PT_edit_misc(EditingPanel, CenterAlignMixIn, Panel):
    bl_label = "Miscellaneous"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_centered(self, context, layout):
        prefs = context.preferences
        edit = prefs.edit

        col = layout.column()
        col.prop(edit, "sculpt_paint_overlay_color", text="Sculpt Overlay Color", shape='PREFS')
        col.prop(edit, "node_margin", text="Node Auto-Offset Margin", shape='PREFS')


# -----------------------------------------------------------------------------
# Animation Panels

class AnimationPanel:
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "animation"


class USERPREF_PT_animation_timeline(AnimationPanel, CenterAlignMixIn, Panel):
    bl_label = "Timeline"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        view = prefs.view
        edit = prefs.edit

        col = layout.column()
        col.prop(edit, "use_negative_frames", shape='PREFS')

        col.prop(view, "view2d_grid_spacing_min", text="Minimum Grid Spacing", shape='PREFS')
        col.prop(view, "timecode_style", shape='PREFS')
        col.prop(view, "view_frame_type", shape='PREFS')
        if view.view_frame_type == 'SECONDS':
            col.prop(view, "view_frame_seconds", shape='PREFS')
        elif view.view_frame_type == 'KEYFRAMES':
            col.prop(view, "view_frame_keyframes", shape='PREFS')


class USERPREF_PT_animation_keyframes(AnimationPanel, CenterAlignMixIn, Panel):
    bl_label = "Keyframes"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        edit = prefs.edit

        col = layout.column()
        col.prop(edit, "use_visual_keying", shape='PREFS')
        col.prop(edit, "use_keyframe_insert_needed", text="Only Insert Needed", shape='PREFS')

        col = layout.column(heading="Auto-Keyframing")
        col.prop(edit, "use_auto_keying_warning", text="Show Warning", shape='PREFS')
        col.prop(edit, "use_keyframe_insert_available", text="Only Insert Available", shape='PREFS')
        col.prop(edit, "use_auto_keying", text="Enable in New Scenes", shape='PREFS')


class USERPREF_PT_animation_fcurves(AnimationPanel, CenterAlignMixIn, Panel):
    bl_label = "F-Curves"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        edit = prefs.edit

        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=False)

        flow.prop(edit, "fcurve_unselected_alpha", text="Unselected Opacity", shape='PREFS')
        flow.prop(edit, "fcurve_new_auto_smoothing", text="Default Smoothing Mode", shape='PREFS')
        flow.prop(edit, "keyframe_new_interpolation_type", text="Default Interpolation", shape='PREFS')
        flow.prop(edit, "keyframe_new_handle_type", text="Default Handles", shape='PREFS')
        flow.prop(edit, "use_insertkey_xyz_to_rgb", text="XYZ to RGB", shape='PREFS')
        flow.prop(edit, "use_anim_channel_group_colors", shape='PREFS')


# -----------------------------------------------------------------------------
# System Panels

class SystemPanel:
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "system"


class USERPREF_PT_system_sound(SystemPanel, CenterAlignMixIn, Panel):
    bl_label = "Sound"
    # bl_options = {'DEFAULT_CLOSED'}

    def draw_centered(self, context, layout):
        prefs = context.preferences
        system = prefs.system

        row = layout.row(align = True)
        col = row.column()
        col.alignment = 'LEFT'
        col.fixed_size = True
        col.separator(factor=3.5)

        col = row.column()
        col.alignment = 'LEFT'

        col.label(text="Audio Device")
        if system.audio_device not in {'NONE', 'None'}:
            col.label(text="Channels")
            col.label(text="Mixing Buffer")
            col.label(text="Sample Rate")
            col.label(text="Sample Format")
            col.label(text="Intro Sound")

        row.separator(factor=4.0)
        col = row.column()

        col.prop(system, "audio_device", expand=False, text="", shape='PREFS')

        if system.audio_device not in {'NONE', 'None'}:
            col.prop(system, "audio_channels", shape='PREFS', text="")
            col.prop(system, "audio_mixing_buffer", shape='PREFS', text="")
            col.prop(system, "audio_sample_rate", shape='PREFS', text="")
            col.prop(system, "audio_sample_format", shape='PREFS', text="")
            col.prop(context.preferences.view, "intro_sound", shape='PREFS', text="")

        layout.separator(shape= "PREFS")


class USERPREF_PT_system_cycles_devices(SystemPanel, CenterAlignMixIn, Panel):
    bl_label = "Render Devices"

    @classmethod
    def poll(cls, _context):
        # No GPU rendering on macOS x86_64 currently.
        import platform
        import sys
        return bpy.app.build_options.cycles and \
               (sys.platform != "darwin" or platform.machine() == "arm64")

    def draw_centered(self, context, layout):
        prefs = context.preferences

        col = layout.column()
        col.use_property_split = False
        col.shape = 'PREFS'

        if bpy.app.build_options.cycles:
            addon = prefs.addons.get("cycles")
            if addon is not None:
                addon.preferences.draw_impl(col, context)
            del addon

        # NOTE: Disabled for until GPU side of OpenSubdiv is brought back.
        # system = prefs.system
        # if hasattr(system, "opensubdiv_compute_type"):
        #     col.label(text="OpenSubdiv compute:")
        #     col.row().prop(system, "opensubdiv_compute_type", text="", shape='PREFS')

        row = layout.row(align=True)

        col = row.column()
        col.alignment = 'LEFT'
        col.fixed_size = True
        col.separator(factor=3.5)

        col = row.column()
        col.alignment = 'LEFT'

        col.label(text="Device")

        row.separator(factor=4.0)
        col = row.column()

        col.alignment = 'LEFT'
        col.fixed_size = True

        cscene = context.scene.cycles
        col.prop(cscene, "device", text="", shape = "PREFS")

# class USERPREF_PT_system_os_settings(SystemPanel, CenterAlignMixIn, Panel):
#     bl_label = "Operating System Settings"

#     @classmethod
#     def poll(cls, _context):
#         # Only for Windows so far
#         import sys
#         return sys.platform[:3] == "win"

#     def draw_centered(self, _context, layout):
#         layout.label(text="Make this installation your default 3IXAM")
#         split = layout.split(factor=0.4)
#         split.alignment = 'RIGHT'
#         split.label(text="")
#         split.operator("preferences.associate_ixam", text="Make Default")

class USERPREF_PT_system_cross_platform(SystemPanel, CenterAlignMixIn, Panel):
    bl_label = "CrossRender"

    def draw_centered(self, context, layout):
        prefs = context.preferences

        row = layout.row(align=True)

        col = row.column()
        col.alignment = 'LEFT'
        col.fixed_size = True
        col.separator(factor=3.5)

        col = row.column()
        col.alignment = 'LEFT'

        row.separator(factor=4.0)
        col = row.column()

        col.alignment = 'LEFT'
        col.fixed_size = True

class USERPREF_PT_system_memory(SystemPanel, CenterAlignMixIn, Panel):
    bl_label = "Memory & Limits"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        # system = prefs.system
        edit = prefs.edit

        row = layout.row(align=True)

        col = row.column()
        col.alignment = 'LEFT'
        col.fixed_size = True
        col.separator(factor=3.5)

        col = row.column()
        col.alignment = 'LEFT'

        col.label(text="Scene Undo")
        col.label(text="Redo Memory Limit")

        row.separator(factor=4.0)
        col = row.column()

        col.alignment = 'LEFT'
        col.fixed_size = True

        col.prop(edit, "undo_steps", shape='PREFS', text="")
        col.prop(edit, "undo_memory_limit", shape='PREFS', text="")

        layout.separator(shape= "PREFS")


# class USERPREF_PT_system_video_sequencer(SystemPanel, CenterAlignMixIn, Panel):
#     bl_label = "Video Sequencer"

#     def draw_centered(self, context, layout):
#         prefs = context.preferences
#         system = prefs.system
#         # edit = prefs.edit

#         layout.prop(system, "memory_cache_limit", shape='PREFS')

#         layout.separator()

#         layout.prop(system, "use_sequencer_disk_cache", shape='PREFS')
#         col = layout.column()
#         col.active = system.use_sequencer_disk_cache
#         col.prop(system, "sequencer_disk_cache_dir", text="Directory", shape='PREFS')
#         col.prop(system, "sequencer_disk_cache_size_limit", text="Cache Limit", shape='PREFS')
#         col.prop(system, "sequencer_disk_cache_compression", text="Compression", shape='PREFS')

#         layout.separator()

#         layout.prop(system, "sequencer_proxy_setup", shape='PREFS')


# -----------------------------------------------------------------------------
# Viewport Panels

class ViewportPanel:
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "viewport"


class USERPREF_PT_viewport_display(ViewportPanel, CenterAlignMixIn, Panel):
    bl_label = "Display"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        view = prefs.view

        col = layout.column(heading="Show")
        col.prop(view, "show_object_info", text="Object Info", shape='PREFS')
        col.prop(view, "show_view_name", text="View Name", shape='PREFS')
        col.prop(view, "show_playback_fps", text="Playback FPS", shape='PREFS')

        layout.separator()

        col = layout.column()
        col.prop(view, "gizmo_size", shape='PREFS')
        col.prop(view, "lookdev_sphere_size", shape='PREFS')

        col.separator()

        col.prop(view, "mini_axis_type", text="3D Viewport Axis", shape='PREFS')

        if view.mini_axis_type == 'MINIMAL':
            col.prop(view, "mini_axis_size", text="Size", shape='PREFS')
            col.prop(view, "mini_axis_brightness", text="Brightness", shape='PREFS')

        if view.mini_axis_type == 'GIZMO':
            col.prop(view, "gizmo_size_navigate_v3d", text="Size", shape='PREFS')


class USERPREF_PT_viewport_quality(ViewportPanel, CenterAlignMixIn, Panel):
    bl_label = "Quality"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        system = prefs.system

        col = layout.column()
        col.prop(system, "viewport_aa", shape='PREFS')

        col = layout.column(heading="Smooth Wires")
        col.prop(system, "use_overlay_smooth_wire", text="Overlay", shape='PREFS')
        col.prop(system, "use_edit_mode_smooth_wire", text="Edit Mode", shape='PREFS')


class USERPREF_PT_viewport_textures(ViewportPanel, CenterAlignMixIn, Panel):
    bl_label = "Textures"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        system = prefs.system

        col = layout.column()
        col.prop(system, "gl_texture_limit", text="Limit Size", shape='PREFS')
        col.prop(system, "anisotropic_filter", shape='PREFS')
        col.prop(system, "gl_clip_alpha", slider=True, shape='PREFS')
        col.prop(system, "image_draw_method", text="Image Display Method", shape='PREFS')


class USERPREF_PT_viewport_selection(ViewportPanel, CenterAlignMixIn, Panel):
    bl_label = "Selection"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_centered(self, context, layout):
        prefs = context.preferences
        system = prefs.system

        layout.prop(system, "use_select_pick_depth", shape='PREFS')


class USERPREF_PT_viewport_subdivision(ViewportPanel, CenterAlignMixIn, Panel):
    bl_label = "Subdivision"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_centered(self, context, layout):
        prefs = context.preferences
        system = prefs.system

        layout.prop(system, "use_gpu_subdivision", shape='PREFS')


# -----------------------------------------------------------------------------
# Theme Panels

class ThemePanel:
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "themes"


class USERPREF_MT_interface_theme_presets(Menu):
    bl_label = "Presets"
    preset_subdir = "interface_theme"
    preset_operator = "script.execute_preset"
    preset_type = 'XML'
    preset_xml_map = (
        ("preferences.themes[0]", "Theme"),
        ("preferences.ui_styles[0]", "ThemeStyle"),
    )

    def path_menu(self, searchpaths, operator, *,
                  props_default=None, prop_filepath="filepath",
                  filter_ext=None, filter_path=None, display_name=None,
                  add_operator=None):
        """
        Populate a menu from a list of paths.

        :arg searchpaths: Paths to scan.
        :type searchpaths: sequence of strings.
        :arg operator: The operator id to use with each file.
        :type operator: string
        :arg prop_filepath: Optional operator filepath property (defaults to "filepath").
        :type prop_filepath: string
        :arg props_default: Properties to assign to each operator.
        :type props_default: dict
        :arg filter_ext: Optional callback that takes the file extensions.

           Returning false excludes the file from the list.

        :type filter_ext: Callable that takes a string and returns a bool.
        :arg display_name: Optional callback that takes the full path, returns the name to display.
        :type display_name: Callable that takes a string and returns a string.
        """

        layout = self.layout

        import os
        import re
        import bpy.utils

        layout = self.layout
        if not searchpaths:
            layout.label(text="* Missing Paths *")

        # collect paths
        files = []
        for searchpath in searchpaths:
            for directory in searchpath:
                files.extend([
                    (f, os.path.join(directory, f))
                    for f in os.listdir(directory)
                    if (not f.startswith("."))
                    if ((filter_ext is None) or
                        (filter_ext(os.path.splitext(f)[1])))
                    if ((filter_path is None) or
                        (filter_path(f)))
                ])

        # Perform a "natural sort", so 20 comes after 3 (for example).
        files.sort(
            key=lambda file_path:
            tuple(int(t) if t.isdigit() else t for t in re.split(r"(\d+)", file_path[0].lower())),
        )

        col = layout.column(align=True)

        opened = set()

        for f, filepath in files:
            with open(filepath, "r") as file:
                read = file.read() + f
                if read in opened:
                    continue
                opened.add(read)

            # Intentionally pass the full path to 'display_name' callback,
            # since the callback may want to use part a directory in the name.
            row = col.row(align=True)
            name = display_name(filepath) if display_name else bpy.path.display_name(f)
            props = row.operator(
                operator,
                text=name,
                translate=False,
            )

            if props_default is not None:
                for attr, value in props_default.items():
                    setattr(props, attr, value)

            setattr(props, prop_filepath, filepath)
            if operator == "script.execute_preset":
                props.menu_idname = self.bl_idname

            if add_operator:
                props = row.operator(add_operator, text="", icon='REMOVE')
                props.name = name
                props.remove_name = True

        if add_operator:
            wm = bpy.data.window_managers[0]

            layout.separator()
            row = layout.row()

            sub = row.row()
            sub.emboss = 'NORMAL'
            sub.prop(wm, "preset_name", text="")

            props = row.operator(add_operator, text="", icon='ADD')
            props.name = wm.preset_name

    def draw(self, _context):
        ext_valid = getattr(self, "preset_extensions", {".py", ".xml"})
        props_default = getattr(self, "preset_operator_defaults", None)
        add_operator = getattr(self, "preset_add_operator", None)
        
        paths = [bpy.utils.user_resource('DATAFILES', path=self.preset_subdir)] + bpy.utils.preset_paths(self.preset_subdir)

        self.path_menu(
            [paths],
            self.preset_operator,
            props_default=props_default,
            filter_ext=lambda ext: ext.lower() in ext_valid,
            add_operator=add_operator,
            display_name=lambda name: bpy.path.display_name(name, title_case=False)
        )

    @staticmethod
    def reset_cb(context):
        bpy.ops.preferences.reset_default_theme()


class USERPREF_PT_theme(ThemePanel, Panel):
    bl_label = "Themes"
    bl_options = {'HIDE_HEADER'}

    def draw(self, _context):
        layout = self.layout

        split = layout.split(factor=0.6)

        row = split.row(align=True)
        row.menu("USERPREF_MT_interface_theme_presets", text=USERPREF_MT_interface_theme_presets.bl_label)
        row.operator("wm.interface_theme_preset_add", text="", icon='ADD')
        row.operator("wm.interface_theme_preset_add", text="", icon='REMOVE').remove_active = True

        row = split.row(align=True)
        row.operator("preferences.theme_install", text="Install...", icon='IMPORT')
        row.operator("preferences.reset_default_theme", text="Reset", icon='LOOP_BACK')


class USERPREF_PT_theme_user_interface(ThemePanel, CenterAlignMixIn, Panel):
    bl_label = "User Interface"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, _context):
        layout = self.layout

        layout.label(icon='WORKSPACE')

    def draw(self, context):
        pass


# Base class for dynamically defined widget color panels.
# This is not registered.
class PreferenceThemeWidgetColorPanel:
    bl_parent_id = "USERPREF_PT_theme_user_interface"

    def draw(self, context):
        theme = context.preferences.themes[0]
        ui = theme.user_interface
        widget_style = getattr(ui, self.wcol)
        layout = self.layout

        layout.use_property_split = True

        flow = layout.grid_flow(row_major=False, columns=2, even_columns=True, even_rows=False, align=False)

        col = flow.column(align=True)
        col.prop(widget_style, "text", shape='PREFS')
        col.prop(widget_style, "text_sel", text="Selected", shape='PREFS')
        col.prop(widget_style, "item", slider=True, shape='PREFS')

        col = flow.column(align=True)
        col.prop(widget_style, "inner", slider=True, shape='PREFS')
        col.prop(widget_style, "inner_sel", text="Selected", slider=True, shape='PREFS')
        col.prop(widget_style, "outline", shape='PREFS')

        col.separator()

        col.prop(widget_style, "roundness", shape='PREFS')


# Base class for dynamically defined widget color panels.
# This is not registered.
class PreferenceThemeWidgetShadePanel:

    def draw(self, context):
        theme = context.preferences.themes[0]
        ui = theme.user_interface
        widget_style = getattr(ui, self.wcol)
        layout = self.layout

        layout.use_property_split = True

        col = layout.column(align=True)
        col.active = widget_style.show_shaded
        col.prop(widget_style, "shadetop", text="Shade Top", shape='PREFS')
        col.prop(widget_style, "shadedown", text="Down", shape='PREFS')

    def draw_header(self, context):
        theme = context.preferences.themes[0]
        ui = theme.user_interface
        widget_style = getattr(ui, self.wcol)

        self.layout.prop(widget_style, "show_shaded", text="", shape='PREFS')


class USERPREF_PT_theme_interface_state(ThemePanel, CenterAlignMixIn, Panel):
    bl_label = "State"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "USERPREF_PT_theme_user_interface"

    def draw_centered(self, context, layout):
        theme = context.preferences.themes[0]
        ui_state = theme.user_interface.wcol_state

        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=False)

        col = flow.column(align=True)
        col.prop(ui_state, "inner_anim", shape='PREFS')
        col.prop(ui_state, "inner_anim_sel", shape='PREFS')

        col = flow.column(align=True)
        col.prop(ui_state, "inner_driven", shape='PREFS')
        col.prop(ui_state, "inner_driven_sel", shape='PREFS')

        col = flow.column(align=True)
        col.prop(ui_state, "inner_key", shape='PREFS')
        col.prop(ui_state, "inner_key_sel", shape='PREFS')

        col = flow.column(align=True)
        col.prop(ui_state, "inner_overridden", shape='PREFS')
        col.prop(ui_state, "inner_overridden_sel", shape='PREFS')

        col = flow.column(align=True)
        col.prop(ui_state, "inner_changed", shape='PREFS')
        col.prop(ui_state, "inner_changed_sel", shape='PREFS')

        col = flow.column(align=True)
        col.prop(ui_state, "blend", shape='PREFS')


class USERPREF_PT_theme_interface_styles(ThemePanel, CenterAlignMixIn, Panel):
    bl_label = "Styles"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "USERPREF_PT_theme_user_interface"

    def draw_centered(self, context, layout):
        theme = context.preferences.themes[0]
        ui = theme.user_interface

        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=False)

        flow.prop(ui, "menu_shadow_fac", shape='PREFS')
        flow.prop(ui, "menu_shadow_width", shape='PREFS')
        flow.prop(ui, "icon_alpha", shape='PREFS')
        flow.prop(ui, "icon_saturation", shape='PREFS')
        flow.prop(ui, "editor_outline", shape='PREFS')
        flow.prop(ui, "widget_text_cursor", shape='PREFS')
        flow.prop(ui, "widget_emboss", shape='PREFS')
        flow.prop(ui, "panel_roundness", shape='PREFS')


class USERPREF_PT_theme_interface_transparent_checker(ThemePanel, CenterAlignMixIn, Panel):
    bl_label = "Transparent Checkerboard"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "USERPREF_PT_theme_user_interface"

    def draw_centered(self, context, layout):
        theme = context.preferences.themes[0]
        ui = theme.user_interface

        flow = layout.grid_flow(
            row_major=False, columns=0, even_columns=True, even_rows=False, align=False)

        flow.prop(ui, "transparent_checker_primary", shape='PREFS')
        flow.prop(ui, "transparent_checker_secondary", shape='PREFS')
        flow.prop(ui, "transparent_checker_size", shape='PREFS')


class USERPREF_PT_theme_interface_gizmos(ThemePanel, CenterAlignMixIn, Panel):
    bl_label = "Axis & Gizmo Colors"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "USERPREF_PT_theme_user_interface"

    def draw_centered(self, context, layout):
        theme = context.preferences.themes[0]
        ui = theme.user_interface

        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=True, align=False)

        col = flow.column(align=True)
        col.prop(ui, "axis_x", text="Axis X", shape='PREFS')
        col.prop(ui, "axis_y", text="Y", shape='PREFS')
        col.prop(ui, "axis_z", text="Z", shape='PREFS')

        col = flow.column()
        col.prop(ui, "gizmo_primary", shape='PREFS')
        col.prop(ui, "gizmo_secondary", shape='PREFS')
        col.prop(ui, "gizmo_view_align", shape='PREFS')

        col = flow.column()
        col.prop(ui, "gizmo_a", shape='PREFS')
        col.prop(ui, "gizmo_b", shape='PREFS')


class USERPREF_PT_theme_interface_icons(ThemePanel, CenterAlignMixIn, Panel):
    bl_label = "Icon Colors"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "USERPREF_PT_theme_user_interface"

    def draw_centered(self, context, layout):
        theme = context.preferences.themes[0]
        ui = theme.user_interface

        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=False)

        flow.prop(ui, "icon_scene", shape='PREFS')
        flow.prop(ui, "icon_collection", shape='PREFS')
        flow.prop(ui, "icon_object", shape='PREFS')
        flow.prop(ui, "icon_object_data", shape='PREFS')
        flow.prop(ui, "icon_modifier", shape='PREFS')
        flow.prop(ui, "icon_shading", shape='PREFS')
        flow.prop(ui, "icon_folder", shape='PREFS')
        flow.prop(ui, "icon_border_intensity", shape='PREFS')


class USERPREF_PT_theme_text_style(ThemePanel, CenterAlignMixIn, Panel):
    bl_label = "Text Style"
    bl_options = {'DEFAULT_CLOSED'}

    @staticmethod
    def _ui_font_style(layout, font_style):
        layout.use_property_split = True
        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=True)

        col = flow.column()
        col.prop(font_style, "points", shape='PREFS')

        col = flow.column(align=True)
        col.prop(font_style, "shadow_offset_x", text="Shadow Offset X", shape='PREFS')
        col.prop(font_style, "shadow_offset_y", text="Y", shape='PREFS')

        col = flow.column()
        col.prop(font_style, "shadow", shape='PREFS')
        col.prop(font_style, "shadow_alpha", shape='PREFS')
        col.prop(font_style, "shadow_value", shape='PREFS')

    def draw_header(self, _context):
        layout = self.layout

        layout.label(icon='FONTPREVIEW')

    def draw_centered(self, context, layout):
        style = context.preferences.ui_styles[0]

        layout.label(text="Panel Title")
        self._ui_font_style(layout, style.panel_title)

        layout.separator()

        layout.label(text="Widget")
        self._ui_font_style(layout, style.widget)

        layout.separator()

        layout.label(text="Widget Label")
        self._ui_font_style(layout, style.widget_label)


class USERPREF_PT_theme_bone_color_sets(ThemePanel, CenterAlignMixIn, Panel):
    bl_label = "Joint Color Sets"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, _context):
        layout = self.layout

        layout.label(icon='COLOR')

    def draw_centered(self, context, layout):
        theme = context.preferences.themes[0]

        layout.use_property_split = True

        for i, ui in enumerate(theme.bone_color_sets, 1):
            layout.label(text=iface_("Color Set %d") % i, translate=False)

            flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=False)

            flow.prop(ui, "normal", shape='PREFS')
            flow.prop(ui, "select", shape='PREFS')
            flow.prop(ui, "active", shape='PREFS')
            flow.prop(ui, "show_colored_constraints", shape='PREFS')


class USERPREF_PT_theme_collection_colors(ThemePanel, CenterAlignMixIn, Panel):
    bl_label = "Collection Colors"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, _context):
        layout = self.layout

        layout.label(icon='OUTLINER_COLLECTION')

    def draw_centered(self, context, layout):
        theme = context.preferences.themes[0]

        layout.use_property_split = True

        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=False)
        for i, ui in enumerate(theme.collection_color, 1):
            flow.prop(ui, "color", text=iface_("Color %d", shape='PREFS') % i, translate=False)


class USERPREF_PT_theme_strip_colors(ThemePanel, CenterAlignMixIn, Panel):
    bl_label = "Strip Colors"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, _context):
        layout = self.layout

        layout.label(icon='SEQ_STRIP_DUPLICATE')

    def draw_centered(self, context, layout):
        theme = context.preferences.themes[0]

        layout.use_property_split = True

        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=False)
        for i, ui in enumerate(theme.strip_color, 1):
            flow.prop(ui, "color", text=iface_("Color %d", shape='PREFS') % i, translate=False)


# Base class for dynamically defined theme-space panels.
# This is not registered.
class PreferenceThemeSpacePanel:

    # not essential, hard-coded UI delimiters for the theme layout
    ui_delimiters = {
        'VIEW_3D': {
            "text_grease_pencil",
            "text_keyframe",
            "speaker",
            "freestyle_face_mark",
            "split_normal",
            "bone_solid",
            "bone_locked_weight",
            "paint_curve_pivot",
        },
        'GRAPH_EDITOR': {
            "handle_vertex_select",
        },
        'IMAGE_EDITOR': {
            "paint_curve_pivot",
        },
        'NODE_EDITOR': {
            "layout_node",
        },
        'CLIP_EDITOR': {
            "handle_vertex_select",
        }
    }

    # TODO theme_area should be deprecated
    @staticmethod
    def _theme_generic(layout, themedata, theme_area):

        layout.use_property_split = True

        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=False)

        props_type = {}

        for prop in themedata.rna_type.properties:
            if prop.identifier == "rna_type":
                continue

            props_type.setdefault((prop.type, prop.subtype), []).append(prop)

        th_delimiters = PreferenceThemeSpacePanel.ui_delimiters.get(theme_area)
        for props_type, props_ls in sorted(props_type.items()):
            if props_type[0] == 'POINTER':
                continue

            if th_delimiters is None:
                # simple, no delimiters
                for prop in props_ls:
                    flow.prop(themedata, prop.identifier, shape='PREFS')
            else:

                for prop in props_ls:
                    flow.prop(themedata, prop.identifier, shape='PREFS')

    def draw_header(self, _context):
        if hasattr(self, "icon") and self.icon != 'NONE':
            layout = self.layout
            layout.label(icon=self.icon)

    def draw(self, context):
        layout = self.layout
        theme = context.preferences.themes[0]

        datapath_list = self.datapath.split(".")
        data = theme
        for datapath_item in datapath_list:
            data = getattr(data, datapath_item)
        PreferenceThemeSpacePanel._theme_generic(layout, data, self.theme_area)


class ThemeGenericClassGenerator:

    @staticmethod
    def generate_panel_classes_for_wcols():
        wcols = [
            ("Regular", "wcol_regular"),
            ("Tool", "wcol_tool"),
            ("Toolbar Item", "wcol_toolbar_item"),
            ("Toolbar Item Pro", "wcol_toolbar_item_pro"),
            ("Radio Buttons", "wcol_radio"),
            ("Text", "wcol_text"),
            ("Option", "wcol_option"),
            ("Toggle", "wcol_toggle"),
            ("Number Field", "wcol_num"),
            ("Value Slider", "wcol_numslider"),
            ("Box", "wcol_box"),
            ("Menu", "wcol_menu"),
            ("Pie Menu", "wcol_pie_menu"),
            ("Preferences Widgets", "wcol_prefs_regular"),
            ("Vertical Trapezoid", "wcol_vert_trapezoid"),
            ("Pulldown", "wcol_pulldown"),
            ("Menu Back", "wcol_menu_back"),
            ("Tooltip", "wcol_tooltip"),
            ("Menu Item", "wcol_menu_item"),
            ("Scroll Bar", "wcol_scroll"),
            ("Progress Bar", "wcol_progress"),
            ("List Item", "wcol_list_item"),
            # Not used yet, so hide this from the UI.
            # ("Data-View Item", "wcol_view_item"),
            ("Tab", "wcol_tab"),
            ("Animbar", "wcol_animbar"),
        ]

        for (name, wcol) in wcols:
            panel_id = "USERPREF_PT_theme_interface_" + wcol
            yield type(panel_id, (PreferenceThemeWidgetColorPanel, ThemePanel, Panel), {
                "bl_label": name,
                "bl_options": {'DEFAULT_CLOSED'},
                "draw": PreferenceThemeWidgetColorPanel.draw,
                "wcol": wcol,
            })

            panel_shade_id = "USERPREF_PT_theme_interface_shade_" + wcol
            yield type(panel_shade_id, (PreferenceThemeWidgetShadePanel, ThemePanel, Panel), {
                "bl_label": "Shaded",
                "bl_options": {'DEFAULT_CLOSED'},
                "bl_parent_id": panel_id,
                "draw": PreferenceThemeWidgetShadePanel.draw,
                "wcol": wcol,
            })

    @staticmethod
    def generate_theme_area_child_panel_classes(parent_id, rna_type, theme_area, datapath):
        def generate_child_panel_classes_recurse(parent_id, rna_type, theme_area, datapath):
            props_type = {}

            for prop in rna_type.properties:
                if prop.identifier == "rna_type":
                    continue

                props_type.setdefault((prop.type, prop.subtype), []).append(prop)

            for props_type, props_ls in sorted(props_type.items()):
                if props_type[0] == 'POINTER':
                    for prop in props_ls:
                        new_datapath = datapath + "." + prop.identifier if datapath else prop.identifier
                        panel_id = parent_id + "_" + prop.identifier
                        yield type(panel_id, (PreferenceThemeSpacePanel, ThemePanel, Panel), {
                            "bl_label": rna_type.properties[prop.identifier].name,
                            "bl_parent_id": parent_id,
                            "bl_options": {'DEFAULT_CLOSED'},
                            "draw": PreferenceThemeSpacePanel.draw,
                            "theme_area": theme_area.identifier,
                            "datapath": new_datapath,
                        })

                        yield from generate_child_panel_classes_recurse(
                            panel_id,
                            prop.fixed_type,
                            theme_area,
                            new_datapath,
                        )

        yield from generate_child_panel_classes_recurse(parent_id, rna_type, theme_area, datapath)

    @staticmethod
    def generate_panel_classes_from_theme_areas():
        from bpy.types import Theme

        for theme_area in Theme.bl_rna.properties['theme_area'].enum_items_static:
            if theme_area.identifier in {'USER_INTERFACE', 'STYLE', 'BONE_COLOR_SETS'}:
                continue

            panel_id = "USERPREF_PT_theme_" + theme_area.identifier.lower()
            # Generate panel-class from theme_area
            yield type(panel_id, (PreferenceThemeSpacePanel, ThemePanel, Panel), {
                "bl_label": theme_area.name,
                "bl_options": {'DEFAULT_CLOSED'},
                "draw_header": PreferenceThemeSpacePanel.draw_header,
                "draw": PreferenceThemeSpacePanel.draw,
                "theme_area": theme_area.identifier,
                "icon": theme_area.icon,
                "datapath": theme_area.identifier.lower(),
            })

            yield from ThemeGenericClassGenerator.generate_theme_area_child_panel_classes(
                panel_id, Theme.bl_rna.properties[theme_area.identifier.lower()].fixed_type,
                theme_area, theme_area.identifier.lower())


# -----------------------------------------------------------------------------
# File Paths Panels

# Panel mix-in.
class FilePathsPanel:
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "file_paths"


class USERPREF_PT_file_paths_data(CenterAlignMixIn, FilePathsPanel, Panel):
    bl_label = "Data"
    bl_options = {'HIDE_HEADER'}

    def draw_centered(self, context, layout):

        paths = context.preferences.filepaths

        row = layout.row(align=True)

        col = row.column()
        col.alignment = 'LEFT'
        col.fixed_size = True
        col.separator(factor=3.5)

        col = row.column()
        col.alignment = 'LEFT'

        col.label(text="Fonts")
        col.label(text="Textures")
        col.label(text="Scripts")
        col.label(text="Sounds")
        col.label(text="Temporary Files")

        row.separator(factor=4.0)
        col = row.column()

        col.prop(paths, "font_directory", text="", shape='PREFS')
        col.prop(paths, "texture_directory", text="", shape='PREFS')
        col.prop(paths, "script_directory", text="", shape='PREFS')
        col.prop(paths, "sound_directory", text="", shape='PREFS')
        col.prop(paths, "temporary_directory", text="", shape='PREFS')

        layout.separator(shape= "PREFS")


class USERPREF_PT_file_paths_render(CenterAlignMixIn, FilePathsPanel, Panel):
    bl_label = "Render"
    bl_options = {'HIDE_HEADER'}

    def draw_centered(self, context, layout):
        # layout = self.layout
        # layout.use_property_split = True
        # layout.use_property_decorate = False

        paths = context.preferences.filepaths

        row = layout.row(align=True)

        col = row.column()
        col.alignment = 'LEFT'
        col.fixed_size = True
        col.separator(factor=3.5)

        col = row.column()
        col.alignment = 'LEFT'

        col.label(text="Render Output")
        col.label(text="Render Cache")

        row.separator(factor=4.0)
        col = row.column()

        col.prop(paths, "render_output_directory", text="", shape='PREFS')
        col.prop(paths, "render_cache_directory", text="", shape='PREFS')

# class USERPREF_PT_file_paths_applications(FilePathsPanel, Panel):
#     bl_label = "Applications"

#     def draw(self, context):
#         layout = self.layout
#         layout.use_property_split = True
#         layout.use_property_decorate = False

#         paths = context.preferences.filepaths

#         col = layout.column()
#         col.prop(paths, "image_editor", text="Image Editor", shape='PREFS')
#         col.prop(paths, "animation_player_preset", text="Animation Player", shape='PREFS')
#         if paths.animation_player_preset == 'CUSTOM':
#             col.prop(paths, "animation_player", text="Player", shape='PREFS')


# class USERPREF_PT_file_paths_development(FilePathsPanel, Panel):
#     bl_label = "Development"

#     @classmethod
#     def poll(cls, context):
#         prefs = context.preferences
#         return prefs.view.show_developer_ui

#     def draw(self, context):
#         layout = self.layout
#         layout.use_property_split = True
#         layout.use_property_decorate = False

#         paths = context.preferences.filepaths
#         layout.prop(paths, "i18n_branches_directory", text="I18n Branches", shape='PREFS')


# class USERPREF_PT_saveload_autorun(FilePathsPanel, Panel):
#     bl_label = "Auto Run Python Scripts"
#     bl_parent_id = "USERPREF_PT_saveload_ixam"

#     def draw_header(self, context):
#         prefs = context.preferences
#         paths = prefs.filepaths

#         self.layout.prop(paths, "use_scripts_auto_execute", text="", shape='PREFS')

#     def draw(self, context):
#         layout = self.layout
#         prefs = context.preferences
#         paths = prefs.filepaths

#         layout.use_property_split = True
#         layout.use_property_decorate = False  # No animation.

#         layout.active = paths.use_scripts_auto_execute

#         box = layout.box()
#         row = box.row()
#         row.label(text="Excluded Paths")
#         row.operator("preferences.autoexec_path_add", text="", icon='ADD', emboss=False)
#         for i, path_cmp in enumerate(prefs.autoexec_paths):
#             row = box.row()
#             row.prop(path_cmp, "path", text="", shape='PREFS')
#             row.prop(path_cmp, "use_glob", text="", icon='FILTER', shape='PREFS')
#             row.operator("preferences.autoexec_path_remove", text="", icon='X', emboss=False).index = i


# class USERPREF_PT_file_paths_asset_libraries(FilePathsPanel, Panel):
#     bl_label = "Asset Libraries"

#     def draw(self, context):
#         layout = self.layout
#         layout.use_property_split = False
#         layout.use_property_decorate = False

#         paths = context.preferences.filepaths

#         box = layout.box()
#         split = box.split(factor=0.35)
#         name_col = split.column()
#         path_col = split.column()

#         row = name_col.row(align=True)  # Padding
#         row.separator()
#         row.label(text="Name")

#         row = path_col.row(align=True)  # Padding
#         row.separator()
#         row.label(text="Path")

#         for i, library in enumerate(paths.asset_libraries):
#             row = name_col.row()
#             row.alert = not library.name
#             row.prop(library, "name", text="", shape='PREFS')

#             row = path_col.row()
#             subrow = row.row()
#             subrow.alert = not library.path
#             subrow.prop(library, "path", text="", shape='PREFS')
#             row.operator("preferences.asset_library_remove", text="", icon='X', emboss=False).index = i

#         row = box.row()
#         row.alignment = 'RIGHT'
#         row.operator("preferences.asset_library_add", text="", icon='ADD', emboss=False)


# -----------------------------------------------------------------------------
# Save/Load Panels

# class SaveLoadPanel:
#     bl_space_type = 'PREFERENCES'
#     bl_region_type = 'WINDOW'
#     bl_context = "save_load"



# class USERPREF_PT_saveload_file_browser(SaveLoadPanel, CenterAlignMixIn, Panel):
#     bl_label = "File Browser"

#     def draw_centered(self, context, layout):
#         prefs = context.preferences
#         paths = prefs.filepaths

#         col = layout.column(heading="Defaults")
#         col.prop(paths, "use_filter_files", shape='PREFS')
#         col.prop(paths, "show_hidden_files_datablocks", shape='PREFS')
#         col.prop(paths, "show_recent_locations", shape='PREFS')
#         col.prop(paths, "show_system_bookmarks", shape='PREFS')


# -----------------------------------------------------------------------------
# Input Panels

class InputPanel:
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "input"


class USERPREF_PT_input_keyboard(InputPanel, CenterAlignMixIn, Panel):
    bl_label = "Keyboard"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        inputs = prefs.inputs

        layout.prop(inputs, "use_emulate_numpad", shape='PREFS')
        layout.prop(inputs, "use_numeric_input_advanced", shape='PREFS')


class USERPREF_PT_input_mouse(InputPanel, CenterAlignMixIn, Panel):
    bl_label = "Mouse"

    def draw_centered(self, context, layout):
        import sys
        prefs = context.preferences
        inputs = prefs.inputs

        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=False)

        flow.prop(inputs, "use_mouse_emulate_3_button", shape='PREFS')
        if sys.platform[:3] != "win":
            rowsub = flow.row()
            rowsub.active = inputs.use_mouse_emulate_3_button
            rowsub.prop(inputs, "mouse_emulate_3_button_modifier", shape='PREFS')
        flow.prop(inputs, "use_mouse_continuous", shape='PREFS')
        flow.prop(inputs, "use_drag_immediately", shape='PREFS')
        flow.prop(inputs, "mouse_double_click_time", text="Double Click Speed", shape='PREFS')
        flow.prop(inputs, "drag_threshold_mouse", shape='PREFS')
        flow.prop(inputs, "drag_threshold_tablet", shape='PREFS')
        flow.prop(inputs, "drag_threshold", shape='PREFS')
        flow.prop(inputs, "move_threshold", shape='PREFS')


class USERPREF_PT_input_touchpad(InputPanel, CenterAlignMixIn, Panel):
    bl_label = "Touchpad"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        import sys
        return sys.platform[:3] == "win" or sys.platform == "darwin"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        inputs = prefs.inputs

        col = layout.column()
        col.prop(inputs, "use_multitouch_gestures")


class USERPREF_PT_input_tablet(InputPanel, CenterAlignMixIn, Panel):
    bl_label = "Tablet"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        inputs = prefs.inputs

        import sys
        if sys.platform[:3] == "win":
            layout.prop(inputs, "tablet_api", shape='PREFS')
            layout.separator()

        col = layout.column()
        col.prop(inputs, "pressure_threshold_max", shape='PREFS')
        col.prop(inputs, "pressure_softness", shape='PREFS')


class USERPREF_PT_input_ndof(InputPanel, CenterAlignMixIn, Panel):
    bl_label = "NDOF"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        prefs = context.preferences
        inputs = prefs.inputs
        return inputs.use_ndof

    def draw_centered(self, context, layout):
        prefs = context.preferences
        inputs = prefs.inputs

        USERPREF_PT_ndof_settings.draw_settings(layout, inputs)


# -----------------------------------------------------------------------------
# Navigation Panels

class NavigationPanel:
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "navigation"


class USERPREF_PT_navigation_orbit(NavigationPanel, CenterAlignMixIn, Panel):
    bl_label = "Orbit & Pan"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        view = prefs.view
        inputs = prefs.inputs

        row = layout.row(align=True)
        col = row.column()
       
        col.alignment = 'LEFT'

        col.label()
        col.label()
        col.prop(inputs, "use_rotate_around_active", text="",shape='PREFS')

        col = row.column()
        col.alignment = 'LEFT'

        col.label(text="Orbit Method")
        col.label(text="Orbit Sensitivity")
        col.label(text="Orbit Around Selection")

        row.separator(factor=4.0)
        col = row.column()
        col.alignment = 'LEFT'

        col.prop(inputs, "view_rotate_method", text="", shape='PREFS')
        if inputs.view_rotate_method == 'TURNTABLE':
            col.prop(inputs, "view_rotate_sensitivity_turntable", text="", shape='PREFS')
        else:
            col.prop(inputs, "view_rotate_sensitivity_trackball", text="", shape='PREFS')
        
        layout.separator(shape= "PREFS")


class USERPREF_PT_navigation_zoom(NavigationPanel, CenterAlignMixIn, Panel):
    bl_label = "Zoom"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        inputs = prefs.inputs

        col = layout.column()

        col.row().prop(inputs, "view_zoom_method", text="Zoom Method", shape='PREFS')
        if inputs.view_zoom_method in {'DOLLY', 'CONTINUE'}:
            col.row().prop(inputs, "view_zoom_axis", shape='PREFS')
            col.prop(inputs, "use_zoom_to_mouse", shape='PREFS')
            col = layout.column(heading="Invert Zoom Direction", align=True)
            col.prop(inputs, "invert_mouse_zoom", text="Mouse", shape='PREFS')
            col.prop(inputs, "invert_zoom_wheel", text="Wheel", shape='PREFS')
        else:
            col.prop(inputs, "use_zoom_to_mouse", shape='PREFS')
            col.prop(inputs, "invert_zoom_wheel", text="Invert Wheel Zoom Direction", shape='PREFS')


class USERPREF_PT_navigation_fly_walk(NavigationPanel, CenterAlignMixIn, Panel):
    bl_label = "Fly & Walk"

    def draw_centered(self, context, layout):
        prefs = context.preferences
        inputs = prefs.inputs
        walk = inputs.walk_navigation

        row = layout.row(align=True)
        col = row.column()
        col.alignment = 'LEFT'
        # col.fixed_size = True
        col.label()
        if inputs.navigation_mode == 'WALK':
            for i in range(0, 6):
                col.label()
            col.prop(walk, "use_gravity", text="", shape='PREFS')
        
        col = row.column()
        col.alignment = 'LEFT'

        col.label(text="View Navigation")
        
        if inputs.navigation_mode == 'WALK':
            col.label()
            col.label(text="Mouse Sensitivity")
            col.label(text="Teleport Duration")
            col.label(text="Walk Speed")
            col.label(text="Speed Factor")
            col.label()
            col.label(text="Gravity")
            col = col.column()
            col.alignment = 'LEFT'
            col.active = walk.use_gravity
            col.label(text="View Height")
            col.label(text="Jump Height")

        row.separator(factor=4.0)
        col = row.column()
        col.alignment = 'LEFT'
        col.fixed_size = True

        col.prop(inputs, "navigation_mode", text="", shape='PREFS')
        if inputs.navigation_mode == 'WALK':
            col.label()
            col.prop(walk, "mouse_speed", text="", shape='PREFS')
            col.prop(walk, "teleport_time", text="", shape='PREFS')
            col.prop(walk, "walk_speed", text="", shape='PREFS')
            col.prop(walk, "walk_speed_factor", text="", shape='PREFS')
            col.label()
            col.label()
            col = col.column()
            col.alignment = 'LEFT'
            col.active = walk.use_gravity
            col.prop(walk, "view_height", text="", shape='PREFS')
            col.prop(walk, "jump_height", text="", shape='PREFS')
        

# Special case, this is only exposed as a popover.
class USERPREF_PT_ndof_settings(Panel):
    bl_label = "3D Mouse Settings"
    bl_space_type = 'TOPBAR'  # dummy.
    bl_region_type = 'HEADER'
    bl_ui_units_x = 12

    @staticmethod
    def draw_settings(layout, props, show_3dview_settings=True):
        col = layout.column()
        col.prop(props, "ndof_sensitivity", text="Pan Sensitivity", shape='PREFS')
        col.prop(props, "ndof_orbit_sensitivity", shape='PREFS')
        col.prop(props, "ndof_deadzone", shape='PREFS')

        layout.separator()

        if show_3dview_settings:
            col = layout.column()
            col.row().prop(props, "ndof_view_navigate_method", expand=True, text="Navigation", shape='PREFS')
            col.row().prop(props, "ndof_view_rotate_method", expand=True, text="Rotation", shape='PREFS')

            layout.separator()

        col = layout.column()
        if show_3dview_settings:
            col.prop(props, "ndof_show_guide", shape='PREFS')
        col.prop(props, "ndof_zoom_invert", shape='PREFS')
        row = col.row(heading="Pan")
        row.prop(props, "ndof_pan_yz_swap_axis", text="Swap Y and Z Axes", shape='PREFS')

        layout.separator()

        row = layout.row(heading=("Invert Axis Pan" if show_3dview_settings else "Invert Pan Axis"))
        for text, attr in (
                ("X", "ndof_panx_invert_axis"),
                ("Y", "ndof_pany_invert_axis"),
                ("Z", "ndof_panz_invert_axis"),
        ):
            row.prop(props, attr, text=text, toggle=True, shape='PREFS')

        if show_3dview_settings:
            row = layout.row(heading="Orbit")
            for text, attr in (
                    ("X", "ndof_rotx_invert_axis"),
                    ("Y", "ndof_roty_invert_axis"),
                    ("Z", "ndof_rotz_invert_axis"),
            ):
                row.prop(props, attr, text=text, toggle=True, shape='PREFS')

            layout.separator()

            col = layout.column(heading="Fly/Walk")
            col.prop(props, "ndof_lock_horizon", shape='PREFS')
            col.prop(props, "ndof_fly_helicopter", shape='PREFS')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        input_prefs = context.preferences.inputs
        is_view3d = context.space_data.type == 'VIEW_3D'
        self.draw_settings(layout, input_prefs, is_view3d)

# -----------------------------------------------------------------------------
# Key-Map Editor Panels


class HotkeysPanel:
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "hotkeys"


class USERPREF_MT_keyconfigs(Menu):
    bl_label = "KeyPresets"
    preset_subdir = "keyconfig"
    preset_operator = "preferences.keyconfig_activate"

    def draw(self, context):
        Menu.draw_preset(self, context)


class USERPREF_PT_keymap(HotkeysPanel, Panel):
    bl_label = "Keymap"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        from rna_keymap_ui import draw_keymaps

        layout = self.layout

        # import time

        # start = time.time()

        # Keymap Settings
        draw_keymaps(context, layout)

        # print("runtime", time.time() - start)


# -----------------------------------------------------------------------------
# Add-On Panels

class AddOnPanel:
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "addons"


class USERPREF_PT_addons(AddOnPanel, Panel):
    bl_label = "Add-ons"
    bl_options = {'HIDE_HEADER'}

    _support_icon_mapping = {
        'OFFICIAL': 'IXAM',
        'COMMUNITY': 'COMMUNITY',
        'TESTING': 'EXPERIMENTAL',
    }

    @staticmethod
    def is_user_addon(mod, user_addon_paths):
        import os

        if not user_addon_paths:
            for path in (
                    bpy.utils.script_path_user(),
                    bpy.utils.script_path_pref(),
            ):
                if path is not None:
                    user_addon_paths.append(os.path.join(path, "addons"))

        for path in user_addon_paths:
            if bpy.path.is_subdir(mod.__file__, path):
                return True
        return False

    @staticmethod
    def draw_error(layout, message):
        lines = message.split("\n")
        box = layout.box()
        sub = box.row()
        sub.label(text=lines[0])
        sub.label(icon='ERROR')
        for l in lines[1:]:
            box.label(text=l)

    def draw(self, context):
        import os
        import addon_utils

        layout = self.layout

        wm = context.window_manager
        prefs = context.preferences
        used_ext = {ext.module for ext in prefs.addons}

        addon_user_dirs = tuple(
            p for p in (
                os.path.join(prefs.filepaths.script_directory, "addons"),
                bpy.utils.user_resource('SCRIPTS', path="addons"),
            )
            if p
        )

        # collect the categories that can be filtered on
        addons = [
            (mod, addon_utils.module_bl_info(mod))
            for mod in addon_utils.modules(refresh=False)
        ]

        split = layout.split(factor=0.6)

        row = split.row()
        row.prop(wm, "addon_support", expand=True, shape='PREFS')

        row = split.row(align=True)
        row.operator("preferences.addon_install", icon='IMPORT', text="Install...")
        row.operator("preferences.addon_refresh", icon='FILE_REFRESH', text="Refresh")

        row = layout.row()
        row.prop(prefs.view, "show_addons_enabled_only", shape='PREFS')
        row.prop(wm, "addon_filter", text="", shape='PREFS')
        row.prop(wm, "addon_search", text="", icon='VIEWZOOM', shape='PREFS')

        col = layout.column()

        # set in addon_utils.modules_refresh()
        if addon_utils.error_duplicates:
            box = col.box()
            row = box.row()
            row.label(text="Multiple add-ons with the same name found!")
            row.label(icon='ERROR')
            box.label(text="Delete one of each pair to resolve:")
            for (addon_name, addon_file, addon_path) in addon_utils.error_duplicates:
                box.separator()
                sub_col = box.column(align=True)
                sub_col.label(text=addon_name + ":")
                sub_col.label(text="    " + addon_file)
                sub_col.label(text="    " + addon_path)

        if addon_utils.error_encoding:
            self.draw_error(
                col,
                "One or more addons do not have UTF-8 encoding\n"
                "(see console for details)",
            )

        show_enabled_only = prefs.view.show_addons_enabled_only
        filter = wm.addon_filter
        search = wm.addon_search.lower()
        support = wm.addon_support

        # initialized on demand
        user_addon_paths = []

        for mod, info in addons:
            module_name = mod.__name__

            is_enabled = module_name in used_ext

            if info["support"] not in support:
                continue

            # check if addon should be visible with current filters
            is_visible = (
                (filter == "All") or
                (filter == info["category"]) or
                (filter == "User" and (mod.__file__.startswith(addon_user_dirs)))
            )
            if show_enabled_only:
                is_visible = is_visible and is_enabled

            if is_visible:
                if search and not (
                        (search in info["name"].lower() or
                         search in iface_(info["name"]).lower()) or
                        (info["author"] and (search in info["author"].lower())) or
                        ((filter == "All") and (search in info["category"].lower() or
                                                search in iface_(info["category"]).lower()))
                ):
                    continue

                # Addon UI Code
                col_box = col.column()
                box = col_box.box()
                colsub = box.column()
                row = colsub.row(align=True)

                row.operator(
                    "preferences.addon_expand",
                    icon='DISCLOSURE_TRI_DOWN' if info["show_expanded"] else 'DISCLOSURE_TRI_RIGHT',
                    emboss=False,
                ).module = module_name

                row.operator(
                    "preferences.addon_disable" if is_enabled else "preferences.addon_enable",
                    icon='CHECKBOX_HLT' if is_enabled else 'CHECKBOX_DEHLT', text="",
                    emboss=False,
                ).module = module_name

                sub = row.row()
                sub.active = is_enabled
                sub.label(text=iface_("%s: %s") % (iface_(info["category"]), iface_(info["name"])))

                if info["warning"]:
                    sub.label(icon='ERROR')

                # icon showing support level.
                sub.label(icon=self._support_icon_mapping.get(info["support"], 'QUESTION'))

                # Expanded UI (only if additional info is available)
                if info["show_expanded"]:
                    if info["description"]:
                        split = colsub.row().split(factor=0.15)
                        split.label(text="Description:")
                        split.label(text=tip_(info["description"]))
                    if info["location"]:
                        split = colsub.row().split(factor=0.15)
                        split.label(text="Location:")
                        split.label(text=tip_(info["location"]))
                    if mod:
                        split = colsub.row().split(factor=0.15)
                        split.label(text="File:")
                        split.label(text=mod.__file__, translate=False)
                    if info["author"]:
                        split = colsub.row().split(factor=0.15)
                        split.label(text="Author:")
                        split.label(text=info["author"], translate=False)
                    if info["version"]:
                        split = colsub.row().split(factor=0.15)
                        split.label(text="Version:")
                        split.label(text=".".join(str(x) for x in info["version"]), translate=False)
                    if info["warning"]:
                        split = colsub.row().split(factor=0.15)
                        split.label(text="Warning:")
                        split.label(text="  " + info["warning"], icon='ERROR')

                    user_addon = USERPREF_PT_addons.is_user_addon(mod, user_addon_paths)
                    tot_row = bool(info["doc_url"]) + bool(user_addon)

                    if tot_row:
                        split = colsub.row().split(factor=0.15)
                        split.label(text="Internet:")
                        sub = split.row()
                        if info["doc_url"]:
                            sub.operator(
                                "wm.url_open", text="Documentation", icon='HELP',
                            ).url = info["doc_url"]
                        # Only add "Report a Bug" button if tracker_url is set
                        # or the add-on is bundled (use official tracker then).
                        if info.get("tracker_url"):
                            sub.operator(
                                "wm.url_open", text="Report a Bug", icon='URL',
                            ).url = info["tracker_url"]
                        elif not user_addon:
                            addon_info = (
                                "Name: %s %s\n"
                                "Author: %s\n"
                            ) % (info["name"], str(info["version"]), info["author"])
                            props = sub.operator(
                                "wm.url_open_preset", text="Report a Bug", icon='URL',
                            )
                            props.type = 'BUG_ADDON'
                            props.id = addon_info
                        if user_addon:
                            sub.operator(
                                "preferences.addon_remove", text="Remove", icon='CANCEL',
                            ).module = mod.__name__

                    # Show addon user preferences
                    if is_enabled:
                        addon_preferences = prefs.addons[module_name].preferences
                        if addon_preferences is not None:
                            draw = getattr(addon_preferences, "draw", None)
                            if draw is not None:
                                addon_preferences_class = type(addon_preferences)
                                box_prefs = col_box.box()
                                box_prefs.label(text="Preferences:")
                                addon_preferences_class.layout = box_prefs
                                try:
                                    draw(context)
                                except:
                                    import traceback
                                    traceback.print_exc()
                                    box_prefs.label(text="Error (see console)", icon='ERROR')
                                del addon_preferences_class.layout

        # Append missing scripts
        # First collect scripts that are used but have no script file.
        module_names = {mod.__name__ for mod, info in addons}
        missing_modules = {ext for ext in used_ext if ext not in module_names}

        if missing_modules and filter in {"All", "Enabled"}:
            col.column().separator()
            col.column().label(text="Missing script files")

            module_names = {mod.__name__ for mod, info in addons}
            for module_name in sorted(missing_modules):
                is_enabled = module_name in used_ext
                # Addon UI Code
                box = col.column().box()
                colsub = box.column()
                row = colsub.row(align=True)

                row.label(text="", icon='ERROR')

                if is_enabled:
                    row.operator(
                        "preferences.addon_disable", icon='CHECKBOX_HLT', text="", emboss=False,
                    ).module = module_name

                row.label(text=module_name, translate=False)


# -----------------------------------------------------------------------------
# Studio Light Panels

class StudioLightPanel:
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "lights"


class StudioLightPanelMixin:

    def _get_lights(self, prefs):
        return [light for light in prefs.studio_lights if light.is_user_defined and light.type == self.sl_type]

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences
        lights = self._get_lights(prefs)

        self.draw_light_list(layout, lights)

    def draw_light_list(self, layout, lights):
        if lights:
            flow = layout.grid_flow(row_major=False, columns=4, even_columns=True, even_rows=True, align=False)
            for studio_light in lights:
                self.draw_studio_light(flow, studio_light)
        else:
            layout.label(text=self.get_error_message())

    def get_error_message(self):
        return tip_("No custom %s configured") % self.bl_label

    def draw_studio_light(self, layout, studio_light):
        box = layout.box()
        row = box.row()

        row.template_icon(layout.icon(studio_light), scale=3.0)
        col = row.column()
        op = col.operator("preferences.studiolight_uninstall", text="", icon='REMOVE')
        op.index = studio_light.index

        if studio_light.type == 'STUDIO':
            op = col.operator("preferences.studiolight_copy_settings", text="", icon='IMPORT')
            op.index = studio_light.index

        box.label(text=studio_light.name)


class USERPREF_PT_studiolight_matcaps(StudioLightPanel, StudioLightPanelMixin, Panel):
    bl_label = "MatCaps"
    sl_type = 'MATCAP'

    def draw_header_preset(self, _context):
        layout = self.layout
        layout.operator("preferences.studiolight_install", icon='IMPORT', text="Install...").type = 'MATCAP'
        layout.separator()

    def get_error_message(self):
        return tip_("No custom MatCaps configured")


class USERPREF_PT_studiolight_world(StudioLightPanel, StudioLightPanelMixin, Panel):
    bl_label = "HDRIs"
    sl_type = 'WORLD'

    def draw_header_preset(self, _context):
        layout = self.layout
        layout.operator("preferences.studiolight_install", icon='IMPORT', text="Install...").type = 'WORLD'
        layout.separator()

    def get_error_message(self):
        return tip_("No custom HDRIs configured")


class USERPREF_PT_studiolight_lights(StudioLightPanel, StudioLightPanelMixin, Panel):
    bl_label = "Studio Lights"
    sl_type = 'STUDIO'

    def draw_header_preset(self, _context):
        layout = self.layout
        op = layout.operator("preferences.studiolight_install", icon='IMPORT', text="Install...")
        op.type = 'STUDIO'
        op.filter_glob = ".sl"
        layout.separator()

    def get_error_message(self):
        return tip_("No custom Studio Lights configured")


class USERPREF_PT_studiolight_light_editor(StudioLightPanel, Panel):
    bl_label = "Editor"
    bl_parent_id = "USERPREF_PT_studiolight_lights"
    bl_options = {'DEFAULT_CLOSED'}

    @staticmethod
    def opengl_light_buttons(layout, light):

        col = layout.column()
        col.active = light.use

        col.prop(light, "use", text="Use Light", shape='PREFS')
        col.prop(light, "diffuse_color", text="Diffuse", shape='PREFS')
        col.prop(light, "specular_color", text="Specular", shape='PREFS')
        col.prop(light, "smooth", shape='PREFS')
        col.prop(light, "direction", shape='PREFS')

    def draw(self, context):
        layout = self.layout

        prefs = context.preferences
        system = prefs.system

        row = layout.row()
        row.prop(system, "use_studio_light_edit", toggle=True, shape='PREFS')
        row.operator("preferences.studiolight_new", text="Save as Studio light", icon='FILE_TICK')

        layout.separator()

        layout.use_property_split = True
        column = layout.split()
        column.active = system.use_studio_light_edit

        light = system.solid_lights[0]
        colsplit = column.split(factor=0.85)
        self.opengl_light_buttons(colsplit, light)

        light = system.solid_lights[1]
        colsplit = column.split(factor=0.85)
        self.opengl_light_buttons(colsplit, light)

        light = system.solid_lights[2]
        colsplit = column.split(factor=0.85)
        self.opengl_light_buttons(colsplit, light)

        light = system.solid_lights[3]
        self.opengl_light_buttons(column, light)

        layout.separator()

        layout.prop(system, "light_ambient", shape='PREFS')


# -----------------------------------------------------------------------------
# Experimental Panels

class ExperimentalPanel:
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "experimental"

    url_prefix = "https://developer.blender.com/"

    @classmethod
    def poll(cls, _context):
        return bpy.app.version_cycle == 'alpha'

    def _draw_items(self, context, items):
        prefs = context.preferences
        experimental = prefs.experimental

        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        for prop_keywords, reference in items:
            split = layout.split(factor=0.66)
            col = split.split()
            col.prop(experimental, **prop_keywords, shape='PREFS')

            if reference:
                if type(reference) is tuple:
                    url_ext = reference[0]
                    text = reference[1]
                else:
                    url_ext = reference
                    text = reference

                col = split.split()
                col.operator("wm.url_open", text=text, icon='URL').url = self.url_prefix + url_ext


"""
# Example panel, leave it here so we always have a template to follow even
# after the features are gone from the experimental panel.

class USERPREF_PT_experimental_virtual_reality(ExperimentalPanel, Panel):
    bl_label = "Virtual Reality"

    def draw(self, context):
        self._draw_items(
            context, (
                ({"property": "use_virtual_reality_scene_inspection"}, "T71347"),
                ({"property": "use_virtual_reality_immersive_drawing"}, "T71348"),
            )
        )
"""


class USERPREF_PT_experimental_new_features(ExperimentalPanel, Panel):
    bl_label = "New Features"

    def draw(self, context):
        self._draw_items(
            context, (
                ({"property": "use_sculpt_tools_tilt"}, "T82877"),
                ({"property": "use_extended_asset_browser"}, ("project/view/130/", "Project Page")),
                ({"property": "use_override_templates"}, ("T73318", "Milestone 4")),
                ({"property": "use_realtime_compositor"}, "T99210"),
            ),
        )


class USERPREF_PT_experimental_prototypes(ExperimentalPanel, Panel):
    bl_label = "Prototypes"

    def draw(self, context):
        self._draw_items(
            context, (
                ({"property": "use_new_curves_tools"}, "T68981"),
                ({"property": "use_new_point_cloud_type"}, "T75717"),
                ({"property": "use_sculpt_texture_paint"}, "T96225"),
                ({"property": "use_full_frame_compositor"}, "T88150"),
                ({"property": "enable_eevee_next"}, "T93220"),
                ({"property": "use_draw_manager_acquire_lock"}, "T98016"),
            ),
        )


# Keep this as tweaks can be useful to restore.
"""
class USERPREF_PT_experimental_tweaks(ExperimentalPanel, Panel):
    bl_label = "Tweaks"

    def draw(self, context):
        self._draw_items(
            context, (
                ({"property": "use_select_nearest_on_first_click"}, "T96752"),
            ),
        )

"""


class USERPREF_PT_experimental_debugging(ExperimentalPanel, Panel):
    bl_label = "Debugging"

    @classmethod
    def poll(cls, _context):
        # Unlike the other experimental panels, the debugging one is always visible
        # even in beta or release.
        return True

    def draw(self, context):
        self._draw_items(
            context, (
                ({"property": "use_undo_legacy"}, "T60695"),
                ({"property": "override_auto_resync"}, "T83811"),
                ({"property": "use_cycles_debug"}, None),
                ({"property": "show_asset_debug_info"}, None),
                ({"property": "use_asset_indexing"}, None),
                ({"property": "use_viewport_debug"}, None),
            ),
        )


# -----------------------------------------------------------------------------
# Class Registration

# Order of registration defines order in UI,
# so dynamically generated classes are 'injected' in the intended order.
classes = (
    USERPREF_PT_theme_user_interface,
    *ThemeGenericClassGenerator.generate_panel_classes_for_wcols(),
    # USERPREF_HT_header,
    USERPREF_PT_navigation_bar,
    # USERPREF_PT_save_preferences,
    # USERPREF_MT_editor_menus,
    # USERPREF_MT_view,
    # USERPREF_MT_save_load,

    USERPREF_PT_saveload_ixam,
    USERPREF_PT_saveload_autosave,
    USERPREF_PT_scene_units,

    USERPREF_PT_interface_screen,
    USERPREF_PT_interface_language,
    USERPREF_PT_interface_text,
    USERPREF_PT_interface_themes,
    # USERPREF_PT_interface_editors,
    # USERPREF_PT_interface_temporary_windows,
    # USERPREF_PT_interface_statusbar,
    # USERPREF_PT_interface_translation,
    # USERPREF_PT_interface_text,
    # USERPREF_PT_interface_menus,
    # USERPREF_PT_interface_menus_mouse_over,
    # USERPREF_PT_interface_menus_pie,

    # USERPREF_PT_viewport_display,
    # USERPREF_PT_viewport_quality,
    # USERPREF_PT_viewport_textures,
    # USERPREF_PT_viewport_selection,
    # USERPREF_PT_viewport_subdivision,

    # USERPREF_PT_edit_objects,
    # USERPREF_PT_edit_objects_new,
    # USERPREF_PT_edit_objects_duplicate_data,
    # USERPREF_PT_edit_cursor,
    # USERPREF_PT_edit_annotations,
    # USERPREF_PT_edit_weight_paint,
    # USERPREF_PT_edit_gpencil,
    # USERPREF_PT_edit_text_editor,
    # USERPREF_PT_edit_misc,

    # USERPREF_PT_animation_timeline,
    # USERPREF_PT_animation_keyframes,
    # USERPREF_PT_animation_fcurves,

    USERPREF_PT_system_cycles_devices,
    # USERPREF_PT_system_os_settings,
    USERPREF_PT_system_memory,
    # USERPREF_PT_system_video_sequencer,
    USERPREF_PT_system_sound,
    USERPREF_PT_system_cross_platform,

    USERPREF_MT_interface_theme_presets,

    # USERPREF_PT_theme,
    # USERPREF_PT_theme_interface_state,
    # USERPREF_PT_theme_interface_styles,
    # USERPREF_PT_theme_interface_gizmos,
    # USERPREF_PT_theme_interface_transparent_checker,
    # USERPREF_PT_theme_interface_icons,
    # USERPREF_PT_theme_text_style,
    # USERPREF_PT_theme_bone_color_sets,
    # USERPREF_PT_theme_collection_colors,
    # USERPREF_PT_theme_strip_colors,

    USERPREF_PT_file_paths_data,
    USERPREF_PT_file_paths_render,
    # USERPREF_PT_file_paths_applications,
    # USERPREF_PT_file_paths_development,
    # USERPREF_PT_file_paths_asset_libraries,

    # USERPREF_PT_saveload_ixam_autosave,
    # USERPREF_PT_saveload_autorun,
    # USERPREF_PT_saveload_file_browser,

    USERPREF_MT_keyconfigs,

    USERPREF_PT_input_keyboard,
    USERPREF_PT_input_mouse,
    USERPREF_PT_input_tablet,
    USERPREF_PT_input_touchpad,
    USERPREF_PT_input_ndof,
    USERPREF_PT_navigation_orbit,
    # USERPREF_PT_navigation_zoom,
    USERPREF_PT_navigation_fly_walk,
    # USERPREF_PT_navigation_fly_walk_navigation,
    # USERPREF_PT_navigation_fly_walk_gravity,

    USERPREF_PT_keymap,
    USERPREF_PG_colorsets,
    # USERPREF_PT_addons,

    # USERPREF_PT_studiolight_lights,
    # USERPREF_PT_studiolight_light_editor,
    # USERPREF_PT_studiolight_matcaps,
    # USERPREF_PT_studiolight_world,

    # Popovers.
    # USERPREF_PT_ndof_settings,

    # USERPREF_PT_experimental_new_features,
    # USERPREF_PT_experimental_prototypes,
    # USERPREF_PT_experimental_debugging,

    # Add dynamically generated editor theme panels last,
    # so they show up last in the theme section.
    *ThemeGenericClassGenerator.generate_panel_classes_from_theme_areas(),
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
