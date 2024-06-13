bl_info = {
    "name": "3D Model Generator",
    "blender": (2, 80, 0),
    "category": "Object",
}

from . import panel

def register():
    panel.register()

def unregister():
    panel.unregister()

if __name__ == "__main__":
    register()
