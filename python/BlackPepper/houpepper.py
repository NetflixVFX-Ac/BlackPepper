import numpy as np
from BlackPepper.pepper import Houpub
from BlackPepper.ffmpeg_process_bar import FFmpegMainWindow
from BlackPepper.mantra_process_bar_w import MantraMainWindow
from PySide2 import QtWidgets
import hou
import _alembic_hom_extensions as abc
import sys

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
        self.cam_node = None
        self._abc_path = None
        self._abc_tree_all = None
        self._abc_tree_path = None
        self._abc_range = None

        # self.aperture = []
        # self.aspect = []
        # self.forcal = [] ..... self.winsizey = []
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
                # abcTreeAll :  ('ABC', 'unknown', (('cam1', 'xform', (('cam1Camera', 'camera', ()),)),))
                # abcTreePath :  ['/', '/', '/cam1', '/cam1', '/cam1/cam1Camera', '/cam1/cam1Camera']
                self.abc_tree_all = abc.alembicGetSceneHierarchy(self.abc_path, '')
                self.abc_tree_path = abc.alembicGetObjectPathListForMenu(self.abc_path)
                self.get_abc_cam_tree(self.abc_tree_all)
        self.abc_range = abc.alembicTimeRange(self.abc_path)

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
        # nodename : ABC -> cam1 -> cam1Camera
        # nodetype : unknown -> xform -> camera
        # nodechildren : (('cam1', 'xform', (('cam1Camera', 'camera', ()),)),) -> (('cam1Camera', 'camera', ()),) -> ()
        if node_type == 'camera':
            # node_name : cam1Camera
            # nodechildren : ()
            # cam_list : ['cam1Camera']
            self.cam_list.append(node_name)
            # abcTreePath :  ['/', '/', '/cam1', '/cam1', '/cam1/cam1Camera', '/cam1/cam1Camera']
            for x in self.abc_tree_path:
                # node_name : cam1Camera
                if node_name in x:
                    # camlipath : /cam1/cam1Camera
                    camlipath = x
            if camlipath not in self.cam_path:
                # cam_path : ['/cam1/cam1Camera']
                self.cam_path.append(camlipath)
        else:
            # node_name : cam1
            # node_type : xform
            # nodechildren : (('cam1Camera', 'camera', ()),)
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


        Args:
            cam: cam node created in houdini

        """
        # abc_range : (0.041666666666666664, 10.0)
        # abc_range * hou.fps() : (1, 240)
        for f in range(int(self.abc_range[0] * hou.fps()), int(self.abc_range[1] * hou.fps()) + 1):
            camera_dict = abc.alembicGetCameraDict(self.abc_path, cam, float(f) / hou.fps())
            self.filmaspectratio.append(camera_dict['filmaspectratio'])
            if camera_dict != None:
                # self.aperture = [{},]
                for parm_name in self.hou_cam_parm_name:
                    exec("self.{}.append({})".format(parm_name, camera_dict.get(parm_name)))

    def get_cam_resolution(self, cam):
        """Alembic file에 있는 카메라가 가진 frame range에 frame rate를 곱하여 real time frame 동안의 \n
        camera 해상도 값을 가져와 Houdini 내 새로 생성한 카메라 해상도 값에 넣어준다.


        Args:
            cam: cam node created in houdini

        """
        # abc_range : (0.041666666666666664, 10.0)
        # abc_range * hou.fps() : (1, 240)
        for f in range(int(self.abc_range[0] * hou.fps()), int(self.abc_range[1] * hou.fps()) + 1):
            cam_resolution = abc.alembicGetCameraResolution(self.abc_path, cam, float(f) / hou.fps())
            if cam_resolution != None:
                self.cam_resolution.append(cam_resolution)
                return True

    def get_cam_xform(self, cam):
        """Alembic file에 있는 카메라가 가진 frame range에 frame rate를 곱하여 real time frame 동안의 \n
        Houdini 내 Matrix4 모듈을 사용하여 camera translate, rotate, scale 값을 가져온다.


        Args:
            cam: camera node created in houdini

        Returns (list): translate, rotate, scale

        """
        # abc_range : (0.041666666666666664, 10.0)
        # abc_range * hou.fps() : (1, 240)
        translate = []
        rotate = []
        scale = []
        # shear = []
        for f in range(int(self.abc_range[0] * hou.fps()), int(self.abc_range[1] * hou.fps())):
            xform = abc.getWorldXform(self.abc_path, cam, float(f) / hou.fps())[0]
            xf = hou.Matrix4(xform)
            translate.append(xf.extractTranslates())
            rotate.append(xf.extractRotates())
            scale.append(xf.extractScales())
            # shear.append(xf.extractShears())
        return translate, rotate, scale

    def set_cam_key(self, key, node, parm):
        """key에 저장된 x, y, z 값(traslate, rotate, scale)을 Houdini obj에 만든 camera parameter에 넣어준다. \n
        numpy convolution 메소드를 사용하여 Key 값이 변하는 구간에서 값들을 읽어 camera parameter에 넣어준다.

        Args:
            key(list): x, y, z position
            node(str): camera node created in houdini
            parm: 't' (translate) or 'r' (rotate) or 's' (scale)

        """
        # self.set_cam_key(tr, cam_node, 't')
        J = ['x', 'y', 'z', 'w']
        # key_np : matrix - tr : [[x1, y1 ,z1],
        #                         [x2,y2,z2] ...] tx, ty, tz rx,rt, rz
        key_np = np.array(key)
        s = [1, -1]
        # frame : 0  k : [x1,y1,z1]
        for frame, k in enumerate(key_np):
            try:
                num_key = len(k)
                if num_key > 1:
                    # n : 0, key_index : x1 = 9.42313...
                    # n : 1, key_index : y1 = 3.23213...
                    # n : 2, key_index : z1 = 2.23423...
                    for n, key_index in enumerate(k):
                        slope = np.convolve(list(map(lambda x: x[1], key_np)), s, mode='same') / (len(s) - 1)
                        if slope[frame] != 0:
                            keyframe = hou.Keyframe(key_index, hou.frameToTime(frame + 1))
                            # tx, ty, tz - traslate / rx, ry, rz - rotate / sx, sy, sz = scale
                            node.parm('{}{}'.format(parm, J[n])).setKeyframe(keyframe)
            except:
                slope = np.convolve(list(map(lambda x: x, key_np)), s, mode='same') / (len(s) - 1)
                if slope[frame] != 0:
                    keyframe = hou.Keyframe(k, hou.frameToTime(frame + 1))
                    node.parm('{}'.format(parm)).setKeyframe(keyframe)

    def set_cam_create(self, abc_path):
        """Houdini obj 경로에 camera node를 만들고, Alembic file에 있는 camera의 정보 값들을 \n
        obj 안에 만든 camera에 넣어준다. 정보는 camera의 dictionary 값, camera resolution, camera x,y,z position에 해당된다.

        Args:
            abc_path: Alembic file path

        """
        self.set_abc_cam_tree(abc_path)
        name = [abc.alembicGetSceneHierarchy(abc_path, i)[0] for i in self.cam_path]
        # cam_list : ['cam1Camera']
        # cam_path : ['/cam1/cam1Camera']
        for cam in self.cam_path:
            # cam_node = cam1Camera
            cam_node = hou.node('/obj').createNode('cam', name[self.cam_path.index(cam)])
            self.cam_node = cam_node
            self.set_cam_view(cam)
            # check_resolution : True
            check_resolution = self.get_cam_resolution(cam)
            # tr, ro, sc : hou.Vector3
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
        """Template에 casting된 shot layout output file인 Alembic의 카메라 정보를 가진 cam node를 저장하여 \n
        shot fx working file path에 저장한다.


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


