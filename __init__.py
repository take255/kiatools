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
from . import display
from . import object_applier
from . import modeling


imp.reload(utils)
imp.reload(modifier)
imp.reload(display)
imp.reload(object_applier)
imp.reload(modeling)


bl_info = {
"name": "kiatools",
"author": "kisekiakeshi",
"version": (0, 1),
"blender": (2, 80, 0),
"description": "kiatools",
"category": "Object"}




@persistent
def kiatools_handler(scene):
    # props = bpy.context.scene.kiatools_oa

    # #モディファイヤメニューから選択されたときの処理
    # if props.modifier_selected  != props.modifier_type:
    #     modtype = props.modifier_type
    #     props.modifier_selected = props.modifier_type
    #     act = utils.getActiveObj()

    #     for mod in act.modifiers:        
    #         if modtype == mod.type:
    #             print(modtype)    
    
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



#コンストレインが１つでもONならTrue
#muteがONなのが
# def get_constraint_status():

#     act = utils.getActiveObj()
#     if act == None:
#         return

#     props = bpy.context.scene.kiatools_oa

#     status = False
#     for const in act.constraints:
#         status = (status or const.mute)

#     props.const_bool = status





#ob　が　selectedの子供かどうか調べる。孫以降も調査。
# def isParent(ob , selected):
#     parent = ob.parent
#     if parent == None:
#         return False

#     if parent in selected:
#         return True
#     else:
#         isParent(parent , selected)


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


#現在のシーンをシーンメニューにセット
def set_current_scene():
    props = bpy.context.scene.kiatools_oa

    props.allscene.clear()
    props.target_allscene.clear()

    for scn in bpy.data.scenes:
        props.allscene.add().name = scn.name
        props.target_allscene.add().name = scn.name

    props.scene_name = bpy.context.scene.name

#選択したコンストレインの表示、非表示
#その際、選択オブジェクトにフォーカスする
#

# def showhide_constraint(self,context):
#     props = bpy.context.scene.kiatools_oa
#     selected = utils.selected()
#     act = utils.getActiveObj()

#     for ob in selected:
#         utils.activeObj(ob)
#         for const in ob.constraints:
#             const.mute = props.const_bool

#             #muteオンオフだけではコンストレインがアップデートされない問題
#             #この行の追加で解消
#             const.influence = 1.0 


#     #表示されているならセレクトする    
#     for ob in bpy.data.objects: 
#         if ob.parent in selected: 
#             if bpy.data.objects[ob.name].visible_get():
#                 utils.select(ob,True)
#             #children.append(ob) 
        
#     bpy.ops.view3d.view_selected(use_all_regions = False)

#     #utils.deselectAll()
#     utils.multiSelection(selected)
#     utils.activeObj(act)


#ＯＮで現在の表示状態を保持しておき選択モデルだけ表示、ＯＦＦでもとに戻す
# def showhide_object(self,context):
#     props = bpy.context.scene.kiatools_oa    
#     selected = utils.selected()

#     #選択以外をハイド
#     if props.showhide_bool:
#         props.displayed_allobjs.clear()
#         #すべてのオブジェクトの表示状態を保持して、選択状態でなければハイドする
#         for ob in bpy.data.objects:
#             if bpy.data.objects[ob.name].visible_get():
#                 props.displayed_allobjs.add().name = ob.name

#                 if not ob in selected: 
#                     if not isParent(ob , selected): 
#                         ob.hide_viewport = True
#                     else:
#                         utils.select(ob,True)
                
    
#     #表示をもとに戻す
#     else:
#         for ob in props.displayed_allobjs:
#             bpy.data.objects[ob.name].hide_viewport = False
#             #utils.select(ob,True)

#         if not ob in selected: 
#             if isParent(ob , selected): 
#                 utils.selectByName(ob,True)

    
#     bpy.ops.view3d.view_selected(use_all_regions = False)
#     utils.deselectAll()
#     utils.multiSelection(selected)



# def showhide_collection(self,context):
#     pass



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
    # 表示
    const_bool : BoolProperty(name="const" , update = display.tgl_constraint)
    showhide_bool : BoolProperty(name="child" , update = display.tgl_child)
    showhide_collection_bool : BoolProperty(name="" , update = display.tgl_collection)

    displayed_obj : StringProperty(name="Target", maxlen=63)    
    displayed_allobjs : CollectionProperty(type=PropertyGroup)

    displayed_collection : StringProperty(name="Coll", maxlen=63)    
    displayed_allcollections : CollectionProperty(type=PropertyGroup)


    #モディファイヤ関連
    mod_init : BoolProperty(default = True)
    modifier_type : EnumProperty(items = MODIFIER_TYPE , name = 'modifier' )


    solidify_thickness : FloatProperty(name = "Solidify_thick",precision = 4, update=modifier.apply)
    shrinkwrap_offset : FloatProperty(name = "wrap_ofset", precision = 4, update=modifier.apply)
    bevel_width : FloatProperty(name = "Bevel_width",update=modifier.apply)
    array_count : IntProperty(name = "Array_num",update=modifier.apply)


    array_offset_x : FloatProperty(name = "x", update=modifier.apply)
    array_offset_y : FloatProperty(name = "y",  update=modifier.apply)
    array_offset_z : FloatProperty(name = "z",  update=modifier.apply)


