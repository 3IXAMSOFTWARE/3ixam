

# This directory is a Python package.

bl_info = {
    "name": "Network Renderer",
    "author": "Martin Poirier",
    "version": (1, 8, 1),
    "ixam": (2, 60, 0),
    "location": "Render > Engine > Network Render",
    "description": "Distributed rendering for 3IXAM",
    "warning": "Stable but still work in progress",
    "doc_url": "https://wiki.3ixam.com/index.php/Extensions:2.6/Py/"
               "Scripts/Render/Net_render",
    "category": "Render",
}


# To support reload properly, try to access a package var, if it's there, reload everything
if "init_data" in locals():
    import importlib
    importlib.reload(model)
    importlib.reload(operators)
    importlib.reload(client)
    importlib.reload(slave)
    importlib.reload(master)
    importlib.reload(master_html)
    importlib.reload(utils)
    importlib.reload(balancing)
    importlib.reload(ui)
    importlib.reload(repath)
    importlib.reload(versioning)
    importlib.reload(baking)
else:
    from netrender import model
    from netrender import operators
    from netrender import client
    from netrender import slave
    from netrender import master
    from netrender import master_html
    from netrender import utils
    from netrender import balancing
    from netrender import ui
    from netrender import repath
    from netrender import versioning
    from netrender import baking

jobs = []
slaves = []
blacklist = []

init_file = ""
valid_address = False
init_data = True


def register():
    import bpy
    bpy.utils.register_module(__name__)

def unregister():
    import bpy
    bpy.utils.unregister_module(__name__)
