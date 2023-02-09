import gazu
import os


class Houpub:
    _project = None
    _sequence = None
    _shot = None
    _asset = None
    _entity = None
    _asset_types = None
    _task_types = None
    # _host = None
    # _identify = None

    def __init__(self):
        pass
        # gazu.client.set_host("http://192.168.3.116/api")
        # gazu.log_in("pipeline@rapa.org", "netflixacademy")

    @staticmethod
    def login(host, identification, password):
        gazu.client.set_host(host)
        gazu.log_in(identification, password)

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, proj_name):
        self._project = gazu.project.get_project_by_name(proj_name)
        self.check_dict(self.project)

    @property
    def sequence(self):
        return self._sequence

    @sequence.setter
    def sequence(self, seq_name):
        if self.project is None:
            return
        self._sequence = gazu.shot.get_sequence_by_name(self.project, seq_name)
        self.check_dict(self.sequence)

    @property
    def shot(self):
        return self._shot

    @shot.setter
    def shot(self, shot_name):
        if self.sequence is None:
            return
        self._shot = gazu.shot.get_shot_by_name(self.sequence, shot_name)
        self.check_dict(self.shot)

    @property
    def asset(self):
        return self._asset

    @asset.setter
    def asset(self, asset_name):
        if self.project is None:
            return
        self._asset = gazu.asset.get_asset_by_name(self.project, asset_name)
        if self.asset is not None:
            print(f"asset Set : {self.asset['name']}")
        else:
            print("Error")

    @property
    def entity(self):
        return self._entity

    @entity.setter
    def entity(self, ent):
        if ent == 'asset':
            self._entity = self._asset
        if ent == 'shot':
            self._entity = self._shot

    @staticmethod
    def check_dict(exp_dict):
        if exp_dict is not None:
            print(f"{exp_dict['type']} set : {exp_dict['name']}")
        else:
            print("Wrong input")

    def set_file_tree(self, mount_point, root):
        file_tree = {
            "working": {
                "mountpoint": mount_point,
                "root": root,
                "folder_path": {
                    "shot": "<Project>/shots/<Sequence>/<Shot>/<TaskType>/working/v<Revision>",
                    "asset": "<Project>/assets/<AssetType>/<Asset>/<TaskType>/working/v<Revision>",
                    "style": "lowercase"
                },
                "file_name": {
                    "shot": "<Project>_<Sequence>_<Shot>_<TaskType>_<Revision>",
                    "asset": "<Project>_<AssetType>_<Asset>_<TaskType>_<Revision>",
                    "style": "lowercase"
                }
            },
            "output": {
                "mountpoint": mount_point,
                "root": root,
                "folder_path": {
                    "shot": "<Project>/shots/<Sequence>/<Shot>/<TaskType>/output/<OutputType>/v<Revision>",
                    "asset": "<Project>/assets/<AssetType>/<Asset>/<TaskType>/output/<OutputType>/v<Revision>",
                    "style": "lowercase"
                },
                "file_name": {
                    "shot": "<Project>_<Sequence>_<Shot>_<OutputType>_v<Revision>",
                    "asset": "<Project>_<AssetType>_<Asset>_<OutputType>_v<Revision>",
                    "style": "lowercase"
                }
            },
            "preview": {
                "mountpoint": mount_point,
                "root": root,
                "folder_path": {
                    "shot": "<Project>/shots/<Sequence>/<Shot>/<TaskType>/output/<OutputType>/v<Revision>/preview",
                    "asset": "<Project>/assets/<AssetType>/<Asset>/<TaskType>/output/<OutputType>/v<Revision>/preview",
                    "style": "lowercase"
                },
                "file_name": {
                    "shot": "<Project>_<Sequence>_<Shot>_<OutputType>_v<Revision>",
                    "asset": "<Project>_<AssetType>_<Asset>_<OutputType>_v<Revision>",
                    "style": "lowercase"
                }
            }
        }
        gazu.files.update_project_file_tree(self.project, file_tree)

    @property
    def asset_types(self):
        return self._asset_types

    @asset_types.setter
    def asset_types(self, *args):
        self._asset_types = [*args]

    @property
    def task_types(self):
        return self._task_types

    @task_types.setter
    def task_types(self, *args):
        self._task_types = [*args]

    def add_task_to_entity(self, task_type_name):
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        if task_type is None:
            return
        gazu.task.new_task(self.entity, task_type)

    @staticmethod
    def new_asset_type(asset_type_name):
        gazu.asset.new_asset_type(asset_type_name)

    def publish_working_file(self, task_type_name, software_name):
        _, task = self.get_task(task_type_name)
        software = self.get_software(software_name)
        gazu.files.new_working_file(task, software=software)

    def publish_output_file(self, task_type_name, output_type_name, comments):
        task_type, task = self.get_task(task_type_name)
        work_file = gazu.files.get_last_working_file_revision(task)
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        gazu.files.new_entity_output_file(self.entity, output_type, task_type, working_file=work_file,
                                          representation=output_type['short_name'], comment=comments)

    def working_file_path(self, task_type_name, software_name, input_num):
        _, task = self.get_task(task_type_name)
        software = self.get_software(software_name)
        revision_max = gazu.files.get_last_working_file_revision(task)['revision']
        revision_num = self.get_revision_num(revision_max, input_num)
        path = gazu.files.build_working_file_path(task, software=software, revision=revision_num)
        ext = software['file_extension']
        return path + '.' + ext

    def make_next_working_path(self, task_type_name):
        _, task = self.get_task(task_type_name)
        revision_max = gazu.files.get_last_working_file_revision(task)['revision']
        path = gazu.files.build_working_file_path(task, revision=revision_max + 1)
        return path

    def output_file_path(self, output_type_name, task_type_name, input_num):
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        revision_max = gazu.files.get_last_entity_output_revision(self.entity, output_type, task_type, name='main')
        revision_num = self.get_revision_num(revision_max, input_num)
        path = gazu.files.build_entity_output_file_path(self.entity, output_type, task_type, revision=revision_num)
        ext = output_type['short_name']
        return path + '.' + ext

    def make_next_output_path(self, output_type_name, task_type_name):
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        revision_max = gazu.files.get_last_entity_output_revision(self.entity, output_type, task_type, name='main')
        path = gazu.files.build_entity_output_file_path(self.entity, output_type, task_type, revision=revision_max + 1)
        ext = output_type['short_name']
        return path + '.' + ext

    @staticmethod
    def get_revision_num(revision_max, input_num):
        if input_num is None:
            return revision_max
        if type(input_num) is not int:
            raise
        if revision_max < input_num:
            return revision_max
        else:
            return input_num

    def get_task(self, task_type_name):
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        if task_type is None:
            return
        task = gazu.task.get_task_by_name(self.entity, task_type)
        return task_type, task

    @staticmethod
    def get_software(software_name):
        if software_name not in ['hou', 'hounc', 'houlc']:
            return gazu.files.get_software_by_name('houdini')
        if software_name == 'hou':
            return gazu.files.get_software_by_name('houdini')
        if software_name == 'hounc':
            return gazu.files.get_software_by_name('houdininc')
        if software_name == 'houlc':
            return gazu.files.get_software_by_name('houdinilc')

    def casting_multiple_assets(self, *args):
        asset_castings = gazu.casting.get_shot_casting(self.shot)
        for asset_name in args:
            asset = gazu.asset.get_asset_by_name(self.project, asset_name)
            new_casting = {"asset_id": asset['id'], "nb_occurences": 1}
            asset_castings.append(new_casting)
        gazu.casting.update_shot_casting(self.project, self.shot, casting=asset_castings)

    def casting_create(self, nb):
        asset_castings = gazu.casting.get_shot_casting(self.shot)
        new_casting = {"asset_id": self.asset['id'], "nb_occurences": nb}
        asset_castings.append(new_casting)
        gazu.casting.update_shot_casting(self.project, self.shot, casting=asset_castings)

    def casting_delete(self):
        asset_name = self.asset['name']
        asset_castings = gazu.casting.get_shot_casting(self.shot)
        filtered_assets = [asset for asset in asset_castings if asset_name != asset['asset_name']]
        gazu.casting.update_shot_casting(self.project, self.shot, casting=filtered_assets)

    def get_casting_path_for_asset(self):
        cast_in = gazu.casting.get_asset_cast_in(self.asset)
        for shot in cast_in:
            print(f'sequence name  : {shot.get("sequence_name")} \n'
                  f'shot name      : {shot.get("shot_name")}')
            tasks = gazu.task.all_tasks_for_shot(shot.get('shot_id'))
            for task in tasks:
                last_revision = gazu.files.get_last_working_file_revision(task)
                print(last_revision)
                if last_revision is None:
                    print("None")

    @staticmethod
    def check_task_status(task):
        if gazu.task.get_task_status(task['task_status']) == 'done':
            return task
        else:
            pass

    def get_all_tasks(self, task_type_name):
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        task_status = gazu.task.get_task_status_by_name("done")
        all_tasks = gazu.task.all_tasks_for_task_status(self.project, task_type, task_status)
        return all_tasks

    def get_task_paths(self, task_type_name, software_name): # 작업중임 테스트 ㄴㄴ
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        task_status = gazu.task.get_task_status_by_name("done")
        tasks = gazu.task.all_tasks_for_task_status(self.project, task_type, task_status)
        software = self.get_software(software_name)
        paths = []
        print(tasks)
        # for task in tasks:
        #     revision_max = gazu.files.get_last_working_file_revision(task)
        #     print(revision_max)
            # path = gazu.files.build_working_file_path(task, software=software, revision=revision_max)
            # ext = software['file_extension']
            # paths.append(path + '.' + ext)
        # return paths

    # -----------Unused methods----------

    # -----Login-----

    # @property
    # def host(self):
    #     return self._host

    # @host.setter
    # def host(self, path):
    #     self._host = path

    # @property
    # def identify(self):
    #     return self._identify

    # @identify.setter
    # def identify(self, id_pw):
    #     self._identify = id_pw

    # def login(self):
    #     gazu.client.set_host(self.host)
    #     gazu.log_in(self.identify[0], self.identify[1])

    # -----Making new entities-----

    # def new_project(self, proj_name):
    #     if gazu.project.get_project_by_name(proj_name) is None:
    #         gazu.project.new_project(proj_name, asset_types=self._asset_types, task_types=self._task_types)

    # def new_sequence(self, seq_name):
    #     if gazu.shot.get_sequence_by_name(self.project, seq_name) is None:
    #         gazu.shot.new_sequence(self.project, seq_name)

    # def new_shot(self, shot_name):
    #     if gazu.entity.get_entity_by_name(shot_name) is None:
    #         gazu.shot.new_shot(self.project, self.sequence, shot_name)

    # def new_asset(self, asset_name, asset_type_name):
    #     asset_type = gazu.asset.get_asset_type_by_name(asset_type_name)
    #     if asset_type is None:
    #         return
    #     if gazu.asset.get_asset_by_name(self.project, asset_name, asset_type) is None:
    #         gazu.asset.new_asset(self.project, asset_type, asset_name)

    # -----Making local directories-----

    # def make_working_dirs(self):
    #     for shot in gazu.shot.all_shots_for_project(self.project):
    #         for task in gazu.task.all_tasks_for_shot(shot):
    #             working_file_path = os.path.dirname(
    #                 gazu.files.build_working_file_path(task)
    #             )
    #             rev = self.get_revision(task)
    #             for rev in range(1, rev + 1):
    #                 rev_path = os.path.join(working_file_path, f'v{rev:03}')
    #                 self.make_dirs(rev_path)

    # def make_output_dirs(self, task_type, output_type):
    #     task_type = gazu.task.get_task_type_by_name(task_type)
    #     output_type = gazu.files.get_output_type_by_name(output_type)
        # gazu.entity.get_entity_by_name(shot)
        # a = gazu.files.build_entity_output_file_path(self.entity, output_type, task_type)
        # print(a)

    # @staticmethod
    # def make_dirs(dir_path):
    #     if os.path.exists(dir_path):
    #         print("Path exists", dir_path)
    #         pass
    #     else:
    #         print("Path made", dir_path)
    #         os.makedirs(dir_path)

    # @staticmethod
    #     def find_shot(dirs, inp):
    #         for arg in dirs:
    #             if arg['name'] == inp:
    #                 return inp
    #             else:
    #                 pass
    #         raise

    # -----Download & uplaad-----

    # def upload_working_file(self, task_type_name, path):
    #     _, task = self.get_task(task_type_name)
    #     working_file = gazu.files.get_last_working_file_revision(task)
    #     gazu.files.upload_working_file(working_file, path)

    # def download_working_file(self, task_type_name, path):
    #     _, task = self.get_task(task_type_name)
    #     working = gazu.files.get_last_working_file_revision(task)
    #     filename = working['path'].split(os.sep)[-1:][0]
    #     gazu.files.download_working_file(working, file_path=os.path.join(path, filename))


a = Houpub()
a.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")
# a.project = 'pepper'
# a.project = 'hoon'
a.project = 'aatest_03'
b = a.get_all_tasks('FX Template')
for i in b:
    print(i)
# c = b[0]['task_status_id']
# d = gazu.task.get_task_status(c)
# print(d)
# a.set_file_tree = '/mnt/project', 'hook'
# a.sequence = 'SQ01'
# a.shot = '0010'
# a.asset = 'GROOT'
# a.entity = 'asset'
# a.casting_create(1)
# a.casting_delete()
# a.get_casting_path_for_asset()
# a.sequence = 'SQ01'
# a.shot = '0030'
# a.entity = 'shot'
# a.get_casting_path_for_shot()
# a.working_file_path('FX', 'fx_template', 'fx_temp_precomp', 'houdini')
# a.output_file_path()
