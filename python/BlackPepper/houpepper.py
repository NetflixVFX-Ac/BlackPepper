import os
import glob
import numpy as np
from BlackPepper.pepper import Houpub
import shutil
from BlackPepper.ffmpeg_process_bar import FFmpegMainWindow
from BlackPepper.mantra_process_bar import MantraMainWindow
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
        """


        Args:
            abc_tree_all:

        Returns:

        """
        self._abc_tree_all = abc_tree_all

    @property
    def abc_tree_path(self):
        return self._abc_tree_path

    @abc_tree_path.setter
    def abc_tree_path(self, abc_tree_path):
        """


        Args:
            abc_tree_path:

        Returns:

        """
        self._abc_tree_path = abc_tree_path

    @property
    def abc_range(self):
        return self._abc_range

    @abc_range.setter
    def abc_range(self, abc_range):
        """


        Args:
            abc_range:

        Returns:

        """
        self._abc_range = abc_range

    def set_abc_cam_tree(self, abc_path):
        """


        Args:
            abc_path:

        Returns:

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
        """


        Args:
            abc_tree_all:

        Returns:

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


        Args:
            abc_path:

        Returns:

        """
        file_name = abc_path
        if 'abc' not in file_name[-3:]:
            print('No filename entered for Alembic scene.')
            return False
        else:
            abc.alembicClearArchiveCache(file_name)
            return True

    def set_cam_view(self, cam):
        """


        Args:
            cam:

        Returns:

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
        """



        Args:
            cam:

        Returns:

        """
        # abc_range : (0.041666666666666664, 10.0)
        # abc_range * hou.fps() : (1, 240)
        for f in range(int(self.abc_range[0] * hou.fps()), int(self.abc_range[1] * hou.fps()) + 1):
            cam_resolution = abc.alembicGetCameraResolution(self.abc_path, cam, float(f) / hou.fps())
            if cam_resolution != None:
                self.cam_resolution.append(cam_resolution)
                return True

    def get_cam_xform(self, cam):
        """



        Args:
            cam:

        Returns:

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
        """



        Args:
            key:
            node:
            parm:

        Returns:

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
        """



        Args:
            abc_path:

        Returns:

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
        """



        Args:
            hip_path:
            abc_path:
            saved_path:

        Returns:

        """
        hou.hipFile.load(hip_path)
        self.set_cam_create(abc_path)
        hou.hipFile.save(file_name=saved_path)
        self.cam_list.clear()
        self.cam_path.clear()

    def set_mantra_for_render(self, hip_path, output_path):
        cam_setting = f'/obj/{self.cam_node}/'
        basename = os.path.basename(hip_path)
        home_path = os.path.expanduser('~')
        temp_path = os.path.join(home_path+'/temp', basename)
        if not os.path.isdir(home_path+'/temp'):
            os.makedirs(home_path+'/temp')
        shutil.copyfile(hip_path, temp_path)
        hou.hipFile.load(temp_path)
        root = hou.node('/out')
        if root is not None:
            n = root.createNode('ifd')
            n.parm('camera').set(cam_setting)
            n.parm('vm_picture').set(f'{output_path[:-8]}$F4.jpg')
            n.parm('trange').set(1)
            for i in n.parmTuple('f'):
                i.deleteAllKeyframes()
            n.parmTuple('f').set([self.abc_range[0] * hou.fps(), 3, 1])
            n.parm('vm_verbose').set(1)
            n.parm("execute").pressButton()
            app = QtWidgets.QApplication()
            w = MantraMainWindow(n.parm('vm_verbose').set(1), self.abc_range[1] * hou.fps())
            w.show()
            app.exec_()

        output_dir = os.path.dirname(output_path) + '/*.jpg'
        error_dir = os.path.dirname(output_path) + '/*.jpg.mantra_checkpoint'
        file_list = glob.glob(output_dir)
        error_list = glob.glob(error_dir)
        if len(file_list) == self.abc_range[1] * hou.fps():
            if len(error_list) == 0:
                shutil.rmtree(home_path+'/temp')
            else:
                print("render error")
        else:
            print("missing sequence frame")


    def set_ffmpeg_seq_to_mov(self, seq_path, output_path):
        """



        Args:
            seq_path:
            output_path:

        Returns:

        """
        output_dir = os.path.dirname(output_path)
        seq_dir = os.path.dirname(seq_path)
        sequence_path = seq_path[:-8] + '%04d.jpg'
        print('seq_dir :', seq_dir)
        print('sequence_path :', sequence_path)
        command = [
            'ffmpeg',
            "-framerate", str(hou.fps()),  # 초당프레임
            "-i", sequence_path,  # 입력할 파일 이름
            "-q 0",  # 출력품질 정함(숫자가 높을 수록 품질이 떨어짐)
            "-threads 8",  # 속도향상을 위해 멀티쓰레드를 지정
            "-c:v", "prores_ks",  # 코덱
            "-pix_fmt", "yuv420p",  # 포맷양식
            "-y",  # 출력파일을 쓸 때 같은 이름의 파일이 있어도 확인없이 덮어씀
            "-loglevel", "debug",  # 인코딩 과정로그를 보여줌
            output_path
        ]
        cmd = (' '.join(str(s) for s in command))
        print(cmd)
        print("output_dir :", output_dir)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        app = QtWidgets.QApplication()
        w = FFmpegMainWindow(cmd, seq_dir)
        w.show()
        app.exec_()


def main():
    pepper = Houpub()
    pepper.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")
    pepper.project = 'PEPPER'
    pepper.asset = 'temp_breaking_glass'
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
        output_type_name = 'JPG'
        fx_output = pepper.output_file_path(output_type_name, fx_type_name)
        output_type_name = 'movie_file'
        mov_output = pepper.output_file_path(output_type_name, fx_type_name)
        print("fx_path :", fx_path)
        print("next_fx_path :", next_fx_path)
        print("fx_output :", fx_output)
        print("layout_output_path :", layout_output_path)
        print("mov_output :", mov_output)
        hou_pepper.set_fx_working_for_shot(simulation_path, layout_output_path,
                                           f'{next_fx_path}.{pepper.software.get("file_extension")}')
        # hou_pepper.set_mantra_for_render(f'{next_fx_path}.{pepper.software.get("file_extension")}', fx_output)
        print("hou_cam_node :", hou_pepper.cam_node)
        if not QtWidgets.QApplication.instance():
            app = QtWidgets.QApplication(sys.argv)
        else:
            app = QtWidgets.QApplication.instance()
        m = MantraMainWindow(f'{next_fx_path}.{pepper.software.get("file_extension")}', fx_output,
                             layout_output_path, hou_pepper.cam_node, hou_pepper.abc_range[1]*hou.fps())
        m.resize(800, 600)
        m.move(1000, 250)
        m.show()
        app.exec_()
        f = FFmpegMainWindow(fx_output, mov_output, hou.fps())
        f.resize(800, 600)
        f.move(1000, 250)
        f.show()
        app.exec_()
        # BlackPepper.publish_working_file(fx_type_name)
        # hou_pepper.set_ffmpeg_seq_to_mov(fx_output, mov_output)


if __name__ == "__main__":
    main()


