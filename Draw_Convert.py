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
    "name": "Draws Objs and Measure distances",  
    "author": "Biagio Nigro",  
    "version": (1, 0, 0),  
    "blender": (2, 6, 8),  
    "location": "View3D > Draw Objs and Measure distances",  
    "description": "Converts strokes into objects and measures distances",  
    "warning": "",  
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Neuro_tool/",  
    "tracker_url": "",  
    "category": "Tool"}  
  
import bpy  
from mathutils import Vector  
import mathutils
import math
import os
import sys


      
bpy.types.Scene.distance = bpy.props.FloatProperty \
      (
        name = "Distance",
        description = "Shortest distance",
        default = float('inf')
      )      

  
class DistanceListItem(bpy.types.PropertyGroup):
    distance_index = bpy.props.StringProperty(default="")
    #template_list_controls = bpy.props.StringProperty(default="", options={"HIDDEN"})  # for Blender 2.65 only?
  
class DrawConvertPanel(bpy.types.Panel):
    bl_label = "Draws-Converts and Measures distances"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

 
    def draw(self, context):
      row = self.layout.row()
        
      self.layout.label("--Draw Strokes--")
      row = self.layout.row()
      row.operator("object.enter_draw", text='Enter Draw Mode')
      obj=bpy.context.object
      if obj is not None:
        pencil=bpy.context.object.grease_pencil
        if obj is not None and pencil is not None:
          draw_gpencil_tools(context, self.layout)
          #row = self.layout.row()
          
        col = self.layout.column(align=True)
        col.label(text="Convert:")
        row = col.row()
        row.operator("object.convert_strokes", text='Convert strokes and points')
        row.operator("object.convert_curves", text='Reconstruct mesh from curves')
          
        col = self.layout.column(align=True)
        col.label(text="Clean:")
        row = col.row()
        row.operator("object.delete_points", text='Delete all empty points')
        row.operator("object.delete_curves", text='Delete all curves')
             
        
        self.layout.label("--Measure Distances--")
        row=self.layout.row()
        row.operator("object.measure_distance", text='Measure Distance')
        self.layout.template_list('UI_UL_list', 'distance_collection_id', context.scene, "distance_collection", \
                                 context.scene, "distance_collection_index", rows = 3)
        row.operator("clear.dist", text='Clear Distances')

class EnterDrawButton(bpy.types.Operator):
    bl_idname = "object.enter_draw"
    bl_label = "Enter Draw Mode"
    
    
    def execute(self, context):
      if bpy.context.mode == 'OBJECT':  
       if (bpy.context.active_object is not None and bpy.context.active_object.type=='EMPTY'):
           emptyimage=bpy.context.active_object
           all_obj = [item.name for item in bpy.data.objects]
           for obname in all_obj:
                print(obname)  
                if  bpy.data.objects[obname].type=="MESH":
                  if bpy.data.objects[obname].select == True:
                      bpy.data.objects[obname].select = False
                  if bpy.data.objects[obname].hide == False:
                      bpy.data.objects[obname].hide = True
                
                         
           bpy.ops.view3d.viewnumpad(type='TOP')
           if bpy.context.object.grease_pencil is None:
              bpy.ops.gpencil.data_add()
              pencil=bpy.context.object.grease_pencil
              pencil.draw_mode='SURFACE'
              bpy.ops.gpencil.layer_add()
              bpy.context.object.grease_pencil.layers.active.color = [1.0,0,0]
              bpy.context.object.grease_pencil.layers.active.line_width = 4
              bpy.context.object.grease_pencil.layers.active.alpha = 0.5
              bpy.context.object.grease_pencil.layers.active.info = bpy.data.images[0].name[:-4]+"_Layer" 
           else:  
              pencil=bpy.context.object.grease_pencil
              if bpy.context.object.grease_pencil.layers.active is None:
                 bpy.ops.gpencil.layer_add()
                 bpy.context.object.grease_pencil.layers.active.color = [1.0,0,0]
                 bpy.context.object.grease_pencil.layers.active.line_width = 4
                 bpy.context.object.grease_pencil.layers.active.alpha = 0.5
                 bpy.context.object.grease_pencil.layers.active.info = bpy.data.images[0].name[:-4]+"_Layer"
           #n_pen=len(bpy.data.grease_pencil)
           #pencil = bpy.data.grease_pencil[0]
              pencil.draw_mode='SURFACE'
      return {'FINISHED'}     

