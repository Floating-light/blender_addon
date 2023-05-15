

import bpy
from mathutils import *
from typing import List
import random
D = bpy.data
C = bpy.context
def draw_curve(start:Vector, end:Vector):

    arrow_length = 1
    normal_side = end.cross(start).normalized()
    normal_to_start = (start - end).normalized()
    arrow_pos1 = end + (normal_to_start + normal_side) * arrow_length
    arrow_pos2 = end + (normal_to_start - normal_side) * arrow_length
    arrow_pos3 = end

    points = [start, end,arrow_pos1,arrow_pos2,arrow_pos3]

    curve_data = bpy.data.curves.new(name="PolyLineCurve", type='CURVE')
    curve_data.dimensions = '3D'

    polyline = curve_data.splines.new('POLY')
    polyline.points.add(len(points) - 1)
    for i, point in enumerate(points):
        polyline.points[i].co = (point[0], point[1], point[2], 1.0)

    mt = bpy.data.materials.new("PolyLineCurveObject")
    mt.diffuse_color = (1,0,0,0)

    obj = bpy.data.objects.new(name="PolyLineCurveObject", object_data=curve_data)
    obj_mesh:bpy.types.Mesh = obj.data
    obj_mesh.materials.append(mt)
    
    bpy.context.scene.collection.objects.link(obj)
    return obj
def random_remove_selected_object(keep_percentage:float) -> int:
    '''
        if keep_percentage > 1, keep_percentage is the number of trisangles to keep 

        return the num of objects removed
    '''
    selected_objects = bpy.context.selected_objects
    random.shuffle(selected_objects)
    if keep_percentage > 1:
        tris_num_need_delete = sum((len(obj.data.polygons) for obj in selected_objects),0.0) - keep_percentage
        num_to_delete = 0
        tris_num_to_deleted = 0
        while num_to_delete <= len(selected_objects) and tris_num_to_deleted < tris_num_need_delete:
            tris_num_to_deleted += len(selected_objects[num_to_delete].data.polygons)
            num_to_delete+=1


    else: 
        num_to_delete = int(len(selected_objects) *(1-keep_percentage))
    deleted_list = selected_objects[0:int(num_to_delete)]
    # bpy.ops.object.delete({"selected_objects": objs})
    bpy.ops.object.delete({"selected_objects": deleted_list})
    return num_to_delete

def get_center_and_averge_normal(obj:bpy.types.Object):
    if obj is None or obj.type != 'MESH':
        print("Error the object type must be mesh")
        return 

    mesh:bpy.types.Mesh = obj.data

    center_average = sum((v.co for v in mesh.vertices), Vector()) / len(mesh.vertices)
    normal_average = Vector((0,0,0))
    for ind,poly in enumerate(mesh.polygons):
        if ind == 0:
            normal_average = poly.normal.normalized()
        else:
            normal_average += poly.normal.normalized()

    return obj.matrix_world @ center_average, normal_average
def find_object_axis(obj:bpy.types.Object, pivotPosition: Vector) -> Matrix:
    mesh:bpy.types.Mesh = obj.data
    pivot_world = obj.matrix_world @ pivotPosition
    center_position, Nv = get_center_and_averge_normal(obj)
    face_count = len(mesh.polygons)
    Rv = (pivot_world - center_position).normalized()
    # draw_curve(pivot_world, center_position)
    Uv = Nv.cross(Rv).normalized()
    Nv = -Uv.cross(Rv).normalized()
    
    # base = Nv.to_track_quat().to_matrix()
    # diff = (base @ Vector((1,0,0))).rotation_difference(-Rv)

    # rot = diff.to_matrix() @ base
    rot = Matrix([-Rv,-Uv,Nv])

    #  @ obj.matrix_world.to_3x3().normalized().to_4x4() 
    # 先旋转后平移
    # 要将轴移到pivotPosition，则需要pivotPosition位于Local空间的原点
    final = rot.to_4x4() @ obj.matrix_world.to_3x3().normalized().to_4x4() @ Matrix.Translation(- pivotPosition) 
    # @ rot.to_4x4()
    return final
