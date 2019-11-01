import bpy
import bmesh
import imp
import math

from mathutils import ( Matrix , Vector )

from . import utils
imp.reload(utils)


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
            m0 = Matrix([-m[0] , -m[1] , m[2]])

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


