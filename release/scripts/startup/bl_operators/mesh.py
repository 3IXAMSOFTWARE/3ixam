# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
from bpy_extras import object_utils
from bpy.types import (
        Operator,
        Menu,
        Panel,
        PropertyGroup,
        )
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        StringProperty,
        PointerProperty,
        )
from mathutils import (
        Vector,
        Matrix,
        )
from math import (
        sin, asin, sqrt,
        acos, cos, pi,
        radians, tan,
        hypot,
        )
from bpy.app.translations import pgettext_tip as tip_


class MeshMirrorUV(Operator):
    """Copy mirror UV coordinates on the X axis based on a mirrored mesh"""
    bl_idname = "mesh.faces_mirror_uv"
    bl_label = "Copy Mirrored UV Coords"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    direction: EnumProperty(
        name="Axis Direction",
        items=(
            ('POSITIVE', "Positive", ""),
            ('NEGATIVE', "Negative", ""),
        ),
    )

    precision: IntProperty(
        name="Precision",
        description=("Tolerance for finding vertex duplicates"),
        min=1, max=16,
        soft_min=1, soft_max=16,
        default=3,
    )

    # Returns has_active_UV_layer, double_warn.
    def do_mesh_mirror_UV(self, mesh, DIR):
        precision = self.precision
        double_warn = 0

        if not mesh.uv_layers.active:
            # has_active_UV_layer, double_warn
            return False, 0

        # mirror lookups
        mirror_gt = {}
        mirror_lt = {}

        vcos = (v.co.to_tuple(precision) for v in mesh.vertices)

        for i, co in enumerate(vcos):
            if co[0] >= 0.0:
                double_warn += co in mirror_gt
                mirror_gt[co] = i
            if co[0] <= 0.0:
                double_warn += co in mirror_lt
                mirror_lt[co] = i

        vmap = {}
        for mirror_a, mirror_b in ((mirror_gt, mirror_lt),
                                   (mirror_lt, mirror_gt)):
            for co, i in mirror_a.items():
                nco = (-co[0], co[1], co[2])
                j = mirror_b.get(nco)
                if j is not None:
                    vmap[i] = j

        polys = mesh.polygons
        loops = mesh.loops
        uv_loops = mesh.uv_layers.active.data
        nbr_polys = len(polys)

        mirror_pm = {}
        pmap = {}
        puvs = [None] * nbr_polys
        puvs_cpy = [None] * nbr_polys
        puvsel = [None] * nbr_polys
        pcents = [None] * nbr_polys
        vidxs = [None] * nbr_polys
        for i, p in enumerate(polys):
            lstart = lend = p.loop_start
            lend += p.loop_total
            puvs[i] = tuple(uv.uv for uv in uv_loops[lstart:lend])
            puvs_cpy[i] = tuple(uv.copy() for uv in puvs[i])
            puvsel[i] = (False not in
                         (uv.select for uv in uv_loops[lstart:lend]))
            # Vert idx of the poly.
            vidxs[i] = tuple(l.vertex_index for l in loops[lstart:lend])
            pcents[i] = p.center
            # Preparing next step finding matching polys.
            mirror_pm[tuple(sorted(vidxs[i]))] = i

        for i in range(nbr_polys):
            # Find matching mirror poly.
            tvidxs = [vmap.get(j) for j in vidxs[i]]
            if None not in tvidxs:
                tvidxs.sort()
                j = mirror_pm.get(tuple(tvidxs))
                if j is not None:
                    pmap[i] = j

        for i, j in pmap.items():
            if not puvsel[i] or not puvsel[j]:
                continue
            elif DIR == 0 and pcents[i][0] < 0.0:
                continue
            elif DIR == 1 and pcents[i][0] > 0.0:
                continue

            # copy UVs
            uv1 = puvs[i]
            uv2 = puvs_cpy[j]

            # get the correct rotation
            v1 = vidxs[j]
            v2 = tuple(vmap[k] for k in vidxs[i])

            if len(v1) == len(v2):
                for k in range(len(v1)):
                    k_map = v1.index(v2[k])
                    uv1[k].xy = - (uv2[k_map].x - 0.5) + 0.5, uv2[k_map].y

        # has_active_UV_layer, double_warn
        return True, double_warn

    @classmethod
    def poll(cls, context):
        obj = context.view_layer.objects.active
        return (obj and obj.type == 'MESH')

    def execute(self, context):
        DIR = (self.direction == 'NEGATIVE')

        total_no_active_UV = 0
        total_duplicates = 0
        meshes_with_duplicates = 0

        ob = context.view_layer.objects.active
        is_editmode = (ob.mode == 'EDIT')
        if is_editmode:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        meshes = [ob.data for ob in context.view_layer.objects.selected
                  if ob.type == 'MESH' and ob.data.library is None]

        for mesh in meshes:
            mesh.tag = False

        for mesh in meshes:
            if mesh.tag:
                continue

            mesh.tag = True

            has_active_UV_layer, double_warn = self.do_mesh_mirror_UV(mesh, DIR)

            if not has_active_UV_layer:
                total_no_active_UV = total_no_active_UV + 1

            elif double_warn:
                total_duplicates += double_warn
                meshes_with_duplicates = meshes_with_duplicates + 1

        if is_editmode:
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        if total_duplicates and total_no_active_UV:
            self.report({'WARNING'},
                        tip_("%d mesh(es) with no active UV layer, "
                             "%d duplicates found in %d mesh(es), mirror may be incomplete")
                        % (total_no_active_UV,
                           total_duplicates,
                           meshes_with_duplicates))
        elif total_no_active_UV:
            self.report({'WARNING'},
                        tip_("%d mesh(es) with no active UV layer")
                        % (total_no_active_UV,))
        elif total_duplicates:
            self.report({'WARNING'},
                        tip_("%d duplicates found in %d mesh(es), mirror may be incomplete")
                        % (total_duplicates, meshes_with_duplicates))

        return {'FINISHED'}


