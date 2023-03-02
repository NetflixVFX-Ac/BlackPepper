import hou
import _alembic_hom_extensions as abc
import numpy as np
from pepper import Houpub


class HouPepper:
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

    @property
    def abc_path(self):
        return self._abc_path

    @abc_path.setter
    def abc_path(self, abc_path):
        self._abc_path = abc_path

    @property
    def abc_tree_all(self):
        return self._abc_tree_all

    @abc_tree_all.setter
    def abc_tree_all(self, abc_tree_all):
        self._abc_tree_all = abc_tree_all

    @property
    def abc_tree_path(self):
        return self._abc_tree_path

    @abc_tree_path.setter
    def abc_tree_path(self, abc_tree_path):
        self._abc_tree_path = abc_tree_path

    @property
    def abc_range(self):
        return self._abc_range

    @abc_range.setter
    def abc_range(self, abc_range):
        self._abc_range = abc_range

    def set_abc_cam_tree(self, abc_path):
        self.abc_path = abc_path
        if len(self.abc_path) > 0:
            self.true = self.check_abc(self.abc_path)
            if self.true:
                # abcTreeAll :  ('ABC', 'unknown', (('cam1', 'xform', (('cam1Camera', 'camera', ()),)),))
                # abcTreePath :  ['/', '/', '/cam1', '/cam1', '/cam1/cam1Camera', '/cam1/cam1Camera']
                self.abc_tree_all = abc.alembicGetSceneHierarchy(self.abc_path, '')
                self.abc_tree_path = abc.alembicGetObjectPathListForMenu(self.abc_path)
                self.get_abc_cam_tree(self.abc_tree_all)
        print("abc_path :", self.abc_path)
        print("cam_path :", self.cam_path)
        print("cam_list :", self.cam_list)
        self.abc_range = abc.alembicTimeRange(self.abc_path)

    def get_abc_cam_tree(self, abc_tree_all):
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
        file_name = abc_path
        if 'abc' not in file_name[-3:]:
            print('No filename entered for Alembic scene.')
            return False
        else:
            abc.alembicClearArchiveCache(file_name)
            return True

    def set_cam_view(self, cam):
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
        # abc_range : (0.041666666666666664, 10.0)
        # abc_range * hou.fps() : (1, 240)
        for f in range(int(self.abc_range[0] * hou.fps()), int(self.abc_range[1] * hou.fps()) + 1):
            cam_resolution = abc.alembicGetCameraResolution(self.abc_path, cam, float(f) / hou.fps())
            if cam_resolution != None:
                self.cam_resolution.append(cam_resolution)
                return True

    def get_cam_xform(self, cam):
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
        self.set_abc_cam_tree(abc_path)
        name = [abc.alembicGetSceneHierarchy(abc_path, i)[0] for i in self.cam_path]
        print("name :", name)
        # cam_path : ['/cam1/cam1Camera']
        for cam in self.cam_path:
            # cam_node = cam1Camera
            cam_node = hou.node('/obj').createNode('cam', name[self.cam_path.index(cam)])
            self.cam_node = cam_node
            print("cam_node :", self.cam_node)
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
        hou.hipFile.load(hip_path)
        self.set_cam_create(abc_path)
        hou.hipFile.save(file_name=saved_path)
        self.cam_list.clear()
        self.cam_path.clear()

    def set_mantra_for_render(self, hip_path, output_path):
        cam_setting = f'/obj/{self.cam_node}/'
        print(cam_setting)
        print(self.abc_range)
        hou.hipFile.load(hip_path)
        root = hou.node('/out')
        if root != None:
            n = root.createNode('ifd')
            print(output_path[:-30])
            n.parm('camera').set(cam_setting)
            n.parm('vm_picture').set(f'{output_path[:-8]}$F4.jpg')
            n.parm('trange').set(1)
            for i in n.parmTuple('f'):
                i.deleteAllKeyframes()
            n.parmTuple('f').set([self.abc_range[0] * hou.fps(), self.abc_range[1] * hou.fps(), 1])
            n.parm("execute").pressButton()

    def set_ffmpeg_seq_to_mov(self, seq_path, output_path):
        framerate = hou.fps()
        sequence_file_path = seq_path

pepper = Houpub()
pepper.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")
pepper.project = 'PEPPER'
pepper.asset = 'temp_dancing_particle'
pepper.entity = 'asset'
# need software handling method
pepper.software = 'hiplc'
simulation_type_name = 'simulation'
simulation_path = pepper.working_file_path(simulation_type_name, input_num=1)
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
    # pepper.publish_working_file(fx_type_name)
    fx_path = pepper.working_file_path(fx_type_name)
    next_fx_path = pepper.make_next_working_path(fx_type_name)
    output_type_name = "JPG"
    fx_output = pepper.output_file_path(output_type_name, fx_type_name)
    print("fx_path :", fx_path)
    print("next_fx_path :", next_fx_path)
    print("fx_output :", fx_output)
    print("layout_output_path :", layout_output_path)
    hou_pepper.set_fx_working_for_shot(simulation_path, layout_output_path,
                                       f'{next_fx_path}.{pepper.software.get("file_extension")}')
    # hou_pepper.set_mantra_for_render(fx_path, fx_output)
    # pepper.publish_working_file(fx_type_name)

