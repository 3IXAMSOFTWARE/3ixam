
import bpy
from bpy.app.handlers import persistent


@persistent
def load_handler(_):
    import bpy
    pass


def register():
    bpy.app.handlers.load_factory_startup_post.append(load_handler)


def unregister():
    bpy.app.handlers.load_factory_startup_post.remove(load_handler)