class MeshSelectNext(Operator):
    """Select the next element (using selection order)"""
    bl_idname = "mesh.select_next_item"
    bl_label = "Select Next Element"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        import bmesh
        from .bmesh import find_adjacent

        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        if find_adjacent.select_next(bm, self.report):
            bm.select_flush_mode()
            bmesh.update_edit_mesh(me, loop_triangles=False)

        return {'FINISHED'}


class MeshSelectPrev(Operator):
    """Select the previous element (using selection order)"""
    bl_idname = "mesh.select_prev_item"
    bl_label = "Select Previous Element"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        import bmesh
        from .bmesh import find_adjacent

        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        if find_adjacent.select_prev(bm, self.report):
            bm.select_flush_mode()
            bmesh.update_edit_mesh(me, loop_triangles=False)


class AddSingleVert(Operator):
    bl_idname = "mesh.primitive_single_vert_add"
    bl_label = "Single Vert"
    bl_description = "Add a Single Vertice"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mesh = bpy.data.meshes.new("Vert")
        mesh.vertices.add(1)

        return {'FINISHED'}

# ------------------------------------------------------------
# Point:

def SimplePoint():
    newpoints = []

    newpoints.append([0.0, 0.0, 0.0])

    return newpoints


# ------------------------------------------------------------
# Line:

def SimpleLine(c1=[0.0, 0.0, 0.0], c2=[2.0, 2.0, 2.0]):
    newpoints = []

    c3 = Vector(c2) - Vector(c1)
    newpoints.append([0.0, 0.0, 0.0])
    newpoints.append([c3[0], c3[1], c3[2]])

    return newpoints


# ------------------------------------------------------------
# Angle:

def SimpleAngle(length=1.0, angle=45.0):
    newpoints = []

    angle = radians(angle)
    newpoints.append([length, 0.0, 0.0])
    newpoints.append([0.0, 0.0, 0.0])
    newpoints.append([length * cos(angle), length * sin(angle), 0.0])

    return newpoints


# ------------------------------------------------------------
# Distance:

def SimpleDistance(length=1.0, center=True):
    newpoints = []

    if center:
        newpoints.append([-length / 2, 0.0, 0.0])
        newpoints.append([length / 2, 0.0, 0.0])
    else:
        newpoints.append([0.0, 0.0, 0.0])
        newpoints.append([length, 0.0, 0.0])

    return newpoints


# ------------------------------------------------------------
# Circle:

def SimpleCircle(sides=4, radius=1.0):
    newpoints = []

    angle = radians(360) / sides
    newpoints.append([radius, 0, 0])
    if radius != 0 :
        j = 1
        while j < sides:
            t = angle * j
            x = cos(t) * radius
            y = sin(t) * radius
            newpoints.append([x, y, 0])
            j += 1

    return newpoints


# ------------------------------------------------------------
# Ellipse:

def SimpleEllipse(a=2.0, b=1.0):
    newpoints = []

    newpoints.append([a, 0.0, 0.0])
    newpoints.append([0.0, b, 0.0])
    newpoints.append([-a, 0.0, 0.0])
    newpoints.append([0.0, -b, 0.0])

    return newpoints


# ------------------------------------------------------------
# Arc:

def SimpleArc(sides=0, radius=1.0, startangle=0.0, endangle=45.0):
    newpoints = []

    startangle = radians(startangle)
    endangle = radians(endangle)
    sides += 1

    angle = (endangle - startangle) / sides
    x = cos(startangle) * radius
    y = sin(startangle) * radius
    newpoints.append([x, y, 0])
    j = 1
    while j < sides:
        t = angle * j
        x = cos(t + startangle) * radius
        y = sin(t + startangle) * radius
        newpoints.append([x, y, 0])
        j += 1
    x = cos(endangle) * radius
    y = sin(endangle) * radius
    newpoints.append([x, y, 0])

    return newpoints


# ------------------------------------------------------------
# Sector:

def SimpleSector(sides=0, radius=1.0, startangle=0.0, endangle=45.0):
    newpoints = []

    startangle = radians(startangle)
    endangle = radians(endangle)
    sides += 1

    newpoints.append([0, 0, 0])
    angle = (endangle - startangle) / sides
    x = cos(startangle) * radius
    y = sin(startangle) * radius
    newpoints.append([x, y, 0])
    j = 1
    while j < sides:
        t = angle * j
        x = cos(t + startangle) * radius
        y = sin(t + startangle) * radius
        newpoints.append([x, y, 0])
        j += 1
    x = cos(endangle) * radius
    y = sin(endangle) * radius
    newpoints.append([x, y, 0])

    return newpoints


