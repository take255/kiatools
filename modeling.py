import bpy
import bmesh
from mathutils import ( Matrix , Vector )
import imp


from . import utils
imp.reload(utils)


def del_half_x():
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='DESELECT')#全選択解除してからの
    bpy.ops.mesh.select_all(action='TOGGLE')#全選択

    bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(1, 0, 0), use_fill=False, clear_inner=True)
    bpy.ops.object.editmode_toggle()

    # bpy.ops.object.select_all(action='DESELECT')

    
    # bpy.ops.object.editmode_toggle()
    # bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(1, 0, 0), use_fill=True, clear_outer=True)
    # bpy.ops.object.editmode_toggle()    

#---------------------------------------------------------------------------------------
#reset pivot by selected face normal
#---------------------------------------------------------------------------------------
def pivot_by_facenormal():

    obj = bpy.context.edit_object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    upvector = Vector((0,0,1.0))
    upvector_x = Vector((-1.0,0,0))

    for f in bm.faces:
        if f.select:
            pos = f.calc_center_bounds()
            normal = f.normal

            #法線が(0,0,1)なら別処理
            d = normal.dot(upvector)

            if d > 0.99 or d < -0.99:
                xaxis = normal.cross(upvector_x)
                yaxis = xaxis.cross(normal)
            else:
                xaxis = normal.cross(upvector)
                yaxis = xaxis.cross(normal)

            normal.normalize()
            xaxis.normalize()
            yaxis.normalize()
            
            x = [x for x in xaxis] +[0.0]
            y = [x for x in yaxis] +[0.0]
            z = [x for x in normal] +[0.0]
            p = [x for x in pos] +[0.0]
            
            m0 = Matrix([xaxis,yaxis,normal])
            m0.transpose()

            matrix = Matrix([x , y , z , p])
            matrix.transpose()
 

    utils.mode_o()

    #empty_p = create_locator(obj.name , matrix)

    #親子付けする前に逆変換しておいて親子付け時の変形を打ち消す
    mat_loc = Matrix.Translation([-x for x in pos])
    obj.matrix_world = m0.inverted().to_4x4() @ mat_loc

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, properties=True)

    obj.matrix_world = Matrix.Translation(pos) @ m0.to_4x4()
    #obj.parent = empty_p