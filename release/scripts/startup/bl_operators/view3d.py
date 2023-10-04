
import typing
import bpy
from bpy.types import Context, Operator
from bpy.props import (
    BoolProperty,
    EnumProperty,
    PointerProperty,
)

import mathutils


class VIEW3D_OT_edit_mesh_extrude_individual_move(Operator):
    """Extrude each individual face separately along local normals"""
    bl_label = "Extrude Individual and Move"
    bl_idname = "view3d.edit_mesh_extrude_individual_move"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and obj.mode == 'EDIT')

    def execute(self, context):
        mesh = context.object.data
        select_mode = context.tool_settings.mesh_select_mode

        totface = mesh.total_face_sel
        totedge = mesh.total_edge_sel
        # totvert = mesh.total_vert_sel

        if select_mode[2] and totface == 1:
            bpy.ops.mesh.extrude_region_move(
                'INVOKE_REGION_WIN',
                TRANSFORM_OT_translate={
                    "orient_type": 'NORMAL',
                    "constraint_axis": (False, False, True),
                }
            )
        elif select_mode[2] and totface > 1:
            bpy.ops.mesh.extrude_faces_move('INVOKE_REGION_WIN')
        elif select_mode[1] and totedge >= 1:
            bpy.ops.mesh.extrude_edges_move('INVOKE_REGION_WIN')
        else:
            bpy.ops.mesh.extrude_vertices_move('INVOKE_REGION_WIN')

        # ignore return from operators above because they are 'RUNNING_MODAL',
        # and cause this one not to be freed. T24671.
        return {'FINISHED'}

    def invoke(self, context, _event):
        return self.execute(context)


class VIEW3D_OT_edit_mesh_extrude_move(Operator):
    """Extrude region together along the average normal"""
    bl_label = "Extrude and Move on Normals"
    bl_idname = "view3d.edit_mesh_extrude_move_normal"

    dissolve_and_intersect: BoolProperty(
        name="dissolve_and_intersect",
        default=False,
        description="Dissolves adjacent faces and intersects new geometry"
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and obj.mode == 'EDIT')

    @staticmethod
    def extrude_region(context, use_vert_normals, dissolve_and_intersect):
        mesh = context.object.data

        totface = mesh.total_face_sel
        totedge = mesh.total_edge_sel
        # totvert = mesh.total_vert_sel

        if totface >= 1:
            if use_vert_normals:
                bpy.ops.mesh.extrude_region_shrink_fatten(
                    'INVOKE_REGION_WIN',
                    TRANSFORM_OT_shrink_fatten={},
                )
            elif dissolve_and_intersect:
                bpy.ops.mesh.extrude_manifold(
                    'INVOKE_REGION_WIN',
                    MESH_OT_extrude_region={
                        "use_dissolve_ortho_edges": True,
                    },
                    TRANSFORM_OT_translate={
                        "orient_type": 'NORMAL',
                        "constraint_axis": (False, False, True),
                    },
                )
            else:
                bpy.ops.mesh.extrude_region_move(
                    'INVOKE_REGION_WIN',
                    TRANSFORM_OT_translate={
                        "orient_type": 'NORMAL',
                        "constraint_axis": (False, False, True),
                    },
                )

        elif totedge == 1:
            bpy.ops.mesh.extrude_region_move(
                'INVOKE_REGION_WIN',
                TRANSFORM_OT_translate={
                    # Don't set the constraint axis since users will expect MMB
                    # to use the user setting, see: T61637
                    # "orient_type": 'NORMAL',
                    # Not a popular choice, too restrictive for retopo.
                    # "constraint_axis": (True, True, False)})
                    "constraint_axis": (False, False, False),
                })
        else:
            bpy.ops.mesh.extrude_region_move('INVOKE_REGION_WIN')

        # ignore return from operators above because they are 'RUNNING_MODAL',
        # and cause this one not to be freed. T24671.
        return {'FINISHED'}

    def execute(self, context):
        return VIEW3D_OT_edit_mesh_extrude_move.extrude_region(context, False, self.dissolve_and_intersect)

    def invoke(self, context, _event):
        return self.execute(context)


