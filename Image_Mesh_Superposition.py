#    Surface_Area_and_Volume_for_Blender.py (C) 2013,   Biagio Nigro
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

# be in edit mode to run this code  
bl_info = {  
    "name": "Obj-Image superposition",  
    "author": "Biagio Nigro",  
    "version": (1, 0, 0),  
    "blender": (2, 6, 8),  
    "location": "View3D",
    #"location": "View3D > Obj Image superposition",  
    "description": "Superimposes image files over 3D object reconstruction",  
    "warning": "",  
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Neuro_tool/visualization",  
    "tracker_url": "",  
    "category": "Tool"}  
  
import bpy  
from mathutils import Vector  
import mathutils
import math
import os
import sys
import random

bpy.types.Scene.x_side = bpy.props.FloatProperty \
      (
        name = "x",
        description = "Sample size x",
        default = 1
      )
bpy.types.Scene.y_side = bpy.props.FloatProperty \
      (
        name = "y",
        description = "Sample size y",
        default = 1
      )
bpy.types.Scene.z_side = bpy.props.FloatProperty \
      (
        name = "z",
        description = "Sample size z",
        default = 1
      )

bpy.types.Scene.image_ext = bpy.props.StringProperty \
      (
        name = "ext",
        description = "Image Extension",
        default = ".tif"
      )
      
bpy.types.Scene.image_path = bpy.props.StringProperty \
      (
        name = "path",
        description = "Image Path",
        default = "c:"
      )
      
bpy.types.Scene.x_grid = bpy.props.IntProperty \
      (
        name = "x_grid",
        description = "x grid subdivision",
        default = 50
      )
      
bpy.types.Scene.y_grid = bpy.props.IntProperty \
      (
        name = "y_grid",
        description = "y grid subdivision",
        default = 50
      )

bpy.types.Scene.file_min = bpy.props.IntProperty \
      (
        name = "file_min",
        description = "min file number",
        default = 0
      )
      

bpy.types.Scene.image_z_interval = bpy.props.FloatProperty \
      (
        name = "image_z_interval",
        description = "interval among stack images",
        default = 0
      )
      
bpy.types.Scene.number_of_images = bpy.props.IntProperty \
      (
        name = "number of images",
        description = "number of images in the stack",
        default = 0
      )
      

   
   
class SuperimposePanel(bpy.types.Panel):
    bl_label = "Superimpose"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

 
    def draw(self, context):
        row = self.layout.row()
        row.prop(context.scene , "x_side")
        row.prop(context.scene , "y_side") 
        row.prop(context.scene , "z_side") 
        
         
        row = self.layout.row()
        
        row.prop(context.scene , "image_path")
        row.operator("importfolder.tif", text='Image Folder')
        
        row = self.layout.row()
        row.prop(context.scene , "image_ext")
        row.operator("imageext.tif", text='Set extension')
        
        row = self.layout.row()
        row.operator("superimpose.tif", text='Show image planes')
        row = self.layout.row()
        row.operator("object.modal_operator", text='Scroll through images')
        
        self.layout.label("--Find Object from Image--") 
        
        row = self.layout.row()
        row.prop(context.scene , "x_grid") 
        row.prop(context.scene , "y_grid") 
        row.operator("object.point_operator", text='Select grid point')
        
        
        row = self.layout.row()
        row.operator("object.pickup_operator", text='Pick up Object')
        
        row = self.layout.row()
        row.operator("object.find_mitocondria", text='Find Mitocondria')
        
        row = self.layout.row()
        row.operator("object.show_names", text='Show Names')
        row.operator("object.hide_names", text='Hide Names')
        
        #mat=bpy.context.object.active_material 
        
        self.layout.label("--Mesh Transparency--") 
        row = self.layout.row()
        row.operator("object.add_transparency", text='Add Transparency')
        row.operator("object.rem_transparency", text='Remove Transpanrency')
        row = self.layout.row()
        if bpy.context.object is not None:
          mat=bpy.context.object.active_material
          if mat is not None:
             row.prop(mat, "alpha", slider=True)
             row.prop(mat, "diffuse_color", text="")
          
       

def active_node_mat(mat):
    # TODO, 2.4x has a pipeline section, for 2.5 we need to communicate
    # which settings from node-materials are used
    if mat is not None:
        mat_node = mat.active_node_material
        if mat_node:
            return mat_node
        else:
            return mat

    return None               
        
