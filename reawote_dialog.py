import bpy

# operator class for displaying a dialog window
class ReawoteDialogWindow(bpy.types.Operator):

    # uniquely identify the operator
    bl_idname = "wm.reawote_dialog_window"
    bl_label = "Reawote Dialog Window"

    # method that gets called when the operator is executed
    def execute(self, context):
        self.report({'INFO'}, "This is Reawote Dialog Window")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(ReawoteDialogWindow)

def unregister():
    bpy.utils.unregister_class(ReawoteDialogWindow)