# ------------------------------------------------------------
# Segment:

def SimpleSegment(sides=0, a=2.0, b=1.0, startangle=0.0, endangle=45.0):
    newpoints = []

    startangle = radians(startangle)
    endangle = radians(endangle)
    sides += 1

    angle = (endangle - startangle) / sides
    x = cos(startangle) * a
    y = sin(startangle) * a
    newpoints.append([x, y, 0])
    j = 1
    while j < sides:
        t = angle * j
        x = cos(t + startangle) * a
        y = sin(t + startangle) * a
        newpoints.append([x, y, 0])
        j += 1
    x = cos(endangle) * a
    y = sin(endangle) * a
    newpoints.append([x, y, 0])

    x = cos(endangle) * b
    y = sin(endangle) * b
    newpoints.append([x, y, 0])
    j = sides - 1
    while j > 0:
        t = angle * j
        x = cos(t + startangle) * b
        y = sin(t + startangle) * b
        newpoints.append([x, y, 0])
        j -= 1
    x = cos(startangle) * b
    y = sin(startangle) * b
    newpoints.append([x, y, 0])

    return newpoints


# ------------------------------------------------------------
# Rectangle:

def SimpleRectangle(width=2.0, length=2.0, rounded=0.0, center=True):
    newpoints = []

    r = rounded / 2

    if center:
        x = width / 2
        y = length / 2
        if rounded != 0.0:
            newpoints.append([-x + r, y, 0.0])
            newpoints.append([x - r, y, 0.0])
            newpoints.append([x, y - r, 0.0])
            newpoints.append([x, -y + r, 0.0])
            newpoints.append([x - r, -y, 0.0])
            newpoints.append([-x + r, -y, 0.0])
            newpoints.append([-x, -y + r, 0.0])
            newpoints.append([-x, y - r, 0.0])
        else:
            newpoints.append([-x, y, 0.0])
            newpoints.append([x, y, 0.0])
            newpoints.append([x, -y, 0.0])
            newpoints.append([-x, -y, 0.0])

    else:
        x = width
        y = length
        if rounded != 0.0:
            newpoints.append([r, y, 0.0])
            newpoints.append([x - r, y, 0.0])
            newpoints.append([x, y - r, 0.0])
            newpoints.append([x, r, 0.0])
            newpoints.append([x - r, 0.0, 0.0])
            newpoints.append([r, 0.0, 0.0])
            newpoints.append([0.0, r, 0.0])
            newpoints.append([0.0, y - r, 0.0])
        else:
            newpoints.append([0.0, 0.0, 0.0])
            newpoints.append([0.0, y, 0.0])
            newpoints.append([x, y, 0.0])
            newpoints.append([x, 0.0, 0.0])

    return newpoints


# ------------------------------------------------------------
# Rhomb:

def SimpleRhomb(width=2.0, length=2.0, center=True):
    newpoints = []
    x = width / 2
    y = length / 2

    if center:
        newpoints.append([-x, 0.0, 0.0])
        newpoints.append([0.0, y, 0.0])
        newpoints.append([x, 0.0, 0.0])
        newpoints.append([0.0, -y, 0.0])
    else:
        newpoints.append([x, 0.0, 0.0])
        newpoints.append([0.0, y, 0.0])
        newpoints.append([x, length, 0.0])
        newpoints.append([width, y, 0.0])

    return newpoints


# ------------------------------------------------------------
# Polygon:

def SimplePolygon(sides=3, radius=1.0):
    newpoints = []
    angle = radians(360.0) / sides
    j = 0

    while j < sides:
        t = angle * j
        x = sin(t) * radius
        y = cos(t) * radius
        newpoints.append([x, y, 0.0])
        j += 1

    return newpoints


# ------------------------------------------------------------
# Polygon_ab:

def SimplePolygon_ab(sides=3, a=2.0, b=1.0):
    newpoints = []
    angle = radians(360.0) / sides
    j = 0

    while j < sides:
        t = angle * j
        x = sin(t) * a
        y = cos(t) * b
        newpoints.append([x, y, 0.0])
        j += 1

    return newpoints


# ------------------------------------------------------------
# Trapezoid:

def SimpleTrapezoid(a=2.0, b=1.0, h=1.0, center=True):
    newpoints = []
    x = a / 2
    y = b / 2
    r = h / 2

    if center:
        newpoints.append([-x, -r, 0.0])
        newpoints.append([-y, r, 0.0])
        newpoints.append([y, r, 0.0])
        newpoints.append([x, -r, 0.0])

    else:
        newpoints.append([0.0, 0.0, 0.0])
        newpoints.append([x - y, h, 0.0])
        newpoints.append([x + y, h, 0.0])
        newpoints.append([a, 0.0, 0.0])

    return newpoints


# ------------------------------------------------------------
# calculates the matrix for the new object
# depending on user pref

def align_matrix(context, location):
    loc = Matrix.Translation(location)
    obj_align = context.preferences.edit.object_align
    if (context.space_data.type == 'VIEW_3D' and
            obj_align == 'VIEW'):
        rot = context.space_data.region_3d.view_matrix.to_3x3().inverted().to_4x4()
    else:
        rot = Matrix()
    align_matrix = loc @ rot

    return align_matrix

