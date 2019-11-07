import bpy , bmesh
import imp

from . import utils
imp.reload(utils)

VERTEX_COLOR = {
'METAL'  :("ff0000","00ffff","993333","339982","ff9999","99ffe9","ffdb99","e4e54c"),
'LEATHER':("fff900","0000ff","999933","333399","ffff99","99bcff","062d0c","ffa500"),
'CLOTH'  :("00ff00","ff00ff","339943","753399","ff6600","db99ff","0d0d59","ec008c"),
'OTHER'  :("590d29","56493d","798ba8","b58f7b","32590d","3e0d59","41410d","af4ce5"),
}

def conv(v):
    return float(int(v,16))/255

def color_vertex(ob, vert, color):
    utils.act(ob)
    mesh = ob.data 

    if mesh.vertex_colors:
        vcol_layer = mesh.vertex_colors.active
    else:
        vcol_layer = mesh.vertex_colors.new()

    for poly in mesh.polygons:
        for loop_index in poly.loop_indices:
            vcol_layer.data[loop_index].color = color



#---------------------------------------------------------------------------------------
#頂点カラーをアサイン
#---------------------------------------------------------------------------------------
def assign_vertex_color():

    props = bpy.context.scene.kiatools_oa
    index = props.material_index

    a = VERTEX_COLOR[ props.material_type ][ index ]
    color = [conv(a[:2]) , conv(a[2:4]) , conv(a[4:]) , 1.0]

    for ob in utils.selected():
        color_vertex(ob, 2, color)

                
#---------------------------------------------------------------------------------------    
#モデルのマテリアルカラーを取得。
#シェーダーはPrincipled BSDFである必要がある。
#---------------------------------------------------------------------------------------
def convert_vertex_color():
    print('asss')
    for ob in utils.selected():
        for mat in ob.data.materials:
            nodes = mat.node_tree.nodes
            Node = nodes.get("Principled BSDF")
            color = Node.inputs["Base Color"].default_value[:]
            print(color)
            color_vertex(ob, 2, color)


