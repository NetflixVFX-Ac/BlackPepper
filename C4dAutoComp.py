##Benjamin Rohel - 11/10/2011###

##################################################################
########### SingleBranch AutoComp for Cinema 4D files ############
import nuke
import os.path


########## Open Panel for selecting files ##########
p = nuke.Panel('C4D AutoComp')
p.setWidth(500)
p.addBooleanCheckBox('3D comp', True)
p.addFilenameSearch('exr file', '/tmp')
p.addClipnameSearch('fbx camera', '/tmp')
ret = p.show()
ret = p.value('exr file')
ret= p.value('fbx camera')
ret= p.value('3D comp')
print p.value('exr file')
print p.value('fbx camera')
fileNameSeq= p.value('exr file')
cameraName=p.value('fbx camera')
dddComp = p.value('3D comp')
print dddComp
########### Read and SET EXR file ################################

def C4dRead(fileNameSeq):
    node=nuke.nodes.Read(xpos=0,ypos=0)
    lastf =int(fileNameSeq.split("-")[-1])
    firstf =int(node['first'].getValue())
    node['last'].setValue(lastf)
    fRange =  [firstf,lastf]
    fileName = fileNameSeq.split(" ")
    fileName = fileName[0]
    node['file'].setValue(fileName)
    node['name'].setValue("c4dread")
    c4dreadFormat = node.format()
    c4dreadFormat.setName("C4DFormat")
    w = str(c4dreadFormat.width())
    h = str(c4dreadFormat.height())
    readFt= w + " "+ h + " C4D Format"
    scriptFormats = nuke.formats()
    nuke.addFormat ( readFt )
    nuke.root()['format'].setValue( "C4D Format" )    
    return fRange



fRange=C4dRead(fileNameSeq)
lf=fRange[1]
ff=fRange[0]
print "Sequence is "+ str(lf-ff+1) + " frames."





####################################################################
########### Comp in a Single Branch ################################



def SingleBranchComp ():
    r=nuke.toNode("c4dread")
    channels=r.channels()
    
    layers = [c.split('.')[0] for c in channels]
    layers = list( set([c.split('.')[0] for c in channels]) )
    layers.sort()
    layers=layers[0:-1]
    for n in layers : 
        if "Diffuse" in n : 
            m= nuke.nodes.Merge2( operation='plus', inputs=[ r, nuke.nodes.Grade( inputs=[r] , channels=n) ], Achannels= n, Bchannels= 'none', output='rgb' )
        
        else : 
            g=nuke.nodes.Grade( inputs=[m], channels=n )
            if ("Shadow"in n )or ("Ambient_Occlusion"in n ) : 
                m= nuke.nodes.Merge2( operation='multiply', inputs=[ g,g], Achannels= n, Bchannels= 'rgba', output='rgb',)
            else :
                m= nuke.nodes.Merge2( operation='plus', inputs=[g, g ], Achannels= n, Bchannels= 'rgba', output='rgb',)
    return m 


lastmerge=SingleBranchComp()

if dddComp is True :
    
    ##################################################################
    ########### Read and SET C4D Cameras ################################
    def LoadCamera (cameraName):
        cam1 = nuke.nodes.Camera2 (name = "cam1")
        cam2 = nuke.nodes.Camera2(name = "cam2")
        
        nuke.show(cam1) 
        cam1['read_from_file'].setValue(True)
        
        cam1['file'].setValue(cameraName)
        cam1['read_from_file'].setValue(False)
        
        cam2['focal'].setExpression("cam1.focal")
        cam2['haperture'].setExpression("cam1.haperture")
        cam2['vaperture'].setExpression("cam1.vaperture")
        cam2['near'].setExpression("cam1.near")
        cam2['far'].setExpression("cam1.far")
        cam2['rotate'].setExpression("cam1.rotate.z",0)
        cam2['rotate'].setExpression("(cam1.rotate.y)-90",1)
        cam2['rotate'].setExpression("-(cam1.rotate.x)",2)
        cam2['translate'].copyAnimations(cam1['translate'].animations())
        return [cam1, cam2]
    
    cams=LoadCamera (cameraName)
    cam1=cams[0]
    cam2=cams[1]
    
    
    ##################################################################
    ########### Bake Camera Animation ################################
    def bakeCamera(ff,lf):
        
        for knob in nuke.toNode("cam2").knobs().values():
            if knob.hasExpression():
                if knob.singleValue():
                    aSize = 1
                else:
                    aSize = knob.arraySize()
                for index in range(aSize):
                    if knob.hasExpression(index):
                        anim = knob.animation(index)
                        f = ff
                        while f <= lf:
                            knob.setValueAt(anim.evaluate(f), f, index)
                            f += 1
                        knob.setExpression("curve", index)
                        if knob.animation(index).constant():
                            knob.clearAnimated(index)
        
        print "Camera is Baked"
    
    
    bakeCamera(ff, lf)
    
    ##################################################################
    ################# Create 3D Scene ################################
    #Create 3DScene
    
    def Built3dScene (cam1,cam2):
        
        # Create a Constant with C4D Format value
        ct = nuke.createNode('Constant')
        ct['format'].setValue ('C4D Format')
        ct.setName("BackGround")
        sc=nuke.nodes.Scene()
        sc.setName("C4DScene")
        rnd=nuke.nodes.ScanlineRender()
        rnd.setInput(1,sc)
        rnd.setInput(2,cam2)
        rnd.setInput(0,ct)
        m= nuke.nodes.Merge2( operation='plus', inputs=[ lastmerge, rnd])
        xPos = rnd.xpos()
        yPos = rnd.ypos()
        ct.setYpos( yPos-24 )
        ct.setXpos (xPos-150)
        sc.setXpos (xPos+150)
        sc.setYpos (yPos-21)
        cam2.setXpos(xPos+10)
        return m
    
    
    m=Built3dScene (cam1,cam2)
    nuke.delete(cam1)
    nuke.connectViewer(0,m)
    v=nuke.toNode("Viewer1")
    mPosX= m.xpos()
    mPosY= m.ypos()
    v.setXpos(mPosX)
    v.setYpos(mPosY+50)
    ####################
    
    
    end=nuke.message( "AutoComp done.\nSequence is "+ str(lf-ff+1) + " frames.")



