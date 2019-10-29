import bpy
from bpy.types import ( PropertyGroup , Panel , Operator ,UIList)
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
from . import apply
from . import curve
from . import scene
from . import constraint
from . import locator
from . import modifierlist


imp.reload(utils)
imp.reload(modifier)
imp.reload(display)
imp.reload(apply)
imp.reload(curve)
imp.reload(scene)
imp.reload(constraint)
imp.reload(locator)
imp.reload(modifierlist)


bl_info = {
"name": "kiatools",
"author": "kisekiakeshi",
"version": (0, 1),
"blender": (2, 80, 0),
"description": "kiatools",
"category": "Object"}


try: 
    bpy.utils.unregister_class(KIATOOLS_modifierlist_item)
except:
    pass


@persistent
def kiatools_handler(scene):
    props = bpy.context.scene.kiatools_oa
    ui_list = bpy.context.window_manager.kiatools_props_modifierlist
    act = utils.getActiveObj()

    if props.handler_through:
        return

    if act == None:
        return 

    mod_count = len(act.modifiers)

    print('kiatool' , props.currentobj , act.name , mod_count ,props.mod_count)

    
    #選択が変わったときにリロード
    #モディファイヤの数を保持しておく。モディファイヤ数が変わったらリロード
    if props.currentobj != act.name:
        modifierlist.reload()
        props.currentobj = act.name
        props.mod_count = mod_count
    else:
        if props.mod_count != mod_count:
            modifierlist.reload()
            props.mod_count = len(act.modifiers)


    

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



class KIATOOLS_Props_OA(PropertyGroup):
    handler_through : BoolProperty(default = False)

    #アプライオプション
    deleteparticle_apply : BoolProperty(name="delete particle" ,  default = False)
    keephair_apply : BoolProperty(name="keep hair" ,  default = False)
    keeparmature_apply : BoolProperty(name="keep armature" ,  default = False)
    merge_apply : BoolProperty(name="merge" ,  default = True)
    create_collection : BoolProperty(name="create collection" ,  default = False)

    #シーン名
    scene_name : StringProperty(name="Scene", maxlen=63 ,update = go_scene)
    allscene : CollectionProperty(type=PropertyGroup)

    target_scene_name : StringProperty(name="Target", maxlen=63 ,update = go_scene)
    target_allscene : CollectionProperty(type=PropertyGroup)

    new_scene_name : StringProperty(name="new scene", maxlen=63)

    #モデリング関連:showhide_bool 選択したオブジェクトだけ表示
    # 表示
    focus_bool : BoolProperty(name="focus" ,  default = False)

    const_bool : BoolProperty(name="const" , update = display.tgl_constraint)
    showhide_bool : BoolProperty(name="child" , update = display.tgl_child)
    showhide_collection_bool : BoolProperty(name="" , update = display.tgl_collection)

    displayed_obj : StringProperty(name="Target", maxlen=63)    
    displayed_allobjs : CollectionProperty(type=PropertyGroup)

    displayed_collection : StringProperty(name="Coll", maxlen=63)    
    displayed_allcollections : CollectionProperty(type=PropertyGroup)


    #モディファイヤ関連
    mod_init : BoolProperty(default = True)
    modifier_type : EnumProperty(items = modifier.TYPE , name = 'modifier' )


    solidify_thickness : FloatProperty(name = "Solidify_thick",precision = 4, update=modifier.apply)
    shrinkwrap_offset : FloatProperty(name = "wrap_ofset", precision = 4, update=modifier.apply)
    bevel_width : FloatProperty(name = "Bevel_width",update=modifier.apply)
    array_count : IntProperty(name = "Array_num",update=modifier.apply)


    array_offset_x : FloatProperty(name = "x", update=modifier.apply)
    array_offset_y : FloatProperty(name = "y",  update=modifier.apply)
    array_offset_z : FloatProperty(name = "z",  update=modifier.apply)

    #コンストレイン関連
    const_type : EnumProperty(items = constraint.TYPE , name = 'constraint' )

    #モディファイヤリスト　handlerでのモデルチェック
    currentobj : StringProperty(maxlen=63)
    mod_count : IntProperty()


