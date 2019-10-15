import bpy
import math
import imp

from mathutils import Matrix

from . import utils
imp.reload(utils)

#コンストレインが１つでもONならTrue
#muteがONなのが
def get_constraint_status():

    props = bpy.context.scene.kiatools_oa

    act = utils.getActiveObj()
    status = False
    for const in act.constraints:
        status = (status or const.mute)

    props.const_bool = status

#オブジェクトをコレクションに移動
def move_collection( ob , col ):
    collections = ob.users_collection
    for c in collections:
         c.objects.unlink(ob)

    col.objects.link(ob)



#モディファイヤのパラメータ値を取得
def get_modifier_param():
    props = bpy.context.scene.kiatools_oa
    act  = utils.getActiveObj()

    props.mod_init = True
    for mod in act.modifiers:
        if mod.type == 'SOLIDIFY':
            props.solidify_thickness = mod.thickness

        if mod.type == 'ARRAY':
            props.array_count = mod.count

        if mod.type == 'BEVEL':
            props.bevel_width = mod.width

        if mod.type == 'SHRINKWRAP':
            props.wrap_ofset = mod.offset


#モデルに位置にロケータを配置してコンストレインする。
#中間にロケータをかます。親のロケータの形状をsphereにする。
#モデルのトランスフォームは初期値にする
#ロケータを '09_ConstRoot'　に入れる

class KIATOOLS_OT_replace_locator(bpy.types.Operator):
    """モデルに位置にロケータを配置してコンストレインする。モデルのトランスフォームは初期値にする。"""
    bl_idname = "kiatools.replace_locator"
    bl_label = "to locator"

    def execute(self, context):
        scn = bpy.context.scene
        selected = utils.selected()
        colname = '09_ConstRoot'
        #master = 'Master Collection'
        #コレクションが存在していればそのまま使用、なければ新規作成
        if colname in scn.collection.children.keys():
            col = scn.collection.children[colname]

        else:
            col = bpy.data.collections.new(colname)
            scn.collection.children.link(col)


        for obj in selected:
            #ロケータを作成
            bpy.ops.object.empty_add(type='PLAIN_AXES')
            empty = bpy.context.active_object
            empty.name =  obj.name + '_constlocator'
            empty.matrix_world = obj.matrix_world

            move_collection(empty , col)
            
            # if not col in empty.users_collection:                 
            #     col.objects.link(empty)
            # scn.collection.objects.unlink(empty)

            #親のロケータを作成
            bpy.ops.object.empty_add(type='SPHERE')
            empty_p = bpy.context.active_object
            empty_p.name = obj.name + '_parent'
            empty_p.matrix_world = Matrix()

            move_collection(empty_p , col)

            # if not  col in empty_p.users_collection:
            #     col.objects.link(empty_p)
            # scn.collection.objects.unlink(empty_p)


            constraint =empty_p.constraints.new('COPY_TRANSFORMS')
            constraint.target = empty
            constraint.target_space ='WORLD'
            constraint.owner_space = 'WORLD'

            
            obj.matrix_world = Matrix()
            obj.parent = empty_p


        return {'FINISHED'}

#選択したモデルをロケータでまとめる
#アクティブなモデルの名前を継承する
class KIATOOLS_OT_group(bpy.types.Operator):
    """ロケータで選択モデルをまとめる"""
    bl_idname = "kiatools.group"
    bl_label = "group"

    def execute(self, context):
        selected = utils.selected()
        act = utils.getActiveObj()
        locatorname = act.name + '_parent'

        bpy.ops.object.empty_add(type='PLAIN_AXES')
        empty = utils.getActiveObj()
        empty.name = locatorname
        empty.matrix_world = Matrix()

        for obj in selected:
            obj.parent = empty
 
        return {'FINISHED'}


