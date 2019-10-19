import bpy

#現在のシーンをシーンメニューにセット
def set_current():
    props = bpy.context.scene.kiatools_oa

    props.allscene.clear()
    props.target_allscene.clear()

    for scn in bpy.data.scenes:
        props.allscene.add().name = scn.name
        props.target_allscene.add().name = scn.name

    props.scene_name = bpy.context.scene.name

    # set_current_scene
    # scene.set_current