from unittest import TestCase
import gazu
from pepper import Houpub


class test_Houpub(TestCase):
    def setUp(self):
        self.pepper = Houpub()
        self.pepper.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")

    def test_casting_multiple_assets(self):
        self.pepper.project = 'pepper'
        sim = self.pepper.get_all_tasks('simulation')
        for task in sim:
            revision_max = gazu.files.get_last_working_file_revision(task)['revision']
            path = gazu.files.build_working_file_path(task, revision=revision_max)
            print(path)

    def test_get_task_paths(self):
        self.pepper.project = 'pepper'
        self.pepper.get_all_working_paths_for_task_type('simulation', 'hou')

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
        _, task = self.pepper.get_task(task_type_name)
        pre_revision = gazu.files.get_last_working_file_revision(task).get('revision')
        self.pepper.publish_working_file(task_type_name, software_name)

        # 함수를 짤 때,
        # _, task = self.pepper.get_task(task_type_name)
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
        task_type, task = self.pepper.get_task(task_type_name)
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        pre_revision = gazu.files.get_last_entity_output_revision(self.pepper.entity, output_type, task_type, name='main')
        task_type, task = self.pepper.get_task(task_type_name)

        self.pepper.publish_output_file(task_type_name, output_type_name, comments)

        # 함수를 짤 때,
        # task_type, task = self.pepper.get_task(task_type_name)
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
        _, task = self.pepper.get_task(task_type_name)
        path = self.pepper.working_file_path(task_type_name, software_name, input_num)

        # 함수를 짤 때,
        # _, task = self.pepper.get_task(task_type_name)
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
        _, task = self.pepper.get_task(task_type_name)
        path = self.pepper.make_next_working_path(task_type_name)

        # 함수를 짤 때,
        # _, task = self.pepper.get_task(task_type_name)
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
        _, task = self.pepper.get_task(task_type_name)
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
        assert False
    
    def test_get_task(self):
        assert False
    
    def test_get_software(self):
        assert False

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












    # def test_get_task_status(self):
    #     self.h.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")
    #     self.h.project = 'pepper'
        # sim = gazu.task.get_task_type_by_name('simulation')

        # -------------------------------------------
        # 뭐 테스트했더라...........................

        # tasks = []
        # assets = gazu.task.all_tasks_for_project(self.h.project)
        # for asset in assets:
        #     tasks.append(asset['task_type_id'])
        # print(tasks)
        # ttt = list(set(tasks))
        # taskfolder = []
        # for i in ttt:
        #     task = gazu.task.get_task_type(i)
        #     at = gazu.task.all_tasks_for_task_type(self.h.project, task)
        #     # print(at)
        #     for task in at:
        #         if type(task) is list:
        #             for tt in task:
        #                 taskfolder.append(tt)
        #         else:
        #             taskfolder.append(task)
        # for task in taskfolder:
        #     print(task)
        #     wkf = gazu.files.get_working_files_for_task(task)
        #     print(wkf)
        # self.h.asset = 'GROOT'
        # aa = gazu.asset.all_assets_for_project(self.h.project)
        # for a in aa:
        #     print(a)
        # a = self.h.get_task_paths('modeling', 'maya')

        # ----------------------------------------------------------
        # 어셋별로 워킹파일 생성 테스트

        # ap = gazu.asset.all_assets_for_project(self.h.project)
        # for asset in ap:
        #     self.h.asset = asset['name']
        #     self.h.entity = 'asset'
        #     self.h.publish_working_file('simulation', 'hounc')

        # ---------------------------------------------------------

        # aaaa = gazu.task.get_task_type_by_name('simulation')
        # print(aaaa)
    # def test_project(self):
    #     self.h.project = 'pepper'
    #
    # def test_sequence(self):
    #     self.h.project = 'pepper'
    #     self.h.sequence = 'SQ01'
    #
    # def test_shot(self):
    #     self.h.project = 'pepper'
    #     self.h.sequence = 'SQ01'
    #     self.h.shot = '0010'
    #
    # def test_asset(self):
    #     self.h.project = 'pepper'
    #     self.h.asset = 'template_01'

    # def test_entity(self):
    #     assert False
    #
    # def test_check_dict(self):
    #     assert False

    # def test_file_tree(self):
    #     self.h.project = 'pepper'
    #     self.h.set_file_tree('mnt/project', 'hook')
    #
    # def test_asset_types(self):
    #     assert False
    #
    # def test_task_types(self):
    #     assert False
    #
    # def test_add_task_to_entity(self):
    #     assert False
    #
    # def test_new_asset_type(self):
    #     assert False
    #
    # def test_publish_working_file(self):
    #     self.h.project = 'chopsticks'
    #     self.h.asset = 'kitchen'
    #     self.h.entity = 'asset'
    #     # print(gazu.files.get_software_by_name('maya'))
    #     self.h.publish_working_file('modeling', 'main', 'maya')
    #
    # def test_publish_output_file(self):
    #     assert False
    #
    # def test_working_file_path(self):
    #     assert False
    #
    # def test_make_next_working_path(self):
    #     assert False
    #
    # def test_output_file_path(self):
    #     assert False
    #
    # def test_make_next_output_path(self):
    #     assert False
    #
    # def test_get_revision_num(self):
    #     assert False
    #
    # def test_get_task(self):
    #     assert False
    #
    # def test_get_software(self):
    #     assert False
    #
    # def test_casting_create(self):
    #     assert False
    #
    # def test_casting_delete(self):
    #     assert False
    #
    # def test_get_casting_path_for_asset(self):
    #     assert False
