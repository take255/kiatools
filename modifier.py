import bpy,bmesh
import imp

from . import utils
imp.reload(utils)


# class ModifierONNOFFTools(bpy.types.Operator):
#     bl_idname = "object.modifieronnofftools"
#     bl_label = "モディファイヤONOFFツールtest"

#     def invoke(self, context, event):
#         return context.window_manager.invoke_props_dialog(self)

#     def draw(self, context):
#         scn = context.scene
#         box = self.layout.box()
#         box.label( text = 'モディファイヤの追加' )
#         row = box.row(align=True)
#         row.alignment = 'EXPAND'

#         row.operator( "object.add_subsurf_modifier" , icon = 'MODIFIER')
#         row.operator( "object.add_solidify_modifier" , icon = 'MODIFIER')

#     def execute(self, context):
#         #main(context)
#         return {'FINISHED'}



class KIATOOLS_MT_modifiertools(bpy.types.Operator):
    bl_idname = "kiatools.modifiertools"
    bl_label = "modifiertools"


    def execute(self, context):
        return {'FINISHED'}


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        scn = context.scene

        #モディファイヤ表示、非表示
        box = self.layout.box()
        box.label( text = 'select' )
        box.operator( "kiatools.selectmodifiercurve" , icon = 'MODIFIER')



        # row = box.row(align=True)
        # row.alignment = 'EXPAND'

        

        # for mod in ("solodify", "shrinkwrap","mirror","armature"):
        #     row.prop(scn, "bool_showhide_%s" % mod, icon='RESTRICT_VIEW_OFF', toggle=True)

        # #モディファイヤ追加1
        # box = self.layout.box()
        # box.label( text = 'モディファイヤの追加' )
        # row = box.row(align=True)
        # row.alignment = 'EXPAND'

        # row.operator( "object.add_subsurf_modifier" , icon = 'MODIFIER')
        # row.operator( "object.add_solidify_modifier" , icon = 'MODIFIER')
        # row.operator( "object.add_shrinkwrap_modifier" , icon = 'MODIFIER')

        #モディファイヤ追加2
        row = box.row(align=True)
        row.alignment = 'EXPAND'

        #row.operator( "kiatools.add_bevel_modifier" , icon = 'MODIFIER')
        #row.operator( "kiatools.add_shrinkwrap_modifier_2node" , icon = 'MODIFIER')
        row.operator( "kiatools.add_lattice_modifier_2node" , icon = 'MODIFIER')

       
        # #モディファイヤアトリビュート調整
        # box = self.layout.box()
        # box.label( text = 'モディファイヤの調整' )

        # row = box.row(align=True)
        # row.alignment = 'EXPAND'
        # row.prop(scn, "slider_solidify_thickness", icon='BLENDER', toggle=True)
        # row.prop(scn, "slider_shrinkwrap_offset", icon='BLENDER', toggle=True)

        # row = box.row(align=True)
        # row.alignment = 'EXPAND'
        # row.prop(scn, "slider_bevel_width", icon='BLENDER', toggle=True)
        # row.prop(scn, "slider_array_count", icon='BLENDER', toggle=True)


        # #モディファイヤの移動
        # box = self.layout.box()
        # box.label( text = 'モディファイヤを最上位に移動' )
        # row = box.row(align=True)
        # row.alignment = 'EXPAND'

        # row.operator( "object.movetop_shrinkwrap" , icon = 'MODIFIER')
        # row.operator( "object.movetop_mirror" , icon = 'MODIFIER')

        # box.prop(scn, "apply_modifier_type", icon='BLENDER', toggle=True)
        # box.operator( "object.apply_modifier" , icon = 'MODIFIER')
        
        
        # box.operator( "object.modifieronnofftools" , icon = 'MODIFIER')
        

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


#二つのノードを選択してモディファイヤアサインと同時にターゲットを割り当てる
#ターゲットモデルをアクティブとするので　モディファイヤをアサインしたいモデルをまず選択、最後にターゲットを選択する
class AddModifier_2Node(bpy.types.Operator):
    modifier_type = ''
    modifier_name = ''

    def execute(self, context):
        sel = bpy.context.selected_objects
        active=bpy.context.active_object

        result = []
        for obj in sel:
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



class KIATOOLS_OT_add_lattice_modifier_2node(AddModifier_2Node):
    """ラティスモディファイヤ追加。複数モデルを選択し、最後にラティスモデルを選択する。"""
    bl_idname = "kiatools.add_lattice_modifier_2node"
    bl_label = "Lattice2node"
    modifier_type = 'LATTICE'
    modifier_name = 'LATTICE'

    def settarget(self,m,active):
        m.object = active




classes = (
    KIATOOLS_MT_modifiertools,
    KIATOOLS_OT_select_modifier_curve,
    KIATOOLS_OT_add_lattice_modifier_2node
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    #bpy.types.Scene.kiatools_oa = PointerProperty(type=KIATOOLS_Props_OA)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


# def register():    
#     addModifier.register()
#     modify_paramater.register()
#     move.register()
#     apply.register()
#     showhide.register()

#     bpy.utils.register_class(ModifierONNOFFTools)
#     bpy.utils.register_class(ModifierTools)


# def unregister():
#     addModifier.unregister()
#     modify_paramater.unregister()
#     move.unregister()
#     apply.unregister()
#     showhide.unregister()

#     bpy.utils.unregister_class(ModifierONNOFFTools)
#     bpy.utils.unregister_class(ModifierTools)
