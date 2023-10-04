
bl_info = {
    "name":        "USDZ Export",
    "author":      "Robert Crosby",
    "version":     (0, 0, 6),
    "ixam":        (2, 80, 0),
    "location":    "File > Import-Export",
    "description": "Import/Export USDZ Files",
    "support":     'OFFICIAL',
    "category":    "Import-Export"
    }

if "bpy" in locals():
    import importlib
    if "import_usdz" in locals():
        importlib.reload(import_usdz)
    if "export_usdz" in locals():
        importlib.reload(export_usdz)

import typing
import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
    EnumProperty,
)
from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    path_reference_mode,
    axis_conversion,
)
from bpy.types import (
    Context,
    Event,
    Operator,
    OperatorFileListElement,
)

class WM_OT_error_popup(Operator):
    bl_idname = "wm.error_popup"
    bl_label = "Error"
    
    message: StringProperty(
        name="Error message",
        description="",
        default="",
    )
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        for msg in self.message.split('\n'):
            col.label(text=msg)
    
    def execute(self, context: Context):
        return {'FINISHED'}
    
    def invoke(self, context: Context, event: Event):
        area = context.area
        context.window.cursor_warp(area.width // 2, area.height // 2)
        context.window_manager.invoke_props_dialog(self, width=400)
        context.window.cursor_warp(event.mouse_x, event.mouse_y)
        return {'RUNNING_MODAL'}

class WM_OT_usdz_import(bpy.types.Operator, ImportHelper):
    """Import a USDZ File"""

    bl_idname = "wm.import_usdz"
    bl_label = "Import USDZ File"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ""
    filter_glob: StringProperty(
        default="*.usdz;*.usda;*.usdc",
        options={'HIDDEN'},
    )

    scale: FloatProperty(
        name="Scale",
        description="Value by which to enlarge or shrink the objects with respect to the world's origin",
        default=1.0,
        min=0.0001, max=1000.0, soft_min=0.0001, soft_max=1000.0
    )
    
    use_frame_range: BoolProperty(
        name="Set Frame Range",
        description="Update the scene's start and end frame to match those of the USD archive",
        default=True,
    )
    
    use_relative_path: BoolProperty(
        name="Relative Path",
        description="Select the file relative to the ixam file",
        default=True,
    )
    
    use_cameras: BoolProperty(
        name="Cameras",
        description="",
        default=True,
    )
    
    use_curves: BoolProperty(
        name="Curves",
        description="",
        default=True,
    )
    
    use_lights: BoolProperty(
        name="Lights",
        description="",
        default=True,
    )
    
    use_materials: BoolProperty(
        name="Materials",
        description="",
        default=True,
    )
    
    use_meshes: BoolProperty(
        name="Meshes",
        description="",
        default=True,
    )

    use_volumes: BoolProperty(
        name="Volumes",
        description="",
        default=True,
    )
    
    use_subdiv: BoolProperty(
        name="Import Subdivision Scheme",
        description="Create subdivision surface modifiers based on the USD SubdivisionScheme attribute",
        default=False,
    )
    
    use_instance_proxies: BoolProperty(
        name="Import Instance Proxies",
        description="Create unique Ixam objects for USD instances",
        default=True,
    )
    
    use_visible: BoolProperty(
        name="Visible Primitives Only",
        description="Do not import invisible USD primitives. Only applies to primitives with a non-animated visibility attribute. \
        Primitives with animated visibility will always be imported",
        default=True,
    )
    
    create_collection: BoolProperty(
        name="Create Collection",
        description="Add all imported objects to a new collection",
        default=False,
    )
    
    use_uv_coordinates: BoolProperty(
        name="UV Coordinates",
        description="Read mesh UV coordinates",
        default=True,
    )
    
    use_mesh_colors: BoolProperty(
        name="Vertex Colors",
        description="Read mesh vertex colors",
        default=False,
    )
    
    path_mask: StringProperty(
        name="Path Mask",
        default="",
        description="Import only the subset of the USD scene rooted at the given primitive")
    
    use_guide: BoolProperty(
        name="Guide",
        description="Import guide geometry",
        default=False,
    )
    
    use_proxy: BoolProperty(
        name="Proxy",
        description="Import proxy geometry",
        default=True,
    )
    
    use_render: BoolProperty(
        name="Render",
        description="Import final render geometry",
        default=True,
    )

    use_render_preview: BoolProperty(
        name="Import USD Preview",
        description="Convert UsdPreviewSurface shaders to Principled BSDF shader networks",
        default=False,
    )
    
    use_material_blend: BoolProperty(
        name="Set Material Blend",
        description="If the Import USD Preview option is enabled, the material blend method will automatically be set based on the shader's opacity and opacityThreshold inputs",
        default=True,
    )
    
    light_intensity_scale: FloatProperty(
        name="Light Intensity Scale",
        description="Scale for the intensity of imported lights",
        default=1.0,
        min=0.0001, max=10000.0, soft_min=0.0001, soft_max=10000.0
    )

    def execute(self, context):
        from . import import_usdz
        keywords = self.as_keywords(ignore=("filter_glob",))
        return import_usdz.import_usdz(context, **keywords)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        sfile = context.space_data
        operator = sfile.active_operator
        
        box = layout.box()
        
        col = box.column(heading="Data Types", align=True)
        col.prop(operator, "use_cameras")
        col.prop(operator, "use_curves")
        col.prop(operator, "use_lights")
        col.prop(operator, "use_materials")
        col.prop(operator, "use_meshes")
        col.prop(operator, "use_volumes")
        col.prop(operator, "path_mask")
        col.prop(operator, "scale")
        
        box = layout.box()
        
        col = box.column(heading="Mesh Data", align=True)
        col.prop(operator, "use_uv_coordinates")
        col.prop(operator, "use_mesh_colors")
        
        col = box.column(heading="Include", align=True)
        col.prop(operator, "use_subdiv")
        col.prop(operator, "use_instance_proxies")
        col.prop(operator, "use_visible")
        col.prop(operator, "use_guide")
        col.prop(operator, "use_proxy")
        col.prop(operator, "use_render")
        
        col = box.column(heading="Options", align=True)
        col.prop(operator, "use_frame_range")
        col.prop(operator, "use_relative_path")
        col.prop(operator, "create_collection")
        col.prop(operator, "light_intensity_scale")
        
        box = layout.box()
        col = box.column(heading="Experimental", align=True)
        col.prop(operator, "use_render_preview")
        col.enabled = operator.use_materials
        
        row = col.row(align=True)
        row.prop(operator, "use_material_blend")
        row.enabled = operator.use_render_preview
        

class WM_OT_export_usdz(bpy.types.Operator, ExportHelper):
    """Save a USDZ File"""

    bl_idname = "wm.export_usdz"
    bl_label = "Export USDZ File"
    bl_options = {'PRESET'}

    filename_ext = ".usdz"
    filter_glob: StringProperty(
        default="*.usdz;*.usda;*.usdc",
        options={'HIDDEN'},
    )
    
    use_selected: BoolProperty(
        name="Selection Only",
        description="Only selected objects are exported. Unselected parents of selected objects are exported as empty transform",
        default=False,
    )
    
    use_visible: BoolProperty(
        name="Visible Only",
        description="Only visible objects are exported. Invisible parents of exported objects are exported as empty transform",
        default=True,
    )
    
    use_animation: BoolProperty(
        name="Animation",
        description="When checked, the render frame range is exported. When false, only the current frame is exported",
        default=False,
    )
    
    use_hair: BoolProperty(
        name="Hair",
        description="When checked, hair is exported as USD curves",
        default=False,
    )
    
    use_uvmaps: BoolProperty(
        name="UV Maps",
        description="When checked, all UV maps of exported meshes are included in the export",
        default=True,
    )
    
    use_normals: BoolProperty(
        name="Normals",
        description="When checked, normals of exported meshes are included in the export",
        default=True,
    )
    
    use_materials: BoolProperty(
        name="Materials",
        description="When checked, the viewport settings of materials are exported as USD preview materials, and material assignments are exported as geometry subsets",
        default=True,
    )
    
    use_instancing: BoolProperty(
        name="Instancing",
        description="When checked, instanced objects are exported as references in USD. When unchecked, instanced objects are exported as real objects",
        default=False,
    )
    
    use_preview_surface: BoolProperty(
        name="To USD Preview Surface",
        description="Generate an approximate USD Preview Surface shader representation of a Principled BSDF node network",
        default=True,
    )
    
    use_textures: BoolProperty(
        name="Export Textures",
        description="If exporting materials, export textures referenced by material nodes to a 'textures' directory in the same directory as the USD file",
        default=True,
    )
    
    overwrite_textures: BoolProperty(
        name="Overwrite Textures",
        description="Allow overwriting existing texture files when exporting textures",
        default=False,
    )
    
    evaluation_mode: EnumProperty(
        name="Use Settings for",
        items=(('RENDER', "Render", "Use Render settings for object visibility, modifier settings, etc"),
                ('VIEWPORT', "Viewport", "Use Viewport settings for object visibility, modifier settings, etc"),
                ),
        default="RENDER"
    )

    def execute(self, context):
        from . import export_usdz
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "global_scale",
                                            "check_existing",
                                            "filter_glob",
                                            ))
        return export_usdz.export_usdz(self, context, **keywords)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        sfile = context.space_data
        operator = sfile.active_operator
        
        box = layout.box()
        
        col = box.column(align=True)
        col.prop(operator, "use_selected")
        col.prop(operator, "use_visible")

        col = box.column(align=True)
        col.prop(operator, "use_animation")
        col.prop(operator, "use_hair")
        col.prop(operator, "use_uvmaps")
        col.prop(operator, "use_normals")
        col.prop(operator, "use_materials")
        
        col = box.column(align=True)
        col.prop(operator, "evaluation_mode")
        
        box = layout.box()
        col = box.column(heading="Materials")
        col.prop(operator, "use_preview_surface")
        col.enabled = operator.use_materials
        
        row = col.row()
        row.prop(operator, "use_textures")
        row.enabled = operator.use_materials and operator.use_preview_surface
        
        row = col.row()
        row.prop(operator, "overwrite_textures")
        row.enabled = operator.use_materials and operator.use_preview_surface and operator.use_textures
        
        box = layout.box()
        box.label(text="Experimental")
        box.prop(operator, "use_instancing")

def menu_func_usdz_import(self, context):
    self.layout.operator(WM_OT_usdz_import.bl_idname, text="USDZ (.usdz)")


def menu_func_usdz_export(self, context):
    self.layout.operator(WM_OT_export_usdz.bl_idname, text="USDZ (.usdz)")


classes = (
    # ImportUSDZ, #TODO fix import from temp files
    WM_OT_export_usdz,
    WM_OT_error_popup,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # bpy.types.TOPBAR_MT_file_import.append(menu_func_usdz_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_usdz_export)


def unregister():
    # bpy.types.TOPBAR_MT_file_import.remove(menu_func_usdz_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_usdz_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
