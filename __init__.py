import bpy
from bpy.types import Panel
from bpy.app.handlers import persistent
import imp

from . import utils
imp.reload(utils)

bl_info = {
"name": "kiatools",
"author": "kisekiakeshi",
"version": (0, 1),
"blender": (2, 80, 0),
"description": "kiatools",
"category": "Object"}


from . import object_applier
from . import modifier

imp.reload(object_applier)
imp.reload(modifier)


@persistent
def kiatools_handler(scene):
    pass


class KIAToolsPanel(utils.panel):   
    bl_label ='KIAtools'
    def draw(self, context):
        self.layout.operator("kiatools.object_applier", icon='BLENDER')
        self.layout.operator("kiatools.modifiertools", icon='BLENDER')


def register():
    bpy.utils.register_class(KIAToolsPanel)
    object_applier.register()
    modifier.register()
    bpy.app.handlers.depsgraph_update_pre.append(kiatools_handler)


def unregister():
    bpy.utils.unregister_class(KIAToolsPanel)
    object_applier.unregister()
    modifier.unregister()
    bpy.app.handlers.depsgraph_update_pre.remove(kiatools_handler)



 
