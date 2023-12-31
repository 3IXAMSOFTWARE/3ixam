# -*- coding:utf-8 -*-



# <pep8 compliant>

# ----------------------------------------------------------
# Author: Stephen Leger (s-leger)
#
# ----------------------------------------------------------
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
import bpy
import numpy as np
from math import sin, cos, atan2, pi
from mathutils import Vector, Matrix
from bpy_extras import view3d_utils, object_utils


# ------------------------------------------------------------------
# Define Gl Handle types
# ------------------------------------------------------------------


class DefaultColorScheme:
    """
        Font sizes and basic colour scheme
        default to this when not found in addon prefs
        Colors are FloatVectorProperty of size 4 and type COLOR_GAMMA
    """
    text_size = 14
    feedback_size_main = 16
    feedback_size_title = 14
    feedback_size_shortcut = 11
    feedback_colour_main = (0.95, 0.95, 0.95, 1.0)
    feedback_colour_key = (0.67, 0.67, 0.67, 1.0)
    feedback_colour_shortcut = (0.51, 0.51, 0.51, 1.0)
    feedback_shortcut_area = (0, 0.4, 0.6, 0.2)
    feedback_title_area = (0, 0.4, 0.6, 0.5)
    handle_colour_normal = (1.0, 1.0, 1.0, 1.0)
    handle_colour_hover = (1.0, 1.0, 0.0, 1.0)
    handle_colour_active = (1.0, 0.0, 0.0, 1.0)
    handle_colour_selected = (0.0, 0.0, 0.7, 1.0)
    handle_colour_inactive = (0.3, 0.3, 0.3, 1.0)


def get_prefs(context):
    global __name__
    try:
        addon_name = __name__.split('.')[0]
        prefs = context.preferences.addons[addon_name].preferences
    except:
        prefs = DefaultColorScheme
        pass
    return prefs


g_poly = None
g_image = None
g_line = None


line_vertSrc = '''
uniform mat4 ModelViewProjectionMatrix;

in vec2 pos;

void main()
{
	gl_Position = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);
}

'''

line_fragSrc = '''
uniform vec4 color;

out vec4 fragColor;

void main()
{
	fragColor = color;
}
'''

"""
# TESTS
_format = gpu.types.GPUVertFormat()
_pos_id = _format.attr_add(
            id="pos",
            comp_type="F32",
            len=2,
            fetch_mode="FLOAT")
coords = [(0,0), (200,100)]
vbo = gpu.types.GPUVertBuf(len=len(coords), format=_format)
"""


class GPU_Line:
    def __init__(self):
        # never call this in -b mode
        if bpy.app.background:
            return
        self._format = gpu.types.GPUVertFormat()
        self._pos_id = self._format.attr_add(
            id="pos",
            comp_type="F32",
            len=2,
            fetch_mode="FLOAT")
        self.shader = gpu.types.GPUShader(line_vertSrc, line_fragSrc)
        self.unif_color = self.shader.uniform_from_name("color")
        self.color = np.array([0.0, 0.0, 0.0, 1.0], 'f')

    def batch_line_strip_create(self, coords):
        vbo = gpu.types.GPUVertBuf(len=len(coords), format=self._format)
        vbo.attr_fill(id=self._pos_id, data=coords)
        batch_lines = gpu.types.GPUBatch(type="LINE_STRIP", buf=vbo)
        batch_lines.program_set(self.shader)
        return batch_lines

    def draw(self, color, list_verts_co):
        if list_verts_co:
            batch = self.batch_line_strip_create(list_verts_co)
            self.color[0:4] = color[0:4]
            self.shader.uniform_vector_float(self.unif_color, self.color, 4)
            batch.draw()
            del batch


class GPU_Poly:

    def __init__(self):
        if bpy.app.background:
            return
        self._format = gpu.types.GPUVertFormat()
        self._pos_id = self._format.attr_add(
            id="pos",
            comp_type="F32",
            len=2,
            fetch_mode="FLOAT")
        self.shader = gpu.types.GPUShader(line_vertSrc, line_fragSrc)
        self.unif_color = self.shader.uniform_from_name("color")
        self.color = np.array([0.0, 0.0, 0.0, 0.5], 'f')

    def batch_create(self, coords):
        vbo = gpu.types.GPUVertBuf(len=len(coords), format=self._format)
        vbo.attr_fill(id=self._pos_id, data=coords)
        batch = gpu.types.GPUBatch(type="TRI_FAN", buf=vbo)
        # batch.program_set(self.shader)
        # batch = batch_for_shader(self.shader, 'TRI_FAN', {"position": coords})
        return batch

    def draw(self, color, list_verts_co):
        if list_verts_co:
            self.shader.bind()
            batch = self.batch_create(list_verts_co)
            self.color[0:4] = color[0:4]
            self.shader.uniform_vector_float(self.unif_color, self.color, 4)
            batch.draw(self.shader)


