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

def color_vertex(ob, vert, color,mode):
    utils.act(ob)
    mesh = ob.data 

    if mesh.vertex_colors:
        vcol_layer = mesh.vertex_colors.active
    else:
        vcol_layer = mesh.vertex_colors.new()

    for poly in mesh.polygons:
        if mode == 0:
            for loop_index in poly.loop_indices:
                vcol_layer.data[loop_index].color = color
        elif mode == 1:
            if poly.select == True:
                for loop_index in poly.loop_indices:
                    print(loop_index)
                    vcol_layer.data[loop_index].color = color
            

#---------------------------------------------------------------------------------------
#頂点カラーをアサイン
#assign vertex color only selected vex
#---------------------------------------------------------------------------------------
def assign_vertex_color(mode):
    global VERTEXCOLOR_BUFFER
    props = bpy.context.scene.kiatools_oa
    index = props.material_index

    mat_type = props.material_type

    if mat_type == 'BUFFER':
        color = VERTEXCOLOR_BUFFER
    else:
        a = VERTEX_COLOR[ props.material_type ][ index ]
        color = [conv(a[:2]) , conv(a[2:4]) , conv(a[4:]) , 1.0]

    utils.mode_o()
    for ob in utils.selected():
        color_vertex(ob, 2, color , mode)

    utils.mode_e()

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

#---------------------------------------------------------------------------------------    
# First, select polugon face (not vertex) and execute this command.
#---------------------------------------------------------------------------------------    
VERTEXCOLOR_BUFFER = [0.0,0.0,0.0,1.0]
def pick_vertex_color(mode):
    global VERTEXCOLOR_BUFFER
    mesh = bpy.context.object.data
    utils.mode_o()

    vcol_layer = mesh.vertex_colors.active
    vtx_index = [loop_index for poly in mesh.polygons if poly.select for loop_index in poly.loop_indices]

    VERTEXCOLOR_BUFFER = vcol_layer.data[vtx_index[0]].color[0:4]
    #print(VERTEXCOLOR_BUFFER) 
    utils.mode_e()