#親子付けの際、ワールドのトランスフォームを維持したいので親のマトリックスを掛け合わせる
class KIATOOLS_OT_preserve_child(bpy.types.Operator):
    """一時的に子供を別ノードに逃がす。親を選択して実行する"""
    bl_idname = "kiatools.preserve_child"
    bl_label = "preserve child"

    def execute(self, context):
        selected = utils.selected()

        for obj in selected:
            #一時的に退避するロケータを作成
            name = '%s_temp' % obj.name
            bpy.ops.object.empty_add(type='PLAIN_AXES')
            #empty = bpy.context.active_object
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
    bl_label = "resore child"

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


#Add Modifier---------------------------------------------------------------------------------------

#二つのノードを選択してモディファイヤアサインと同時にターゲットを割り当てる
#ターゲットモデルをアクティブとするので　モディファイヤをアサインしたいモデルをまず選択、最後にターゲットを選択する
class AddModifier_2Node(bpy.types.Operator):
    modifier_type = ''
    modifier_name = ''

    def execute(self, context):
        sel = bpy.context.selected_objects
        #active=bpy.context.active_object
        active = utils.getActiveObj()
        print('active-----')
        print(active.name)

        result = []
        for obj in sel:
            print('obj-----')
            print(obj.name)


            if obj != active:
                result.append(obj)
                m = obj.modifiers.new( self.modifier_name , type = self.modifier_type )
                self.settarget(m,active)
                #m.target = active
                self.setAttr(m)

        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        for ob in result:
            #ob.select = True
            utils.select(ob,True)
            utils.activeObj(ob)
            #bpy.context.scene.objects.active = ob #アクティブにしておかないとモディファイヤをmoveしたとき固まるぞ


        return {'FINISHED'}

    def settarget(self,m,active):
        m.target = active

    def setAttr(self,m):
        pass


class KIATOOLS_OT_add_lattice(AddModifier_2Node):
    """ラティスモディファイヤ追加。複数モデルを選択し、最後にラティスモデルを選択する。"""
    bl_idname = "kiatools.add_lattice"
    bl_label = "Lattice"
    modifier_type = 'LATTICE'
    modifier_name = 'LATTICE'

    def settarget(self,m,active):
        m.object = active

class KIATOOLS_OT_add_shrinkwrap(AddModifier_2Node):
    """シュリンクラップモディファイヤ追加\n複数モデルを選択し、最後にラップモデルを選択する。"""
    bl_idname = "kiatools.add_shrinkwrap"
    bl_label = "Shrinkwrap"
    modifier_type = 'SHRINKWRAP'
    modifier_name = 'Shrinkwrap'


class KIATOOLS_OT_add_curve(AddModifier_2Node):
    """カーブモディファイヤ追加\n複数モデルを選択し、最後にカーブモデルを選択する。"""
    bl_idname = "kiatools.add_curve"
    bl_label = "Curve"
    modifier_type = 'CURVE'
    modifier_name = 'CURVE'

    def settarget(self,m,active):
        m.object = active

#Constraint---------------------------------------------------------------------------------------
#アクティブをコンスト先にする
class Constraint_Add(bpy.types.Operator):
    const_type = ''
    #const_name = ''

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
                #objects.active = obj
                utils.activeObj(obj)

                constraint =obj.constraints.new(self.const_type)
                constraint.target = active
                #constraint.target_space ='WORLD'
                #constraint.owner_space = 'WORLD'
        
        # bpy.ops.object.mode_set(mode='OBJECT')
        # bpy.ops.object.select_all(action='DESELECT')
        utils.mode_o
        utils.deselectAll()

        # for ob in result:
        #     ob.select = True
        #     bpy.context.scene.objects.active = ob #アクティブにしておかないとモディファイヤをmoveしたとき固まるぞ


        return {'FINISHED'}

    def setAttr(self,m):
        pass


class KIATOOLS_OT_const_add_copy_transform(Constraint_Add):
    """Copy Transform コンストレイン追加"""
    bl_idname = "kiatools.const_add_copy_transform"
    bl_label = "Copy Transforms"
    const_type = 'COPY_TRANSFORMS'
    #const_name = 'COPY_TORANSFORMS'


