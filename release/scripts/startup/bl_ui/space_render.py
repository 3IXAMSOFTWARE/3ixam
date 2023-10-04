

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
class RENDER_PT_main(Panel):
    bl_space_type = 'RENDER'
    bl_region_type = 'WINDOW'
    bl_label = "Render Main"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="MAIN REGION")
        
class RENDER_PT_menu_header(Panel):
    bl_space_type = 'RENDER'
    bl_region_type = 'PRO_MENU'
    bl_label = "Render Menu Header"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        space = context.space_data

        layout.shape = "TRAPEZOID"
        layout.prop(space, "menu_active_section", expand=True)

class RENDER_PT_menu_common(Panel):
    bl_space_type = 'RENDER'
    bl_region_type = 'PRO_MENU'
    bl_label = "Render Menu Common"
    bl_options = {'HIDE_HEADER'}
    bl_context = "common"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.label(text="COMMON PARAMETERS", shape = "PREFS")

        rd = context.scene.render
        scene = context.scene
        image_settings = rd.image_settings
        
        layout.label(text="Time Output")
        col = layout.column(align=True)
        col.prop(rd, "is_animation", text="Render Animation", shape = "PREFS")
        sub = col.column(align=True)
        sub.enabled = rd.is_animation
        sub.prop(scene, "frame_start", text="Frame Start", shape = "PREFS")
        sub.prop(scene, "frame_end", text="End", shape = "PREFS")
        sub.prop(scene, "frame_step", text="Step", shape = "PREFS")

        layout.label(text="Output Size")
        col = layout.column(align=True)
        col2 = col.column(heading='Presets')
        col2.menu("SNA_MT_New_Menu_7317B", text=bpy.context.scene.name_of_menu, shape="PREFS")
        col.prop(rd, "resolution_x", text="Width", shape = "PREFS")
        col.prop(rd, "resolution_y", text="Heigth", shape = "PREFS")
        col.prop(rd, "resolution_percentage", text="%", shape = "PREFS")
        col.prop(rd, "fps", text="Fps", shape = "PREFS")

        col = layout.column(align=True)
        col.prop(rd, "pixel_aspect_x", text="Aspect X", shape = "PREFS")
        col.prop(rd, "pixel_aspect_y", text="Aspect Y", shape = "PREFS")

        layout.label(text="Render Output")

        col = layout.column(heading="Background")
        col.prop(rd, "film_transparent", text="Alpha/Transparent")
        
        layout.prop(rd, "filepath", text="Path", shape = "PREFS")

        col = layout.column(heading="Saving")
        col.prop(rd, "use_file_extension", shape = "PREFS")
        col.prop(rd, "use_render_cache", shape = "PREFS")
        
        sub = layout.column()
        sub.shape = "PREFS"
        sub.template_image_settings(image_settings, color_management=False)

        if not rd.is_movie_format:
            col = layout.column(heading="Image Sequence")
            col.prop(rd, "use_overwrite", shape = "PREFS")
            col.prop(rd, "use_placeholder", shape = "PREFS")


def show_device_active(context):
    cscene = context.scene.cycles
    if cscene.device != 'GPU':
        return True
    return context.preferences.addons['cycles'].preferences.has_active_device()

