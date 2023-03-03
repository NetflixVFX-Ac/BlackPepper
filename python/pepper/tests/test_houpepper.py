from unittest import TestCase
from pepper import Houpub
from houpepper import HouPepper
import hou

class TestHouPepper(TestCase):

    def setUp(self):
        """
        기본 로그인 값 설정
        host : http://192.168.3.116/api
        identify : pipeline@rapa.org
        password : netflixacademy
        """
        self.pepper = Houpub()
        self.pepper.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")
        self.hou_pepper = HouPepper()

    def test_abc_path(self):
        self.pepper.project = 'PEPPER'
        self.pepper.asset = 'temp_dancing_particle'
        self.pepper.entity = 'asset'
        self.pepper.software = 'hiplc'
        simulation_type_name = 'simulation'
        simulation_path = self.pepper.working_file_path(simulation_type_name, input_num=1)
        casted_shots = self.pepper.get_casting_path_for_asset()
        for shot in casted_shots:
            self.pepper.sequence = shot.get('sequence_name')
            self.pepper.shot = shot.get('shot_name')
            self.pepper.entity = 'shot'
            layout_type_name = 'layout'
            output_type_name = 'camera_cache'
            layout_output_path = self.pepper.output_file_path(output_type_name, layout_type_name)
            print(layout_output_path)

    def test_abc_path(self):
        self.fail()

    def test_abc_tree_all(self):
        self.fail()

    def test_abc_tree_all(self):
        self.fail()

    def test_abc_tree_path(self):
        self.fail()

    def test_abc_tree_path(self):
        self.fail()

    def test_abc_range(self):
        self.fail()

    def test_abc_range(self):
        self.fail()

    def test_set_abc_cam_tree(self):
        self.fail()

    def test_get_abc_cam_tree(self):
        self.fail()

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

    def test_set_ffmpeg_seq_to_mov(self):
        self.fail()
