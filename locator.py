import bpy
import bmesh
import imp

from mathutils import ( Matrix , Vector )

from . import utils
imp.reload(utils)

#---------------------------------------------------------------------------------------
#モデルに位置にロケータを配置してコンストレインする。
#中間にロケータをかます。親のロケータの形状をsphereにする。
#モデルのトランスフォームは初期値にする
#ロケータを '09_ConstRoot'　に入れる
#コレクションをインスタンスに差し替える関数追加
#---------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------
#オブジェクトをコレクションに移動
#---------------------------------------------------------------------------------------
def move_collection( ob , col ):
    collections = ob.users_collection
    for c in collections:
         c.objects.unlink(ob)

    col.objects.link(ob)


#---------------------------------------------------------------------------------------
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


#---------------------------------------------------------------------------------------
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

#---------------------------------------------------------------------------------------
#replace : オブジェクトをロケータの子供にして扱いやすくする
#選択モデルをロケータに親子付けをしてコンストレイン。
#---------------------------------------------------------------------------------------
def replace():
    selected = utils.selected()
    
    for obj in selected:
        empty_p = create_locator(obj.name , obj.matrix_world)
        
        obj.matrix_world = Matrix()
        obj.parent = empty_p


#---------------------------------------------------------------------------------------
#エディットモードで選択したフェースのノーマルを基準にロケータを生成する
#法線方向が(0,0,1)の時は例外処理する必要あり。内積をとって判定。
#---------------------------------------------------------------------------------------
def replace_facenormal():

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

#---------------------------------------------------------------------------------------
#選択したモデルをロケータでまとめる
#アクティブなモデルの名前を継承する
#---------------------------------------------------------------------------------------
def group():
    selected = utils.selected()
    act = utils.getActiveObj()
    locatorname = act.name + '_parent'

    bpy.ops.object.empty_add(type='PLAIN_AXES')
    empty = utils.getActiveObj()
    empty.name = locatorname
    empty.matrix_world = Matrix()

    for obj in selected:
        obj.parent = empty


#---------------------------------------------------------------------------------------
def preserve_child():
    selected = utils.selected()

    for obj in selected:
        #一時的に退避するロケータを作成
        name = '%s_temp' % obj.name
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        empty = utils.getActiveObj()
        empty.name = name
        for child in obj.children:
            m = child.matrix_world
            child.parent = empty
            child.matrix_world = m

    utils.multiSelection(selected)    


#---------------------------------------------------------------------------------------
def restore_child():
    selected = utils.selected()
    objects = bpy.context.scene.objects

    #selected = bpy.context.selected_objects
    for obj in selected:
        #一時的に退避するロケータを作成
        tmpname = '%s_temp' % obj.name
        
        for child in objects[tmpname].children:
            m = child.matrix_world
            child.parent = obj
            child.matrix_world = m

        utils.delete(objects[tmpname])

    utils.multiSelection(selected) 


#---------------------------------------------------------------------------------------
#コレクションをインスタンス化
#元モデルを原点にもってくる。選択したモデルをピボットとし、メンバーになっているコレクションを対象
#---------------------------------------------------------------------------------------
def instancer():
    col = bpy.context.scene.collection

    #選択したオブジェクトのコレクションを選択
    #回転matrixと位置vectorに分ける
    act = utils.getActiveObj()
    pos_act = Vector(act.location) 
    m_rot = act.matrix_world.to_3x3()
    m_rot.invert()

    matrix = Matrix(act.matrix_world)
    col_selected = act.users_collection[0]


    #平行移動
    for ob in col_selected.objects:
        ob.location -= pos_act

    #回転
    for ob in col_selected.objects:
        pos = Vector(ob.location)
        pos_new = m_rot @ pos
        print (ob.name , ob.location , pos)
        m = m_rot @ ob.matrix_world.to_3x3()
        ob.matrix_world = m.to_4x4()
        ob.location = pos_new

    #インスタンス　空オブジェクトを作成
    instance = bpy.data.objects.new(col_selected.name , None)
    instance.instance_collection = col_selected
    instance.instance_type = 'COLLECTION'
    instance.matrix_world  = matrix

    col.objects.link(instance)