class RENDER_PT_menu_scene(Panel):
    bl_space_type = 'RENDER'
    bl_region_type = 'PRO_MENU'
    bl_label = "Render Menu Scene"
    bl_options = {'HIDE_HEADER'}
    bl_context = "scene"

    def draw_eevee_settings(self, context, scene, rd):
        layout = self.layout
        props = scene.eevee
        
        row = layout.row()
        col = row.column()
        col.ui_units_x = 3
        col.prop(rd, "engine", text="Render Engine", shape = "PREFS")

        row.separator(factor = 8)

        layout.label(text="Sampling")

        col = layout.column(align=True)
        col.prop(props, "taa_render_samples", text="Render", shape = "PREFS")
        col.prop(props, "taa_samples", text="Viewport", shape = "PREFS")

        col = layout.column()
        col.prop(props, "use_taa_reprojection", shape = "PREFS")
    
    def draw_workbench_settings(self, context, scene, rd):
        layout = self.layout
        props = scene.display

        row = layout.row()
        col = row.column()
        col.ui_units_x = 3
        col.prop(rd, "engine", text="Render Engine", shape = "PREFS")

        row.separator(factor = 8)

        layout.label(text="Sampling")

        col = layout.column(align=True)
        col.prop(props, "render_aa", text="Render", shape = "PREFS")
        col.prop(props, "viewport_aa", text="Viewport", shape = "PREFS")   
    
    def draw_cycles_viewport_settings(self, context, cscene):
        layout = self.layout
        
        layout.label(text="Viewport")
        col = layout.column(align=True)

        col.prop(context.scene.cycles, "use_preview_denoising", text="Denoiser")
        col.prop(cscene, "use_preview_adaptive_sampling", text="Noise Threshold")
        sub = col.row(align=True)
        sub.active = cscene.use_preview_adaptive_sampling
        sub.enabled = cscene.use_preview_adaptive_sampling
        sub.prop(cscene, "preview_adaptive_threshold", text="Threshold", shape="PREFS")

        if cscene.use_preview_adaptive_sampling:
            col.prop(cscene, "preview_samples", text=" Max Samples", shape="PREFS")
            col.prop(cscene, "preview_adaptive_min_samples", text="Min Samples", shape="PREFS")
        else:
            col.prop(cscene, "preview_samples", text="Samples", shape="PREFS")
    
    def draw_cycles_render_settings(self, context, cscene):
        layout = self.layout
        
        layout.label(text="Render")
        col = layout.column(align=True)
        col.prop(context.scene.cycles, "use_denoising", text="Denoiser")
        col.prop(cscene, "use_adaptive_sampling", text="Noise Threshold")
        sub = col.row(align=True)
        sub.active = cscene.use_adaptive_sampling
        sub.prop(cscene, "adaptive_threshold", text="Threshold", shape="PREFS")

        if cscene.use_adaptive_sampling:
            col.prop(cscene, "samples", text=" Max Samples", shape="PREFS")
            col.prop(cscene, "adaptive_min_samples", text="Min Samples", shape="PREFS")
        else:
            col.prop(cscene, "samples", text="Samples", shape="PREFS")
        col.prop(cscene, "time_limit", shape="PREFS")
        
    def draw_world_settings(self, context):
        layout = self.layout
        
        layout.label(text="World")
        col = layout.column(align=True)
        col.shape = 'PREFS'
        col.prop(context.scene.world, "use_nodes", text="Use HDRI")
        col.separator(factor=2.0)
        if context.scene.world.use_nodes:
            row = col.row(align=True)
            row.label(text="Environment Texture")
            row.template_ID(context.scene.world.node_tree.nodes['Environment Texture'], "image", open="image.open", text="")
            
            row = col.row(align=True)
            row.label(text="Strength")
            row.prop(context.scene.world.node_tree.nodes["Background"].inputs[1], "default_value", text="")

            col.separator(factor=2.0)
            col.label(text="HDRI Advanced Settings")
            col.separator(factor=2.0)

            row = col.row(align=True)
            row.label(text="Location X")
            row.prop(context.scene.world.node_tree.nodes['Mapping'].inputs[1], "default_value", index=0,  text="", shape="PREFS")
            
            row = col.row(align=True)
            row.label(text="Location Y")
            row.prop(context.scene.world.node_tree.nodes['Mapping'].inputs[1], "default_value", index=1,  text="", shape="PREFS")
            
            row = col.row(align=True)
            row.label(text="Location Z")
            row.prop(context.scene.world.node_tree.nodes['Mapping'].inputs[1], "default_value", index=2,  text="", shape="PREFS")

            row = col.row(align=True)
            row.label(text="Rotation X")
            row.prop(context.scene.world.node_tree.nodes['Mapping'].inputs[2], "default_value", index=0,  text="", shape="PREFS")

            row = col.row(align=True)
            row.label(text="Rotation Y")
            row.prop(context.scene.world.node_tree.nodes['Mapping'].inputs[2], "default_value", index=1,  text="", shape="PREFS")
            
            row = col.row(align=True)
            row.label(text="Rotation Z")
            row.prop(context.scene.world.node_tree.nodes['Mapping'].inputs[2], "default_value", index=2,  text="", shape="PREFS")

            row = col.row(align=True)
            row.label(text="Scale X")
            row.prop(context.scene.world.node_tree.nodes['Mapping'].inputs[3], "default_value", index=0,  text="", shape="PREFS")

            row = col.row(align=True)
            row.label(text="Scale Y")
            row.prop(context.scene.world.node_tree.nodes['Mapping'].inputs[3], "default_value", index=1,  text="", shape="PREFS")
            
            row = col.row(align=True)
            row.label(text="Scale Z")
            row.prop(context.scene.world.node_tree.nodes['Mapping'].inputs[3], "default_value", index=2,  text="", shape="PREFS")
        else:
            row = col.row(align=True)
            row.prop(context.scene.world, "color")     
        

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        rd = scene.render
        
        layout.label(text="SCENE", shape="PREFS")
        
        if context.engine == 'IXAM_EEVEE':
            self.draw_eevee_settings(context, scene, rd)

        elif context.engine == 'IXAM_WORKBENCH':
            self.draw_workbench_settings(context, scene, rd)

        elif context.engine == 'CYCLES':
            cscene = scene.cycles

            row = layout.row()
            col = row.column()
            col.ui_units_x = 3
            col.prop(rd, "engine", text="Render Engine", shape = "PREFS")
            # col.prop(cscene, "device", text="Render Device", shape = "PREFS")

            row.separator(factor = 8)

            self.draw_cycles_viewport_settings(context, cscene)
            
            self.draw_cycles_render_settings(context, cscene)
        self.draw_world_settings(context)


