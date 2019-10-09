import bpy
import math
from mathutils import Matrix

from bpy.types import ( PropertyGroup , Panel)
from bpy.props import(
    PointerProperty,
    IntProperty,
    BoolProperty,
    StringProperty,
    CollectionProperty
    )

import imp

from . import utils
imp.reload(utils)

    
class KIATOOLS_Props_OA(bpy.types.PropertyGroup):
    #アプライオプション
    deleteparticle_apply : BoolProperty(name="delete particle" ,  default = False)
    keephair_apply : BoolProperty(name="keep hair" ,  default = False)
    keeparmature_apply : BoolProperty(name="keep armature" ,  default = False)
    merge_apply : BoolProperty(name="merge" ,  default = True)

    #シーン名
    prop : StringProperty(name="Scene", maxlen=63 )
    allscene : CollectionProperty(type=PropertyGroup)

    #アプライ先シーン
    applyscene : StringProperty(name="target:", maxlen=63 )


#ロケータに親子付けする
#ロケータを作成してペアレント。ロケータがすでに存在していれば作成しない
def parent_empty(current_scene_name , result):

    new_name = current_scene_name + '_parent'

    if bpy.data.objects.get(new_name) is not None:
        empty = utils.objectByName(new_name)

    else:
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        empty = utils.getActiveObj()
        empty.name = new_name
        empty.matrix_world = Matrix()

    for obj in result:
        obj.parent = empty


#パブリッシュ時にコレクションにまとめる
#orgのモデルがコレクションに属していれば、そのコレクションも複製
def put_into_collection(current_scene_name , result ,scn):
    new_name = current_scene_name + '_collection'

    #コレクションが存在していればそのまま使用、なければ新規作成
    if new_name in bpy.context.scene.collection.children.keys():
        col = scn.collection.children[new_name]

    else:
        col = bpy.data.collections.new(new_name)
        scn.collection.children.link(col)

    for dat in result:

        #所属していたコレクションがマスターでないなら
        #コレクション名 + 'Applied' というコレクションに移動

        if dat.colname != 'Master Collection':
            new_name = dat.colname + '_Applied'

            if new_name in col.children.keys():
                col2 = col.children[new_name]

            else:
                col2 = bpy.data.collections.new(new_name)
                col.children.link(col2)

            col2.objects.link(dat.obj)
        else:
            col.objects.link(dat.obj)

#髪の毛のコンバート
# #複数のヘアパーティクルがあることを想定
def convert_hair(hairarray, new_name , ob):

    new_obj_array = []
    for num,hairname in enumerate(hairarray):
        utils.activeObj(ob)
        utils.select(ob,True)
        #コンバートするとメッシュオブジェクトが作られてそれがアクティブな状態になっている
        print(hairname)
        bpy.ops.object.modifier_convert(modifier = hairname)

        bpy.ops.object.convert(target='CURVE')
        new_obj = bpy.context.active_object

        new_obj_array.append(new_obj)

        #マスターコレクションを選択した状態で実行するとここでエラーがでる。不便そうなら解決策を考える
        # utils.sceneLink(new_obj)
        bpy.ops.object.move_to_collection(collection_index = 0)
        new_obj.name = '%s_%02d' % (new_name,num)


        #カーブのサークルを作成してベベルに使用する
        #サークルカーブは終わったら削除
        #カーブにUVを設定することであとの調整を容易にする
        bpy.ops.curve.primitive_bezier_circle_add()
        circleobj = bpy.context.active_object
        circleobj.scale = (0.01,0.01,0.01)                    
        circleobj.data.resolution_u = 1 #<<<<<元は６。あとで数値入力できるように調整

        bpy.ops.object.move_to_collection(collection_index = 0)

        #テーパー用オブジェクト
        bpy.ops.curve.primitive_bezier_curve_add()
        taperobj = bpy.context.active_object
        taperobj.data.resolution_u = 6 #<<<<<元は６。あとで数値入力できるように調整

        bpy.ops.object.move_to_collection(collection_index = 0)


        new_obj.data.bevel_object = circleobj
        new_obj.data.taper_object = taperobj
        new_obj.data.use_uv_as_generated = True
        new_obj.data.resolution_u = 1


        utils.select(new_obj,True)
        utils.activeObj(new_obj)

        #髪の毛をメッシュ化しない場合はベベルとテーパーカーブをFixScnに送る
        if not bpy.context.scene.publishnotmesh_bool:
            #bpy.ops.object.convert(target = 'MESH')
            utils.select(new_obj,False)

            utils.select(circleobj,True)
            utils.select(taperobj,True)
            utils.activeObj(circleobj)

            bpy.ops.object.delete()

        else:
           new_obj_array.append(circleobj)
           new_obj_array.append(taperobj)
    
    return new_obj_array


