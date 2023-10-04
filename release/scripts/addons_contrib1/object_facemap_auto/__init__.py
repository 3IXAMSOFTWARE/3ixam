

# <pep8 compliant>

bl_info = {
    "name": "Auto Face Map Widgets",
    "author": "Campbell Barton",
    "version": (1, 0),
    "ixam": (2, 80, 0),
    "location": "View3D",
    "description": "Use face-maps in the 3D view when rigged meshes are selected.",
    "warning": "This is currently a proof of concept.",
    "doc_url": "",
    "category": "Rigging",
}

submodules = (
    "auto_fmap_widgets",
    "auto_fmap_ops",
)

# reload at runtime, for development.
USE_RELOAD = False
USE_VERBOSE = False

from bpy.utils import register_submodule_factory

register, unregister = register_submodule_factory(__name__, submodules)

if __name__ == "__main__":
    register()
