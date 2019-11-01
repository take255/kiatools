import bpy
import imp
import re

from . import utils
imp.reload(utils)


regex = re.compile('\d+')

#---------------------------------------------------------------------------------------
#連番でリネーム
#---------------------------------------------------------------------------------------
def continuous_renumber():
    props = bpy.context.scene.kiatools_oa
    num = props.rename_start_num

    for ob in utils.selected():
        ob.name = '%s_%02d' % ( props.rename_string , num )
        num += 1

#---------------------------------------------------------------------------------------
#最後に選択された名前から数字とそれ以外に分ける。
#数字のうち一番最後尾の要素を連番とする。
#数字は"_"で区切ったもの
#番号の最大数を検索してそれ以降から連番を始める。
#---------------------------------------------------------------------------------------


def by_rule():
    active = utils.getActiveObj()

    name = active.name
    buf = name.split('_')
    max = len(buf)-1

    decim_num = False
    for i,s in enumerate(buf):
        if s.isdecimal():
            decim_num = i

    newname = ''
    if decim_num != False:
        for i,s in enumerate(buf):
            if i == decim_num:
                newname += '%02d'
            else:
                newname += s

            if i < max:
                newname += '_'
            
    num = 1
    for ob in utils.selected():
        if ob != active:
            #オブジェクトが存在しないことを確認
            while (newname % num) in bpy.data.objects:
                num += 1
            print(newname % num)
            ob.name = newname % num
            num += 1
                #ob.name = newname % num    

def add(op):
    props = bpy.context.scene.kiatools_oa   
    for ob in utils.selected():
        currentname = ob.name
        if op == 'PREFIX':
            ob.name = '%s_%s' % ( props.rename_string , currentname )
        elif op == 'SUFFIX':
            ob.name = '%s_%s' % ( currentname , props.rename_string )

def replace():
    props = bpy.context.scene.kiatools_oa   
    for ob in utils.selected():
        ob.name = ob.name.replace(props.from_string, props.to_string)

def replace_defined(s):
    buf = s.split('>')
    for ob in utils.selected():
        ob.name = ob.name.replace('_' + buf[0] , '_' + buf[1] )


#maya仕様のリネーム：末尾の数字をshapeの後ろにくっつける
#ちょっとめんどくさいので作業あと回し
#数字を割り出して、最後の要素が末尾かどうがチェックする
def mesh(s):
    for ob in utils.selected():
        if s == 'object':
            ob.data.name = ob.name
        elif s == 'maya':
            num = regex.findall(ob.name)[-1]            
            ob.data.name = ob.name + 'Shape'

def add_defined(s):
    for ob in utils.selected():
        ob.name = ob.name + '_' + s


#セレクト：フィールドに入力した名前で選択
def select():
    props = bpy.context.scene.kiatools_oa

    matchobj = []
    utils.deselectAll()
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.context.scene.objects:
        if re.search(props.rename_string , ob.name) != None:
            matchobj.append(ob)

    utils.multiSelection(matchobj)

#アクティブオブジェクトの名前をピック
def dropper():
    props = bpy.context.scene.kiatools_oa
    props.rename_string = utils.getActiveObj().name
