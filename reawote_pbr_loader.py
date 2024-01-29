import bpy

def register_properties():
    bpy.types.WindowManager.selected_folder_path = bpy.props.StringProperty(
        name="Folder Path",
        subtype='DIR_PATH',
        default=""
    )

def unregister_properties():
    del bpy.types.WindowManager.selected_folder_path

# creates a basic material with nodes
def create_basic_material():
    material = bpy.data.materials.new(name="Basic_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    for node in nodes:
        nodes.remove(node)

    node_diffuse = nodes.new(type='ShaderNodeBsdfDiffuse')
    node_diffuse.location = (0, 0)

    node_output = nodes.new('ShaderNodeOutputMaterial')
    node_output.location = (200, 0)

    links = material.node_tree.links
    link = links.new(node_diffuse.outputs["BSDF"], node_output.inputs["Surface"])

    return material

# creates and applies the basic material to the active object
class ReawotePBRLoaderOperator(bpy.types.Operator):
    bl_idname = "material.reawote_pbr_loader_operator"
    bl_label = "Load Basic Material"

    def execute(self, context):
        material = create_basic_material()
        if context.object:
            context.object.active_material = material
        self.report({'INFO'}, "Basic Material Loaded")
        return {'FINISHED'}
    
class ReawoteFolderBrowseOperator(bpy.types.Operator):
    bl_idname = "material.reawote_folder_browse_operator"
    bl_label = "Browse Folder"

    filepath: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        context.window_manager.selected_folder_path = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# defines a UI panel for the add-on
class ReawotePBRLoaderPanel(bpy.types.Panel):
    bl_label = "Reawote PBR Loader"
    bl_idname = "MATERIAL_PT_reawote_pbr_loader"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        wm = context.window_manager
        layout = self.layout

        split = layout.split(factor=0.3)
        split.label(text="Material folder:")

        if wm.selected_folder_path:
            split.label(text=wm.selected_folder_path)
        else:
            split.operator(ReawoteFolderBrowseOperator.bl_idname, text="Browse")

        layout.label(text="Simonek je borec")
        layout.operator(ReawotePBRLoaderOperator.bl_idname)

def register():
    bpy.utils.register_class(ReawotePBRLoaderOperator)
    bpy.utils.register_class(ReawotePBRLoaderPanel)
    bpy.utils.register_class(ReawoteFolderBrowseOperator)
    register_properties()

def unregister():
    bpy.utils.unregister_class(ReawotePBRLoaderOperator)
    bpy.utils.unregister_class(ReawotePBRLoaderPanel)
    bpy.utils.unregister_class(ReawoteFolderBrowseOperator)
    unregister_properties()