class RENDER_PT_menu_camera(Panel):
    bl_space_type = 'RENDER'
    bl_region_type = 'PRO_MENU'
    bl_label = "Render Menu Camera"
    bl_options = {'HIDE_HEADER'}
    bl_context = "camera"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.label(text="CAMERA", shape="PREFS")

        scene = context.scene

        layout.prop(scene, "camera", text="Camera", shape="PREFS")

        if not scene.camera:
            layout.label(text="No camera selected", shape="PREFS")
            return

        cam = scene.camera.data
        
        layout.label(text="Lens")
        col = layout.column(align=True)
        col.shape = 'PREFS'
        col.prop(cam, "type")

        if cam.type == 'PERSP':
            if cam.lens_unit == 'MILLIMETERS':
                col.prop(cam, "lens")
            elif cam.lens_unit == 'FOV':
                col.prop(cam, "angle")
            col.prop(cam, "lens_unit")

        elif cam.type == 'ORTHO':
            col.prop(cam, "ortho_scale")

        elif cam.type == 'PANO':
            engine = context.engine
            if engine == 'CYCLES':
                ccam = cam.cycles
                col.prop(ccam, "panorama_type")
                if ccam.panorama_type == 'FISHEYE_EQUIDISTANT':
                    col.prop(ccam, "fisheye_fov")
                elif ccam.panorama_type == 'FISHEYE_EQUISOLID':
                    col.prop(ccam, "fisheye_lens", text="Lens")
                    col.prop(ccam, "fisheye_fov")
                elif ccam.panorama_type == 'EQUIRECTANGULAR':
                    sub = col.column(align=True)
                    sub.prop(ccam, "latitude_min", text="Latitude Min")
                    sub.prop(ccam, "latitude_max", text="Max")
                    sub = col.column(align=True)
                    sub.prop(ccam, "longitude_min", text="Longitude Min")
                    sub.prop(ccam, "longitude_max", text="Max")
                elif ccam.panorama_type == 'FISHEYE_LENS_POLYNOMIAL':
                    col.prop(ccam, "fisheye_fov")
                    col.prop(ccam, "fisheye_polynomial_k0", text="K0")
                    col.prop(ccam, "fisheye_polynomial_k1", text="K1")
                    col.prop(ccam, "fisheye_polynomial_k2", text="K2")
                    col.prop(ccam, "fisheye_polynomial_k3", text="K3")
                    col.prop(ccam, "fisheye_polynomial_k4", text="K4")

            elif engine in {'IXAM_RENDER', 'IXAM_EEVEE', 'IXAM_WORKBENCH'}:
                if cam.lens_unit == 'MILLIMETERS':
                    col.prop(cam, "lens")
                elif cam.lens_unit == 'FOV':
                    col.prop(cam, "angle")
                col.prop(cam, "lens_unit")

        col = layout.column()
        col.separator()

        sub = layout.column(align=True)
        sub.shape = 'PREFS'
        sub.prop(cam, "shift_x", text="Shift X")
        sub.prop(cam, "shift_y", text="Y")

        sub = layout.column(align=True)
        sub.shape = 'PREFS'
        sub.prop(cam, "clip_start", text="Clip Start")
        sub.prop(cam, "clip_end", text="End")

        layout.label(text="Sensor")
        col = layout.column(align=True)
        col.shape = 'PREFS'
        col.prop(cam, "sensor_fit")

        if cam.sensor_fit == 'AUTO':
            col.prop(cam, "sensor_width", text="Size")
        else:
            sub = col.column(align=True)
            if cam.sensor_fit == 'HORIZONTAL':
                sub.prop(cam, "sensor_width", text="Width")
            else:
                sub.prop(cam, "sensor_height", text="Height")

        dof = cam.dof
        
        layout.label(text="Depth of Field")
        col = layout.column(align=True)
        col.shape = "PREFS"
        col.active = dof.use_dof
        col.prop(dof, "use_dof", text="Depth of Field")
        col.prop(dof, "focus_object", text="Focus on Object")
        sub = col.column(align=True)
        sub.active = (dof.focus_object is None)
        sub.prop(dof, "focus_distance", text="Focus Distance")


        layout.label(text="Aperture")
        col = layout.column(align=True)
        col.shape = "PREFS"
        col.active = dof.use_dof
        col.prop(dof, "aperture_fstop")
        col.prop(dof, "aperture_blades")
        col.prop(dof, "aperture_rotation")
        col.prop(dof, "aperture_ratio")