class DrawStroke(bpy.types.Operator):
    bl_idname = "object.draw"
    bl_label = "Draw strokes on image"
    
    
    def execute(self, context):
      if bpy.context.mode == 'OBJECT':  
       if (bpy.context.active_object is not None and bpy.context.active_object.type=='EMPTY'): 
              
              pencil=bpy.context.object.grease_pencil
              layerfound=False
              for lay in bpy.context.object.grease_pencil.layers:
                  lay.select=True
                  bpy.context.object.grease_pencil.layers.active.hide= True
              for lay in bpy.context.object.grease_pencil.layers:
                 if bpy.data.images[0].name[:-4]+"_Layer"==lay.info:
                    print(bpy.data.images[0].name[:-4]+"_Layer")
                    print("old_layer "+lay.info)
                    lay=bpy.context.object.grease_pencil.layers.active
                    bpy.context.object.grease_pencil.layers.active.hide= False
                    layerfound=True
                    
              if layerfound==False:
                           
                   bpy.ops.gpencil.layer_add()
                
                   bpy.context.object.grease_pencil.layers.active.hide= False
                   bpy.context.object.grease_pencil.layers.active.color = [1.0,0,0]
                   bpy.context.object.grease_pencil.layers.active.line_width = 4
                   bpy.context.object.grease_pencil.layers.active.alpha = 0.5
                   bpy.context.object.grease_pencil.layers.active.info = bpy.data.images[0].name[:-4]+"_Layer" 
                   bpy.ops.gpencil.draw('INVOKE_REGION_WIN',mode='DRAW', stroke=[]) 
              else:
                                
                   bpy.ops.gpencil.draw('INVOKE_REGION_WIN',mode='DRAW', stroke=[])  
                                
      return {'FINISHED'}  


class EraseStroke(bpy.types.Operator):
    bl_idname = "object.erase"
    bl_label = "Erase strokes from image"
    
    
    def execute(self, context):
      if bpy.context.mode == 'OBJECT':  
       if (bpy.context.active_object is not None and bpy.context.active_object.type=='EMPTY'):
              pencil=bpy.context.object.grease_pencil
              if (bpy.context.object.grease_pencil.layers.active is not None):
              
                 bpy.ops.gpencil.draw('INVOKE_REGION_WIN',mode='ERASER', stroke=[]) 
      return {'FINISHED'}  



class DeleteEmptyPointsButton(bpy.types.Operator):
    bl_idname = "object.delete_points"
    bl_label = "Delete all Empty points"
    
    
    def execute(self, context):
      if bpy.context.mode == 'OBJECT':  
          #delete previous grids
        all_obj = [item.name for item in bpy.data.objects]
        for object_name in all_obj:
          
              bpy.data.objects[object_name].select = False
              
        
        for object_name in all_obj:
            
          if object_name[0:5]=='Point':
              
              delThisObj(bpy.data.objects[object_name])  
      return {'FINISHED'}  


class DeleteCurvesButton(bpy.types.Operator):
    bl_idname = "object.delete_curves"
    bl_label = "Delete all Curves from Strokes"
    def execute(self, context):
      if bpy.context.mode == 'OBJECT':  
          
        all_obj = [item.name for item in bpy.data.objects]
        for object_name in all_obj:
          
              bpy.data.objects[object_name].select = False
              
        
        for object_name in all_obj:
            
          if object_name[0:5]=='curve':
              print(object_name)
              delThisObj(bpy.data.objects[object_name])  
      return {'FINISHED'}  



