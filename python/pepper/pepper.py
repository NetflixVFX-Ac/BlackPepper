import gazu


class Houpub:
    _project = None
    _sequence = None
    _shot = None
    _asset = None
    _entity = None

    def __init__(self):
        # self._id = None
        pass

    def login(self, host, identify, password):
        gazu.client.set_host(host)
        gazu.log_in(identify, password)
        # self.identif = identify

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, proj_name):
        self.args_str_check(proj_name)
        self._project = gazu.project.get_project_by_name(proj_name)
        self.dict_check(self.project, 'none')

    @property
    def sequence(self):
        return self._sequence

    @sequence.setter
    def sequence(self, seq_name):
        self.dict_check(self.project, 'no_project')
        self.args_str_check(seq_name)
        self._sequence = gazu.shot.get_sequence_by_name(self.project, seq_name)
        self.dict_check(self.sequence, 'none')

    @property
    def shot(self):
        return self._shot

    @shot.setter
    def shot(self, shot_name):
        self.dict_check(self.sequence, 'no_sequence')
        self.args_str_check(shot_name)
        self._shot = gazu.shot.get_shot_by_name(self.sequence, shot_name)
        self.dict_check(self.shot, 'none')

    @property
    def asset(self):
        return self._asset

    @asset.setter
    def asset(self, asset_name):
        self.dict_check(self.project, 'no_project')
        self._asset = gazu.asset.get_asset_by_name(self.project, asset_name)
        self.dict_check(self.asset, 'none')

    @property
    def entity(self):
        return self._entity

    @entity.setter
    def entity(self, ent):
        if ent == 'asset':
            self.dict_check(self.asset, 'no_asset')
            self._entity = self._asset
        if ent == 'shot':
            self.dict_check(self.shot, 'no_')
            self._entity = self._shot
        else:
            self.error('not_asset_shot')

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
        self.dict_check(self.project, 'no_project')
        gazu.files.update_project_file_tree(self.project, file_tree)

    def publish_working_file(self, task_type_name, software_name):
        """get_task 함수로 task_type(dict) 과 task(dict) 중 task를 받고
        software(dict)도 사용하여  새로운 working file(revision +1) 을 만든다. \n
        Create a new 'working file' with 'task_type' and 'task' corresponding to
        the specified entity and the selected software name.

        Example:
            publish_working_file("simulation", "hou") \n
            need self parameter : project,asset,entity or project,seq,shot,entity

        Args:
            task_type_name(str):
            software_name(str):
        """
        self.args_str_check(task_type_name, software_name)
        _, task = self.get_task(task_type_name)
        software = self.get_software(software_name)
        gazu.files.new_working_file(task, software=software)

    def publish_output_file(self, task_type_name, output_type_name, comments):
        """
        Create a new 'outputfile' in kitzu with 'task_type', 'task' and 'output_type'
        corresponding to the specified entity.

        Example:
            publish_output_file('FX', 'Movie_file', "test") \n
            need self parameter : project,asset,entity or project,seq,shot,entity \n
            task_type_name 으로  task_type(dict),task(dict)를 get \n
            last working file(dict) get \n
            output_type_name 으로 output type을 가져온다

        Args:
            task_type_name(str):
            output_type_name(str):
            comments(str):
        """
        self.args_str_check(task_type_name, output_type_name, comments)
        task_type, task = self.get_task(task_type_name)
        self.dict_check(task_type, 'no_task_type')
        work_file = gazu.files.get_last_working_file_revision(task)
        self.dict_check(work_file, 'no_work_file')
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        gazu.files.new_entity_output_file(self.entity, output_type, task_type, working_file=work_file,
                                          representation=output_type['short_name'], comment=comments)

    def working_file_path(self, task_type_name, software_name, input_num):
        """revision = (intput_num < last revision) \n
        input num 이 크면 last revision 을 반환, 작으면 input_num 반환 \n
        The working file is created by adding 'ext' to the desired local path with the desired revision.

        Example:
            working_file_path("simulation", "hou", 10) \n
            need self parameter : project,asset,entity or project,seq,shot,entity

        Args:
            task_type_name(str):
            software_name(str):
            input_num(int): 받고 싶은 path의 revision number

        Returns:
            working file path(str)

        """
        self.args_str_check(task_type_name, software_name)
        _, task = self.get_task(task_type_name)
        software = self.get_software(software_name)
        revision_max = gazu.files.get_last_working_file_revision(task).get('revision', self.error('no_work_file'))
        # 여기서 working file revision이 없을 경우의 에러핸들링 필요함. 메소드를 수정해야 할 수도 있음
        revision_num = self.get_revision_num(revision_max, input_num)
        path = gazu.files.build_working_file_path(task, software=software, revision=revision_num)
        ext = software['file_extension']
        return path + '.' + ext

    def make_next_working_path(self, task_type_name):
        """working file path revision +1 된 path 를 리턴한다. \n
        Make the next version of the working file in the latest revision local path.

        Example:
            make_next_working_path("simulation") \n
            need self parameter : project,asset,entity or project,seq,shot,entity

        Args:
            task_type_name(str):

        Returns:
            (path) working file revision +1 된 path
        """
        self.args_str_check(task_type_name)
        _, task = self.get_task(task_type_name)
        self.dict_check(task, 'no_task_in_entity')
        revision_max = gazu.files.get_last_working_file_revision(task)['revision']
        # 여기서 working file revision이 없을 경우의 에러핸들링 필요함. 메소드를 수정해야 할 수도 있음
        path = gazu.files.build_working_file_path(task, revision=revision_max + 1)
        return path

    def output_file_path(self, output_type_name, task_type_name, input_num):
        """revision = (intput_num < last revision) \n
        input num 이 크면 last revision 을 반환, 작으면 input_num 반환 \n
        Call up 'output_type_name', 'task_type_name', 'input_num'. A file path combined with 'ext' is created with
        'revision_num' to local path that matches 'input_num' on the specified 'entity'.

        Example:
            output_file_path('Movie_file', 'FX', 4) \n
            need self parameter : project,asset,entity or project,seq,shot,entity

        Args:
            output_type_name(str):
            task_type_name(str):
            input_num(int): 받고 싶은 path의 revision number

        Returns:
            working file path(str)
도
        """
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        self.dict_check(task_type, 'no_task_type')
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        self.dict_check(output_type, 'no_output_type')
        revision_max = gazu.files.get_last_entity_output_revision(self.entity, output_type, task_type, name='main')
        # 여기서 working file revision이 없을 경우의 에러핸들링 필요함. 메소드를 수정해야 할 수도 있음도
        revision_num = self.get_revision_num(revision_max, input_num)
        path = gazu.files.build_entity_output_file_path(self.entity, output_type, task_type, revision=revision_num)
        ext = output_type['short_name']
        return path + '.' + ext

    def make_next_output_path(self, output_type_name, task_type_name):
        """output file path revision +1 된 path 를 리턴한다. \n
        Call up 'output_type_name', 'task_type_name'. A file path combined with 'ext' is created with last
        'revision_num' specified 'entity'.

        Example:
            make_next_output_path('Movie_file', 'FX') \n
            need self parameter : project,asset,entity or project,seq,shot,entity

        Args:
            output_type_name(str):
            task_type_name(str):

        Returns:
            output file revision +1 된  path

        """
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        self.dict_check(task_type, 'no_task_type')
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        self.dict_check(output_type, 'no_output_type')
        revision_max = gazu.files.get_last_entity_output_revision(self.entity, output_type, task_type, name='main')
        # 여기서 working file revision이 없을 경우의 에러핸들링 필요함. 메소드를 수정해야 할 수도 있음도
        path = gazu.files.build_entity_output_file_path(self.entity, output_type, task_type, revision=revision_max + 1)
        ext = output_type['short_name']
        return path + '.' + ext

    def get_revision_num(self, revision_max, input_num):
        """
        Example:
            input_num이 None일시 revision_max, input_num이 정수가 아닐 시 raise, input_num이 revision_max보다 클 시
            revision_max 반환, input_num이 revision_max보다 작을 시 input_num 반환

        Args:
            revision_max(int):
            input_num(int):

        Returns:
            input num 이 크면 last revision 을 반환, 작으면 input_num 반환
        """
        if input_num is None:
            return revision_max
        self.int_check(input_num)
        if revision_max < input_num:
            return revision_max
        else:
            return input_num

    def get_task(self, task_type_name):
        """task_type_name을 통해 task_type와 task를 받아온다.

        Example:
            get_task("FX")
            need self parameter : project,asset,entity or project,seq,shot,entity

        Args:
            task_type_name: string

        Returns:
            task_type, task

        """
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        self.dict_check(task_type, 'no_task')
        task = gazu.task.get_task_by_name(self.entity, task_type)
        self.dict_check(task, 'no_task_in_entity')
        return task_type, task

    def get_software(self, software_name):
        """houdini 관련 3가지 software 만 받고 뱉어준다.

        Args:
            software_name(str):

        Returns:
            (dict) Software object corresponding to given name.
        """
        if software_name == 'hou':
            return gazu.files.get_software_by_name('houdini')
        if software_name == 'hounc':
            return gazu.files.get_software_by_name('houdininc')
        if software_name == 'houlc':
            return gazu.files.get_software_by_name('houdinilc')
        else:
            self.error('hou')

    def get_casting_path_for_asset(self):  # 에러핸들링 해야함
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
                    
    def dict_check(self, test_dict, code):
        if test_dict is None:
            self.error(code)
        else:
            return test_dict

    def args_str_check(self, *args):
        if type(args) is tuple:
            str_confirms = ','.join(args)
            for str_confirm in str_confirms:
                self.str_check(str_confirm)
            return str_confirms
        else:
            self.str_check(args)
            return args

    def str_check(self, strn):
        if type(strn) is not str:
            self.error("not_string")
        else:
            return strn

    def int_check(self, num):
        if type(num) is not int:
            self.error('not_int')
        else:
            return num

    @staticmethod
    def error(code):
        if code == 'not_string':
            raise ValueError("Input must be string")
        if code == 'not_int':
            raise ValueError("Input must be integer.")
        if code == 'none':
            raise ValueError("There is no dict")
        if code == 'hou':
            raise ValueError("Software input must be hou, hounc, or houlc.")
        if code == 'no_task':
            raise ValueError("There's no task in entity.")
        if code == 'no_project':
            raise NameError("No project is assigned.")
        if code == 'no_sequence':
            raise NameError("No sequence is assigned.")
        if code == 'no_shot':
            raise NameError("No shot is assigned.")
        if code == 'no_asset':
            raise NameError("No asset is assigned.")
        if code == 'no_work_file':
            raise NameError("")
        if code == 'no_output_file':
            raise NameError("")
        if code == 'not_asset_shot':
            raise NameError("")
        if 'no_task_type' in code:
            raise NameError(f"There's no task type named '{code[11:]}")
        if 'no_output_type' in code:
            raise NameError(f"There's no output type named '{code[11:]}")
            
    def print_get_all_info(self, select):
        if select == 'project' and self.project is not None:
            print(self.project['name'])
        if select == 'project' and self.project is None:
            for proj in gazu.project.all_open_projects():
                print(proj['name'])
        if select == 'sequence' and self.sequence is not None:
            print(self.sequence['name'])
        if select == 'sequence' and self.sequence is None:
            for seq in gazu.shot.all_sequences_for_project(self.project):
                print(seq['name'])
        if select == 'shot' and self.shot is not None:
            print(self.shot['name'])
        if select == 'shot' and self.shot is None:
            for st in gazu.shot.all_shots_for_sequence(self.sequence):
                print(st['name'])
        if select == 'asset' and self.asset is not None:
            print(self.asset['name'])
        if select == 'asset' and self.asset is None:
            for asse in gazu.asset.all_asset_types_for_project(self.project):
                print(asse['name'])
        if select == 'asset_task_type' and self.asset is not None:
            for task_type in gazu.task.all_task_types_for_asset(self.asset):
                print(task_type['name'])
        if select == 'shot_task_type' and self.shot is not None:
            for task_type in gazu.task.all_task_types_for_shot(self.shot):
                print(task_type['name'])
        if select == 'casting' and self.shot is not None:
            casting = gazu.casting.get_shot_casting(self.shot)
            for cast in casting:
                print(cast['asset_type_name'] + " : " + cast['asset_name'])
        if type(select) != str:
            raise ValueError('Write down as string')
        list_element = ['project', 'sequence', 'shot', 'asset', 'asset_task_type', 'shot_task_type', 'casting']
        if select not in list_element:
            print('[Select from the list below]')
            for element in list_element:
                print(f"'{element}'")
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

    # ----------asset type & task type-----------

    # @property
    # def asset_types(self):
    #     return self._asset_types
    #
    # @asset_types.setter
    # def asset_types(self, *args):
    #     self._asset_types = [*args]
    #
    # @property
    # def task_types(self):
    #     return self._task_types
    #
    # @task_types.setter
    # def task_types(self, *args):
    #     self._task_types = [*args]
    #
    # def add_task_to_entity(self, task_type_name):
    #     task_type = gazu.task.get_task_type_by_name(task_type_name)
    #     if task_type is None:
    #         return
    #     gazu.task.new_task(self.entity, task_type)
    #
    # @staticmethod
    # def new_asset_type(asset_type_name):
    #     gazu.asset.new_asset_type(asset_type_name)

    # ----------casting----------

    # def casting_multiple_assets(self, *args):
    #     asset_castings = gazu.casting.get_shot_casting(self.shot)
    #     for asset_name in args:
    #         asset = gazu.asset.get_asset_by_name(self.project, asset_name)
    #         new_casting = {"asset_id": asset['id'], "nb_occurences": 1}
    #         asset_castings.append(new_casting)
    #     gazu.casting.update_shot_casting(self.project, self.shot, casting=asset_castings)
    #
    # def casting_create(self, nb):
    #     asset_castings = gazu.casting.get_shot_casting(self.shot)
    #     new_casting = {"asset_id": self.asset['id'], "nb_occurences": nb}
    #     asset_castings.append(new_casting)
    #     gazu.casting.update_shot_casting(self.project, self.shot, casting=asset_castings)
    #
    # def casting_delete(self):
    #     asset_name = self.asset['name']
    #     asset_castings = gazu.casting.get_shot_casting(self.shot)
    #     filtered_assets = [asset for asset in asset_castings if asset_name != asset['asset_name']]
    #     gazu.casting.update_shot_casting(self.project, self.shot, casting=filtered_assets)

    # @staticmethod
    # def check_task_status(task):
    #     if gazu.task.get_task_status(task['task_status']) == 'done':
    #         return task
    #     else:
    #         pass

    # ----------get all tasks-----------

    # def get_all_tasks(self, task_type_name):
    #     task_type = gazu.task.get_task_type_by_name(task_type_name)
    #     task_status = gazu.task.get_task_status_by_name("done")
    #     all_tasks = gazu.task.all_tasks_for_task_status(self.project, task_type, task_status)
    #     return all_tasks
    #
    # def get_all_working_paths_for_task_type(self, task_type_name, software_name):
    #     tasks = self.get_all_tasks(task_type_name)
    #     ext = self.get_software(software_name)['file_extension']
    #     paths = []
    #     for task in tasks:
    #         if task['task_status_id'] == gazu.task.get_task_status_by_name('Done')['id']:
    #             working = gazu.files.get_last_working_file_revision(task)
    #             paths.append(working['path'] + '.' + ext)
    #     return paths


# a = Houpub()
# a.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")
# a.project = 'pepper'
# a.project = 'hoon'
# a.project = 'pepper'
# b = a.get_all_tasks('FX Template')
# for i in b:
#     print(i)
# c = b[0]['task_status_id']
# d = gazu.task.get_task_status(c)
# print(d)
# a.set_file_tree('/mnt/project', 'hook')
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
