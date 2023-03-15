import gazu
from BlackPepper.log.moduler_log import Logger


class Houpub:
    """
     이 모듈은 kitsu에 올라간 정보를 gazu를 통해서 path를 추출한다. 그 정보는 local에 저장된 houdini template에 working file path로
    지정한 경로에서 cam, asset 파일을 기존 working hip파일에 적용한다. 부가적으로 shots마다 cating된 template를 확인 할 수 있다.
     예를 들어, test_01.hip의 working file template에 cam, asset을 적용해서 새로운 jpg, hip, mov를 outputfile로 만든다.
    hip파일의 경우는 test_02.hip이라는 형식으로 outputfile이자 새로운 revision의 working file을 만든다.
    """
    _project = None
    _sequence = None
    _shot = None
    _asset = None
    _entity = None
    _software = None

    def __init__(self):
        self.identif = None
        self.user = None
        self.mylog = Logger()
        pass

    def login(self, host, identify, password):
        """Host를 지정해주고, identify와 password 를 이용해 로그인 하는 방식. \n
        유저 id는 self.identif에 저장해 logging이 가능하게 한다.

        Examples:
            pepper.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")

        Args:
            host(str): host url
            identify(str): user id
            password(str): user password

        Raises:
            ConnectionError: Host ip에 다른 값이 있을 때
            ServerErrorException: Host의 주소가 맞지 않을 때
            AuthFailedException: id나 password가 맞지 않을 때
        """
        gazu.client.set_host(host)
        self.user = gazu.log_in(identify, password)
        self.identif = identify
        self.mylog.set_logger(self.identif)

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, proj_name):
        """입력한 project 이름과 동일한 이름을 가진 project의 dict를 반환한다.

        Examples:
            pepper.project = 'BlackPepper'

        Args:
            proj_name(str): Project name

        Raises:
            Exception: If input is not string, or if there is no dict named 'project name'
        """
        self.args_str_check(proj_name)
        self._project = gazu.project.get_project_by_name(proj_name)
        self.dict_check(self.project, 'none')
        return

    @property
    def sequence(self):
        return self._sequence

    @sequence.setter
    def sequence(self, seq_name):
        """입력한 sequence 이름과 동일한 이름을 가진 sequence의 dict를 반환한다. \n
        self.project가 없을 시 작동하지 않는다.

        Examples:
            pepper.sequence = "SQ01"

        Args:
            seq_name(str) : Sequence name

        Raises:
            Exception: If self.project don't exist, if input is not string,
                and if there is no dict named 'sequence name'
        """
        self.dict_check(self.project, 'no_project')
        self.args_str_check(seq_name)
        self._sequence = gazu.shot.get_sequence_by_name(self.project, seq_name)
        self.dict_check(self.sequence, 'none')
        return

    @property
    def shot(self):
        return self._shot

    @shot.setter
    def shot(self, shot_name):
        """입력한 shot 이름과 동일한 이름을 가진 shot의 dict를 반환한다. \n
        self.project와 self.sequence가 없을 시 작동하지 않는다.

        Examples:
            pepper.shot = '0010'

        Args:
            shot_name(str): Shot name

        Raises:
            Exception: If self.project or self.sequence don't exist, if input is not string,
                or if there is no dict named 'shot name'
        """
        self.dict_check(self.sequence, 'no_sequence')
        self.args_str_check(shot_name)
        self._shot = gazu.shot.get_shot_by_name(self.sequence, shot_name)
        self.dict_check(self.shot, 'none')
        return

    @property
    def asset(self):
        return self._asset

    @asset.setter
    def asset(self, asset_name):
        """입력한 asset 이름과 동일한 이름을 가진 asset의 dict를 반환한다. \n
        self.project가 없을 시 작동하지 않는다.

        Examples:
            pepper.asset = 'temp_fire'

        Args:
            asset_name(str): Asset name

        Raises:
            Exception: If self.project don't exist, if input is not string, and if there is no dict named 'asset name'
        """
        self.dict_check(self.project, 'no_project')
        self._asset = gazu.asset.get_asset_by_name(self.project, asset_name)
        self.dict_check(self.asset, 'none')
        return

    @property
    def entity(self):
        return self._entity

    @entity.setter
    def entity(self, ent):
        """사용할 entity가 self.asset이 될지, self.shot이 될지 지정한다. \n
        asset 입력시 self.asset이 있어야 하고, shot 입력시 self.shot이 있어야 한다. 맞는 인자가 없을 시 작동하지 않는다.

        Examples:
            pepper.entity('asset') or BlackPepper.entity('shot')

        Args:
            ent(str): 'asset' or 'shot'

        Raises:
            Exception: If self.asset doesn't exist when ent is 'asset', if self.shot doesn't exist when ent is 'shot',
                and if ent is not 'asset' or 'shot'
        """
        if ent == 'asset':
            self.dict_check(self.asset, 'no_asset')
            self._entity = self._asset
            return
        if ent == 'shot':
            self.dict_check(self.shot, 'no_shot')
            self._entity = self._shot
            return
        self.error('not_asset_shot')

    @property
    def software(self):
        return self._software

    @software.setter
    def software(self, software_name):
        """houdini의 extension 타입별로 software dict를 반환해준다

        Example:
            pepper.software = 'hip'

        Args:
            software_name(str): 'hip', 'hipnc', or 'hiplc'

        Returns:
            Software dict

        Raises:
            Exception: If software_name is not hip, hipnc, or hiplc.
        """
        if software_name == 'hip':
            self._software = gazu.files.get_software_by_name('houdini')
            return
        if software_name == 'hipnc':
            self._software = gazu.files.get_software_by_name('houdininc')
            return
        if software_name == 'hiplc':
            self._software = gazu.files.get_software_by_name('houdinilc')
            return
        else:
            self.error('hou')

    def set_file_tree(self, mount_point, root):
        """self.project의 file tree를 업데이트 해준 뒤 file tree 변경 로그를 저장한다. \n
        self.project가 없을 시 작동하지 않는다.

        Examples:
            pepper.set_file_tree('mnt/projects', 'hook')

        Args:
            mount_point(str): Local mountpoint path
            root(str): Root directory for local kitsu path

        Raises:
            Exception: If self.project don't exist, and if input is not string that leads to local path
        """
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
        self.mylog.tree_log(self.project)

    def publish_working_file(self, task_type_name):
        """task_type_name과 self.entity를 통해 해당 entity의 입력된 task_type을 가진 task를 받아온다.\n
        받아온 task에 software_name에 해당하는 software을 사용해 작업한 working file을 생성하고, publish 한다. \n
        Publish가 될 때 마다 로그인한 유저의 id와 debug 메시지를 정해진 logger(log_pepper)에 따라 logging 한다. \n
        self.entity가 지정되어있지 않으면 작동하지 않는다.

        Example:
            publish_working_file('simulation')

        Args:
            task_type_name(str): 'simulation', 'layout', ...

        Raises:
            Exception: If self.entity doesn't exist, if self.entity has no task,
                if task_type_name and software_name is not string, and if task_type is None
        """
        self.args_str_check(task_type_name)
        _, task = self.get_task(task_type_name)
        gazu.files.new_working_file(task, software=self.software)
        self.mylog.publish_working_file_log(task_type_name)

    def publish_output_file(self, task_type_name, output_type_name, comments):
        """task_type_name과 output_type_name, self.entity를 통해 해당 entity의 입력된 task_type을 가진 task를 받아온다.\n
        받아온 task에 output_type_name에 맞는 output_type로 output file을 publish 한다. \n
        Publish가 될 때 마다 로그인한 유저의 id와 debug 메시지를 정해진 logger(log_pepper)에 따라 logging 한다. \n
        self.entity가 지정되어있지 않으면 작동하지 않는다.

        Example:
            publish_output_file('FX', 'Movie_file', "first_output")

        Args:
            task_type_name(str): 'FX', 'layout', ...
            output_type_name(str): 'Movie_file', 'mpeg-4', 'jpeg', ...
            comments(str): Short commetnt about output file

        Raises:
            Exception: If self.entity doesn't exist, if self.entity has no task, if self.entity has no working file,
                if task_type_name or output_type_name is not string, and if task_type or output_type is None
        """
        self.args_str_check(task_type_name, output_type_name, comments)
        task_type, task = self.get_task(task_type_name)
        self.dict_check(task_type, f'no_task_type{task_type_name}')
        work_file = gazu.files.get_last_working_file_revision(task)
        self.dict_check(work_file, 'no_work_file')
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        self.dict_check(task_type, f'no_task_type{output_type_name}')
        gazu.files.new_entity_output_file(self.entity, output_type, task_type, working_file=work_file,
                                          representation=output_type['short_name'], comment=comments)
        self.mylog.publish_output_file_log(task_type_name, output_type_name)

    def working_file_path(self, task_type_name, input_num=None):
        """self.entity에 해당된 task_type_name을 가진 task의 working file 중 input_num의 revision을 반환한다. \n

        Example:
            BlackPepper.working_file_path("simulation") or BlackPepper.working_file_path('layout', input_num=12)

        Args:
            task_type_name(str): 'simulation', 'FX', ...
            input_num(int): user's revision number

        Returns:
            working file path(revision=input_num)
        """
        self.args_str_check(task_type_name)
        _, task = self.get_task(task_type_name)
        revision_max = self.get_working_revision_max(task)
        revision_num = self.get_revision_num(revision_max, input_num)
        path = gazu.files.build_working_file_path(task, software=self.software, revision=revision_num)
        ext = self.software['file_extension']
        return path + '.' + ext

    def make_next_working_path(self, task_type_name):
        """self.entity에 해당된 task_type_name을 가진 task의 다음 working file path를 반환한다. \n
        input_num이 revision_max보다 크다면 revision_max를 반환하고, 아닐 시 input_num을 반환한다. \n
        input_num이 None일시 revision_max를 반환한다.

        Example:
            make_next_working_path("simulation")

        Args:
            task_type_name(str): 'simulation', 'FX', ...

        Returns:
            next working file path(revision + 1)

        Raises:
            Exception: If self.entity doesn't exist, if self.entity has no task. if task_type is None
        """
        self.args_str_check(task_type_name)
        _, task = self.get_task(task_type_name)
        self.dict_check(task, 'no_task_in_entity')
        last_working_file = gazu.files.get_last_working_file_revision(task)
        if last_working_file is None:
            revision_max = 0
        else:
            revision_max = self.get_working_revision_max(task)
        path = gazu.files.build_working_file_path(task, revision=revision_max + 1)
        return path

    def output_file_path(self, output_type_name, task_type_name, input_num=None):
        """self.entity에 해당된 task의 output_type중 output_type_name의 output file path 중 input_num의 revision을 반환한다.\n
        input_num이 revision_max보다 크다면 revision_max를 반환하고, 아닐 시 input_num을 반환한다. \n
        input_num이 None일시 revision_max를 반환한다.

        Example:
            output_file_path('Movie_file', 'FX', 4)

        Args:
            output_type_name(str): 'Movie_file', 'mpeg-4', 'jpeg', ...
            task_type_name(str): 'simulation', 'FX', ...
            input_num(int): user's revision number

        Returns:
            output file path(revision=input_num)

        Raises:
            Exception: If self.entity doesn't exist, if self.entity has no task, if self.entity has no working file,
                if task_type_name or output_type_name is not string, and if task_type or output_type is None
        """
        task_type, _ = self.get_task(task_type_name)
        self.dict_check(task_type, f'no_task_type{task_type_name}')
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        self.dict_check(output_type, f'no_output_type{output_type_name}')
        self.dict_check(self.entity, 'no_shot_asset')
        revision_max = gazu.files.get_last_entity_output_revision(self.entity, output_type, task_type, name='main')
        revision_num = self.get_revision_num(revision_max, input_num)
        path = gazu.files.build_entity_output_file_path(self.entity, output_type, task_type, revision=revision_num)
        ext = output_type['short_name']
        return path + '.' + ext

    def make_next_output_path(self, output_type_name, task_type_name):
        """self.entity에 해당된 task_type의 output_type중 output_file_name의 output file path를 반환한다.

        Example:
            make_next_output_path("Movie_file")

        Args:
            output_type_name(str): 'Movie_file', 'mpeg-4', 'jpeg', ...
            task_type_name(str): 'simulation', 'FX', ...

        Returns:
            next output file path(revision + 1)

        Raises:
            Exception: If self.entity doesn't exist, if self.entity has no task. if task_type is None
        """
        task_type, _ = self.get_task(task_type_name)
        self.dict_check(task_type, f'no_task_type{task_type_name}')
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        self.dict_check(output_type, f'no_output_type{output_type_name}')
        revision_max = gazu.files.get_last_entity_output_revision(self.entity, output_type, task_type, name='main')
        path = gazu.files.build_entity_output_file_path(self.entity, output_type, task_type, revision=revision_max + 1)
        return path

    def get_working_revision_max(self, task):
        """해당 task의 마지막 working file의 revision을 반환한다.

        Args:
            task: task dict

        Returns:
            last working file의 revision number(int)

        Raises:
            Exception: if task have no working file
        """
        last_working_file = gazu.files.get_last_working_file_revision(task)
        if last_working_file is None:
            self.error("no_work_file")
        return last_working_file['revision']

    def get_revision_num(self, revision_max, input_num):
        """working file이나 output file의 revision_max와 input_num을 비교한다. \n
        input_num이 revision_max보다 크다면 revision_max를 반환하고, 아닐 시 input_num을 반환한다. \n
        input_num이 None일시 revision_max를 반환한다.

        Example:
            pepper.get_revision_num(revision_max, 10)

        Args:
            revision_max(int): max revision number of working file or output file
            input_num(int): user's revision number

        Returns:
            revision_max if input_num is None or input_num > revision_max, input_num if input_num <= revision_max
        """
        if input_num is None:
            return revision_max
        self.int_check(input_num)
        if revision_max < input_num:
            return revision_max
        else:
            return input_num

    def get_task(self, task_type_name):
        """self.entity에 task_type_name의 task가 있다면, 그 task_type와 task의 dict를 반환한다.
        self.entity가 없다면 작동하지 않는다. \n
        메소드 내부에서만 사용되는 메소드다.

        Example:
            pepper.get_task("FX")

        Args:
            task_type_name: 'simulation', 'layout', ...

        Returns:
            task_type, task

        Raises:
            Exception: If self.entity is None, if type(task_type_name) is not string, if task_type is None,
                and if there's no task in self.entity.
        """
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        self.dict_check(task_type, 'no_task')
        self.dict_check(self.entity, 'entity_not_assigned')
        task = gazu.task.get_task_by_name(self.entity, task_type)
        self.dict_check(task, 'no_task_in_entity')
        return task_type, task

    # ---------------------------------------------
    # ----------- ui 작동에 필요한 메소드들 -----------
    # ---------------------------------------------

    def get_casting_path_for_asset(self):
        """asset이 casting된 shot과 그 shot의 layout과 FX task를 튜플로 묶어 모든 shot들을 리스트로 반환해준다.
        self.asset이 없을시 작동하지 않는다.

        Example:
            pepper.get_casting_path_for_asset()

        Returns:
            casted_shots: [(shot_1_dict), (shot_2_dict), ...]

        Raises:
            Exception: If self.asset doesn't exist.
        """
        self.dict_check(self.asset, 'no_asset')
        casted_shots = gazu.casting.get_asset_cast_in(self.asset)
        # layout_task_type = gazu.task.get_task_type_by_name('Layout')
        # fx_task_type = gazu.task.get_task_type_by_name('FX')
        # layout_tasks = [gazu.task.get_task_by_name(shot['shot_id'], layout_task_type) for shot in casted_shots]
        # fx_tasks = [gazu.task.get_task_by_name(shot['shot_id'], fx_task_type) for shot in casted_shots]
        return casted_shots

    def make_precomp_dict(self, casted_shot, temp_revision=None, cam_revision=None):
        """shot 별로 houdini에서 필요한 path들을 딕셔너리로 만들어준다.

        Example:
            for shot in render_shots:
                pepper.make_precomp_dict(shot)
            return pepper.precomp_dict

        Args:
            casted_shot(dict): shot dict
            temp_revision:
            cam_revision:
        """
        sequence_name = casted_shot['sequence_name']
        shot_name = casted_shot['shot_name']
        name = '_'.join([self.project['name'], self.asset['name'][5:], sequence_name, shot_name])
        self.entity = 'asset'
        temp_working_path = self.working_file_path('simulation', input_num=temp_revision)
        self.sequence = sequence_name
        self.shot = shot_name
        self.entity = 'shot'
        layout_output_path = self.output_file_path('camera_cache', 'layout_camera', input_num=cam_revision)
        fx_working_path = self.make_next_working_path('FX')
        jpg_output_path = self.make_next_output_path('jpg_sequence', 'FX')
        video_output_path = self.make_next_output_path('movie_file', 'FX')

        precomp = {'name': name, 'temp_working_path': temp_working_path,
                   'layout_output_path': layout_output_path, 'fx_working_path': fx_working_path,
                   'jpg_output_path': jpg_output_path, 'video_output_path': video_output_path}
        return precomp

    def publish_precomp_working(self, precomp):
        """self.make_precomp_dict 의 정보들로 fx의 working file을 publish 해준다. \n
        실제 hip 파일이 오류 없이 정상적으로 생성되었을 때 이 메소드를 작동해야 한다.

        Example:
            for precomp in pepper.precomp_dict:
                pepper.publish_precomp_working(precomp)

        Args:
            precomp(dict): make_precomp_dict에서 만든 dict
        """
        split_name = precomp['name'].split('_')
        self.project = split_name[0]
        self.sequence = split_name[2]
        self.shot = split_name[3]
        self.entity = 'shot'
        self.publish_working_file('FX')

    def publish_precomp_output(self, precomp):
        """self.make_precomp_dict 의 정보들로 fx의 output file을 publish 해준다. \n
        실제 mov 파일이 오류 없이 정상적으로 생성되었을 때 이 메소드를 작동해야 한다.

        Example:
            for precomp in pepper.precomp_dict:
                pepper.publish_precomp_output(precomp)

        Args:
            precomp(dict): make_precomp_dict에서 만든 dict
        """
        split_name = precomp['name'].split('_')
        self.project = split_name[0]
        self.sequence = split_name[2]
        self.shot = split_name[3]
        self.entity = 'shot'
        self.publish_output_file('FX', 'Movie_file', 'test_precomp')

    def get_every_revision_for_working_file(self, task_name):
        """self.entity의 task_name에 해당하는 task의 모든 working file의 revision이 담긴 list를 반환한다.

        Example:
            rev_list = pepper.get_every_revision_for_working_file('fx_template')

        Args:
            task_name(str): working file을 찾을 task의 이름

        Returns:
            [9, 8, 7, 6, 5, 4, 3, 2, 1]
        """
        working_files = gazu.files.get_all_working_files_for_entity(self.entity)
        revision_list = [working_file['revision'] for working_file in working_files
                         if gazu.task.get_task(working_file['task_id'])['entity_type']['name'] == task_name]
        return revision_list

    def get_every_revision_for_output_file(self, output_type_name, task_type_name):
        """self.entity의 task_name에 해당하는 task의 모든 output file의 revision이 담긴 list를 반환한다.

        Example:
            rev_list = pepper.get_every_revision_for_output_file('fx_template')

        Args:
            output_type_name(str): output file의 output task 이름
            task_type_name(str): output file을 찾을 task type의 이름

        Returns:
            [9, 8, 7, 6, 5, 4, 3, 2, 1]
        """
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        output_files = gazu.files.all_output_files_for_entity(self.entity, output_type, task_type)
        revision_list = [output_file['revision'] for output_file in output_files]
        return revision_list

    # -------------------------------------------
    # ----------- preview 관련 메소드들 -----------
    # -------------------------------------------

    def get_task_status(self, task_status_name):
        all_status = ['Todo', 'Ready To Start', 'Work In Progress', 'Done', 'Retake']
        if task_status_name not in all_status:
            self.error('no_task_status')
        task_status = gazu.task.get_task_status_by_name(task_status_name)
        return task_status

    def publish_preview(self, task_type_name, task_status_name, comment_text, preview_file_path):
        _, task = self.get_task(task_type_name)
        task_status = self.get_task_status(task_status_name)
        gazu.task.add_comment(task, task_status, comment=comment_text)
        comment = gazu.task.get_last_comment_for_task(task)
        # gazu.task.create_preview(task, 'test')
        gazu.task.add_preview(task, comment, preview_file_path)
        # gazu.task.upload_preview_file(task, '/home/rapa/tornado/Plate/plate_undistort_2k.0001.png')

    # -------------------------------------------
    # ----------- get all 관련 메소드들 -----------
    # -------------------------------------------

    @staticmethod
    def get_all_projects():
        """Host DB 안의 모든 project들을 반환한다.

        Examples:
            pepper.get_all_projects()

        Returns:
            ['BlackPepper', 'chopsticks', ...]
        """
        return [proj['name'] for proj in gazu.project.all_open_projects()]

    def get_all_assets(self):
        """self.project안의 모든 asset들을 반환한다. \n
        self.project가 없을 시 작동하지 않는다.

        Example:
            pepper.get_all_assets()

        Returns:
            ['temp_fire', 'temp_waterfall', ...]

        Raises:
            Exception: if self.project doesn't exist.
        """
        self.dict_check(self.project, 'no_project')
        return [asset['name'] for asset in gazu.asset.all_assets_for_project(self.project)]

    def get_all_sequences(self):
        """self.project 안의 모든 sequence들을 반환한다. \n
        self.project가 없을 시 작동하지 않는다.

        Example:
            pepper.get_all_sequences()

        Returns:
            ['sq01', 'sq02', ...]

        Raises:
            Exception: if self.project doesn't exist.
        """
        self.dict_check(self.project, 'no_project')
        return [seq['name'] for seq in gazu.shot.all_sequences_for_project(self.project)]

    def get_all_shots(self):
        """self.sequence 안의 모든 shot들을 반환한다. \n
        self.project와 self.sequence가 없을 시 작동하지 않는다.

        Example :
            pepper.get_all_shots()

        Returns:
            ['0010', '0020, ...]

        Raises :
            Exception: If self.project doesn't exist, and if self.sequence doesn't exist.
        """
        self.dict_check(self.project, 'no_project')
        self.dict_check(self.sequence, 'no_sequence')
        return [shot['name'] for shot in gazu.shot.all_shots_for_sequence(self.sequence)]

    def get_task_types_for_asset(self):
        """self.asset의 의 모든 task들에 대한 task type을 반환한다. \n
        self.project가 없을 시 작동하지 않는다.

        Examples:
            pepper.get_task_types_for_asset()

        Returns:
            ['simulation', 'FX', ...]

        Raises:
            Exception: If self.project doesn't exist, and if self.asset doesn't exist.
        """
        self.dict_check(self.asset, 'no_asset')
        return [task_type['name'] for task_type in gazu.task.all_task_types_for_asset(self.asset)]

    def get_casted_assets_for_shot(self):
        """self.shot에 캐스팅 된 모든 asset의 type name과 asset name을 dict로 반환해준다. \n
        self.project, self.sequence, self.shot이 없을 시 작동하지 않는다.

        Examples:
            pepper.get_casted_assets_for_shot()

        Returns:
            [(asset_type_name: asset_name), (asset_type_name_2: asset_name_2), ...]

        Raises:
            Exception: If self.project doesn't exist, if self.sequenece doesn't exist, and if self.shot don't exist.
        """
        self.dict_check(self.project, 'no_project')
        self.dict_check(self.sequence, 'no_sequence')
        self.dict_check(self.shot, 'no_shot')
        return [(asset['asset_type_name'] + ':' + asset['asset_name'])
                for asset in gazu.casting.get_shot_casting(self.shot)]

    def check_asset_type(self, asset_name, asset_type_name):
        """asset의 asset type이 asset_type_name과 일치하는지 확인해주고 일치한다면 asset을 그대로 반환해준다.


        """
        asset = gazu.asset.get_asset_by_name(self.project, asset_name)
        asset_type = gazu.asset.get_asset_type_from_asset(asset)
        if asset_type['name'] == asset_type_name:
            return asset_name
        return

    # ----------------------------------
    # ----------user 관련 메소드----------
    # ----------------------------------

    @staticmethod
    def get_my_projects():
        """로그인한 유저가 assign되어있는 모든 project의 이름을 반환한다.

        Examples:
            BlackPepper.get_my_projects()

        Returns:
            ['PEPPER', 'Redpepper', ...]
        """
        my_projects = [project['name'] for project in gazu.user.all_open_projects()]
        return my_projects

    def get_working_file_data(self, task_type_name, revision, entity_type):
        """task의 working file의 revision에 맞는 데이터를 반환해준다.

                Example:
                    name, time, rev = pepper.get_working_file_data('simulation', 5, 'asset')
                Args:
                    task_type_name(str):
                    revision:
                    entity_type(str):

                Returns:
                    JaehyukLee, Date-Time, 1
                """
        global the_working_file
        self.entity = entity_type
        _, task = self.get_task(task_type_name)
        working_files = gazu.files.get_all_working_files_for_entity(self.entity)
        for check_file in working_files:
            if str(check_file['revision']) == revision:
                the_working_file = check_file
        created_time = the_working_file['created_at']
        rev = the_working_file['revision']
        person_id = the_working_file['person_id']
        person = gazu.person.get_person(person_id)
        return person['first_name'] + person['last_name'], created_time, rev

    def get_output_file_data(self, output_type_name, task_type_name, revision, entity_type):
        """task의 output file의 revision에 맞는 데이터를 반환해준다.

        Example:
            name, time, rev = pepper.get_output_file_data('camera_cache', 'layout', 10, 'shot')
        Args:
            output_type_name(str):
            task_type_name(str):
            revision:
            entity_type(str):

        Returns:
            JaehyukLee, Date-Time, 1
        """
        global the_output_file
        self.entity = entity_type
        task_type, _ = self.get_task(task_type_name)
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        output_files = gazu.files.all_output_files_for_entity(self.entity, output_type, task_type)
        for check_file in output_files:
            if str(check_file['revision']) == revision:
                the_output_file = check_file
                break
        rev = the_output_file['revision']
        created_time = the_output_file['created_at']
        person_id = the_output_file['person_id']
        person = gazu.person.get_person(person_id)
        return person['first_name'] + person['last_name'], created_time, rev

    # --------------------------------------------
    # ----------error handling 관련 메소드----------
    # --------------------------------------------

    def dict_check(self, test_dict, code):
        """다른 메소드를 통해 dict값을 받아오려 할 때, 잘못된 입력으로 None이 받아지지 않았는지 체크한다.

        Example:
            BlackPepper.dict_check(self.sequence, 'no_sequence')

        Returns:
            test_dict(if test_dict is not None)

        Raises:
            Exception: If test_dict is None.
        """
        if test_dict is None:
            self.error(code)
        else:
            return test_dict

    def args_str_check(self, *args):
        """args에 들어온 인자들을 str인지 체크할 수 있는 메소드로 보내준다. \n
        메소드 내에서만 사용되는 메소드다.

        Example:
            BlackPepper.args_str_check(task_type_name)

        Args:
            args : 여러가지 인자들을 받을 수 있다

        Returns:
            받은 args들을 그대로 반환한다
        """
        if type(args) is tuple:
            str_confirms = ','.join(args)
            for str_confirm in str_confirms:
                self.str_check(str_confirm)
            return str_confirms
        else:
            self.str_check(args)
            return args

    def str_check(self, strn):
        """strn의 타입이 str인지 체크한다.\n
        메소드 내에서만 사용되는 메소드다.

        Args:
            strn: type이 str인지 체크하고 싶은 인자값

        Examples:
            BlackPepper.int_check(revision_num)

        Returns:
            strn(if str)

        Raises:
            Exceptions: If type(strn) is not str
        """
        if type(strn) is not str:
            self.error("not_string")
        else:
            return strn

    def int_check(self, num):
        """num의 타입이 정수인지 체크한다.\n
        메소드 내에서만 사용되는 메소드다.

        Args:
            num: type이 int인지 체크하고 싶은 인자값

        Examples:
            BlackPepper.int_check(revision_num)

        Returns:
            num(if int)

        Raises:
            Exceptions: If type(num) is not int
        """
        if type(num) is not int:
            self.error('not_int')
        else:
            return num

    @staticmethod
    def error(code):
        """에러 핸들링을 위한 메소드, code에 받은 값에 따라 다른 Exception을 raise해준다.

        Examples:
            BlackPepper.error('not_string')

        Args:
            code(str): Error code

        Returns:
            raise Exceptions
        """
        if code == 'not_string':
            raise Exception("Input must be string")
        if code == 'not_int':
            raise Exception("Input must be integer.")
        if code == 'none':
            raise Exception("There is no dict")
        if code == 'hou':
            raise Exception("Software input must be hip, hipnc, or hiplc.")
        if code == 'no_task':
            raise Exception("There's no task in entity.")
        if code == 'no_task_status':
            raise Exception("There's no task status in project.")
        if code == 'no_task_in_entity':
            raise Exception("There's no task in entity")
        if code == 'no_project':
            raise Exception("No project is assigned.")
        if code == 'no_sequence':
            raise Exception("No sequence is assigned.")
        if code == 'no_shot':
            raise Exception("No shot is assigned.")
        if code == 'no_asset':
            raise Exception("No asset is assigned.")
        if code == 'no_work_file':
            raise Exception("No working file found.")
        if code == 'no_output_file':
            raise Exception("No output file found.")
        if code == 'not_asset_shot':
            raise Exception("No shot or asset is assigned.")
        if code == 'entity_not_assigned':
            raise Exception("Entity is not assigned")
        if 'no_task_type' in code:
            raise Exception(f"There's no task type named '{code[12:]}'")
        if 'no_output_type' in code:
            raise Exception(f"There's no output type named '{code[14:]}'")
        else:
            raise Exception("NO ERROR CODE")


