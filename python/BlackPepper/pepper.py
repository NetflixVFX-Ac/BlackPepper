import gazu
from BlackPepper.log.moduler_log import Logger
import os
import json


class Houpub:
    """pepper 모듈은 Gazu (Kitsu API 용 python 클라이언트)를 사용하여 원하는 path를 추출하는 Mapping API 이다. \n
    * kitsu는 VFX 스튜디오 제작관리 web application이며,
    * Gazu는 Kitsu API용 Python 클라이언트다.
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

    @property
    def project(self):
        """설정한 project의 dict를 반환하는 메소드.

        Returns:
            self._project dict
        """
        return self._project

    @project.setter
    def project(self, proj_name):
        """proj_name이 Kitsu에 등록된 project 중 하나와 일치하면 해당 project를 현재 project로 지정하는 메소드.

        Examples:
            pepper.project = 'BlackPepper'

        Args:
            proj_name(str): Project name

        Raises:
            Exception: If input is not string, or if there is no dict named 'project name'
        """
        self.str_check(proj_name)
        self._project = gazu.project.get_project_by_name(proj_name)
        self.dict_check(self.project, 'none')
        return

    @property
    def sequence(self):
        """설정한 sequence의 dict를 반환하는 메소드.

        Returns:
            self._sequence dict
        """
        return self._sequence

    @sequence.setter
    def sequence(self, seq_name):
        """seq_name이 설정된 project 안의 sequence 중 하나와 일치하면 해당 sequence를 현재 sequence로 지정하는 메소드. \n
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
        self.str_check(seq_name)
        self._sequence = gazu.shot.get_sequence_by_name(self.project, seq_name)
        self.dict_check(self.sequence, 'none')
        return

    @property
    def shot(self):
        """설정한 shot의 dict를 반환하는 메소드.

        Returns:
            self._shot dict
        """
        return self._shot

    @shot.setter
    def shot(self, shot_name):
        """shot_name이 설정된 sequence 안의 shot 중 하나와 일치하면 해당 shot을 현재 shot으로 지정하는 메소드. \n
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
        self.str_check(shot_name)
        self._shot = gazu.shot.get_shot_by_name(self.sequence, shot_name)
        self.dict_check(self.shot, 'none')
        return

    @property
    def asset(self):
        """설정한 asset의 dict를 반환하는 메소드.

        Returns:
            self._asset dict
        """
        return self._asset

    @asset.setter
    def asset(self, asset_name):
        """asset_name이 설정된 project 안의 asset 중 하나와 일치하면 해당 asset을 현재 asset으로 지정하는 메소드. \n
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
        """설정한 entity의 dict를 반환하는 메소드.

        Returns:
            self._entity dict
        """
        return self._entity

    @entity.setter
    def entity(self, ent):
        """사용할 entity가 self.asset이 될지, self.shot이 될지 지정하는 메소드. \n
        asset 입력시 self.asset이 있어야 하고, shot 입력시 self.shot이 있어야 한다. 맞는 인자가 없을 시 작동하지 않는다.

        Examples:
            pepper.entity('asset') or pepper.entity('shot')

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
        """설정한 software의 dict를 반환해주는 메소드.

        Returns:
            self._software dict
        """
        return self._software

    @software.setter
    def software(self, software_name):
        """task에 사용될 software을 지정해주는 메소드. hip, hipnc, hiplc만 지원한다.

        Example:
            pepper.software = 'hip'

        Args:
            software_name(str): 'hip', 'hipnc', or 'hiplc'

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
        """self.project의 file tree를 업데이트 해준 뒤 file tree 변경 로그를 저장해주는 메소드. \n
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
        self.read_json_file()
        self.mylog.set_logger(self.identif)
        self.mylog.tree_log(self.project)

    def publish_working_file(self, task_type_name):
        """self.entity 내 task의 working file을 publish 해주는 메소드. \n
        task_type_name과 self.entity를 통해 해당 entity의 입력된 task_type을 가진 task를 받아온다.\n
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
        self.str_check(task_type_name)
        _, task = self.get_task(task_type_name)
        gazu.files.new_working_file(task, software=self.software)
        self.read_json_file()
        self.mylog.set_logger(self.identif)
        self.mylog.publish_working_file_log(task_type_name)

    def publish_output_file(self, task_type_name, output_type_name, comments):
        """self.entity 내 output type의 output file을 publish 해주는 메소드. \n
        task_type_name과 output_type_name, self.entity를 통해 해당 entity의 입력된 task_type을 가진 task를 받아온다.\n
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
        for check in [task_type_name, output_type_name, comments]:
            self.str_check(check)
        task_type, task = self.get_task(task_type_name)
        self.dict_check(task_type, f'no_task_type{task_type_name}')
        work_file = gazu.files.get_last_working_file_revision(task)
        self.dict_check(work_file, 'no_work_file')
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        self.dict_check(output_type, f'no_task_type{output_type_name}')
        gazu.files.new_entity_output_file(self.entity, output_type, task_type, working_file=work_file,
                                          representation=output_type['short_name'], comment=comments)
        self.read_json_file()
        self.mylog.set_logger(self.identif)
        self.mylog.publish_output_file_log(task_type_name, output_type_name)

    def working_file_path(self, task_type_name, input_num=None):
        """self.entity에 해당된 task_type_name을 가진 task의 working file 중 input_num의 revision을 반환한다. \n

        Example:
            pepper.working_file_path("simulation") or pepper.working_file_path('layout', input_num=12)

        Args:
            task_type_name(str): 'simulation', 'FX', ...
            input_num(int): user's revision number

        Returns:
            working file path(revision=input_num)
        """
        self.str_check(task_type_name)
        _, task = self.get_task(task_type_name)
        revision_max = self.get_working_revision_max(task)
        revision_num = self.get_revision_num(revision_max, input_num)
        path = gazu.files.build_working_file_path(task, revision=revision_num)
        return path

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
        self.str_check(task_type_name)
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
        return path

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
        if gazu.files.all_output_files_for_entity(self.entity, output_type, task_type, name='main'):
            revision_max += 1
        path = gazu.files.build_entity_output_file_path(self.entity, output_type, task_type, revision=revision_max)
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
        """self.entity에 task_type_name의 task가 있다면, 그 task_type와 task의 dict를 반환한다. \n
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
        """asset이 casting된 shot과 그 shot의 layout과 FX task를 튜플로 묶어 모든 shot들을 리스트로 반환해준다. \n
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
        return casted_shots

    def make_precomp_dict(self, casted_shot, temp_revision=None, cam_revision=None):
        """Houdini에서 fx template와 camera cache를 합쳐 새 hip file을 만드는데에 필요한 path들을 dict에 모아 반환해주는 메소드. \n
        dict는 <project name>_<template name>_<sequence name>_<shot name>인 name,
        temp_revision에 맞는 fx template의 working file인 hip file path,
        cam_revision에 맞는 layout_camera의 camera_cache output file인 abc file path,
        새로 만들어진 hip file을 저장할 shot의 fx working file path,
        렌더될 이미지와 합쳐져서 만들어질 동영상을 저장할 shot의 fx output file path로 구성되어 있다.

        Example:
            for shot in render_shots:
                pepper.make_precomp_dict(shot)
            return pepper.precomp_dict

        Args:
            casted_shot(dict): shot dict
            temp_revision: template revision for making fx working file
            cam_revision: camera cache revisionf for making fx working file

        Returns:
            dict for houpepper render queue
        """
        cameratask = 'layout_camera'
        cameraoutput = 'camera_cache'
        if self.project['name'] == 'RAPA':
            cameratask = 'camera'
            cameraoutput = 'alembic'
        hou_ext = self.software['file_extension']
        self.dict_check(casted_shot, 'not_dict')
        if 'shot_name' not in casted_shot or 'sequence_name' not in casted_shot:
            self.error('not_dict')
        sequence_name = casted_shot['sequence_name']
        shot_name = casted_shot['shot_name']
        name = '_'.join([self.project['name'], self.asset['name'][5:], sequence_name, shot_name])
        if self.project['name'] == 'RAPA':
            name = '_'.join([self.project['name'], self.asset['name'], sequence_name, shot_name])
        self.entity = 'asset'
        temp_working_path = self.working_file_path('simulation', input_num=temp_revision) + f'.{hou_ext}'
        self.sequence = sequence_name
        self.shot = shot_name
        self.entity = 'shot'
        layout_output_path = self.output_file_path(cameraoutput, cameratask, input_num=cam_revision) + '.abc'
        fx_working_path = self.make_next_working_path('FX') + f'.{hou_ext}'
        jpg_output_path = self.make_next_output_path('jpg_sequence', 'FX')
        video_output_path = self.make_next_output_path('movie_file', 'FX')
        exr_output_path = self.make_next_output_path('EXR', 'FX')
        precomp = {'name': name, 'temp_working_path': temp_working_path, 'layout_output_path': layout_output_path,
                   'fx_working_path': fx_working_path, 'jpg_output_path': jpg_output_path,
                   'video_output_path': video_output_path, 'exr_output_path': exr_output_path}
        return precomp

    @staticmethod
    def path_seperator(precomp):
        """self.make_precomp_dict로 생성한 dict에서 각 path들을 추출해주는 메소드. \n

        Args:
            precomp(dict): dict made with self.make_precomp_dict

        Returns:
            temp_working_path, layout_output_path, fx_working_path, jpg_output_path, video_output_path
        """
        temp_working_path = precomp['temp_working_path']
        layout_output_path = precomp['layout_output_path']
        fx_working_path = precomp['fx_working_path']
        jpg_output_path = precomp['jpg_output_path']
        video_output_path = precomp['video_output_path']
        exr_output_path = precomp['exr_output_path']
        return temp_working_path, layout_output_path, fx_working_path,\
            jpg_output_path, video_output_path, exr_output_path

    def get_every_revision_for_working_file(self, task_type_name):
        """self.entity의 task_name에 해당하는 task의 모든 working file의 revision이 담긴 list를 반환한다.

        Example:
            rev_list = pepper.get_every_revision_for_working_file('fx_template')

        Args:
            task_type_name(str): working file을 찾을 task의 이름

        Returns:
            [9, 8, 7, 6, 5, 4, 3, 2, 1]
        """
        working_files = gazu.files.get_all_working_files_for_entity(self.entity)
        # Task id of working file leads to task, task_type of task have task type name
        revision_list = [working_file['revision'] for working_file in working_files
                         if gazu.task.get_task(working_file['task_id'])['task_type']['name'] == task_type_name]
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

    def check_task_status(self, task_status_name, task_type_name):
        """self.entity의 task_type_name에 해당하는 task가 task_status_name과 동일한 task status를 가지고 있는지 확인해준다.

        Args:
            task_status_name(str): Task status name to be checked
            task_type_name(str): Task type of the task to be checked

        Returns:
            True if task status is correct, False if not
        """
        status = self.get_task_status(task_status_name)
        _, task = self.get_task(task_type_name)
        if status['id'] == task['task_status_id']:
            return True
        return False

    def get_task_status(self, task_status_name):
        """task_status_name에 맞는 task status dict를 반환한다. \n
        Todo, Ready To Start, Work In Progress, Done, Retake 중에서만 반환받을 수 있다.

        Examples:
            pepper.get_task_status('Done')

        Args:
            task_status_name(str): Task status name

        Returns:
            Task status dict
        """
        all_status = ['Todo', 'Ready To Start', 'Work In Progress', 'Done', 'Retake']
        if task_status_name not in all_status:
            self.error('no_task_status')
        task_status = gazu.task.get_task_status_by_name(task_status_name)
        return task_status

    def publish_preview(self, task_type_name, task_status_name, comment_text, preview_file_path):
        """self.entity의 task_type에 comment를 남기며 task status를 변경해주고, preview file을 업로드한다.

        Examples:
            pepper.publish_preview('FX', 'Done', 'sq01_0010 done', /home/rapa/test.png')

        Args:
            task_type_name(str): output file을 찾을 task type의 이름
            task_status_name(str): Destination task status
            comment_text(str): Text for publishing comment
            preview_file_path(str): Local path of preview file
        """
        _, task = self.get_task(task_type_name)
        task_status = self.get_task_status(task_status_name)
        gazu.task.add_comment(task, task_status, comment=comment_text)
        comment = gazu.task.get_last_comment_for_task(task)
        preview_dict = gazu.task.add_preview(task, comment, preview_file_path=preview_file_path)
        return preview_dict

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
        """asset의 asset type이 asset_type_name과 일치하는지 확인해주고 일치한다면 asset을 그대로 반환해주는 메소드. \n
        asset_name의 asset이 없거나 asset의 asset type이 asset_type_name과 일치하지 않는다면 아무것도 반환하지 않는다.
        """
        asset = gazu.asset.get_asset_by_name(self.project, asset_name)
        if asset is None:
            return
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
            pepper.get_my_projects()

        Returns:
            ['PEPPER', 'Redpepper', ...]
        """
        my_projects = [project['name'] for project in gazu.user.all_open_projects()]
        return my_projects

    def get_working_file_data(self, task_type_name, revision, entity_type):
        """해당 working file의 revision에 맞는 person, created time을 반환해준다.

        Example:
            name, time, rev = pepper.get_working_file_data('simulation', 5, 'asset')

        Args:
            task_type_name(str): Task type of working file
            revision: Revision number of working file
            entity_type(str): Entity type(asset or shot)

        Returns:
            JaehyukLee, Date-Time, 1
        """
        self.entity = entity_type
        _, task = self.get_task(task_type_name)
        working_files = gazu.files.get_all_working_files_for_entity(self.entity)
        working_file = self.find_revision_in_list(working_files, revision)
        person, created_time, rev = self.make_info_data(working_file)
        return person, created_time, rev

    def get_output_file_data(self, output_type_name, task_type_name, revision, entity_type):
        """해당 output file의 revision에 맞는 person, created time을 반환해준다.

        Example:
            name, time, rev = pepper.get_output_file_data('camera_cache', 'layout', 10, 'shot')

        Args:
            output_type_name(str): Output type of output file
            task_type_name(str): Task type of output file
            revision: Revision number of output file
            entity_type(str): Entity type(asset or shot)

        Returns:
            JaehyukLee, Date-Time, 1
        """
        self.entity = entity_type
        task_type, _ = self.get_task(task_type_name)
        output_type = gazu.files.get_output_type_by_name(output_type_name)
        output_files = gazu.files.all_output_files_for_entity(self.entity, output_type, task_type)
        output_file = self.find_revision_in_list(output_files, revision)
        person, created_time, rev = self.make_info_data(output_file)
        return person, created_time, rev

    @staticmethod
    def find_revision_in_list(files, revision):
        """Working file이나 Output file들이 들어있는 리스트에서 input된 revision과 같은 revision을 가진 dict를 반환해주는 메소드. \n
        self.get_output_file_data 메소드 안에서만 사용된다.

        Args:
            files(list): List of working file dicts or output file dicts
            revision: Revision number of working file the user is looking for

        Returns:
            Working file dict with the right revision number(if exists)
        """
        for file in files:
            if str(file['revision']) == str(revision):
                return file
        return

    @staticmethod
    def make_info_data(file):
        """Working file이나 Output file의 dict에서 person, created time, revision을 찾아 반환해주는 메소드. \n
        Dict가 제대로 들어오지 않는다면 공백을 반환한다. self.get_output_file_data 메소드 안에서만 사용된다.

        Args:
            file(dict): Working file dict or output file dict

        Returns:
            JaehyukLee, Date-Time, 1
        """
        if file is None:
            rev = ''
            person = ''
            created_time = ''
        else:
            rev = file['revision']
            created_time = file['created_at']
            person_id = file['person_id']
            person_dict = gazu.person.get_person(person_id)
            person = person_dict['full_name']
        return person, created_time, rev

    def read_json_file(self):
        """Auto login을 할 수 있는 json file의 생성 경로나 불러올 경로를 지정한다. root는 현재 .py file이 위치한 곳으로 한다.
        """
        now_path = os.path.realpath(__file__)
        split_path = now_path.split('/')[:-1]
        dir_path = os.path.join('/'.join(split_path), '.config')
        user_path = os.path.join(dir_path, 'user.json')
        with open(user_path, 'r') as json_file:
            user_dict = json.load(json_file)
        for i in user_dict['auto']:
            if self.identif is None:
                self.identif = i['user_id']
            else:
                pass

    # --------------------------------------------
    # ----------error handling 관련 메소드----------
    # --------------------------------------------

    def dict_check(self, test_dict, code):
        """다른 메소드를 통해 dict값을 받아오려 할 때, 잘못된 입력으로 None이 받아지지 않았는지 체크한다.

        Example:
            pepper.dict_check(self.sequence, 'no_sequence')

        Returns:
            test_dict(if test_dict is not None)

        Raises:
            Exception: If test_dict is None.
        """
        if test_dict is None:
            self.error(code)
        else:
            return test_dict

    def str_check(self, strn):
        """strn의 타입이 str인지 체크한다.

        Examples:
            pepper.str_check(text)

        Args:
            strn(str): String to be checked

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

        Args:
            num(int): integer

        Examples:
            pepper.int_check(revision_num)

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
            pepper.error('not_string')

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
        if code == 'not_dict':
            raise Exception("Input must be dict.")
        if 'no_task_type' in code:
            raise Exception(f"There's no task type named '{code[12:]}'")
        if 'no_output_type' in code:
            raise Exception(f"There's no output type named '{code[14:]}'")
        else:
            raise Exception("NO ERROR CODE")

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


# p = Houpub()
# p.login('http://192.168.3.116/api', 'pepper@hook.com', 'pepperpepper')
# p.project = 'RAPA'
# p.sequence = 'SQ01'
# p.shot = '0010'
# p.entity = 'shot'
# p.asset = 'fire'
# p.entity = 'asset'
# p.publish_working_file('camera')
# p.publish_output_file('plate', 'EXR', 'test')
# p.casting_multiple_assets('dancing_particle', 'fire')
# p.casting_create(1)
# a = p.working_file_path('camera')
# a = p.output_file_path('EXR', 'plate')
# b = p.make_next_output_path('alembic', 'camera')
# print(a)