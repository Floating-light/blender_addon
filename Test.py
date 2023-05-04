import bpy
from mathutils import *
from typing import List
import bmesh
import bpy
from mathutils import Vector

def draw_curve(start:Vector, end:Vector, width, color):

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

def draw_arrow_right(start:Vector, end:Vector, color=(1, 0, 0,0)):
    # 计算箭头的向量
    vec = end - start
    arrow_length = 5
    normal_side = end.cross(start).normalized()
    normal_to_start = (start - end).normalized()
    arrow_pos1 = (normal_side + normal_to_start) * arrow_length
    arrow_pos2 = (normal_to_start - normal_side) * arrow_length
    arrow_pos3 = end

    vec.normalize()

    # 计算箭头的两个侧面向量
    up = Vector((0, 0, 1))
    if abs(up.dot(vec)) == 1:
        up = Vector((1, 0, 0))
    side1 = vec.cross(up).normalized()
    side2 = vec.cross(side1).normalized()

    # 定义箭头形状
    points = [start, end, end - vec * 0.2 - side1 * 0.1, end - vec * 0.2, 
              end - vec * 0.2 + side1 * 0.1, start]

    # 创建贝塞尔曲线对象
    curve = bpy.data.curves.new(name='Arrow', type='CURVE')
    curve.dimensions = '3D'

    # 创建曲线对象的路径
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)

    # 设置每个控制点的位置
    for i, coord in enumerate(points):
        x, y, z = coord
        spline.bezier_points[i].co = (x, y, z)

    # 创建曲线对象的材质
    material = bpy.data.materials.new(name='Arrow')
    material.diffuse_color = color

    # 创建曲线对象的网格对象
    obj = bpy.data.objects.new(name='Arrow', object_data=curve)
    obj.data.materials.append(material)

    # 将曲线对象添加到场景中
    bpy.context.scene.collection.objects.link(obj)

def main():
    ob = bpy.context.object
    # Loops per face
    for face in ob.data.polygons:
        for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
            uv_coords = ob.data.uv_layers.active.data[loop_idx].uv
            print("face idx: %i, vert idx: %i, uvs: %f, %f" % (face.index, vert_idx, uv_coords.x, uv_coords.y))
def SetActivateUVChannel():
    # 获取选中的对象列表
    selected_objects = bpy.context.selected_objects

    # 遍历选中的对象
    for obj in selected_objects:
        # 检查对象是否为 Mesh
        if obj.type == 'MESH':
            # 获取对象的 UV 图层列表
            uv_layers = obj.data.uv_layers
            # 设置 UV 通道 1 为激活的图层
            if len(uv_layers) >= 1:
                obj.data.uv_layers.active_index = 1
def draw_arrow(from_vec, to_vec, color):
    head_length = (to_vec - from_vec).length * 0.2
    head_size = head_length * 0.5
    bpy.ops.curve.primitive_bezier_curve_add(location=from_vec)
    bpy.ops.curve.primitive_bezier_curve_add(location=to_vec)
    curve = bpy.context.object.data
    curve.splines[0].bezier_points[0].co = from_vec
    curve.splines[0].bezier_points[0].handle_right = from_vec + Vector((head_size, 0, 0))
    curve.splines[0].bezier_points[1].co = to_vec
    curve.splines[0].bezier_points[1].handle_left = to_vec - Vector((head_size, 0, 0))
    curve.splines[0].bezier_points[0].handle_right_type = 'VECTOR'
    curve.splines[0].bezier_points[1].handle_left_type = 'VECTOR'
    curve.splines[0].bezier_points[0].handle_right_type = 'VECTOR'
    curve.splines[0].bezier_points[1].handle_left_type = 'VECTOR'
    curve.splines[0].bezier_points[0].handle_right = from_vec + Vector((0, head_size, 0))
    curve.splines[0].bezier_points[1].handle_left = to_vec - Vector((0, head_size, 0))
    curve.splines[0].bezier_points[0].handle_right_type = 'VECTOR'
    curve.splines[0].bezier_points[1].handle_left_type = 'VECTOR'
    curve.splines[0].bezier_points[0].handle_right_type = 'VECTOR'
    curve.splines[0].bezier_points[1].handle_left_type = 'VECTOR'
    material = bpy.data.materials.new('Debug Arrow Material')
    material.diffuse_color = color
    curve.materials.append(material)
