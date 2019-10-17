import bpy,bmesh
import imp

from . import utils
imp.reload(utils)


#モディファイヤのパラメータ値を取得
def get_param():
    act  = utils.getActiveObj()
    if act == None:
        return

    props = bpy.context.scene.kiatools_oa
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

    props.mod_init = False

# #モディファイヤのリストから選択した状態を取得
# def get_selected_list_param(self,context):
#     props = bpy.context.scene.kiatools_oa    
#     modtype = props.modifier_type

#     act = utils.getActiveObj()

#     #print('mod----')    
#     for mod in act.modifiers:        
#         if modtype == mod.type:
#             print(modtype)


#モディファイヤの値調整
#Solidifyの厚み　、Shrinkwrapオフセット、ベベル幅調整　、アレイの個数
def apply(self,context):
    act = utils.getActiveObj()
    props = bpy.context.scene.kiatools_oa
    
    print(props.mod_init)
    if props.mod_init:
        #props.mod_init = False
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


def assign():
    props = bpy.context.scene.kiatools_oa    
    modtype = props.modifier_type

    sel = bpy.context.selected_objects
    active = utils.getActiveObj()

    result = []
    for obj in sel:
        if obj != active:
            result.append(obj)
            m = obj.modifiers.new( modtype , type = modtype )

            if modtype == 'LATTICE' or modtype == 'CURVE':
                m.object = active

            elif modtype == 'SHRINKWRAP':
                mm.target = active


    # bpy.ops.object.mode_set(mode='OBJECT')
    # bpy.ops.object.select_all(action='DESELECT')
    utils.mode_o()
    utils.deselectAll()

    for ob in result:
        utils.select(ob,True)
        utils.activeObj(ob)


def show(status):
    props = bpy.context.scene.kiatools_oa    
    modtype = props.modifier_type

    sel = utils.selected()
    active = utils.getActiveObj()

    result = []
    for obj in sel:
        for mod in obj.modifiers:        
            
            if modtype == mod.type:
                mod.show_viewport = status
