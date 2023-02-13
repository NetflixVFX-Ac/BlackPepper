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
        """



        Returns:

        """
        # 실행부
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'layout'
        software_name = 'hou'
        task, task_type = self.pepper.get_task(task_type_name)
        pre_revision = gazu.files.get_last_working_file_revision(task).get('revision')
        self.pepper.publish_working_file(task_type_name, software_name)

        # 함수를 짤 때,
        # task, task_type = self.pepper.get_task(task_type_name)
        # software = self.pepper.get_software(software_name)
        # gazu.files.new_working_file(task, software=software)

        # 검증부
        update_revision = gazu.files.get_last_working_file_revision(task).get('revision')
        print(pre_revision, update_revision)
        self.assertLess(pre_revision, update_revision)

    def test_publish_output_file(self):
        """



        Returns:

        """
        # 조건부
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        output_type_name = 'movie_file'
        comments = 'for unittest_yeolhoon '
        task, task_type = self.pepper.get_task(task_type_name)
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        pre_revision = gazu.files.get_last_entity_output_revision(self.pepper.entity, output_type, task_type, name='main')
        task, task_type = self.pepper.get_task(task_type_name)

        self.pepper.publish_output_file(task_type_name, output_type_name, comments)

        # 함수를 짤 때,
        # task, task_type = self.pepper.get_task(task_type_name)
        # work_file = gazu.files.get_last_working_file_revision(task)
        # output_type = gazu.files.get_output_type_by_name(output_type_name)
        # gazu.files.new_entity_output_file(self.pepper.entity, output_type, task_type, working_file=work_file,
        #                                   representation=output_type['short_name'], comment=comments)

        # 검증부
        update_revision = gazu.files.get_last_entity_output_revision(self.pepper.entity, output_type, task_type, name='main')
        self.assertLess(pre_revision, update_revision)

    def test_working_file_path(self):
        """



        Returns:

        """
        # 실행부
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'layout'
        software_name = 'hou'
        input_num = 100
        task, task_type = self.pepper.get_task(task_type_name)
        path = self.pepper.working_file_path(task_type_name, software_name, input_num)

        # 함수를 짤 때,
        # task, task_type = self.pepper.get_task(task_type_name)
        # software = self.pepper.get_software(software_name)
        # revision_max = gazu.files.get_last_working_file_revision(task)['revision']
        # revision_num = self.get_revision_num(revision_max, input_num)
        # path = gazu.files.build_working_file_path(task, software=software, revision=revision_num)
        # ext = software['file_extension']
        # return path + '.' + ext

        # 검증부
        latest_revision = gazu.files.get_last_working_file_revision(task).get('revision')
        self.assertEqual(latest_revision, int(path.strip()[-7:-4]))

    def test_make_next_working_path(self):
        """



        Returns:

        """
        # 조건부
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'layout'
        task, task_type = self.pepper.get_task(task_type_name)
        path = self.pepper.make_next_working_path(task_type_name)

        # 함수를 짤 때,
        # task, task_type = self.pepper.get_task(task_type_name)
        # revision_max = gazu.files.get_last_working_file_revision(task)['revision']
        # path = gazu.files.build_working_file_path(task, revision=revision_max + 1)
        # return path

        # 검증부
        latest_revision = gazu.files.get_last_working_file_revision(task).get('revision')
        self.assertEqual(latest_revision+1, int(path.strip()[-3:]))

    def test_output_file_path(self):
        """



        Returns:

        """
        # 조건부
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        output_type_name = 'movie_file'
        input_num = 100
        task, task_type = self.pepper.get_task(task_type_name)
        path = self.pepper.output_file_path(output_type_name, task_type_name, input_num)

        # 함수를 짤 때,
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        # revision_max = gazu.files.get_last_entity_output_revision(self.pepper.entity, output_type, task_type, name='main')
        # revision_num = self.get_revision_num(revision_max, input_num)
        # path = gazu.files.build_entity_output_file_path(self.pepper.entity, output_type, task_type, revision=revision_num)
        # ext = output_type['short_name']
        # return path + '.' + ext

        # 검증부
        latest_revision = gazu.files.get_last_entity_output_revision(self.pepper.entity, output_type, task_type, name='main')
        self.assertEqual(latest_revision, int(path.strip()[-7:-4]))

    def test_make_next_output_path(self):
        """



        Returns:

        """
        # 조건부
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'SQ01'
        self.pepper.shot = '0010'
        self.pepper.entity = 'shot'
        task_type_name = 'fx'
        output_type_name = 'movie_file'
        path = self.pepper.make_next_output_path(output_type_name, task_type_name)

        # 함수를 짤 때,
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        # revision_max = gazu.files.get_last_entity_output_revision(self.pepper.entity, output_type, task_type, name='main')
        # path = gazu.files.build_entity_output_file_path(self.pepper.entity, output_type, task_type, revision=revision_max + 1)
        # ext = output_type['short_name']
        # return path + '.' + ext

        # 검증부
        latest_revision = gazu.files.get_last_entity_output_revision(self.pepper.entity, output_type, task_type, name='main')
        self.assertEqual(latest_revision + 1, int(path.strip()[-7:-4]))

    def test_get_revision_num(self):
        """


        Returns:

        """
        # 조건부
        revision_max = 6
        input_num = 10
        mock_num = None
        check_latest = self.pepper.get_revision_num(revision_max, input_num)
        check_none = self.pepper.get_revision_num(revision_max, mock_num)
        # 함수를 짤 때,
        # if input_num is None:
        #     return revision_max
        # self.pepper.int_check(input_num)
        # if revision_max < input_num:
        #     return revision_max
        # else:
        #     return input_num

        # 검증부
        self.assertEqual(check_latest, 6)
        self.assertEqual(check_none, 6)

    def test_get_task(self):
        """


        Returns:

        """
        # 조건부
        task_type_name = 'Layout'
        self.pepper.get_task(task_type_name)

        # 함수를 짤 때,

        # 검증부


    def test_get_software(self):
        self.fail()

    def test_casting_create(self):
        """

        Return casting for given shot
        if shot already casted to asset, raise "this shot already casted to asset"
        successful casting,

        Returns: True

        """
        # 실행부
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'sq01'
        self.pepper.shot = '0040'
        self.pepper.asset = 'temp_fire'
        self.pepper.casting_create(1)

        # 검증부
        occurences = 0
        assets = gazu.casting.get_asset_cast_in(self.pepper.asset)
        for asset in assets:
            if asset.get('sequence_name').lower() == 'sq01' and asset.get('shot_name') == '0040':
                occurences = asset.get('nb_occurences')
        self.assertEqual(occurences, 1)

    def test_casting_delete(self):
        """

        Return casting for given shot
        if casting non exist, return True, this raise error "casting non exist"
        casting exist, delete casting asset from shot
        successful delete casting,

        Returns: True

        """
        # 실행부
        self.pepper.project = 'PEPPER'
        self.pepper.sequence = 'sq01'
        self.pepper.shot = '0040'
        self.pepper.asset = 'temp_fire'
        self.pepper.casting_delete()

        # 함수를 짤 때,
        # asset_name = self.pepper.asset['name']
        # asset_castings = gazu.casting.get_shot_casting(self.pepper.shot)
        # filtered_assets = [asset for asset in asset_castings if asset_name != asset['asset_name']]
        # gazu.casting.update_shot_casting(self.pepper.project, self.pepper.shot, casting=filtered_assets)

        # 검증부
        asset_castings = gazu.casting.get_shot_casting(self.pepper.shot)
        asset_picked = None
        for casting in asset_castings:
            if casting.get('asset_name') == self.pepper.asset.get('name'):
                asset_picked = casting
        self.assertIsNone(asset_picked)

    def test_get_casting_path_for_asset(self):
        """

        asset에 Casting 되어 있는 shot의 working file lastest revision에 해당하는 dictionary를 가져온다.
        해당 함수에는 key 값이 revision인 value 값이 필요하고, revision이 0보다 커야한다.

        Returns:

        """
        # 실행부
        self.pepper.project = 'PEPPER'
        self.pepper.asset = 'temp_fire'

        # 함수를 짤 때,
        # out = None
        # cast_in = gazu.casting.get_asset_cast_in(self.pepper.asset)
        # for shot in cast_in:
        #     tasks = gazu.task.all_tasks_for_shot(shot)
        #     for task in tasks:
        #         last_revision = gazu.files.get_last_working_file_revision(task)
        #         out = last_revision
        # return out

        # 검증부
        last_revision = self.pepper.get_casting_path_for_asset()
        self.assertIn('revision', last_revision)
        self.assertTrue(last_revision.get('revision') > 0)