class VIEW3D_OT_edit_mesh_extrude_shrink_fatten(Operator):
    """Extrude region together along local normals"""
    bl_label = "Extrude and Move on Individual Normals"
    bl_idname = "view3d.edit_mesh_extrude_move_shrink_fatten"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and obj.mode == 'EDIT')

    def execute(self, context):
        return VIEW3D_OT_edit_mesh_extrude_move.extrude_region(context, True, False)

    def invoke(self, context, _event):
        return self.execute(context)


class VIEW3D_OT_edit_mesh_extrude_manifold_normal(Operator):
    """Extrude manifold region along normals"""
    bl_label = "Extrude Manifold Along Normals"
    bl_idname = "view3d.edit_mesh_extrude_manifold_normal"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and obj.mode == 'EDIT')

    def execute(self, _context):
        bpy.ops.mesh.extrude_manifold(
            'INVOKE_REGION_WIN',
            MESH_OT_extrude_region={
                "use_dissolve_ortho_edges": True,
            },
            TRANSFORM_OT_translate={
                "orient_type": 'NORMAL',
                "constraint_axis": (False, False, True),
            },
        )
        return {'FINISHED'}

    def invoke(self, context, _event):
        return self.execute(context)


class VIEW3D_OT_transform_gizmo_set(Operator):
    """Set the current transform gizmo"""
    bl_label = "Transform Gizmo Set"
    bl_options = {'REGISTER', 'UNDO'}
    bl_idname = "view3d.transform_gizmo_set"

    extend: BoolProperty(
        name="Extend",
        default=False,
    )
    type: EnumProperty(
        name="Type",
        items=(
            ('TRANSLATE', "Move", ""),
            ('ROTATE', "Rotate", ""),
            ('SCALE', "Scale", ""),
        ),
        options={'ENUM_FLAG'},
    )

    @classmethod
    def poll(cls, context):
        area = context.area
        return area and (area.type == 'VIEW_3D')

    def execute(self, context):
        space_data = context.space_data
        space_data.show_gizmo = True
        attrs = ("show_gizmo_object_translate", "show_gizmo_object_rotate", "show_gizmo_object_scale")
        attr_active = tuple(
            attrs[('TRANSLATE', 'ROTATE', 'SCALE').index(t)]
            for t in self.type
        )
        if self.extend:
            for attr in attrs:
                if attr in attr_active:
                    setattr(space_data, attr, True)
        else:
            for attr in attrs:
                setattr(space_data, attr, attr in attr_active)
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.properties.is_property_set("extend"):
            self.extend = event.shift
        return self.execute(context)


class VIEW3D_OT_find(Operator):
    """Find object in spaceview"""
    bl_label = "Find Object"
    bl_options = {'REGISTER', 'UNDO'}
    bl_idname = "view3d.find"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        area = context.area
        if area is not None and area.type == 'VIEW_3D':
            return bpy.ops.view3d.view_selected({"area":area}, 'INVOKE_REGION_WIN')
        
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                return bpy.ops.view3d.view_selected({"area":area, "region":area.regions[-1]}, 'INVOKE_DEFAULT') 

class VIEW3D_OT_render(Operator):
    """Render Image"""
    bl_label = "Render Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_idname = "view3d.render"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.ops.render.render('INVOKE_DEFAULT')
        return {'FINISHED'}


class VIEW3D_OT_render_animation(Operator):
    """Render Animation"""
    bl_label = "Render Animation"
    bl_options = {'REGISTER', 'UNDO'}
    bl_idname = "view3d.render_animation"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.scene.render.image_settings.file_format = 'AVI_JPEG'
        bpy.ops.render.render('INVOKE_DEFAULT', animation = True)
        return {'FINISHED'}

class VIEW3D_OT_material(Operator):
    """Change Material"""
    bl_label = "Change Material"
    bl_options = {'REGISTER', 'UNDO'}
    bl_idname = "view3d.material"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'NODE_EDITOR':
                    return {'FINISHED'}

        bpy.ops.screen.userpref_show()
        screen = bpy.context.window_manager.windows[-1].screen
        area = screen.areas[0]
        area.type = 'MATLIB'
        return {'FINISHED'}