class RENDER_PT_menu_render_elements(Panel):
    bl_space_type = 'RENDER'
    bl_region_type = 'PRO_MENU'
    bl_label = "Render Menu Render Elemets"
    bl_options = {'HIDE_HEADER'}
    bl_context = "render_elements"

    def draw(self, context):
        layout = self.layout
        layout.label(text="RENDER ELEMENTS", shape="PREFS")

        if context.engine == 'IXAM_EEVEE':
            view_layer = context.view_layer
            view_layer_eevee = view_layer.eevee
            scene = context.scene
            scene_eevee = scene.eevee

            layout.label(text="Data")
            col = layout.row()
            col.prop(view_layer, "use_pass_combined")
            col.prop(view_layer, "use_pass_z")
            col.prop(view_layer, "use_pass_mist")
            col.prop(view_layer, "use_pass_normal")

            layout.label(text="Light")
            row = layout.row()
            col = row.column(heading="Diffuse", align=True)
            col.prop(view_layer, "use_pass_diffuse_direct", text="Light")
            col.prop(view_layer, "use_pass_diffuse_color", text="Color")

            col = row.column(heading="Specular", align=True)
            col.prop(view_layer, "use_pass_glossy_direct", text="Light")
            col.prop(view_layer, "use_pass_glossy_color", text="Color")

            row = layout.row()
            col = row.column(heading="Volume", align=True)
            col.prop(view_layer_eevee, "use_pass_volume_direct", text="Light")

            col = row.column(heading="Other", align=True)
            col.prop(view_layer, "use_pass_emit", text="Emission")
            col.prop(view_layer, "use_pass_environment")
            col.prop(view_layer, "use_pass_shadow")
            col.prop(view_layer, "use_pass_ambient_occlusion",
                        text="Ambient Occlusion")

        elif context.engine == 'CYCLES':
            scene = context.scene
            rd = scene.render
            view_layer = context.view_layer
            cycles_view_layer = view_layer.cycles

            layout.label(text="Data")
            col = layout.grid_flow(row_major=True, columns=2)
            col.prop(view_layer, "use_pass_combined")
            col.prop(view_layer, "use_pass_z")
            col.prop(view_layer, "use_pass_mist")
            col.prop(view_layer, "use_pass_position")
            col.prop(view_layer, "use_pass_normal")
            sub = col.column()
            sub.active = not rd.use_motion_blur
            sub.prop(view_layer, "use_pass_vector")
            col.prop(view_layer, "use_pass_uv")
            col.prop(cycles_view_layer, "denoising_store_passes", text="Denoising Data")
            col.prop(view_layer, "use_pass_object_index")
            col.prop(view_layer, "use_pass_material_index")

            col = layout.column(heading="Debug", align=True)
            col.prop(cycles_view_layer, "pass_debug_sample_count", text="Sample Count")

            layout.label(text="Light")
            row = layout.row()
            col = row.column(heading="Diffuse", align=True)
            col.prop(view_layer, "use_pass_diffuse_direct", text="Direct")
            col.prop(view_layer, "use_pass_diffuse_indirect", text="Indirect")
            col.prop(view_layer, "use_pass_diffuse_color", text="Color")

            col = row.column(heading="Glossy", align=True)
            col.prop(view_layer, "use_pass_glossy_direct", text="Direct")
            col.prop(view_layer, "use_pass_glossy_indirect", text="Indirect")
            col.prop(view_layer, "use_pass_glossy_color", text="Color")

            row = layout.row()
            col = row.column(heading="Transmission", align=True)
            col.prop(view_layer, "use_pass_transmission_direct", text="Direct")
            col.prop(view_layer, "use_pass_transmission_indirect", text="Indirect")
            col.prop(view_layer, "use_pass_transmission_color", text="Color")

            col = row.column(heading="Volume", align=True)
            col.prop(cycles_view_layer, "use_pass_volume_direct", text="Direct")
            col.prop(cycles_view_layer, "use_pass_volume_indirect", text="Indirect")

            col = layout.column(heading="Other", align=True)
            col.prop(view_layer, "use_pass_emit", text="Emission")
            col.prop(view_layer, "use_pass_environment")
            col.prop(view_layer, "use_pass_shadow")
            col.prop(view_layer, "use_pass_ambient_occlusion", text="Ambient Occlusion")
            col.prop(cycles_view_layer, "use_pass_shadow_catcher")


