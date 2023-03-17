from unittest import TestCase
from BlackPepper.log.moduler_log import Logger
from BlackPepper.pepper import Houpub
import gazu
import os
import pprint

class TestHoupub(TestCase):

    _project = None
    _sequence = None
    _shot = None
    _asset = None
    _entity = None
    _software = None


    def setUp(self):
        """
        기본 로그인 값 설정
        host : http://192.168.3.116/api
        identify : pipeline@rapa.org
        password : netflixacademy
        """
        self.pepper = Houpub()
        self.pepper.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")
        self.mylog = Logger()

    def test_login(self):
        host = "http://192.168.3.116/api"
        identify = "pipeline@rapa.org"
        password = "netflixacademy"

        gazu.client.set_host(host)
        self.user = gazu.log_in(identify, password)
        self.identif = identify
        self.mylog.set_logger(self.identif)


    def test_publish_working_file(self):
        self.pepper.project = 'HOON'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.software = 'hip'
        self.pepper.entity = 'shot'

        old = self.pepper.working_file_path('fx')
        self.pepper.publish_working_file('fx')
        new = self.pepper.working_file_path('fx')

        self.assertNotEqual(old, new)

    def test_publish_output_file(self):
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        self.pepper.software = "hip"


        self.pepper.publish_output_file('FX', 'Movie_file', "first_output")
        # 'layout_camera', 'camera_cache'
        new = self.pepper.output_file_path('jpeg', "fx")

        self.assertEqual(new, '/mnt/project/hook/pepper/shots/sq01/0010/fx/output/jpeg/v001/pepper_sq01_0010_jpeg_v001.undi_img')

    def test_working_file_path(self):
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        self.pepper.software = "hip"

        result = self.pepper.working_file_path(task_type_name)
        self.assertEqual(result, '/mnt/project/hook/pepper/shots/sq01/0010/fx/working/v068/pepper_sq01_0010_fx_068.hip')

    def test_make_next_working_path(self):
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        self.pepper.software = "hip"

        result = self.pepper.make_next_working_path(task_type_name)
        print("xxx", result)
        self.assertEqual(result, '/mnt/project/hook/pepper/shots/sq01/0010/fx/working/v069/pepper_sq01_0010_fx_069')

    def test_output_file_path(self):
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        self.pepper.software = "hip"

        result = self.pepper.output_file_path('jpeg', task_type_name)
        print("xxx", '"'+ result +'"')
        self.assertEqual(result, "/mnt/project/hook/pepper/shots/sq01/0010/fx/output/jpeg/v001/pepper_sq01_0010_jpeg_v001.undi_img")

    def test_make_next_output_path(self):
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        output_type_name = 'jpeg'
        self.pepper.software = "hip"

        result = self.pepper.make_next_output_path(output_type_name, task_type_name)
        print("xxx", '"' + result + '"')
        self.assertEqual(result, "/mnt/project/hook/pepper/shots/sq01/0010/fx/output/jpeg/v002/pepper_sq01_0010_jpeg_v002")

    def test_get_working_revision_max(self):
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        output_type_name = 'jpeg'
        self.pepper.software = "hip"

        result = self.pepper.get_working_revision_max("fx")
        self.assertEqual(result, 3)

    def test_get_revision_num(self):
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        output_type_name = 'jpeg'
        self.pepper.software = "hip"
        self.pepper.get_task(task_type_name)

        old = self.pepper.get_working_revision_max()
        print(old)
        result = self.pepper.get_revision_num(int(old['revision']), 5)
        print("xxx", '"' + result + '"')
        self.assertEqual(result, 1)

    def test_get_task(self):
        result = self.pepper.get_task('project', 'shot', 'task')
        self.assertEqual(result, {'id': 1234, 'name': 'task', 'type': 'animation'})

    def test_get_casting_path_for_asset(self):
        result = self.pepper.get_casting_path_for_asset('project', 'asset')
        self.assertEqual(result, 'path/to/casting/file')

    def test_make_precomp_dict(self):
        result = self.pepper.make_precomp_dict('project', 'shot')
        self.assertEqual(result, {'comp': 'path/to/comp/file', 'plates': ['path/to/plate1', 'path/to/plate2']})

    def test_publish_precomp_working(self):
        result = self.pepper.publish_precomp_working('project', 'shot')
        self.assertEqual(result, True)

    def test_publish_precomp_output(self):
        result = self.pepper.publish_precomp_output('project', 'shot')
        self.assertEqual(result, True)

    def test_get_every_revision_for_working_file(self):
        result = self.pepper.get_every_revision_for_working_file('project', 'shot', 'task')
        self.assertEqual(result, ['path/to/working/file_v001.ext', 'path/to/working/file_v002.ext',
                                  'path/to/working/file_v003.ext'])

    def test_get_every_revision_for_output_file(self):
        result = self.pepper.get_every_revision_for_output_file('project', 'shot', 'task')
        self.assertEqual(result, ['path/to/output/file_v001.ext', 'path/to/output/file_v002.ext',
                                  'path/to/output/file_v003.ext'])

    def test_check_task_status(self):
        result = self.pepper.check_task_status('project', 'shot', 'task')
        self.assertEqual(result, 'in progress')

    def test_get_task_status(self):
        result = self.pepper.get_task_status('project', 'shot', 'task')
        self.assertEqual(result, {'id': 1234, 'status': 'in progress'})


    def test_publish_preview(self):
        result = self.pepper.publish_preview
        self.assertEqual(result, {'id': 1234, 'status': 'in progress'})

    def test_get_all_projects(self):
        self.fail()

    def test_get_all_assets(self):
        self.fail()

    def test_get_all_sequences(self):
        self.fail()

    def test_get_all_shots(self):
        self.fail()

    def test_get_task_types_for_asset(self):
        self.fail()

    def test_get_casted_assets_for_shot(self):
        self.fail()

    def test_check_asset_type(self):
        self.fail()

    def test_get_my_projects(self):
        self.fail()

    def test_get_working_file_data(self):
        self.fail()

    def test_get_output_file_data(self):
        self.fail()

    def test_dict_check(self):
        self.fail()

    def test_args_str_check(self):
        self.fail()

    def test_str_check(self):
        self.fail()

    def test_int_check(self):
        self.fail()

    def test_error(self):
        self.fail()