def TEST_find_object_axis(obj:bpy.types.Object):
    pivot = find_pivot(obj)
    axis = find_object_axis(obj,pivot )
    xaxis = axis.inverted() @ Vector((-1,0,0))
    draw_curve(pivot, pivot - xaxis.normalized() * 15)

def process_object(Obj:int, V:bpy.types.MeshVertex):
    V.co
    context = bpy.context 
    scene = context.scene 
    ob = context.object 
    mw = ob.matrix_world 
    imw = mw.inverted() 
    me = ob.data 
    offset = Vector((0, 0, 3)) 
    me.transform(Matrix.Translation( -offset )) 
    ob.matrix_world.translation = mw @ offset
    pass
def find_pivot(obj:bpy.types.Object) -> Vector:
    '''
        return world space pivot 
    '''
    verts:List[bpy.types.MeshVertex] = obj.data.vertices
    
    # local space 
    coords = [v.co for v in verts]  

    min_z = coords[0][2]
    min_idx = 0
    for idx, val in enumerate(coords):        
        if val.z < min_z :
            min_z = val.z
            min_idx = idx
    return  coords[min_idx]
def find_pivot_average_bottom(obj:bpy.types.Object, delta_z:float) -> Vector:
    verts:List[bpy.types.MeshVertex] = obj.data.vertices
    
    # local space 
    verts_sorted = sorted(verts, key=lambda x:(obj.matrix_world@x.co).z, reverse=False)
    out_pivot:Vector = ((0,0,0))
    min_z:float = 0.0
    for idx, val in enumerate(verts_sorted):
        if idx == 0 :
            out_pivot = val.co
            min_z = (obj.matrix_world @ val.co).z
        else:
            if abs((obj.matrix_world @ val.co).z - min_z) <= delta_z:
                out_pivot = (out_pivot + val.co) / 2.0
            else:
                break
    return  out_pivot

def main():
    selected_objects = bpy.context.selected_objects

    for obj in selected_objects:
        obj.data
        print("===>>> ", obj.name_full)
        # print("matrix_world : ",obj.matrix_world)
        verts:List[bpy.types.MeshVertex] = obj.data.vertices
        
        RealVerts = [v.co for v in verts]
        # print("Vertex: ", RealVerts)
        coords = [obj.matrix_world @ v.co for v in verts]    
        # print("Cooridinate : ", coords)

        # min_z = min(coords, key=lambda c: c[2]) # 导致浮点数精度改变 -0.03561079874634743 -> -0.0356
        min_z = coords[0][2]
        min_idx = 0
        for idx, val in enumerate(coords):
            if val.z < min_z :
                min_z = val.z
                min_idx = idx
        
        final_position = coords[min_idx]

        # print("Final position ", final_position)

        T = Matrix.Translation(-verts[min_idx].co)
        obj.data.transform(T)
        obj.matrix_world.translation = coords[min_idx]
        
    print("-----------End script ")
def main2(deltaZ:float):
    selected_objects = bpy.context.selected_objects
    for ind, obj in enumerate(selected_objects):
        print("Process ", ind)
        pivot:Vector = ((0.0,0.0,0.0))
        if deltaZ > 0:
            pivot = find_pivot_average_bottom(obj, deltaZ)
        else:
            pivot = find_pivot(obj)
        pivot_world = obj.matrix_world @ pivot

        axis = find_object_axis(obj, pivot)
        inv = axis.inverted()

        obj.data.transform(axis)

        # print("matrix world ", obj.matrix_world)
        # 这里强制Copy一个，不然保存的是引用，后面乘的时候就有问题
        previous_mat = Matrix(obj.matrix_world)
        obj.matrix_world = previous_mat @ inv 
class OUTPOST_CreatePivot(bpy.types.Operator):
    bl_label = "Create Pivot"
    bl_idname = "ue4_tools.create_pivot"
    bl_description = "对选中的所有Mesh, 以其最底部的顶点为Pivot重新设置Pivot, 并将其Pivot的x axis的正方向设为朝向其Mesh的几何中心"
    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'
    def execute(self, context):
        print("execute my create pivot method ")
        pp = bpy.context.scene.pivot_painter
        main2(pp.pivotCalculateDeltaZ)
        return {'FINISHED'}
# main()
# TEST_find_object_axis(bpy.context.object)

if __name__ == "__main__":
    main2()