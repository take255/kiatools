import bpy
from . import utils

#コンストレインが１つでもONならTrue
#muteがONなのが
def get_constraint_status():

    act = utils.getActiveObj()
    if act == None:
        return

    props = bpy.context.scene.kiatools_oa

    status = False
    for const in act.constraints:
        status = (status or const.mute)

    props.const_bool = status

# #所属しているコレクションの状態を取得
# def get_collection_status():

#     act = utils.getActiveObj()
#     if act == None:
#         return

#     props = bpy.context.scene.kiatools_oa

#     status = False
#     for col in act.users_collection:
#         print(col.name)

#     props.showhide_collection_bool = status



#ob　が　selectedの子供かどうか調べる。孫以降も調査。
def isParent(ob , selected):
    parent = ob.parent
    if parent == None:
        return False

    if parent in selected:
        return True
    else:
        isParent(parent , selected)

#選択したコンストレインの表示、非表示
#その際、選択オブジェクトにフォーカスする
def tgl_constraint(self,context):
    props = bpy.context.scene.kiatools_oa
    selected = utils.selected()
    act = utils.getActiveObj()

    for ob in selected:
        utils.activeObj(ob)
        for const in ob.constraints:
            const.mute = props.const_bool

            #muteオンオフだけではコンストレインがアップデートされない問題
            #この行の追加で解消
            const.influence = 1.0 


    #表示されているならセレクトする    
    for ob in bpy.data.objects: 
        if ob.parent in selected: 
            if bpy.data.objects[ob.name].visible_get():
                utils.select(ob,True)
            #children.append(ob) 
        
    bpy.ops.view3d.view_selected(use_all_regions = False)

    #utils.deselectAll()
    utils.multiSelection(selected)
    utils.activeObj(act)


#ＯＮで現在の表示状態を保持しておき選択モデルと子供だけ表示、ＯＦＦでもとに戻す
def tgl_child(self,context):
    props = bpy.context.scene.kiatools_oa    
    selected = utils.selected()

    #選択以外をハイド
    if props.showhide_bool:
        props.displayed_allobjs.clear()
        #すべてのオブジェクトの表示状態を保持して、選択状態でなければハイドする
        for ob in bpy.data.objects:
            if bpy.data.objects[ob.name].visible_get():
                props.displayed_allobjs.add().name = ob.name

                if not ob in selected: 
                    if not isParent(ob , selected): 
                        ob.hide_viewport = True
                    else:
                        utils.select(ob,True)
                
    
    #表示をもとに戻す
    else:
        for ob in props.displayed_allobjs:
            bpy.data.objects[ob.name].hide_viewport = False
            #utils.select(ob,True)

        if not ob in selected: 
            if isParent(ob , selected): 
                utils.selectByName(ob,True)

    
    bpy.ops.view3d.view_selected(use_all_regions = False)
    utils.deselectAll()
    utils.multiSelection(selected)


#すべてのコレクションを調べて、表示状態ならリストに追加する
def tgl_collection(self,context):

    act = utils.getActiveObj()
    if act == None:
        return

    props = bpy.context.scene.kiatools_oa

    #選択されているオブジェクトのコレクション名    
    colname_selected = [x.name for x in act.users_collection]
    print(props.showhide_collection_bool)


    cols = [x.name for x in props.displayed_allcollections]

    #選択以外をハイド
    print(colname_selected)
    if not props.showhide_collection_bool:
        for col in bpy.context.window.view_layer.layer_collection.children:
            if not col.name in colname_selected:
                col.exclude = True

                
    #表示をもとに戻す
    else:
        print('vvvv------------------------------------------------------------')
        for col in bpy.context.window.view_layer.layer_collection.children:
            col.exclude = False
        print(cols)
        for col in bpy.context.scene.collection.children:
            print(col.name ,  col.name in cols)
            if not col.name in cols:
                bpy.context.window.view_layer.layer_collection.children[col.name].exclude = True
