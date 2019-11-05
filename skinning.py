import bpy
import imp
import re

from . import utils
imp.reload(utils)

#選択したモデルのアーマチュアモディファイヤを全面に出す
def bone_xray(self,context):
    for ob in utils.selected():
        print(ob.name)
        for m in ob.modifiers:
            if m.type == 'ARMATURE':
                amt = m.object
                print(amt)
                #ob.show_x_ray = not ob.show_x_ray
                amt.show_in_front = not amt.show_in_front


##スキンバインド
def bind():
    selected = utils.selected()

    obArray = []
    for ob in selected:
        if ob.type == 'ARMATURE':
            amt = ob

    for ob in selected:
        if ob != amt:
            obArray.append(ob)
            utils.activeObj(ob)
            m = ob.modifiers.new("Armature", type='ARMATURE')
            m.object = amt

    #頂点グループ追加
    for ob in obArray:
        utils.activeObj(amt)
        utils.mode_e()

        for b in amt.data.edit_bones:
            ob.vertex_groups.new(name = b.name)

    utils.mode_e()

    return {'FINISHED'}


# class Add_Vertex_Group(bpy.types.Operator):
#     """スキニングされたオブジェクトに全ボーンの頂点グループを追加する"""
#     bl_idname = "object.add_vertex_group"
#     bl_label = "頂点グループ追加"

#     def execute(self, context):
#         sel = bpy.context.selected_objects
#         scene_obj = bpy.context.scene.objects

#         for ob in sel:
#             for i, mod in enumerate(ob.modifiers):

#                 if mod.type == 'ARMATURE':
#                     print(mod.object.name)
#                     amt = mod.object
#                     scene_obj.active = amt
#                     bpy.ops.object.mode_set(mode='EDIT')

#                     for b in amt.data.edit_bones:
#                         ob.vertex_groups.new(name = b.name)
#         return {'FINISHED'}



def asssign_maxweight():
    selected = bpy.context.selected_objects
    obj = selected[1]

    result =[]
    for bone in bpy.context.selected_bones:
        print( bone.name )
        result.append(bone.name)


    bpy.ops.object.mode_set(mode = 'OBJECT')        
    objects = bpy.context.scene.objects

    #アーマチュアをエディットモードのままにしておくと選択がおかしくなるのでいったん全選択解除       
    bpy.ops.object.select_all(action='DESELECT')

    for obj in selected:
        if obj.type != 'ARMATURE':

            #選択モデルをアクティブに
            objects.active =obj

            msh = obj.data
            vtxCount = len(msh.vertices)#頂点数

            #頂点数でループ
            #一致するバーテックスグループの名前を検索し、100%ウェイトを与える。
            for i in range(vtxCount):
                for group in obj.vertex_groups:
                    if group.name  in result:
                        group.add( [i], 1.0, 'REPLACE' )



def add_influence_bone():
    selected = utils.selected()
    obj = selected[1]

    result =[]
    for bone in utils.get_selected_bones():
        print( bone.name )
        result.append( bone.name )

    utils.mode_o()
    utils.deselectAll()

    for obj in selected:
        if obj.type != 'ARMATURE':

            utils.activeObj(obj)    
            msh = obj.data

            #頂点グループを追加
            for group in result:
                bpy.context.object.vertex_groups.new(name = group)




#アーマチュア以外のモディファイヤをapply
def apply_not_armature_modifiers():
    sel = bpy.context.selected_objects
    scene_obj = bpy.context.scene.objects
    for ob in sel:
        scene_obj.active = ob

        for i, mod in enumerate(ob.modifiers):
            if mod.type != 'ARMATURE':
                print(mod.name)
                bpy.ops.object.modifier_apply(modifier=mod.name)



def delete_all_vtxgrp():
    obj = bpy.context.object
    me = obj.data
    result = []
    for group in obj.vertex_groups:
        bpy.context.object.vertex_groups.remove(group)



def delete_notexist_vtxgrp():
    sel = bpy.context.selected_objects
    scene_obj = bpy.context.scene.objects
    for obj in sel:
        boneset = set()
        for i, mod in enumerate(obj.modifiers):
            #bonearra y = []
            if mod.type == 'ARMATURE':
                #print(mod.object.name)
                amt = mod.object
                #scene_obj.active = amt
                Utils.activeObj(amt)
                bpy.ops.object.mode_set(mode='EDIT')

                #アーマチュア内の骨をリストアップしてセットに格納
                for b in amt.data.edit_bones:
                    boneset.add(b.name)

        #頂点グループを走査してボーンのセットに含まれているかどうか調査
        bpy.ops.object.mode_set(mode='OBJECT')
        #scene_obj.active = obj
        Utils.activeObj(obj)
        for group in obj.vertex_groups:
            if (group.name in boneset) == False:
                bpy.context.object.vertex_groups.remove(group)
    return {'FINISHED'}

    result = []
    #jntが含まれていなければ削除対象
    for group in obj.vertex_groups:
        if group.name.find("jnt") == -1:
            result.append(group)

    for group in result:
        print(group.name)
        bpy.context.object.vertex_groups.remove(group)