class MeasureDistButton(bpy.types.Operator):
    bl_idname = "object.measure_distance"
    bl_label = "Measure distance between two objects"
    
    
    def execute(self, context):
      if bpy.context.mode == 'OBJECT':  
          
       candidate_list = [item.name for item in bpy.data.objects if item.select == True]  
       actobj=bpy.context.active_object
       scn=context.scene
         
       if len(candidate_list)>=2:
        for candidate in candidate_list:
           if candidate!=actobj.name:    
             
             print("candidate list")
             print(candidate)
             #print(candidate_list[1])
             print(len(candidate_list))
             dist=0  
             ob1=bpy.data.objects[candidate]
             ob2=bpy.data.objects[actobj.name]
             if ob1.type=="EMPTY" and ob2.type=="EMPTY":
                 print(ob1.name[0:4])
                 if ob1.name[0:5]=="Point" and ob2.name[0:5]=="Point":
                   print("ciaokjkjhk")
                   print(ob1.location)
                   print(ob2.location) 
                   dist=findPointMinDist(ob1.location, ob2.location)
                   print(dist)
                 
                 
             if ob1.type=="EMPTY" and ob2.type=="MESH":
                 point=ob1.location
                 selected_idx = [i.index for i in ob2.data.vertices if i.select]
                 if len(selected_idx)==0:
                    dist=findMinDist(point, ob2)
                 else:
                    dist=findPartialMinDist(point, ob2)  
                 print(dist)      
             if ob1.type=="MESH" and ob2.type=="EMPTY":
                 point=ob2.location
                 selected_idx = [i.index for i in ob1.data.vertices if i.select]
                 if len(selected_idx)==0:
                    dist=findMinDist(point, ob1)
                 else:
                    dist=findPartialMinDist(point, ob1)
                 print(dist)    
             if ob1.type=="MESH" and ob2.type=="MESH":
                dist=findMeshesMinDist(ob1,ob2)                 
                print(dist)
             if ob1.type=="EMPTY" and ob2.type=="EMPTY":
                print("ciao")  
                if ob1.name[0:5]=="Empty":
                  print("ciao")    
                  print(ob2.location.z)
                  print(ob1.location.z)
                  dist=abs(ob2.location.z-ob1.location.z)     
                  print(dist)
             if ob1.type=="EMPTY" and ob2.type=="EMPTY":
                print("ciao") 
                if ob2.name[0:5]=="Empty":
                  print("ciao")
                  print(ob2.location.z)
                  print(ob1.location.z) 
                  dist=abs(ob2.location.z-ob1.location.z)     
                  print(dist)
             
             scn.distance_collection.add().distance_index = str(dist)
             scn.distance_collection[-1].name = str(dist)+" "+ ob1.name+"---"+ob2.name
             print(len(scn.distance_collection))
             print(scn.distance_collection)          
      return {'FINISHED'}     

class ClearDistances(bpy.types.Operator):
    bl_idname = "clear.dist"
    bl_label = "Clear Distances"
    
    def execute(self, context):
        scn = context.scene
        #bpy.ops.object.mode_set(mode='OBJECT')
        i=0
        N=len(scn.distance_collection)
        if N >0:
          for i in range(N-1,-1,-1):
              print(i)
              scn.distance_collection.remove(i)
            
          print(scn.distance_collection)    
        return{'FINISHED'}  

 


class ConvertStrokesButton(bpy.types.Operator):
   bl_idname = "object.convert_strokes"
   bl_label = "Convert strokes into curves and point into empties"
    
   def execute(self, context):
    if bpy.context.mode == 'OBJECT':  
     if (bpy.context.active_object is not None and bpy.context.active_object.type=='EMPTY'):
      imempty=bpy.context.active_object   
      pencil = bpy.context.object.grease_pencil
        
      if pencil is not None: 
       layers=bpy.context.object.grease_pencil.layers
       if layers is not None:
        
        obinscene = bpy.context.scene.objects
        if (pencil is not None and layers is not None): 
          
         for layer in layers:
          print("info "+layer.info)  
          layer.hide=False
      
          print("active "+layer.info)
          
          if layer.active_frame is not None:
            empty_list=[]
            for i, stroke in enumerate(layer.active_frame.strokes):
              if len(layer.active_frame.strokes[i].points)>1:  
                
                 stroke_points = layer.active_frame.strokes[i].points
          
                 data_list = [ (point.co.x, point.co.y, point.co.z) for point in stroke_points ]
                 curve_new=MakePolyLine("curve_new", "curve", data_list)
                 #curve_new=MakeBezierLine("curve_new", "curve", data_list)
                   
                 
                 curve_new.select=True  
                 bpy.context.scene.objects.active = curve_new  
                 bpy.ops.object.mode_set(mode = 'EDIT')
                 bpy.ops.curve.select_all(action='SELECT')
                 bpy.ops.curve.cyclic_toggle()  
                 bpy.ops.object.mode_set(mode = 'OBJECT') 
                 imempty.select=True  
                 curve_new.select=False
                 bpy.context.scene.objects.active = imempty  
                  
                 
              elif len(layer.active_frame.strokes[i].points)==1:
                 
                  stroke_x = layer.active_frame.strokes[i].points[0].co.x
                  stroke_y = layer.active_frame.strokes[i].points[0].co.y
                  stroke_z = layer.active_frame.strokes[i].points[0].co.z
                  stroke_points = layer.active_frame.strokes[i].points
                  punto=[(stroke_x, stroke_y, stroke_z)]
                  empty_list.extend(punto)
            #bpy.context.scene.objects.active = imempty 
            #bpy.ops.gpencil.data_unlink()
      
            if len(empty_list)!=0:
                 for point in empty_list:
                     print(point[0])
                     bpy.ops.object.add(type='EMPTY', location=(point[0], point[1],point[2]))
                     emo = bpy.context.active_object
                     emo.empty_draw_size = emo.empty_draw_size / 5
                     emo.name="Point"
                     emo.select=False
      
            
    return {"FINISHED"}