class RENDER_PT_post_effects_header(Panel):
    bl_space_type = 'RENDER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Render Post Effects Header"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        space = context.space_data

        layout.shape = "TRAPEZOID"
        layout.prop(space, "post_active_section", expand=True)

class RENDER_PT_post_effects_tone_mapping(Panel):
    bl_space_type = 'RENDER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Render Post Effects Tone Mapping"
    bl_options = {'HIDE_HEADER'}
    bl_context = "tone_mapping"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        nt = scene.node_tree
        nodes = nt.nodes

        layout.label(text="Balance")
        col = layout.column(align=True)
        col.shape = "PREFS"
        col.prop(nodes['Exposure'].inputs[1], "default_value", text="Exposure")
        col.prop(nodes['Bright/Contrast'].inputs[2], "default_value", text="Contrast")
        col.prop(nodes['Hue Saturation Value'].inputs[2], "default_value", text="Saturation")
        col.prop(nodes['Color Correction'], "highlights_gain", text="Filmic Highlights")
        col.prop(nodes['Color Correction'], "highlights_lift", text="Filmic Shadows")
        
        layout.label(text="Color Correction")
        col = layout.column(align=True)
        col.shape = "PREFS"
        col.prop(nodes['Color Balance'], "slope", text="Color Balance")
        col.prop(nodes['RGB Curves'].inputs[2], "default_value", text="Black Level")
        col.prop(nodes['RGB Curves'].inputs[3], "default_value", text="White Level")

        layout.label(text="Vignette")
        col = layout.column(align=True)
        col.shape = "PREFS"
        col.prop(nodes['Mix.001'].inputs[0], "default_value", text="Vignette Intensity")

