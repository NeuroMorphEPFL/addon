#    import_obj_batch_v1_3_3.py (C) 2013  Diego Marcos, Corrado Cali', Biagio Nigro
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/



bl_info = {  
    "name": "Wavefront (.obj) batch import",  
    "author": "Diego Marcos, Corrado Cali', Biagio Nigro",  
    "version": (1, 0, 0),  
    "blender": (2, 6, 8),  
    "location": "Scene > Wavefront batch import",  
    "description": "Imports .obj files in batch, with option of applying a Remesh modifier",  
    "warning": "",  
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Neuro_tool/import",  
    "tracker_url": "",  
    "category": "Import-Export"}  

import bpy
import os

bpy.types.Scene.remesh_when_importing = bpy.props.BoolProperty \
      (
        name = "Remesh",
        description = "Add Remesh modifier to imported meshes in smooth mode",
        default = True
      )
bpy.types.Scene.use_smooth_shade = bpy.props.BoolProperty \
      (
        name = "Smooth shading",
        description = "Smooth output faces",
        default = False
      )
bpy.types.Scene.apply_remesh = bpy.props.BoolProperty \
      (
        name = "Apply Remesh",
        description = "Apply remesh modifier to all the imported meshes; full faces remeshes will be deleted",
        default = False
      )
bpy.types.Scene.remesh_octree_depth = bpy.props.IntProperty \
      (
        name = "Remesh resolution",
        description = "Batch octree resolution: higher values give finer details",
        default = 7
      )
bpy.types.Scene.scale_when_importing = bpy.props.FloatProperty \
      (
        name = "Scale",
        description = "Set scale when importing",
        default = 1
      )

def _gen_order_update(name1, name2):
        def _u(self, ctxt):
            if (getattr(self, name1)):
                setattr(self, name2, False)
        return _u

bpy.types.Scene.use_size_rescaling = bpy.props.BoolProperty \
      (
        name = "Use rescaling factor",
        description = "Resize all imported meshes using a known rescaling factor",
        default = False,
        update=_gen_order_update("use_size_rescaling", "use_pixel_rescaling")
      )

bpy.types.Scene.use_pixel_rescaling = bpy.props.BoolProperty \
      (
        name = "Rescale by pixel size (Micron)",
        description = "Resize all imported meshes using pixel size (Micron)",
        default = True,
        update=_gen_order_update("use_pixel_rescaling", "use_size_rescaling")
      )

bpy.types.Scene.import_pixels = bpy.props.FloatProperty \
      (
        name = "Pixel number",
        description = "Number of pixels within image side",
        default = 400
      )
bpy.types.Scene.import_size = bpy.props.FloatProperty \
      (
        name = "Image side length (Micron)",
        description = "Image side length (in microns)",
        default = 5
      )
class ImportWavefrontPanel(bpy.types.Panel):
    bl_label = "Import .obj from folder"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
 
    def draw(self, context):
        row = self.layout.row()
        row.prop(context.scene , "remesh_when_importing")
        row.prop(context.scene , "apply_remesh")         
        
 
        row = self.layout.row()
        row.prop(context.scene , "use_smooth_shade") 
        row.prop(context.scene , "remesh_octree_depth") 
        
        row = self.layout.row()
        row.prop(context.scene , "use_size_rescaling")
        row.active = context.scene.use_size_rescaling      
        row.prop(context.scene , "scale_when_importing")

        row = self.layout.row()
        
        row.prop(context.scene , "use_pixel_rescaling")      
        row.active = context.scene.use_pixel_rescaling
        
        row.prop(context.scene , "import_pixels")      
        row.prop(context.scene , "import_size")
             
       
       
        row = self.layout.row()
        row.operator("import.obj", text='Import')
              
        
        
class ObjImportButton(bpy.types.Operator):
    bl_idname = "import.obj"
    bl_label = "Import (might take several minutes)"
 
    directory = bpy.props.StringProperty(subtype="FILE_PATH")
    files = bpy.props.CollectionProperty(name='File path', type=bpy.types.OperatorFileListElement)
    def execute(self, context):
        print(self.directory)
        items = [file.name for file in self.files]
        
        ObjBatchImport(self.directory,items)
        return {'FINISHED'} 
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}         

bpy.types.Scene.source =  bpy.props.StringProperty(subtype="FILE_PATH")

def ObjBatchImport(dir,files):
    old_objects = bpy.data.objects[:]
    for oobj in old_objects:
       print("Old obj")    
       print(oobj.name)
    
    print("New files")
    for f in files:
        if f[-4:] == '.obj':
            print(f)
            bpy.ops.import_scene.obj(filepath=dir + f)
    
    if bpy.context.scene.use_size_rescaling == True:
     
                s = bpy.context.scene.scale_when_importing
    else:       
                #bpy.context.scene.use_pixel_rescaling =True
                s = (bpy.context.scene.import_size)/(bpy.context.scene.import_pixels)
                
    for ob in bpy.data.objects[:]:
         
         if ob not in old_objects:
             
             
             bpy.context.scene.objects.active = ob
             bpy.data.objects.get(ob.name).select = True
             ob.scale = [s, s, s]
             ob.rotation_euler = [-0, 0, 0]
             bpy.ops.object.transform_apply(scale=True)
             if bpy.context.scene.remesh_when_importing == True:
                
                ob.modifiers.new("import_remesh", type='REMESH')
                ob.modifiers['import_remesh'].use_remove_disconnected=False
                ob.modifiers['import_remesh'].octree_depth = bpy.context.scene.remesh_octree_depth
                ob.modifiers['import_remesh'].mode = 'SMOOTH'
                ob.modifiers['import_remesh'].use_smooth_shade = bpy.context.scene.use_smooth_shade
                #ob.modifiers['import_remesh'].remove_disconnected_pieces = False
                if bpy.context.scene.apply_remesh == True:
                   bpy.context.scene.objects.active = ob
                   bpy.ops.object.modifier_apply(modifier='import_remesh')

    #bpy.ops.object.transform_apply(scale=True)
               

def register():
    bpy.utils.register_module(__name__)

    pass
    
def unregister():
    bpy.utils.unregister_module(__name__)

    pass
    
if __name__ == "__main__":
    register()  
