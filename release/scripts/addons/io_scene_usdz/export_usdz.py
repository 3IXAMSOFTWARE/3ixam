import bpy
import os
import subprocess
import tempfile
import shutil
import time
import zipfile

try:
    import zlib
    crc32 = zlib.crc32
except ImportError:
    crc32 = binascii.crc32


MAX_NUMBER_OF_POLYS = 64_000


def draw_popup_with_warning(self, context):
    layout = self.layout
    layout.label(text="Popup warning")


def export_usdz(self, context, filepath='', use_selected=False, use_visible=True,
                use_animation=False, use_hair=False, use_uvmaps=True,
                use_normals=True, use_materials=True,
                use_instancing=False, evaluation_mode='RENDER',
                use_preview_surface=True, use_textures=True,
                overwrite_textures=False,
                ):
    objects_to_export = context.selected_objects if use_selected else bpy.data.objects
    objects_to_export = [obj for obj in objects_to_export if not obj.protect]
    number_of_polygons = sum(
        map(len, [obj.data.polygons for obj in objects_to_export if obj.data is not None and hasattr(obj.data, "polygons")]))
    if number_of_polygons > MAX_NUMBER_OF_POLYS:
        print(f"[USDZ Export] Exceeded number of polys: [{number_of_polygons}/{MAX_NUMBER_OF_POLYS}]")
        self.report({'WARNING'}, "This model has a large number of polygons and may not render well on phones.\n"
                    f"The limit is {MAX_NUMBER_OF_POLYS}.")

    export_dir, file_name = os.path.split(filepath)
    file_name, file_extension = os.path.splitext(file_name)
    if not file_name:
        file_name = "untitled"
    if not file_extension:
        file_extension = ".usdz"

    temp_file_name = file_name + ".usda"
    file_name = file_name + file_extension
    filepath = os.path.join(export_dir, file_name)

    temp_dir = tempfile.mkdtemp()
    temp_filepath = os.path.join(temp_dir, temp_file_name)

    print(f"[USDZ Export] Temporary dir: {temp_dir}")
    print(f"[USDZ Export] Temporary file: {temp_filepath}")
    print(f"[USDZ Export] File path of usdz: {filepath}")

    bpy.ops.wm.usd_export(filepath=temp_filepath,
                          selected_objects_only=use_selected, visible_objects_only=use_visible,
                          export_animation=use_animation, export_hair=use_hair,
                          export_uvmaps=use_uvmaps, export_normals=use_normals,
                          export_materials=use_materials, use_instancing=use_instancing,
                          evaluation_mode=evaluation_mode, generate_preview_surface=use_preview_surface,
                          export_textures=use_textures, overwrite_textures=overwrite_textures,
                          )

    subdirs = [file.path for file in os.scandir(temp_dir) if file.is_dir()]

    with zipfile.ZipFile(filepath, 'w') as zipf:
        zipf.write(temp_filepath, temp_file_name)
        for dir in subdirs:
            print(f"[USDZ Export] Adding folder: {dir}") 
            zipdir(dir, zipf)

    if temp_dir:
        shutil.rmtree(temp_dir)

    return {'FINISHED'}


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))
