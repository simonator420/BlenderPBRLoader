import bpy
import os

import bpy.utils.previews


valid_paths = [] # all material paths that include target folder
true_paths = [] # all paths selected through browse or add to queue buttons
paths_to_load = [] # paths of materials that were selected and are about to be loaded
preview_paths = [] # paths of all the materials that include preview folder
file_names = []
target_folders = ["1K", "2K", "3K", "4K", "5K", "6K", "7K", "8K", "9K", "10K", "11K", "12K", "13K", "14K", "15K", "16K"]

global custom_icons
custom_icons = None



def register_properties():
    bpy.types.WindowManager.selected_folder_path = bpy.props.StringProperty(
        name="Folder Path",
        subtype='DIR_PATH',
        default=""
    )
    
    bpy.types.WindowManager.selected_hdri_path = bpy.props.StringProperty(
        name="Folder Path",
        subtype='DIR_PATH',
        default=""
    )

    bpy.types.WindowManager.reawote_materials_index = bpy.props.IntProperty(update=print_selected_material_name)


    bpy.types.WindowManager.mapping_type = bpy.props.EnumProperty(
        name="Mapping Type",
        description="Mapping Type",
        items=[
            #('REAWOTE_DEFAULT', "Reawote Default - UV", ""),
            #('MOSAIC_DETILING', "Mosaic De-tiling - UV", ""),
            ('blender_original', "Blender Original - UV", ""),
            ('box_generated', "Box Mapping - Generated", ""),
            ('box_object', "Box Mapping - Object", "")
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
    
    bpy.types.WindowManager.is_hdri_selected = bpy.props.BoolProperty(
        name="Is HDRI Selected",
        default=False
    )


def unregister_properties():
    del bpy.types.WindowManager.selected_folder_path
    del bpy.types.WindowManager.selected_hdri_path
    del bpy.types.WindowManager.mapping_type
    del bpy.types.WindowManager.include_ao_maps
    del bpy.types.WindowManager.include_displacement_maps
    del bpy.types.WindowManager.use_16bit_displacement_maps
    del bpy.types.WindowManager.use_16bit_normal_maps
    del bpy.types.WindowManager.conform_maps
    del bpy.types.WindowManager.is_folder_selected
    del bpy.types.WindowManager.is_hdri_selected

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
        if file[0].isalpha():
            parts = file.split(".")[0].split("_")
            mapID = parts[3]
            mapID_list.append(mapID)
        else:
            continue
    return mapID_list

def load_preview_image(material_name, preview_file_path):
    # global custom_icons
    if material_name not in custom_icons:
        if os.path.exists(preview_file_path):
            custom_icons.load(material_name, preview_file_path, 'IMAGE')
        else:
            print(f"Preview image path does not exist: {preview_file_path}")

def print_selected_material_name(self, context):
    idx = context.window_manager.reawote_materials_index
    if idx >= 0 and idx < len(context.window_manager.reawote_materials):
        self.report({'WARNING'}, "Tak jsme tadyyyyy.")
        # material_name = context.window_manager.reawote_materials[idx].name
        material_name = file_names[idx]
        preview_path = preview_paths[idx]
        res = [i for i in preview_paths if len(i.split(os.path.sep)) >= 3 and i.split(os.path.sep)[-3] == material_name]
        load_preview_image(material_name, res[0])
        if context.area:
            context.area.tag_redraw()

def update_material_selection(self, context):
    material_list = context.window_manager.reawote_materials
    for index, material in enumerate(material_list):
        if material == self and material.selected:
            full_path = valid_paths[index]
            for target_folder in os.listdir(full_path):
                if "PREVIEW" in target_folder:
                    preview_path = os.path.join(full_path,target_folder)
                    for preview_file in os.listdir(preview_path):
                        if "SPHERE" in preview_file or "FABRIC" in preview_file or "PLANE" in preview_file:
                            preview_file_path = os.path.join(preview_path,preview_file)
                            load_preview_image(material.name, preview_file_path)
                            if context.area:
                                context.area.tag_redraw()
                            break

# workaround for macOS to display material preview
def initialize_materials(self, materials):
    for material in materials:
        material.selected = True
    
    for material in materials:
        material.selected = False


class ReawoteMaterialItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    selected: bpy.props.BoolProperty(name="Select", default=False, update=update_material_selection)
    preview_file_path: bpy.props.StringProperty(name="Preview File Path") 


class REAWOTE_UL_MATERIALLIST(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item, "selected", text="")
        row.label(text=item.name)
        
class ReawoteHDRIBrowseOperator(bpy.types.Operator):
    bl_idname = "material.reawote_hdri_browse_operator"
    bl_label = "Browse HDRI Folder"
    bl_description = "Select the HDRI folder"
    
    filepath: bpy.props.StringProperty(subtype="DIR_PATH")
    
    def execute(self, context):
        folder_path = self.filepath
        if not folder_path or not os.path.exists(folder_path):
            self.report({'WARNING'}, "No valid HDRI folder selected.")
            return {'CANCELLED'}
        try:
            for file_name in os.listdir(folder_path):
                full_path = os.path.join(folder_path, file_name)
                if os.path.isdir(full_path):
                    for target_folder in os.listdir(full_path):
                        if target_folder in target_folders:
                            context.window_manager.selected_hdri_path = self.filepath
                            self.populate_hdri_list(context, self.filepath, clear_list=True)
                            context.window_manager.is_hdri_selected = True
                            
                            hdris = context.window_manager.reawote_materials
                            
                            initialize_materials(self,hdris)
                            
                            return {'FINISHED'}
            
            self.report({'WARNING'}, "Selected path doesn't contain any valid Reawote HDRIs.")
                            
        except NotADirectoryError:
            self.report({'WARNING'}, "Selected path doesn't contain any valid Reawote HDRIs.")
        
        return {'CANCELLED'}
    
    def invoke(self, context, event):
        print("Invoking HDRI folder selector...")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
        
    def populate_hdri_list(self, context, folder_path, clear_list=True):
        folder_path = context.window_manager.selected_hdri_path
        hdri_list = context.window_manager.reawote_materials
        added_true = False
        hdri_count = 0
        
        if clear_list:
            hdri_list.clear()
        
        try:
            for file_name in os.listdir(folder_path):
                full_path = os.path.join(folder_path, file_name)
                
                if os.path.isdir(full_path):
                    for target_folder in os.listdir(full_path):
                        if target_folder in target_folders:
                            target_folder_full_path = os.path.join(full_path, target_folder)
                            # Check for .hdr files in the target folder
                            if any(f.lower().endswith('.hdr') for f in os.listdir(target_folder_full_path)):
                                item = hdri_list.add()
                                parts = file_name.split('_')
                                item.name = '_'.join(parts[:3])
                                file_names.append(file_name)
                                valid_paths.append(full_path)
                                hdri_count += 1
                                if not added_true:
                                    true_paths.append(folder_path)
                                    added_true = True
                                
                        elif "PREVIEW" in target_folder:
                            preview_path = os.path.join(full_path, target_folder)
                            for preview_file in os.listdir(preview_path):
                                if "PLANE" in preview_file:
                                    preview_file_path = os.path.join(preview_path, preview_file)
                                    preview_paths.append(preview_file_path)
                                    
                                    # load_preview_image(item.name, preview_file_path)
                                    break
        except:
            self.report({'WARNING'}, "Selected path isn't a valid directory.")
            return {'CANCELLED'}
        
        self.report({'WARNING'}, f"Tohle jsou valid_paths {valid_paths}.")
        self.report({'WARNING'}, f"Tohle jsou true_paths {true_paths}.")
        self.report({'WARNING'}, f"Tohle jsou preview_paths {preview_paths}.")
        return {'FINISHED'}
            
    
class ReawoteFolderBrowseOperator(bpy.types.Operator):
    bl_idname = "material.reawote_folder_browse_operator"
    bl_label = "Browse Folder"
    bl_description = "Select the material folder"

    filepath: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):

        folder_path = self.filepath
        try:
            for file_name in os.listdir(folder_path):
                full_path = os.path.join(folder_path, file_name)
                if os.path.isdir(full_path):
                    for target_folder in os.listdir(full_path):
                        if target_folder in target_folders:
                            context.window_manager.selected_folder_path = self.filepath
                            self.populate_material_list(context, self.filepath, clear_list=True)
                            context.window_manager.is_folder_selected = True
                            materials = context.window_manager.reawote_materials
                            
                            initialize_materials(self,materials)

                            context.window_manager.include_ao_maps = True
                            context.window_manager.include_displacement_maps = True
                            context.window_manager.use_16bit_displacement_maps = True
                            context.window_manager.use_16bit_normal_maps = True
                            context.window_manager.conform_maps = True

                            return {'FINISHED'}
            self.report({'WARNING'}, "Selected path doesn't contain any valid Reawote materials.")
                        
        except NotADirectoryError:
            self.report({'WARNING'}, "Selected path isn't a valid directory.")

        return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def populate_material_list(self, context, folder_path, clear_list=True):
        folder_path = context.window_manager.selected_folder_path
        material_list = context.window_manager.reawote_materials
        added_true = False # not adding the path to true_paths list twice
        mat_count = 0
        
        if clear_list:
            material_list.clear()

        try:
            for file_name in os.listdir(folder_path):
                full_path = os.path.join(folder_path, file_name)

                if os.path.isdir(full_path):
                    for target_folder in os.listdir(full_path):
                        if target_folder in target_folders:
                            target_folder_full_path = os.path.join(full_path, target_folder)
                            # Skip folders with .hdr files
                            if not any(f.lower().endswith('.hdr') for f in os.listdir(target_folder_full_path)):
                                item = material_list.add()
                                parts = file_name.split('_')
                                item.name = '_'.join(parts[:3])
                                file_names.append(file_name)
                                valid_paths.append(full_path)
                                mat_count += 1
                                if not added_true:
                                    true_paths.append(folder_path)
                                    added_true = True

                        elif "PREVIEW" in target_folder:
                            preview_path = os.path.join(full_path, target_folder)
                            for preview_file in os.listdir(preview_path):
                                if "SPHERE" in preview_file or "FABRIC" in preview_file:
                                    preview_file_path = os.path.join(preview_path, preview_file)
                                    preview_paths.append(preview_file_path)
                                    break
            
            if mat_count == 0:
                self.report({'WARNING'}, "Selected path doesn't contain any valid Reawote materials.")
                return {'CANCELLED'}

        except:
            self.report({'WARNING'}, "Selected path isn't a valid directory.")
            return {'CANCELLED'}

        self.report({'WARNING'}, f"Tohle jsou valid_paths {valid_paths}.")
        self.report({'WARNING'}, f"Tohle jsou true_paths {true_paths}.")
        self.report({'WARNING'}, f"Tohle jsou preview_paths {preview_paths}.")
        return {'FINISHED'}



class LoadMaterialsOperator(bpy.types.Operator):
    bl_idname = "wm.load_materials_operator"
    bl_label = "Load Material(s)"
    bl_description = "Load selected materials from the list"

    def set_projection(self, mapping, node):
        if mapping in ('box_generated', 'box_object'):
            node.projection = 'BOX'
            node.projection_blend = 0.3

    def execute(self, context):
        materials = context.window_manager.reawote_materials
        mapping = context.window_manager.mapping_type
        material_selected = False

        start_x, start_y = -300, 300
        offset_x, offset_y = 300, -300

        for index, material in enumerate(materials):
            if material.selected:
                material_selected = True
                current_x, current_y = start_x, start_y
                full_path = valid_paths[index]
                paths_to_load.append(full_path)
                principled_material = create_principled_bsdf_material(material.name, full_path)
                nodes = principled_material.node_tree.nodes
                material_node =  nodes.get('Principled BSDF')
                material_node.location = (start_x + 2*offset_x, current_y)
                output_node = nodes.get('Material Output')
                output_node.location = (start_x + 3*offset_x, current_y)
                if context.object:

                    context.object.data.materials.append(principled_material)
                    for target_folder in os.listdir(full_path):
                        if target_folder in target_folders:
                            target_folder_full_path = os.path.join(full_path, target_folder)
                            mapID_list = get_mapID(self, target_folder_full_path)
                            mix_rgb_node = None

                            tex_coord_node = principled_material.node_tree.nodes.new('ShaderNodeTexCoord')
                            tex_coord_node.location = (start_x - offset_x - offset_x, current_y)
                            mapping_node = principled_material.node_tree.nodes.new('ShaderNodeMapping')
                            mapping_node.location = (start_x - offset_x, current_y)

                            if mapping == "blender_original":
                                principled_material.node_tree.links.new(mapping_node.inputs['Vector'], tex_coord_node.outputs['UV'])

                            elif mapping == "box_generated":
                                offset_y -= 20
                                principled_material.node_tree.links.new(mapping_node.inputs['Vector'], tex_coord_node.outputs['Generated'])

                            elif mapping == "box_object":
                                offset_y -= 20
                                principled_material.node_tree.links.new(mapping_node.inputs['Vector'], tex_coord_node.outputs['Object'])

                            for file in os.listdir(target_folder_full_path):
                                texture_path = bpy.data.images.load(os.path.join(target_folder_full_path, file))

                                mapping = bpy.context.window_manager.mapping_type

                                
                                include_ao_maps = bpy.context.window_manager.include_ao_maps
                                include_displacement_maps = bpy.context.window_manager.include_displacement_maps
                                use_16bit_displacement_maps = bpy.context.window_manager.use_16bit_displacement_maps
                                use_16bit_normal_maps = bpy.context.window_manager.use_16bit_normal_maps
                                conform_maps = bpy.context.window_manager.conform_maps
                                
                                if conform_maps:
                                    if texture_path.size[0] > 0 and texture_path.size[1] > 0:
                                        aspect_ratio = texture_path.size[0] / texture_path.size[1]

                                        if hasattr(mapping_node, 'scale'):
                                                mapping_node.scale[0] = 1/aspect_ratio
                                        else:
                                            mapping_node.inputs['Scale'].default_value[0] = 1/aspect_ratio

                                        # mapping_node.inputs['Scale'].default_value[0] = 1.0 / aspect_ratio
                                        # mapping_node.inputs['Scale'].default_value[1] = 1.0
                                try:
                                    parts = file.split(".")[0].split("_")
                                    manufacturer = parts[0]
                                    product_number = parts[1]
                                    product = parts[2]
                                    mapID = parts[3]
                                    resolution = parts[4]

                                    if mapID == "COL":
                                        img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        img_texture_node.image = texture_path
                                        img_texture_node.location = (current_x, current_y)
                                        color_node_y = current_y
                                        current_y += offset_y
                                        self.set_projection(mapping,img_texture_node)

                                        principled_material.node_tree.links.new(img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        if not include_ao_maps or "AO" not in mapID_list:
                                            bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                            if bsdf_node:
                                                principled_material.node_tree.links.new(bsdf_node.inputs['Base Color'], img_texture_node.outputs['Color'])

                                        else:
                                            if not mix_rgb_node:
                                                mix_rgb_node = principled_material.node_tree.nodes.new('ShaderNodeMixRGB')
                                                mix_rgb_node.blend_type = 'MULTIPLY'
                                                mix_rgb_node.location = (current_x + offset_x, color_node_y)
                                                bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                                if bsdf_node:
                                                    principled_material.node_tree.links.new(bsdf_node.inputs['Base Color'], mix_rgb_node.outputs['Color'])

                                            principled_material.node_tree.links.new(mix_rgb_node.inputs['Color1'], img_texture_node.outputs['Color'])

                                    
                                    elif mapID == "AO" and include_ao_maps:
                                        ao_img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        ao_img_texture_node.image = texture_path
                                        ao_img_texture_node.location = (current_x, current_y)
                                        ao_node_y = current_y
                                        current_y += offset_y
                                        self.set_projection(mapping, ao_img_texture_node)
                                        principled_material.node_tree.links.new(ao_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        if not mix_rgb_node:
                                            mix_rgb_node = principled_material.node_tree.nodes.new('ShaderNodeMixRGB')
                                            mix_rgb_node.blend_type = 'MULTIPLY'
                                            mix_rgb_node.location = (current_x + offset_x, ao_node_y)
                                            bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                            if bsdf_node:
                                                principled_material.node_tree.links.new(bsdf_node.inputs['Base Color'], mix_rgb_node.outputs['Color'])

                                        # Link AO Image Texture to Color2 of MixRGB Node
                                        principled_material.node_tree.links.new(mix_rgb_node.inputs['Color2'], ao_img_texture_node.outputs['Color'])


                                    elif mapID == "ROUGH":
                                        rough_img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        rough_img_texture_node.image = texture_path
                                        rough_img_texture_node.image.colorspace_settings.name = 'Non-Color'
                                        rough_img_texture_node.location = (current_x, current_y)
                                        current_y += offset_y
                                        self.set_projection(mapping, rough_img_texture_node)
                                        principled_material.node_tree.links.new(rough_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                        if bsdf_node:
                                            principled_material.node_tree.links.new(bsdf_node.inputs['Roughness'], rough_img_texture_node.outputs['Color'])

                                    elif mapID == "NRM" and (not use_16bit_normal_maps or "NRM16" not in mapID_list):
                                        normal_img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        normal_img_texture_node.image = texture_path
                                        normal_img_texture_node.image.colorspace_settings.name = 'Non-Color'
                                        normal_img_texture_node.location = (current_x, current_y)
                                        self.set_projection(mapping, normal_img_texture_node)
                                        principled_material.node_tree.links.new(normal_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        # Create Normal Map Node
                                        normal_map_node = principled_material.node_tree.nodes.new('ShaderNodeNormalMap')
                                        normal_map_node.location = (current_x + offset_x, current_y)
                                        current_y += offset_y

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
                                        normal_img_texture_node.location = (current_x, current_y)
                                        self.set_projection(mapping, normal_img_texture_node)
                                        principled_material.node_tree.links.new(normal_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        # Create Normal Map Node
                                        normal_map_node = principled_material.node_tree.nodes.new('ShaderNodeNormalMap')
                                        normal_map_node.location = (current_x + offset_x, current_y)
                                        current_y += offset_y

                                        # Link Image Texture to Normal Map Node
                                        principled_material.node_tree.links.new(normal_map_node.inputs['Color'], normal_img_texture_node.outputs['Color'])

                                        # Link Normal Map Node to Normal of Principled BSDF
                                        bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                        if bsdf_node:
                                            principled_material.node_tree.links.new(bsdf_node.inputs['Normal'], normal_map_node.outputs['Normal'])

                                    elif mapID == "DISP" and include_displacement_maps and (not use_16bit_displacement_maps or "DISP" not in mapID_list):
                                        disp_img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        disp_img_texture_node.image = texture_path
                                        disp_img_texture_node.image.colorspace_settings.name = 'Non-Color'
                                        disp_img_texture_node.location = (current_x, current_y)
                                        
                                        self.set_projection(mapping, disp_img_texture_node)
                                        principled_material.node_tree.links.new(disp_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        # Create Displacement Node
                                        displacement_node = principled_material.node_tree.nodes.new('ShaderNodeDisplacement')
                                        displacement_node.location = (current_x + offset_x, current_y)
                                        current_y += offset_y
                                        # Link Image Texture to Displacement Node
                                        principled_material.node_tree.links.new(displacement_node.inputs['Height'], disp_img_texture_node.outputs['Color'])

                                        # Find Material Output Node
                                        material_output_node = principled_material.node_tree.nodes.get('Material Output')
                                        if material_output_node:
                                            # Link Displacement Node to Material Output's Displacement
                                            principled_material.node_tree.links.new(material_output_node.inputs['Displacement'], displacement_node.outputs['Displacement'])

                                    elif mapID == "DISP16" and use_16bit_displacement_maps and include_displacement_maps:
                                        disp_img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        disp_img_texture_node.image = texture_path
                                        disp_img_texture_node.image.colorspace_settings.name = 'Non-Color'
                                        disp_img_texture_node.location = (current_x, current_y)
                                        self.set_projection(mapping, disp_img_texture_node)
                                        principled_material.node_tree.links.new(disp_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])
                                        # Create Displacement Node
                                        displacement_node = principled_material.node_tree.nodes.new('ShaderNodeDisplacement')
                                        displacement_node.location = (current_x + offset_x, current_y)
                                        current_y += offset_y

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
                                        metal_img_texture_node.location = (current_x, current_y)
                                        current_y += offset_y
                                        self.set_projection(mapping, metal_img_texture_node)
                                        principled_material.node_tree.links.new(metal_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        # Link Image Texture to Metallic of Principled BSDF
                                        bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                        if bsdf_node:
                                            principled_material.node_tree.links.new(bsdf_node.inputs['Metallic'], metal_img_texture_node.outputs['Color'])

                                    elif mapID == "OPAC":
                                        opac_img_texture_node = principled_material.node_tree.nodes.new('ShaderNodeTexImage')
                                        opac_img_texture_node.image = texture_path
                                        opac_img_texture_node.image.colorspace_settings.name = 'Non-Color'
                                        opac_img_texture_node.location = (current_x, current_y)
                                        current_y += offset_y
                                        self.set_projection(mapping, opac_img_texture_node)
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
                                        sss_img_texture_node.location = (current_x, current_y)
                                        current_y += offset_y
                                        self.set_projection(mapping, sss_img_texture_node)
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
                                        sheen_img_texture_node.location = (current_x, current_y)
                                        current_y += offset_y
                                        self.set_projection(mapping, sheen_img_texture_node)
                                        principled_material.node_tree.links.new(sheen_img_texture_node.inputs['Vector'], mapping_node.outputs['Vector'])

                                        # Link Image Texture to Sheen of Principled BSDF
                                        bsdf_node = principled_material.node_tree.nodes.get('Principled BSDF')
                                        if bsdf_node:
                                            principled_material.node_tree.links.new(bsdf_node.inputs['Sheen Weight'], sheen_img_texture_node.outputs['Color'])

                                except:
                                    pass

        if not material_selected:
            self.report({'WARNING'}, "No materials were selected.")
            return {'CANCELLED'}
    
        self.report({'INFO'}, "Material(s) loaded successfully.")
        return {'FINISHED'}
    
class ApplyMaterialOperator(bpy.types.Operator):
    bl_idname = "wm.apply_material_operator"
    bl_label = "Apply Material On Selection"
    bl_description = "Apply material on selected object"
    
    def execute(self, context):
        obj = context.active_object
        material_list = context.window_manager.reawote_materials
        selected_mat = None
        select_count = 0

        if obj is None or 'materials' not in dir(obj.data):
            self.report({'WARNING'}, "No active object.")
            return {'CANCELLED'}
        
        for mat in material_list:
            if mat.selected:
                selected_mat = mat
                select_count += 1
        
        if selected_mat == None:
            self.report({'WARNING'}, "Select at least one material to be applied on the selected object.")
            return {'CANCELLED'}
        
        elif select_count > 1:
            self.report({'WARNING'}, "Only one material can be applied to selected object, you selected " + str(select_count) + ".")
            return {'CANCELLED'}
        
        for i, material in enumerate(obj.data.materials):
            if selected_mat.name == material.name:

                first_material = obj.data.materials[0]
                obj.data.materials[0] = material
                obj.data.materials[i] = first_material
                obj.data.update()
                self.report({'INFO'}, material.name + " has been applied.")
                return {'FINISHED'}
        
        self.report({'WARNING'}, "The material hasn't been loaded. Please load the material you wish to apply by using the 'Load Material(s)' button first.")        
        return {'CANCELLED'}
    
class SelectAllOperator(bpy.types.Operator):
    bl_idname = "wm.select_all_operator"
    bl_label = "Select All"
    bl_description = "Select all items in the list"

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
    bl_description = "Refresh the content of the folder(s)"

    def execute(self, context):
        material_list = context.window_manager.reawote_materials
        material_list.clear()
        valid_paths.clear()
        preview_paths.clear()
        
        if context.window_manager.is_hdri_selected:
            # Process HDRI files
            for true_path in true_paths:
                for file_name in os.listdir(true_path):
                    full_path = os.path.join(true_path, file_name)
                    
                    if os.path.isdir(full_path):
                        for target_folder in os.listdir(full_path):
                            if target_folder in target_folders:
                                target_folder_full_path = os.path.join(full_path, target_folder)
                                
                                # Check for HDRI files
                                if any(f.lower().endswith('.hdr') for f in os.listdir(target_folder_full_path)):
                                    item = material_list.add()
                                    parts = file_name.split('_')
                                    item.name = '_'.join(parts[:3])
                                    valid_paths.append(full_path)
                                
                                elif "PREVIEW" in target_folder:
                                    preview_path = os.path.join(full_path, target_folder)
                                    for preview_file in os.listdir(preview_path):
                                        if "PLANE" in preview_file:
                                            preview_file_path = os.path.join(preview_path, preview_file)
                                            preview_paths.append(preview_file_path)
                                            break
                                        
        elif context.window_manager.is_folder_selected:
            # Process material files
            for true_path in true_paths:
                for file_name in os.listdir(true_path):
                    full_path = os.path.join(true_path, file_name)

                    if os.path.isdir(full_path):
                        for target_folder in os.listdir(full_path):
                            if target_folder in target_folders:
                                target_folder_full_path = os.path.join(full_path, target_folder)

                                # Skip folders with .hdr files
                                if not any(f.lower().endswith('.hdr') for f in os.listdir(target_folder_full_path)):
                                    item = material_list.add()
                                    parts = file_name.split('_')
                                    item.name = '_'.join(parts[:3])
                                    valid_paths.append(full_path)
                                
                                elif "PREVIEW" in target_folder:
                                    preview_path = os.path.join(full_path, target_folder)
                                    for preview_file in os.listdir(preview_path):
                                        if "SPHERE" in preview_file or "FABRIC" in preview_file:
                                            preview_file_path = os.path.join(preview_path, preview_file)
                                            preview_paths.append(preview_file_path)
                                            break

        else:
            self.report({'WARNING'}, "No valid selection detected.")
            return {'CANCELLED'}

        initialize_materials(self, material_list)

        return {'FINISHED'}

class AddToQueueOperator(bpy.types.Operator):
    bl_idname = "wm.add_to_queue_operator"
    bl_label = "Add To Queue"
    bl_description = "Add another path to the list"

    filepath: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        materials = context.window_manager.reawote_materials
        if self.filepath:
            context.window_manager.selected_folder_path = self.filepath
            ReawoteFolderBrowseOperator.populate_material_list(self, context=context, folder_path=self.filepath, clear_list=False)
            initialize_materials(self, materials)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class CleanOperator(bpy.types.Operator):
    bl_idname = "wm.clean_operator"
    bl_label = "Clean"
    bl_description = "Reset plugin to the default state"

    def execute(self, context):
        material_list = context.window_manager.reawote_materials
        material_list.clear()
        valid_paths.clear()
        true_paths.clear()
        preview_paths.clear()

        context.window_manager.selected_folder_path = ""
        context.window_manager.selected_hdri_path = ""
        context.window_manager.is_folder_selected = False
        context.window_manager.is_hdri_selected = False

        context.window_manager.include_ao_maps = False
        context.window_manager.include_displacement_maps = False
        context.window_manager.use_16bit_displacement_maps = False
        context.window_manager.use_16bit_normal_maps = False
        context.window_manager.conform_maps = False

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
            # Wrap the operator in a row to conditionally disable it
            row = split.row()
            row.enabled = not wm.get("is_hdri_selected", False)  # Disable if HDRI is selected
            row.operator(ReawoteFolderBrowseOperator.bl_idname, text="Browse")
        
        split = layout.split(factor=0.4)
        split.label(text="HDRI folder:")
        
        if wm.selected_hdri_path:
            split.label(text=wm.selected_hdri_path)
        else:
            row = split.row()
            row.enabled = not wm.get("is_folder_selected", False)
            row.operator(ReawoteHDRIBrowseOperator.bl_idname, text="Browse")
        
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

        sub_layout.operator("wm.load_materials_operator", text="Load Material(s)")

        sub_layout.operator("wm.apply_material_operator", text="Apply Material On Selected Object")

        button_row = layout.row(align=False)
        button_row.enabled = wm.is_folder_selected or wm.is_hdri_selected
        button_row.operator("wm.select_all_operator", text="Select All")
        button_row.operator("wm.refresh_operator", text="Refresh")
        button_row.operator("wm.add_to_queue_operator", text="Add To Queue")
        button_row.operator("wm.clean_operator", text="Clean")

        layout.template_list("REAWOTE_UL_MATERIALLIST", "", wm, "reawote_materials", wm, "reawote_materials_index")
        
        # row = layout.row(align=False)
        # thumbnail_size = 6 if bpy.app.version >= (2, 80) else 5
        # row.scale_y = 0.5
        # row.template_icon_view(
        #     wmp,
        #     'thumbnails',
        #     show_labels=False,
        #     scale=thumbnail_size,
        # )

        material_list = wm.reawote_materials
        if material_list:
            selected_material = material_list[wm.reawote_materials_index]
            if selected_material and selected_material.name in custom_icons:
                layout.template_icon(icon_value=custom_icons[selected_material.name].icon_id, scale=5)
                layout.label(text=selected_material.name)

def register():
    global custom_icons
    custom_icons = bpy.utils.previews.new()

    bpy.utils.register_class(ReawotePBRLoaderPanel)
    bpy.utils.register_class(ReawoteFolderBrowseOperator)
    bpy.utils.register_class(ReawoteHDRIBrowseOperator)
    bpy.utils.register_class(SelectAllOperator)
    bpy.utils.register_class(RefreshOperator)
    bpy.utils.register_class(AddToQueueOperator)
    bpy.utils.register_class(CleanOperator)
    bpy.utils.register_class(LoadMaterialsOperator)
    bpy.utils.register_class(ApplyMaterialOperator)
    bpy.utils.register_class(ReawoteMaterialItem)
    bpy.utils.register_class(REAWOTE_UL_MATERIALLIST)
    bpy.types.WindowManager.reawote_materials = bpy.props.CollectionProperty(type=ReawoteMaterialItem)
    bpy.types.WindowManager.reawote_materials_index = bpy.props.IntProperty()
    register_properties()

def unregister():
    global custom_icons
    bpy.utils.previews.remove(custom_icons)
    custom_icons = None
    bpy.utils.unregister_class(ReawotePBRLoaderPanel)
    bpy.utils.unregister_class(ReawoteFolderBrowseOperator)
    bpy.utils.unregister_class(ReawoteHDRIBrowseOperator)
    bpy.utils.unregister_class(SelectAllOperator)
    bpy.utils.unregister_class(RefreshOperator)
    bpy.utils.unregister_class(AddToQueueOperator)
    bpy.utils.unregister_class(CleanOperator)
    bpy.utils.unregister_class(LoadMaterialsOperator)
    bpy.utils.unregister_class(ApplyMaterialOperator)
    bpy.utils.unregister_class(ReawoteMaterialItem)
    bpy.utils.unregister_class(REAWOTE_UL_MATERIALLIST)
    del bpy.types.WindowManager.reawote_materials
    del bpy.types.WindowManager.reawote_materials_index
    unregister_properties()
