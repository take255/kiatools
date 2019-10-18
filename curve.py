import bpy
from . import utils

#ベベル込みのカーブを作成する
#ベベルはcurve_collenctionに格納される￥
def create_with_bevel():
    #ベベル用のサークル
    bpy.ops.curve.primitive_bezier_circle_add()
    circleobj = bpy.context.active_object
    circleobj.scale = (0.01,0.01,0.01) 
    circleobj.data.resolution_u = 6

    #カーブの作成
    bpy.ops.curve.primitive_bezier_curve_add()
    curve  = utils.getActiveObj()
    curve.data.bevel_object = circleobj
    curve.data.use_fill_caps = True
    curve.data.use_uv_as_generated = True


#直線カーブを作る
def create_liner():
    bpy.ops.curve.primitive_bezier_curve_add()
    act  = utils.getActiveObj()

    utils.mode_e()    
    curve = act.data.splines[0]
    for p in curve.points:
        #p.handle_type = 'AUTOMATIC'
        p.select = True
    bpy.ops.curve.handle_type_set(type = 'AUTOMATIC')
    utils.mode_o()

    return act

def assign_bevel_loop( selected , bevelobj):
    for obj in selected:
        obj.data.bevel_object = bevelobj
        obj.data.use_fill_caps = True
        obj.data.use_uv_as_generated = True    


def assign_bevel():
    selected = utils.selected()
    bevelobj = utils.getActiveObj()
    assign_bevel_loop( selected , bevelobj)

def assign_circle_bevel():
    selected = utils.selected()
    bpy.ops.curve.primitive_bezier_circle_add()
    bevelobj = bpy.context.active_object
    assign_bevel_loop( selected , bevelobj)

def assign_liner_bevel():
    selected = utils.selected()
    bevelobj = create_liner()
    assign_bevel_loop( selected , bevelobj)

def select_bevel():
    act  = utils.getActiveObj()
    bevelobj = act.data.bevel_object

    utils.deselectAll()

    utils.activeObj(bevelobj)
    utils.select(bevelobj,True)