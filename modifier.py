import bpy,bmesh
import imp

from . import utils
imp.reload(utils)

TYPE = (
('LATTICE','LATTICE','') ,
('SHRINKWRAP','SHRINKWRAP','') ,
('CURVE','CURVE','') ,
('ARRAY','ARRAY',''),
('BOOLEAN','BOOLEAN',''),
)

COLLECTION_SEND_TO = '09_ModifierObjects'

#---------------------------------------------------------------------------------------
#モディファイヤを一か所に集める
#---------------------------------------------------------------------------------------
def send_to():
    col = utils.collection.create(COLLECTION_SEND_TO)

    mod_object = []
    for ob in utils.selected():
        for mod in ob.modifiers:
            if hasattr(mod , 'object' ):
                utils.collection.move_obj( ob , col )

#---------------------------------------------------------------------------------------
#モディファイヤのパラメータ値を取得
#---------------------------------------------------------------------------------------
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

        if mod.type == 'BEVEL':
            props.bevel_width = mod.width

        if mod.type == 'SHRINKWRAP':
            props.wrap_ofset = mod.offset

    props.mod_init = False


#---------------------------------------------------------------------------------------
#モディファイヤの値調整
#Solidifyの厚み　、Shrinkwrapオフセット、ベベル幅調整　、アレイの個数
#---------------------------------------------------------------------------------------
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


#---------------------------------------------------------------------------------------
#モディファイヤにターゲットを割り当てる場合とそれ以外で分ける
#---------------------------------------------------------------------------------------
def assign():
    props = bpy.context.scene.kiatools_oa    
    modtype = props.modifier_type

    sel = bpy.context.selected_objects
    active = utils.getActiveObj()
    result = []

    print(modtype)
    if modtype in ('LATTICE','CURVE','SHRINKWRAP','BOOLEAN'):
        #2node
        for obj in sel:
            if obj != active:
                result.append(obj)
                m = obj.modifiers.new( modtype , type = modtype )

                if modtype == 'LATTICE' or modtype == 'CURVE' or modtype == 'BOOLEAN':
                    m.object = active

                elif modtype == 'SHRINKWRAP':
                    m.target = active
    
    else:
        for obj in sel:
            result.append(obj)
            obj.modifiers.new( modtype , type = modtype )


    utils.mode_o()
    utils.deselectAll()

    for ob in result:
        utils.select(ob,True)
        utils.activeObj(ob)
    
    get_param()


#---------------------------------------------------------------------------------------
def show(status):
    props = bpy.context.scene.kiatools_oa    
    modtype = props.modifier_type

    sel = utils.selected()
    active = utils.getActiveObj()

    for obj in sel:
        for mod in obj.modifiers:        
            
            if modtype == mod.type:
                mod.show_viewport = status


#---------------------------------------------------------------------------------------
def apply_mod():
    props = bpy.context.scene.kiatools_oa    
    modtype = props.modifier_type

    sel = utils.selected()
    #active = utils.getActiveObj()

    for obj in sel:
        utils.activeObj(obj)
        for mod in obj.modifiers:                    
            if modtype == mod.type:
                bpy.ops.object.modifier_apply( modifier = mod.name )


#---------------------------------------------------------------------------------------
#選択したモデルのモディファイヤカーブのカーブ選択。
#---------------------------------------------------------------------------------------
def select(TYPE):
    sel = bpy.context.selected_objects
    utils.deselectAll()

    mod_object = []
    for ob in sel:
        for i, mod in enumerate(ob.modifiers):
            if mod.type == TYPE:
                mod_object.append(mod.object)

    for obj in mod_object:
        obj.hide_set(False)
        utils.select(obj,True)
        utils.activeObj(obj)


    utils.mode_e()
    