class AddTranspButton(bpy.types.Operator):
    bl_idname = "object.add_transparency"
    bl_label = "Add Transparency"
    
    
    def execute(self, context):
      if bpy.context.mode == 'OBJECT':  
       if (bpy.context.active_object is not None and  bpy.context.active_object.type=='MESH'):
           myob = bpy.context.active_object 
           myob.show_transparent=True
           bpy.data.materials[:]
           if bpy.context.object.active_material:
             matact=bpy.context.object.active_material
             matact.use_transparency=True
             matact.transparency_method = 'Z_TRANSPARENCY'   
             matact.alpha = 0.5
             #matact.diffuse_color = (0.8,0.8,0.8)  
           else: 
             matname=""
             for mater in bpy.data.materials[:]:
                             
                if mater.name=="_mat_"+myob.name:
                   matname=mater.name
                   break
             if matname=="":   
               mat = bpy.data.materials.new("_mat_"+myob.name)
             else:
                mat=bpy.data.materials[matname]
             mat.use_transparency=True
             mat.transparency_method = 'Z_TRANSPARENCY'            
             mat.alpha = 0.5   
             mat.diffuse_color = (0.8,0.8,0.8)         
             context.object.active_material = mat
             
      return {'FINISHED'} 

class RemTranspButton(bpy.types.Operator):
    bl_idname = "object.rem_transparency"
    bl_label = "Remove Transparency"
    
    
    def execute(self, context):
      if bpy.context.mode == 'OBJECT':  
       if (bpy.context.active_object is not None and bpy.context.active_object.type=='MESH'):
           myob = bpy.context.active_object 
           if bpy.context.object.active_material:
               matact=bpy.context.object.active_material
               if matact.name[0:5]=="_mat_":
                  
                  matact.use_transparency=False
                  bpy.ops.object.material_slot_remove()
                  bpy.data.materials[:].remove(matact)
                  myob.show_transparent=False
               else:
                  matact.alpha = 1       
                  matact.use_transparency=False
                  myob.show_transparent=False
                  
      return {'FINISHED'} 


class ImagePutOnButton(bpy.types.Operator):
    bl_idname = "superimpose.tif"
    bl_label = "Superimpose image"
    
    
    def execute(self, context):
      if bpy.context.mode == 'EDIT_MESH':
      
        directory = bpy.props.StringProperty(subtype="FILE_PATH")
        directory=bpy.context.scene.image_path
        exte = bpy.props.StringProperty(subtype="NONE")
        exte=bpy.context.scene.image_ext
        print(directory)
        print(exte)
        if os.path.exists(directory):
            
          files = os.listdir(directory)
          N=countFiles(directory, exte)
          if N>2:
            x=bpy.context.scene.x_side
            y=bpy.context.scene.y_side
            z=bpy.context.scene.z_side
            
            if (bpy.context.active_object.type=='MESH'):
                 ImagePutOnFunction(directory,exte,files, x,y,z, N)
          else:
            self.report({'INFO'},"No image stack within the selected directory")
        else: 
           self.report({'INFO'},"Wrong Directory Path")
      return {'FINISHED'} 
  
    
class ImageFolderButton(bpy.types.Operator):
    bl_idname = "importfolder.tif"
    bl_label = "Choose image folder"
 
    directory = bpy.props.StringProperty(subtype="FILE_PATH")
    
    def execute(self, context):
        directory = self.directory  
        
        bpy.context.scene.image_path=directory
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
       
        return {"RUNNING_MODAL"}

class ImageExtensionButton(bpy.types.Operator):
    bl_idname = "imageext.tif"
    bl_label = "Choose image ext"
 
    exte = bpy.props.StringProperty(subtype="NONE")
        
    def invoke(self, context, event):
        self.exte=bpy.context.scene.image_ext
        
        
        return {"FINISHED"}
   
        

