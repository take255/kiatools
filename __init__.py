import bpy
from bpy.types import ( PropertyGroup , Panel)
from bpy.app.handlers import persistent
import imp

from bpy.props import(
    PointerProperty,
    IntProperty,
    BoolProperty,
    StringProperty,
    CollectionProperty
    )

from . import utils
imp.reload(utils)

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
        isParent(parent , parent)


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
def showhide_constraint(self,context):
    props = bpy.context.scene.kiatools_oa
    
    selected = utils.selected()

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
                
        # for ob in selected:
        #     ob.hide_viewport = False

    #表示をもとに戻す
    else:
        for ob in props.displayed_allobjs:
            #print(ob.name)
            #ob.hide_viewport = False
            bpy.data.objects[ob.name].hide_viewport = False



    # for ob in selected:
    #     utils.activeObj(ob)
    #     for const in ob.constraints:
    #         const.mute = props.const_bool

    #         #muteオンオフだけではコンストレインがアップデートされない問題
    #         #この行の追加で解消
    #         const.influence = 1.0 


    # #表示されているならセレクトする    
    # for ob in bpy.data.objects: 
    #     if ob.parent in selected: 
    #         if bpy.data.objects[ob.name].visible_get():
    #             utils.select(ob,True)
        
    bpy.ops.view3d.view_selected(use_all_regions = False)

    utils.multiSelection(selected)





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


class KIAToolsPanel(utils.panel):   
    bl_label ='KIAtools'
    def draw(self, context):
        self.layout.operator("kiatools.object_applier", icon='BLENDER')
        #self.layout.operator("kiatools.modifiertools", icon='BLENDER')
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



 
