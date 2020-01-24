import bpy
import bmesh
import imp
import math

from mathutils import ( Matrix , Vector )

from . import utils
imp.reload(utils)


def bone_chain_loop( bone , chain ,vtxarray ,bonenamearray):
    amt = bpy.context.active_object
    for b in amt.data.edit_bones:
        if b.parent == bone:
            chain.append(b.name)
            bonenamearray.append(b.name)
            vtxarray.append(b.tail)
            bone_chain_loop(b,chain ,vtxarray,bonenamearray)
            

#ジョイントのクラスタからメッシュを作成
#
def create_mesh_from_bone():
    props = bpy.context.scene.kiatools_oa
    amt = bpy.context.object
    selected = bpy.context.selected_bones
    num_col = 0
    num_row = len(selected)


    #頂点座標の配列生成
    #最初のボーンのheadだけの座標を入れれば、残りはtailの座標だけ入れていけばOK
    vtxarray = []

    bonenamearray = []
    chainarray = []
    for bone in selected:
        chain = [bone.name]
        bonenamearray.append(bone.name)
        vtxarray += [bone.head , bone.tail ]
        bone_chain_loop( bone , chain ,vtxarray ,bonenamearray)
        num_col = len(chain)
        chainarray.append(chain)

    polyarray = []
    ic = num_col + 1 #コラムの増分

    #ポリゴンのインデックス生成
    #円筒状にしたくない場合はrowを１つ減らす
    if props.cloth_open:
        row = num_row -1
    else:
        row = num_row

    for c in range(row):
        array = []
        for r in range(num_col):
            #シリンダ状にループさせたいので、最後のrowは一番目のrowを指定
            if c == num_row - 1:
                array = [
                    r + ic*c ,
                    r + 1 + ic*c ,
                    r + 1  ,
                    r 
                    ]

            else:
                array = [
                    r + ic*c ,
                    r + 1 + ic*c ,
                    r + 1 + ic*(c + 1) ,
                    r + ic*(c + 1)
                    ]

            polyarray.append(array)
    
    #メッシュの生成
    mesh_data = bpy.data.meshes.new("cube_mesh_data")
    mesh_data.from_pydata(vtxarray, [], polyarray)
    mesh_data.update()


    obj = bpy.data.objects.new('test', mesh_data)

    scene = bpy.context.scene
    utils.sceneLink(obj)
    utils.select(obj,True)


    #IKターゲットの頂点グループ作成    
    #ウェイト値の設定
    for j,chain in enumerate(chainarray):
        for i,bone in enumerate(chain):
            obj.vertex_groups.new(name = bone)
            index = 1 + i + j * (num_col+1)

            vg = obj.vertex_groups[bone]
            vg.add( [index], 1.0, 'REPLACE' )


    #IKのセットアップ
    utils.mode_o()
    utils.act(amt)
    utils.mode_p()


    for j,chain in enumerate(chainarray):
        for i,bone in enumerate(chain):

            jnt = amt.pose.bones[bone]
            c = jnt.constraints.new('IK')
            c.target = obj
            c.subtarget = bone
            c.chain_count = 1


    #クロスの設定
    #ピンの頂点グループを設定する
    pin = 'pin'
    obj.vertex_groups.new(name = pin)
    for c in range(num_row):
        index =  c * ( num_col + 1 )
        vg = obj.vertex_groups[pin]
        vg.add( [index], 1.0, 'REPLACE' )


    #bpy.ops.object.modifier_add(type='CLOTH')
    mod = obj.modifiers.new("cloth", 'CLOTH')
    mod.settings.vertex_group_mass = "pin"

#---------------------------------------------------------------------------------------
#ローカル軸で回転
#マトリックスの値を入れても描画が更新されないので位置を入れなおすことで回避
#---------------------------------------------------------------------------------------
def transform_rotate_axis(axis):
    selected = utils.selected()
    for ob in selected:
        utils.activeObj(ob)
        loc = Vector(ob.location)
        m = ob.matrix_local.to_3x3()
        m.transpose()
        
        #m0 = transpose(m)
        if axis == 'x90d':
            m0 = Matrix([ m[0] , -m[2] , m[1]])
        elif axis == 'x-90d':
            m0 = Matrix([ m[0] , m[2] , -m[1]])
        elif axis == 'y90d':
            m0 = Matrix([ -m[2] , m[1] , m[0]])
        elif axis == 'y-90d':
            m0 = Matrix([ m[2] , m[1] , -m[0]])
        elif axis == 'z90d':
            m0 = Matrix([ -m[1] , m[0] , m[2]])
        elif axis == 'z-90d':
            m0 = Matrix([ m[1] , -m[0] , m[2]])

        elif axis == 'x180d':
            m0 = Matrix([ m[0] , -m[1] , -m[2]])
        elif axis == 'y180d':
            m0 = Matrix([ -m[0] , m[1] , -m[2]])
        elif axis == 'z180d':
            m0 = Matrix([
                -m[0] , -m[1] , m[2]])

        m0.transpose()            
        ob.matrix_local = m0.to_4x4()
        ob.location = loc

#---------------------------------------------------------------------------------------
#スケールを正にする
#---------------------------------------------------------------------------------------
def transform_scale_abs():
    for ob in utils.selected():
        s = ob.scale
        ob.scale = (math.fabs(s[0]), math.fabs(s[1]), math.fabs(s[2]))


#---------------------------------------------------------------------------------------
#ボーンにコンストレイン
#選択されているボーンでコンストレインする。モデル、アーマチュアの順に選択し、Editモードでボーンを選択して実行する。
#---------------------------------------------------------------------------------------
def constraint_to_bone():
    selected = utils.selected()
    amt = [x for x in selected if x.type == 'ARMATURE']

    #選択されたボーンを取得
    result = []
    for bone in utils.get_selected_bones():
        result.append(bone.name)    

    #アーマチュアをエディットモードのままにしておくと選択がおかしくなるのでいったん全選択解除
    #bpy.ops.object.select_all(action='DESELECT')
    utils.mode_o()
    utils.deselectAll()

    for obj in selected:
        if obj.type != 'ARMATURE':

            utils.activeObj(obj)                    
            constraint =obj.constraints.new('COPY_TRANSFORMS')
            constraint.target = amt[0]
            constraint.subtarget = result[0]
            constraint.target_space ='WORLD'
            constraint.owner_space = 'WORLD'

            utils.select(obj,True)

#---------------------------------------------------------------------------------------
#リファレンス関連
#---------------------------------------------------------------------------------------
def refernce_make_proxy():
    selected = utils.selected()
    bpy.ops.object.select_all(action = 'TOGGLE')

    for ob in selected:
        utils.activeObj(ob)
        bpy.ops.object.proxy_make()
        bpy.ops.object.select_all(action = 'TOGGLE')

def refernce_make_link():
        #print(self.filepath)
        #path = 'D:/data/blender_ref/human_rig/model/'
        #source = 'D:/projects/_model/character/model/human_rig.blend'
        source = bpy.data.filepath#カレントファイルパス
        filename = source.split('.')[0].split('\\')[-1]
        print(source)
        for i in range(10):
            new = '%s%s_%03d.blend' % (self.filepath , filename , i)
##            print(new)
##            os.symlink(source,new)

            cmd = 'mklink %s %s' %(new,source)
            subprocess.Popen(cmd,shell=True)