#---------------------------------------------------------------------------------------
#UI
#---------------------------------------------------------------------------------------
class KIATOOLS_MT_toolPanel(utils.panel):   
    bl_label ='KIAtools'
    def draw(self, context):
        self.layout.operator("kiatools.apply", icon='BLENDER')
        self.layout.operator("kiatools.modelingtools", icon='BLENDER')
        self.layout.operator("kiatools.kia_helper_tools", icon='BLENDER')
        self.layout.operator("kiatools.curvetools", icon='BLENDER')


class KIATOOLS_MT_kia_helper_tools(Operator):

    bl_idname = "kiatools.kia_helper_tools"
    bl_label = "kia helper"

    def execute(self, context):
        return{'FINISHED'}

    def invoke(self, context, event):
        #アクティブオブジェクトのコンストレインの状態を取得
        display.get_constraint_status()
        modifier.get_param()
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.kiatools_oa
        layout=self.layout

        box = layout.box()
        box.label( text = 'display toggle' )


        row1 = box.row()
        box2 = row1.box()

        row2 = box2.row()
        row2.prop(props, "const_bool" , icon='CONSTRAINT')#コンストレインのON、OFF
        row2.prop(props, "showhide_bool" , icon='EMPTY_DATA')#選択した子供のみ表示

        
        box2.prop(props, "focus_bool")


        box1 = row1.box()
        box1.label( text = 'collection' )

        row1 = box1.row()
        row1.prop(props, "showhide_collection_bool" , icon='GROUP')
        row1.operator( "kiatools.preserve_collections" , icon = 'IMPORT')
        row1.operator( "kiatools.collections_hide" )


        #row = box.row()
        box1 = layout.box()
        row = box1.row()
        box2 = row.box()
        box2.label( text = 'locator' )
        box2.operator( "kiatools.replace_locator" , icon = 'MODIFIER')
        box2.operator( "kiatools.replace_locator_facenormal" , icon = 'MODIFIER')
        box2.operator( "kiatools.group" , icon = 'MODIFIER')

        col = row.column()
        box3 = col.box()
        box3.label( text = 'child' )
        box3.operator( "kiatools.preserve_child" , icon = 'MODIFIER')
        box3.operator( "kiatools.restore_child" , icon = 'MODIFIER')

        box3 = col.box()
        box3.label( text = 'select' )
        box3.operator( "kiatools.select_instance_collection" , icon = 'MODIFIER')
        



class KIATOOLS_MT_modelingtools(Operator):
    bl_idname = "kiatools.modelingtools"
    bl_label = "kia mod"

    def execute(self, context):
        return{'FINISHED'}

    def invoke(self, context, event):
        #アクティブオブジェクトのコンストレインの状態を取得
        display.get_constraint_status()
        modifier.get_param()
        return context.window_manager.invoke_props_dialog(self , width=400)

    def draw(self, context):
        props = bpy.context.scene.kiatools_oa
        layout=self.layout

        row = layout.row(align=False)

        box = layout.box()
        box.label( text = 'modifier' , icon = 'MODIFIER')

        row = box.row()
        box1 = row.box()
        box1.label( text = 'Edit'  , icon='MOD_ARRAY')

        box1.operator( "kiatools.selectmodifiercurve" , icon = 'MODIFIER')
        box1.operator( "kiatools.selectmodifierboolean" , icon = 'MODIFIER')


        box2 = row.box()
        box2.label( text = 'mod'  , icon='MOD_ARRAY')

        box2.prop(props, "solidify_thickness" , icon='RESTRICT_VIEW_OFF')
        box2.prop(props, "shrinkwrap_offset" , icon='RESTRICT_VIEW_OFF')
        box2.prop(props, "bevel_width" , icon='RESTRICT_VIEW_OFF')

        box3 = row.box()
        box3.label( text = 'Array'  , icon='MOD_ARRAY')

        box3.prop(props, "array_count")
        box3.prop(props, "array_offset_x" )
        box3.prop(props, "array_offset_y" )
        box3.prop(props, "array_offset_z" )


        row = layout.row()
        box = row.box()
        box.label( text = 'modifier (assign/apply/show/hide)' )
        box.prop(props, "modifier_type" , icon='RESTRICT_VIEW_OFF')

        #row = layout.row()
        #box = row.box()
        row1 = box.row()
        row1.operator( "kiatools.modifier_asign" , icon = 'VIEW_PAN')
        row1.operator( "kiatools.modifier_apply" , icon = 'CHECKBOX_HLT')
        row1.operator( "kiatools.modifier_show" , icon = 'HIDE_OFF')
        row1.operator( "kiatools.modifier_hide" , icon = 'HIDE_ON')
        
        #row.prop(props, "modifier_view_bool" , icon='RESTRICT_VIEW_OFF')


        box = row.box()
        box.label( text = 'constraint (apply)' )
        box.prop(props, "const_type" , icon='RESTRICT_VIEW_OFF')
        row1 = box.row()
        row1.operator( "kiatools.constraint_asign" , icon = 'VIEW_PAN')



