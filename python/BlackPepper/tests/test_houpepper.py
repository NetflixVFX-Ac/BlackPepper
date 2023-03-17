from unittest import TestCase
from BlackPepper.process.houpepper import HouPepper
from BlackPepper.pepper import Houpub
import hou
import _alembic_hom_extensions as abc
import os

class TestHouPepper(TestCase):
    def setUp(self):
        self.pepper = Houpub()
        self.pepper.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")
        self.hou_pepper = HouPepper()

    def test_abc_path(self):
        abc_path = '/mnt/project/hook/pepper/shots/sq01/0010/layout_camera/output/camera_cache/v005/pepper_sq01_0010_camera_cache_v005.abc'
        self.hou_pepper.abc_path = abc_path
        self.assertEqual(self.hou_pepper.abc_path, abc_path)

    def test_abc_tree_all(self):
        test_tree = "1"
        self.hou_pepper.abc_tree_all = test_tree
        self.assertEqual(self.hou_pepper.abc_tree_all, test_tree)

    def test_abc_tree_path(self):
        abc_path = '/mnt/project/hook/pepper/shots/sq01/0010/layout_camera/output/camera_cache/v005/pepper_sq01_0010_camera_cache_v005.abc'
        self.abc_tree_path = abc.alembicGetObjectPathListForMenu(abc_path)

    def test_abc_range(self):
        abc_path = '/mnt/project/hook/pepper/shots/sq01/0010/layout_camera/output/camera_cache/v005/pepper_sq01_0010_camera_cache_v005.abc'
        abc_range = abc.alembicTimeRange(abc_path)
        self.hou_pepper.abc_range = abc_range
        check = self.hou_pepper.abc_range
        self.assertEqual(check, (0.041666666666666664, 10.0))

    def test_set_abc_cam_tree(self):
        # 조건부
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'layout_camera'
        output_type_name = 'camera_cache'
        cam_path = self.pepper.output_file_path(output_type_name, task_type_name)
        # 실행부
        self.hou_pepper.set_abc_cam_tree(cam_path)
        abc_tree_all = self.hou_pepper.abc_tree_all

        self.hou_pepper.get_abc_cam_tree(abc_tree_all)
        # 검증부
        self.assertEqual(type(self.hou_pepper.abc_tree_all), tuple)
        self.assertEqual(type(self.hou_pepper.abc_tree_path), list)
        self.assertEqual(type(self.hou_pepper.abc_range), tuple)
        self.assertEqual(self.hou_pepper.abc_range[0] * hou.fps(), 1)
        self.assertEqual(self.hou_pepper.abc_range[1] * hou.fps(), 240)
        self.assertEqual(self.hou_pepper.abc_tree_all[0], 'ABC')
        self.assertEqual(self.hou_pepper.abc_tree_all,
                         ('ABC', 'unknown', (('cam1', 'xform', (('cam1Camera', 'camera', ()),)),)))
        # assert False

    def test_get_abc_cam_tree(self):
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'layout_camera'
        output_type_name = 'camera_cache'
        cam_path = self.pepper.output_file_path(output_type_name, task_type_name)
        self.hou_pepper.set_abc_cam_tree(cam_path)
        abc_tree_all = self.hou_pepper.abc_tree_all
        # abc_tree_all = ('ABC', 'unknown', (('cam1', 'xform', (('cam1Camera', 'camera', ()),)),))

        self.hou_pepper.get_abc_cam_tree(abc_tree_all)

        self.assertIsNotNone(self.hou_pepper.cam_list)
        self.assertIn('cam1Camera', self.hou_pepper.cam_list)

    def test_check_abc(self):
        abc_path = '/mnt/project/hook/pepper/shots/sq01/0010/layout_camera/output/camera_cache/v005/pepper_sq01_0010_camera_cache_v005.abc'
        file_name = abc_path
        self.assertEqual(file_name[-3:], 'abc')

    def test_set_cam_view(self):
        abc_path = '/mnt/project/hook/pepper/shots/sq01/0010/layout_camera/output/camera_cache/v005/pepper_sq01_0010_camera_cache_v005.abc'
        abc_range = abc.alembicTimeRange(abc_path)
        self.hou_pepper.set_abc_cam_tree(abc_path)
        cam = '/cam1/cam1Camera'

        self.hou_pepper.set_cam_view(cam)

        self.assertEqual(len(self.hou_pepper.filmaspectratio), abc_range[1]*hou.fps())
        self.assertEqual(len(self.hou_pepper.aperture), abc_range[1] * hou.fps())
        self.assertEqual(len(self.hou_pepper.aspect), abc_range[1] * hou.fps())
        self.assertEqual(len(self.hou_pepper.focal), abc_range[1] * hou.fps())
        self.assertEqual(len(self.hou_pepper.near), abc_range[1] * hou.fps())
        self.assertEqual(len(self.hou_pepper.far), abc_range[1] * hou.fps())
        self.assertEqual(len(self.hou_pepper.focus), abc_range[1] * hou.fps())
        self.assertEqual(len(self.hou_pepper.fstop), abc_range[1] * hou.fps())
        self.assertEqual(len(self.hou_pepper.shutter), abc_range[1] * hou.fps())
        self.assertEqual(len(self.hou_pepper.winx), abc_range[1] * hou.fps())
        self.assertEqual(len(self.hou_pepper.winy), abc_range[1] * hou.fps())
        self.assertEqual(len(self.hou_pepper.winsizex), abc_range[1] * hou.fps())
        self.assertEqual(len(self.hou_pepper.winsizey), abc_range[1] * hou.fps())

    def test_get_cam_resolution(self):
        abc_path = '/mnt/project/hook/pepper/shots/sq01/0010/layout_camera/output/camera_cache/v005/pepper_sq01_0010_camera_cache_v005.abc'
        self.hou_pepper.set_abc_cam_tree(abc_path)
        cam = '/cam1/cam1Camera'

        self.hou_pepper.get_cam_resolution(cam)

        self.assertEqual(self.hou_pepper.cam_resolution, [(1280.0, 720.0)])

    def test_get_cam_xform(self):
        abc_path = '/mnt/project/hook/pepper/shots/sq01/0010/layout_camera/output/camera_cache/v005/pepper_sq01_0010_camera_cache_v005.abc'
        abc_range = abc.alembicTimeRange(abc_path)
        self.hou_pepper.set_abc_cam_tree(abc_path)
        cam = '/cam1/cam1Camera'

        translate, rotate, scale = self.hou_pepper.get_cam_xform(cam)

        self.assertEqual(len(translate), abc_range[1] * hou.fps())
        self.assertEqual(len(rotate), abc_range[1] * hou.fps())
        self.assertEqual(len(scale), abc_range[1] * hou.fps())

    def test_set_cam_create(self):
        abc_path = '/mnt/project/hook/pepper/shots/sq01/0010/layout_camera/output/camera_cache/v005/pepper_sq01_0010_camera_cache_v005.abc'

        self.hou_pepper.set_cam_create(abc_path)

        self.assertEqual(self.hou_pepper.cam_path, ['/cam1/cam1Camera'])
        self.assertIsNotNone(self.hou_pepper.cam_node.parm('tx'))
        self.assertIsNotNone(self.hou_pepper.cam_node.parm('ty'))
        self.assertIsNotNone(self.hou_pepper.cam_node.parm('tz'))
        self.assertIsNotNone(self.hou_pepper.cam_node.parm('rx'))
        self.assertIsNotNone(self.hou_pepper.cam_node.parm('ry'))
        self.assertIsNotNone(self.hou_pepper.cam_node.parm('rz'))
        self.assertIsNotNone(self.hou_pepper.cam_node.parm('sx'))
        self.assertIsNotNone(self.hou_pepper.cam_node.parm('sy'))
        self.assertIsNotNone(self.hou_pepper.cam_node.parm('sz'))
        self.assertIsNotNone(self.hou_pepper.cam_node.parm('resx'))
        self.assertIsNotNone(self.hou_pepper.cam_node.parm('resy'))

    def test_set_fx_working_for_shot(self):
        self.pepper.project = 'PEPPER'
        self.pepper.asset = 'temp_fire'
        self.pepper.software = 'hipnc'
        self.pepper.entity = 'asset'
        for shot in self.pepper.get_casting_path_for_asset():
            precomp = self.pepper.make_precomp_dict(shot)
            temp_working_path = precomp.get('temp_working_path')
            layout_output_path = precomp.get('layout_output_path')
            fx_working_path = precomp.get('fx_working_path')

            self.hou_pepper.set_fx_working_for_shot(temp_working_path, layout_output_path,
                                         f'{fx_working_path}.{self.pepper.software.get("file_extension")}')
            fx_dir = os.path.dirname(fx_working_path)
            self.assertIsNotNone(os.path.isfile(fx_dir))

        self.assertEqual(self.hou_pepper.cam_list, [])
        self.assertEqual(self.hou_pepper.cam_path, [])


    def test_make_cmd(self):
        self.pepper.project = 'PEPPER'
        self.pepper.asset = 'temp_fire'
        self.pepper.software = 'hipnc'
        self.pepper.entity = 'asset'

        for shot in self.pepper.get_casting_path_for_asset():
            precomp = self.pepper.make_precomp_dict(shot)
            temp_working_path = precomp.get('temp_working_path')
            layout_output_path = precomp.get('layout_output_path')
            fx_working_path = precomp.get('fx_working_path')
            self.hou_pepper.set_fx_working_for_shot(temp_working_path, layout_output_path,
                                                    f'{fx_working_path}.{self.pepper.software.get("file_extension")}')
            self.hou_pepper.make_cmd(precomp)

        self.assertEqual(self.hou_pepper.cmd_list[0][:6], 'python')
        self.assertEqual(self.hou_pepper.cmd_list[1][:6], 'ffmpeg')
        self.assertEqual(self.hou_pepper.cmd_list[2][:6], 'python')
        self.assertEqual(self.hou_pepper.cmd_list[3][:6], 'ffmpeg')
        self.assertEqual(len(self.hou_pepper.cmd_list), 4)
        self.assertEqual(len(self.hou_pepper.total_frame_list), 4)