# ------------------------------------------------------------
# get array of vertcoordinates according to splinetype
def vertsToPoints(Verts, splineType):

    # main vars
    vertArray = []

    # array for BEZIER spline output (V3)
    if splineType == 'BEZIER':
        for v in Verts:
            vertArray += v

    # array for nonBEZIER output (V4)
    else:
        for v in Verts:
            vertArray += v
            if splineType == 'NURBS':
                # for nurbs w=1
                vertArray.append(1)
            else:
                # for poly w=0
                vertArray.append(0)
    return vertArray


# ------------------------------------------------------------
# Main Function

def main(context, self, align_matrix, use_enter_edit_mode):
    # output splineType 'POLY' 'NURBS' 'BEZIER'
    splineType = self.outputType
    
    sides = abs(int((self.Simple_endangle - self.Simple_startangle) / 90))

    # get verts
    if self.Simple_Type == 'Point':
        verts = SimplePoint()

    if self.Simple_Type == 'Line':
        verts = SimpleLine(self.Simple_startlocation, self.Simple_endlocation)

    if self.Simple_Type == 'Distance':
        verts = SimpleDistance(self.Simple_length, self.Simple_center)

    if self.Simple_Type == 'Angle':
        verts = SimpleAngle(self.Simple_length, self.Simple_angle)

    if self.Simple_Type == 'Circle':
        if self.Simple_sides < 4:
            self.Simple_sides = 4
        if self.Simple_radius == 0:
            return {'FINISHED'}
        verts = SimpleCircle(self.Simple_sides, self.Simple_radius)

    if self.Simple_Type == 'Ellipse':
        verts = SimpleEllipse(self.Simple_a, self.Simple_b)

    if self.Simple_Type == 'Arc':
        if self.Simple_sides < sides:
            self.Simple_sides = sides
        if self.Simple_radius == 0:
            return {'FINISHED'}
        verts = SimpleArc(
                    self.Simple_sides, self.Simple_radius,
                    self.Simple_startangle, self.Simple_endangle
                    )

    if self.Simple_Type == 'Sector':
        if self.Simple_sides < sides:
            self.Simple_sides = sides
        if self.Simple_radius == 0:
            return {'FINISHED'}
        verts = SimpleSector(
                    self.Simple_sides, self.Simple_radius,
                    self.Simple_startangle, self.Simple_endangle
                    )

    if self.Simple_Type == 'Segment':
        if self.Simple_sides < sides:
            self.Simple_sides = sides
        if self.Simple_a == 0 or self.Simple_b == 0 or self.Simple_a == self.Simple_b:
            return {'FINISHED'}
        if self.Simple_a > self.Simple_b:
            verts = SimpleSegment(
                    self.Simple_sides, self.Simple_a, self.Simple_b,
                    self.Simple_startangle, self.Simple_endangle
                    )
        if self.Simple_a < self.Simple_b:
            verts = SimpleSegment(
                    self.Simple_sides, self.Simple_b, self.Simple_a,
                    self.Simple_startangle, self.Simple_endangle
                    )

    if self.Simple_Type == 'Rectangle':
        verts = SimpleRectangle(
                    self.Simple_width, self.Simple_length,
                    self.Simple_rounded, self.Simple_center
                    )

    if self.Simple_Type == 'Rhomb':
        verts = SimpleRhomb(
                    self.Simple_width, self.Simple_length, self.Simple_center
                    )

    if self.Simple_Type == 'Polygon':
        if self.Simple_sides < 3:
            self.Simple_sides = 3
        verts = SimplePolygon(
                    self.Simple_sides, self.Simple_radius
                    )

    if self.Simple_Type == 'Polygon_ab':
        if self.Simple_sides < 3:
            self.Simple_sides = 3
        verts = SimplePolygon_ab(
                    self.Simple_sides, self.Simple_a, self.Simple_b
                    )

    if self.Simple_Type == 'Trapezoid':
        verts = SimpleTrapezoid(
                    self.Simple_a, self.Simple_b, self.Simple_h, self.Simple_center
                    )
    
    # turn verts into array
    vertArray = vertsToPoints(verts, splineType)
    
    # create object
    if bpy.context.mode == 'EDIT_CURVE':
        Curve = context.active_object
        newSpline = Curve.data.splines.new(type=splineType)          # spline
    else:
        name = self.Simple_Type  # Type as name
    
        dataCurve = bpy.data.curves.new(name, type='CURVE')  # curve data block
        newSpline = dataCurve.splines.new(type=splineType)          # spline

        # create object with new Curve
        Curve = object_utils.object_data_add(context, dataCurve, operator=self)  # place in active scene
        Curve.matrix_world = align_matrix  # apply matrix
        Curve.rotation_euler = self.Simple_rotation_euler
        Curve.select_set(True)
    
    for spline in Curve.data.splines:
        if spline.type == 'BEZIER':
            for point in spline.bezier_points:
                point.select_control_point = False
                point.select_left_handle = False
                point.select_right_handle = False
        else:
            for point in spline.points:
                point.select = False
    
    # create spline from vertarray
    all_points = []
    if splineType == 'BEZIER':
        newSpline.bezier_points.add(int(len(vertArray) * 0.33))
        newSpline.bezier_points.foreach_set('co', vertArray)
        for point in newSpline.bezier_points:
            point.handle_right_type = self.handleType
            point.handle_left_type = self.handleType
            point.select_control_point = True
            point.select_left_handle = True
            point.select_right_handle = True
            all_points.append(point)
    else:
        newSpline.points.add(int(len(vertArray) * 0.25 - 1))
        newSpline.points.foreach_set('co', vertArray)
        newSpline.use_endpoint_u = True
        for point in newSpline.points:
            all_points.append(point)
            point.select = True
    
    n = len(all_points)

    d = 2 * 0.27606262

    if splineType == 'BEZIER':
        if self.Simple_Type == 'Circle' or self.Simple_Type == 'Arc' or \
           self.Simple_Type == 'Sector' or self.Simple_Type == 'Segment' or \
           self.Simple_Type == 'Ellipse':

            for p in all_points:
                p.handle_right_type = 'FREE'
                p.handle_left_type = 'FREE'

        if self.Simple_Type == 'Circle':
            i = 0
            for p1 in all_points:
                if i != (n - 1):
                    p2 = all_points[i + 1]
                    u1 = asin(p1.co.y / self.Simple_radius)
                    u2 = asin(p2.co.y / self.Simple_radius)
                    if p1.co.x > 0 and p2.co.x < 0:
                        u1 = acos(p1.co.x / self.Simple_radius)
                        u2 = acos(p2.co.x / self.Simple_radius)
                    elif p1.co.x < 0 and p2.co.x > 0:
                        u1 = acos(p1.co.x / self.Simple_radius)
                        u2 = acos(p2.co.x / self.Simple_radius)
                    u = u2 - u1
                    if u < 0:
                        u = -u
                    l = 4 / 3 * tan(1 / 4 * u) * self.Simple_radius
                    v1 = Vector((-p1.co.y, p1.co.x, 0))
                    v1.normalize()
                    v2 = Vector((-p2.co.y, p2.co.x, 0))
                    v2.normalize()
                    vh1 = v1 * l
                    vh2 = v2 * l
                    v1 = Vector((p1.co.x, p1.co.y, 0)) + vh1
                    v2 = Vector((p2.co.x, p2.co.y, 0)) - vh2
                    p1.handle_right = v1
                    p2.handle_left = v2
                if i == (n - 1):
                    p2 = all_points[0]
                    u1 = asin(p1.co.y / self.Simple_radius)
                    u2 = asin(p2.co.y / self.Simple_radius)
                    if p1.co.x > 0 and p2.co.x < 0:
                        u1 = acos(p1.co.x / self.Simple_radius)
                        u2 = acos(p2.co.x / self.Simple_radius)
                    elif p1.co.x < 0 and p2.co.x > 0:
                        u1 = acos(p1.co.x / self.Simple_radius)
                        u2 = acos(p2.co.x / self.Simple_radius)
                    u = u2 - u1
                    if u < 0:
                        u = -u
                    l = 4 / 3 * tan(1 / 4 * u) * self.Simple_radius
                    v1 = Vector((-p1.co.y, p1.co.x, 0))
                    v1.normalize()
                    v2 = Vector((-p2.co.y, p2.co.x, 0))
                    v2.normalize()
                    vh1 = v1 * l
                    vh2 = v2 * l
                    v1 = Vector((p1.co.x, p1.co.y, 0)) + vh1
                    v2 = Vector((p2.co.x, p2.co.y, 0)) - vh2
                    p1.handle_right = v1
                    p2.handle_left = v2
                i += 1
    
        if self.Simple_Type == 'Ellipse':
            all_points[0].handle_right = Vector((self.Simple_a, self.Simple_b * d, 0))
            all_points[0].handle_left = Vector((self.Simple_a, -self.Simple_b * d, 0))
            all_points[1].handle_right = Vector((-self.Simple_a * d, self.Simple_b, 0))
            all_points[1].handle_left = Vector((self.Simple_a * d, self.Simple_b, 0))
            all_points[2].handle_right = Vector((-self.Simple_a, -self.Simple_b * d, 0))
            all_points[2].handle_left = Vector((-self.Simple_a, self.Simple_b * d, 0))
            all_points[3].handle_right = Vector((self.Simple_a * d, -self.Simple_b, 0))
            all_points[3].handle_left = Vector((-self.Simple_a * d, -self.Simple_b, 0))
    
        if self.Simple_Type == 'Arc':
            i = 0
            for p1 in all_points:
                if i != (n - 1):
                    p2 = all_points[i + 1]
                    u1 = asin(p1.co.y / self.Simple_radius)
                    u2 = asin(p2.co.y / self.Simple_radius)
                    if p1.co.x > 0 and p2.co.x < 0:
                        u1 = acos(p1.co.x / self.Simple_radius)
                        u2 = acos(p2.co.x / self.Simple_radius)
                    elif p1.co.x < 0 and p2.co.x > 0:
                        u1 = acos(p1.co.x / self.Simple_radius)
                        u2 = acos(p2.co.x / self.Simple_radius)
                    u = u2 - u1
                    if u < 0:
                        u = -u
                    l = 4 / 3 * tan(1 / 4 * u) * self.Simple_radius
                    v1 = Vector((-p1.co.y, p1.co.x, 0))
                    v1.normalize()
                    v2 = Vector((-p2.co.y, p2.co.x, 0))
                    v2.normalize()
                    vh1 = v1 * l
                    vh2 = v2 * l
                    if self.Simple_startangle < self.Simple_endangle:
                        v1 = Vector((p1.co.x, p1.co.y, 0)) + vh1
                        v2 = Vector((p2.co.x, p2.co.y, 0)) - vh2
                        p1.handle_right = v1
                        p2.handle_left = v2
                    else:
                        v1 = Vector((p1.co.x, p1.co.y, 0)) - vh1
                        v2 = Vector((p2.co.x, p2.co.y, 0)) + vh2
                        p1.handle_right = v1
                        p2.handle_left = v2
                i += 1
            all_points[0].handle_left_type = 'VECTOR'
            all_points[-1].handle_right_type = 'VECTOR'
    
        if self.Simple_Type == 'Sector':
            i = 0
            for p1 in all_points:
                if i == 0:
                    p1.handle_right_type = 'VECTOR'
                    p1.handle_left_type = 'VECTOR'
                elif i != (n - 1):
                    p2 = all_points[i + 1]
                    u1 = asin(p1.co.y / self.Simple_radius)
                    u2 = asin(p2.co.y / self.Simple_radius)
                    if p1.co.x > 0 and p2.co.x < 0:
                        u1 = acos(p1.co.x / self.Simple_radius)
                        u2 = acos(p2.co.x / self.Simple_radius)
                    elif p1.co.x < 0 and p2.co.x > 0:
                        u1 = acos(p1.co.x / self.Simple_radius)
                        u2 = acos(p2.co.x / self.Simple_radius)
                    u = u2 - u1
                    if u < 0:
                        u = -u
                    l = 4 / 3 * tan(1 / 4 * u) * self.Simple_radius
                    v1 = Vector((-p1.co.y, p1.co.x, 0))
                    v1.normalize()
                    v2 = Vector((-p2.co.y, p2.co.x, 0))
                    v2.normalize()
                    vh1 = v1 * l
                    vh2 = v2 * l
                    if self.Simple_startangle < self.Simple_endangle:
                        v1 = Vector((p1.co.x, p1.co.y, 0)) + vh1
                        v2 = Vector((p2.co.x, p2.co.y, 0)) - vh2
                        p1.handle_right = v1
                        p2.handle_left = v2
                    else:
                        v1 = Vector((p1.co.x, p1.co.y, 0)) - vh1
                        v2 = Vector((p2.co.x, p2.co.y, 0)) + vh2
                        p1.handle_right = v1
                        p2.handle_left = v2
                i += 1
            all_points[0].handle_left_type = 'VECTOR'
            all_points[0].handle_right_type = 'VECTOR'
            all_points[1].handle_left_type = 'VECTOR'
            all_points[-1].handle_right_type = 'VECTOR'
    
        if self.Simple_Type == 'Segment':
            i = 0
            if self.Simple_a > self.Simple_b:
                Segment_a = self.Simple_a
                Segment_b = self.Simple_b
            if self.Simple_a < self.Simple_b:
                Segment_b = self.Simple_a
                Segment_a = self.Simple_b
            for p1 in all_points:
                if i < (n / 2 - 1):
                    p2 = all_points[i + 1]
                    u1 = asin(p1.co.y / Segment_a)
                    u2 = asin(p2.co.y / Segment_a)
                    if p1.co.x > 0 and p2.co.x < 0:
                        u1 = acos(p1.co.x / Segment_a)
                        u2 = acos(p2.co.x / Segment_a)
                    elif p1.co.x < 0 and p2.co.x > 0:
                        u1 = acos(p1.co.x / Segment_a)
                        u2 = acos(p2.co.x / Segment_a)
                    u = u2 - u1
                    if u < 0:
                        u = -u
                    l = 4 / 3 * tan(1 / 4 * u) * Segment_a
                    v1 = Vector((-p1.co.y, p1.co.x, 0))
                    v1.normalize()
                    v2 = Vector((-p2.co.y, p2.co.x, 0))
                    v2.normalize()
                    vh1 = v1 * l
                    vh2 = v2 * l
                    if self.Simple_startangle < self.Simple_endangle:
                        v1 = Vector((p1.co.x, p1.co.y, 0)) + vh1
                        v2 = Vector((p2.co.x, p2.co.y, 0)) - vh2
                        p1.handle_right = v1
                        p2.handle_left = v2
                    else:
                        v1 = Vector((p1.co.x, p1.co.y, 0)) - vh1
                        v2 = Vector((p2.co.x, p2.co.y, 0)) + vh2
                        p1.handle_right = v1
                        p2.handle_left = v2
                elif i != (n / 2 - 1) and i != (n - 1):
                    p2 = all_points[i + 1]
                    u1 = asin(p1.co.y / Segment_b)
                    u2 = asin(p2.co.y / Segment_b)
                    if p1.co.x > 0 and p2.co.x < 0:
                        u1 = acos(p1.co.x / Segment_b)
                        u2 = acos(p2.co.x / Segment_b)
                    elif p1.co.x < 0 and p2.co.x > 0:
                        u1 = acos(p1.co.x / Segment_b)
                        u2 = acos(p2.co.x / Segment_b)
                    u = u2 - u1
                    if u < 0:
                        u = -u
                    l = 4 / 3 * tan(1 / 4 * u) * Segment_b
                    v1 = Vector((-p1.co.y, p1.co.x, 0))
                    v1.normalize()
                    v2 = Vector((-p2.co.y, p2.co.x, 0))
                    v2.normalize()
                    vh1 = v1 * l
                    vh2 = v2 * l
                    if self.Simple_startangle < self.Simple_endangle:
                        v1 = Vector((p1.co.x, p1.co.y, 0)) - vh1
                        v2 = Vector((p2.co.x, p2.co.y, 0)) + vh2
                        p1.handle_right = v1
                        p2.handle_left = v2
                    else:
                        v1 = Vector((p1.co.x, p1.co.y, 0)) + vh1
                        v2 = Vector((p2.co.x, p2.co.y, 0)) - vh2
                        p1.handle_right = v1
                        p2.handle_left = v2
    
                i += 1
            all_points[0].handle_left_type = 'VECTOR'
            all_points[n - 1].handle_right_type = 'VECTOR'
            all_points[int(n / 2) - 1].handle_right_type = 'VECTOR'
            all_points[int(n / 2)].handle_left_type = 'VECTOR'

    # move and rotate spline in edit mode
    if bpy.context.mode == 'EDIT_CURVE':
        bpy.ops.transform.translate(value = self.Simple_startlocation)
        bpy.ops.transform.rotate(value = self.Simple_rotation_euler[0], orient_axis = 'X')
        bpy.ops.transform.rotate(value = self.Simple_rotation_euler[1], orient_axis = 'Y')
        bpy.ops.transform.rotate(value = self.Simple_rotation_euler[2], orient_axis = 'Z')
    
    # set newSpline Options
    newSpline.use_cyclic_u = self.use_cyclic_u
    newSpline.use_endpoint_u = self.endp_u
    newSpline.order_u = self.order_u
    
    # set curve Options
    Curve.data.dimensions = self.shape
    Curve.data.use_path = True
    if self.shape == '3D':
        Curve.data.fill_mode = 'FULL'
    else:
        Curve.data.fill_mode = 'BOTH'

