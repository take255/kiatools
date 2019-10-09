from bpy.types import Panel
import bpy

class panel(Panel):   
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'#2.79から修正
    bl_category ='Tool'
    bl_options = {'DEFAULT_CLOSED'}

icon = {
    'OBJECT':'OBJECT_DATA',
    'ADD':'ADD',
    'REMOVE':'REMOVE',
    'UP':'TRIA_UP_BAR',
    'DOWN':'TRIA_DOWN_BAR',
    'CANCEL':'CANCEL',
    'SELECT':'RESTRICT_SELECT_OFF',
    'BONE':"BONE_DATA"
    }

def activeObj(ob):
     bpy.context.view_layer.objects.active = ob

def getActiveObj():
    return bpy.context.active_object
    
def select(ob,state):
     ob.select_set(state=state)

def delete(ob):
     bpy.ops.object.select_all(action='DESELECT')
     select(ob,True)
     bpy.ops.object.delete()

#選択をすべて解除して最後のオブジェクトをアクティブにする
def multiSelection(objarray):
     if len(objarray) == 0:return
     bpy.ops.object.select_all(action='DESELECT')
     for ob in objarray:
          select(ob,True)

     activeObj(objarray[0])

def deselectAll():
     bpy.ops.object.select_all(action='DESELECT')

def selectByName(obname,state):
    bpy.data.objects[obname].select_set(state=state)

def objectByName(obname):
    return bpy.data.objects[obname]

def showhide(ob,state):
     bpy.data.objects[ob.name].hide_viewport = state

def sceneLink(ob):
     bpy.context.scene.collection.objects.link(ob)

def sceneUnlink(ob):
     bpy.context.scene.collection.objects.unlink(ob)

#パブリッシュシーンをアクティブに
def sceneActive(fix_scene):
     scn = bpy.data.scenes[fix_scene]
     bpy.context.window.scene = scn
     return scn

def selected():
    return bpy.context.selected_objects

#UV meshデータを入れると新規UVを返す
def UV_new(mesh_data):
     return mesh_data.uv_layers.new()

#カーソルを原点に
def cursorOrigin():
     #bpy.context.space_data.pivot_point = 'CURSOR'
     bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
     bpy.context.scene.cursor.location = (0,0,0)

def mirrorBoneXaxis():
     bpy.ops.transform.mirror(orient_type='GLOBAL', constraint_axis=(True, False, False))


#マテリアル関連
#ノーマルマップイメージのカラースペース指定
def nmt_colorspace(node):
     node.image.colorspace_settings.name = 'Non-Color'


#マトリックスの掛け算
def m_mul(m0,m1):
     return m0 @ m1


#モード
def mode_e():
     bpy.ops.object.mode_set(mode = 'EDIT')

def mode_o():
     bpy.ops.object.mode_set(mode = 'OBJECT')
