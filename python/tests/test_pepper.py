from unittest import TestCase
import gazu
from pepper import Houpub


class test_Houpub(TestCase):
    def setUp(self):
        self.h = Houpub()
        self.h.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")

    def test_casting_multiple_assets(self):
        self.h.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")
        self.h.project = 'pepper'
        sim = self.h.get_all_tasks('simulation')
        for task in sim:
            revision_max = gazu.files.get_last_working_file_revision(task)['revision']
            path = gazu.files.build_working_file_path(task, revision=revision_max)
            print(path)

    def test_get_task_paths(self):
        self.h.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")
        self.h.project = 'pepper'
        self.h.get_all_working_paths_for_task_type('simulation', 'hou')

    # def test_working_file_path(self):
        # self.h.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")
        # self.h.project = 'pepper'
        # self.h.asset = 'temp_fire'
        # self.h.entity = 'asset'
        # path = self.h.working_file_path('simulation', 'hou', 2)
        # print(path)


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
