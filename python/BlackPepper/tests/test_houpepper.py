from unittest import TestCase
from BlackPepper.process.houpepper import HouPepper
import os
import numpy as np
import hou
import _alembic_hom_extensions as abc
import os


class TestHouPepper(TestCase):
    def setUp(self):
        self.hou_pepper = HouPepper()

    def test_abc_path(self):
        abc_path = '/mnt/project/hook/pepper/shots/sq01/0010/layout_camera/output/camera_cache/v005/pepper_sq01_0010_camera_cache_v005.abc'
        self.hou_pepper.abc_path = abc_path
        check = self.hou_pepper.abc_path
        self.assertEqual(check, ('/mnt/project/hook/pepper/shots/sq01/0010/layout_camera/output/camera_cache/v005/pepper_sq01_0010_camera_cache_v005.abc'))

    def test_abc_tree_all(self, abc_tree_all=None):
        abc_path = '/mnt/project/hook/pepper/shots/sq01/0010/layout_camera/output/camera_cache/v005/pepper_sq01_0010_camera_cache_v005.abc'
        abc_range = abc.alembicTimeRange(abc_path)
        abc_tree_all = [
            "root",
            "group",
            [
                ["camera1", "camera", []],
                ["group1", "group", [
                    ["camera2", "camera", []],
                    ["group2", "group", [
                        ["camera3", "camera", []]
                    ]]
                ]]
            ]]
        self.get_abc_cam_tree(abc_tree_all)

        self.assertListEqual(self.cam_list, ["camera1", "camera2", "camera3"])
        self.assertListEqual(self.cam_path, ["root/group/camera1", "root/group/group1/camera2",
                                                    "root/group/group1/group2/camera3"])
        self.assertIsNotNone(self.abc_range)

    def test_abc_tree_path(self):
        self.abc_tree_path = abc.alembicGetObjectPathListForMenu(abc_path)

    def test_abc_range(self):
        abc_path = '/mnt/project/hook/pepper/shots/sq01/0010/layout_camera/output/camera_cache/v005/pepper_sq01_0010_camera_cache_v005.abc'
        abc_range = abc.alembicTimeRange(abc_path)
        self.hou_pepper.abc_range = abc_range
        check = self.hou_pepper.abc_range
        self.assertEqual(check, (0.041666666666666664, 10.0))

    def test_set_abc_cam_tree(self):
        assert False

    def test_get_abc_cam_tree(self):
        assert False

    def test_check_abc(self):
        assert False

    def test_set_cam_view(self):
        assert False

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