#---------------------------------------------------------------------------------------
#軸変換　まず　x->y　を作ってみる
#1．原点において意図する姿勢にしたあとapplyする
#2. 元の状態に戻す。この場合軸を入れ替えた状態のマトリックスにする
#---------------------------------------------------------------------------------------
def swap_axis():
    act = utils.getActiveObj()
    matrix = act.matrix_world.to_3x3()
    pos = Vector(act.location)

    #第一段階
    m = Matrix(((-1,0,0),(1,0,0),(0,0,1)))
    m.transpose()
    act.matrix_world = m.to_4x4()

    bpy.ops.object.transform_apply( location = True , rotation=True , scale=True )
    
    
    #第二段階　転置して成分分離
    matrix.transpose()
    print(matrix)
    y = -matrix[0]
    x =  matrix[1]
    z =  matrix[2]

    m = Matrix((x,y,z))

    m.transpose()
    act.matrix_world = m.to_4x4()
    act.location = pos

CONST_PARAM_LOC_SOURCE = ( ( -100, 100),( -100, 100 ),( -100, 100) )
CONST_PARAM_LOC_DEST = ( ( 100, -100),( -100, 100 ),( -100, 100) )
CONST_PARAM_ROT_SOURCE = ( ( -3.14, 3.14),( -3.14 , 3.14 ),( -3.14 , 3.14 ) )
CONST_PARAM_ROT_DEST = ( ( -3.14, 3.14),( 3.14 , -3.14 ),( 3.14 , -3.14 ) )

CONST_PARAM_LOC_SOURCE_Y = ( ( -100, 100),( -100, 100 ),( -100, 100) )
CONST_PARAM_LOC_DEST_Y = ( ( -100, 100),( 100, -100 ),( -100, 100) )
CONST_PARAM_ROT_SOURCE_Y = ( ( -3.14, 3.14),( -3.14 , 3.14 ),( -3.14 , 3.14 ) )
CONST_PARAM_ROT_DEST_Y = ( ( 3.14, -3.14),( -3.14 , 3.14 ),( 3.14 , -3.14 ) )


#---------------------------------------------------------------------------------------
#オブジェクトをインスタンスしてX軸でミラーコンストレインする
#---------------------------------------------------------------------------------------
def mirror(axis):
    ob_source = utils.getActiveObj()
    bpy.ops.object.duplicate_move_linked()

    ob_target = utils.getActiveObj()
    ob_target.matrix_world = Matrix()

    if axis == 'x':
        const_setting( ob_source , ob_target , CONST_PARAM_LOC_SOURCE , CONST_PARAM_LOC_DEST ,'LOCATION' ,'' )
        const_setting( ob_source , ob_target , CONST_PARAM_ROT_SOURCE , CONST_PARAM_ROT_DEST ,'ROTATION' ,'_rot')
        const_setting( ob_source , ob_target , CONST_PARAM_LOC_SOURCE , CONST_PARAM_LOC_DEST ,'SCALE' ,'_scale')

    if axis == 'y':
        const_setting( ob_source , ob_target , CONST_PARAM_LOC_SOURCE_Y , CONST_PARAM_LOC_DEST_Y ,'LOCATION' ,'' )
        const_setting( ob_source , ob_target , CONST_PARAM_ROT_SOURCE_Y , CONST_PARAM_ROT_DEST_Y ,'ROTATION' ,'_rot')
        const_setting( ob_source , ob_target , CONST_PARAM_LOC_SOURCE_Y , CONST_PARAM_LOC_DEST_Y ,'SCALE' ,'_scale')



def const_setting( ob_source , ob_target , source , dest , maptype , suffix ):
    constraint =ob_target.constraints.new('TRANSFORM')
    constraint.target = ob_source
    constraint.map_from = maptype
    constraint.map_to = maptype

    for x,val in zip(( 'x' , 'y' , 'z' ) , source ):
        exec('constraint.from_min_%s%s = %02f' % (x , suffix , val[0]) )
        exec('constraint.from_max_%s%s = %02f' % (x , suffix , val[1]) )

    for x,val in zip(( 'x' , 'y' , 'z' ),dest):
        exec('constraint.to_min_%s%s = %02f' % ( x , suffix , val[0]) )
        exec('constraint.to_max_%s%s = %02f' % ( x , suffix , val[1]) )













