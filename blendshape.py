#import numpy as np
import bpy
import bmesh
from mathutils import ( Vector , Matrix , Quaternion )
import math
import imp

from . import utils
imp.reload(utils)


#クオータニオンにを回転角ウェイトをかける
#クオータニオンを返す
def quat_weight(q , weight):
    axis_angle = q.to_axis_angle()
    axis = axis_angle[0]
    angle = axis_angle[1] * weight #角度を出しウェイトを掛ける
    return Quaternion(axis , angle)


class Bone:
    quatanion = Quaternion()    
    parent_number = 0

    initmatrix = Matrix()
    matrix = Matrix()
    location = Vector()
    
    parent = ''

    def __init__(self , name):
        self.name = name

    #クオータニオンの回転をワールドに変換する
    def conv_quat_axis(self):
        axis_angle = self.quatanion.to_axis_angle()
        axis = axis_angle[0]
        angle = axis_angle[1]
        self.initmatrix
        axis_conv = self.initmatrix @ axis
        self.quatanion = Quaternion(axis_conv , angle)


class Vtx:
    """頂点出力のためのクラス"""

    co = ''
    #weight = []
    class Weight:
        """ウェイトの構造体"""
        value = 0
        name = ''


    def __init__(self):
        self.weight = []

    def getWeight(self,index,weight,boneArray):
        w = self.Weight()
        w.value = weight
        w.name =  boneArray[index]
        self.weight.append(w)


    def normalize_weight(self):
        sum = 0
        for w in self.weight:
            sum += w.value

        for w in self.weight:
            w.value = w.value/sum




  #親のクオータニオンにもウェイトを掛ける必要ある？
  #子供のほうから順にかけていかなければならない。結果がよくないのは親から順にかけられているから
    def calc_quat(self , val , BoneArray):
        #ウェイトをボーンの階層順にソートする。parent_numberを含むリストを作成して、それをキーにしてソート
        bonelist = []
        for w in self.weight:
            bonelist.append([ BoneArray[w.name].parent_number , w])

        bonelist.sort(key=lambda x:x[0])

        for w in reversed([ x[1] for x in bonelist ] ):
            parent = BoneArray[w.name].parent
            v = val - BoneArray[w.name].location #回転軸を原点以外に移動 位置にウェイトは掛けなくてよい

            q0 = quat_weight( BoneArray[ w.name ].quatanion , w.value ) #ボーンの逆クオータニオン
            q1 = quat_weight( BoneArray[ parent ].quatanion , w.value ) #親の逆クオータニオン
            
            #クオータニオンに戻し頂点座標にかける。位置をもとに戻す。最後に親の逆クオータニオンをかける。
            val =  q1 @ ( ( q0 @ v + BoneArray[w.name].location ) - BoneArray[parent].location ) + BoneArray[parent].location
        return  val


    def calc_mat(self , val , BoneArray):
        vec = Vector()
        for w in self.weight:
            #vec +=  BoneArray[BoneArray[w.name].parent].matrix @ BoneArray[w.name].matrix @ ( val - BoneArray[w.name].location ) * w.value  + BoneArray[w.name].location * w.value
            if w.name == 'Bone.001':
                #vec +=   BoneArray[BoneArray[w.name].parent].matrix @ ( BoneArray[w.name].matrix @ ( val - BoneArray[w.name].location ) * w.value  + BoneArray[w.name].location * w.value )
                vec +=   ( BoneArray[w.name].matrix @ ( val - BoneArray[w.name].location ) * w.value  + BoneArray[w.name].location * w.value )
            
            else:
                vec +=     ( val - BoneArray[w.name].location ) * w.value  + BoneArray[w.name].location * w.value 

        print(vec)
        return vec


    #ウェイト割合とマトリックスをかけて足していくことで初期姿勢に戻していく
    def calc_mat__(self , val , boneMatrixArray , initmatrixarray ,boneLocationArray):
        vec = Vector()
        for w in self.weight:
            vec +=  boneMatrixArray[w.name] @ ( val - boneLocationArray[w.name] ) * w.value  + boneLocationArray[w.name] * w.value

        return vec


    