class ModalOperator(bpy.types.Operator):
    bl_idname = "object.modal_operator"
    bl_label = "Simple Modal Operator"

    def __init__(self):
        print("Start")

    def __del__(self):
        print("End")

    
    def modal(self, context, event):
     
     if bpy.context.mode == 'OBJECT':  
       if (bpy.context.active_object.type=='EMPTY'):
        myob = bpy.context.active_object  
        directory = bpy.props.StringProperty(subtype="FILE_PATH")
        directory=bpy.context.scene.image_path
        exte = bpy.props.StringProperty(subtype="NONE")
        exte=bpy.context.scene.image_ext
        
        files = os.listdir(directory)
        N=countFiles(directory, exte)
        z_max=bpy.context.scene.z_side
        z_min=0
        l=(z_max-z_min)/(N-1)
        bu = [];
        for i in range(0,N):
          bu.append(i*l);
        
        point=myob.location.z
        minim=float('inf')
        i=0
        ind=0
        while i < len(bu):
       
         if abs(bu[i]-point) < minim:
            minim=abs(bu[i]-point)
            ind=i
         else: 
            pass
         i=i+1           
       
        #ind=ind+1
        
        files = os.listdir( directory )
      
        f=""
        
        for fi in files:
          if fi[-7:] == '{:03}'.format(ind+bpy.context.scene.file_min)+exte:
            
            f=fi
          else:
            
            pass   
            
        
        
        if event.type == 'WHEELDOWNMOUSE':  # Apply
           ind=ind-1
           if ind >=0:
             newf=f[0:-7]+'{:03}'.format(ind+bpy.context.scene.file_min)+exte
             
             bpy.data.images.load(directory+newf)
             myob.data = bpy.data.images[newf]
             myob.location.z= myob.location.z-l
            
        if event.type == 'WHEELUPMOUSE':  # Apply
           ind=ind+1
           if ind<=N-1:
             newf=f[0:-7]+'{:03}'.format(ind+bpy.context.scene.file_min)+exte
             
             bpy.data.images.load(directory+newf)
             myob.data = bpy.data.images[newf]
             myob.location.z= myob.location.z+l
            
        elif event.type == 'LEFTMOUSE':  # Confirm
            return {'FINISHED'}
        elif event.type in ('RIGHTMOUSE', 'ESC'):  # Cancel
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if bpy.ops.object.mode_set.poll():
          bpy.ops.object.mode_set(mode='OBJECT')
          if (bpy.context.active_object.type=='EMPTY'):
        
            print(context.window_manager.modal_handler_add(self))
            return {'RUNNING_MODAL'}
          else:
             return {'FINISHED'}
         

class PointOperator(bpy.types.Operator):
    bl_idname = "object.point_operator"
    bl_label = "Choose Point Operator"
    
    
    def execute(self, context):
                      
     if bpy.context.mode == 'OBJECT': 
      if bpy.context.active_object is not None:  
             
       if (bpy.context.active_object.type=='EMPTY'):    
          mt = bpy.context.active_object
         
          #delete previous grids
          all_obj = [item.name for item in bpy.data.objects]
          for object_name in all_obj:
            bpy.data.objects[object_name].select = False  
            if object_name[0:4]=='Grid':
              delThisObj(bpy.data.objects[object_name]) 
           
          zlattice=mt.location.z
          x_off=bpy.context.scene.x_side
          y_off=bpy.context.scene.y_side
          
          xg=bpy.context.scene.x_grid
          yg=bpy.context.scene.y_grid
       
          bpy.ops.mesh.primitive_grid_add(x_subdivisions=xg, y_subdivisions=yg, location=(0.0+x_off/2,0.0+y_off/2, zlattice-0.0001))
          grid = bpy.context.active_object
          grid.scale.x=x_off/2
          grid.scale.y=y_off/2
          bpy.ops.object.mode_set(mode = 'EDIT')
          
     return {"FINISHED"}