#UI---------------------------------------------------------------------------------------
class KIATOOLS_MT_toolPanel(utils.panel):   
    bl_label ='KIAtools'
    def draw(self, context):
        self.layout.operator("kiatools.object_applier", icon='BLENDER')
        self.layout.operator("kiatools.modelingtools", icon='BLENDER')


class KIATOOLS_MT_modelingtools(bpy.types.Operator):

    bl_idname = "kiatools.modelingtools"
    bl_label = "modeling tools"


    def execute(self, context):
        return{'FINISHED'}

    def invoke(self, context, event):
        #アクティブオブジェクトのコンストレインの状態を取得
        display.get_constraint_status()
        #display.get_collection_status()
        modifier.get_param()
        props = bpy.context.scene.kiatools_oa

        #props.showhide_collection_bool = True #アクティブなモデルのコレクションは表示になっているはず。
        #props.displayed_allcollections.clear()

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        #scn = context.scene
        props = bpy.context.scene.kiatools_oa
        layout=self.layout

        row = layout.row(align=False)
        box = row.box()

        row = box.row()

        box1 = row.box()
        box1.label( text = 'display tgl' , icon = 'IMGDISPLAY')
        box1.prop(props, "const_bool" , icon='CONSTRAINT')
        box1.prop(props, "showhide_bool" , icon='EMPTY_DATA')

        row1 = box1.row(align=True)
        row.alignment = 'LEFT'
        row1.prop(props, "showhide_collection_bool" , icon='GROUP')
        row1.operator( "kiatools.preserve_collections" , icon = 'IMPORT')


        box2 = row.box()
        box2.label( text = 'locator' )
        box2.operator( "kiatools.replace_locator" , icon = 'MODIFIER')
        box2.operator( "kiatools.replace_locator_facenormal" , icon = 'MODIFIER')
        box2.operator( "kiatools.group" , icon = 'MODIFIER')

        box3 = row.box()
        box3.label( text = 'child' )
        box3.operator( "kiatools.preserve_child" , icon = 'MODIFIER')
        box3.operator( "kiatools.restore_child" , icon = 'MODIFIER')


        box = layout.box()
        box.label( text = 'modifier' , icon = 'MODIFIER')

        row = box.row()
        box1 = row.box()
        box1.operator( "kiatools.selectmodifiercurve" , icon = 'MODIFIER')
        box1.prop(props, "solidify_thickness" , icon='RESTRICT_VIEW_OFF')
        box1.prop(props, "shrinkwrap_offset" , icon='RESTRICT_VIEW_OFF')
        box1.prop(props, "bevel_width" , icon='RESTRICT_VIEW_OFF')

        box2 = row.box()
        box2.label( text = 'Array'  , icon='MOD_ARRAY')

        box2.prop(props, "array_count")
        box2.prop(props, "array_offset_x" )
        box2.prop(props, "array_offset_y" )
        box2.prop(props, "array_offset_z" )


        box = layout.box()
        box.label( text = 'modifier edit' )
        box.prop(props, "modifier_type" , icon='RESTRICT_VIEW_OFF')

        row = box.row()
        row.operator( "kiatools.modifier_asign" , icon = 'MODIFIER')
        row.operator( "kiatools.modifier_show" , icon = 'HIDE_OFF')
        row.operator( "kiatools.modifier_hide" , icon = 'HIDE_ON')
        
        #row.prop(props, "modifier_view_bool" , icon='RESTRICT_VIEW_OFF')


        box = layout.box()
        box.label( text = 'constraint' )
        box.operator( "kiatools.const_add_copy_transform" , icon = 'MODIFIER')
        box.operator( "kiatools.collections_hide" , icon = 'MODIFIER')


  


class KIATOOLS_MT_object_applier(bpy.types.Operator):
    bl_idname = "kiatools.object_applier"
    bl_label = "Object Applier"

    def invoke(self, context, event):
        set_current_scene()        
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        return{'FINISHED'}


    def draw(self, context):
        #scn = context.scene
        props = bpy.context.scene.kiatools_oa
        layout=self.layout

        row = layout.row(align=False)
        box = row.box()

        #row = box.row()

        box.prop_search(props, "scene_name", props, "allscene", icon='SCENE_DATA')

        #row.operator("kiatools.change_scene", icon = 'FILE_IMAGE')

        box = layout.row(align=False).box()
        row = box.row()
        box.prop_search(props, "target_scene_name", props, "target_allscene", icon='SCENE_DATA')

        #row.operator("kiatools.set_apply_scene", icon='TRACKING_FORWARDS')
        #row.prop(props, "applyscene" , icon='APPEND_BLEND')

        row = box.row()
        row.operator("kiatools.apply_model" , icon='OBJECT_DATAMODE' )
        row.operator("kiatools.apply_collection" , icon='GROUP' )
        row.operator("kiatools.apply_particle_instance", icon='PARTICLES' )
        row.operator("kiatools.move_model" , icon = 'DECORATE_DRIVER')


        row = layout.row(align=False)
        box = row.box()
        box.label(text = 'options')
        row = box.row()

        row = box.row()
        row.prop(props, "merge_apply")
        row.prop(props, "deleteparticle_apply")

        row = box.row()
        row.prop(props, "keeparmature_apply")
        row.prop(props, "keephair_apply")



classes = (
    KIATOOLS_Props_OA,
    KIATOOLS_MT_toolPanel,
    KIATOOLS_MT_modelingtools,
    KIATOOLS_MT_object_applier
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



 