class KIATOOLS_MT_curvetools(Operator):
    bl_idname = "kiatools.curvetools"
    bl_label = "kia curve"


    def execute(self, context):
        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.kiatools_oa
        layout=self.layout
        row = layout.row(align=False)

        box = layout.box()
        #box.label( text = 'curve' )
        row = box.row()

        box1 = row.box()
        box1.label( text = 'create' )
        box1.operator( "kiatools.curve_create_with_bevel" , icon = 'MODIFIER')
        box1.operator( "kiatools.curve_create_liner" , icon = 'MODIFIER')

        box2 = row.box()
        box2.label( text = 'bevel assign' )
        box2.operator( "kiatools.curve_assign_bevel" , icon = 'MODIFIER')
        box2.operator( "kiatools.curve_assign_circle_bevel" , icon = 'MODIFIER')
        box2.operator( "kiatools.curve_assign_liner_bevel" , icon = 'MODIFIER')

        box3 = row.box()
        box3.label( text = 'select' )
        box3.operator( "kiatools.curve_select_bevel" , icon = 'MODIFIER')


class KIATOOLS_MT_object_applier(Operator):
    bl_idname = "kiatools.apply"
    bl_label = "Object Applier"

    def invoke(self, context, event):
        scene.set_current()        
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        return{'FINISHED'}


    def draw(self, context):
        props = bpy.context.scene.kiatools_oa
        layout=self.layout

        row = layout.row(align=False)
        box = row.box()

        row = box.row()

        row.prop_search(props, "scene_name", props, "allscene", icon='SCENE_DATA')
        row.operator("kiatools.new_scene" , icon = 'DUPLICATE')
        box.operator("kiatools.remove_empty_collection" , icon = 'DUPLICATE')


        box = layout.row(align=False).box()
        row = box.row()
        box.prop_search(props, "target_scene_name", props, "target_allscene", icon='SCENE_DATA')


        row = box.row()
        row.label( text = 'apply' )
        row.operator("kiatools.apply_model" , icon='OBJECT_DATAMODE' )
        row.operator("kiatools.apply_collection" , icon='GROUP' )
        row.operator("kiatools.apply_particle_instance", icon='PARTICLES' )

        row = box.row()
        row.label( text = 'move' )
        row.operator("kiatools.move_model" , icon = 'OBJECT_DATAMODE')
        row.operator("kiatools.move_collection" , icon = 'GROUP')
        


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

        row = box.row()
        row.prop(props, "create_collection")

#---------------------------------------------------------------------------------------
#Operator
#---------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------
#Curve Tool
#---------------------------------------------------------------------------------------

class KIATOOLS_OT_curve_create_with_bevel(Operator):
        """ベベル込みのカーブを作成する。"""
        bl_idname = "kiatools.curve_create_with_bevel"
        bl_label = "bevel curve"
        
        def execute(self, context):
            curve.create_with_bevel()
            return {'FINISHED'}

class KIATOOLS_OT_curve_assign_bevel(Operator):
        """カーブにベベルをアサイン\nカーブ、ベベルカーブの順に選択して実行"""
        bl_idname = "kiatools.curve_assign_bevel"
        bl_label = "select"
        
        def execute(self, context):
            curve.assign_bevel()
            return {'FINISHED'}