class PickupOperator(bpy.types.Operator):
    bl_idname = "object.pickup_operator"
    bl_label = "Pick up object Operator"
    
    
    def execute(self, context):
     if bpy.context.mode == 'EDIT_MESH': 
     #print(bpy.context.mode)     
       if bpy.context.active_object is not None:
         if bpy.context.active_object.name[0:4]=="Grid":
           bpy.ops.object.mode_set(mode = 'OBJECT') 
           grid=bpy.context.active_object 
           print("Active Object: "+grid.name)    
           selected_idx = [i.index for i in grid.data.vertices if i.select]
           lidx=len(selected_idx)
           l=len(bpy.data.objects)
             
          
           if l!=0 and lidx==1: 
             mindist=float('inf')
               
             #i=0
             #while i < l:
             for myob in bpy.data.objects:
               picked_obj_name=""   
               #myob=bpy.data.objects[i]                                  
               if myob.type=='MESH':
                  if myob.name[0:4]!='Grid':
                    
                    for v_index in selected_idx:
                      #get local coordinate, turn into word coordinate
                      
                      vert_coordinate = grid.data.vertices[v_index].co  
                      vert_coordinate = grid.matrix_world * vert_coordinate
                      
                      
                      dist=-1.0
                      if pointInBox(vert_coordinate, myob)==True:
                        dist=findMinDist(vert_coordinate, myob)
                        print(dist)
                        if dist==0:
                           mindist=dist
                           picked_obj_name=myob.name
                           print("point on surface " + picked_obj_name)
                           showObj(picked_obj_name)
                        elif dist>0 and pointInsideMesh(vert_coordinate, myob)==True:
                               
                           mindist=dist
                           picked_obj_name=myob.name
                           print("point inside " + picked_obj_name)
                           showObj(picked_obj_name)
                      
           
           all_obj = [item.name for item in bpy.data.objects]
           for object_name in all_obj:
             bpy.data.objects[object_name].select = False  
             if object_name[0:4]=='Grid':
                delThisObj(bpy.data.objects[object_name]) 
             
     return {"FINISHED"}


class FindMitoOperator(bpy.types.Operator):
    bl_idname = "object.find_mitocondria"
    bl_label = "Find Mitocondria"
    
    
    def execute(self, context):
     if bpy.context.mode == 'OBJECT': 
       print("--------------------------------------------------------------")    
       if bpy.context.active_object is not None and bpy.context.active_object.type=="MESH":
         myob = bpy.context.active_object 
         #bpy.ops.object.rem_transparency()
         
         myob_child=myob.children
         candidate_list = [item.name for item in bpy.data.objects if item.type == "MESH" and item.name!=myob.name and item not in myob_child]
         oblist=[]
         
         for object_name in candidate_list:
            if (bpy.data.objects[object_name].select == True):
              bpy.data.objects[object_name].select = False
            centro=BoundBoxCenter(bpy.data.objects[object_name])
            
            if pointInBox(centro, myob)==True:
               oblist.append(bpy.data.objects[object_name])    
             
         
         for ob in oblist:
            idx = [i.index for i in ob.data.vertices]
            l=len(idx)
            count=0
            for i in range(0,20):
               point_index=random.randint(0,l-1)
               point=ob.data.vertices[point_index].co 
               if pointInsideMesh(point, myob)==True:
                  count=count+1
            if count > 10:
              if ob.hide==True:
                 ob.hide=False      
                                           
            #print(ob.name)   
            bpy.context.scene.objects.active=myob   
                   
             
     return {"FINISHED"}

def BoundBoxCenter(obj):
 
   center = sum((Vector(b) for b in obj.bound_box), Vector())
   center /= 8
   return center 


class ShowNameButton(bpy.types.Operator):
    bl_idname = "object.show_names"
    bl_label = "Show Object names"
 
    
    
    def execute(self, context):
        if bpy.context.mode == 'OBJECT': 
         if bpy.context.active_object is not None:      
          if (bpy.context.active_object.type=='MESH'):    
           
           mt = bpy.context.active_object
           child=mt.children
           center=mathutils.Vector((0,0,0))
           center=centermass(mt)
           
           #add empty and make it child
           bpy.ops.object.add(type='EMPTY', location=center)
           emo = bpy.context.active_object
           emo.parent = mt                         
           bpy.ops.object.constraint_add(type='CHILD_OF')           
           emo.constraints['Child Of'].target = mt
           bpy.ops.constraint.childof_set_inverse(constraint=emo.constraints['Child Of'].name, owner='OBJECT')
           emo.name=mt.name+" "
           emo.show_name=True  
           emo.empty_draw_size = emo.empty_draw_size / 100
           
           mt.select=False
           emo.select=False
           stringtmp=""
           
           for obch in child:
           
               obch.select=True             
               bpy.context.scene.objects.active = obch
               if (obch.type=='MESH'):
                 ind=obch.name.find("_")
                 if ind!=-1:
                  stringname=obch.name[0:ind]
                  if (stringname!=stringtmp):
                   
                   center=centermass(obch)
                   bpy.ops.object.add(type='EMPTY', location=center)
                   em = bpy.context.active_object
                   em.parent = mt                         
                   bpy.ops.object.constraint_add(type='CHILD_OF')           
                   em.constraints['Child Of'].target = mt
                   bpy.ops.constraint.childof_set_inverse(constraint=em.constraints['Child Of'].name, owner='OBJECT')
                   em.name=stringname+" "
                   em.show_name=True  
                   em.empty_draw_size = emo.empty_draw_size / 100
                   obch.select=False
                   emo.select=False
                   stringtmp=stringname
        return {'FINISHED'}