#UI---------------------------------------------------------------------------------------
class KIATOOLS_MT_modelingtools(bpy.types.Operator):

    bl_idname = "kiatools.modelingtools"
    bl_label = "modeling tools"


    def execute(self, context):
        return{'FINISHED'}

    def invoke(self, context, event):
        #アクティブオブジェクトのコンストレインの状態を取得
        get_constraint_status()
        get_modifier_param()
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        #scn = context.scene
        props = bpy.context.scene.kiatools_oa
        layout=self.layout

        row = layout.row(align=False)
        box = row.box()

        row = box.row()
        row.prop(props, "const_bool" , icon='RESTRICT_VIEW_OFF')
        row.prop(props, "showhide_bool" , icon='RESTRICT_VIEW_OFF')
        row.operator( "kiatools.group" , icon = 'MODIFIER')

        row = box.row()
        row.operator( "kiatools.preserve_child" , icon = 'MODIFIER')
        row.operator( "kiatools.restore_child" , icon = 'MODIFIER')
        row.operator( "kiatools.replace_locator" , icon = 'MODIFIER')


        box = layout.box()
        box.label( text = 'modifier' )

        box.operator( "kiatools.selectmodifiercurve" , icon = 'MODIFIER')

        row = box.row()
        row.operator( "kiatools.add_lattice" , icon = 'MODIFIER')
        row.operator( "kiatools.add_shrinkwrap" , icon = 'MODIFIER')
        row.operator( "kiatools.add_curve" , icon = 'MODIFIER')

        row = box.row()
        row.prop(props, "solidify_thickness" , icon='RESTRICT_VIEW_OFF')
        row.prop(props, "shrinkwrap_offset" , icon='RESTRICT_VIEW_OFF')

        row = box.row()
        row.prop(props, "bevel_width" , icon='RESTRICT_VIEW_OFF')
        row.prop(props, "array_count" , icon='RESTRICT_VIEW_OFF')




        box = layout.box()
        box.label( text = 'constraint' )

        box.operator( "kiatools.const_add_copy_transform" , icon = 'MODIFIER')
        
        box.operator( "kiatools.collections_hide" , icon = 'MODIFIER')




        #box.label(text = 'トランスフォーム')
        # box.operator("object.scale_abs", icon = 'MODIFIER')

        # box.label(text = '軸変換(時計回り＋)')
        # row = box.row(align=True)
        # row.alignment = 'EXPAND'
        # row.operator("object.rotate_axis_x90")
        # row.operator("object.rotate_axis_x90_neg")
        # row.operator("object.rotate_axis_y90")
        # row.operator("object.rotate_axis_y90_neg")
        # row.operator("object.rotate_axis_z90")
        # row.operator("object.rotate_axis_z90_neg")

        # row = box.row(align=True)
        # row.alignment = 'EXPAND'
        # row.operator("object.rotate_axis_x180")
        # row.operator("object.rotate_axis_y180")
        # row.operator("object.rotate_axis_z180")


        # row = layout.row(align=False)
        # box = row.box()
        # box.label(text = 'ペアレント')

        # row = box.row(align=True)
        # row.alignment = 'EXPAND'

        # row.operator("object.preserve_child", icon = 'MODIFIER')
        # row.operator("object.restore_child", icon = 'MODIFIER')

        # row = box.row(align=True)
        # row.alignment = 'EXPAND'
        # row.operator("object.parent_children", icon = 'MODIFIER')

        # row = layout.row(align=False)
        # box = row.box()
        # box.label(text = 'カーブ')

        # row = box.row(align=True)
        # row.prop(scn, "change_hair_reso_value", icon='BLENDER', toggle=True)
        # row.operator("object.create_bevel_curve")

classes = (
    KIATOOLS_MT_modelingtools,
    KIATOOLS_OT_group,
    KIATOOLS_OT_restore_child,
    KIATOOLS_OT_preserve_child,
    KIATOOLS_OT_select_modifier_curve,

    KIATOOLS_OT_add_lattice,
    KIATOOLS_OT_add_shrinkwrap,
    KIATOOLS_OT_add_curve,

    KIATOOLS_OT_const_add_copy_transform,
    KIATOOLS_OT_replace_locator,
    KIATOOLS_OT_collections_hide

)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        