def NewSceneName():
    num = bpy.context.scene.publishslot
    if num == 0:
        fix_scene = 'Fix_Scn'
    else:
        fix_scene = 'Fix%02d_Scn' % num

    return fix_scene


#現在のシーンをシーンメニューにセット
def set_current_scene():
    props = bpy.context.scene.kiatools_oa
    props.allscene.clear()        
    for scn in bpy.data.scenes:
        props.allscene.add().name = scn.name

    bpy.context.scene.kiatools_oa.prop = bpy.context.scene.name


class PublishedData:
    obj = None
    colname = ''
    mirror = False
    def __init__(self ,  obj , colname , mirror):
        self.obj = obj
        self.colname = colname
        self.mirror = mirror



class KIATOOLS_MT_object_applier(bpy.types.Operator):
    bl_idname = "kiatools.object_applier"
    bl_label = "Object Applier"

    def invoke(self, context, event):
        set_current_scene()        
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        return{'FINISHED'}


    def draw(self, context):
        #scn = context.scene
        props = bpy.context.scene.kiatools_oa
        layout=self.layout

        row = layout.row(align=False)
        box = row.box()
        box.prop_search(props, "prop", props, "allscene", icon='SCENE_DATA')

        row = box.row()
        row.operator("kiatools.change_scene", icon = 'FILE_IMAGE')
        row.operator("kiatools.move_model" , icon = 'DECORATE_DRIVER')

        box = layout.row(align=False).box()
        row = box.row()
        row.operator("kiatools.set_apply_scene", icon='TRACKING_FORWARDS')
        row.prop(props, "applyscene" , icon='APPEND_BLEND')

        row = box.row()
        row.operator("kiatools.apply_model")
        row.operator("kiatools.apply_particle_instance")


        row = layout.row(align=False)
        box = row.box()
        box.label(text = 'options')
        row = box.row()

        row = box.row()
        row.prop(props, "merge_apply")
        row.prop(props, "deleteparticle_apply")

        row = box.row()
        row.prop(props, "keeparmature_apply")
        row.prop(props, "keephair_apply")


#リストから選択したシーンに移動
class KIATOOLS_OT_change_scene(bpy.types.Operator):
    """選択したシーンに移動する"""
    bl_idname = "kiatools.change_scene"
    bl_label = "go to scene"

    def execute(self, context):        
        scene = bpy.context.scene.kiatools_oa.prop
        bpy.context.window.scene = bpy.data.scenes[scene]
        set_current_scene()
        #bpy.context.scene.kiatools_oa.prop = bpy.context.scene.name
        return {'FINISHED'}


#アプライするシーンを指定する
class KIATOOLS_OT_set_apply_scene(bpy.types.Operator):
    """アプライするシーンを指定する"""
    bl_idname = "kiatools.set_apply_scene"
    bl_label = "target scene"

    def execute(self, context):        
        bpy.context.scene.kiatools_oa.applyscene= bpy.context.scene.kiatools_oa.prop
        return {'FINISHED'}



#選択モデルをリスト選択されたシーンに移動
class KIATOOLS_OT_move_model(bpy.types.Operator):
    """選択したモデルをリスト選択されたシーンに移動する"""
    bl_idname = "kiatools.move_model"
    bl_label = "move model"

    def execute(self, context):
        current = bpy.context.window.scene.name
        scene = bpy.context.scene.kiatools_oa.prop

        result = []
        for ob in utils.selected():
            col = ob.users_collection[0]
            #col_name = ob.users_collection[0].name
            result.append(PublishedData(ob , col.name ,False))

            col.objects.unlink(ob)
            #utils.sceneUnlink(ob)
        
        put_into_collection(current , result ,bpy.data.scenes[scene])
        set_current_scene()

        # bpy.context.window.scene = bpy.data.scenes[scene]

        # for ob in utils.selected():
        #     utils.sceneLink(ob)


        # bpy.context.scene.kiatools_oa.prop = bpy.context.scene.name
        return {'FINISHED'}


# class KIATOOLS_OT_add_new_fixScn(bpy.types.Operator):
#     """新しいFixScnを生成する"""
#     bl_idname = "kiatools.add_new_fixscn"
#     bl_label = "FixScn追加"

