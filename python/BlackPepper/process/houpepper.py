import os
import numpy as np
import hou
import _alembic_hom_extensions as abc


class HouPepper:
    """
    이 모듈은 Template으로 정한 Houdini 파일에 Alembic 파일의 카메라값을 불러와 FX working file path에 저장한다. Alembic 파일은
    Template에 캐스팅 된 샷의 Layout output file path에서 불러온다. Houdini Mantra를 사용하여 JPG의 시퀀스 파일로 컨버팅하는데,
    Temp 내 복사한 FX working file을 이용한다. FX output file path에 시퀀스 파일을 저장하고 사용한 Temp를 지워주면서 Publish를
    진행한다.
    """

    def __init__(self):
        self.cam_list = []
        self.cam_path = []
        self.cmd_list = []
        self.total_frame_list = []

        self.cam_node = None
        self._abc_path = None
        self._abc_tree_all = None
        self._abc_tree_path = None
        self._abc_range = None

        self.hou_cam_parm_name = (
            'aperture',
            'aspect',
            'focal',
            'near',
            'far',
            'focus',
            'fstop',
            'shutter',
            'winx',
            'winy',
            'winsizex',
            'winsizey')
        for str in self.hou_cam_parm_name:
            exec("self.{}=[]".format(str))
        self.cam_resolution = []
        self.filmaspectratio = []
        self.file_count = 0

    @property
    def abc_path(self):
        return self._abc_path

    @abc_path.setter
    def abc_path(self, abc_path):
        """입력한 Alembic 경로를 저장한다.

        Example:
            BlackPepper.abc_path = 'path'

        Args:
            abc_path: (str): Alembic file path

        Returns:
            Alembic file path
        """
        self._abc_path = abc_path

    @property
    def abc_tree_all(self):
        return self._abc_tree_all

    @abc_tree_all.setter
    def abc_tree_all(self, abc_tree_all):
        """Alembic 파일 내 노드 정보를 받는다.


        Args:
            abc_tree_all (tuple): node in .abc

        Returns: node list
        """
        self._abc_tree_all = abc_tree_all

    @property
    def abc_tree_path(self):
        return self._abc_tree_path

    @abc_tree_path.setter
    def abc_tree_path(self, abc_tree_path):
        """Alembic 파일 내 노드의 경로를 받는다.


        Args:
            abc_tree_path: node path in .abc

        Returns: node path
        """
        self._abc_tree_path = abc_tree_path

    @property
    def abc_range(self):
        return self._abc_range

    @abc_range.setter
    def abc_range(self, abc_range):
        """ Alembic 파일 내 Camera가 가지고 있는 frame range를 받는다


        Args:
            abc_range(list): camera in, out frame

        Returns: camera in, out frame
        """
        self._abc_range = abc_range

    def set_abc_cam_tree(self, abc_path):
        """ Alembic file에 포함된 node, node path, camera in/out frame을 설정한다. \n
        Alembic file 내, Camera node를 찾아 cam list, cam path를 구한다.

        Args:
            abc_path (str): Alembic file path
        """
        self.abc_path = abc_path
        if len(self.abc_path) > 0:
            self.true = self.check_abc(self.abc_path)
            if self.true:
                self.abc_tree_all = abc.alembicGetSceneHierarchy(self.abc_path, '')
                self.abc_tree_path = abc.alembicGetObjectPathListForMenu(self.abc_path)
                self.get_abc_cam_tree(self.abc_tree_all)
        self.abc_range = abc.alembicTimeRange(self.abc_path)
        # print(self.abc_tree_all)

    def get_abc_cam_tree(self, abc_tree_all):
        """Alembic 파일 내 Node에서 이름이 camera인 노드를 찾는다. \n
        Node를 node_name, node_type, node_children으로 나누고 node_type이 camera인 경우, 해당 노드를 cam_list에 저장한다. \n
        node_type이 camera인 노드의 node_name에 해당하는 경로를 가져와 cam_path에 저장한다.

        Args:
            abc_tree_all: abc.alembicGetSceneHierarchy(alembic file path, '')
        """
        node_name = abc_tree_all[0]
        node_type = abc_tree_all[1]
        node_children = abc_tree_all[2]
        # print(abc_tree_all)
        if node_type == 'camera':
            self.cam_list.append(node_name)
            for x in self.abc_tree_path:
                if node_name in x:
                    camlipath = x
            if camlipath not in self.cam_path:
                self.cam_path.append(camlipath)
        else:
            for children in node_children:
                self.get_abc_cam_tree(children)


    def check_abc(self, abc_path):
        """
        입력받은 path가 Alembic file path인지 확인한다.

        Args:
            abc_path (str): path

        Returns: boolean
        """
        file_name = abc_path
        if 'abc' not in file_name[-3:]:
            print('No filename entered for Alembic scene.')
            return False
        else:
            abc.alembicClearArchiveCache(file_name)
            return True

    def set_cam_view(self, cam):
        """Alembic file에 있는 카메라가 가진 frame range에 frame rate를 곱하여 real time frame 동안의 \n
        camera 정보 값을 가져와 Houdini 내 새로 생성한 카메라 정보 값에 넣어준다.

        Example:
            hou.hipFile.load(hip_path)
            cam = '/cam1/cam1Camera'
            set_cam_view(cam)

        Args:
            cam: cam node created in houdini
        """
        for f in range(int(self.abc_range[0] * hou.fps()), int(self.abc_range[1] * hou.fps()) + 1):
            camera_dict = abc.alembicGetCameraDict(self.abc_path, cam, float(f) / hou.fps())
            self.filmaspectratio.append(camera_dict['filmaspectratio'])
            if camera_dict:
                for parm_name in self.hou_cam_parm_name:
                    exec("self.{}.append({})".format(parm_name, camera_dict.get(parm_name)))


    def get_cam_resolution(self, cam):
        """Alembic file에 있는 카메라가 가진 frame range에 frame rate를 곱하여 real time frame 동안의 \n
        camera 해상도 값을 가져와 Houdini 내 새로 생성한 카메라 해상도 값에 넣어준다. 해상도 값이 존재할 경우, \n
        cam_resolution 리스트에 해상도 값을 추가하고 return 값으로 True를 갖는다.

        Example:
            hou.hipFile.load(hip_path)
            cam = '/cam1/cam1Camera'
            check_resolution = self.get_cam_resolution(cam)

        Args:
            cam: cam node created in houdini

        Returns: True
        """
        for f in range(int(self.abc_range[0] * hou.fps()), int(self.abc_range[1] * hou.fps()) + 1):
            cam_resolution = abc.alembicGetCameraResolution(self.abc_path, cam, float(f) / hou.fps())
            if cam_resolution:
                self.cam_resolution.append(cam_resolution)
                return True

    def get_cam_xform(self, cam):
        """Alembic file에 있는 카메라가 가진 frame range에 frame rate를 곱하여 real time frame 동안의 \n
        Houdini 내 Matrix4 모듈을 사용하여 camera translate, rotate, scale 값을 가져온다.

        Example:
            hou.hipFile.load(hip_path)
            cam = '/cam1/cam1Camera'
            tr, ro, sc = self.get_cam_xform(cam)

        Args:
            cam: camera node created in houdini

        Returns (list): translate, rotate, scale
        """
        translate = []
        rotate = []
        scale = []
        for f in range(int(self.abc_range[0] * hou.fps()), int(self.abc_range[1] * hou.fps()) + 1):
            xform = abc.getWorldXform(self.abc_path, cam, float(f) / hou.fps())[0]
            xf = hou.Matrix4(xform)
            translate.append(xf.extractTranslates())
            rotate.append(xf.extractRotates())
            scale.append(xf.extractScales())
        return translate, rotate, scale

    def set_cam_key(self, key, node, parm):
        """key에 저장된 x, y, z 값(traslate, rotate, scale)을 Houdini obj에 만든 camera parameter에 넣어준다. \n
        numpy, convolution 메소드를 사용하여 camera Key 값이 변하는 구간에서 값들을 읽어 camera parameter에 넣어준다.

        Example:
            hou.hipFile.load(hip_path)
            cam = '/cam1/cam1Camera'
            tr, ro, sc = get_cam_xform(cam)
            cam_node = hou.node('/obj').createNode('cam', name[cam_path.index(cam)])
            set_cam_key(tr, cam_node, 't')

        Args:
            key(list): x, y, z position
            node(str): camera node created in houdini
            parm: 't' (translate) or 'r' (rotate) or 's' (scale)
        """
        J = ['x', 'y', 'z', 'w']

        key_np = np.array(key)
        s = [1, -1]
        for frame, k in enumerate(key_np):
            try:
                num_key = len(k)
                if num_key > 1:
                    for n, key_index in enumerate(k):
                        slope = np.convolve(list(map(lambda x: x[1], key_np)), s, mode='same') / (len(s) - 1)
                        if slope[frame] != 0:
                            keyframe = hou.Keyframe(key_index, hou.frameToTime(frame + 1))
                            node.parm('{}{}'.format(parm, J[n])).setKeyframe(keyframe)
            except:
                slope = np.convolve(list(map(lambda x: x, key_np)), s, mode='same') / (len(s) - 1)
                if slope[frame] != 0:
                    keyframe = hou.Keyframe(k, hou.frameToTime(frame + 1))
                    node.parm('{}'.format(parm)).setKeyframe(keyframe)

    def set_cam_create(self, abc_path):
        """Houdini obj에 camera를 생성하고, Alembic file에 있는 camera의 정보 값들을 \n
        obj에 만든 camera에 넣어준다. 해당 data는 camera의 dictionary, camera resolution, camera x,y,z position 값이 된다.

        Example:
            precomp = pepper.make_precomp_dict(casted_shot)
            set_cam_create(precomp.get('layout_output_path'))

        Args:
            abc_path: Alembic file path
        """
        self.set_abc_cam_tree(abc_path)
        name = [abc.alembicGetSceneHierarchy(abc_path, i)[0] for i in self.cam_path]
        for cam in self.cam_path:
            cam_node = hou.node('/obj').createNode('cam', name[self.cam_path.index(cam)])
            self.cam_node = cam_node
            self.set_cam_view(cam)
            check_resolution = self.get_cam_resolution(cam)
            tr, ro, sc = self.get_cam_xform(cam)
            self.set_cam_key(tr, cam_node, 't')
            self.set_cam_key(ro, cam_node, 'r')
            self.set_cam_key(sc, cam_node, 's')
            cam_node.parmTuple('t').lock((1, 1, 1))
            cam_node.parmTuple('r').lock((1, 1, 1))
            cam_node.parmTuple('s').lock((1, 1, 1))
            for str in self.hou_cam_parm_name:
                exec("self.set_cam_key(self.{}, cam_node, '{}')".format(str, str))
            if check_resolution:
                self.set_cam_key(self.cam_resolution, cam_node, 'res')
            else:
                self.cam_node.parm('resx').set(1920)
                self.cam_node.parm('resy').set(int(1920 / self.filmaspectratio[0]))

    def set_fx_working_for_shot(self, hip_path, abc_path, saved_path):
        """Template file obj에 shot layout output file인 Alembic의 카메라 정보를 가진 camera를 생성하여\n
        shot fx working file path에 저장한다.

        Example:
            precomp = pepper.make_precomp_dict(casted_shot)
            houp.set_fx_working_for_shot(precomp.get('temp_working_path'), precomp.get('layout_output_path'),
                             f'{precomp.get('fx_working_path')}.{pepper.software.get("file_extension")}')

        Args:
            hip_path: template asset working file path
            abc_path: shot casted asset layout output file path
            saved_path: shot casted asset fx working file path
        """
        hou.hipFile.load(hip_path)
        self.set_cam_create(abc_path)
        hou.hipFile.save(file_name=saved_path)
        self.cam_list.clear()
        self.cam_path.clear()

    def make_cmd(self, precomp_list):
        """터미널에서 실행할 command를 list에 넣어준다. Houdini Mantra를 사용하여 렌더링하기 위해 mantra_render.py를 실행한다.
        mantra_render.py에는 4개의 argument를 받도록 설정하였다. list에 mantra command가 들어가고 sequence file을 mov로
        컨버팅하기 위해 FFmpeg을 사용하는 command를 list에 추가로 넣어준다. alembic file의 camera frame out count를 위해
        mantra와 ffmpeg을 사용한 command를 리스트에 넣어줄때, 지정한 total_frame를 total_frame_list에 넣어준다.

        Example:
            precomp = pepper.make_precomp_dict(casted_shot)
            houpepper.make_cmd(precomp)

        Args:
            precomp_list (dict): precomp = {'name': name, 'temp_working_path': temp_working_path,
                    'layout_output_path': layout_output_path, 'fx_working_path': fx_working_path,
                    'jpg_output_path': jpg_output_path, 'video_output_path': video_output_path}

        Returns: cmd_list, total_frame_list
        """
        total_frame = self.abc_range[1] * hou.fps()

        self.mantra_command = [
            'python',
            '/home/rapa/git/hook/python/BlackPepper/mantra_render.py',
            f'{precomp_list.get("fx_working_path")}.hipnc',
            precomp_list.get('jpg_output_path'),
            self.abc_path,
            self.cam_node
        ]
        self.mantra_cmd = (' '.join(str(s) for s in self.mantra_command))
        self.cmd_list.append(self.mantra_cmd)
        self.total_frame_list.append(total_frame)

        self.sequence_path = precomp_list.get('jpg_output_path')[:-17] + \
                             precomp_list.get('jpg_output_path')[-4:] + '_%04d.jpg'

        self.ffmpeg_command = [
            "ffmpeg",
            "-framerate 24",  # 초당프레임
            "-i", self.sequence_path,  # 입력할 파일 이름
            "-q 0",  # 출력품질 정함(숫자가 높을 수록 품질이 떨어짐)
            "-threads 8",  # 속도향상을 위해 멀티쓰레드를 지정
            "-c:v", "libx264",  # 코덱
            "-pix_fmt", "yuv420p",  # 포맷양식
            "-y",  # 출력파일을 쓸 때 같은 이름의 파일이 있어도 확인없이 덮어씀
            "-loglevel", "debug",
            f'{precomp_list.get("video_output_path")}.mov'
        ]

        self.output_dir = os.path.dirname(precomp_list.get("video_output_path"))
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

        self.ffmpeg_cmd = (' '.join(str(s) for s in self.ffmpeg_command))
        self.cmd_list.append(self.ffmpeg_cmd)
        self.total_frame_list.append(total_frame)

        cmd_list = self.cmd_list
        total_frame_list = self.total_frame_list

        return cmd_list, total_frame_list

