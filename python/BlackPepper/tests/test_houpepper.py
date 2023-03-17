from unittest import TestCase
from BlackPepper.process.houpepper import HouPepper
from BlackPepper.pepper import Houpub
import os
import numpy as np
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
        self.hou_pepper.abc_path = abc_path
        self.hou_pepper.abc_range = abc_range
        cam = '/cam1/camCamera'

        bbb = abc.alembicGetCameraDict(abc_path, cam, 1)
        print(bbb)
        return

        self.hou_pepper.set_cam_view(cam)
        for parm_name in self.hou_pepper.hou_cam_parm_name:
            print('parm_name :', f'self.{parm_name}')

        # self.hou_pepper.cam_node = cam
        # parm_name = 'focal'
        # camera_dict = abc.alembicGetCameraDict(abc_path, cam, float(f) / hou.fps()).hou_pepper.hou_cam_parm_name
        # print(camera_dict)
        # for f in range(int(self.abc_range[0] * hou.fps()), int(self.abc_range[1] * hou.fps()) + 1):





    def test_get_cam_resolution(self):
        assert False

    def test_get_cam_xform(self):
        assert False

    def test_set_cam_key(self):
        assert False

    def test_set_cam_create(self):
        assert False

    def test_set_fx_working_for_shot(self):
        assert False

    def test_make_cmd(self):
        assert False