def main():
    pepper = Houpub()
    pepper.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")
    pepper.project = 'PEPPER'
    pepper.asset = 'temp_fire'
    pepper.entity = 'asset'
    # need software handling method
    pepper.software = 'hipnc'
    simulation_type_name = 'simulation'
    simulation_path = pepper.working_file_path(simulation_type_name)
    casted_shots = pepper.get_casting_path_for_asset()
    hou_pepper = HouPepper()

    for shot in casted_shots:
        pepper.sequence = shot.get('sequence_name')
        pepper.shot = shot.get('shot_name')
        pepper.entity = 'shot'
        layout_type_name = 'layout'
        output_type_name = 'camera_cache'
        layout_output_path = pepper.output_file_path(output_type_name, layout_type_name)
        pepper.software = 'hipnc'
        fx_type_name = 'fx'
        # BlackPepper.publish_working_file(fx_type_name)
        fx_path = pepper.working_file_path(fx_type_name)
        next_fx_path = pepper.make_next_working_path(fx_type_name)
        output_type_name = 'jpg_sequence'
        fx_output = pepper.output_file_path(output_type_name, fx_type_name)
        fx_next_output = pepper.make_next_output_path(output_type_name, fx_type_name)
        output_type_name = 'movie_file'
        mov_output = pepper.output_file_path(output_type_name, fx_type_name)
        mov_next_output = pepper.make_next_output_path(output_type_name, fx_type_name)
        print("fx_path :", fx_path)
        print("next_fx_path :", next_fx_path)
        print("fx_output :", fx_output)
        print("layout_output_path :", layout_output_path)
        print("mov_output :", mov_output)
        print("fx_next_output :", fx_next_output)
        print("mov_next_output :", mov_next_output)
        hou_pepper.set_fx_working_for_shot(simulation_path, layout_output_path,
                                           f'{next_fx_path}.{pepper.software.get("file_extension")}')
        # hou_pepper.set_mantra_for_render(f'{next_fx_path}.{pepper.software.get("file_extension")}', fx_output)
        print("hou_cam_node :", hou_pepper.cam_node)
        if not QtWidgets.QApplication.instance():
            app = QtWidgets.QApplication(sys.argv)
        else:
            app = QtWidgets.QApplication.instance()
        m = MantraMainWindow(f'{next_fx_path}.{pepper.software.get("file_extension")}', fx_next_output,
                             layout_output_path, hou_pepper.cam_node, hou_pepper.abc_range[1]*hou.fps())
        m.resize(800, 600)
        m.move(1000, 250)
        m.show()
        app.exec_()
        f = FFmpegMainWindow(fx_next_output, mov_next_output, hou.fps())
        f.resize(800, 600)
        f.move(1000, 250)
        f.show()
        app.exec_()
        # BlackPepper.publish_working_file(fx_type_name)
        # hou_pepper.set_ffmpeg_seq_to_mov(fx_output, mov_output)

#
# if __name__ == "__main__":
#     main()


