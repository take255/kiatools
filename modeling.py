import bpy
import math
import imp

from mathutils import Matrix

from . import utils
from . import modifier
from . import locator

imp.reload(utils)
imp.reload(locator)


class KIATOOLS_OT_replace_locator(bpy.types.Operator):
    """モデルに位置にロケータを配置してコンストレインする。モデルのトランスフォームは初期値にする。"""
    bl_idname = "kiatools.replace_locator"
    bl_label = "to locator"

    def execute(self, context):
        locator.replace()
        return {'FINISHED'}

class KIATOOLS_OT_replace_locator_facenormal(bpy.types.Operator):
    """モデルに位置にロケータを配置してコンストレインする。モデルのトランスフォームは初期値にする。"""
    bl_idname = "kiatools.replace_locator_facenormal"
    bl_label = "face normal"

    def execute(self, context):
        locator.replace_facenormal()
        return {'FINISHED'}

class KIATOOLS_OT_group(bpy.types.Operator):
    """ロケータで選択モデルをまとめる"""
    bl_idname = "kiatools.group"
    bl_label = "group"

    def execute(self, context):
        locator.group()
        return {'FINISHED'}


#親子付けの際、ワールドのトランスフォームを維持したいので親のマトリックスを掛け合わせる
class KIATOOLS_OT_preserve_child(bpy.types.Operator):
    """一時的に子供を別ノードに逃がす。親を選択して実行する"""
    bl_idname = "kiatools.preserve_child"
    bl_label = "preserve"

    def execute(self, context):
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
        return {'FINISHED'}


#親子付けの際、ワールドのトランスフォームを維持したいので親のマトリックスを掛け合わせる
class KIATOOLS_OT_restore_child(bpy.types.Operator):
    """一時的に逃がした子供を復旧させる。もとの親を選択して実行する。"""
    bl_idname = "kiatools.restore_child"
    bl_label = "resore"

    def execute(self, context):
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
        return {'FINISHED'}


#選択したモデルのモディファイヤカーブのカーブ選択。
class KIATOOLS_OT_select_modifier_curve(bpy.types.Operator):
    """選択したモデルのモディファイヤカーブのカーブ選択"""
    bl_idname = "kiatools.selectmodifiercurve"
    bl_label = "EditCurve"

    def execute(self, context):
        sel = bpy.context.selected_objects

        utils.deselectAll()
        

        curve = []

        for ob in sel:
            for i, mod in enumerate(ob.modifiers):
                if mod.type == 'CURVE':
                    curve.append(mod.object)

        for obj in curve:
            utils.select(obj,True)
            utils.activeObj(obj)


        utils.mode_e()
        
        return {'FINISHED'}


#選択したモデルの所属するコレクションをハイド
class KIATOOLS_OT_collections_hide(bpy.types.Operator):
    """選択したオブジェクトが属するコレクションをハイド"""
    bl_idname = "kiatools.collections_hide"
    bl_label = "hide"

    def execute(self, context):
        selected = utils.selected()
        
        for ob in selected:
            for col in ob.users_collection:
                col.hide_viewport = True


        return {'FINISHED'}

#現在のコレクション表示状態を保持する
class KIATOOLS_OT_preserve_collections(bpy.types.Operator):
    """現在のコレクション表示状態を保持する"""
    bl_idname = "kiatools.preserve_collections"
    bl_label = ""

    def execute(self, context):
        props = bpy.context.scene.kiatools_oa
        props.displayed_allcollections.clear()

        for col in bpy.context.scene.collection.children:            
            if bpy.context.window.view_layer.layer_collection.children[col.name].exclude == False:
                    props.displayed_allcollections.add().name = col.name



        return {'FINISHED'}



#Modifier---------------------------------------------------------------------------------------
#二つのノードを選択してモディファイヤアサインと同時にターゲットを割り当てる
#ターゲットモデルをアクティブとするので　モディファイヤをアサインしたいモデルをまず選択、最後にターゲットを選択する
class KIATOOLS_OT_modifier_asign(bpy.types.Operator):
    """モディファイヤをアサインする"""
    bl_idname = "kiatools.modifier_asign"
    bl_label = "assign"

    def execute(self, context):
        modifier.assign()
        return {'FINISHED'}


class KIATOOLS_OT_modifier_show(bpy.types.Operator):    
    """モディファイヤを表示する"""
    bl_idname = "kiatools.modifier_show"
    bl_label = "show"

    def execute(self, context):
        modifier.show(True)
        return {'FINISHED'}


class KIATOOLS_OT_modifier_hide(bpy.types.Operator):    
    """モディファイヤを表示する"""
    bl_idname = "kiatools.modifier_hide"
    bl_label = "hide"

    def execute(self, context):
        modifier.show(False)
        return {'FINISHED'}


#Constraint---------------------------------------------------------------------------------------
#アクティブをコンスト先にする
class Constraint_Add(bpy.types.Operator):
    const_type = ''

    def execute(self, context):
        selected = utils.selected()
        active = utils.getActiveObj()

        utils.deselectAll()
        #objects = bpy.context.scene.objects
        result = []
        for obj in selected:
            if obj != active:
                result.append(obj)

                #選択モデルをアクティブに
                utils.activeObj(obj)

                constraint =obj.constraints.new(self.const_type)
                constraint.target = active
        utils.mode_o
        utils.deselectAll()

        return {'FINISHED'}



class KIATOOLS_OT_const_add_copy_transform(Constraint_Add):
    """Copy Transform コンストレイン追加"""
    bl_idname = "kiatools.const_add_copy_transform"
    bl_label = "Copy Transforms"
    const_type = 'COPY_TRANSFORMS'
    #const_name = 'COPY_TORANSFORMS'


classes = (
    KIATOOLS_OT_group,
    KIATOOLS_OT_restore_child,
    KIATOOLS_OT_preserve_child,
    KIATOOLS_OT_select_modifier_curve,

    KIATOOLS_OT_modifier_asign,
    KIATOOLS_OT_modifier_show,
    KIATOOLS_OT_modifier_hide,

    KIATOOLS_OT_const_add_copy_transform,
    KIATOOLS_OT_replace_locator,
    KIATOOLS_OT_replace_locator_facenormal,
    KIATOOLS_OT_collections_hide,
    KIATOOLS_OT_preserve_collections

)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        