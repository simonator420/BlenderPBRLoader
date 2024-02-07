import bpy
import os

valid_paths = [] # all material paths that include target folder
true_paths = [] # all paths selected through browse or add to queure buttons
paths_to_load = [] # paths of materials that were selected and are about to be loaded
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

def create_principled_bsdf_material(material_name, material_path):
    # Create a new material
    material = bpy.data.materials.new(name=material_name)
    material.use_nodes = True
    nodes = material.node_tree.nodes

    # Clear existing nodes
    for node in nodes:
        nodes.remove(node)

    # Create Principled BSDF and Material Output nodes
    bsdf_node = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf_node.location = (0, 0)

    output_node = nodes.new('ShaderNodeOutputMaterial')
    output_node.location = (200, 0)

    # Connect Principled BSDF to Material Output
    links = material.node_tree.links
    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

    # TODO: Load textures from material_path and connect them to the Principled BSDF node
    # You will need to add code here to load and connect textures based on your file naming conventions and structure

    return material

def get_mapID(self, files):
    mapID_list = []
    for file in os.listdir(files):
        parts = file.split(".")[0].split("_")
        mapID = parts[3]
        mapID_list.append(mapID)
        # print(f"This is mapID_list for {file} : {mapID_list}")
    return mapID_list

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
    preview_file_path: bpy.props.StringProperty(name="Preview File Path") 

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
                full_path = valid_paths[index]
                paths_to_load.append(full_path)
                print(f"Checked Material: {material.name}, Index: {index}")
                principled_material = create_principled_bsdf_material(material.name, full_path)
                if context.object:
                    # # Check if the material already exists in the slots
                    # if principled_material.name not in context.object.data.materials:
                    #     context.object.data.materials.append(principled_material)
                    # else:
                    #     # If the material already exists, get its index
                    #     mat_index = context.object.data.materials.find(principled_material.name)
                    #     context.object.active_material_index = mat_index
                    context.object.data.materials.append(principled_material)
                    # finding folder with bitmaps
                    for target_folder in os.listdir(full_path):
                        if target_folder in target_folders:
                            target_folder_full_path = os.path.join(full_path, target_folder)
                            mapID_list = get_mapID(self, target_folder_full_path)
                            mix_rgb_node = None

                            tex_coord_node = principled_material.node_tree.nodes.new('ShaderNodeTexCoord')
                            mapping_node = principled_material.node_tree.nodes.new('ShaderNodeMapping')

                            principled_material.node_tree.links.new(mapping_node.inputs['Vector'], tex_coord_node.outputs['UV'])

                            for file in os.listdir(target_folder_full_path):
                                print(" ")
                                print(f"Tohle je ta moje full_path: {target_folder_full_path}")
                                print(" ")
                                texture_path = bpy.data.images.load(os.path.join(target_folder_full_path, file))
                                try:
                                    parts = file.split(".")[0].split("_")
                                    manufacturer = parts[0]
                                    product_number = parts[1]
                                    product = parts[2]
                                    mapID = parts[3]
                                    print(f"This is mapID: {mapID}")
                                    resolution = parts[4]

                                    include_ao_maps = bpy.context.window_manager.include_ao_maps
                                    include_displacement_maps = bpy.context.window_manager.include_displacement_maps
                                    use_16bit_displacement_maps = bpy.context.window_manager.use_16bit_displacement_maps
                                    use_16bit_normal_maps = bpy.context.window_manager.use_16bit_normal_maps
                                    conform_maps = bpy.context.window_manager.conform_maps

                                    if mapID == "COL":
                                        img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        img_texture_node.image = texture_path
                                        principled_material.node_tree.links.new(img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        if not include_ao_maps or "AO" not in mapID_list:
                                            bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                            if bsdf_node:
                                                principled_material.node_tree.links.new(bsdf_node.inputs['Base Color'], img_texture_node.outputs['Color'])

                                        else:
                                            if not mix_rgb_node:
                                                mix_rgb_node = principled_material.node_tree.nodes.new('ShaderNodeMixRGB')
                                                mix_rgb_node.blend_type = 'MULTIPLY'
                                                bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                                if bsdf_node:
                                                    principled_material.node_tree.links.new(bsdf_node.inputs['Base Color'], mix_rgb_node.outputs['Color'])

                                            principled_material.node_tree.links.new(mix_rgb_node.inputs['Color1'], img_texture_node.outputs['Color'])

                                    
                                    elif mapID == "AO" and include_ao_maps:
                                        ao_img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        ao_img_texture_node.image = texture_path
                                        principled_material.node_tree.links.new(ao_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        if not mix_rgb_node:
                                            mix_rgb_node = principled_material.node_tree.nodes.new('ShaderNodeMixRGB')
                                            mix_rgb_node.blend_type = 'MULTIPLY'
                                            bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                            if bsdf_node:
                                                principled_material.node_tree.links.new(bsdf_node.inputs['Base Color'], mix_rgb_node.outputs['Color'])

                                        # Link AO Image Texture to Color2 of MixRGB Node
                                        principled_material.node_tree.links.new(mix_rgb_node.inputs['Color2'], ao_img_texture_node.outputs['Color'])


                                    elif mapID == "ROUGH":
                                        rough_img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        rough_img_texture_node.image = texture_path
                                        rough_img_texture_node.image.colorspace_settings.name = 'Non-Color'
                                        principled_material.node_tree.links.new(rough_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                        if bsdf_node:
                                            principled_material.node_tree.links.new(bsdf_node.inputs['Roughness'], rough_img_texture_node.outputs['Color'])

                                    elif mapID == "NRM" and (not use_16bit_normal_maps or "NRM16" not in mapID_list):
                                        normal_img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        normal_img_texture_node.image = texture_path
                                        normal_img_texture_node.image.colorspace_settings.name = 'Non-Color'
                                        principled_material.node_tree.links.new(normal_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        # Create Normal Map Node
                                        normal_map_node = principled_material.node_tree.nodes.new('ShaderNodeNormalMap')

                                        # Link Image Texture to Normal Map Node
                                        principled_material.node_tree.links.new(normal_map_node.inputs['Color'], normal_img_texture_node.outputs['Color'])

                                        # Link Normal Map Node to Normal of Principled BSDF
                                        bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                        if bsdf_node:
                                            principled_material.node_tree.links.new(bsdf_node.inputs['Normal'], normal_map_node.outputs['Normal'])
                                    
                                    elif mapID == "NRM16" and use_16bit_normal_maps:
                                        normal_img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        normal_img_texture_node.image = texture_path
                                        normal_img_texture_node.image.colorspace_settings.name = 'Non-Color'
                                        principled_material.node_tree.links.new(normal_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        # Create Normal Map Node
                                        normal_map_node = principled_material.node_tree.nodes.new('ShaderNodeNormalMap')

                                        # Link Image Texture to Normal Map Node
                                        principled_material.node_tree.links.new(normal_map_node.inputs['Color'], normal_img_texture_node.outputs['Color'])

                                        # Link Normal Map Node to Normal of Principled BSDF
                                        bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                        if bsdf_node:
                                            principled_material.node_tree.links.new(bsdf_node.inputs['Normal'], normal_map_node.outputs['Normal'])

                                    elif mapID == "DISP" and (not use_16bit_displacement_maps or "DISP" not in mapID_list):
                                        disp_img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        disp_img_texture_node.image = texture_path
                                        disp_img_texture_node.image.colorspace_settings.name = 'Non-Color'
                                        principled_material.node_tree.links.new(disp_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        # Create Displacement Node
                                        displacement_node = principled_material.node_tree.nodes.new('ShaderNodeDisplacement')

                                        # Link Image Texture to Displacement Node
                                        principled_material.node_tree.links.new(displacement_node.inputs['Height'], disp_img_texture_node.outputs['Color'])

                                        # Find Material Output Node
                                        material_output_node = principled_material.node_tree.nodes.get('Material Output')
                                        if material_output_node:
                                            # Link Displacement Node to Material Output's Displacement
                                            principled_material.node_tree.links.new(material_output_node.inputs['Displacement'], displacement_node.outputs['Displacement'])

                                    elif mapID == "DISP16" and use_16bit_displacement_maps:
                                        disp_img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        disp_img_texture_node.image = texture_path
                                        disp_img_texture_node.image.colorspace_settings.name = 'Non-Color'
                                        principled_material.node_tree.links.new(disp_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])
                                        # Create Displacement Node
                                        displacement_node = principled_material.node_tree.nodes.new('ShaderNodeDisplacement')

                                        # Link Image Texture to Displacement Node
                                        principled_material.node_tree.links.new(displacement_node.inputs['Height'], disp_img_texture_node.outputs['Color'])

                                        # Find Material Output Node
                                        material_output_node = principled_material.node_tree.nodes.get('Material Output')
                                        if material_output_node:
                                            # Link Displacement Node to Material Output's Displacement
                                            principled_material.node_tree.links.new(material_output_node.inputs['Displacement'], displacement_node.outputs['Displacement'])

                                    elif mapID == "METAL":
                                        metal_img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        metal_img_texture_node.image = texture_path
                                        metal_img_texture_node.image.colorspace_settings.name = 'Non-Color'
                                        principled_material.node_tree.links.new(metal_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        # Link Image Texture to Metallic of Principled BSDF
                                        bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                        if bsdf_node:
                                            principled_material.node_tree.links.new(bsdf_node.inputs['Metallic'], metal_img_texture_node.outputs['Color'])

                                    elif mapID == "OPAC":
                                        opac_img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        opac_img_texture_node.image = texture_path
                                        opac_img_texture_node.image.colorspace_settings.name = 'Non-Color'
                                        principled_material.node_tree.links.new(opac_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        # Link Image Texture to Alpha of Principled BSDF
                                        bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                        if bsdf_node:
                                            principled_material.node_tree.links.new(bsdf_node.inputs['Alpha'], opac_img_texture_node.outputs['Color'])

                                        # Set material settings for Blend and Shadow mode
                                        principled_material.blend_method = 'CLIP'
                                        principled_material.shadow_method = 'CLIP'
                                    
                                    elif mapID == "SSS":
                                        sss_img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        sss_img_texture_node.image = texture_path
                                        principled_material.node_tree.links.new(sss_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        # Link Image Texture to Subsurface Color of Principled BSDF
                                        bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                        if bsdf_node:
                                            
                                            principled_material.node_tree.links.new(bsdf_node.inputs['Subsurface Weight'], sss_img_texture_node.outputs['Color'])
                                            bsdf_node.subsurface_method = 'BURLEY'

                                            principled_material.node_tree.links.new(bsdf_node.inputs['Subsurface Color'], sss_img_texture_node.outputs['Color'])
                                        

                                    elif mapID == "SHEEN":
                                        sheen_img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        sheen_img_texture_node.image = texture_path
                                        sheen_img_texture_node.image.colorspace_settings.name = 'Non-Color'
                                        principled_material.node_tree.links.new(sheen_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        # Link Image Texture to Sheen of Principled BSDF
                                        bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                        if bsdf_node:
                                            principled_material.node_tree.links.new(bsdf_node.inputs['Sheen Weight'], sheen_img_texture_node.outputs['Color'])

                                except:
                                    pass


        print(f"These are selected paths: {paths_to_load}")
        self.report({'INFO'}, "Materials loaded")
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
        wmp = context.window_manager.pmc_props
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
        
        row = layout.row(align=False)
        thumbnail_size = 6 if bpy.app.version >= (2, 80) else 5
        row.scale_y = 0.5
        row.template_icon_view(
            wmp,
            'thumbnails',
            show_labels=False,
            scale=thumbnail_size,
        )

        global custom_icons
        icon_id = custom_icons["custom_icon"].icon_id
        layout.template_icon(icon_id, scale=6)
        
        layout.label(text="Simonek je borec")
        layout.operator(ReawotePBRLoaderOperator.bl_idname)

def register():
    global custom_icons
    custom_icons = bpy.utils.previews.new()
    script_dir = os.path.dirname(__file__)
    image_path = os.path.join(script_dir, "testovaci.jpeg")  # Replace with your image path
    custom_icons.load("custom_icon", image_path, 'IMAGE')

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
    global custom_icons
    bpy.utils.previews.remove(custom_icons)
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
