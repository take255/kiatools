import bpy
import math
import imp

from mathutils import Matrix

from . import utils
from . import modifier
from . import locator

imp.reload(utils)
imp.reload(locator)


# #現在のコレクション表示状態を保持する
# class KIATOOLS_OT_preserve_collections(bpy.types.Operator):
#     """現在のコレクション表示状態を保持する"""
#     bl_idname = "kiatools.preserve_collections"
#     bl_label = ""

#     def execute(self, context):
#         props = bpy.context.scene.kiatools_oa
#         props.displayed_allcollections.clear()

#         for col in bpy.context.scene.collection.children:            
#             if bpy.context.window.view_layer.layer_collection.children[col.name].exclude == False:
#                     props.displayed_allcollections.add().name = col.name

#         return {'FINISHED'}


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
    KIATOOLS_OT_const_add_copy_transform,
    #KIATOOLS_OT_preserve_collections

)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        