def draw_arrow2(from_coord, to_coord):
    # 线的起点坐标
    x1, y1, z1 = from_coord
    # 线的终点坐标
    x2, y2, z2 = to_coord

    # 画线
    bpy.context.scene.cursor.location = (x1, y1, z1)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.curve.primitive_bezier_curve_add()
    curve_obj = bpy.context.object
    curve_obj.data.splines.active.type = 'POLY'
    curve_obj.data.splines.active.points.add(1)
    curve_obj.data.splines.active.points[0].co = (x1, y1, z1, 1)
    curve_obj.data.splines.active.points[1].co = (x2, y2, z2, 1)
    curve_obj.data.bevel_depth = 0.01
    curve_obj.data.bevel_resolution = 2
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.curve.select_all(action='SELECT')
    bpy.ops.curve.handle_type_set(type='VECTOR')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.cursor.location = (0, 0, 0)
def draw_debug_arrow(location, direction, arrow_size=1.0, arrow_length=1.0):
    '''
    在3D视图中绘制一个箭头，用于调试。该箭头从指定的位置出发，沿着指定方向。

    Args:
        location: Vector, 箭头起点的位置
        direction: Vector, 箭头的方向
        arrow_size: float, 箭头尾部宽度
        arrow_length: float, 箭头长度
    '''
    # 绘制箭头尾部
    bpy.ops.mesh.primitive_cylinder_add(radius=arrow_size, depth=1.0, location=location)
    cylinder = bpy.context.object
    cylinder.scale = Vector((1, 1, arrow_length))
    cylinder.rotation_mode = 'QUATERNION'
    cylinder.rotation_quaternion = direction.to_track_quat('Z', 'Y')

    # 绘制箭头头部
    bpy.ops.mesh.primitive_cone_add(radius1=arrow_size*2, radius2=0, depth=arrow_size*4, location=location + direction*arrow_length)
    cone = bpy.context.object
    cone.rotation_mode = 'QUATERNION'
    cone.rotation_quaternion = direction.to_track_quat('Z', 'Y')

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
def TEST_get_center_and_averge_normal():
    obj = bpy.context.object
    center_position, normal_world = get_center_and_averge_normal(obj)
    draw_curve(center_position, center_position + normal_world.normalized() * 15, 0.5,(1,0,0,0))

def TestGetMesh():
    obj = bpy.context.object
    if obj is not None and obj.type != 'MESH':
        return 
    print("data type : ", obj.type)

    mesh:bpy.types.Mesh = obj.data
    ind = 0
    print("polygon len {}".format(len(mesh.polygons)))
    for poly in  mesh.polygons:
        face_normal = poly.normal.normalized()
        normal_world = face_normal
        center_position =obj.matrix_world @ poly.center
        print("{} normal world {}, center position {}".format(ind, normal_world,center_position))
        draw_curve(center_position, center_position + normal_world.normalized() * 15, 0.5,(1,0,0,0))
        ind += 1
def Method2():
    obj = bpy.context.object
    mesh = bpy.context.object.data
    my_bmesh = bmesh.new()
    my_bmesh.from_mesh(mesh)
    # my_bmesh.faces.ensure_lookup_table()
    for face in my_bmesh.faces:
    # ind = 0
    # face = my_bmesh.faces[0]
        ind = 0
        print("face " , ind)
        normal_world = obj.matrix_world @ face.normal 
        center_position = obj.matrix_world @ face.verts[0].co
        if ind == 0:
            print("draw ")
            dir_with_length = normal_world * 100
            bgl = bpy.context.space_data.overlay.bgl
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glColor4f(1, 0, 0, 1)
            bgl.glLineWidth(2)
            bgl.glBegin(bgl.GL_LINES)
            bgl.glVertex3f(*center_position)
            bgl.glVertex3f(*(center_position + dir_with_length))
            bgl.glEnd()
            bgl.glBegin(bgl.GL_TRIANGLES)
            bgl.glVertex3f(*(center_position + dir_with_length))
            bgl.glVertex3f(*(center_position + dir_with_length - Vector((0.2, 0, 0.2))))
            bgl.glVertex3f(*(center_position + dir_with_length - Vector((-0.2, 0, 0.2))))
            bgl.glEnd()
            bgl.glDisable(bgl.GL_BLEND)

TEST_get_center_and_averge_normal()

# TestGetMesh()
# draw_curve(Vector((0, 0, 0)), Vector((100,100,100)), 1,(1,0,0,0))
# draw_arrow_right(Vector((0, 0, 0)), Vector((100,100,100)))