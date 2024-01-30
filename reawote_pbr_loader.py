import bpy
import os

valid_paths = [] # all material paths that include target folder
true_paths = [] # all paths selected through browse or add to queure buttons
target_folders = ["1K", "2K", "3K", "4K", "5K", "6K", "7K", "8K", "9K", "10K", "11K", "12K", "13K", "14K", "15K", "16K"]

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

    bpy.types.WindowManager.is_folder_selected = bpy.props.BoolProperty(
        name="Is Folder Selected",
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
    del bpy.types.WindowManager.is_folder_selected

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

def update_material_selection(self, context):
    material_list = context.window_manager.reawote_materials
    for index, material in enumerate(material_list):
        if material == self:
            print(f"Checkbox for Material: {material.name}, Index: {index} has been {'checked' if material.selected else 'unchecked'}")
            full_path = valid_paths[index]
            for target_folder in os.listdir(full_path):
                if "PREVIEW" in target_folder:
                    preview_path = os.path.join(full_path,target_folder)
                    for preview_file in os.listdir(preview_path):
                        if "SPHERE" or "FABRIC" in preview_file:
                            preview_file_path = os.path.join(preview_path,preview_file)
                            break

class ReawoteMaterialItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    selected: bpy.props.BoolProperty(name="Select", default=False, update=update_material_selection)

# Define a UI List
class ReawoteMaterialUIList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item, "selected", text="")
        row.label(text=item.name)

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
    bl_description = "Select the material folder"

    filepath: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):

        folder_path = self.filepath
        for file_name in os.listdir(folder_path):
            full_path = os.path.join(folder_path, file_name)
            if os.path.isdir(full_path):
                for target_folder in os.listdir(full_path):
                    if target_folder in target_folders:
                        context.window_manager.selected_folder_path = self.filepath
                        self.populate_material_list(context, self.filepath, clear_list=True)
                        context.window_manager.is_folder_selected = True
                        return {'FINISHED'}
        self.report({'WARNING'}, "No Reawote materials were found in selected path")
        return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def populate_material_list(self, context, folder_path, clear_list=True):
        folder_path = context.window_manager.selected_folder_path
        material_list = context.window_manager.reawote_materials
        added_true = False
        
        if clear_list:
            material_list.clear()

        for file_name in os.listdir(folder_path):
            full_path = os.path.join(folder_path, file_name)

            if os.path.isdir(full_path):  # Check if it's a directory
                # print(f"These is the content of {file_name} : {os.listdir(full_path)}")
                
                for target_folder in os.listdir(full_path):
                    if target_folder in target_folders:
                        target_folder_full_path = os.path.join(full_path, target_folder)
                        item = material_list.add()
                        item.name = file_name
                        valid_paths.append(full_path)
                        print("-----------")
                        print(f"This is target_folder_full_path: {target_folder_full_path}")
                        print("-----------")
                        if added_true == False:
                            true_paths.append(folder_path)
                            added_true = True

            else:
                print(f"{file_name} is not a directory")

class LoadMaterialsOperator(bpy.types.Operator):
    bl_idname = "wm.load_materials_operator"
    bl_label = "Load Materials"
    bl_description = "Load selected materials from the list view"

    def execute(self, context):
        materials = context.window_manager.reawote_materials

        for index, material in enumerate(materials):
            if material.selected:
                print(f"Checked Material: {material.name}, Index: {index}")

        return {'FINISHED'}
    
class SelectAllOperator(bpy.types.Operator):
    bl_idname = "wm.select_all_operator"
    bl_label = "Select All"
    bl_description = "Select all items in the listview"

    def execute(self, context):
        materials = context.window_manager.reawote_materials

        # Determine if all materials are currently selected
        all_selected = all(item.selected for item in materials)

        # Set 'selected' to the opposite of 'all_selected' for each item
        for item in materials:
            item.selected = not all_selected
        return {'FINISHED'}

class RefreshOperator(bpy.types.Operator):
    bl_idname = "wm.refresh_operator"
    bl_label = "Refresh"
    bl_description = "Load materials from the paths in list view once again"

    def execute(self, context):
        material_list = context.window_manager.reawote_materials
        material_list.clear()
        valid_paths.clear()
        for true_path in true_paths:

            for file_name in os.listdir(true_path):
                full_path = os.path.join(true_path, file_name)

                if os.path.isdir(full_path):
                    for target_folder in os.listdir(full_path):
                        if target_folder in target_folders:
                            target_folder_full_path = os.path.join(full_path, target_folder)
                            item = material_list.add()
                            item.name = file_name
                            valid_paths.append(full_path)
                            print("-----------")
                            print(f"This is target_folder_full_path: {target_folder_full_path}")
                            print("-----------")
        print(" ")
        print(f"New valid_paths: {valid_paths}")
        return {'FINISHED'}

class AddToQueueOperator(bpy.types.Operator):
    bl_idname = "wm.add_to_queue_operator"
    bl_label = "Add To Queue"
    bl_description = "Add another path to list view"

    filepath: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        if self.filepath:
            context.window_manager.selected_folder_path = self.filepath
            ReawoteFolderBrowseOperator.populate_material_list(self, context=context, folder_path=self.filepath, clear_list=False)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class CleanOperator(bpy.types.Operator):
    bl_idname = "wm.clean_operator"
    bl_label = "Clean"
    bl_description = "Reset the plugin to default state"

    def execute(self, context):
        material_list = context.window_manager.reawote_materials
        material_list.clear()
        valid_paths.clear()
        true_paths.clear()
        context.window_manager.selected_folder_path = ""
        context.window_manager.is_folder_selected = False
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
        
        props_enabled = wm.is_folder_selected

        sub_layout = layout.column()
        sub_layout.enabled = props_enabled

        split = sub_layout.split(factor=0.4)
        split.label(text="Import mapping as:")
        split.prop(wm, "mapping_type", text="")

        # layout.separator()
        sub_layout.prop(wm, "include_ao_maps")
        sub_layout.prop(wm, "include_displacement_maps")
        sub_layout.prop(wm, "use_16bit_displacement_maps")
        sub_layout.prop(wm, "use_16bit_normal_maps")
        sub_layout.prop(wm, "conform_maps")

        sub_layout.operator("wm.load_materials_operator", text="Load Materials")

        button_row = layout.row(align=False)
        button_row.enabled = wm.is_folder_selected
        button_row.operator("wm.select_all_operator", text="Select All")
        button_row.operator("wm.refresh_operator", text="Refresh")
        button_row.operator("wm.add_to_queue_operator", text="Add To Queue")
        button_row.operator("wm.clean_operator", text="Clean")

        layout.template_list("ReawoteMaterialUIList", "", wm, "reawote_materials", wm, "reawote_materials_index")

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
    bpy.utils.register_class(ReawoteMaterialItem)
    bpy.utils.register_class(ReawoteMaterialUIList)
    bpy.types.WindowManager.reawote_materials = bpy.props.CollectionProperty(type=ReawoteMaterialItem)
    bpy.types.WindowManager.reawote_materials_index = bpy.props.IntProperty()
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
    bpy.utils.unregister_class(ReawoteMaterialItem)
    bpy.utils.unregister_class(ReawoteMaterialUIList)
    del bpy.types.WindowManager.reawote_materials
    del bpy.types.WindowManager.reawote_materials_index
    unregister_properties()
