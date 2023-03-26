import sys
import os
import shutil
import glob
import re
import hou
import _alembic_hom_extensions as abc


def set_mantra_fx_for_comp(hip_path, output_path, abc_path, cam_node):
    """Houdini python module _alembic_hom_extensions를 활용하여 Alembic file에서 Camera frame range를 가져온다. \n
    shot FX working file path를 argument로 받아, shutil를 활용하여 홈 경로에 새로만든 temp directory에 복사한다. \n
    Houdini python module Hou를 활용하여 복사한 Houdini file을 실행시키고, out에 Mantra 노드를 생성하여 render를 시작한다. \n
    Alembic file camera에서 가져온 frame in/out을 render frame range로 갖고 argument로 저장경로를 설정한다. \n
    mantra parameter인 vm_verbose를 활용하여 터미널 내, render 과정을 출력시킨다. \n
    render가 끝나면, output 경로에 출력하고자 했던 frame out count와 비교하고 render가 진행 중이면 생성되는 \n
    checkpoint 확장자가 있는지 체크하고 문제 없을 시, 홈 경로에 생성한 temp directory를 제거한다.

    Args:
        hip_path: shot fx working file path
        output_path: shot fx output file jpg_sequence path
        abc_path: shot layout_camera output file path
        cam_node: Alembic file cam node
    """
    abc_range = abc.alembicTimeRange(abc_path)
    cam_setting = f'/obj/{cam_node}/'
    basename = os.path.basename(hip_path)
    home_path = os.path.expanduser('~')
    temp_path = os.path.join(home_path + '/temp', basename)
    if not os.path.isdir(home_path + '/temp'):
        os.makedirs(home_path + '/temp')
    shutil.copyfile(hip_path, temp_path)
    hou.hipFile.load(temp_path)
    root = hou.node('/out')
    obj_root = hou.node('/obj')
    fx_check = re.compile('^(fx_\w+)')
    for child in obj_root.children():
        check = fx_check.search(str(child))
        if check:
            break

    fx_name = check.group(1)

    if root is not None:
        mantra_comp = root.createNode('ifd')
        mantra_comp.parm('vobject').set('')
        mantra_comp.parm('forceobject').set(fx_name)
        mantra_comp.parm('camera').set(cam_setting)
        mantra_comp.parm('vm_picture').set(f'{output_path}_$F4.exr')
        mantra_comp.parm('trange').set(1)
        for i in mantra_comp.parmTuple('f'):
            i.deleteAllKeyframes()
        # mantra_comp.parmTuple('f').set([abc_range[0] * hou.fps(), abc_range[1] * hou.fps(), 1])
        mantra_comp.parmTuple('f').set([abc_range[0] * hou.fps(), 1, 1])
        mantra_comp.parm('vm_verbose').set(1)
        mantra_comp.parm("execute").pressButton()
    output_dir = os.path.dirname(output_path) + '/*.exr'
    error_dir = os.path.dirname(output_path) + '/*.exr.mantra_checkpoint'
    file_list = glob.glob(output_dir)
    error_list = glob.glob(error_dir)
    if len(file_list) == abc_range[1] * hou.fps():
        if len(error_list) == 0:
            shutil.rmtree(home_path + '/temp')
        else:
            print("exr.mantra_checkpoint exists")
    else:
        print("missing sequence frame")

    hou.hipFile.save('/home/rapa/yh/test/save/test_yh.hipnc')


def main():
    """Terminal에 실행할 command로 활용하기 위해 만들었으며, \n
    set_mantra_for_render()에 필요한 인자값을 python 실행시, argument로 받도록 한다.
    argument 개수에 부합한 값이 들어올 경우 Insufficient arguments를 출력한다.
    """
    args = sys.argv
    if len(args) != 5:
        print('Insufficient arguments')
        sys.exit()

    hip_path = args[1]
    output_path = args[2]
    abc_path = args[3]
    cam_node = args[4]
    set_mantra_fx_for_comp(hip_path, output_path, abc_path, cam_node)


if __name__ == "__main__":
    main()

