import hou
import _alembic_hom_extensions as abc
import re

class ForceTest:

    def __init__(self):
        pass

    def set_mantra_for_preview(self):
        pass

    def set_mantra_for_comp(self):
        abc_path = '/mnt/project/hook/pepper/shots/sq01/0010/layout_camera/output/camera_cache/v005/pepper_sq01_0010_camera_cache_v005.abc'
        abc_range = abc.alembicTimeRange(abc_path)
        path = '/mnt/project/hook/pepper/shots/sq01/0010/fx/working/v098/pepper_sq01_0010_fx_098.hipnc'
        saved_path = '/home/rapa/yh/test/save/test.hipnc'
        hou.hipFile.load(path)
        root = hou.node('/out')
        obj_root = hou.node('/obj')
        fx_check = re.compile('^fx_(\w+)')
        for child in obj_root.children():
            check = fx_check.search(str(child))
            if check:
                break

        fx_name = 'fx_'+check.group(1)
        bg_name = []

        for child in obj_root.children():
            if str(child) != fx_name:
                bg_name.append(str(child))

        result = ' '.join(s for s in bg_name)

        print(result)

        if root is not None:
            mantra_preview = root.createNode('ifd')
            mantra_preview.parm('camera').set('obj/cam1Camera/')
            mantra_preview.parm('vm_picture').set('/home/rapa/yh/test/jpg/test_$F4.jpg')
            mantra_preview.parm('trange').set(1)
            for i in mantra_preview.parmTuple('f'):
                i.deleteAllKeyframes()
            mantra_preview.parmTuple('f').set([abc_range[0] * hou.fps(), abc_range[1] * hou.fps(), 1])
            mantra_preview.parm('vm_verbose').set(1)

            mantra_comp = root.createNode('ifd')
            mantra_comp.parm('vobject').set('')
            mantra_comp.parm('forceobject').set(result)
            mantra_comp.parm('camera').set('obj/cam1Camera/')
            mantra_comp.parm('vm_picture').set('/home/rapa/yh/test/exr/test_$F4.exr')
            for i in mantra_comp.parmTuple('f'):
                i.deleteAllKeyframes()
            mantra_comp.parmTuple('f').set([abc_range[0] * hou.fps(), abc_range[1] * hou.fps(), 1])
            mantra_comp.parm('vm_verbose').set(1)
            hou.hipFile.save(file_name=saved_path)

def main():
    aaa = ForceTest()
    aaa.set_mantra_for_comp()


if __name__ == "__main__":
    main()