class RENDER_PT_post_effects_bloom_glare(Panel):
    bl_space_type = 'RENDER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Render Post Effects Bloom Glare"
    bl_options = {'HIDE_HEADER'}
    bl_context = "bloom_glare"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        nt = scene.node_tree
        nodes = nt.nodes

        layout.label(text="Bloom")
        col = layout.column(align=True)
        col.shape = "PREFS"
        col.prop(nodes['Glare'], "mix", text="Bloom Intensity")
        col.prop(nodes['Glare'], "threshold", text="Bloom Threshold")
        
        layout.label(text="Glare")
        col = layout.column(align=True)
        col.shape = "PREFS"
        col.prop(nodes['Glare.001'], "mix", text="Glare Intensity")
        col.prop(nodes['Glare.001'], "threshold", text="Glare Threshold")
        col.prop(nodes['Glare.001'], "streaks", text="Streaks")
        col.prop(nodes['Glare.001'], "angle_offset", text="Angle Offset")
        col.prop(nodes['Glare.001'], "fade", text="Fade")

class RENDER_PT_post_effects_sharpening_bluring(Panel):
    bl_space_type = 'RENDER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Render Post Effects Sharpening Bluring"
    bl_options = {'HIDE_HEADER'}
    bl_context = "sharpening_bluring"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        nt = scene.node_tree
        nodes = nt.nodes

        layout.label(text="Sharpening")
        col = layout.column(align=True)
        col.shape = "PREFS"
        col.prop(nodes['Filter'].inputs[0], "default_value", text="Sharpen Amount")

        layout.label(text="Blurring")
        col = layout.column(align=True)
        col.shape = "PREFS"
        col.prop(nodes['Blur'].inputs[1], "default_value", text="Blur Radius")


class RENDER_PT_statistic_header(Panel):
    bl_space_type = 'RENDER'
    bl_region_type = 'EXECUTE'
    bl_label = "Render Statistic Header"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        space = context.space_data

        layout.shape = "TRAPEZOID"
        layout.prop(space, "statistic_active_section", expand=True)

class RENDER_PT_statistic_statistic(Panel):
    bl_space_type = 'RENDER'
    bl_region_type = 'EXECUTE'
    bl_label = "Render Statistic Statistic"
    bl_options = {'HIDE_HEADER'}
    bl_context = "statistics"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text='RENDERING PROGRESS', shape='PREFS')
        col = layout.column_flow(columns=2, align=True)
        frame = '0'
        last = '0'
        remain = '0'
        time = '0'
        sample = '0/0'
        s = scene.render_statistics()
        if len(s) > 0:
            for stat in s.split(' | '):
                if stat.startswith('Time:'):
                    time= stat[5:]
                    continue

                if stat.startswith('Frame:'):
                    frame = stat[6:]
                    continue

                if stat.startswith('Last:'):
                    last = stat[5:]
                    continue
                
                if stat.startswith('Remaining:'):
                    remain = stat[10:]
                    continue

                if stat.startswith('Sample'):
                    sample = stat[6:]
                    continue

        col.label(text=f"Frame:  #{frame}")
        col.label(text=f"Pass:  {sample}")
        col.label(text="")
        col.label(text=f"Last Frame Time:  {last}")
        col.label(text=f"Remain Time:  {remain}")
        col.label(text=f"Elapsed Time:  {time}")

        layout.separator()
        layout.label(text='RENDER SETTINGS', shape='PREFS')
        col = layout.column_flow(columns=2, align=True)

        camera = scene.camera
        rd = scene.render
        col.label(text=f"Camera:  {camera.name if camera else ''}")
        col.label(text=f"Width:  {int(rd.resolution_x * rd.resolution_percentage / 100)}")
        col.label(text=f"Height:  {int(rd.resolution_y * rd.resolution_percentage / 100)}")
        col.label(text="")
        col.label(text=f"Start Frame:  {scene.frame_start}")
        col.label(text=f"End Frame:  {scene.frame_end}")

 
        layout.separator()
        layout.label(text="SCENE STATISTICS", shape='PREFS')
        col = layout.column_flow(columns=2, align=True)
        faces = '0'
        verts = '0'
        objects = '0'
        mem = '0'
        for stat in bpy.context.scene.statistics(bpy.context.view_layer).split(' | '):
            if stat.startswith('Faces:'):
                faces = stat[6:]
                continue

            if stat.startswith('Verts:'):
                verts = stat[6:]
                continue

            if stat.startswith('Objects:'):
                objects = stat[8:].split('/')[-1]
                continue

            if stat.startswith('Memory:'):
                mem = stat[7:]
                continue
        
        col.label(text=f'Polygons:  {faces}')
        col.label(text=f'Memory:  {mem}')
        col.label(text=f'Verts:  {verts}')
        col.label(text=f'Objects:  {objects}')