class GPU_Image:
    uvs = [(0, 0), (1, 0), (0, 1), (1, 1)]
    indices = [(0, 1, 2), (2, 1, 3)]

    def __init__(self):
        if bpy.app.background:
            return
        self._format = gpu.types.GPUVertFormat()
        self._pos_id = self._format.attr_add(
            id="pos",
            comp_type="F32",
            len=2,
            fetch_mode="FLOAT")
        self.shader = gpu.shader.from_builtin('2D_IMAGE')

    def batch_create(self, coords):
        batch = batch_for_shader(self.shader, 'TRIS',
                                 {"pos": coords,
                                  "texCoord": self.uvs},
                                 indices=self.indices)
        return batch

    def draw(self, texture_id, list_verts_co):
        if list_verts_co:
            batch = self.batch_create(list_verts_co)

            # in case someone disabled it before
            bgl.glEnable(bgl.GL_TEXTURE_2D)

            # bind texture to image unit 0
            bgl.glActiveTexture(bgl.GL_TEXTURE0)
            bgl.glBindTexture(bgl.GL_TEXTURE_2D, texture_id)

            self.shader.bind()
            # tell shader to use the image that is bound to image unit 0
            self.shader.uniform_int("image", 0)
            batch.draw(self.shader)

            bgl.glDisable(bgl.GL_TEXTURE_2D)


class Gl():
    """
        handle 3d -> 2d gl drawing
        d : dimensions
            3 to convert pos from 3d
            2 to keep pos as 2d absolute screen position
    """

    def __init__(self,
                 d=3,
                 colour=(0.0, 0.0, 0.0, 1.0)):

        global g_poly, g_image, g_line

        if g_poly is None:
            g_poly = GPU_Poly()

        if g_image is None:
            g_image = GPU_Image()

        if g_line is None:
            g_line = GPU_Line()

        # nth dimensions of input coords 3=word coords 2=pixel screen coords
        self.d = d
        self.pos_2d = Vector((0, 0))
        self.colour_inactive = colour

    @property
    def colour(self):
        return self.colour_inactive

    def position_2d_from_coord(self, context, coord, render=False):
        """ coord given in local input coordsys
        """
        if self.d == 2:
            return Vector(coord)
        if render:
            return self.get_render_location(context, coord)
        region = context.region
        rv3d = context.region_data
        loc = view3d_utils.location_3d_to_region_2d(region, rv3d, coord, self.pos_2d)
        return Vector(loc)

    def get_render_location(self, context, coord):
        scene = context.scene
        co_2d = object_utils.world_to_camera_view(scene, scene.camera, coord)
        # Get pixel coords
        render_scale = scene.render.resolution_percentage / 100
        render_size = (int(scene.render.resolution_x * render_scale),
                       int(scene.render.resolution_y * render_scale))
        return Vector(round(co_2d.x * render_size[0]), round(co_2d.y * render_size[1]))


