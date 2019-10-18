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
from . import curve


imp.reload(utils)
imp.reload(modifier)
imp.reload(display)
imp.reload(object_applier)
imp.reload(modeling)
imp.reload(curve)


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
    modifier_type : EnumProperty(items = modifier.TYPE , name = 'modifier' )


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
        self.layout.operator("kiatools.displaytools", icon='BLENDER')



class KIATOOLS_MT_displaytools(bpy.types.Operator):

    bl_idname = "kiatools.displaytools"
    bl_label = "display toggle"

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

        row = layout.row(align=False)
        box = row.box()

        row = box.row(align=True)

        #row.alignment = 'LEFT'
        row.prop(props, "const_bool" , icon='CONSTRAINT')
        row.prop(props, "showhide_bool" , icon='EMPTY_DATA')

        box = row.box()
        box.label( text = 'collection' )

        row = box.row()
        row.prop(props, "showhide_collection_bool" , icon='GROUP')
        row.operator( "kiatools.preserve_collections" , icon = 'IMPORT')



class KIATOOLS_MT_modelingtools(bpy.types.Operator):

    bl_idname = "kiatools.modelingtools"
    bl_label = "modeling tools"


    def execute(self, context):
        return{'FINISHED'}

    def invoke(self, context, event):
        #アクティブオブジェクトのコンストレインの状態を取得
        # display.get_constraint_status()
        # modifier.get_param()
        # props = bpy.context.scene.kiatools_oa

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        #scn = context.scene
        props = bpy.context.scene.kiatools_oa
        layout=self.layout

        row = layout.row(align=False)
        box = row.box()

        row = box.row()

        # box1 = row.box()
        # box1.label( text = 'display tgl' , icon = 'IMGDISPLAY')
        # box1.prop(props, "const_bool" , icon='CONSTRAINT')
        # box1.prop(props, "showhide_bool" , icon='EMPTY_DATA')

        # row1 = box1.row(align=True)
        # row.alignment = 'LEFT'
        # row1.prop(props, "showhide_collection_bool" , icon='GROUP')
        # row1.operator( "kiatools.preserve_collections" , icon = 'IMPORT')


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

        box = layout.box()
        box.label( text = 'curve' )
        row = box.row()

        box1 = row.box()
        box1.label( text = 'create' )
        box1.operator( "kiatools.curve_create_with_bevel" , icon = 'MODIFIER')
        box1.operator( "kiatools.curve_create_liner" , icon = 'MODIFIER')


        box2 = row.box()
        box2.label( text = 'bevel' )
        box2.operator( "kiatools.curve_assign_bevel" , icon = 'MODIFIER')
        box2.operator( "kiatools.curve_assign_circle_bevel" , icon = 'MODIFIER')
        box2.operator( "kiatools.curve_assign_liner_bevel" , icon = 'MODIFIER')

        box3 = row.box()
        box3.label( text = 'select' )
        box3.operator( "kiatools.curve_select_bevel" , icon = 'MODIFIER')


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


#Operator--------------------------------------------------------------------

#Curve Tool
class KIATOOLS_OT_curve_create_with_bevel(bpy.types.Operator):
        """ベベル込みのカーブを作成する。"""
        bl_idname = "kiatools.curve_create_with_bevel"
        bl_label = "bevel curve"
        
        def execute(self, context):
            curve.create_with_bevel()
            return {'FINISHED'}

class KIATOOLS_OT_curve_assign_bevel(bpy.types.Operator):
        """カーブにベベルをアサイン\nカーブ、ベベルカーブの順に選択して実行"""
        bl_idname = "kiatools.curve_assign_bevel"
        bl_label = "select"
        
        def execute(self, context):
            curve.assign_bevel()
            return {'FINISHED'}

class KIATOOLS_OT_curve_assign_circle_bevel(bpy.types.Operator):
        """カーブに円のベベルをアサイン"""
        bl_idname = "kiatools.curve_assign_circle_bevel"
        bl_label = "circle"
        
        def execute(self, context):
            curve.assign_circle_bevel()
            return {'FINISHED'}

class KIATOOLS_OT_curve_assign_liner_bevel(bpy.types.Operator):
        """カーブに直線のベベルをアサイン"""
        bl_idname = "kiatools.curve_assign_liner_bevel"
        bl_label = "liner"
        
        def execute(self, context):
            curve.assign_liner_bevel()
            return {'FINISHED'}


class KIATOOLS_OT_curve_create_liner(bpy.types.Operator):
        """直線カーブを作成"""
        bl_idname = "kiatools.curve_create_liner"
        bl_label = "add liner"
        
        def execute(self, context):
            curve.create_liner()
            return {'FINISHED'}

class KIATOOLS_OT_curve_select_bevel(bpy.types.Operator):
        """選択カーブのベベルを選択"""
        bl_idname = "kiatools.curve_select_bevel"
        bl_label = "bevel"
        
        def execute(self, context):
            curve.select_bevel()
            return {'FINISHED'}




classes = (
    KIATOOLS_Props_OA,

    KIATOOLS_MT_toolPanel,
    KIATOOLS_MT_displaytools,
    KIATOOLS_MT_modelingtools,
    KIATOOLS_MT_object_applier,

    KIATOOLS_OT_curve_create_with_bevel,
    KIATOOLS_OT_curve_create_liner,
    KIATOOLS_OT_curve_assign_bevel,
    KIATOOLS_OT_curve_assign_circle_bevel,
    KIATOOLS_OT_curve_assign_liner_bevel,
    KIATOOLS_OT_curve_select_bevel

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



 