#     def execute(self, context):
#         fix_scene = NewSceneName()
#         if bpy.data.scenes.get(fix_scene) is not None:
#             return {'FINISHED'}


#         #cur_scene = bpy.context.scene
#         #print("current Scene?: %s" % (cur_scene))
#         bpy.ops.scene.new(type='EMPTY')     
#         bpy.context.scene.name = fix_scene
#         #new_context = bpy.context.scene
#         #print("newScene?: %s" % (new_context))

#         return {'FINISHED'}


#モデル名に_orgをつけてそれを作業用のモデルとする。Fix_Scnというシーンにリンクする。
#ヘアーパーティクルも対象とする機能を追加
#木などパーティクルインスタンスがついているがアプライ時に削除したいときパーティクルモディファイヤを削除　

class KIATOOLS_OT_apply_model(bpy.types.Operator):
    """モデルのモディファイアフリーズ＞_orgを削除したモデルを複製＞選択シーンににリンク"""
    bl_idname = "kiatools.apply_model"
    bl_label = "apply model"

    def execute(self, context):

        props = bpy.context.scene.kiatools_oa
        merge = False


        if props.merge_apply:
            merge = True

        current_scene_name = bpy.context.scene.name

        #fix_scene = NewSceneName()
        fix_scene = bpy.context.scene.kiatools_oa.prop
        if bpy.data.scenes.get(fix_scene) is None:
            print(u'Not found Scene')
            return {'FINISHED'}


        #scn = bpy.context.scene
        sel = bpy.context.selected_objects
        #scene_obj = bpy.context.scene.objects
        objs = bpy.data.objects


        result = []
        for ob in sel:
            isOrg = False
            isMirror = False
            isHair = False

            name = ob.name
            col_name = ob.users_collection[0].name #現在所属しているコレクションを保持しておく

            #objの末尾に_orgがついていなければスルー
            if name[-3:] == 'org':
                new_name = name.replace('_org','')
                isOrg = True


            if name[-4:] == 'orgm':
                new_name = name.replace('_orgm','')
                isOrg = True
                isMirror = True

            if isOrg:
                utils.activeObj(ob)
                utils.select(ob,False)

                #既にモデルが存在していたら削除する
                if bpy.data.objects.get(new_name) is not None:
                    objs.remove(objs[new_name], do_unlink = True)
                    

                #ヘアーパーティクルの場合
                #パーティクル削除にチェックがあったら髪の毛として処理しない
                #複数のパーティクルがある場合に対応する必要あり

                hairarray = []
                for mod in ob.modifiers:
                    if mod.type == 'PARTICLE_SYSTEM':
                        if not props.deleteparticle_apply:#髪の毛として処理しない
                            hairarray.append(mod.name)
                            isHair = True
                print('---------------------------')
                print(hairarray)
                print('---------------------------')

                #髪の毛でなければオブジェクトをコピーする。
                #髪の毛ならパーティクルをコンバートする
                if isHair:
                    new_obj_array = convert_hair(hairarray, new_name , ob)
                    for new_obj in new_obj_array:
                        result.append(PublishedData(new_obj , col_name ,isMirror))

                
                #髪の毛でない場合
                else:
                    new_obj = ob.copy()
                    new_obj.data = ob.data.copy()
                    new_obj.animation_data_clear()

                    utils.sceneLink(new_obj)
                    new_obj.name = new_name

                    utils.select(new_obj,True)
                    utils.activeObj(new_obj)


                    result.append(PublishedData(new_obj , col_name ,isMirror))

        bpy.ops.object.select_all(action='DESELECT')


        for dat in result:
            utils.select(dat.obj,True)
            utils.activeObj(dat.obj)

            #カーブならメッシュ化する。前のループで実行するとなぜかorgモデルまでメッシュ化してしまう。なのでここで実行する。
            #髪の毛はここでメッシュ化される

            if dat.obj.type == 'CURVE':
                if not props.publishnotmesh_bool:
                    bpy.ops.object.convert(target = 'MESH')            

            #モディファイヤ適用
            for mod in dat.obj.modifiers:

                #アーマチュアをキープする
                if (mod.type == 'ARMATURE') and bpy.context.scene.publishkeeparmature_bool:
                    pass

                #モディファイヤが非表示なら削除する
                elif mod.show_viewport == False:
                    bpy.context.object.modifiers.remove(mod)
                else:
                    bpy.ops.object.modifier_apply(modifier=mod.name)



            #ミラーパブリッシュモード(この前のループで処理しようとするとエラーが出るのでここで実行)
            #if bpy.context.scene.publishmirror_bool:
            if dat.mirror:
                #親子付けを切る
                bpy.ops.object.parent_clear(type = 'CLEAR_KEEP_TRANSFORM')

                bpy.ops.object.transform_apply( location = True , rotation=True , scale=True )
                mod = dat.obj.modifiers.new( 'mirror' , type = 'MIRROR' )
                bpy.ops.object.modifier_apply(modifier=mod.name)            



        #シーンごとのコレクションにまとめるので下記は不要。
        # この行を有効にすると親のコレクションにも含まれてしまい2重に表示されてしまう。
        #bpy.ops.object.make_links_scene(scene = fix_scene)
        
        for dat in result:
            utils.sceneUnlink(dat.obj)

        #パブリッシュシーンをアクティブに
        scn = utils.sceneActive(fix_scene)

        #親子付けをする場合（現状はオミット）
        #parent_empty(current_scene_name , result)

        #コレクションにまとめる
        put_into_collection(current_scene_name , result , scn)

        #マージする
        if merge:
            utils.deselectAll()
            for dat in result:
                utils.select(dat.obj,True)


            utils.activeObj(result[0].obj)
            bpy.ops.object.join()
        

        return {'FINISHED'}