class GlText(Gl):

    def __init__(self,
                 d=3,
                 label="",
                 value=None,
                 precision=4,
                 unit_mode='AUTO',
                 unit_type='SIZE',
                 dimension=1,
                 angle=0,
                 font_size=None,
                 colour=(1, 1, 1, 1),
                 z_axis=Vector((0, 0, 1))):
        """
            d: [2|3] coords type: 2 for coords in screen pixels, 3 for 3d world location
            label : string label
            value : float value (will add unit according following settings)
            precision : integer rounding for values
            dimension : [1 - 3] nth dimension of unit (single, square, cubic)
            unit_mode : ['ADAPTIVE','METER','CENTIMETER','MILIMETER','FEET','INCH','RADIANS','DEGREE']
                        unit type to use to postfix values
                        ADAPTIVE use scene units setup
            unit_type : ['SIZE','ANGLE']
                        unit type to add to value
            angle : angle to rotate text

        """
        self.z_axis = z_axis
        # text, add as prefix to value
        self.label = label
        # value with unit related
        self.value = value
        self.precision = precision
        self.dimension = dimension
        self.unit_type = unit_type
        self.unit_mode = unit_mode
        if font_size is None:
            prefs = get_prefs(bpy.context)
            self.font_size = prefs.text_size
        else:
            self.font_size = font_size
        self.angle = angle
        Gl.__init__(self, d)
        self.colour_inactive = colour
        # store text with units
        self._text = ""
        self.cbuff = bgl.Buffer(bgl.GL_FLOAT, 4)

    def text_size(self, context):
        """
            overall on-screen size in pixels
        """
        dpi, font_id = context.preferences.system.dpi, 0
        if self.angle != 0:
            blf.enable(font_id, blf.ROTATION)
            blf.rotation(font_id, self.angle)
        blf.aspect(font_id, 1.0)
        blf.size(font_id, self.font_size, dpi)
        x, y = blf.dimensions(font_id, self.text)
        if self.angle != 0:
            blf.disable(font_id, blf.ROTATION)
        return Vector((x, y))

    @property
    def pts(self):
        return [self.pos_3d]

    @property
    def text(self):
        s = self.label + self._text
        return s.strip()

    def add_units(self, context):
        if self.value is None:
            return ""
        system = context.scene.unit_settings.system
        if self.unit_type == 'ANGLE':
            scale = 1
            mode = 'ADAPTIVE'
        else:
            scale = context.scene.unit_settings.scale_length
            mode = self.unit_mode
            if mode == 'AUTO':
                mode = context.scene.unit_settings.length_unit.upper()

        val = self.value * scale

        if mode == 'ADAPTIVE':
            if self.unit_type == 'ANGLE':
                mode = context.scene.unit_settings.system_rotation
            else:
                if system == "IMPERIAL":
                    if round(val * (3.2808399 ** self.dimension), 2) >= 1.0:
                        mode = 'FOOT'
                    else:
                        mode = 'INCH'
                elif context.scene.unit_settings.system == "METRIC":
                    if round(val, 2) >= 1.0:
                        mode = 'METER'
                    else:
                        if round(val, 2) >= 0.01:
                            mode = 'CENTIMETER'
                        else:
                            mode = 'MILIMETER'

        # TODO: support for separate units (through 2.8 api)
        # convert values
        unit = ""
        if mode == 'METER':
            unit = "m"
        elif mode == 'CENTIMETER':
            val *= (100 ** self.dimension)
            unit = "cm"
        elif mode == 'MILIMETER':
            val *= (1000 ** self.dimension)
            unit = 'mm'
        elif mode in {'FOOT', 'FEET'}:
            val *= (3.2808399 ** self.dimension)
            unit = "ft"
        elif mode == 'INCH':
            val *= (39.3700787 ** self.dimension)
            unit = "in"
        elif mode == 'RADIANS':
            unit = ""
        elif mode == 'DEGREES':
            val = self.value / pi * 180
            unit = "°"
        if system == 'IMPERIAL':
            if self.dimension == 2:
                unit = "sq " + unit
            elif self.dimension == 3:
                unit = "cu " + unit
        elif system == 'METRIC':
            if self.dimension == 2:
                unit += "\u00b2"  # Superscript two
            elif self.dimension == 3:
                unit += "\u00b3"  # Superscript three

        fmt = "%1." + str(self.precision) + "f"
        # remove trailing zeros
        res = fmt % val
        while res[-1] == '0':
            res = res[:-1]

        if res[-1] == ".":
            res = res + '0'

        return "{} {}".format(res, unit)

    def set_pos(self, context, value, pos_3d, direction, angle=0, normal=Vector((0, 0, 1))):
        self.up_axis = direction.normalized()
        self.c_axis = self.up_axis.cross(normal)
        self.pos_3d = pos_3d
        self.value = value
        self.angle = angle
        self._text = self.add_units(context)

    def draw(self, context, render=False):

        # print("draw_text %s %s" % (self.text, type(self).__name__))
        self.render = render
        p = self.position_2d_from_coord(context, self.pts[0], render)

        # dirty fast assignment
        dpi, font_id = context.preferences.system.dpi, 0

        # self.cbuff[0:4] = self.colour

        # bgl.glEnableClientState(bgl.GL_COLOR_ARRAY)
        # bgl.glColorPointer(4, bgl.GL_FLOAT, 0, self.cbuff)
        blf.color(0, *self.colour)
        if self.angle != 0:
            blf.enable(font_id, blf.ROTATION)
            blf.rotation(font_id, self.angle)
        blf.size(font_id, self.font_size, dpi)
        blf.position(font_id, p.x, p.y, 0)
        blf.draw(font_id, self.text)
        if self.angle != 0:
            blf.disable(font_id, blf.ROTATION)

        # bgl.glDisableClientState(bgl.GL_COLOR_ARRAY)


class GlBaseLine(Gl):

    def __init__(self,
                 d=3,
                 width=1,
                 style=bgl.GL_LINE,
                 closed=False,
                 n_pts=2):
        Gl.__init__(self, d)
        # default line width
        self.width = width
        # default line style
        self.style = style
        # allow closed lines
        self.closed = closed

        self.n_pts = n_pts

    def draw(self, context, render=False):
        """
            render flag when rendering
        """
        self.render = render
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glLineWidth(self.width)
        list_verts_co = [
            tuple(self.position_2d_from_coord(context, pt, render)[0:2])
            for i, pt in enumerate(self.pts)]
        if self.closed:
            list_verts_co.append(list_verts_co[0])
        g_line.draw(self.colour, list_verts_co)
        bgl.glLineWidth(1.0)
        bgl.glDisable(bgl.GL_BLEND)