class KIATOOLS_OT_curve_assign_circle_bevel(Operator):
        """カーブに円のベベルをアサイン"""
        bl_idname = "kiatools.curve_assign_circle_bevel"
        bl_label = "circle"
        
        def execute(self, context):
            curve.assign_circle_bevel()
            return {'FINISHED'}

class KIATOOLS_OT_curve_assign_liner_bevel(Operator):
        """カーブに直線のベベルをアサイン"""
        bl_idname = "kiatools.curve_assign_liner_bevel"
        bl_label = "liner"
        
        def execute(self, context):
            curve.assign_liner_bevel()
            return {'FINISHED'}


class KIATOOLS_OT_curve_create_liner(Operator):
        """直線カーブを作成"""
        bl_idname = "kiatools.curve_create_liner"
        bl_label = "add liner"
        
        def execute(self, context):
            curve.create_liner()
            return {'FINISHED'}

class KIATOOLS_OT_curve_select_bevel(Operator):
        """選択カーブのベベルを選択"""
        bl_idname = "kiatools.curve_select_bevel"
        bl_label = "bevel"
        
        def execute(self, context):
            curve.select_bevel()
            return {'FINISHED'}


#---------------------------------------------------------------------------------------
#Locator
#---------------------------------------------------------------------------------------

class KIATOOLS_OT_replace_locator(Operator):
    """モデルに位置にロケータを配置してコンストレインする。モデルのトランスフォームは初期値にする。"""
    bl_idname = "kiatools.replace_locator"
    bl_label = "to locator"

    def execute(self, context):
        locator.replace()
        return {'FINISHED'}

class KIATOOLS_OT_replace_locator_facenormal(Operator):
    """モデルに位置にロケータを配置してコンストレインする。モデルのトランスフォームは初期値にする。"""
    bl_idname = "kiatools.replace_locator_facenormal"
    bl_label = "face normal"

    def execute(self, context):
        locator.replace_facenormal()
        return {'FINISHED'}

class KIATOOLS_OT_group(Operator):
    """ロケータで選択モデルをまとめる"""
    bl_idname = "kiatools.group"
    bl_label = "group"

    def execute(self, context):
        locator.group()
        return {'FINISHED'}

#親子付けの際、ワールドのトランスフォームを維持したいので親のマトリックスを掛け合わせる
class KIATOOLS_OT_preserve_child(Operator):
    """一時的に子供を別ノードに逃がす。親を選択して実行する"""
    bl_idname = "kiatools.preserve_child"
    bl_label = "preserve"

    def execute(self, context):
        locator.preserve_child()
        return {'FINISHED'}

#親子付けの際、ワールドのトランスフォームを維持したいので親のマトリックスを掛け合わせる
class KIATOOLS_OT_restore_child(Operator):
    """一時的に逃がした子供を復旧させる。もとの親を選択して実行する。"""
    bl_idname = "kiatools.restore_child"
    bl_label = "resore"

    def execute(self, context):
        locator.restore_child()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#Select
#---------------------------------------------------------------------------------------
class KIATOOLS_OT_select_instance_collection(Operator):
    """コレクションインスタンスから元のコレクションを選択する"""
    bl_idname = "kiatools.select_instance_collection"
    bl_label = "instance source"

    def execute(self, context):
        display.select_instance_collection()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#ObjectApplier
#---------------------------------------------------------------------------------------

#選択モデルをリスト選択されたシーンに移動
class KIATOOLS_OT_move_model(Operator):
    """選択したモデルをリスト選択されたシーンに移動する"""
    bl_idname = "kiatools.move_model"
    bl_label = "model"

    def execute(self, context):
        apply.move_object_to_other_scene()
        return {'FINISHED'}


#選択コレクションをリスト選択されたシーンに移動
class KIATOOLS_OT_move_collection(Operator):
    """選択コレクションをリスト選択されたシーンに移動"""
    bl_idname = "kiatools.move_collection"
    bl_label = "collection"

    def execute(self, context):
        apply.move_collection_to_other_scene()
        return {'FINISHED'}


