from unittest import TestCase
from BlackPepper.pepper import Houpub
import gazu
import os
import pprint
import random


class TestHoupub(TestCase):

    def setUp(self):
        """
        기본 로그인 값 설정
        host : http://192.168.3.116/api
        identify : pipeline@rapa.org
        password : netflixacademy
        """
        self.pepper = Houpub()
        self.pepper.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")

    def test_publish_working_file(self):
        """
        publish를 통해 working file의 last revision이 정상적으로 업데이트 됐는지 체크한다.
        """
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'layout_camera'
        self.pepper.software = 'hip'

        task_type, task = self.pepper.get_task(task_type_name)
        pre_revision = gazu.files.get_last_working_file_revision(task).get('revision')
        self.pepper.publish_working_file(task_type_name)
        update_revision = gazu.files.get_last_working_file_revision(task).get('revision')
        self.assertLess(pre_revision, update_revision)

        old = self.pepper.working_file_path('fx')
        self.pepper.publish_working_file('fx')
        new = self.pepper.working_file_path('fx')
        self.assertNotEqual(old, new)

    def test_publish_output_file(self):
        """
        publish를 통해 output file의 last revision이 정상적으로 업데이트 됐는지 체크한다.
        """
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        output_type_name = 'movie_file'
        comments = 'for unittest_yeolhoon'
        task_type, task = self.pepper.get_task(task_type_name)
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        pre_revision = gazu.files.get_last_entity_output_revision(self.pepper.entity, output_type, task_type,
                                                                  name='main')
        task_type, task = self.pepper.get_task(task_type_name)
        self.pepper.publish_output_file(task_type_name, output_type_name, comments)
        update_revision = gazu.files.get_last_entity_output_revision(self.pepper.entity, output_type, task_type,
                                                                     name='main')
        self.assertLess(pre_revision, update_revision)

        new = self.pepper.output_file_path('jpeg', "fx")
        self.assertEqual(new,
                         '/mnt/project/hook/pepper/shots/sq01/0010/fx/output/'
                         'jpeg/v001/pepper_sq01_0010_jpeg_v001.undi_img')

    def test_working_file_path(self):
        """
        woking file path를 출력하여 last revisioln에 해당하는 path가 제대로 출력되는지 체크한다.
        """
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        self.pepper.software = 'hip'
        task_type_name = 'layout_camera'
        task_type, task = self.pepper.get_task(task_type_name)
        path = self.pepper.working_file_path(task_type_name)
        latest_revision = gazu.files.get_last_working_file_revision(task).get('revision')
        self.assertEqual(latest_revision, int(path.strip()[-7:-4]))

    def test_make_next_working_path(self):
        """
        working file이 저장될 path를 출력하면, last revision에 +1이 더해진 경로로 출력되는지 체크한다.
        """
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'layout_camera'
        task_type, task = self.pepper.get_task(task_type_name)
        path = self.pepper.make_next_working_path(task_type_name)
        latest_revision = gazu.files.get_last_working_file_revision(task).get('revision')
        self.assertEqual(latest_revision + 1, int(path.strip()[-3:]))

    def test_output_file_path(self):
        """
        output file path를 출력하여 last revisioln에 해당하는 path가 제대로 출력되는지 체크한다.
        """
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        output_type_name = 'movie_file'
        input_num = 100
        path = self.pepper.output_file_path(output_type_name, task_type_name, input_num)
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        latest_revision = gazu.files.get_last_entity_output_revision(self.pepper.entity, output_type, task_type,
                                                                     name='main')
        self.assertEqual(latest_revision, int(path.strip()[-7:-4]))
        result = self.pepper.output_file_path('jpeg', task_type_name)
        self.assertEqual(result,
                         "/mnt/project/hook/pepper/shots/sq01/0010/fx/"
                         "output/jpeg/v001/pepper_sq01_0010_jpeg_v001.undi_img")

    def test_make_next_output_path(self):
        """
        output file이 저장될 path를 출력하면, last revision에 +1이 더해진 경로로 출력되는지 체크한다.
        """
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        output_type_name = 'movie_file'
        path = self.pepper.make_next_output_path(output_type_name, task_type_name)
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        latest_revision = gazu.files.get_last_entity_output_revision(self.pepper.entity, output_type, task_type,
                                                                     name='main')

        self.assertEqual(latest_revision + 1, int(path.strip()[-3:]))

    def test_get_revision_num(self):
        """
        input_num이 revision_max보다 클 경우, revision_max로 출력되는지 체크한다.
        input_num이 None값일 경우, revision_max로 출력되는지 체크한다.
        """
        revision_max = 6
        input_num = 10
        mock_num = None
        check_latest = self.pepper.get_revision_num(revision_max, input_num)
        check_none = self.pepper.get_revision_num(revision_max, mock_num)
        self.assertEqual(check_latest, check_none)
        self.assertEqual(check_latest, 6)
        self.assertEqual(check_none, 6)

    def test_get_task(self):
        """
        task_type_name에 해당하는 task_type과 task가 제대로 출력되는지 체크한다.
        """
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        task_type, task = self.pepper.get_task(task_type_name)
        self.assertTrue(type(task_type), dict)
        self.assertEqual(task_type.get('name'), 'FX')

    def test_software(self):
        """
        software 함수에서 if문이 제대로 작동하는지 체크한다.
        """
        self.pepper.software = 'hipnc'
        self.assertEqual(self.pepper.software.get('file_extension'), 'hipnc')
        self.pepper.software = 'hip'
        self.assertEqual(self.pepper.software.get('file_extension'), 'hip')
        self.pepper.software = 'hiplc'
        self.assertEqual(self.pepper.software.get('file_extension'), 'hiplc')

    def test_get_casting_path_for_asset(self):
        """
        asset에 캐스팅 된 layout의 entity가 shot의 id와 같은지 체크한다.
        """
        self.pepper.project = 'PEPPER'
        self.pepper.asset = 'temp_fire'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        # last_revision = self.BlackPepper.get_casting_path_for_asset()
        # shot_dict = None
        # for i in range(len(last_revision)):
        #     if last_revision[i][0].get('shot_name') == self.BlackPepper.shot.get('name'):
        #         shot_dict = last_revision[i][0]
        # self.assertIsNotNone(shot_dict)
        casted_shots = self.pepper.get_casting_path_for_asset()
        shot = None
        layout_task = None
        fx_task = None
        for i in casted_shots:
            if i.get('shot_name') == '0010':
                shot = i
        self.assertEqual(shot.get('shot_name'), '0010')

    def test_dick_check(self):
        """
        임의의 dictionary를 만들고 dict_check가 dictionary 형태로 반환하는지 체크한다.
        """
        test_dict = {'hook': 'team', 'mem_num': '7'}
        code = 'none'
        check = self.pepper.dict_check(test_dict, code)
        self.assertIs(type(check), dict)

    def test_args_str_check(self):
        """
        argment가 str인지 체크한다.
        다수의 인자가 들어올 경우, ','로 나눠서 반환하는지 체크한다.
        *오류발생 : int값을 넣을 경우 if 문의 else로 빠지는 것이 아닌, if의 tuple일 경우로 빠진다.
        """
        # arg_num = 1
        arg = 'hook'
        args = 'num'
        # check_arg_num = self.BlackPepper.args_str_check(arg_num)
        check_arg = self.pepper.args_str_check(arg)
        check_args = self.pepper.args_str_check(arg, args)
        self.assertEqual(check_arg, arg)
        self.assertEqual(check_args, f'{arg},{args}')

    def test_str_check(self):
        """
        str을 제대로 분별하는지 체크한다.
        int 값이 들어갔을 때, 오류를 발생하는지 체크한다.
        """
        strn = 'hook'
        str_num = 1
        check = self.pepper.str_check(strn)
        self.assertEqual(check, strn)
        with self.assertRaises(Exception) as context:
            self.pepper.str_check(str_num)
        self.assertEqual("Input must be string", str(context.exception))

    def test_int_check(self):
        """
        int를 제대로 분별하는지 체크한다.
        str 값이 들어갔을 때, 오류를 발생하는지 체크한다.
        """
        num = 5
        num_str = '5'
        check = self.pepper.int_check(num)
        self.assertEqual(check, num)
        with self.assertRaises(Exception) as context:
            self.pepper.int_check(num_str)
        self.assertEqual("Input must be integer.", str(context.exception))

    def test_error(self):
        """
        code에 따라 오류가 제대로 발생하는지 체크한다.
        """
        code = 'not_string'
        with self.assertRaises(Exception) as context:
            self.pepper.error(code)
        self.assertEqual("Input must be string", str(context.exception))
        code = 'not_int'
        with self.assertRaises(Exception) as context:
            self.pepper.error(code)
        self.assertEqual("Input must be integer.", str(context.exception))
        code = 'none'
        with self.assertRaises(Exception) as context:
            self.pepper.error(code)
        self.assertEqual("There is no dict", str(context.exception))
        code = 'no_task'
        with self.assertRaises(Exception) as context:
            self.pepper.error(code)
        self.assertEqual("There's no task in entity.", str(context.exception))
        code = 'no_project'
        with self.assertRaises(Exception) as context:
            self.pepper.error(code)
        self.assertEqual("No project is assigned.", str(context.exception))
        code = 'no_sequence'
        with self.assertRaises(Exception) as context:
            self.pepper.error(code)
        self.assertEqual("No sequence is assigned.", str(context.exception))
        code = 'no_shot'
        with self.assertRaises(Exception) as context:
            self.pepper.error(code)
        self.assertEqual("No shot is assigned.", str(context.exception))
        code = 'no_asset'
        with self.assertRaises(Exception) as context:
            self.pepper.error(code)
        self.assertEqual("No asset is assigned.", str(context.exception))
        code = 'no_work_file'
        with self.assertRaises(Exception) as context:
            self.pepper.error(code)
        self.assertEqual("No working file found.", str(context.exception))
        code = 'no_output_file'
        with self.assertRaises(Exception) as context:
            self.pepper.error(code)
        self.assertEqual("No output file found.", str(context.exception))
        code = 'not_asset_shot'
        with self.assertRaises(Exception) as context:
            self.pepper.error(code)
        self.assertEqual("No shot or asset is assigned.", str(context.exception))

    def test_get_working_revision_max(self):
        """
        working file의 revision_max가 int값으로 제대로 출력되는지 체크한다.
        """
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0020'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        _, task = self.pepper.get_task(task_type_name)

        get_revision = self.pepper.get_working_revision_max(task)
        next_revision = self.pepper.make_next_working_path(task_type_name)
        self.assertLess(get_revision, int(next_revision[-3:]))

        # with self.assertRaises(Exception) as context:
        #     self.pepper.get_working_revision_max(task)
        # self.assertEqual("No working file found.", str(context.exception))

        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0030'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        _, task = self.pepper.get_task(task_type_name)

        check = self.pepper.get_working_revision_max(task)
        self.assertIs(type(check), int)

    def test_get_all_shots(self):
        """
        project와 sequence를 입력했을때, sequence 안에 있는 shot list를 출력하고, 안에 shot이 있는지 체크한다.
        """
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.assertIn('0010', self.pepper.get_all_shots())
        self.assertIn('0020', self.pepper.get_all_shots())
        self.assertIn('0030', self.pepper.get_all_shots())
        self.assertIn('0040', self.pepper.get_all_shots())

        result = self.pepper.get_all_shots()
        self.assertEqual(str(result), "['0010', '0020', '0030', '0040']")

    def test_get_task_types_for_asset(self):
        """
        project와 asset을 입력했을때, asset안에 simulation task_type이 있는지 체크한다.
        """
        self.pepper.project = "PEPPER"
        self.pepper.asset = "temp_breaking_glass"

        result = self.pepper.get_task_types_for_asset()
        self.assertIn("simulation", self.pepper.get_task_types_for_asset())
        self.assertEqual(str(result), "['simulation']")

    def test_get_all_projects(self):
        """
        모든 프로젝트를 출력하고, 그 안에 PEPPER project가 있는지 체크한다.
        """
        self.assertIn('PEPPER', self.pepper.get_all_projects())

    def test_get_all_assets(self):
        """
        PEPPER asset내, Template이 제대로 출력됐는지 체크한다.
        """
        self.pepper.project = 'PEPPER'
        self.assertIn('temp_breaking_glass', self.pepper.get_all_assets())
        self.assertIn('temp_dancing_particle', self.pepper.get_all_assets())
        self.assertIn('temp_fire', self.pepper.get_all_assets())

    def test_get_all_sequences(self):
        """
        PEPPER sequence내, SQ01이 제대로 출력됐는지 체크한다.
        """
        self.pepper.project = 'PEPPER'
        self.assertIn('SQ01', self.pepper.get_all_sequences())

    def test_user_flow(self):
        """

        user_flow에 맞춰 unittest를 진행한다.

        1. login unittest
        소프트웨어 assign
        self.BlackPepper.software = 'hipnc'
        """
        host = 'http://192.168.3.116/api'
        identify = 'pepper@hook.com'
        password = 'pepperpepper'
        project = None
        self.pepper.login(host, identify, password)
        self.assertIn('PEPPER', self.pepper.get_my_projects())

        """
        2. my_projects unittest / 
        
        saved info
        -   self.BlackPepper.project = project
        
        """
        for proj in self.pepper.get_my_projects():
            if proj == 'PEPPER':
                project = proj
        self.pepper.project = project
        self.assertEqual(project, 'PEPPER')

        """
        3. template list unittest
        
        saved info
        -   self.BlackPepper.project = project
        
        """
        assets = []
        for asset in self.pepper.get_all_assets():
            assets.append(asset)
        self.assertIn('temp_breaking_glass', assets)
        self.assertIn('temp_dancing_particle', assets)
        self.assertIn('temp_fire', assets)

        """
        4. pick template
        
        saved info
        -   self.BlackPepper.project = project = "PEPPER"
        -   self.BlackPepper.asset = 'temp_fire'
        """
        pick_template = None
        for asset in self.pepper.get_all_assets():
            if asset == 'temp_fire':
                pick_template = asset
        self.pepper.asset = pick_template
        self.assertEqual(self.pepper.asset.get('name'), 'temp_fire')

        """
        5. template 'temp_fire' working file path unittest
        
        saved info
        -   self.BlackPepper.project = project = "PEPPER"
        -   self.BlackPepper.asset = 'temp_fire'
        """
        task_type = None
        self.pepper.entity = 'asset'
        self.pepper.software = 'hip'
        for t in gazu.task.all_task_types_for_asset(self.pepper.asset):
            if t.get('name') == 'simulation':
                task_type = t
                path = self.pepper.working_file_path(task_type.get('name'))
                dir = os.path.dirname(path)
        self.assertEqual(dir, '/mnt/project/hook/pepper/assets/fx_template/temp_fire/simulation/working/v009')

        """
        6. casting shot unittest
        saved info
        -   self.BlackPepper.project = project
        -   self.BlackPepper.asset = 'temp_fire'
        
        
        """
        shots = []
        casted_shots = self.pepper.get_casting_path_for_asset()
        for shot in casted_shots:
            shots.append(shot.get('shot_name'))
        self.assertIn('0010', shots)
        self.assertIn('0030', shots)

        """
        7. pick shot
        
        saved info
        -   self.BlackPepper.project = project
        -   self.BlackPepper.asset = 'temp_fire'
        -   self.BlackPepper.sequence = shot.get('sequence_name') = SQ01
        -   self.BlackPepper.shot = shot.get('shot_name') = 0010
        """
        picked_shot = None
        shot = '0010'
        for shot in casted_shots:
            if shot.get('shot_name') == '0010':
                picked_shot = shot
        self.pepper.sequence = picked_shot.get('sequence_name')
        self.pepper.shot = picked_shot.get('shot_name')
        self.pepper.entity = 'shot'

        """
        8. template + shot(layout) 

        saved info
        -   self.BlackPepper.project = project
        -   self.BlackPepper.asset = 'temp_fire'
        -   self.BlackPepper.sequence = shot.get('sequence_name') = SQ01
        -   self.BlackPepper.shot = shot.get('shot_name') = 0010        
        """
        self.pepper.make_precomp_dict(picked_shot)
        result = self.pepper.make_precomp_dict(picked_shot)
        self.assertEqual(result['name'], 'PEPPER_fire_SQ01_0010')
        """
        9. render button
        
        saved info
        -   self.BlackPepper.project = project
        -   self.BlackPepper.asset = 'temp_fire'
        -   self.BlackPepper.sequence = shot.get('sequence_name') = SQ01
        -   self.BlackPepper.shot = shot.get('shot_name') = 0010        
        """

        """
        10. publish
        
        """

        aa = self.pepper.publish_precomp_working(result)
        nwp = self.pepper.make_next_working_path('FX')
        pprint.pp(nwp)

        self.pepper.publish_precomp_output(result)
        nwp2 = self.pepper.make_next_output_path('Movie_file', 'FX')
        pprint.pp(nwp2)

