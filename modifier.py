import bpy,bmesh
import imp

from . import utils
imp.reload(utils)


#モディファイヤのパラメータ値を取得
def get_param():
    props = bpy.context.scene.kiatools_oa
    act  = utils.getActiveObj()

    props.mod_init = True
    for mod in act.modifiers:
        if mod.type == 'SOLIDIFY':
            props.solidify_thickness = mod.thickness

        if mod.type == 'ARRAY':
            props.array_count = mod.count
            props.array_offset_x = mod.relative_offset_displace[0]
            props.array_offset_y = mod.relative_offset_displace[1]
            props.array_offset_z = mod.relative_offset_displace[2]
            #props.array_count = mod.count
            #print(mod.relative_offset_displace[0])

        if mod.type == 'BEVEL':
            props.bevel_width = mod.width

        if mod.type == 'SHRINKWRAP':
            props.wrap_ofset = mod.offset



#モディファイヤの値調整
#Solidifyの厚み　、Shrinkwrapオフセット、ベベル幅調整　、アレイの個数
def apply(self,context):
    act = utils.getActiveObj()
    props = bpy.context.scene.kiatools_oa
    
    print(props.mod_init)
    if props.mod_init:
        props.mod_init = False
        return

    for mod in act.modifiers:
        if mod.type == 'SOLIDIFY':
            mod.thickness = props.solidify_thickness

        if mod.type == 'ARRAY':
            mod.count = props.array_count
            mod.relative_offset_displace[0] = props.array_offset_x
            mod.relative_offset_displace[1] = props.array_offset_y
            mod.relative_offset_displace[2] = props.array_offset_z

        if mod.type == 'BEVEL':
            mod.width = props.bevel_width

        if mod.type == 'SHRINKWRAP':
            mod.offset = props.shrinkwrap_offset