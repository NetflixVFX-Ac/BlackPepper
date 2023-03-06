from unittest import TestCase
from BlackPepper.houpepper import HouPepper
import hou


class TestHouPepper(TestCase):
    def setUp(self):
        self.hou_pepper = HouPepper()
        self.hou_pepper.set_abc_cam_tree('/mnt/project/hook/pepper/shots/sq01/0010/layout/output/camera_cache/v001'
                                         '/pepper_sq01_0010_camera_cache_v001.abc')

    def test_check_abc(self):
        self.fail()

    def test_set_cam_view(self):
        self.fail()

    def test_get_cam_resolution(self):
        self.fail()

    def test_get_cam_xform(self):
        self.fail()

    def test_set_cam_key(self):
        self.fail()

    def test_set_cam_create(self):
        self.fail()

    def test_set_fx_working_for_shot(self):
        self.fail()

    def test_set_mantra_for_render(self):
        self.fail()

    def test_set_ffmpeg_seq_to_mp4(self):
        self.fail()