# BlackPepper = Houpub()
# BlackPepper.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")
# BlackPepper.software = 'hipnc'
# BlackPepper.project = 'Chopsticks'
# BlackPepper.sequence = 'S1'
# BlackPepper.shot = 'shot_01'
# BlackPepper.entity = 'shot'
# BlackPepper.publish_preview('FX', 'Ready To Start', '230315 1158 test',
#                             '/home/rapa/tornado/Plate/plate_undistort_2k.0001.png')

# BlackPepper.asset = 'temp_dancing_particle'
# css = BlackPepper.get_casting_path_for_asset()
# for cs in css:
#     BlackPepper.make_precomp_dict(cs)
# BlackPepper.delete_precomp_dict('PEPPER_dancing_particle_SQ01_0040')
# BlackPepper.entity = 'shot'
# nwp = BlackPepper.make_next_working_path('FX')
# nop = BlackPepper.make_next_output_path('test', 'FX')
# print(nwp)

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

# ------------set software-------------
# def get_software(self, software_name):
#     """houdini의 extension 타입별로 software dict를 반환해준다
#
#     Args:
#         software_name(str): 'hip', 'hipnc', or 'hiplc'
#
#     Returns:
#         Software dict
#
#     Raises:
#         Exception: If software_name is not hip, hipnc, or hiplc.
#
#     """
#     if software_name == 'hip':
#         return gazu.files.get_software_by_name('houdini')
#     if software_name == 'hipnc':
#         return gazu.files.get_software_by_name('houdininc')
#     if software_name == 'hpilc':
#         return gazu.files.get_software_by_name('houdinilc')
#     else:
#         self.error('hou')
