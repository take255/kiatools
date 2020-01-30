import bpy


def del_half_x():
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='DESELECT')#全選択解除してからの
    bpy.ops.mesh.select_all(action='TOGGLE')#全選択

    bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(1, 0, 0), use_fill=False, clear_inner=True)
    bpy.ops.object.editmode_toggle()

    # bpy.ops.object.select_all(action='DESELECT')

    
    # bpy.ops.object.editmode_toggle()
    # bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(1, 0, 0), use_fill=True, clear_outer=True)
    # bpy.ops.object.editmode_toggle()    