#空のコレクションを削除
class KIATOOLS_OT_remove_empty_collection(Operator):
    """空のコレクションを削除"""
    bl_idname = "kiatools.remove_empty_collection"
    bl_label = "remove empty collection"

    def execute(self, context):
        apply.remove_empty_collection()
        return {'FINISHED'}


#選択したコレクションに含まれたモデルを対象に
#出力名にコレクション名を付ける
#末尾にorgcを付ける
class KIATOOLS_OT_apply_collection(Operator):
    """選択したコレクション以下のモデルが対象\nコレクションのモデルはジョインされる\n名前はコレクション名+orgcとする"""
    bl_idname = "kiatools.apply_collection"
    bl_label = "col"

    def execute(self, context):
        apply.apply_collection()
        return {'FINISHED'}

#Newシーンのパネルを開く
class KIATOOLS_MT_new_scene(Operator):
    """新しいFixScnを生成する"""
    bl_idname = "kiatools.new_scene"
    bl_label = ""

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
   
    def draw(self, context):
        props = bpy.context.scene.kiatools_oa
        row = self.layout.row(align=False)
        row.prop(props, "new_scene_name", icon='BLENDER', toggle=True)    

    def execute(self, context):
        props = bpy.context.scene.kiatools_oa

        scene_name = props.new_scene_name
        if bpy.data.scenes.get(scene_name) is not None:
            return {'FINISHED'}

        bpy.ops.scene.new(type='EMPTY')     
        bpy.context.scene.name = scene_name
        scene.set_current()
        return {'FINISHED'}

#パーティクルインスタンスのApply
class KIATOOLS_OT_apply_particle_instance(Operator):
    """パーティクルインスタンスを実体化して1つのモデルに集約"""
    bl_idname = "kiatools.apply_particle_instance"
    bl_label = "particle to model"

    def execute(self, context):
        apply.particle_instance()
        return {'FINISHED'}

#モデル名に_orgをつけてそれを作業用のモデルとする。
class KIATOOLS_OT_apply_model(Operator):
    """名前の末尾にorgがついたモデルが対象\nモディファイアフリーズ＞_orgを削除したモデルを複製＞選択シーンににリンク"""
    bl_idname = "kiatools.apply_model"
    bl_label = "org"

    def execute(self, context):
        apply.model_org()
        return {'FINISHED'}



#---------------------------------------------------------------------------------------
#Modifier
#---------------------------------------------------------------------------------------

#二つのノードを選択してモディファイヤアサインと同時にターゲットを割り当てる
#ターゲットモデルをアクティブとするので　モディファイヤをアサインしたいモデルをまず選択、最後にターゲットを選択する
class KIATOOLS_OT_modifier_asign(Operator):
    """モディファイヤをアサインする"""
    bl_idname = "kiatools.modifier_asign"
    bl_label = ""

    def execute(self, context):
        modifier.assign()
        return {'FINISHED'}

class KIATOOLS_OT_modifier_show(Operator):    
    """モディファイヤを表示する"""
    bl_idname = "kiatools.modifier_show"
    bl_label = ""

    def execute(self, context):
        modifier.show(True)
        return {'FINISHED'}

class KIATOOLS_OT_modifier_hide(Operator):    
    """モディファイヤを表示する"""
    bl_idname = "kiatools.modifier_hide"
    bl_label = ""

    def execute(self, context):
        modifier.show(False)
        return {'FINISHED'}

class KIATOOLS_OT_modifier_apply(Operator):    
    """モディファイヤを適用する"""
    bl_idname = "kiatools.modifier_apply"
    bl_label = ""

    def execute(self, context):
        modifier.apply_mod()
        return {'FINISHED'}

#選択したモデルのモディファイヤカーブのカーブ選択。
class KIATOOLS_OT_modifier_select_curve(Operator):
    """選択したモデルのモディファイヤカーブのカーブ選択"""
    bl_idname = "kiatools.selectmodifiercurve"
    bl_label = "Curve"

    def execute(self, context):
        modifier.select('CURVE')
        return {'FINISHED'}

#選択したモデルのモディファイヤカーブのカーブ選択。
class KIATOOLS_OT_modifier_select_boolean(Operator):
    """選択したモデルのブーリアン選択"""
    bl_idname = "kiatools.selectmodifierboolean"
    bl_label = "Boolean"

    def execute(self, context):
        modifier.select('BOOLEAN')
        return {'FINISHED'}

