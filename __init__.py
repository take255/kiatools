import bpy
from bpy.types import ( PropertyGroup , Panel)
from bpy.app.handlers import persistent
import imp

from bpy.props import(
    PointerProperty,
    IntProperty,
    BoolProperty,
    StringProperty,
    CollectionProperty,
    FloatProperty,
    EnumProperty
    )

from . import utils
from . import modifier

imp.reload(utils)
imp.reload(modifier)

bl_info = {
"name": "kiatools",
"author": "kisekiakeshi",
"version": (0, 1),
"blender": (2, 80, 0),
"description": "kiatools",
"category": "Object"}


from . import object_applier
#from . import modifier
from . import modeling

imp.reload(object_applier)
#imp.reload(modifier)
imp.reload(modeling)


@persistent
def kiatools_handler(scene):
    # props = bpy.context.scene.kiatools_oa
    # scene = props.prop
    # bpy.context.window.scene = bpy.data.scenes[scene]
    # #set_current_scene()    
    # print('----------------------------')
    # print(scene)
    # print('----------------------------')
    # #props = bpy.context.scene.kiatools_oa
    # props.allscene.clear()        
    # for scn in bpy.data.scenes:
    #     props.allscene.add().name = scn.name

    # print(scene)
    # print('----------------------------')
    # bpy.context.scene.kiatools_oa.prop = scene
    pass


#ob　が　selectedの子供かどうか調べる。孫以降も調査。
def isParent(ob , selected):
    parent = ob.parent
    if parent == None:
        return False

    if parent in selected:
        return True
    else:
        isParent(parent , selected)


#シーンを追加したとき、それぞれのシーンにあるシーンリストを更新してあげる必要がある
def go_scene(self,context):
    props = bpy.context.scene.kiatools_oa
    scene = props.scene_name
    bpy.context.window.scene = bpy.data.scenes[scene]
    count = len(bpy.data.scenes)

    #シーンを変更したので、propsを読み直し
    props = bpy.context.scene.kiatools_oa
    if props.scene_name != scene:
        props.scene_name = scene

    #シーンを追加した場合、シーンのコレクションプロパティとの差が生じてしまっているので修正
    if len(props.allscene) != count:
        props.allscene.clear()        
        for scn in bpy.data.scenes:
            props.allscene.add().name = scn.name       

    if len(props.target_allscene) != count:
        props.target_allscene.clear()        
        for scn in bpy.data.scenes:
            props.target_allscene.add().name = scn.name       


#選択したコンストレインの表示、非表示
#その際、選択オブジェクトにフォーカスする
#

def showhide_constraint(self,context):
    props = bpy.context.scene.kiatools_oa
    selected = utils.selected()
    act = utils.getActiveObj()

    for ob in selected:
        utils.activeObj(ob)
        for const in ob.constraints:
            const.mute = props.const_bool

            #muteオンオフだけではコンストレインがアップデートされない問題
            #この行の追加で解消
            const.influence = 1.0 


    #表示されているならセレクトする    
    for ob in bpy.data.objects: 
        if ob.parent in selected: 
            if bpy.data.objects[ob.name].visible_get():
                utils.select(ob,True)
            #children.append(ob) 
        
    bpy.ops.view3d.view_selected(use_all_regions = False)

    #utils.deselectAll()
    utils.multiSelection(selected)
    utils.activeObj(act)


#ＯＮで現在の表示状態を保持しておき選択モデルだけ表示、ＯＦＦでもとに戻す
def showhide_object(self,context):
    props = bpy.context.scene.kiatools_oa    
    selected = utils.selected()

    #選択以外をハイド
    if props.showhide_bool:
        props.displayed_allobjs.clear()
        #すべてのオブジェクトの表示状態を保持して、選択状態でなければハイドする
        for ob in bpy.data.objects:
            if bpy.data.objects[ob.name].visible_get():
                props.displayed_allobjs.add().name = ob.name

                if not ob in selected: 
                    if not isParent(ob , selected): 
                        ob.hide_viewport = True
                    else:
                        utils.select(ob,True)
                
    
    #表示をもとに戻す
    else:
        for ob in props.displayed_allobjs:
            bpy.data.objects[ob.name].hide_viewport = False
            #utils.select(ob,True)

        if not ob in selected: 
            if isParent(ob , selected): 
                utils.selectByName(ob,True)

    
    bpy.ops.view3d.view_selected(use_all_regions = False)
    utils.deselectAll()
    utils.multiSelection(selected)


