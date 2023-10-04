import bpy
import os
import subprocess
import tempfile
import shutil
import zipfile
import bmesh
import mathutils
import math

def import_usdz(context, filepath = '', scale = 1.0, use_frame_range = True,
                use_relative_path = True, use_cameras = True, use_curves = True,
                use_lights = True, use_materials = True, use_meshes = True,
                use_volumes = True, use_subdiv = False, use_instance_proxies = True,
                use_visible = True, create_collection = False, use_uv_coordinates = True,
                use_mesh_colors = False, path_mask = "", use_guide = False,
                use_proxy = True, use_render = True, use_render_preview = False,
                use_material_blend = True, light_intensity_scale = 1.0,
                ):
    import_dir, file_name = os.path.split(filepath)
    file_name, file_extension = os.path.splitext(file_name)
    if not file_name:
        file_name = "untitled"
    if not file_extension:
        file_extension = ".usdz"
    
    temp_file_name = file_name + ".usdz"
    file_name = file_name + file_extension
    filepath = os.path.join(import_dir, file_name)
    
    temp_dir = tempfile.mkdtemp()
    temp_filepath = os.path.join(temp_dir, temp_file_name)
    
    print(f"[USDZ Import] Temporary dir: {temp_dir}")
    print(f"[USDZ Import] Temporary file: {temp_filepath}")
    print(f"[USDZ Import] File path of usdz: {filepath}")
    
    shutil.copy(filepath, temp_filepath)
    zip = zipfile.ZipFile(temp_filepath)
    zip.extractall(temp_dir)
    
    usd_temp_file = find_usd(temp_dir)
    if not usd_temp_file:
        print("[USDZ Import] Unpacked usdc file was not found.")
        return {'CANCELLED'}
    
    print(f"[USDZ Import] Found unpacked usdc file: {usd_temp_file}")
    
    bpy.ops.wm.usd_import(filepath=usd_temp_file, relative_path = use_relative_path,
                          import_instance_proxies = use_instance_proxies, import_visible_only = use_visible,
                          create_collection = create_collection, read_mesh_uvs = use_uv_coordinates,
                          read_mesh_colors = use_mesh_colors, prim_path_mask = path_mask,
                          import_guide = use_guide, import_proxy = use_proxy,
                          import_render = use_render, import_usd_preview = use_render_preview,
                          set_material_blend = use_material_blend, light_intensity_scale = light_intensity_scale,
                          scale=scale, set_frame_range = use_frame_range,
                          import_cameras = use_cameras, import_curves = use_curves,
                          import_lights = use_lights, import_materials = use_materials,
                          import_meshes = use_meshes, import_volumes = use_volumes,
                          import_subdiv = use_subdiv, 
                          )
    
    if temp_dir:
        shutil.rmtree(temp_dir)
    
    return {'FINISHED'}
    
def find_usd(path):
    usd_extensions = ('.usd', '.usda', '.usdc')
    for dirpath, dirnames, filenames in os.walk(path):
        for file in filenames:
            _, extension = os.path.splitext(file)
            if extension not in usd_extensions:
                continue
            return os.path.join(dirpath, file)
    return None