#---------------------------------------------------------------------------------------
#Constraint
#---------------------------------------------------------------------------------------
class KIATOOLS_OT_constraint_asign(Operator):
    """モディファイヤをアサインする"""
    bl_idname = "kiatools.constraint_asign"
    bl_label = ""

    def execute(self, context):
        constraint.assign()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#helper
#---------------------------------------------------------------------------------------

#選択したモデルの所属するコレクションをハイド
class KIATOOLS_OT_collections_hide(Operator):
    """選択したオブジェクトが属するコレクションをハイド"""
    bl_idname = "kiatools.collections_hide"
    bl_label = "hide"

    def execute(self, context):
        display.collection_hide()
        return {'FINISHED'}

#現在のコレクション表示状態を保持する
class KIATOOLS_OT_preserve_collections(Operator):
    """現在のコレクション表示状態を保持する"""
    bl_idname = "kiatools.preserve_collections"
    bl_label = ""

    def execute(self, context):
        display.preserve_collections()
        return {'FINISHED'}



#---------------------------------------------------------------------------------------
#modifierList
#---------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------
#リスト内のアイテムの見た目を指定
#---------------------------------------------------------------------------------------
class KIATOOLS_UL_modifierlist_uilist(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            #item.nameが表示される
            layout.prop(item, "bool_val", text = "")
            layout.prop(item, "name", text="", emboss=False, icon_value=icon)
            
            #layout.label(item.name, icon_value='BONE_DATA')

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


#---------------------------------------------------------------------------------------
#リスト名 , list_id can be ””　，item_ptr ,item , index_pointer ,active_index
#active_indexをui_list.active_indexで取得できる
#---------------------------------------------------------------------------------------
class KIATOOLS_MT_modifierlist(utils.panel):
    bl_label = "kia_modifierlist"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self , width=400)

    def draw(self, context):
        layout=self.layout
        row = layout.row()

        col = row.column()
        ui_list = context.window_manager.kiatools_props_modifierlist

        col.template_list("KIATOOLS_UL_modifierlist_uilist", "", ui_list, "itemlist", ui_list, "active_index", rows=8)
        col = row.column(align=True)

        col.operator("kiatools.modifierlist_apply", icon='MODIFIER_ON')
        col.operator("kiatools.modifierlist_apply_checked", icon='CHECKBOX_HLT')
        col.operator("kiatools.modifierlist_remove", icon='TRASH')
        col.operator("kiatools.modifierlist_move_item", icon=utils.icon['UP']).type = 'TOP'
        col.operator("kiatools.modifierlist_move_item", icon='TRIA_UP').type = 'UP'
        col.operator("kiatools.modifierlist_move_item", icon='TRIA_DOWN').type = 'DOWN'
        col.operator("kiatools.modifierlist_move_item", icon=utils.icon['DOWN']).type = 'BOTTOM'


#---------------------------------------------------------------------------------------
#リストのアイテムに他の情報を埋め込みたい場合はプロパティを追加できるのでいろいろ追加してみよう。
#ここでレジストしないと不具合がでる。register()に含めたいところだが。
#TestCollectionPropertyのitemListの型として指定する必要があるので後でレジストできない
#---------------------------------------------------------------------------------------

class KIATOOLS_modifierlist_item(PropertyGroup):
    name : StringProperty(get=modifierlist.get_item, set=modifierlist.set_item)
    bool_val : BoolProperty( update = modifierlist.showhide )

bpy.utils.register_class(KIATOOLS_modifierlist_item)


#---------------------------------------------------------------------------------------
#アイテムのリストクラス
#複数のアイテムをリストに持ち、リストにアイテムを加えたり、選択したリストを取得したりする。
#このクラス自体はuiをもっているわけではないので、現在リストで選択されているインデックスを取得する必要がある。
#
#col.template_list("Modifierlist_group_list", "", ui_list, "itemlist", ui_list, "active_index", rows=3)
#template_listで選択されたアイテムのインデックスをactive_indexに渡すため、上のように指定する必要がある。