class HideNameButton(bpy.types.Operator):
    bl_idname = "object.hide_names"
    bl_label = "Hide Object names"
 
   
    def execute(self, context):
        if bpy.context.mode == 'OBJECT': 
         if bpy.context.active_object is not None:  
          mt = bpy.context.active_object    
          if (mt.type=='MESH'):    
           
           
           child=mt.children
                      
           mt.select=False
                     
           for obch in child:
               if (obch.type=='EMPTY'): 
                 obch.select = True
                 bpy.context.scene.objects.active = obch
        
                 bpy.ops.object.delete() 
        return {'FINISHED'}

#calculate center of mass of a mesh 
def centermass(me):
  sum=mathutils.Vector((0,0,0))
  for v in me.data.vertices:
    #print(v.co)
    sum =sum+ v.co
  center = (sum)/len(me.data.vertices)
  print("center")
  print(center)
  return center 

#control mesh visibility
def showObj(obname):
   if bpy.data.objects[obname].hide == True:
         bpy.data.objects[obname].hide = False
      

#check if a point falls within bounding box of a mesh
def pointInBox(point, obj):
    
    bound=obj.bound_box
    minx=float('inf')
    miny=float('inf')
    minz=float('inf')
    maxx=-1.0
    maxy=-1.0
    maxz=-1.0
    
    minx=min(bound[0][0], bound[1][0],bound[2][0],bound[3][0],bound[4][0],bound[5][0],bound[6][0],bound[6][0])
    miny=min(bound[0][1], bound[1][1],bound[2][1],bound[3][1],bound[4][1],bound[5][1],bound[6][1],bound[6][1])
    minz=min(bound[0][2], bound[1][2],bound[2][2],bound[3][2],bound[4][2],bound[5][2],bound[6][2],bound[6][2])
    
    maxx=max(bound[0][0], bound[1][0],bound[2][0],bound[3][0],bound[4][0],bound[5][0],bound[6][0],bound[6][0])
    maxy=max(bound[0][1], bound[1][1],bound[2][1],bound[3][1],bound[4][1],bound[5][1],bound[6][1],bound[6][1])
    maxz=max(bound[0][2], bound[1][2],bound[2][2],bound[3][2],bound[4][2],bound[5][2],bound[6][2],bound[6][2])
    
    if (point[0]>minx and point[0]<maxx and point[1]>miny and point[1]<maxy and point[2]>minz and point[2]<maxz):
       
       return True
    else: 
         
       return False
    
# calculate minimum distance among a point in space and mesh vertices    
def findMinDist(point, obj):
    idx = [i.index for i in obj.data.vertices]
    min_dist=float('inf') 
    for v_index in idx:
       vert_coordinate = obj.data.vertices[v_index].co  
       vert_coordinate = obj.matrix_world * vert_coordinate
       a=(point[0]-vert_coordinate[0])*(point[0]-vert_coordinate[0])
       b=(point[1]-vert_coordinate[1])*(point[1]-vert_coordinate[1])
       c=(point[2]-vert_coordinate[2])*(point[2]-vert_coordinate[2])
       dist=math.sqrt(a+b+c)
       if (dist<min_dist):
            min_dist=dist
    return min_dist


