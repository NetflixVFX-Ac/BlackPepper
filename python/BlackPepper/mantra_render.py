import hou
import _alembic_hom_extensions as abc
import os
import shutil
import glob
import sys

def set_mantra_for_render(hip_path, output_path, abc_path, cam_node):
    """



    Args:
        hip_path:
        output_path:
        abc_path:
        cam_node:

    Returns:

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
    if root is not None:
        n = root.createNode('ifd')
        n.parm('camera').set(cam_setting)
        n.parm('vm_picture').set(f'{output_path[:-8]}$F4.jpg')
        n.parm('trange').set(1)
        for i in n.parmTuple('f'):
            i.deleteAllKeyframes()
        n.parmTuple('f').set([abc_range[0] * hou.fps(), abc_range[1] * hou.fps(), 1])
        n.parm('vm_verbose').set(1)
        n.parm("execute").pressButton()
    output_dir = os.path.dirname(output_path) + '/*.jpg'
    error_dir = os.path.dirname(output_path) + '/*.jpg.mantra_checkpoint'
    file_list = glob.glob(output_dir)
    error_list = glob.glob(error_dir)
    if len(file_list) == abc_range[1] * hou.fps():
        if len(error_list) == 0:
            shutil.rmtree(home_path + '/temp')
        else:
            print("render error")
    else:
        print("missing sequence frame")

def main():
    args = sys.argv
    if len(args) != 5:
        print('Insufficient arguments')
        sys.exit()

    hip_path = args[1]
    output_path = args[2]
    abc_path = args[3]
    cam_node = args[4]
    set_mantra_for_render(hip_path, output_path, abc_path, cam_node)

if __name__ == "__main__":
    main()