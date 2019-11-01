# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.types import ( PropertyGroup , Panel , Operator ,UIList)
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
from . import etc
from . import rename

imp.reload(utils)
imp.reload(modifier)
imp.reload(display)
imp.reload(apply)
imp.reload(curve)
imp.reload(scene)
imp.reload(constraint)
imp.reload(locator)
imp.reload(etc)
imp.reload(rename)


bl_info = {
"name": "kiatools",
"author": "kisekiakeshi",
"version": (0, 1),
"blender": (2, 80, 0),
"description": "kiatools",
"category": "Object"}


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
    modifier_type : EnumProperty(items = modifier.TYPE , name = '' )


    solidify_thickness : FloatProperty(name = "Solidify_thick",precision = 4, update=modifier.apply)
    shrinkwrap_offset : FloatProperty(name = "wrap_ofset", precision = 4, update=modifier.apply)
    bevel_width : FloatProperty(name = "Bevel_width",update=modifier.apply)
    array_count : IntProperty(name = "Array_num",update=modifier.apply)


    array_offset_x : FloatProperty(name = "x", update=modifier.apply)
    array_offset_y : FloatProperty(name = "y",  update=modifier.apply)
    array_offset_z : FloatProperty(name = "z",  update=modifier.apply)

    #コンストレイン関連
    const_type : EnumProperty(items = constraint.TYPE , name = '' )

    #リネームツール関連
    rename_start_num : IntProperty( name = "start",min=1,default=1 )
    rename_string : StringProperty(name = "word")
    from_string : StringProperty(name = "from")
    to_string : StringProperty(name = "to")

#---------------------------------------------------------------------------------------
#UI
#---------------------------------------------------------------------------------------
class KIATOOLS_PT_toolPanel(utils.panel):   
    bl_label ='KIAtools'
    def draw(self, context):
        self.layout.operator("kiatools.apply", icon='BLENDER')
        self.layout.operator("kiatools.modelingtools", icon='BLENDER')
        self.layout.operator("kiatools.kia_helper_tools", icon='BLENDER')
        self.layout.operator("kiatools.curvetools", icon='BLENDER')
        self.layout.operator("kiatools.etc", icon='BLENDER')
        self.layout.operator("kiatools.rename", icon='BLENDER')


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

        row1 = box3.row()
        row1.operator( "kiatools.preserve_child" , icon = 'PINNED')
        row1.operator( "kiatools.restore_child" , icon = 'UNPINNED')

        box3 = col.box()
        box3.label( text = 'instance' )
        box3.operator( "kiatools.select_instance_collection" , icon = 'MODIFIER')
        box3.operator( "kiatools.select_instance_instancer" , icon = 'MODIFIER')

        box3.operator( "kiatools.swap_axis" , icon = 'MODIFIER')
        box3.operator( "kiatools.instance_mirror" , icon = 'MODIFIER')



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

        row1 = box.row()
        row1.alignment = 'RIGHT'
        row1.operator( "kiatools.modifier_asign" , icon = 'VIEW_PAN')
        row1.operator( "kiatools.modifier_apply" , icon = 'CHECKBOX_HLT')
        row1.operator( "kiatools.modifier_show" , icon = 'HIDE_OFF')
        row1.operator( "kiatools.modifier_hide" , icon = 'HIDE_ON')
        
        box = row.box()
        box.label( text = 'constraint (apply)' )
        box.prop(props, "const_type" , icon='RESTRICT_VIEW_OFF')
        row1 = box.row()
        row1.alignment = 'RIGHT'
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
#移植したツールをひとまずここにあつめる。
#---------------------------------------------------------------------------------------
class KIATOOLS_MT_etc(Operator):
    bl_idname = "kiatools.etc"
    bl_label = "kia etc"

    def invoke(self, context, event):
        scene.set_current()        
        return context.window_manager.invoke_props_dialog(self, width=450)

    def execute(self, context):
        return{'FINISHED'}


    def draw(self, context):
        layout=self.layout

        col = layout.column()
        box = col.box()
        row = box.row(align=False)

        box1 = row.box()
        row1 = box1.row()
        row1.alignment = 'LEFT'
        row1.label( text = 'x90d:' )
        row1.operator("kiatools.transform_rotate_axis", icon='LOOP_FORWARDS').axis = 'x90d'
        row1.operator("kiatools.transform_rotate_axis", icon='LOOP_BACK').axis = 'x-90d'

        box1 = row.box()
        row1 = box1.row()
        row1.alignment = 'LEFT'
        row1.label( text = 'y90d:' )
        row1.operator("kiatools.transform_rotate_axis", icon='LOOP_FORWARDS').axis = 'y90d'
        row1.operator("kiatools.transform_rotate_axis", icon='LOOP_BACK').axis = 'y-90d'

        box1 = row.box()
        row1 = box1.row()
        row1.alignment = 'LEFT'
        row1.label( text = 'z90d:' )
        row1.operator("kiatools.transform_rotate_axis", icon='LOOP_FORWARDS').axis = 'z90d'
        row1.operator("kiatools.transform_rotate_axis", icon='LOOP_BACK').axis = 'z-90d'

        box1 = row.box()
        row1 = box1.row()
        row1.alignment = 'LEFT'
        row1.label( text = '180:' )

        row1.operator("kiatools.transform_rotate_axis", icon='LOOP_BACK').axis = 'x180d'
        row1.operator("kiatools.transform_rotate_axis", icon='LOOP_BACK').axis = 'y180d'
        row1.operator("kiatools.transform_rotate_axis", icon='LOOP_BACK').axis = 'z180d'

        box = col.box()
        row = box.row()        
        row.operator("kiatools.transform_scale_abs", icon='LOOP_BACK')
        row.operator("kiatools.constraint_to_bone", icon='LOOP_BACK')
        row.operator("kiatools.reference_make_proxy", icon='LOOP_BACK')
        row.operator("kiatools.refernce_make_link_draw", icon='LOOP_BACK')

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
#Instance
#---------------------------------------------------------------------------------------
class KIATOOLS_OT_instance_select_collection(Operator):
    """コレクションインスタンスから元のコレクションを選択する"""
    bl_idname = "kiatools.select_instance_collection"
    bl_label = "select source"
    def execute(self, context):
        display.select_instance_collection()
        return {'FINISHED'}

