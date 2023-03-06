import os
import _alembic_hom_extensions as abc
import numpy as np

try:
    from hou import ui
except:
    ui = None


def selFile():
    return hou.ui.selectFile(start_directory='$HIP', file_type=hou.fileType.Geometry, title='Select ABC Camera File')


class ImportABC:
    def __init__(self, seletFile):
        import _alembic_hom_extensions as abc
        self.camList = []
        self.camPath = []
        self.file = seletFile
        # file : file : /mnt/project/hook/BlackPepper/shots/sq01/0010/layout/working/v001/pepper_sq01_0010_layout_001.abc
        if len(self.file) > 0:
            self.true = self.BuildHierarchyRoot()
            if self.true:
                # abcTreeAll :  ('ABC', 'unknown', (('cam1', 'xform', (('cam1Camera', 'camera', ()),)),))
                # abcTreePath :  ['/', '/', '/cam1', '/cam1', '/cam1/cam1Camera', '/cam1/cam1Camera']
                self.abcTreeAll = abc.alembicGetSceneHierarchy(self.file, '')
                self.abcTreePath = abc.alembicGetObjectPathListForMenu(self.file)
                self.getABCCamTree(self.abcTreeAll)

    def getABCCamTree(self, abcTreeAll):
        nodeName = abcTreeAll[0]
        nodeType = abcTreeAll[1]
        nodeChildren = abcTreeAll[2]
        # nodename : ABC -> cam1 -> cam1Camera
        # nodetype : unknown -> xform -> camera
        # nodechildren : (('cam1', 'xform', (('cam1Camera', 'camera', ()),)),) -> (('cam1Camera', 'camera', ()),) -> ()
        if nodeType == 'camera':
            # camera nodename :  cam1Camera
            self.camList.append(nodeName)
            # camlist : ['cam1Camera']
            # camera abcTreePath : ['/', '/', '/cam1', '/cam1', '/cam1/cam1Camera', '/cam1/cam1Camera']
            for x in self.abcTreePath:
                # camer x : / -> / -> /cam1 -> /cam1 -> /cam1/cam1Camera
                # nodename : cam1Camera
                if nodeName in x:
                    # if nodeName in x : cam1Camera
                    camlipath = x
            # camlipath : /cam1/cam1Camera
            if camlipath not in self.camPath:
                self.camPath.append(camlipath)
            # camPath : ['/cam1/cam1Camera']
        else:
            for children in nodeChildren:
                self.getABCCamTree(children)

    def getCamList(self):
        import _alembic_hom_extensions as abc
        # getCamList true : True
        # getCamList camlist : ['cam1Camera']
        if self.true:
            index = hou.ui.selectFromList(self.camList, title='Select Camera Node')
            # index : (0,)
            camlist = [self.camPath[i] for i in index]
            return camlist

    def BuildHierarchyRoot(self):
        import _alembic_hom_extensions as abc
        fileName = self.file
        if 'abc' not in fileName:
            if ui:
                ui.displayMessage(title='No Filename',
                                  text='Please enter an Alembic file to load.',
                                  severity=hou.severityType.Warning)
            else:
                print('No filename entered for Alembic scene.')
            return False
        else:
            abc.alembicClearArchiveCache(fileName)
            return True