class GlLine(GlBaseLine):
    """
        2d/3d Line
    """

    def __init__(self, d=3, p=None, v=None, p0=None, p1=None, z_axis=None):
        """
            d=3 use 3d coords, d=2 use 2d pixels coords
            Init by either
            p: Vector or tuple origin
            v: Vector or tuple size and direction
            or
            p0: Vector or tuple 1 point location
            p1: Vector or tuple 2 point location
            Will convert any into Vector 3d
            both optionnals
        """
        if p is not None and v is not None:
            self.p = Vector(p)
            self.v = Vector(v)
        elif p0 is not None and p1 is not None:
            self.p = Vector(p0)
            self.v = Vector(p1) - self.p
        else:
            self.p = Vector()
            self.v = Vector()
        if z_axis is not None:
            self.z_axis = z_axis
        else:
            self.z_axis = Vector((0, 0, 1))
        GlBaseLine.__init__(self, d, n_pts=2)

    @property
    def p0(self):
        return self.p

    @property
    def p1(self):
        return self.p + self.v

    @p0.setter
    def p0(self, p0):
        """
            Note: setting p0
            move p0 only
        """
        p1 = self.p1
        self.p = Vector(p0)
        self.v = p1 - p0

    @p1.setter
    def p1(self, p1):
        """
            Note: setting p1
            move p1 only
        """
        self.v = Vector(p1) - self.p

    @property
    def length(self):
        return self.v.length

    @property
    def angle(self):
        return atan2(self.v.y, self.v.x)

    @property
    def cross(self):
        """
            Vector perpendicular on plane defined by z_axis
            lie on the right side
            p1
            |--x
            p0
        """
        return self.v.cross(self.z_axis)

    def normal(self, t=0):
        """
            Line perpendicular on plane defined by z_axis
            lie on the right side
            p1
            |--x
            p0
        """
        n = GlLine()
        n.p = self.lerp(t)
        n.v = self.cross
        return n

    def sized_normal(self, t, size):
        """
            GlLine perpendicular on plane defined by z_axis and of given size
            positioned at t in current line
            lie on the right side
            p1
            |--x
            p0
        """
        n = GlLine()
        n.p = self.lerp(t)
        n.v = size * self.cross.normalized()
        return n

    def lerp(self, t):
        """
            Interpolate along segment
            t parameter [0, 1] where 0 is start of arc and 1 is end
        """
        return self.p + self.v * t

    def offset(self, offset):
        """
            offset > 0 on the right part
        """
        self.p += offset * self.cross.normalized()

    def point_sur_segment(self, pt):
        """ point_sur_segment (2d)
            point: Vector 3d
            t: param t de l'intersection sur le segment courant
            d: distance laterale perpendiculaire positif a droite
        """
        dp = (pt - self.p).to_2d()
        v2d = self.v.to_2d()
        dl = v2d.length
        d = (self.v.x * dp.y - self.v.y * dp.x) / dl
        t = v2d.dot(dp) / (dl * dl)
        return t > 0 and t < 1, d, t

    @property
    def pts(self):
        return [self.p0, self.p1]


class GlCircle(GlBaseLine):

    def __init__(self,
                 d=3,
                 radius=0,
                 center=Vector((0, 0, 0)),
                 z_axis=Vector((0, 0, 1))):

        self.r = radius
        self.c = center
        z = z_axis

        if z.z < 1:
            x = z.cross(Vector((0, 0, 1)))
            y = x.cross(z)
        else:
            x = Vector((1, 0, 0))
            y = Vector((0, 1, 0))

        self.rM = Matrix([
            Vector((x.x, y.x, z.x)),
            Vector((x.y, y.y, z.y)),
            Vector((x.z, y.z, z.z))
        ])
        self.z_axis = z
        self.a0 = 0
        self.da = 2 * pi
        GlBaseLine.__init__(self, d, n_pts=60)

    def lerp(self, t):
        """
            Linear interpolation
        """
        a = self.a0 + t * self.da
        return self.c + self.rM @ Vector((self.r * cos(a), self.r * sin(a), 0))

    @property
    def pts(self):
        n_pts = max(1, int(round(abs(self.da) / pi * 30, 0)))
        self.n_pts = n_pts
        t_step = 1 / n_pts
        return [self.lerp(i * t_step) for i in range(n_pts + 1)]


class GlArc(GlCircle):

    def __init__(self,
                 d=3,
                 radius=0,
                 center=Vector((0, 0, 0)),
                 z_axis=Vector((0, 0, 1)),
                 a0=0,
                 da=0):
        """
            a0 and da arguments are in radians
            a0 = 0   on the x+ axis side
            a0 = pi  on the x- axis side
            da > 0 CCW contrary-clockwise
            da < 0 CW  clockwise
        """
        GlCircle.__init__(self, d, radius, center, z_axis)
        self.da = da
        self.a0 = a0

    @property
    def length(self):
        return self.r * abs(self.da)

    def normal(self, t=0):
        """
            perpendicular line always on the right side
        """
        n = GlLine(d=self.d, z_axis=self.z_axis)
        n.p = self.lerp(t)
        if self.da < 0:
            n.v = self.c - n.p
        else:
            n.v = n.p - self.c
        return n

    def sized_normal(self, t, size):
        n = GlLine(d=self.d, z_axis=self.z_axis)
        n.p = self.lerp(t)
        if self.da < 0:
            n.v = size * (self.c - n.p).normalized()
        else:
            n.v = size * (n.p - self.c).normalized()
        return n

    def tangeant(self, t, length):
        a = self.a0 + t * self.da
        ca = cos(a)
        sa = sin(a)
        n = GlLine(d=self.d, z_axis=self.z_axis)
        n.p = self.c + self.rM @ Vector((self.r * ca, self.r * sa, 0))
        n.v = self.rM @ Vector((length * sa, -length * ca, 0))
        if self.da > 0:
            n.v = -n.v
        return n

    def offset(self, offset):
        """
            offset > 0 on the right part
        """
        if self.da > 0:
            radius = self.r + offset
        else:
            radius = self.r - offset
        return GlArc(d=self.d,
                     radius=radius,
                     center=self.c,
                     a0=self.a0,
                     da=self.da,
                     z_axis=self.z_axis)


class GlPolygon(Gl):

    def __init__(self,
                 colour=(0.3, 0.3, 0.3, 1.0),
                 d=3, n_pts=60):
        self.pts_3d = []
        Gl.__init__(self, d, colour)

        self.n_pts = min(n_pts, 60)

    def set_pos(self, pts_3d):
        self.pts_3d = pts_3d

    @property
    def pts(self):
        return self.pts_3d

    def draw(self, context, render=False):
        """
            render flag when rendering
        """
        # return

        self.render = render
        if self.n_pts == 0:
            return

        pts = self.pts

        g_vertices = [
            tuple(self.position_2d_from_coord(context, pt, render)[0:2])
            for i, pt in enumerate(pts)]
        bgl.glEnable(bgl.GL_BLEND)
        g_poly.draw(self.colour, g_vertices)
        bgl.glDisable(bgl.GL_BLEND)