class Simple(Operator, object_utils.AddObjectHelper):
    bl_idname = "simple.add"
    bl_label = "Add simple primitive"
    bl_description = "Construct a Simple Primitive"
    bl_options = {'REGISTER', 'UNDO'}

    # align_matrix for the invoke
    align_matrix : Matrix()

    # change properties
    Simple : BoolProperty(
            name="Simple",
            default=True,
            description="Simple Curve"
            )
    Simple_Change : BoolProperty(
            name="Change",
            default=False,
            description="Change Simple Curve"
            )
    Simple_Delete : StringProperty(
            name="Delete",
            description="Delete Simple Curve"
            )
    # general properties
    Types = [('Point', "Point", "Construct a Point"),
             ('Line', "Line", "Construct a Line"),
             ('Distance', "Distance", "Construct a two point Distance"),
             ('Angle', "Angle", "Construct an Angle"),
             ('Circle', "Circle", "Construct a Circle"),
             ('Ellipse', "Ellipse", "Construct an Ellipse"),
             ('Arc', "Arc", "Construct an Arc"),
             ('Sector', "Sector", "Construct a Sector"),
             ('Segment', "Segment", "Construct a Segment"),
             ('Rectangle', "Rectangle", "Construct a Rectangle"),
             ('Rhomb', "Rhomb", "Construct a Rhomb"),
             ('Polygon', "Polygon", "Construct a Polygon"),
             ('Polygon_ab', "Polygon ab", "Construct a Polygon ab"),
             ('Trapezoid', "Trapezoid", "Construct a Trapezoid")
            ]
    Simple_Type : EnumProperty(
            name="Type",
            description="Form of Curve to create",
            items=Types
            )
    # Line properties
    Simple_startlocation : FloatVectorProperty(
            name="",
            description="Start location",
            default=(0.0, 0.0, 0.0),
            subtype='TRANSLATION'
            )
    Simple_endlocation : FloatVectorProperty(
            name="",
            description="End location",
            default=(2.0, 2.0, 0.0),
            subtype='TRANSLATION'
            )
    Simple_rotation_euler : FloatVectorProperty(
            name="",
            description="Rotation",
            default=(0.0, 0.0, 0.0),
            subtype='EULER'
            )
    # Trapezoid properties
    Simple_a : FloatProperty(
            name="Side a",
            default=2.0,
            min=0.0, soft_min=0.0,
            unit='LENGTH',
            description="a side Value"
            )
    Simple_b : FloatProperty(
            name="Side b",
            default=1.0,
            min=0.0, soft_min=0.0,
            unit='LENGTH',
            description="b side Value"
            )
    Simple_h : FloatProperty(
            name="Height",
            default=1.0,
            unit='LENGTH',
            description="Height of the Trapezoid - distance between a and b"
            )
    Simple_angle : FloatProperty(
            name="Angle",
            default=45.0,
            description="Angle"
            )
    Simple_startangle : FloatProperty(
            name="Start angle",
            default=0.0,
            min=-360.0, soft_min=-360.0,
            max=360.0, soft_max=360.0,
            description="Start angle"
            )
    Simple_endangle : FloatProperty(
            name="End angle",
            default=45.0,
            min=-360.0, soft_min=-360.0,
            max=360.0, soft_max=360.0,
            description="End angle"
            )
    Simple_sides : IntProperty(
            name="Sides",
            default=3,
            min=0, soft_min=0,
            description="Sides"
            )
    Simple_radius : FloatProperty(
            name="Radius",
            default=1.0,
            min=0.0, soft_min=0.0,
            unit='LENGTH',
            description="Radius"
            )
    Simple_center : BoolProperty(
            name="Length center",
            default=True,
            description="Length center"
            )

    Angle_types = [('Degrees', "Degrees", "Use Degrees"),
                   ('Radians', "Radians", "Use Radians")]
    Simple_degrees_or_radians : EnumProperty(
            name="Degrees or radians",
            description="Degrees or radians",
            items=Angle_types
            )
    # Rectangle properties
    Simple_width : FloatProperty(
            name="Width",
            default=2.0,
            min=0.0, soft_min=0,
            unit='LENGTH',
            description="Width"
            )
    Simple_length : FloatProperty(
            name="Length",
            default=2.0,
            min=0.0, soft_min=0.0,
            unit='LENGTH',
            description="Length"
            )
    Simple_rounded : FloatProperty(
            name="Rounded",
            default=0.0,
            min=0.0, soft_min=0.0,
            unit='LENGTH',
            description="Rounded corners"
            )
    # Curve Options
    shapeItems = [
        ('2D', "2D", "2D shape Curve"),
        ('3D', "3D", "3D shape Curve")]
    shape : EnumProperty(
            name="2D / 3D",
            items=shapeItems,
            description="2D or 3D Curve"
            )
    outputType : EnumProperty(
            name="Output splines",
            description="Type of splines to output",
            items=[
            ('POLY', "Poly", "Poly Spline type"),
            ('NURBS', "Nurbs", "Nurbs Spline type"),
            ('BEZIER', "Bezier", "Bezier Spline type")],
            default='BEZIER'
            )
    use_cyclic_u : BoolProperty(
            name="Cyclic",
            default=True,
            description="make curve closed"
            )
    endp_u : BoolProperty(
            name="Use endpoint u",
            default=True,
            description="stretch to endpoints"
            )
    order_u : IntProperty(
            name="Order u",
            default=4,
            min=2, soft_min=2,
            max=6, soft_max=6,
            description="Order of nurbs spline"
            )
    handleType : EnumProperty(
            name="Handle type",
            default='VECTOR',
            description="Bezier handles type",
            items=[
            ('VECTOR', "Vector", "Vector type Bezier handles"),
            ('AUTO', "Auto", "Automatic type Bezier handles")]
            )
    edit_mode : BoolProperty(
            name="Show in edit mode",
            default=True,
            description="Show in edit mode"
            )
    popover : BoolProperty(
            name="Show popover",
            default=True,
            description="Show in edit mode"
            )

    def draw(self, context):
        layout = self.layout

        # general options
        col = layout.column()

        if self.Simple_Type == 'Point':
            box = layout.box()
            col = box.column(align=True)
            col.label(text=self.Simple_Type + " Options:")
            col.prop(self, "Simple_startlocation")

        if self.Simple_Type == 'Line':
            box = layout.box()
            col = box.column(align=True)
            col.label(text=self.Simple_Type + " Options:")
            col.prop(self, "Simple_endlocation")

        if self.Simple_Type == 'Arc':
            box = layout.box()
            col = box.column(align=True)
            col.label(text=self.Simple_Type + " Options:")
            col.prop(self, "Simple_sides")
            col.prop(self, "Simple_radius")

            col = box.column(align=True)
            col.prop(self, "Simple_startangle")
            col.prop(self, "Simple_endangle")

        if self.Simple_Type == 'Circle':
            box = layout.box()
            col = box.column(align=True)
            col.label(text=self.Simple_Type + " Options:")
            col.prop(self, "Simple_sides")
            col.prop(self, "Simple_radius")

        if self.Simple_Type == 'Rectangle':
            box = layout.box()
            col = box.column(align=True)
            col.label(text=self.Simple_Type + " Options:")
            col.prop(self, "Simple_width")
            col.prop(self, "Simple_length")
            col.prop(self, "Simple_rounded")

            box.prop(self, "Simple_center")

        if self.Simple_Type == 'Polygon':
            box = layout.box()
            col = box.column(align=True)
            col.label(text=self.Simple_Type + " Options:")
            col.prop(self, "Simple_sides")
            col.prop(self, "Simple_radius")

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context): 
        # turn off 'Enter Edit Mode'
        bpy.context.preferences.edit.use_enter_edit_mode = False
        
        # main function
        self.align_matrix = align_matrix(context, self.Simple_startlocation)
        main(context, self, self.align_matrix, False)

        return {'FINISHED'}


classes = (
    Simple,
    MeshMirrorUV,
    MeshSelectNext,
    MeshSelectPrev,
    AddSingleVert,
)
