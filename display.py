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
    
    for ob in selected:
        for col in ob.users_collection:
            col.hide_viewport = True


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
#コレクションインスタンスから元のコレクションを選択する
#カレントにコレクションがあるかどうか調べ、なければ別のシーンを検索する
#---------------------------------------------------------------------------------------
def select_instance_collection():
    act = utils.getActiveObj()
    col = act.instance_collection

    utils.deselectAll()

    exist = False
    #カレントシーンにコレクションがあるかどうか調べる
    current_scn = bpy.context.window.scene
    exist = select_instance_collection_loop( col , current_scn.collection ,exist)

    print(exist)
    
    #コレクションが見つからない場合、別のシーンを走査
    #見つかったら、シーンをアクティブにしてビューレイヤを表示状態にする
    if not exist:
        for scn in bpy.data.scenes:
            if current_scn != scn:
                exist = select_instance_collection_loop( col , scn.collection ,exist)
                print(scn.name , scn.collection.name,exist)

                if exist:
                    utils.sceneActive(scn.name)
                    layer = bpy.context.window.view_layer.layer_collection
                    show_collection_by_name( layer , col.name)
                    break
    
    utils.deselectAll()                        
    for ob in bpy.data.collections[col.name].objects:
        utils.select(ob,True)
        utils.activeObj(ob)


#---------------------------------------------------------------------------------------
#ビューレイヤーを再帰的に調べて表示状態にする
#---------------------------------------------------------------------------------------
def select_instance_collection_loop( col ,current ,exist):
    props = bpy.context.scene.kiatools_oa
    children = current.children

    if children != None:
        for c in children:
            if col.name == c.name:
                exist = True

            exist = select_instance_collection_loop(col ,c, exist)

    return exist


#---------------------------------------------------------------------------------------
#ビューレイヤーを名前で表示状態切替
#---------------------------------------------------------------------------------------
def show_collection_by_name(layer ,name):
    props = bpy.context.scene.kiatools_oa
    children = layer.children

    if children != None:
        for ly in children:
            if name == ly.name:
                ly.hide_viewport = False                

            show_collection_by_name(ly , name)