class ABC_Work:
    def __init__(self, abcPath, abcFile):
        import _alembic_hom_extensions as abc
        self.abcFile = abcFile
        self.abcPath = abcPath
        print("ABC_Work abcFile :", self.abcFile)
        print("ABC_Work abcPath :", self.abcPath)
        self.name = [abc.alembicGetSceneHierarchy(self.abcFile, i)[0] for i in abcPath]
        for i in abcPath:
            print("name test i :", i)
            check = abc.alembicGetSceneHierarchy(self.abcFile, i)[0]
            print("check :", check)
        print("ABC_Work name :", self.name)

        self.houCamParmName = (
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
        for str in self.houCamParmName:
            # exec : None
            exec("self.{}=[]".format(str))
        # alembicTimeRange : (0.041666666666666664, 10.0)
        self.abcRange = abc.alembicTimeRange(self.abcFile)
        self.camRes = []
        self.filmaspectratio = []

    def setCamView(self, cam):
        import _alembic_hom_extensions as abc
        # alembicTimeRange : (0.041666666666666664, 10.0) getXfrom range: range(1, 240) ABC_Work abcFile :
        # /mnt/project/hook/BlackPepper/shots/sq01/0010/layout/working/v001/pepper_sq01_0010_layout_001.abc cam :
        # /cam1/cam1Camera
        for t in range(int(self.abcRange[0] * hou.fps()), int(self.abcRange[1] * hou.fps()) + 1):
            cameraDict = abc.alembicGetCameraDict(self.abcFile, cam, t / hou.fps())
            self.filmaspectratio.append(cameraDict['filmaspectratio'])
            if cameraDict != None:
                for parmName in self.houCamParmName:
                    exec("self.{}.append({})".format(parmName, cameraDict.get(parmName)))

    def getCamRes(self, cam):
        import _alembic_hom_extensions as abc
        # alembicTimeRange : (0.041666666666666664, 10.0) getXfrom range: range(1, 240) ABC_Work abcFile :
        # /mnt/project/hook/BlackPepper/shots/sq01/0010/layout/working/v001/pepper_sq01_0010_layout_001.abc cam :
        # /cam1/cam1Camera
        for t in range(int(self.abcRange[0] * hou.fps()), int(self.abcRange[1] * hou.fps()) + 1):
            resTuple = abc.alembicGetCameraResolution(self.abcFile, cam, t)
            if resTuple != None:
                self.camRes.append(self.camRes)
                return True

    def getXfrom(self, cam):
        import _alembic_hom_extensions as abc
        tr = []
        rot = []
        scl = []
        she = []
        # alembicTimeRange : (0.041666666666666664, 10.0)
        # getXfrom range: range(1, 240)
        # print("getXfrom range:", range(int(self.abcRange[0] * hou.fps()), int(self.abcRange[1] * hou.fps())))
        for t in range(int(self.abcRange[0] * hou.fps()), int(self.abcRange[1] * hou.fps())):
            xfrom = abc.getWorldXform(self.abcFile, cam, float(t) / hou.fps())[0]
            xf = hou.Matrix4(xfrom)
            tr.append(xf.extractTranslates())
            rot.append(xf.extractRotates())
            scl.append(xf.extractScales())
            she.append(xf.extractShears())
            if t == 1:
                print(float(t) / hou.fps())
                print(xf.extractTranslates(), xf.extractRotates(), xf.extractScales())
        return tr, rot, scl

    def setKey(self, key, node, parm):
        import numpy as np
        J = ['x', 'y', 'z', 'w']
        # convertKey = ['cam1Camera']
        convertKey = [a for a in key]
        keyNp = np.array(convertKey)
        s = [1, -1]
        # enumerath(['cam1Camera']
        # frame : 0 k : cam1Camera
        for frame, k in enumerate(key):
            try:
                numKEY = len(k)
                if numKEY > 1:
                    for aix, keyIndex in enumerate(k):
                        slope = np.convolve(list(map(lambda x: x[1], keyNp)), s, mode='same') / (len(s) - 1)
                        if slope[frame] != 0:
                            keyframe = hou.Keyframe(keyIndex, hou.frameToTime(frame + 1))
                            node.parm('{}{}'.format(parm, J[aix])).setKeyframe(keyframe)
            except:
                slope = np.convolve(list(map(lambda x: x, keyNp)), s, mode='same') / (len(s) - 1)
                if slope[frame] != 0:
                    keyframe = hou.Keyframe(k, hou.frameToTime(frame + 1))
                    node.parm('{}'.format(parm)).setKeyframe(keyframe)

    def createCam(self):
        # ABC_Work abcPath : ['/cam1/cam1Camera']
        for cam in self.abcPath:
            # camNode : cam1Camera
            # self.abcPath.index(cam) : 0
            camNode = hou.node('/obj').createNode('cam', self.name[self.abcPath.index(cam)])
            self.setCamView(cam)
            hasRes = self.getCamRes(cam)
            t, r, s = self.getXfrom(cam)
            self.setKey(t, camNode, 't')
            self.setKey(r, camNode, 'r')
            self.setKey(s, camNode, 's')
            camNode.parmTuple('t').lock((1, 1, 1))
            camNode.parmTuple('r').lock((1, 1, 1))
            camNode.parmTuple('s').lock((1, 1, 1))
            for str in self.houCamParmName:
                hs = "self.setKey(self.{},camNode,'{}')".format(str, str)
                exec(hs)
            if hasRes:
                self.setKey(self.camRes, camNode, 'res')
            else:
                camNode.parm('resx').set(2048)
                camNode.parm('resy').set(int(2048 / self.filmaspectratio[0]))


abcFile = selFile()
abcPath = ImportABC(abcFile).getCamList()
ABC_Work(abcPath, abcFile).createCam()