#CollectionPropertyへの追加方法例
# item = self.list.add()
# item.name = bone.name
# item.int_val = 10
#---------------------------------------------------------------------------------------
class KIATOOLS_Props_modifierlist(PropertyGroup):
    active_index : IntProperty()
    itemlist : CollectionProperty(type=KIATOOLS_modifierlist_item)#アイテムプロパティの型を収めることができるリストを生成



class KIATOOLS_OT_modifierlist_move_item(Operator):
    bl_idname = "kiatools.modifierlist_move_item"
    bl_label = ""
    type = StringProperty(default='UP')

    def execute(self, context):
        modifierlist.move(self.type)
        return {'FINISHED'}

class KIATOOLS_OT_modifierlist_apply(Operator):
    """選択をapplyする"""
    bl_idname = "kiatools.modifierlist_apply"
    bl_label = ""

    def execute(self, context):
        modifierlist.apply()
        return {'FINISHED'}

class KIATOOLS_OT_modifierlist_apply_checked(Operator):
    """チェックされたものをapplyする"""
    bl_idname = "kiatools.modifierlist_apply_checked"
    bl_label = ""

    def execute(self, context):
        modifierlist.apply_checked()
        return {'FINISHED'}

class KIATOOLS_OT_modifierlist_remove(Operator):
    """選択されたものを削除する"""
    bl_idname = "kiatools.modifierlist_remove"
    bl_label = ""

    def execute(self, context):
        modifierlist.remove()
        return {'FINISHED'}



classes = (
    KIATOOLS_Props_OA,

    KIATOOLS_MT_toolPanel,
    KIATOOLS_MT_kia_helper_tools,
    KIATOOLS_MT_modelingtools,
    KIATOOLS_MT_object_applier,
    KIATOOLS_MT_curvetools,
    KIATOOLS_MT_modifierlist,

    KIATOOLS_OT_curve_create_with_bevel,
    KIATOOLS_OT_curve_create_liner,
    KIATOOLS_OT_curve_assign_bevel,
    KIATOOLS_OT_curve_assign_circle_bevel,
    KIATOOLS_OT_curve_assign_liner_bevel,
    KIATOOLS_OT_curve_select_bevel,

    KIATOOLS_OT_replace_locator,
    KIATOOLS_OT_replace_locator_facenormal,
    KIATOOLS_OT_group,
    KIATOOLS_OT_restore_child,
    KIATOOLS_OT_preserve_child,
    KIATOOLS_OT_collections_hide,
    KIATOOLS_OT_preserve_collections,

    KIATOOLS_OT_select_instance_collection,

    KIATOOLS_OT_modifier_asign,
    KIATOOLS_OT_modifier_show,
    KIATOOLS_OT_modifier_hide,
    KIATOOLS_OT_modifier_apply,
    KIATOOLS_OT_modifier_select_curve,
    KIATOOLS_OT_modifier_select_boolean,

    KIATOOLS_OT_constraint_asign,

    #object applier
    KIATOOLS_MT_new_scene,
    KIATOOLS_OT_move_model,
    KIATOOLS_OT_apply_collection,
    KIATOOLS_OT_remove_empty_collection,
    KIATOOLS_OT_apply_particle_instance,
    KIATOOLS_OT_apply_model,
    KIATOOLS_OT_move_collection,

    #modifierlist
    KIATOOLS_Props_modifierlist,
    KIATOOLS_UL_modifierlist_uilist,
    KIATOOLS_OT_modifierlist_move_item,
    KIATOOLS_OT_modifierlist_apply,
    KIATOOLS_OT_modifierlist_apply_checked,
    KIATOOLS_OT_modifierlist_remove
    

)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.kiatools_oa = PointerProperty(type=KIATOOLS_Props_OA)
    bpy.app.handlers.depsgraph_update_pre.append(kiatools_handler)
    bpy.types.WindowManager.kiatools_props_modifierlist = PointerProperty(type=KIATOOLS_Props_modifierlist)



def unregister():
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.kiatools_oa
    del bpy.types.WindowManager.kiatools_props_modifierlist

    bpy.app.handlers.depsgraph_update_pre.remove(kiatools_handler)



 
