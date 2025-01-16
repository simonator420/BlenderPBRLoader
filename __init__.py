#  information about the add-on
bl_info = {
    "name": "Reawote PBR Loader",
    "description": "Loads PBR materials from Reawote library into Blender.",
    "blender": (2, 80, 0),
    "category": "Material"
}

# importing functionalities
from . import reawote_dialog
from . import reawote_pbr_loader

# enable the add-on
def register():
    reawote_dialog.register()
    reawote_pbr_loader.register()

# disable the add-on
def unregister():
    reawote_pbr_loader.register()

if __name__ == "__main__":
    register()