class GlRect(GlPolygon):
    def __init__(self,
                 colour=(0.0, 0.0, 0.0, 1.0),
                 d=2):
        GlPolygon.__init__(self, colour, d, n_pts=4)

    @property
    def pts(self):
        return self.pts_2d

    def draw(self, context, render=False):
        pts = [
            self.position_2d_from_coord(context, pt, render)
            for pt in self.pts_3d
        ]
        x0, y0 = pts[0]
        x1, y1 = pts[1]
        self.pts_2d = [Vector((x, y)) for x, y in [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]]
        GlPolygon.draw(self, context, render)


class GlImage(Gl):
    def __init__(self,
                 d=2,
                 image=None):
        # GImage bindcode[0]
        self.image = image
        self.colour_inactive = (1, 1, 1, 1)
        Gl.__init__(self, d)
        self.pts_2d = [Vector((0, 0)), Vector((10, 10))]
        self.n_pts = 4

    def set_pos(self, pts):
        self.pts_2d = pts

    @property
    def pts(self):
        return self.pts_2d

    def draw(self, context, render=False):
        if self.image is None:
            return

        p0 = self.pts[0]
        p1 = self.pts[1]
        coords = [(p0.x, p0.y), (p1.x, p0.y), (p0.x, p1.y), (p1.x, p1.y)]
        g_image.draw(self.image.bindcode, coords)


class GlPolyline(GlBaseLine):
    def __init__(self, colour, d=3, n_pts=60):
        self.pts_3d = []
        GlBaseLine.__init__(self, d, n_pts=n_pts)
        self.colour_inactive = colour

    def set_pos(self, pts_3d):
        self.pts_3d = pts_3d
        # self.pts_3d.append(pts_3d[0])

    @property
    def pts(self):
        return self.pts_3d


class GlHandle(GlPolygon):

    def __init__(self, sensor_size, size, draggable=False, selectable=False, d=3, n_pts=4):
        """
            sensor_size : 2d size in pixels of sensor area
            size : 3d size of handle
        """
        GlPolygon.__init__(self, d=d, n_pts=n_pts)
        prefs = get_prefs(bpy.context)
        self.colour_active = prefs.handle_colour_active
        self.colour_hover = prefs.handle_colour_hover
        self.colour_normal = prefs.handle_colour_normal
        self.colour_selected = prefs.handle_colour_selected
        self.colour_inactive = prefs.handle_colour_inactive
        # variable symbol size in world coords
        self.size = size
        # constant symbol size in pixels
        self.symbol_size = sensor_size
        # scale factor for constant symbol pixel size
        self.scale = 1
        # sensor size in pixels
        self.sensor_width = sensor_size
        self.sensor_height = sensor_size
        self.pos_3d = Vector((0, 0, 0))
        self.up_axis = Vector((0, 0, 0))
        self.c_axis = Vector((0, 0, 0))
        self.hover = False
        self.active = False
        self.draggable = draggable
        self.selectable = selectable
        self.selected = False

    def scale_factor(self, context, pts):
        """
         Compute screen scale factor for symbol
         given 2 points in symbol direction (eg start and end of arrow)
        """
        prefs = get_prefs(context)
        if not prefs.constant_handle_size:
            return 1

        p2d = []
        for pt in pts:
            p2d.append(self.position_2d_from_coord(context, pt))
        sx = [p.x for p in p2d]
        sy = [p.y for p in p2d]
        x = max(sx) - min(sx)
        y = max(sy) - min(sy)
        s = max(x, y)
        if s > 0:
            fac = self.symbol_size / s
        else:
            fac = 1
        return fac

    def set_pos(self, context, pos_3d, direction, normal=Vector((0, 0, 1))):
        self.up_axis = direction.normalized()
        self.c_axis = self.up_axis.cross(normal)
        self.pos_3d = pos_3d
        self.pos_2d = self.position_2d_from_coord(context, self.sensor_center)
        x = self.up_axis * 0.5 * self.size
        y = self.c_axis * 0.5 * self.size
        pts = [self.sensor_center + v for v in [-x, x, -y, y]]
        self.scale = self.scale_factor(context, pts)

    def check_hover(self, pos_2d):
        if self.draggable:
            dp = pos_2d - self.pos_2d
            self.hover = abs(dp.x) < self.sensor_width and abs(dp.y) < self.sensor_height

    @property
    def sensor_center(self):
        pts = self.pts
        n = len(pts)
        x, y, z = 0, 0, 0
        for pt in pts:
            x += pt.x
            y += pt.y
            z += pt.z
        return Vector((x / n, y / n, z / n))

    @property
    def pts(self):
        raise NotImplementedError

    @property
    def colour(self):
        if self.render:
            return self.colour_inactive
        elif self.draggable:
            if self.active:
                return self.colour_active
            elif self.hover:
                return self.colour_hover
            elif self.selected:
                return self.colour_selected
            return self.colour_normal
        else:
            return self.colour_inactive