# check if  point is surrounded by a mesh
def pointInsideMesh(point,ob):
    
    axes = [ mathutils.Vector((1,0,0)), mathutils.Vector((0,1,0)), mathutils.Vector((0,0,1)), mathutils.Vector((-1,0,0)), mathutils.Vector((0,-1,0)), mathutils.Vector((0,0,-1))  ]
   
    outside = False
    count = 0
    for axis in axes:
     
        orig=point
        
        location,normal,index = ob.ray_cast(orig,orig+axis*10000.0)
        if index!=-1:
            count=count+1
        
    if count<6:
       print("intersections "+str(count))
       return False
    else: 
       print("intersections "+str(count))
       return  True      
      


# delete object
def delThisObj(obj):
    bpy.data.objects[obj.name].select = True
    #bpy.ops.object.select_name(name=obj.name)
    bpy.context.scene.objects.active = obj
    print("deleting ",obj.name)
    bpy.ops.object.delete() 


def ShowBoundingBox(obname):
    bpy.data.objects[obname].show_bounds = True
    return

#count numeber of files within a folder          
def countFiles(path, exte):
  count=0
  minim=sys.maxsize
  dirs = os.listdir( path )
  for item in dirs:
    if os.path.isfile(os.path.join(path, item)):
       if item[-4:] == exte:
         count = count+1
         
         if int(item[-7:-4]) < minim:
           minim=int(item[-7:-4])    
  bpy.context.scene.file_min=minim   
  
  return count
  
  
#create an empty an empty and upload an image according to the vertical height field (z-axis)
def ImagePutOnFunction(directory, exte, files, xx, yy, zz, Nfiles):  
 
   myob = bpy.context.active_object  
   bpy.ops.object.mode_set(mode = 'OBJECT')  

  
   all_obj = [item.name for item in bpy.data.objects]
   for object_name in all_obj:
      bpy.data.objects[object_name].select = False
  
   candidate_list = [item.name for item in bpy.data.objects if item.type == "EMPTY"]

   for object_name in candidate_list:
      bpy.data.objects[object_name].select = True
 
   # remove all selected.
   bpy.ops.object.delete()
  
   x_min=0.0
   x_max=xx
   y_min=0.0
   y_max=yy
   z_min=0.0
   z_max=zz
   
   print("z_max"+str(z_max))
   
   N=Nfiles

   l=(z_max-z_min)/(N-1)

   bpy.context.scene.number_of_images=N
   bpy.context.scene.image_z_interval=l

   bu = [];
   for i in range(0,N):
      bu.append(i*l);
      
    
  

   # collect selected verts
   selected_idx = [i.index for i in myob.data.vertices if i.select]
   original_object = myob.name
 
 
   for v_index in selected_idx:
      # get local coordinate, turn into word coordinate
      vert_coordinate = myob.data.vertices[v_index].co  
      vert_coordinate = myob.matrix_world * vert_coordinate
      
      
      # unselect all  
      for item in bpy.context.selectable_objects:  
          item.select = False  
       
    
      # this deals with adding the empty      
      bpy.ops.object.empty_add(type='IMAGE', location=vert_coordinate, rotation=(3.141592653,0,0))  
      mt = bpy.context.active_object 
      
      
      
      point=vert_coordinate[2]
      minim=float('inf')

      i=0
      ind=0
      while i < len(bu):
       
        if abs(bu[i]-point) < minim:
           minim=abs(bu[i]-point)
           ind=i
        else: 
           pass
        i=i+1           
      
      
      files = os.listdir( directory )
      
      f=""
      
      for fi in files:
        if fi[-7:] == '{:03}'.format(ind+bpy.context.scene.file_min)+exte:
            
            f=fi
        else:
            #print("File "+fi+" not found") 
            pass   
            
      bpy.data.images.load(directory+f)
      mt.data = bpy.data.images[f]
      
      mt.scale.x=xx
      mt.scale.y=xx
      mt.location = (0,0+yy, bu[ind])
      
      bpy.ops.object.select_all(action='TOGGLE')  
      bpy.ops.object.select_all(action='DESELECT')  
    
  # set original object to active, selects it, place back into editmode
   bpy.context.scene.objects.active = myob
   myob.select = True  
   bpy.ops.object.mode_set(mode = 'OBJECT')



def register():
    bpy.utils.register_module(__name__)
    
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    kmi = km.keymap_items.new(ModalOperator.bl_idname, 'Y', 'PRESS', ctrl=True)
    pass
    
def unregister():
    bpy.utils.unregister_module(__name__)
    
    pass
    
if __name__ == "__main__":
    register()  