def delete_by_word():
    props = bpy.context.scene.kiatools_oa
    name = props.vertexgrp_string

    obj = bpy.context.object
    me = obj.data
    result = []
    #jntが含まれていなければ削除対象
    for group in obj.vertex_groups:
        if group.name.find(name) == -1:
            result.append(group)

    for group in result:
        print(group.name)
        bpy.context.object.vertex_groups.remove(group)


def delete_allweights():
    obj=bpy.context.active_object

    boneArray = []
    for group in obj.vertex_groups:
        boneArray.append(group.name)

    #頂点の情報
    msh = obj.data
    vtxCount = str(len(msh.vertices))#頂点数
    for v in msh.vertices:
        for vge in v.groups:
            vge.weight = 0


def delete_unselectedweights():
    selected = bpy.context.selected_objects
    print( selected[1].name)
    result =set()


    #選択されたボーンを取得
    for bone in bpy.context.selected_bones:
        print( bone.name)
        result.add(bone.name)
    
    bpy.ops.object.mode_set(mode = 'OBJECT')

    objects = bpy.context.scene.objects

    #アーマチュアをエディットモードのままにしておくと選択がおかしくなるのでいったん全選択解除
    bpy.ops.object.select_all(action='DESELECT')


    # objArray = []
    for obj in selected:
        if obj.type != 'ARMATURE':
            #選択モデルをアクティブに
            objects.active =obj
    
            msh = obj.data
            vtxCount = len(msh.vertices)#頂点数

            #頂点数でループ
            for i in range(vtxCount):
                for group in obj.vertex_groups:
                    if group.name not in result:
                        group.add( [i], 0, 'REPLACE' )

            obj.select = True



#---------------------------------------------------------------------------------------
#ウェイトの転送
#---------------------------------------------------------------------------------------
def weights_transfer():
    bpy.ops.object.data_transfer(
        use_create=True,
        vert_mapping='NEAREST',
        data_type='VGROUP_WEIGHTS',
        layers_select_src='ALL',
        layers_select_dst='NAME',
        mix_mode='REPLACE')

#---------------------------------------------------------------------------------------
#ウェイトのミラー
#---------------------------------------------------------------------------------------
SMALL = 0.01
signR = 'R_'
signL = 'L_'

def nameFlip(name):
    strlen=len(name)
    if(strlen<1):
        return name
    #last=name[strlen-1]
    #名前に.Lか.Rが含まれているかどうか
##		if(last=='R'):
##			return name[0:strlen-1]+'L'
##		if(last=='L'):
##			return name[0:strlen-1]+'R'
    if(name.find(signR) != -1):
        return name.replace(signR,signL)
    if(name.find(signL) != -1):
        return name.replace(signL,signR)

    return name

def calDistance(v1,v2):
    vx=v1.x-v2.x
    vy=v1.y-v2.y
    vz=v1.z-v2.z
    return math.sqrt(vx*vx+vy*vy+vz*vz)

def getTgt(v,array):
    vcp=v.co.copy()
    vcp.x*=-1
    array.remove(v)
    ret=None
    for tv in array:
        dist=calDistance(vcp,tv.co)
        if(dist<SMALL):
            ret=tv
            array.remove(tv)
            break
    return ret

def weights_mirror(self):
    index2name={}
    nameflip={}

    obj=bpy.context.active_object
    if(obj.type!='MESH'):
        return

    mesh=obj.data
    for vg in obj.vertex_groups:
        index2name[vg.index]=vg.name
        nameflip[vg.name] = nameFlip(vg.name)
        targets=mesh.vertices.values()
    for v in mesh.vertices:
        if(v.co.x>SMALL):
            tgt = getTgt(v,targets)
            if(tgt==None):
                print("no")
                continue
            for vg in obj.vertex_groups:
                vg.remove([tgt.index])
            vgs=v.groups
            for vge in vgs:
                tvg=obj.vertex_groups[nameflip[index2name[vge.group]]]
                tvg.add([tgt.index],vge.weight,'REPLACE')