#モディファイヤの値調整
#Solidifyの厚み　、Shrinkwrapオフセット、ベベル幅調整　、アレイの個数
# def modifier_apply(self,context):
#     act = utils.getActiveObj()
#     props = bpy.context.scene.kiatools_oa
    
#     print(props.mod_init)
#     if props.mod_init:
#         props.mod_init = False
#         return

#     for mod in act.modifiers:
#         if mod.type == 'SOLIDIFY':
#             mod.thickness = props.solidify_thickness

#         if mod.type == 'ARRAY':
#             mod.count = props.array_count

#         if mod.type == 'BEVEL':
#             mod.width = props.bevel_width

#         if mod.type == 'SHRINKWRAP':
#             mod.offset = props.shrinkwrap_offset


MODIFIER_TYPE = ( ('LATTICE','LATTICE','') , ('SHRINKWRAP','SHRINKWRAP','') , ('CURVE','CURVE',''))



class KIATOOLS_Props_OA(bpy.types.PropertyGroup):
    #アプライオプション
    deleteparticle_apply : BoolProperty(name="delete particle" ,  default = False)
    keephair_apply : BoolProperty(name="keep hair" ,  default = False)
    keeparmature_apply : BoolProperty(name="keep armature" ,  default = False)
    merge_apply : BoolProperty(name="merge" ,  default = True)

    #シーン名 currentsceneに現在のシーン名を保存しておき、
    scene_name : StringProperty(name="Scene", maxlen=63 ,update = go_scene)
    allscene : CollectionProperty(type=PropertyGroup)

    target_scene_name : StringProperty(name="Target", maxlen=63 ,update = go_scene)
    target_allscene : CollectionProperty(type=PropertyGroup)

    #モデリング関連:showhide_bool 選択したオブジェクトだけ表示
    const_bool : BoolProperty(name="mute const" , update = showhide_constraint)

    showhide_bool : BoolProperty(name="showhide" , update = showhide_object)
    displayed_obj : StringProperty(name="Target", maxlen=63)    
    displayed_allobjs : CollectionProperty(type=PropertyGroup)


    #モディファイヤ関連
    # mod_init :モデリングツールを起動したときmodifier_applyが走らないようにする
    mod_init : BoolProperty(default = True)

    # modifier_name : StringProperty(name="Target", maxlen=63 ,update = go_scene)
    # target_allscene : CollectionProperty(type=PropertyGroup)
    modifier_type : EnumProperty(items = MODIFIER_TYPE , name = 'modifier')

    solidify_thickness : FloatProperty(
        name = "Solidify_thick",
        description = "Soliifyの厚みを調整する",
        min=-1.0,
        max=1.0,
        default=0.01,
        precision = 4,
        step = 0.1,        
        update=modifier.apply)

    shrinkwrap_offset : FloatProperty(
        name = "wrap_ofset",
        description = "Shrinkwrapのオフセットを調整する",
        min=0,
        max=1.0,
        default=0.01,
        precision = 4,
        step = 0.1,
        update=modifier.apply)

    bevel_width : FloatProperty(
        name = "Bevel_width",
        description = "Bevel幅を調整する",
        min=0,
        max=0.5,
        default=0.1,
        precision = 4,
        step = 0.1,
        update=modifier.apply)

    array_count : IntProperty(
        name = "Array_num",
        description = "アレイの数調整",
        min=1,
        max=200,
        default=1,
        step = 1,
        update=modifier.apply)

    array_offset_x : FloatProperty(name = "x", update=modifier.apply)
    array_offset_y : FloatProperty(name = "y",  update=modifier.apply)
    array_offset_z : FloatProperty(name = "z",  update=modifier.apply)



class KIAToolsPanel(utils.panel):   
    bl_label ='KIAtools'
    def draw(self, context):
        self.layout.operator("kiatools.object_applier", icon='BLENDER')
        self.layout.operator("kiatools.modelingtools", icon='BLENDER')


classes = (
    KIATOOLS_Props_OA,
    KIAToolsPanel
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.kiatools_oa = PointerProperty(type=KIATOOLS_Props_OA)

    object_applier.register()
    #modifier.register()
    modeling.register()
    bpy.app.handlers.depsgraph_update_pre.append(kiatools_handler)


def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)

    del bpy.types.Scene.kiatools_oa

    object_applier.unregister()
    #modifier.unregister()
    modeling.unregister()
    bpy.app.handlers.depsgraph_update_pre.remove(kiatools_handler)



 