class VIEW3D_OT_pro_material(Operator):
    bl_label = "Open Material Editor"
    bl_options = {'REGISTER', 'UNDO'}
    bl_idname = "view3d.pro_material"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'NODE_EDITOR':
                    return {'FINISHED'}

        bpy.ops.screen.shadereditor_show()
        return {'FINISHED'}

        
class VIEW3D_OT_add_point_light(Operator):
    """Add Point Light"""
    bl_label = "Add Point Light"
    bl_options = {'REGISTER', 'UNDO'}
    bl_idname = "view3d.point_light"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.object.light_add(type='POINT')
        return {'FINISHED'}


class VIEW3D_OT_collection_delete(Operator):
    bl_label = "Delete selected collection"
    bl_options = {'REGISTER', 'UNDO'}
    bl_idname = "view3d.collection_delete"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        collection = context.collection
        if collection is None:
            return {'FINISHED'}
        for obj in collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
            
        bpy.data.collections.remove(collection)

        

        return {'FINISHED'}
        

class VIEW3D_OT_add_point_sun(Operator):
    """Add Sun Light"""
    bl_label = "Add Sun Light"
    bl_options = {'REGISTER', 'UNDO'}
    bl_idname = "view3d.sun_light"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.object.light_add(type='SUN')
        return {'FINISHED'}


def createLibraryScene(context):
    if "Library" not in bpy.data.scenes.keys():
        currentScene = bpy.context.scene
        bpy.ops.scene.new(type='NEW')
        context.scene.name = "Library"        
        context.window.scene = currentScene


class VIEW3D_OT_group(bpy.types.Operator):
    """Create a collection with selected objects in Library"""
    bl_idname = "view3d.group"
    bl_label = "Convert to Library Group"
    bl_options = {'REGISTER', 'UNDO'}

    instname: bpy.props.StringProperty(name="Instance Name", default="Group")
    instance_center: bpy.props.EnumProperty(
        name='Center of Instance',
        items={
            ('WORLD', 'World', 'Center of world coordinates'),
            ('MEDIAN', 'Median Point', 'Median of object origins'),
            # ('BOX', 'Bounding Box Center', 'Center of bounding box'),
            ('CURSOR', '3D Cursor', '3D cursor coordinates'),
            ('ACTIVE', 'Active Object', 'Active object orign')},
        default='MEDIAN')

    def createLibraryInstance(context, instname, instance_center):
        # create a scene Library, if it doesn't exisists
        createLibraryScene(context)

        library = bpy.data.scenes['Library']

        # Create a collection with given name
        collection = bpy.data.collections.new(name=instname)
        collection.protect = True
        library.collection.children.link(collection)

        # find center of collection
        collection_loc = mathutils.Vector((0, 0, 0))

        if instance_center == 'ACTIVE':
            collection_loc += context.active_object.matrix_world.translation

        if instance_center == 'CURSOR':
            collection_loc = context.scene.cursor.location

        if instance_center == 'MEDIAN':
            for obj in context.selected_objects:
                collection_loc += obj.matrix_world.translation
            collection_loc = collection_loc / len(context.selected_objects)
            
        if(context.scene == library):    
            context.view_layer.layer_collection.children[collection.name].exclude=True
        
        # set new location for root objects
        for obj in context.selected_objects:            
            if obj.parent not in context.selected_objects:
                obj.parent = None
                current_loc = obj.matrix_world.translation
                obj.matrix_world.translation = current_loc - collection_loc
            
        # move object to new collection    
        for obj in context.selected_objects:   
            collection.objects.link(obj)
            for col in obj.users_collection:
                if col!=collection:
                    col.objects.unlink(obj)       
        
        bpy.ops.object.collection_instance_add(collection=collection.name, align="WORLD", location=collection_loc)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        VIEW3D_OT_group.createLibraryInstance(context, self.instname, self.instance_center)
        return {'FINISHED'}


