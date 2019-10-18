import bpy
import bmesh
import imp

from mathutils import ( Matrix , Vector )

from . import utils
imp.reload(utils)


#オブジェクトをコレクションに移動
def move_collection( ob , col ):
    collections = ob.users_collection
    for c in collections:
         c.objects.unlink(ob)

    col.objects.link(ob)


def create_locator_collection():
    scn = bpy.context.scene
    colname = '09_ConstRoot'
    #コレクションが存在していればそのまま使用、なければ新規作成
    if colname in scn.collection.children.keys():
        col = scn.collection.children[colname]

    else:
        col = bpy.data.collections.new(colname)
        scn.collection.children.link(col)
    return col



def create_locator(name , matrix):

    col = create_locator_collection()

    #ロケータを作成
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    empty = bpy.context.active_object
    empty.name =  name + '_constlocator'
    empty.matrix_world = matrix

    move_collection(empty , col)
    

    #親のロケータを作成
    bpy.ops.object.empty_add(type='SPHERE')
    empty_p = bpy.context.active_object
    empty_p.name = name + '_parent'
    empty_p.matrix_world = Matrix()

    move_collection(empty_p , col)

    constraint =empty_p.constraints.new('COPY_TRANSFORMS')
    constraint.target = empty
    constraint.target_space ='WORLD'
    constraint.owner_space = 'WORLD'

    return empty_p


def replace_locator():
    selected = utils.selected()
    

    for obj in selected:
        # #ロケータを作成
        # bpy.ops.object.empty_add(type='PLAIN_AXES')
        # empty = bpy.context.active_object
        # empty.name =  obj.name + '_constlocator'
        # empty.matrix_world = obj.matrix_world

        # move_collection(empty , col)
        

        # #親のロケータを作成
        # bpy.ops.object.empty_add(type='SPHERE')
        # empty_p = bpy.context.active_object
        # empty_p.name = obj.name + '_parent'
        # empty_p.matrix_world = Matrix()

        # move_collection(empty_p , col)


        # constraint =empty_p.constraints.new('COPY_TRANSFORMS')
        # constraint.target = empty
        # constraint.target_space ='WORLD'
        # constraint.owner_space = 'WORLD'

        empty_p = create_locator(obj.name , obj.matrix_world)
        
        obj.matrix_world = Matrix()
        obj.parent = empty_p


#エディットモードで選択したフェースのノーマルを基準にロケータを生成する
#法線方向が(0,0,1)の時は例外処理する必要あり。内積をとって判定。
def replace_locator_facenormal():

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

    empty_p = create_locator(obj.name , matrix)

    #親子付けする前に逆変換しておいて親子付け時の変形を打ち消す
    mat_loc = Matrix.Translation([-x for x in pos])
    obj.matrix_world = m0.inverted().to_4x4() @ mat_loc
    
    obj.parent = empty_p
