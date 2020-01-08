import bpy
import imp

from mathutils import Vector

from . import utils
imp.reload(utils)

def apply_x(axis):
    selected = utils.selected()
    utils.deselectAll()

    for ob in selected:
        utils.act(ob)
        loc = Vector(ob.location)
        ob.location = (loc[0],0,0)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, properties=True)
        ob.location = (0,loc[1],loc[2])

def reset_cursor_rot():
    bpy.context.scene.cursor.rotation_euler = (0,0,0)