class RENDER_PT_statistic_common_parameters(Panel):
    bl_space_type = 'RENDER'
    bl_region_type = 'EXECUTE'
    bl_label = 'Render Statistic Common Parameters'
    bl_options = {'HIDE_HEADER'}
    bl_context = 'common_parameters'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        rd = context.scene.render
        cscene = context.scene.cycles

        layout.label(text="PERFOMANCE", shape='PREFS')
        col = layout.column(align=True)
        col.prop(rd, "threads_mode", shape='PREFS')
        sub = col.column(align=True)
        sub.enabled = rd.threads_mode == 'FIXED'
        sub.prop(rd, "threads", shape='PREFS')

        layout.separator()
        col = layout.column(align=True)
        col.prop(cscene, "use_auto_tile", shape='PREFS')
        sub = col.column()
        sub.active = cscene.use_auto_tile
        sub.prop(cscene, "tile_size", shape='PREFS')

        layout.separator()
        col = layout.column()
        col.prop(rd, "preview_pixel_size", text="Pixel Scale", shape='PREFS')

class RENDER_PT_progress_bar(Panel):
    bl_space_type = 'RENDER'
    bl_region_type = 'PRO_MENU'
    bl_label = "Render Parameters"
    bl_options = {'HIDE_HEADER', 'INSTANCED'}

    def draw(self, context):
        layout = self.layout

        layout.template_render_jobs()


class RENDER_PT_control(Panel):
    bl_space_type = 'RENDER'
    bl_region_type = 'TEMPORARY'
    bl_label = "Render Control"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):

        layout = self.layout

        sima = context.space_data
        iuser = sima.image_user

        row = layout.row(align=True)
        row.separator(factor=7.0)

        col = row.column()
        col.separator()
        col.scale_x = 0.1
        col.template_image_pass_selector_only(sima, "image", iuser, multiview=True, compact=True)

        row.separator()

        button = row.column()
        button.scale_y = 2.1
        button.ui_units_x = 0.5
        button.operator("render.save_as", text="SAVE", shape="ADVANCED")

        row.separator()

        button = row.column()
        button.scale_y = 2.1
        button.ui_units_x = 0.5
        anim = context.scene.render.is_animation
        but_label = "Render"
        if context.scene.is_rendering:
            but_label = "Cancel"
        props = button.operator("render.render", text=but_label, shape="ADVANCED")
        if anim:
            props.animation = True
            props.use_viewport = True

classes = (
    RENDER_PT_main,
    RENDER_PT_menu_header,
    RENDER_PT_menu_common,
    RENDER_PT_menu_scene,
    RENDER_PT_menu_camera,
    RENDER_PT_menu_render_elements,
    RENDER_PT_post_effects_header,
    RENDER_PT_post_effects_tone_mapping,
    RENDER_PT_post_effects_bloom_glare,
    RENDER_PT_post_effects_sharpening_bluring,  
    RENDER_PT_statistic_header,
    RENDER_PT_statistic_statistic,
    RENDER_PT_statistic_common_parameters,
    RENDER_PT_progress_bar,
    RENDER_PT_control,
    #RENDER_PT_image_properties,
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