class ConvertCurveButton(bpy.types.Operator):
    bl_idname = "object.convert_curves"
    bl_label = "Convert curves into mesh"
    def execute(self, context):
     if bpy.context.mode == 'OBJECT':
      candidate_list = [item.name for item in bpy.data.objects if item.type == "CURVE" and item.select==True ]
      if len(candidate_list)!=0: 
       print(candidate_list)    
       if CheckIsoZ(candidate_list)==True:
           print("OK")
           curve_list, z_list, z_extrude=SortListZ(candidate_list)
           print(curve_list)
           print(z_list)
           print(z_extrude)
           for obname, zext in zip(curve_list, z_extrude):
    
              ConvertToMesh(obname)
              ExtrudeMesh(obname, zext)
              
           for obname in curve_list:
              object = bpy.data.objects.get(obname)
              object.select = True
              scene = bpy.context.scene  
              scene.objects.active = object
           bpy.ops.object.join()
           ob = bpy.context.active_object
           #ob.modifiers.new("new_tri", type='TRIANGULATE')
           #bpy.ops.object.modifiers_add(type='TRIANGULATE')
           #ob = bpy.context.active_object
           #ob.modifiers.new("new_remesh", type='REMESH')
           #ob.modifiers['new_remesh'].use_remove_disconnected=True
           #ob.modifiers['new_remesh'].octree_depth = bpy.context.scene.remesh_octree_depth
           #ob.modifiers['new_remesh'].mode = 'SMOOTH'
           #ob.modifiers['new_remesh'].use_smooth_shade = bpy.context.scene.use_smooth_shade
           #bpy.ops.object.modifier_apply(modifier='new_remesh')          
       else:
        self.report({'INFO'},"Wrong isocurve")    
          

     return {"FINISHED"}
 
def ConvertToMesh(src_name, keep_original=False, clean=True):
  bpy.ops.object.select_all(action='DESELECT')
  object = bpy.data.objects.get(src_name)
  object.select = True
  scene = bpy.context.scene
  scene.objects.active = object
  bpy.ops.object.convert(target='MESH', keep_original=keep_original)
  if (clean):
      bpy.ops.object.editmode_toggle()
      bpy.ops.mesh.remove_doubles(threshold=0.0001, use_unselected=False)
      bpy.ops.object.editmode_toggle()
  bpy.ops.object.select_all(action='DESELECT')
 
 
def ExtrudeMesh(src_name, zext):
  bpy.ops.object.select_all(action='DESELECT')
  object = bpy.data.objects.get(src_name)
  object.select = True
  print(src_name+" extruded "+ str(zext))
  scene = bpy.context.scene
  scene.objects.active = object
  bpy.ops.object.editmode_toggle()
  bpy.ops.mesh.select_all(action='SELECT')
  #bpy.ops.mesh.extrude_faces_move(MESH_OT_extrude_faces_indiv={"mirror":True}, TRANSFORM_OT_shrink_fatten={"value":zext}) 
  myVec = Vector((0,0,zext))

  bpy.ops.mesh.extrude_region_move( TRANSFORM_OT_translate={"value":myVec})
  bpy.ops.object.editmode_toggle()
  bpy.ops.object.select_all(action='DESELECT')

#check if curves lay on xy plane  
def CheckIsoZ(list):
    flag=True
    for obname in list:
        curve=bpy.data.objects[obname]
        print(obname)      
        z=curve.data.splines[0].points[0].co.z
        for point in curve.data.splines[0].points:
           if point.co.z!=z:
              flag==False
    return flag


#Sort curves according to their decreasing z value
def SortListZ(candidate_list):
           curve_list=[]
           curve_list.append(candidate_list[0])
           
           for element in candidate_list:
               a=bpy.data.objects[curve_list[0]].data.splines[0].points[0].co.z
               b=bpy.data.objects[curve_list[len(curve_list)-1]].data.splines[0].points[0].co.z
               
               if element!=curve_list[0]:
                    
                 curve=bpy.data.objects[element]      
                 z=curve.data.splines[0].points[0].co.z
                 
                 if z < b:
                    
                    curve_list.append(element)
                 elif z > a:
                     
                     curve_list.insert(0,element)  
                 else:
                     i=0
                     while z>bpy.data.objects[curve_list[i]].data.splines[0].points[0].co.z:
                       i=i+1
                     
                     curve_list.insert(i+1,element)  
                              
             
           z_list=[]
           z_extrude=[]
           for element in curve_list:
              curve=bpy.data.objects[element]      
              z=curve.data.splines[0].points[0].co.z 
              z_list.append(z)           
           
           for i in range(len(z_list)-1):
             print(z_list[i])
             print(z_list[i+1])  
             z_extrude.append(z_list[i]-z_list[i+1])
             
                     
           z_extrude.append(bpy.context.scene.image_z_interval)
           
           return curve_list, z_list, z_extrude

