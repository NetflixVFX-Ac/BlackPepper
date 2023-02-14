from unittest import TestCase
from pepper import Houpub
import gazu
import pprint


class TestHoupub(TestCase):


    def setUp(self):
        self.pepper = Houpub()
        self.pepper.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")

    @property
    def check(self):
        return self._check

    @check.setter
    def check(self, bool):
        self._check = bool

    def test_publish_working_file(self):
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'layout'
        software_name = 'hou'
        task_type, task = self.pepper.get_task(task_type_name)
        pre_revision = gazu.files.get_last_working_file_revision(task).get('revision')
        self.pepper.publish_working_file(task_type_name, software_name)
        update_revision = gazu.files.get_last_working_file_revision(task).get('revision')
        print(pre_revision, update_revision)
        self.assertLess(pre_revision, update_revision)

    def test_publish_output_file(self):
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        output_type_name = 'movie_file'
        comments = 'for unittest_yeolhoon '
        task_type, task = self.pepper.get_task(task_type_name)
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        pre_revision = gazu.files.get_last_entity_output_revision(self.pepper.entity, output_type, task_type,
                                                                  name='main')
        task_type, task = self.pepper.get_task(task_type_name)
        self.pepper.publish_output_file(task_type_name, output_type_name, comments)
        update_revision = gazu.files.get_last_entity_output_revision(self.pepper.entity, output_type, task_type,
                                                                     name='main')
        self.assertLess(pre_revision, update_revision)

    def test_working_file_path(self):
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'layout'
        software_name = 'hou'
        input_num = 100
        task_type, task = self.pepper.get_task(task_type_name)
        path = self.pepper.working_file_path(task_type_name, software_name, input_num)
        latest_revision = gazu.files.get_last_working_file_revision(task).get('revision')
        self.assertEqual(latest_revision, int(path.strip()[-7:-4]))

    def test_make_next_working_path(self):
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'layout'
        task_type, task = self.pepper.get_task(task_type_name)
        path = self.pepper.make_next_working_path(task_type_name)
        latest_revision = gazu.files.get_last_working_file_revision(task).get('revision')
        self.assertEqual(latest_revision + 1, int(path.strip()[-3:]))

    def test_output_file_path(self):
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

    def test_make_next_output_path(self):
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
        self.assertEqual(latest_revision + 1, int(path.strip()[-7:-4]))

    def test_get_revision_num(self):
        revision_max = 6
        input_num = 10
        mock_num = None
        check_latest = self.pepper.get_revision_num(revision_max, input_num)
        check_none = self.pepper.get_revision_num(revision_max, mock_num)
        self.assertEqual(check_latest, 6)
        self.assertEqual(check_none, 6)

    def test_get_task(self):
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        task_type, task = self.pepper.get_task(task_type_name)
        self.assertTrue(type(task_type), dict)
        self.assertEqual(task_type.get('name'), 'FX')

    def test_get_software(self):
        software_name = 'hou'
        check = self.pepper.get_software(software_name)
        self.assertEqual(check.get('file_extension'), 'hip')

    def test_get_casting_path_for_asset(self):
        self.pepper.project = 'PEPPER'
        self.pepper.asset = 'temp_fire'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        last_revision = self.pepper.get_casting_path_for_asset()
        shot_dict = None
        for i in range(len(last_revision)):
            if last_revision[i][0].get('shot_name') == self.pepper.shot.get('name'):
                shot_dict = last_revision[i][0]
        self.assertIsNotNone(shot_dict)

    def test_dick_check(self):
        test_dict = {'hook': 'team', 'mem_num': '7'}
        code = 'none'
        check = self.pepper.dict_check(test_dict, code)
        self.assertIs(type(check), dict)

    def test_args_str_check(self):
        arg = 'hook'
        args = 'num'
        check_arg = self.pepper.args_str_check(arg)
        check_args = self.pepper.args_str_check(arg, args)
        self.assertEqual(check_arg, arg)
        self.assertEqual(check_args, f'{arg},{args}')

    def test_str_check(self):
        strn = 'hook'
        check = self.pepper.str_check(strn)
        self.assertEqual(check, strn)

    def test_int_check(self):
        num = 5
        check = self.pepper.int_check(num)
        self.assertEqual(check, num)

    def test_error(self):
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
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0020'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        _, task = self.pepper.get_task(task_type_name)

        with self.assertRaises(Exception) as context:
            self.pepper.get_working_revision_max(task)
        self.assertEqual("No working file found.", str(context.exception))

        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0030'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        _, task = self.pepper.get_task(task_type_name)

        check = self.pepper.get_working_revision_max(task)
        self.assertIs(type(check), int)

    def test_get_all_shots(self):
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.assertIn('0010', self.pepper.get_all_shots())
        self.assertIn('0020', self.pepper.get_all_shots())
        self.assertIn('0030', self.pepper.get_all_shots())
        self.assertIn('0040', self.pepper.get_all_shots())
        self.assertIn('0050', self.pepper.get_all_shots())

    def test_get_task_types_for_asset(self):
        self.pepper.project = "PEPPER"
        self.pepper.asset = "temp_explosion"
        self.assertIn("simulation", self.pepper.get_task_types_for_asset())

    def test_get_all_projects(self):
        self.assertIn('PEPPER', self.pepper.get_all_projects())

    def test_get_all_assets(self):
        self.pepper.project = 'PEPPER'
        self.assertIn('fx_template', self.pepper.get_all_assets())

    def test_get_all_sequences(self):
        self.pepper.project = 'PEPPER'
        self.assertIn('SQ01', self.pepper.get_all_sequences())

    def test_get_casted_assets_for_shot(self):
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.assertIn('fx_template:temp_explosion', self.pepper.get_casted_assets_for_shot())