# -------------------------------------------------

    def test_make_precomp_dict(self):
        self.pepper.project = 'PEPPER'
        self.pepper.software = 'hip'
        asset_name = 'temp_breaking_glass'
        self.pepper.asset = asset_name
        casted_shots = self.pepper.get_casting_path_for_asset()
        for casted_shot in casted_shots:
            self.assertIn('shot_name', casted_shot)
            self.assertIn('sequence_name', casted_shot)
            made_dict = self.pepper.make_precomp_dict(casted_shot)
            sequence_name = casted_shot['sequence_name']
            shot_name = casted_shot['shot_name']
            test_name = '_'.join([self.pepper.project['name'], self.pepper.asset['name'][5:],
                                 sequence_name, shot_name])
            self.pepper.asset = asset_name
            self.pepper.entity = 'asset'
            test_temp_working_path = self.pepper.working_file_path('simulation')
            self.pepper.sequence = sequence_name
            self.pepper.shot = shot_name
            self.pepper.entity = 'shot'
            test_layout_output_path = self.pepper.output_file_path('camera_cache', 'layout_camera')
            test_fx_working_path = self.pepper.make_next_working_path('FX')
            test_jpg_output_path = self.pepper.make_next_output_path('jpg_sequence', 'FX')
            test_video_output_path = self.pepper.make_next_output_path('movie_file', 'FX')
            self.assertEqual(made_dict['name'], test_name)
            self.assertEqual(made_dict['temp_working_path'], test_temp_working_path)
            self.assertEqual(made_dict['layout_output_path'], test_layout_output_path)
            self.assertEqual(made_dict['fx_working_path'], test_fx_working_path)
            self.assertEqual(made_dict['jpg_output_path'], test_jpg_output_path)
            self.assertEqual(made_dict['video_output_path'], test_video_output_path)

    def test_path_seperator(self):
        self.pepper.project = 'PEPPER'
        self.pepper.software = 'hip'
        asset_name = 'temp_breaking_glass'
        self.pepper.asset = asset_name
        casted_shots = self.pepper.get_casting_path_for_asset()
        for casted_shot in casted_shots:
            self.assertIn('shot_name', casted_shot)
            self.assertIn('sequence_name', casted_shot)
            made_dict = self.pepper.make_precomp_dict(casted_shot)
            sequence_name = casted_shot['sequence_name']
            shot_name = casted_shot['shot_name']
            self.pepper.asset = asset_name
            self.pepper.entity = 'asset'
            test_temp_working_path = self.pepper.working_file_path('simulation')
            self.pepper.sequence = sequence_name
            self.pepper.shot = shot_name
            self.pepper.entity = 'shot'
            test_layout_output_path = self.pepper.output_file_path('camera_cache', 'layout_camera')
            test_fx_working_path = self.pepper.make_next_working_path('FX')
            test_jpg_output_path = self.pepper.make_next_output_path('jpg_sequence', 'FX')
            test_video_output_path = self.pepper.make_next_output_path('movie_file', 'FX')
            temp_working_path, layout_output_path, fx_working_path, jpg_output_path, video_output_path = \
                self.pepper.path_seperator(made_dict)
            self.assertEqual(temp_working_path, test_temp_working_path)
            self.assertEqual(layout_output_path, test_layout_output_path)
            self.assertEqual(fx_working_path, test_fx_working_path)
            self.assertEqual(jpg_output_path, test_jpg_output_path)
            self.assertEqual(video_output_path, test_video_output_path)

    def test_publish_precomp_working(self):
        self.pepper.project = 'PEPPER'
        self.pepper.software = 'hip'
        asset_name = 'temp_breaking_glass'
        self.pepper.asset = asset_name
        casted_shots = self.pepper.get_casting_path_for_asset()
        for casted_shot in casted_shots:
            precomp = self.pepper.make_precomp_dict(casted_shot)
            sequence_name = casted_shot['sequence_name']
            shot_name = casted_shot['shot_name']
            split_name = precomp['name'].split('_')
            self.assertEqual(split_name[0], self.pepper.project['name'])
            self.assertEqual(split_name[-2], sequence_name)
            self.assertEqual(split_name[-1], shot_name)
            self.pepper.sequence = casted_shot['sequence_name']
            self.pepper.shot = casted_shot['shot_name']
            old_path = self.pepper.working_file_path('FX')
            self.pepper.publish_precomp_working(precomp)
            new_path = self.pepper.working_file_path('FX')
            self.assertNotEqual(old_path, new_path)

    def test_publish_precomp_output(self):
        self.pepper.project = 'PEPPER'
        self.pepper.software = 'hip'
        asset_name = 'temp_breaking_glass'
        self.pepper.asset = asset_name
        casted_shots = self.pepper.get_casting_path_for_asset()
        for casted_shot in casted_shots:
            precomp = self.pepper.make_precomp_dict(casted_shot)
            sequence_name = casted_shot['sequence_name']
            shot_name = casted_shot['shot_name']
            split_name = precomp['name'].split('_')
            self.assertEqual(split_name[0], self.pepper.project['name'])
            self.assertEqual(split_name[-2], sequence_name)
            self.assertEqual(split_name[-1], shot_name)
            self.pepper.sequence = casted_shot['sequence_name']
            self.pepper.shot = casted_shot['shot_name']
            old_path = self.pepper.output_file_path('Movie_file', 'FX')
            self.pepper.publish_precomp_output(precomp)
            new_path = self.pepper.output_file_path('Movie_file', 'FX')
            self.assertNotEqual(old_path, new_path)

    def test_get_every_revision_for_working_file(self):
        asset_name = 'temp_breaking_glass'
        asset_test_task_type_name = 'simulation'
        sequence_name = 'SQ01'
        shot_name = '0020'
        shot_test_task_type_name = 'FX'
        self.pepper.project = 'PEPPER'
        self.pepper.software = 'hip'
        self.pepper.asset = asset_name
        self.pepper.entity = 'asset'
        rev_list = self.pepper.get_every_revision_for_working_file(asset_test_task_type_name)
        self.assertTrue(rev_list)
        for num in rev_list:
            self.assertEqual(type(num), int)
        self.pepper.sequence = sequence_name
        self.pepper.shot = shot_name
        self.pepper.entity = 'shot'
        rev_list = self.pepper.get_every_revision_for_working_file(shot_test_task_type_name)
        self.assertTrue(rev_list)
        for num in rev_list:
            self.assertEqual(type(num), int)

    def test_get_every_revision_for_output_file(self):
        sequence_name = 'SQ01'
        shot_name = '0040'
        shot_test_task_type_name = 'layout_camera'
        shot_output_type_name = 'camera_cache'
        self.pepper.project = 'PEPPER'
        self.pepper.software = 'hip'
        self.pepper.sequence = sequence_name
        self.pepper.shot = shot_name
        self.pepper.entity = 'shot'
        rev_list = self.pepper.get_every_revision_for_output_file(shot_output_type_name, shot_test_task_type_name)
        self.assertTrue(rev_list)
        for num in rev_list:
            self.assertEqual(type(num), int)

    def test_get_task_status(self):
        all_status = ['Todo', 'Ready To Start', 'Work In Progress', 'Done', 'Retake']
        for status in all_status:
            status_dict = self.pepper.get_task_status(status)
            self.assertTrue(status_dict)
            self.assertDictEqual(status_dict, gazu.task.get_task_status_by_name(status))

    def test_check_task_status(self):
        asset_name = 'temp_breaking_glass'
        asset_test_task_type_name = 'simulation'
        sequence_name = 'SQ01'
        shot_name = '0020'
        shot_test_task_type_name = 'FX'
        self.pepper.project = 'PEPPER'
        self.pepper.software = 'hip'
        self.pepper.asset = asset_name
        self.pepper.entity = 'asset'
        self.assertTrue(self.pepper.check_task_status('Done', asset_test_task_type_name))
        self.assertFalse(self.pepper.check_task_status('Retake', asset_test_task_type_name))

    def test_publish_preview(self):
        sequence_name = 'SQ01'
        shot_name = '0040'
        shot_test_task_type_name = 'layout_camera'
        path = f'/mnt/project/test/dino/dino.{random.randrange(1, 218)}.png'
        self.pepper.project = 'PEPPER'
        self.pepper.software = 'hip'
        self.pepper.sequence = sequence_name
        self.pepper.shot = shot_name
        self.pepper.entity = 'shot'
        task_type, task = self.pepper.get_task(shot_test_task_type_name)
        task_id = task['id']
        task_type_id = task_type['id']
        all_preview = gazu.shot.all_previews_for_shot(self.pepper.entity)
        for preview in all_preview[task_type_id]:
            self.assertEqual(preview['task_id'], task_id)
        old_revs = [preview['revision'] for preview in all_preview[task_type_id]]
        self.pepper.publish_preview(shot_test_task_type_name, 'Done', f'Test publish, preview file : {path}', path)
        all_preview = gazu.shot.all_previews_for_shot(self.pepper.entity)
        for preview in all_preview[task_type_id]:
            self.assertEqual(preview['task_id'], task_id)
        new_revs = [preview['revision'] for preview in all_preview[task_type_id]]
        self.assertNotEqual(old_revs, new_revs)

    def test_check_asset_type(self):
        self.pepper.project = 'PEPPER'
        asset_name = 'temp_breaking_glass'
        asset_type_name = 'fx_template'
        self.assertIsNotNone(self.pepper.check_asset_type(asset_name, asset_type_name))
        self.assertEqual(self.pepper.check_asset_type(asset_name, asset_type_name), asset_name)
        self.assertIsNone(self.pepper.check_asset_type(asset_name, 'testname'))
        self.assertIsNone(self.pepper.check_asset_type('testname', asset_type_name))

    def test_get_my_projects(self):
        my_projects = self.pepper.get_my_projects()
        self.assertTrue(my_projects)
        for project in my_projects:
            self.pepper.project = project
            self.assertEqual(self.pepper.project['type'], 'Project')

    def test_get_working_file_data(self):
        asset_name = 'temp_breaking_glass'
        asset_task_type_name = 'simulation'
        self.pepper.project = 'PEPPER'
        self.pepper.software = 'hip'
        self.pepper.asset = asset_name
        self.pepper.entity = 'asset'
        rev_list = self.pepper.get_every_revision_for_working_file(asset_task_type_name)
        for revision in rev_list:
            name, time, rev = self.pepper.get_working_file_data(asset_task_type_name, revision, 'asset')
            self.assertTrue(gazu.person.get_person_by_full_name(name))
            self.assertEqual(rev, revision)
            date = time[:10]
            for data in date.split('-'):
                self.assertTrue(data.isdigit())
            clock = time[11:]
            for data in clock.split(':'):
                self.assertTrue(data.isdigit())

    def test_get_output_file_data(self):
        sequence_name = 'SQ01'
        shot_name = '0020'
        task_type_name = 'layout_camera'
        output_type_name = 'camera_cache'
        self.pepper.project = 'PEPPER'
        self.pepper.software = 'hip'
        self.pepper.sequence = sequence_name
        self.pepper.shot = shot_name
        self.pepper.entity = 'shot'
        rev_list = self.pepper.get_every_revision_for_output_file(output_type_name, task_type_name)
        for revision in rev_list:
            name, time, rev = self.pepper.get_working_file_data(task_type_name, revision, 'shot')
            self.assertTrue(gazu.person.get_person_by_full_name(name))
            self.assertEqual(rev, revision)
            date = time[:10]
            for data in date.split('-'):
                self.assertTrue(data.isdigit())
            clock = time[11:]
            for data in clock.split(':'):
                self.assertTrue(data.isdigit())