class KIATOOLS_OT_instance_instancer(Operator):
    """選択したオブジェクトがメンバーのコレクションをインスタンス化"""
    bl_idname = "kiatools.select_instance_instancer"
    bl_label = "instancer"
    def execute(self, context):
        locator.instancer()
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
#transform
#---------------------------------------------------------------------------------------

#現在のコレクション表示状態を保持する
class KIATOOLS_OT_swap_axis(Operator):
    """軸をスワップする"""
    bl_idname = "kiatools.swap_axis"
    bl_label = "swap axis"
    def execute(self, context):
        locator.swap_axis()
        return {'FINISHED'}


#オブジェクトをX軸ミラーコンストレインする
class KIATOOLS_OT_instance_mirror(Operator):
    """インスタンスをX軸ミラーする"""
    bl_idname = "kiatools.instance_mirror"
    bl_label = "constraint mirror"
    def execute(self, context):
        locator.mirror()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#etc
#---------------------------------------------------------------------------------------

#オブジェクトをX軸ミラーコンストレインする
class KIATOOLS_OT_transform_rotate_axis(Operator):
    """ローカル軸を中心に回転"""
    bl_idname = "kiatools.transform_rotate_axis"
    bl_label = ""
    axis : StringProperty(default='x90') 
    def execute(self, context):
        etc.transform_rotate_axis(self.axis)
        return {'FINISHED'}

#オブジェクトをX軸ミラーコンストレインする
class KIATOOLS_OT_transform_scale_abs(Operator):
    """スケールを正にする"""
    bl_idname = "kiatools.transform_scale_abs"
    bl_label = "scale abs"
    def execute(self, context):
        etc.transform_scale_abs()
        return {'FINISHED'}

#オブジェクトをX軸ミラーコンストレインする
class KIATOOLS_OT_constraint_to_bone(Operator):
    """選択されているボーンでコンストレインする\nモデル、アーマチュアの順に選択しEditモードでボーンを選択して実行する"""
    bl_idname = "kiatools.constraint_to_bone"
    bl_label = "constraint to bone"
    def execute(self, context):
        etc.constraint_to_bone()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#リファレンス関連ツール
#---------------------------------------------------------------------------------------

#複数のモデルを同時にプロキシ化
class KIATOOLS_OT_refernce_make_proxy(Operator):
    """選択した複数のモデルをプロキシする"""
    bl_idname = "kiatools.reference_make_proxy"
    bl_label = "make proxy"
    def execute(self, context):
        etc.refernce_make_proxy()
        return {'FINISHED'}