class SquareHandle(GlHandle):

    def __init__(self, sensor_size, size, draggable=False, selectable=False):
        GlHandle.__init__(self, sensor_size, size, draggable, selectable, n_pts=4)

    @property
    def pts(self):
        n = self.up_axis
        c = self.c_axis
        if self.selected or self.hover or self.active:
            scale = 1
        else:
            scale = 0.5
        x = n * self.scale * self.size * scale
        y = c * self.scale * self.size * scale
        return [self.pos_3d - x - y, self.pos_3d + x - y, self.pos_3d + x + y, self.pos_3d - x + y]


class TriHandle(GlHandle):

    def __init__(self, sensor_size, size, draggable=False, selectable=False):
        GlHandle.__init__(self, sensor_size, size, draggable, selectable, n_pts=3)

    @property
    def pts(self):
        n = self.up_axis
        c = self.c_axis
        # does move sensitive area so disable for tri handle
        # may implement sensor_center property to fix this
        # if self.selected or self.hover or self.active:
        scale = 1
        # else:
        #    scale = 0.5
        x = n * self.scale * self.size * 4 * scale
        y = c * self.scale * self.size * scale
        return [self.pos_3d - x + y, self.pos_3d - x - y, self.pos_3d]


class CruxHandle(GlHandle):

    def __init__(self, sensor_size, size, draggable=True, selectable=False):
        GlHandle.__init__(self, sensor_size, size, draggable, selectable, n_pts=0)
        self.branch_0 = GlPolygon((1, 1, 1, 1), d=3, n_pts=4)
        self.branch_1 = GlPolygon((1, 1, 1, 1), d=3, n_pts=4)

    def set_pos(self, context, pos_3d, direction, normal=Vector((0, 0, 1))):
        self.pos_3d = pos_3d
        self.pos_2d = self.position_2d_from_coord(context, self.sensor_center)
        o = self.pos_3d
        d = 0.5 * self.size
        x = direction.normalized()
        y = x.cross(normal)

        sx = x * 0.5 * self.size
        sy = y * 0.5 * self.size
        pts = [o + v for v in [-sx, sx, -sy, sy]]
        self.scale = self.scale_factor(context, pts)

        c = self.scale * d / 1.4242
        w = self.scale * self.size
        s = w - c

        xs = x * s
        xw = x * w
        ys = y * s
        yw = y * w
        p0 = o + xs + yw
        p1 = o + xw + ys
        p2 = o - xs - yw
        p3 = o - xw - ys
        p4 = o - xs + yw
        p5 = o + xw - ys
        p6 = o + xs - yw
        p7 = o - xw + ys

        self.branch_0.set_pos([p0, p1, p2, p3])
        self.branch_1.set_pos([p4, p5, p6, p7])

    @property
    def pts(self):
        return [self.pos_3d]

    def draw(self, context, render=False):
        self.render = render
        self.branch_0.colour_inactive = self.colour
        self.branch_1.colour_inactive = self.colour
        self.branch_0.draw(context)
        self.branch_1.draw(context)


class PlusHandle(GlHandle):

    def __init__(self, sensor_size, size, draggable=True, selectable=False):
        GlHandle.__init__(self, sensor_size, size, draggable, selectable, n_pts=0)
        self.branch_0 = GlPolygon((1, 1, 1, 1), d=3, n_pts=4)
        self.branch_1 = GlPolygon((1, 1, 1, 1), d=3, n_pts=4)

    def set_pos(self, context, pos_3d, direction, normal=Vector((0, 0, 1))):
        self.pos_3d = pos_3d
        self.pos_2d = self.position_2d_from_coord(context, self.sensor_center)
        o = self.pos_3d
        x = direction.normalized()
        y = x.cross(normal)
        sx = x * 0.5 * self.size
        sy = y * 0.5 * self.size
        pts = [o + v for v in [-sx, sx, -sy, sy]]
        self.scale = self.scale_factor(context, pts)
        w = self.scale * self.size
        s = self.scale * 0.25 * w

        xs = x * s
        xw = x * w
        ys = y * s
        yw = y * w
        p0 = o - xw + ys
        p1 = o + xw + ys
        p2 = o + xw - ys
        p3 = o - xw - ys
        p4 = o - xs + yw
        p5 = o + xs + yw
        p6 = o + xs - yw
        p7 = o - xs - yw
        self.branch_0.set_pos([p0, p1, p2, p3])
        self.branch_1.set_pos([p4, p5, p6, p7])

    @property
    def pts(self):
        return [self.pos_3d]

    def draw(self, context, render=False):
        self.render = render
        self.branch_0.colour_inactive = self.colour
        self.branch_1.colour_inactive = self.colour
        self.branch_0.draw(context)
        self.branch_1.draw(context)


class EditableText(GlText, GlHandle):
    def __init__(self, sensor_size, size, draggable=False, selectable=False):
        GlHandle.__init__(self, sensor_size, size, draggable, selectable)
        GlText.__init__(self, colour=(0, 0, 0, 1))

    def set_pos(self, context, value, pos_3d, direction, normal=Vector((0, 0, 1))):
        self.up_axis = direction.normalized()
        self.c_axis = self.up_axis.cross(normal)
        self.pos_3d = pos_3d
        self.value = value
        self._text = self.add_units(context)
        ts = self.text_size(context)
        self.pos_2d = self.position_2d_from_coord(context, pos_3d)
        self.pos_2d.x += 0.5 * ts.x
        self.sensor_width, self.sensor_height = 0.5 * ts.x, ts.y

    @property
    def sensor_center(self):
        return self.pos_3d


