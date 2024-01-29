import bpy

def register_properties():
    bpy.types.WindowManager.selected_folder_path = bpy.props.StringProperty(
        name="Folder Path",
        subtype='DIR_PATH',
        default=""
    )

    bpy.types.WindowManager.mapping_type = bpy.props.EnumProperty(
        name="Mapping Type",
        description="Choose the mapping type",
        items=[
            ('REAWOTE_DEFAULT', "Reawote Default - UV", ""),
            ('MOSAIC_DETILING', "Mosaic De-tiling - UV", ""),
            ('BLENDER_ORIGINAL', "Blender Original - UV", ""),
            ('BOX_MAPPING_GEN', "Box Mapping - Generated", ""),
            ('BOX_MAPPING_OBJ', "Box Mapping - Object", "")
        ]
    )

    bpy.types.WindowManager.include_ao_maps = bpy.props.BoolProperty(
        name="Include ambient occlusion (AO) maps",
        default=False
    )
    
    bpy.types.WindowManager.include_displacement_maps = bpy.props.BoolProperty(
        name="Include displacement maps",
        default=False
    )

    bpy.types.WindowManager.use_16bit_displacement_maps = bpy.props.BoolProperty(
        name="Use 16 bit displacement maps (when available)",
        default=False
    )

    bpy.types.WindowManager.use_16bit_normal_maps = bpy.props.BoolProperty(
        name="Use 16 bit normal maps (when available)",
        default=False
    )

    bpy.types.WindowManager.conform_maps = bpy.props.BoolProperty(
        name="Conform maps to image dimensions",
        default=False
    )


def unregister_properties():
    del bpy.types.WindowManager.selected_folder_path
    del bpy.types.WindowManager.mapping_type
    del bpy.types.WindowManager.include_ao_maps
    del bpy.types.WindowManager.include_displacement_maps
    del bpy.types.WindowManager.use_16bit_displacement_maps
    del bpy.types.WindowManager.use_16bit_normal_maps
    del bpy.types.WindowManager.conform_maps

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

class LoadMaterialsOperator(bpy.types.Operator):
    bl_idname = "wm.load_materials_operator"
    bl_label = "Load Materials"
    bl_description = "Load selected materials from the list view"

    def execute(self, context):
        # Your code here (e.g., loading materials)
        return {'FINISHED'}
    
class SelectAllOperator(bpy.types.Operator):
    bl_idname = "wm.select_all_operator"
    bl_label = "Select All"

    def execute(self, context):
        # Your code here
        return {'FINISHED'}

class RefreshOperator(bpy.types.Operator):
    bl_idname = "wm.refresh_operator"
    bl_label = "Refresh"

    def execute(self, context):
        # Your code here
        return {'FINISHED'}

class AddToQueueOperator(bpy.types.Operator):
    bl_idname = "wm.add_to_queue_operator"
    bl_label = "Add To Queue"

    def execute(self, context):
        # Your code here
        return {'FINISHED'}

class CleanOperator(bpy.types.Operator):
    bl_idname = "wm.clean_operator"
    bl_label = "Clean"

    def execute(self, context):
        # Your code here
        return {'FINISHED'}

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

        split = layout.split(factor=0.4)
        split.label(text="Material folder:")

        if wm.selected_folder_path:
            split.label(text=wm.selected_folder_path)
        else:
            split.operator(ReawoteFolderBrowseOperator.bl_idname, text="Browse")

        split = layout.split(factor=0.4)
        split.label(text="Import mapping as:")
        split.prop(wm, "mapping_type", text="")

        # layout.separator()
        layout.prop(wm, "include_ao_maps")
        layout.prop(wm, "include_displacement_maps")
        layout.prop(wm, "use_16bit_displacement_maps")
        layout.prop(wm, "use_16bit_normal_maps")
        layout.prop(wm, "conform_maps")

        layout.operator("wm.load_materials_operator", text="Load Materials")

        button_row = layout.row(align=False)
        button_row.operator("wm.select_all_operator", text="Select All")
        button_row.operator("wm.refresh_operator", text="Refresh")
        button_row.operator("wm.add_to_queue_operator", text="Add To Queue")
        button_row.operator("wm.clean_operator", text="Clean")

        layout.label(text="Simonek je borec")
        layout.operator(ReawotePBRLoaderOperator.bl_idname)

def register():
    bpy.utils.register_class(ReawotePBRLoaderOperator)
    bpy.utils.register_class(ReawotePBRLoaderPanel)
    bpy.utils.register_class(ReawoteFolderBrowseOperator)
    bpy.utils.register_class(SelectAllOperator)
    bpy.utils.register_class(RefreshOperator)
    bpy.utils.register_class(AddToQueueOperator)
    bpy.utils.register_class(CleanOperator)
    bpy.utils.register_class(LoadMaterialsOperator)
    register_properties()

def unregister():
    bpy.utils.unregister_class(ReawotePBRLoaderOperator)
    bpy.utils.unregister_class(ReawotePBRLoaderPanel)
    bpy.utils.unregister_class(ReawoteFolderBrowseOperator)
    bpy.utils.unregister_class(SelectAllOperator)
    bpy.utils.unregister_class(RefreshOperator)
    bpy.utils.unregister_class(AddToQueueOperator)
    bpy.utils.unregister_class(CleanOperator)
    bpy.utils.unregister_class(LoadMaterialsOperator)
    unregister_properties()
