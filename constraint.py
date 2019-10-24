import bpy
import imp

from . import utils
imp.reload(utils)

TYPE = (
('COPY_TRANSFORMS','COPY_TRANSFORMS','') ,
('COPY_TRANSFORMS','COPY_TRANSFORMS','') ,
('CURVE','CURVE','') ,
('ARRAY','ARRAY',''),
('BOOLEAN','BOOLEAN',''),
)

#Constraint---------------------------------------------------------------------------------------
#アクティブをコンスト先にする
def assign():
    props = bpy.context.scene.kiatools_oa

    selected = utils.selected()
    active = utils.getActiveObj()

    utils.deselectAll()


    result = []
    for obj in selected:
        if obj != active:
            result.append(obj)

            #選択モデルをアクティブに
            utils.activeObj(obj)

            constraint =obj.constraints.new(props.const_type)
            constraint.target = active
    utils.mode_o
    utils.deselectAll()