class ThumbHandle(GlHandle):

    def __init__(self, size_2d, label, image=None, draggable=False, selectable=False, d=2):
        GlHandle.__init__(self, size_2d, size_2d, draggable, selectable, d, n_pts=4)
        self.image = GlImage(image=image)
        self.label = GlText(d=2, label=label.replace("_", " ").capitalize())
        self.frame = GlPolyline((1, 1, 1, 1), d=2, n_pts=4)
        self.frame.closed = True
        self.size_2d = size_2d
        self.sensor_width = 0.5 * size_2d.x
        self.sensor_height = 0.5 * size_2d.y
        self.colour_normal = (0.715, 0.905, 1, 0.9)
        self.colour_hover = (1, 1, 1, 1)

    def set_pos(self, context, pos_2d):
        """
            pos 2d is center !!
        """
        self.pos_2d = pos_2d
        ts = self.label.text_size(context)
        self.label.pos_3d = pos_2d + Vector((-0.5 * ts.x, ts.y - 0.5 * self.size_2d.y))
        p0, p1 = self.pts
        self.image.set_pos(self.pts)
        self.frame.set_pos([p0, Vector((p1.x, p0.y)), p1, Vector((p0.x, p1.y))])

    @property
    def pts(self):
        s = 0.5 * self.size_2d
        return [self.pos_2d - s, self.pos_2d + s]

    @property
    def sensor_center(self):
        return self.pos_2d + 0.5 * self.size_2d

    def draw(self, context, render=False):
        self.render = render
        self.image.colour_inactive = self.colour
        # GlHandle.draw(self, context, render=False)
        self.image.draw(context, render=False)
        self.label.draw(context, render=False)
        self.frame.draw(context, render=False)


class Screen():
    def __init__(self, margin):
        self.margin = margin

    def size(self, context):

        system = context.preferences.system
        w = context.region.width
        h = context.region.height
        y_min = self.margin
        y_max = h - self.margin
        x_min = self.margin
        x_max = w - self.margin
        if system.use_region_overlap:
            #    system.window_draw_method in {'TRIPLE_BUFFER', 'ADAPTIVEMATIC'}):
            area = context.area
            for r in area.regions:
                if r.type == 'TOOLS':
                    x_min += r.width
                elif r.type == 'UI':
                    x_max -= r.width
        return x_min, x_max, y_min, y_max


