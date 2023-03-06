import hou
import gazu
import objecttoolutils
import os
import _alembic_hom_extensions as abc
import numpy as np

try:
    from hou import ui
except:
    ui = None

_AbcModule = __import__("_alembic_hom_extensions")

temp_hip = "/mnt/project/hook/BlackPepper/shots/sq01/0010/fx/working/v046/pepper_sq01_0010_fx_046.hipnc"

new_hip = "/home/rapa/test_21.hipnc"

hou.hipFile.load(temp_hip)

# n = hou.node("obj/geo1") #대문자 Node는 옆에 아이콘이 보이게 하는거다(class지 function은 아님).
# Parent (tree에있는 어떤것) 에 있는 노드에서 자식을 만드는 것이다.


# 씬 001의 있는 cam light여러 요소들을 불러와서 지금 여기 temp hip(템플릿) 에 적용하여 렌더

# obj = hou.node('/obj')
# geo = obj.createNode('geo')
# sphere = geo.createNode('sphere')
# box = geo.createNode('box')
# geo.setName('please')
# sphere.setName('sphere')
# obj.createNode('geo', 'wongyu')
out = hou.node('/out')
node = hou.pwd()


# def createCamera():
#     root = hou.node("/obj/")
#     if root != None:
#         n = root.createNode("cam")
#         n.parm("focal").set(35)


def createMantra():
    root = hou.node("/out")
    if root is not None:
        n = root.createNode("ifd")
        f1 = '$F4'
        s = f'/mnt/project/hook/BlackPepper/shots/sq01/0010/fx/output/my_filename_{f1}.jpg'
        archive_path = '/mnt/project/hook/pepper/shots/sq01/0010/layout/working/v001/pepper_sq01_0010_layout_001.abc'
        n.parm("camera").set("/obj/cam1Camera")
        n.parm("vm_picture").set(s)

        timerange = abc.alembicTimeRange(archive_path)
        # print(timerange[0]*hou.fps(), timerange[1]*hou.fps())
        # start_frame = timerange[0]*hou.fps()
        # end_frame = timerange[1]*hou.fps()
        n.parm("trange").set(1)
        n.parmTuple("f").set((timerange[0]*hou.fps(), timerange[1]*hou.fps(), 1))
        # n.parmTuple('f').set((timerange[0]*hou.fps(), timerange[1]*hou.fps(), 1))
        # n.parm("execute").pressButton()


createMantra()
# createCamera()

hou.hipFile.save(file_name=temp_hip)