#シンボリックリンク作成
class KIATOOLS_OT_refernce_make_link(Operator):
    bl_idname = "kiatools.refernce_make_link_draw"
    bl_label = "make link"
    filepath : bpy.props.StringProperty(subtype="DIR_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        etc.refernce_make_link()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#リネームツール
#リネームとオブジェクト選択に関するツール群
#---------------------------------------------------------------------------------------
class KIATOOLS_MT_rename(Operator):
    bl_idname = "kiatools.rename"
    bl_label = "rename select"

    def execute(self, context):
        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self , width = 400 )

    def draw(self, context):
        props = bpy.context.scene.kiatools_oa
        layout=self.layout

        col_root = layout.column()
        split = col_root.split(factor = 0.5, align = False)
        box = split.box()
        box.label(text="rename select")

        col = box.column()
        col.prop(props, "rename_string")
        
        
        #spl_sel = col.split(factor = 0.2, align = False)
        row1 = col.row()
        row1.alignment = 'LEFT'
        row1.operator("kiatools.rename_select" , icon = 'VIEW_PAN')
        row1.operator("kiatools.rename_dropper" , icon = 'EYEDROPPER')
        row1.operator("kiatools.rename_common_renumber" , icon = 'LINENUMBERS_ON')
        row1.prop(props, "rename_start_num")

        split1 = col.split(factor = 0.5, align = False)
        split1.operator("kiatools.rename_by_rule")

        row2 =split1.row()
        row2.operator("kiatools.rename_add" , text = 'Prefix').op = 'PREFIX'
        row2.operator("kiatools.rename_add", text = 'Suffix').op = 'SUFFIX'

        

        #split = split.split(factor = , align = False)
        box = split.box()
        #box = row.box()
        col = box.column()
        col.operator("kiatools.rename_replace")
        col.prop(props, "from_string")
        col.prop(props, "to_string")
        
        box = col_root.box()

        row = box.row()

        box1 = row.box()
        box1.label(text="replace")
        col = box1.column()        
        for s in ('high>low' , 'low>high' , '.>_'):
            col.operator("kiatools.rename_add", text = s).op = s

        box1 = row.box()
        box1.label(text="shape name")
        col = box1.column()        
        for s in ('object','maya'):
            col.operator("kiatools.rename_mesh", text = s).op = s

        box1 = row.box()
        box1.label(text="add")
        col = box1.column()        
        for s in ('org',):
            col.operator("kiatools.rename_add_defined", text = s).op = s


class KIATOOLS_OT_rename_continuous_renumber(Operator):
    """入力した文字列の末尾に連番を振るリネーム"""
    bl_idname = "kiatools.rename_common_renumber"
    bl_label = ""
    def execute(self, context):
        rename.continuous_renumber()
        return {'FINISHED'}

class KIATOOLS_OT_rename_by_rule(Operator):
    """複数選択し、最後に選択したノード名のネーミングルールに従ってリネームする。"""
    bl_idname = "kiatools.rename_by_rule"
    bl_label = "rename by rule"
    def execute(self, context):
        rename.by_rule()
        return {'FINISHED'}

#プレフィックスとサフィックスの追加
class KIATOOLS_OT_rename_add(Operator):
    """プレフィクスを追加する。番号は振らない。"""
    bl_idname = "kiatools.rename_add"
    bl_label = ""
    op : StringProperty()
    def execute(self, context):
        rename.add(self.op)
        return {'FINISHED'}

class KIATOOLS_OT_rename_replace(Operator):
    """fromの文字列をtoに置き換える"""
    bl_idname = "kiatools.rename_replace"
    bl_label = "replace"
    def execute(self, context):
        rename.replace()
        return {'FINISHED'}

class KIATOOLS_OT_rename_replace_defined(Operator):
    bl_idname = "kiatools.rename_replace_defined"
    bl_label = ""
    op : StringProperty()
    def execute(self, context):
        rename.replace_defined(self.op)
        return {'FINISHED'}

class KIATOOLS_OT_rename_mesh(Operator):
    """メッシュの名前をオブジェクト名に合わせる"""
    bl_idname = "kiatools.rename_mesh"
    bl_label = "メッシュ名をオブジェクト名に修正"
    op : StringProperty()
    def execute(self, context):
        rename.mesh(self.op)
        return {'FINISHED'}

class KIATOOLS_OT_rename_add_defined(Operator):
    bl_idname = "kiatools.rename_add_defined"
    bl_label = ""
    op : StringProperty()
    def execute(self, context):
        rename.add_defined(self.op)
        return {'FINISHED'}

class KIATOOLS_OT_rename_select(Operator):
    """名前フィールドのワードで選択する"""
    bl_idname = "kiatools.rename_select"
    bl_label = ""
    def execute(self, context):
        rename.select()
        return {'FINISHED'}