class VIEW3D_OT_ungroup(bpy.types.Operator):
    """Ungroup instanced collection and remove it from Library"""
    bl_idname = "view3d.ungroup"
    bl_label = "Ungroup Instanced Collection"
    bl_options = {'REGISTER', 'UNDO'}

    removefromlib: bpy.props.BoolProperty(name="Remove from Library Scene", default=True)

    def getLibraryInstances(objects, skiplibrarycheck):
        list_objects = []
        
        for obj in objects:
            if obj.type != 'EMPTY':
                continue
            if obj.instance_collection is None:
                continue
            if obj.instance_type != 'COLLECTION':
                continue
            if skiplibrarycheck:
                list_objects.append(obj)
                continue
            if "Library" not in bpy.data.scenes.keys():
                continue
            library = bpy.data.scenes["Library"]
            if obj.instance_collection.name not in library.collection.children:
                continue
            if library.collection.children[obj.instance_collection.name] != obj.instance_collection:
                continue
            list_objects.append(obj)
            # for sub_obj in obj.instance_collection.objects:
            #     if sub_obj.type == 'EMPTY' and sub_obj.instance_collection is not None:
            #         list_objects.append(sub_obj)

        return list_objects

    def ungroupLibraryInstance(s, context, removefromlib):
        objs = bpy.data.objects
        listremove_collections = []

        createLibraryScene(context)
        
        listremove_objects = VIEW3D_OT_ungroup.getLibraryInstances(context.selected_objects, False)

        if len(listremove_objects) == 0:
            s.report({'ERROR'}, "Selected objects is not instances or instances are not from Library scene")
            return False

        for obj in listremove_objects:
            if len(obj.instance_collection.users_dupli_group) <= 1:
                listremove_collections.append(obj.instance_collection)

        bpy.ops.object.duplicates_make_real(
            {'selected_objects': listremove_objects, 'active_object': listremove_objects[0]},
            keep_animdata=True
            )

        for obj in listremove_objects:
            objs.remove(obj)

        if removefromlib:
            cols = bpy.data.collections
            for col in listremove_collections:
                for obj in col.objects:
                    objs.remove(obj)
                cols.remove(col)


    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        VIEW3D_OT_ungroup.ungroupLibraryInstance(self, context, self.removefromlib)
        return {'FINISHED'}
    
class VIEW3D_OT_view_from(bpy.types.Operator):
    """Toggle view from camera"""

    bl_idname = "view3d.view_from"
    bl_label = "Toggle view from camera"
    bl_options = {'REGISTER', 'UNDO'}
    
    camera_name: bpy.props.StringProperty(name="Camera", default="")

    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):
        camera_name = self.camera_name
        if not camera_name:
            return { 'CANCELLED' }
        
        camera_obj = bpy.data.objects.get(camera_name, None)
        if camera_obj is None:
            return { 'CANCELLED' }

        if camera_obj.type != "CAMERA":
            return { 'CANCELLED' }

        current_obj = bpy.context.active_object
        bpy.context.view_layer.objects.active = camera_obj
        bpy.ops.view3d.object_as_camera("INVOKE_DEFAULT")
        bpy.context.view_layer.objects.active = current_obj

        return {'FINISHED'}
        
classes = (
    VIEW3D_OT_collection_delete,
    VIEW3D_OT_group,
    VIEW3D_OT_ungroup,
    VIEW3D_OT_find,
    VIEW3D_OT_render,
    VIEW3D_OT_render_animation,
    VIEW3D_OT_material,
    VIEW3D_OT_pro_material,
    VIEW3D_OT_add_point_light,
    VIEW3D_OT_add_point_sun,
    VIEW3D_OT_edit_mesh_extrude_individual_move,
    VIEW3D_OT_edit_mesh_extrude_move,
    VIEW3D_OT_edit_mesh_extrude_shrink_fatten,
    VIEW3D_OT_edit_mesh_extrude_manifold_normal,
    VIEW3D_OT_transform_gizmo_set,
    VIEW3D_OT_view_from,
    # VIEW3D_OT_vr_hands,
)