#---------------------------------------------------------------------------------------
#ブレンドシェイプを元に姿勢に戻す
#ウェイトは振られた状態、アーマチュアモディファイヤはオフにしておく。姿勢はポーズを付けた状態にしておく
#現在の姿勢のインバースをかけて元の姿勢に戻す

#ワールドマトリクスなので親のマトリックスは必要なし
#初期マトリックスが必要
#インバートを掛けたあと初期マトリックスをかける

#ローカルのインバートを掛ける際、原点以外の軸を中心に変換する必要がある
#やり方は頂点座標(vector)からボーンポーズの座標をひく
#---------------------------------------------------------------------------------------


def invert():
    scn = bpy.context.scene.objects
    BoneArray = {}
    BoneArray['init'] = Bone('init')

    #アーマチャーを取得
    for obj in bpy.context.selected_objects:
        if obj.type == 'ARMATURE':
            amt = obj


    utils.activeObj(amt)

    for bone in amt.pose.bones:
        q = Quaternion(bone.rotation_quaternion)
        q.invert()

        BoneArray[bone.name] = Bone(bone.name)
        BoneArray[bone.name].quatanion = q

        m_world = Matrix(bone.matrix)
        BoneArray[bone.name].location = Vector((m_world[0][3] , m_world[1][3] , m_world[2][3]) )


        BoneArray[bone.name].parent_number = len(bone.parent_recursive)
        


        if bone.parent != None:
            BoneArray[bone.name].parent = bone.parent.name
        else:
            BoneArray[bone.name].parent = 'init'


    #初期マトリックス
    utils.mode_e()
    for bone in amt.data.edit_bones:
        BoneArray[bone.name].initmatrix = Matrix(bone.matrix).to_3x3()

    utils.mode_o()

    for b in BoneArray.values():
        b.conv_quat_axis()

    for obj in bpy.context.selected_objects:
        if obj.type != 'ARMATURE':
            mesh = obj.data        
            bm = bmesh.new()
            bm.from_mesh(mesh)

            boneArray = []
            for group in obj.vertex_groups:
                    boneArray.append(group.name)

            #ウェイト値を取得
            vtxarray = []
            for v in mesh.vertices:
                    vtx = Vtx()
                    for vge in v.groups:
                        if vge.weight > 0.00001:#ウェイト値０は除外
                            vtx.getWeight(vge.group, vge.weight ,boneArray) #boneArrayから骨名を割り出して格納
                    vtx.normalize_weight() #ウェイトをノーマライズする
                    vtxarray.append(vtx)


            #obj = bpy.context.object
            #シェイプのインデックス
            #shapekeysList = len(obj.data.shape_keys.key_blocks)
            spIndex = obj.active_shape_key_index

            print(spIndex)
            key = bm.verts.layers.shape.keys()[spIndex]

            val = bm.verts.layers.shape.get(key)
            #sk=mesh.shape_keys.key_blocks[key]

            for v,vtx in zip(bm.verts,vtxarray):
                delta = v[val] - v.co
                v[val] = vtx.calc_quat( v[val] , BoneArray)

            #ブレンドシェイプキーの操作
            # for key in bm.verts.layers.shape.keys():
            #     val = bm.verts.layers.shape.get(key)
            #     #print("%s = %s" % (key,val) )
            #     sk=mesh.shape_keys.key_blocks[key]
            #     #print("v=%f, f=%f" % ( sk.value, sk.frame))
            #     #print(vtxarray)

            #     for v,vtx in zip(bm.verts,vtxarray):
            #         delta = v[val] - v.co
            #         # if (delta.length > 0):
            #         #     print ( "v[%d]+%s" % ( i,delta) )
            #         #v[val] = vtx.calc_mat( v[val] , boneMatrixArray ,initmatrixarray ,boneLocationArray)
            #         v[val] = vtx.calc_quat( v[val] , BoneArray)
            #         #v[val] = m @ v[val]*0.5 + v[val] * 0.5

            bm.to_mesh(obj.data)