class FeedbackPanel():
    """
        Feed-back panel
        inspired by np_station
    """

    def __init__(self, title='Archipack'):

        prefs = get_prefs(bpy.context)

        self.main_title = GlText(d=2,
                                 label=title + " : ",
                                 font_size=prefs.feedback_size_main,
                                 colour=prefs.feedback_colour_main
                                 )
        self.title = GlText(d=2,
                            font_size=prefs.feedback_size_title,
                            colour=prefs.feedback_colour_main
                            )
        self.spacing = Vector((
            0.5 * prefs.feedback_size_shortcut,
            0.5 * prefs.feedback_size_shortcut))
        self.margin = 50
        self.explanation = GlText(d=2,
                                  font_size=prefs.feedback_size_shortcut,
                                  colour=prefs.feedback_colour_main
                                  )
        self.shortcut_area = GlPolygon(colour=prefs.feedback_shortcut_area, d=2, n_pts=4)
        self.title_area = GlPolygon(colour=prefs.feedback_title_area, d=2, n_pts=4)
        self.shortcuts = []
        self.on = False
        self.show_title = True
        self.show_main_title = True
        # read only, when enabled, after draw() the top left coord of info box
        self.top = Vector((0, 0))
        self.screen = Screen(self.margin)

    def disable(self):
        self.on = False

    def enable(self):
        self.on = True

    def instructions(self, context, title, explanation, shortcuts):
        """
            position from bottom to top
        """
        prefs = get_prefs(context)

        self.explanation.label = explanation
        self.title.label = title

        self.shortcuts = []

        for key, label in shortcuts:
            key = GlText(d=2, label=key,
                         font_size=prefs.feedback_size_shortcut,
                         colour=prefs.feedback_colour_key)
            label = GlText(d=2, label=' : ' + label,
                           font_size=prefs.feedback_size_shortcut,
                           colour=prefs.feedback_colour_shortcut)
            ks = key.text_size(context)
            ls = label.text_size(context)
            self.shortcuts.append([key, ks, label, ls])

    def draw(self, context, render=False):

        if self.on:
            """
                draw from bottom to top
                so we are able to always fit needs
            """
            x_min, x_max, y_min, y_max = self.screen.size(context)
            available_w = x_max - x_min - 2 * self.spacing.x
            main_title_size = self.main_title.text_size(context) + Vector((5, 0))

            # h = context.region.height
            # 0,0 = bottom left
            pos = Vector((x_min + self.spacing.x, y_min))
            shortcuts = []

            # sort by lines
            lines = []
            line = []
            space = 0
            sum_txt = 0

            for key, ks, label, ls in self.shortcuts:
                space += ks.x + ls.x + self.spacing.x
                if pos.x + space > available_w:
                    txt_spacing = (available_w - sum_txt) / (max(1, len(line) - 1))
                    sum_txt = 0
                    space = ks.x + ls.x + self.spacing.x
                    lines.append((txt_spacing, line))
                    line = []
                sum_txt += ks.x + ls.x
                line.append([key, ks, label, ls])

            if len(line) > 0:
                txt_spacing = (available_w - sum_txt) / (max(1, len(line) - 1))
                lines.append((txt_spacing, line))

            # reverse lines to draw from bottom to top
            lines = list(reversed(lines))
            for spacing, line in lines:
                pos.y += self.spacing.y
                pos.x = x_min + self.spacing.x
                for key, ks, label, ls in line:
                    key.pos_3d = pos.copy()
                    pos.x += ks.x
                    label.pos_3d = pos.copy()
                    pos.x += ls.x + spacing
                    shortcuts.extend([key, label])
                pos.y += ks.y + self.spacing.y

            n_shortcuts = len(shortcuts)
            # shortcut area
            self.shortcut_area.pts_3d = [
                (x_min, self.margin),
                (x_max, self.margin),
                (x_max, pos.y),
                (x_min, pos.y)
            ]

            # small space between shortcut area and main title bar
            if n_shortcuts > 0:
                pos.y += 0.5 * self.spacing.y

            self.title_area.pts_3d = [
                (x_min, pos.y),
                (x_max, pos.y),
                (x_max, pos.y + main_title_size.y + 2 * self.spacing.y),
                (x_min, pos.y + main_title_size.y + 2 * self.spacing.y)
            ]
            pos.y += self.spacing.y

            title_size = self.title.text_size(context)
            # check for space available:
            # if explanation + title + main_title are too big
            # 1 remove main title
            # 2 remove title
            explanation_size = self.explanation.text_size(context)

            self.show_title = True
            self.show_main_title = True

            if title_size.x + explanation_size.x > available_w:
                # keep only explanation
                self.show_title = False
                self.show_main_title = False
            elif main_title_size.x + title_size.x + explanation_size.x > available_w:
                # keep title + explanation
                self.show_main_title = False
                self.title.pos_3d = (x_min + self.spacing.x, pos.y)
            else:
                self.title.pos_3d = (x_min + self.spacing.x + main_title_size.x, pos.y)

            self.explanation.pos_3d = (x_max - self.spacing.x - explanation_size.x, pos.y)
            self.main_title.pos_3d = (x_min + self.spacing.x, pos.y)

            self.shortcut_area.draw(context)
            self.title_area.draw(context)
            if self.show_title:
                self.title.draw(context)
            if self.show_main_title:
                self.main_title.draw(context)
            self.explanation.draw(context)
            for s in shortcuts:
                s.draw(context)

            self.top = Vector((x_min, pos.y + main_title_size.y + self.spacing.y))


class GlCursorFence():
    """
        Cursor crossing Fence
    """

    def __init__(self, width=1, colour=(1.0, 1.0, 1.0, 0.5), style=2852):
        self.line_x = GlLine(d=2, n_pts=2)
        self.line_x.style = style
        self.line_x.width = width
        self.line_x.colour_inactive = colour
        self.line_y = GlLine(d=2, n_pts=2)
        self.line_y.style = style
        self.line_y.width = width
        self.line_y.colour_inactive = colour
        self.on = True

    def set_location(self, context, location):
        w = context.region.width
        h = context.region.height
        p = Vector(location)
        x, y = p.x, p.y
        self.line_x.p = Vector((0, y))
        self.line_x.v = Vector((w, 0))
        self.line_y.p = Vector((x, 0))
        self.line_y.v = Vector((0, h))

    def enable(self):
        self.on = True

    def disable(self):
        self.on = False

    def draw(self, context, render=False):
        if self.on:
            self.line_x.draw(context)
            self.line_y.draw(context)


class GlCursorArea():
    def __init__(self,
                 width=1,
                 bordercolour=(1.0, 1.0, 1.0, 0.5),
                 areacolour=(0.5, 0.5, 0.5, 0.08),
                 style=2852):

        self.border = GlPolyline(bordercolour, d=2, n_pts=4)
        self.border.style = style
        self.border.width = width
        self.border.closed = True
        self.area = GlPolygon(areacolour, d=2, n_pts=4)
        self.min = Vector((0, 0))
        self.max = Vector((0, 0))
        self.on = False

    def in_area(self, pt):
        return (self.min.x <= pt.x and self.max.x >= pt.x and
                self.min.y <= pt.y and self.max.y >= pt.y)

    def set_location(self, context, p0, p1):
        p = Vector(p0)
        x0, y0 = p.x, p.y
        p = Vector(p1)
        x1, y1 = p.x, p.y
        if x0 > x1:
            x1, x0 = x0, x1
        if y0 > y1:
            y1, y0 = y0, y1
        self.min = Vector((x0, y0))
        self.max = Vector((x1, y1))
        pos = [
            Vector((x0, y0)),
            Vector((x0, y1)),
            Vector((x1, y1)),
            Vector((x1, y0))]
        self.area.set_pos(pos)
        self.border.set_pos(pos)

    def enable(self):
        self.on = True

    def disable(self):
        self.on = False

    def draw(self, context, render=False):
        if self.on:
            # print("GlCursorArea.draw()")
            self.area.draw(context)
            self.border.draw(context)
