import bpy
from . import utils

#---------------------------------------------------------------------------------------
#コンストレインが１つでもONならTrue
#muteがONなのが
#---------------------------------------------------------------------------------------
def get_constraint_status():

    act = utils.getActiveObj()
    if act == None:
        return

    props = bpy.context.scene.kiatools_oa

    status = False
    for const in act.constraints:
        status = (status or const.mute)

    props.const_bool = status


#---------------------------------------------------------------------------------------
#選択オブジェクトのコレクションをハイド
#---------------------------------------------------------------------------------------
def collection_hide():
    selected = utils.selected()
    layer = bpy.context.window.view_layer.layer_collection

    for ob in selected:
        for col in ob.users_collection:
            show_collection_by_name(layer ,col.name , True)
            #col.hide_viewport = True


#---------------------------------------------------------------------------------------
#ob　が　selectedの子供かどうか調べる。孫以降も調査。
#---------------------------------------------------------------------------------------
def isParent(ob , selected):
    parent = ob.parent
    if parent == None:
        return False

    if parent in selected:
        return True
    else:
        isParent(parent , selected)


#---------------------------------------------------------------------------------------
#選択したコンストレインの表示、非表示
#その際、選択オブジェクトにフォーカスする
#---------------------------------------------------------------------------------------
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
        
    if props.focus_bool:
        bpy.ops.view3d.view_selected(use_all_regions = False)

    #utils.deselectAll()
    utils.multiSelection(selected)
    utils.activeObj(act)


#---------------------------------------------------------------------------------------
#ＯＮで現在の表示状態を保持しておき選択モデルと子供だけ表示、ＯＦＦでもとに戻す
#---------------------------------------------------------------------------------------
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

    if props.focus_bool:
        bpy.ops.view3d.view_selected(use_all_regions = False)
    utils.deselectAll()
    utils.multiSelection(selected)


#---------------------------------------------------------------------------------------
#すべてのコレクションを調べて、表示状態ならリストに追加する
#tgl_collection_dic[子供] = [親名 , 親オブジェクト]
#---------------------------------------------------------------------------------------
tgl_collection_array = set()
tgl_collection_dic = {}

def tgl_collection(self,context):
    tgl_collection_array.clear()
    tgl_collection_dic.clear()

    act = utils.getActiveObj()
    if act == None:
        return

    props = bpy.context.scene.kiatools_oa

    #選択されているオブジェクトのコレクション名    
    colname_selected = [x.name for x in act.users_collection]
    cols = [x.name for x in props.displayed_allcollections]

    lc = bpy.context.window.view_layer.layer_collection

    #選択以外をハイド
    if not props.showhide_collection_bool:
        tgl_hide_collections_loop(lc ,colname_selected)

        for c in colname_selected:
            parent_name = c
            while parent_name != 'Master Collection':
                p = tgl_collection_dic[ parent_name ]
                parent_name = p[0]
                p[1].hide_viewport = False
                
    #表示をもとに戻す
    else:
        tgl_show_collections_loop(lc)


#---------------------------------------------------------------------------------------
#ビューレイヤーを再帰的に調べて非表示状態にする
#親レイヤを非表示にすると自分も見えなくなってしまうので、その処理が必要
#---------------------------------------------------------------------------------------
def tgl_hide_collections_loop(col , colname_selected):
    props = bpy.context.scene.kiatools_oa
    children = col.children

    if children != None:
        for c in children:
            tgl_collection_dic[c.name] = [ col.name , col ]
            if not c.name in colname_selected:
                c.hide_viewport = True
            else:
                tgl_collection_array.add(c.name)
            tgl_hide_collections_loop(c , colname_selected)



#---------------------------------------------------------------------------------------
#ビューレイヤーを再帰的に調べて表示状態にする
#---------------------------------------------------------------------------------------
def tgl_show_collections_loop(col):
    props = bpy.context.scene.kiatools_oa
    children = col.children

    
    if children != None:
        for c in children:
            if c.name in props.displayed_allcollections:
                c.hide_viewport = False
                #props.displayed_allcollections.add().name = c.name

            tgl_show_collections_loop(c)


#---------------------------------------------------------------------------------------
#ビューレイヤーを再帰的に調べて全部取得する
#ビューレイヤーとコレクションは別もので、目のアイコンはビューレイヤーのプロパティでコントロールする
#---------------------------------------------------------------------------------------
def preserve_collections_loop(col):
    props = bpy.context.scene.kiatools_oa
    children = col.children

    if children != None:
        for c in children:
            print(c.name,c.hide_viewport)
            if not c.hide_viewport:
                props.displayed_allcollections.add().name = c.name

            preserve_collections_loop(c)


#---------------------------------------------------------------------------------------
#すべてのコレクションをプロパティに登録
#---------------------------------------------------------------------------------------
def preserve_collections():
    props = bpy.context.scene.kiatools_oa
    props.displayed_allcollections.clear()

    preserve_collections_loop( bpy.context.window.view_layer.layer_collection )


#---------------------------------------------------------------------------------------
#ビューレイヤーを名前で表示状態切替
#---------------------------------------------------------------------------------------
def show_collection_by_name(layer ,name , state):
    props = bpy.context.scene.kiatools_oa
    children = layer.children

    if children != None:
        for ly in children:
            if name == ly.name:
                ly.hide_viewport = state                

            show_collection_by_name(ly , name , state)