#パーティクルインスタンスのApply
class KIATOOLS_OT_apply_particle_instance(bpy.types.Operator):
    """パーティクルインスタンスを実体化して1つのモデルに集約"""
    bl_idname = "kiatools.apply_particle_instance"
    bl_label = "particle to model"

    def execute(self, context):
        scn = bpy.context.scene
        current_scene_name = bpy.context.scene.name

        fix_scene = NewSceneName()
        if bpy.data.scenes.get(fix_scene) is None:
            print(u'Not found Scene')
            return {'FINISHED'}

        sel = bpy.context.selected_objects
        objs = bpy.data.objects

        result = []
        for ob in sel:
            name = ob.name
            current_col = ob.users_collection[0] #現在所属しているコレクションを保持しておく
            col_name = current_col.name

            #一時的なコレクションを用意
            tmp_col_name = 'tmpcollection_apply_particleinstance'

            tmp_col = bpy.data.collections.new(tmp_col_name)
            scn.collection.children.link(tmp_col)

            tmp_col.objects.link(ob)
            current_col.objects.unlink(ob)

            utils.activeObj(ob)

            bpy.ops.object.duplicates_make_real()


            #オブジェクトの選択をクリア
            bpy.ops.object.select_all(action='DESELECT') 

            #選択されたコレクションにリンクされたオブジェクトを取得
            for ob0 in bpy.context.scene.objects: 
                if ob0.users_collection[0].name == tmp_col_name: 
                    utils.select(ob0,True)

            #自分自身は選択解除
            utils.select(ob,False)

            #空のメッシュオブジェクト作成
            mesh = bpy.data.meshes.new("mesh")  # add a new mesh
            empty_mesh = bpy.data.objects.new("Merged_Instance", mesh)  # add a new object using the mesh
            tmp_col.objects.link(empty_mesh)

            utils.select(empty_mesh,True)
            utils.activeObj(empty_mesh)


            #メッシュをマージ
            bpy.ops.object.join()

            #後片付け
            #元のモデルとマージされたオブジェクトをもとのコレクションにリンク
            # tempコレクションからアンリンク
            # tempコレクション削除：
            # for ob0 in ( ob , empty_mesh ):
            #     tmp_col.objects.unlink(ob0)
            #     current_col.objects.link(ob0)


            tmp_col.objects.unlink(ob)
            current_col.objects.link(ob)

            tmp_col.objects.unlink(empty_mesh)
            #current_col.objects.link(empty_mesh)



            bpy.data.collections.remove(tmp_col)

            result.append(PublishedData(empty_mesh , col_name,mirror))


        #パブリッシュシーンをアクティブに
        scn = utils.sceneActive(fix_scene)
        
        #コレクションにまとめる
        put_into_collection(current_scene_name , result , scn)

        return {'FINISHED'}


classes = (
    KIATOOLS_Props_OA,
    KIATOOLS_MT_object_applier,
    KIATOOLS_OT_apply_model,
    KIATOOLS_OT_apply_particle_instance,
    KIATOOLS_OT_change_scene,
    KIATOOLS_OT_move_model,
    KIATOOLS_OT_set_apply_scene
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.kiatools_oa = PointerProperty(type=KIATOOLS_Props_OA)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)