def draw_gpencil_tools(context, layout):
    col = layout.column(align=True)

    col.label(text="Grease Pencil:")

    row = col.row()
    #row.operator("gpencil.draw", text="Draw").mode = 'DRAW'
    #row.operator("gpencil.draw", text="Erase").mode = 'ERASER'
    row.operator("object.draw", text="Draw")
    row.operator("object.erase", text="Erase")
    


def MakeBezierLine(objname, curvename, data_list):
   curve = bpy.data.curves.new(name=curvename, type='CURVE')  
   curve.dimensions = '2D'  
  
   curve_new = bpy.data.objects.new(objname, curve) 
   bpy.context.scene.objects.link(curve_new)
   
   points_to_add = len(data_list)-1
    
   flat_list = []
   for point in data_list:
       flat_list.extend(point)
                 
   spline = curve.splines.new(type="BEZIER")
   spline.bezier_points.add(points_to_add)
   spline.bezier_points.foreach_set("co", flat_list)
    
   for point in spline.bezier_points:
       point.handle_left_type="AUTO"
       point.handle_right_type="AUTO"
   return curve_new





def MakePolyLine(objname, curvename, cList):  
    w=1
    curvedata = bpy.data.curves.new(name=curvename, type='CURVE')  
    curvedata.dimensions = '2D'  
  
    curve_new = bpy.data.objects.new(objname, curvedata)  
    curve_new.location = (0,0,0) #object origin  
    bpy.context.scene.objects.link(curve_new)  
  
    polyline = curvedata.splines.new('POLY')  
    polyline.points.add(len(cList)-1)  
    for num in range(len(cList)):  
        x, y, z = cList[num]  
        polyline.points[num].co = (x, y, z, w)  
  
    polyline.order_u = len(polyline.points)-1
    polyline.use_endpoint_u = True
    return curve_new



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

def findPointMinDist(point1, point2):
       min_dist=float('inf') 

       a=(point1[0]-point2[0])*(point1[0]-point2[0])
       b=(point1[1]-point2[1])*(point1[1]-point2[1])
       c=(point1[2]-point2[2])*(point1[2]-point2[2])
       dist=math.sqrt(a+b+c)
       if (dist<min_dist):
            min_dist=dist
       return min_dist

def findPartialMinDist(point, obj):
      
    idx = [i.index for i in obj.data.vertices if i.select]
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

def findMeshesMinDist(obj1, obj2):
      
    idx1 = [i.index for i in obj1.data.vertices if i.select]
    idx2 = [i.index for i in obj2.data.vertices if i.select]
    if len(idx1)==0:
       idx1 = [i.index for i in obj1.data.vertices]
    if len(idx2)==0:
       idx2 = [i.index for i in obj2.data.vertices]
            
    min_dist=float('inf') 
    for v_index1 in idx1:
       vert_coordinate1 = obj1.data.vertices[v_index1].co  
       vert_coordinate1 = obj1.matrix_world * vert_coordinate1
       for v_index2 in idx2:
           vert_coordinate2 = obj2.data.vertices[v_index2].co  
           vert_coordinate2 = obj2.matrix_world * vert_coordinate2
           
           a=(vert_coordinate1[0]-vert_coordinate2[0])*(vert_coordinate1[0]-vert_coordinate2[0])
           b=(vert_coordinate1[1]-vert_coordinate2[1])*(vert_coordinate1[1]-vert_coordinate2[1])
           c=(vert_coordinate1[2]-vert_coordinate2[2])*(vert_coordinate1[2]-vert_coordinate2[2])
           
           dist=math.sqrt(a+b+c)
           if (dist<min_dist):
              min_dist=dist
    return min_dist

# delete object
def delThisObj(obj):
    bpy.data.objects[obj.name].select = True
    #bpy.ops.object.select_name(name=obj.name)
    bpy.context.scene.objects.active = obj
    print("deleting ",obj.name)
    bpy.ops.object.delete() 


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.distance_collection = bpy.props.CollectionProperty(type=DistanceListItem)
    bpy.types.Scene.distance_collection_index = bpy.props.IntProperty(min= -1,default= -1)

    pass
    
def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.distance_collection
    del bpy.types.Scene.distance_collection_index
    

    pass
    
if __name__ == "__main__":
    register()  