#アクティブなオブジェクトの名前をフィールドに入力する
class KIATOOLS_OT_rename_dropper(Operator):
    """アクティブなオブジェクトの名前をフィールドに入力する"""
    bl_idname = "kiatools.rename_dropper"
    bl_label = ""
    def execute(self, context):
        rename.dropper()
        return {'FINISHED'}



#---------------------------------------------------------------------------------------
#ここから下のリネームツール、未対応
#---------------------------------------------------------------------------------------
class Rename_del_suffix(bpy.types.Operator):
    """アンダーバーで区切られたサフィックスを削除する"""
    bl_idname = "object.rename_del_suffix"
    bl_label = "suffixを削除"

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            buf = ob.name.split('_')
            new = ob.name.replace('_'+buf[-1],'')
            print(ob.data.name)
            ob.name = new
            ob.data.name = new#メッシュの名前もついでに変更する
        return {'FINISHED'}


class Rename_Del_Suffix_number(bpy.types.Operator):
    """ノード名の末尾の.数字を削除"""
    bl_idname = "object.rename_del_suffix_number"
    bl_label = "ノード名の末尾の.数字を削除"

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            buf = ob.name.split(".")
            #末尾が数字か調べる
            if buf[-1].isdigit():
                ob.name = ob.name[:-(len(buf[-1])+1)]
        return {'FINISHED'}

#前提条件として、orgは先頭の要素ではない、orgの前に必ず数字がついてる
class Renumber_Pre_Org(bpy.types.Operator):
    """orgの前の番号をスタート番号から順番に番号を振りなおす"""
    bl_idname = "object.renumber_pre_org"
    bl_label = "orgの前の番号を振りなおす"

    def execute(self, context):
        num = bpy.context.scene.nico2_rename_start_number
        for ob in bpy.context.selected_objects:
            buf = ob.name.split("_")

            #org.001みたいになっている場合も考慮する必要あり

            for i,b in enumerate(buf):
                if b.find('org') != -1:
                    index = i - 1

            buf[index] = '%02d' % num
            num += 1

            newname = ''
            for b in buf:
                newname += b + '_'

            ob.name = newname[:-1] #最後の _ を削除している
        return {'FINISHED'}






classes = (
    KIATOOLS_Props_OA,

    KIATOOLS_PT_toolPanel,
    KIATOOLS_MT_kia_helper_tools,
    KIATOOLS_MT_modelingtools,
    KIATOOLS_MT_object_applier,
    KIATOOLS_MT_curvetools,
    KIATOOLS_MT_etc,

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

    #instance
    KIATOOLS_OT_instance_select_collection,
    KIATOOLS_OT_instance_instancer,

    KIATOOLS_OT_modifier_asign,
    KIATOOLS_OT_modifier_show,
    KIATOOLS_OT_modifier_hide,
    KIATOOLS_OT_modifier_apply,
    KIATOOLS_OT_modifier_select_curve,
    KIATOOLS_OT_modifier_select_boolean,

    #コンストレイン
    KIATOOLS_OT_constraint_asign,
    KIATOOLS_OT_instance_mirror,

    #object applier
    KIATOOLS_MT_new_scene,
    KIATOOLS_OT_move_model,
    KIATOOLS_OT_apply_collection,
    KIATOOLS_OT_remove_empty_collection,
    KIATOOLS_OT_apply_particle_instance,
    KIATOOLS_OT_apply_model,
    KIATOOLS_OT_move_collection,

    #transform
    KIATOOLS_OT_swap_axis,

    #etc
    KIATOOLS_OT_transform_rotate_axis,
    KIATOOLS_OT_transform_scale_abs,
    KIATOOLS_OT_constraint_to_bone,
    KIATOOLS_OT_refernce_make_proxy,
    KIATOOLS_OT_refernce_make_link,

    #リネーム
    KIATOOLS_MT_rename,
    KIATOOLS_OT_rename_continuous_renumber,
    KIATOOLS_OT_rename_by_rule,
    KIATOOLS_OT_rename_add,
    KIATOOLS_OT_rename_replace,
    KIATOOLS_OT_rename_replace_defined,
    KIATOOLS_OT_rename_mesh,
    KIATOOLS_OT_rename_add_defined,
    KIATOOLS_OT_rename_select,
    KIATOOLS_OT_rename_dropper
    
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.kiatools_oa = PointerProperty(type=KIATOOLS_Props_OA)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.kiatools_oa