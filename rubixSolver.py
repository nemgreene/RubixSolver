import maya.cmds as m
import pymel.core as pmc
from pymel.core.datatypes import Vector
from random import random
import uuid
#vector region
#region
# vector substration
def vecsub(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
# vector crossproduct
def veccross(x, y):
    v = [0, 0, 0]
    v[0] = x[1]*y[2] - x[2]*y[1]
    v[1] = x[2]*y[0] - x[0]*y[2]
    v[2] = x[0]*y[1] - x[1]*y[0]
    return v
def Normal(v0, v1, v2):
    return veccross(vecsub(v0, v1),vecsub(v0, v2))
# calculate normal from 3 verts
def Normal4(v0, v1, v2, v3):
    return veccross(vecsub(v0, v2),vecsub(v1, v3))
#endregion

dictionary = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA"]
whiteList = []
yellowList = []
edgelist=[]
edgesList = []
select = []
kernelList = []
cube = []
visualize = True
# Obj for each node in cube
class Node:
    def __init__(self,id):
        self.id = id
        self.colors = []
        self.faces = []
        self.normalList = []

        cube = m.ls(id)
        shaders = m.listConnections(m.listHistory(cube,f=1),type='lambert')
        for i in range(1,len(shaders)):
            self.colors.append(shaders[i])

    def height(self):
        ret = [0, 0, 0]
        for i in self.normals():
            ret = [ret[0] + i[0], ret[1] + i[1], ret[2] + i[2]]
        return ret

    def name(self):
        return(self.id)

    def normals(self) :
        ret = []
        for c in self.colors:
            ret.append(self.normal(c))
        return ret
    
    
    def normal(self, color):
        self.normalList = []
        m.select(self.id)
        m.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
        m.select(self.id)
        m.hyperShade(smn=1) # that will select the shader
        for i in range(int(len(self.colors))):
            s = m.ls(sl=1)[i + 1] # remember the selected shader
            sg = m.listConnections(color +".oc", s=0, d=1)[0] # figure out the shading group
            # select the faces of the same object with same shader attached
            l = []
            for o in m.sets(sg, q=1):
                if self.id not in o: continue
                l.append(o)
                m.select(l, add=1)
                ns = m.polyInfo(l[0], fn=1)[0]
                null, null, x, y, z = ns.split()
                self.normalList.append([int(float(x)), int(float(y)), int(float(z))])
        m.select(cl=1)
        return(self.normalList[0])

    def selfSelect(self):
        m.select(str(self.id), add=1)
    
    def position(self, str):
        x, y, z = self.height()
        global re
        if str == "left":
            if x < 0 and z < 0:
                return "xNeg"
            if x > 0 and z < 0:
                return "zNeg"
            if x < 0 and z > 0:
                return "zPos"
            if x > 0 and z > 0:
                return "xPos"
        if str == "right":
            if x < 0 and z < 0:
                return "zNeg"
            if x < 0 and z > 0:
                return "xNeg"
            if x > 0 and z < 0:
                return "xPos"
            if x > 0 and z > 0:
                return "zPos"

        # calling func to test which side of cube colored face is on
        else:
            nX, nY, nZ = self.normal(str)
            hX, hY, hZ = self.height()
            if nZ == 1:
                if hX == -1: 
                    return ["left", self.position("left")]
                if hX == 1: 
                    return ["right", self.position("right")]
            if nZ == -1:
                if hX == -1: 
                    return ["right", self.position("right")]
                if hX == 1: 
                    return ["left", self.position("left")]
            if nX == 1:
                if hZ == -1: 
                    return ["right", self.position("right")]
                if hZ == 1: 
                    return ["left", self.position("left")]
            if nX == -1:
                if hZ == -1: 
                    return ["left", self.position("left")]
                if hZ == 1: 
                    return ["right", self.position("right")]
                    # will return face that is not up
            # if nY == 1 and nX == 0 and nZ == 0:
# obj for machine, rotating relative to view
class Handler :
    def __init__(self, face):
        self.face = face
    
    def top(self, dir):
        direction = "+" if dir == "cw" else "-"
        rotator([0, 1, 0], "pos", direction)
    def bottom(self, dir):
        direction = "-" if dir == "cw" else "+"
        rotator([0, 1, 0], "neg", direction)  
    
    def wingRot(self, orientation, dir):
        wings = [1, 0, 0] if "z" in self.face else [0, 0, 1]
        if self.face == "zNeg" or self.face=="xPos":
            dir = "-" if dir == "cw" else "+"
        else:
            dir = "+" if dir == "cw" else "-"
        rotator(wings, orientation, dir)
    
    def left(self, dir):
        orientation = ("pos" if "Neg" in self.face else "neg") if "z" in self.face else ("pos" if "Pos" in self.face else "neg")
        self.wingRot(orientation, dir)
    
    def right(self, dir):
        orientation = ("pos" if "Neg" in self.face else "neg") if "x" in self.face else ("pos" if "Pos" in self.face else "neg")
        self.wingRot(orientation, dir)

    def facing(self, dir):
        loc = [1, 0, 0] if "x" in self.face else [0, 0, 1]
        orientation = "neg" if "Neg" in self.face else "pos"
        dir = ("+" if dir == "cw" else "-")  if "Neg" in self.face else ("-" if dir == "cw" else "+")
        rotator(loc, orientation, dir)

# # generate array of nodes
for index in range(27):
    node = Node(dictionary[index])
    cube.append(node)

def rotator(vec, direction, wise):
    flat = []
    vec = map(lambda x : x * -1 if direction == "neg" else x, vec)
    for i in range(27):
        if vec in cube[i].normals():
            flat.append(cube[i].name())
    m.select(flat)
    m.group(n='rotator')
    m.xform(cp=1)

    vec = map(lambda x :  x if x == 0 else int(wise + "90"), vec)
    m.select(cl=1)
    if(visualize):
        vec= Vector([x for x in vec]) * .05
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        m.refresh()
    else:
        vec= Vector([x for x in vec])
        m.rotate(vec.x, vec.y, vec.z, "rotator", r=1)
        

    m.parent(flat, "cubeGroup")
    m.delete("rotator*")
    # m.xform("rotator", a=1,ws=1, rotation=vec)

def Step__Scramble(num):
    dic = ["x", "y", "z"]
    dir = ["pos", "neg"]
    for i in range(num):
        origin = dic[int(random() * 3)]
        input = map(lambda x : 1 if x == origin else 0, dic)
        rotator(input, dir[int(random() * 2)], "+")
    m.refresh()

def facingFunction(i, color):
    if len(i.colors) >= 2:
        facing = ("x" if i.normal(color)[0] !=0 else "z") + ("Pos" if i.normal(color)[0] + i.normal(color)[2] > 0  else "Neg")
        # facing = ("x" if i.normals()[0][0] !=0 else "z") + ("Pos" if i.normals()[0][0] + i.normals()[0][2] > 0  else "Neg")
        return facing
    if len(i.colors) == 1:
        facing = ("x" if i.normal()[0][0] !=0 else "z") + ("Pos" if i.normals()[0][0] + i.normals()[0][2] > 0  else "Neg")
        return facing

def generateCleanCube():
    try:
        pmc.delete("CubeGroup")
    except:
        pass
    group = pmc.group(em = 1, n = "CubeGroup")
    for index in range(27):
        nodeGeo = pmc.polyCube(n= dictionary[index])
        node = Node(dictionary[index])
        pmc.sets("lambert2SG", e=1, forceElement = nodeGeo[0])
        cube.append(node)
        cube.append(node)
        pmc.polyBevel(pmc.ls(nodeGeo[0] + ".e[*]"), f=.1, oaf=1)
        pmc.parent(nodeGeo[0], group)
        pmc.delete(nodeGeo, ch=1)
        # x coords
        x =(((index % 9) / 3) -1) * -1
        # y coords
        y = (index /9 -1 )* -1
        # z coords
        z = (index % 3 -1) * -1
        translate = Vector(x,y,z, )
        pmc.xform(nodeGeo[0], t=translate)

        # x+ == green
        # x- == blue
        # y + == yellow
        # y- == white
        # z + == orange
        # x- == red

        # colors will manually be assigned for now

        # # color
        # if(x == 1):
        #     faces = pmc.ls(nodeGeo[0] + ".e[3]")
        #     mat = "lambert4SG"
        #     shading_engine = pmc.sets(empty=True, renderable=True, noSurfaceShader=True, name="{}SG".format(mat))
        #     pmc.defaultNavigation(connectToExisting=True, source=mat, destination=shading_engine, f=True)
        #     pmc.sets(faces, e=True, forceElement=shading_engine)
        #     continue


#region

# #find all whites and edges
for i in cube:
    if "yellow" in i.colors:
        yellowList.append(i)
    if "white" in i.colors:
        whiteList.append(i)
        if len(i.colors) == 2:
            edgelist.append(i)
    if len(i.colors) == 1:
        kernelList.append(i)
    if len(i.colors) == 2:
        edgesList.append(i)

def Step0__Daisy():
    #make the Step0__Daisy
    # pass in a machine faced with the node to be flipped 
    def flipEdge(machine):
            machine.facing("cw")
            machine.top("cw")
            machine.right("ccw")

    #check its neighbors to remove adjacent whites

    def neighbors(i):
        passed = [True, "neighhbors"]
        for w in whiteList:
            if i.normal("white") == w.normal("white"):
                x, y, z = i.height()
                if ([x, y + 1, z] == w.height()):
                    passed = [False, "top"]
                elif ([x, y - 1, z] == w.height()):
                    passed = [False, "bottom"]
        return passed
    #daisy Primary
    def primary(i):
        passed = [True, "primary"]
        #make sure were not disrupting daisy already made
        dirV = i.normal("white")
        for l in edgelist:
            # check node is not comparing itself
            if  l.name() == i.name() or l.height()[1] != 1 or passed[0] == False:
                continue
            # if white normal is on the z axis
            if i.normal("white")[2] != 0:
                # the top node on the corresponding X axis must be checked
                if l.height()[0] == i.height()[0]:
                    if l.normal("white")[1] == 1:
                        passed = [False, "primary"]
            #  else if the white normal is on the x axis
            elif i.normal("white")[0] != 0:
                # the top node on the corresponding z axis is checked
                if l.height()[2] == i.height()[2]:
                    if l.normal("white")[1] == 1:
                        #check to see if other rotation is available
                        passed = [False, "primary"]
        return passed
    # finally make sure that moving will not send edge away
    def flat(i):
        passed = [True, "flat"]
        for l in edgelist:
            white = i.normal("white")
            x, y, z = white
            other = filter(lambda x : x != white, i.normals())[0]
            if l.normal("white") == other and l.height()[1] == 0:
                passed = [False, "flat"]
            if l.normal("white") == [x * -1, 0, z * -1]:
                other = filter(lambda x: x != i.normal("white"), i.normals())[0]
                passed = [False, "mirror"]
        return passed
    #check if secondary rotation vector is possible
    def secondary(i):
        passed = [False, "secondary"]
        heightList = []
        for w in whiteList:
            heightList.append(w.height())
        x, y, z = i.normal("white")
        if [x, 1, z] not in heightList:
            passed = [True, "secondary"]
        return passed

    def middleRowUp(i):
        n = neighbors(i)
        p = primary(i)
        s =  secondary(i)
        f = flat(i)

        def recMiddle(i, counter):
            if counter < 0:
                return
            if n[1] == "bottom":
                machine = Handler("xPos")
                machine.bottom("cw")
            if p[0]:
                facing = facingFunction(i, i.colors[0])
                machine = Handler(facing)
                for r in range(4):
                    if i.normal("white")[1] != 1:
                        machine.facing("cw")
                        pass
            if s[0]:
                if i.normal("white")[1] == 1:
                    return
                # run secondary rotation around axis
                machine = Handler(i.position("white")[1])
                for r in range(4):
                    other = filter(lambda x: x != i.normal("white"), i.normals())[0]
                    if other[1] != 1:
                        machine.facing("cw")
            if (p[0] == False and s[0] == False):
                machine = Handler("xPos")
                machine.top("cw")
            #iterate to see if everyone is facing up
                # recMiddle(i, counter - 1)



        recMiddle(i, 4)

    def bottomRowUp(i):
        x, y, z = i.height()
        def rec(counter):
            passed = True
            if counter < 0:
                return
            for w in whiteList:
                if w.height() == [x, 1, z]:
                    passed = False
            if passed == False:
                machine = Handler("xPos")
                machine.top("cw")
                rec(counter - 1)
            elif passed == True:
                face = facingFunction(i, "white")
                machine = Handler(face)
                machine.left("cw")
                machine.facing("cw")

        rec(4)
        
    def bottomFaceUp(obj):

        def rec(i, counter):
            if counter < 0:
                return
            passed = True
            white = i.normal("white")
            other = filter(lambda x : x != white, i.normals())[0]
            face = ("x" if other[0] !=0 else "z") + ("Pos" if other[0] + other[2] > 0  else "Neg")

            for t in edgelist:
                if t.name() == i.name():
                    continue
                x, y, z = obj.height()
                if t.height() == [x, 1, z] and t.name()!= i.name():
                    passed = False

            machine = Handler(face)
            if passed == False:
                machine.top("cw")
                rec(i, counter -1)
            elif passed == True:
                machine.facing("cw")
                machine.facing("cw")


        rec(obj, 4)

    def daisyRec(counter):
        if counter <= 0:
            return
        for i in edgelist:
            # test if edges are at bottom, least likely case
            string = "white"
            if i.normal("white")[1] == -1:
                bottomFaceUp(i)
            #proceed to bottom row
            if i.normal("white")[1] == 0 and i.height()[1] == -1:
                bottomRowUp(i)
            #next middle row up
            if i.normal("white")[1] == 0 and i.height()[1] == 0:
                middleRowUp(i)
            #test if edges have to be flipped
            if i.normal("white")[1] == 0 and i.height()[1] == 1:
                facing = ("x" if i.normal("white")[0] !=0 else "z") + ("Pos" if i.normal("white")[0] + i.normal("white")[2]> 0  else "Neg")
                machine = Handler(facing)
                flipEdge(machine)
            #should leave us with a clear bottom row and top row.
            checklist = []

            for w in edgelist:
                if w.normal(str("white"))[1] != 1:
                    checklist.append(0)
                pass
            if 0 not in checklist:
                return
            else:
                daisyRec(counter - 1)
                pass
    daisyRec(4)
    pmc.select(cl=1)
    m.refresh()

def otherN(i):
    other = filter(lambda x : x != i.normals("white"), i.normals())[0]
    return other

def Step1_WhiteCross():
    coloredEdgeList = []
    for i in edgelist:
        if i.normal("white")[1] == 1:
            coloredEdgeList.append(i)

    
    def matchingKernel(i):
        # find normal of colored face
        other = filter(lambda x : x != i.normal("white"), i.normals())[0]
        # find matching kernel by normal
        for k in kernelList:
            if k.normals()[0] == other:
                return k

    def flipDown(i):

        def rec(counter, i):
            if counter <= 0:
                return
            # grab matching kernel by normal
            match = matchingKernel(i)
            # select color on edge faces that is not white
            otherColor = filter(lambda x : x != "white", i.colors)
            # check if match
            if otherColor[0] == match.colors[0]:
                machine = Handler(facingFunction(i, otherColor[0]))
                machine.facing("cw")
                machine.facing("cw")
            else:
                machine = Handler("xPos")
                machine.top("cw")
                rec(counter - 1, i)
    
        rec(4, i)
    
    for i in coloredEdgeList:
        flipDown(i)
        pass
    m.refresh()
    pmc.select(cl=1)
    # # # # # #  #  # # # # # # # # ## # 

def Step2_WhiteCorners():
    '''Step 3. Once the White cross has been created on the bottom of the cube, this function will find all remaining white nodes, and handle moving them to the bottom row, as well as making sure their other colors correspond to the red, blue, green and orange kernels'''
    def masterRec(counter):
        if counter <= 0:
            return        
        def bottomRowUp(i):
            
            def reorientWhiteNodes(i):
                # machine will be set to understand "facing" as the face that does not have white, leaving white facing our either right or left
                var = "white"
                if i.normal("white")[1] == 1:
                    # this will break the position function, do something else
                    var = i.colors[0]
                if i.position(var)[0] == "left":
                    machine = Handler(i.position("right"))
                    machine.top("cw")
                    machine.facing("ccw")
                    machine.top("ccw")
                    machine.facing("cw")
                    pass
                elif i.position(var)[0] == "right":
                    machine = Handler(i.position("left"))
                    machine.top("ccw")
                    machine.facing("cw")
                    machine.top("cw")
                    machine.facing("ccw")
                    pass

            def __bottomRowUpRecursion(counter):
                if counter <= 0:
                    return
                # find the colors of the lower not white
                neighbors = filter(lambda x : x != "white", i.colors)
                # find the vectors on the lower not up
                vec = filter(lambda x: x[1] == 0 ,i.normals())
                # find out the nighboring kernel colors
                matchingKernels = []
                matchingColors = []
                for k in kernelList:
                    if k.normals()[0] in vec and k.colors[0] in neighbors:
                        matchingKernels.append(k)
                        matchingColors.append(True)
                #correctly positioned and oriented

                # If matching colors, that indicates that a node is adjacent to the correct 2 kernels, but the rotation needs to be addressed
                if len(matchingColors) == 2 and i.normal("white")[1] == 0:
                    # successRotate(i)
                    reorientWhiteNodes(i)
                else :
                    machine = Handler("xPos")
                    machine.top("cw")
                    __bottomRowUpRecursion(counter - 1)
                    return

            __bottomRowUpRecursion(1)

        def topToBottom(i):
            '''Node with improper orientation in the correct row
            Needs to be moved down, then reassessed
            '''
            f = i.position("left")
            machine = Handler(f)
            machine.left("ccw")
            machine.top("cw")
            machine.left("cw")

        def downToFront(i):
            f = i.position("left")
            machine = Handler(f)
            machine.facing("cw")
            machine.top("cw")
            machine.facing("ccw")
            machine.top("ccw")
            machine.top("ccw")

        def __entryRecursion(counter, i):
            # if normals are facing down, its already in place
            if counter <= 0 or i.normal("white")[1] == -1:
                return
            # if white is down facing
            if i.normal("white")[1] == -1:
                return
            # if white is in top layer
            if i.normal("white")[1] == 1:
                downToFront(i)
                pass
            if i.height()[1] == -1 and len(i.colors) == 3:
                topToBottom(i)
                pass
            #for bottomlayer 
            if i.height()[1] == 1 and len(i.colors) == 3:
                bottomRowUp(i)
                pass
            if i.normal("white")[1] != -1:
                __entryRecursion(counter - 1, i)
                pass
            return
        
        for i in whiteList:
            __entryRecursion(4, i)
        masterRec(counter - 1)

    masterRec(4)
    m.refresh()
    pmc.select(cl=1)

        

# def Step3_EdgesToMiddle():
    # find all edges that do not have a yellow up on the top row
    def __Step3Recursion(counter):
        if(counter<= 0):
            return
        wrongUp = [x for x in edgesList if "yellow" not in x.colors and x.height()[1] == 1]
        def __edgesToMiddleAlgorithm(string, machine):
            if string == "right":
                machine.top("ccw")
                machine.right("ccw")
                machine.top("cw")
                machine.right("cw")
                machine.top("cw")
                machine.facing("ccw")
                machine.top("ccw")
                machine.facing("cw")
                pass
            if string == "left":
                machine.top("cw")
                machine.left("ccw")
                machine.top("ccw")
                machine.left("cw")
                machine.top("ccw")
                machine.facing("cw")
                machine.top("cw")
                machine.facing("ccw")
                pass
            return

        def __nodeRecursion(node, counter):
            if(counter <= 0):
                return False
            # get lateral face color
            lateralFaceColor = [x for x in node.colors if node.normal(x) != [0,1,0] ][0]
            matchingKernel = [x for x in kernelList if lateralFaceColor in x.colors][0]
            if(matchingKernel.normal(lateralFaceColor) == node.normal(lateralFaceColor)):
                return True
            else:
                machine = Handler("xPos")
                machine.top('cw')
                return __nodeRecursion(node, counter-1)

        if(len(wrongUp) > 0):
            for node in wrongUp:
                if(__nodeRecursion(node, 4)):
                    facingColor = [x for x in node.colors if node.normal(x) != [0,1,0] ][0]
                    machine = Handler(facingFunction(node, facingColor))
                    __edgesToMiddleAlgorithm(directional(node, facingColor), machine)
                else:
                    __Step3Recursion(counter -1)
                # check if its facing is near its matchin kernel
            return
        # else check for wrong laterally
        wrongLateral = [x for x in edgesList if "yellow" not in x.colors and x.height()[1] == 0]
        # grab a random one, 
        
    __Step3Recursion(4)

def Step3_EdgesToMiddle():
    def masterRec(counter) :
        if counter <= 0:
            return
        def moving(i, string, machine):
            # if "yellow" in i.colors:
            #     return
            if string == "right":
                machine.top("ccw")
                machine.right("ccw")
                machine.top("cw")
                machine.right("cw")
                machine.top("cw")
                machine.facing("ccw")
                machine.top("ccw")
                machine.facing("cw")
                pass
            if string == "left":
                machine.top("cw")
                machine.left("ccw")
                machine.top("ccw")
                machine.left("cw")
                machine.top("ccw")
                machine.facing("cw")
                machine.top("cw")
                machine.facing("ccw")

                pass
        
        def directional(i, color1):
            other = filter(lambda x: x != color1, i.colors)[0]
            test = []
            for k in kernelList:
                if k.colors[0] == other:
                    test.append(k)
            k = test[0]
            dir = facingFunction(i, color1)
            nX, nY, nZ = k.normals()[0]
            if "z" in dir:
                if "Pos" in dir:
                    if nX < 0:
                        return "left"
                    if nX > 0:
                        return "right"
                if "Neg" in dir:
                    if nX < 0:
                        return "right"
                    if nX > 0:
                        return "left"
            if "x" in dir:
                if "Pos" in dir:
                    if nZ < 0:
                        return "right"
                    if nZ > 0:
                        return "left"
                if "Neg" in dir:
                    if nZ < 0:
                        return "left"
                    if nZ > 0:
                        return "right"


        # recursively check if vertical bar exists: else rotate top and recurse
        def rec(k, counter):
            if counter <= 0:
                return
            passed = []
            parallel = []
            for i in edgesList:
                if k.normals()[0] in i.normals():
                    if i.height()[1] == 1:
                        # we have found vertical neighbors, now check if colors match:
                        index = i.normals().index(k.normals()[0])
                        if i.colors[index] == k.colors[0] and "yellow" not in i.colors:
                            # if colors match, append to passed
                            passed.append(i)
                    # check to see if the edges are in the wrong area
                    if i.height()[1] == 0:
                        # we have found vertical neighbors, now check if colors match:
                        index = i.normals().index(k.normals()[0])
                        if i.colors[index] != k.colors[0] and "yellow" not in i.colors:
                            # if colors match, append to parallel
                            # print i.name()
                            parallel.append(i)
            if len(passed) > 0:
                for p in passed:
                    if p.height()[1] == -1:
                        continue
                    # found successful node, now decide to move it right or left:
                    if "yellow" in p.colors:
                        continue
                    # checklist[k.name()].append(True)
                    machine = Handler(facingFunction(p, k.colors[0]))
                    moving(p, directional(p, k.colors[0]), machine)
                return
            if len(parallel) >= 1:
                matched = parallel[0]
                node1Color = [x for x in matched.colors if x != "yellow"][0]
                node2Color = [x for x in matched.colors if x != "yellow"][1]
                firstNodePosition = Vector(matched.normal(node1Color))
                secondNodePosition = Vector(matched.normal(node2Color))
                driver = node1Color
                # # draw traingle with the drivers position as the third vertex
                plane = pmc.polyCreateFacet(ch=1, p=[firstNodePosition, [0,0,0], [0, 1, 0]], n="temp")
                
                info = pmc.polyInfo(plane[0] + ".f[0]", fn=1)[0]
                null, null, x, y, z = info.split()
                planeNormal = Vector([float(x),float(y),float(z)])
                pmc.delete(plane)
                # # # # if the traingles normals do not face the same direction as the secondary node, secondary node is to screen right, primary node should be the driver
                if(planeNormal != secondNodePosition):
                    driver = node2Color
                facing = facingFunction(matched, driver)
                machine = Handler(facing)
                moving(matched, "right", machine)
                return

            else:
                checklist = []
                for i in edgesList:
                    if "yellow" in i.colors and i.height()[1] == 1:
                        checklist.append(True)
                if len(checklist) == 4:
                    return
                else :
                    machine = Handler("xPos")
                    machine.top("cw")
                rec(k, counter - 1)
            return

        for k in kernelList:
            if k.height()[1] == -1 or k.normals()[0][1] == 1:
                continue
            rec(k, 4)
        masterRec(counter - 1)
    masterRec(4)

def directional(i, color1):
    other = filter(lambda x: x != color1, i.colors)[0]
    test = []
    for k in kernelList:
        if k.colors[0] == other:
            test.append(k)
    k = test[0]
    dir = facingFunction(i, color1)
    nX, nY, nZ = k.normals()[0]
    if "z" in dir:
        if "Pos" in dir:
            if nX < 0:
                return "left"
            if nX > 0:
                return "right"
        if "Neg" in dir:
            if nX < 0:
                return "right"
            if nX > 0:
                return "left"
    if "x" in dir:
        if "Pos" in dir:
            if nZ < 0:
                return "right"
            if nZ > 0:
                return "left"
        if "Neg" in dir:
            if nZ < 0:
                return "left"
            if nZ > 0:
                return "right"
            
def Step4__YellowCross():
    def furf(machine):
        machine.facing("cw")
        machine.right("ccw")
        machine.top("ccw")
        machine.right("cw")
        machine.top("cw")
        machine.facing("ccw")
    

    def _L_to_cross(machine):
        machine.facing("cw")
        machine.top("ccw")
        machine.right("ccw")
        machine.top("cw")
        machine.right("cw")
        machine.facing("ccw")

    upwards = []
    yellowList = []
    # check to see which yellow edges are facing up
    for i in edgesList:
        if "yellow" not in i.colors:
            continue
        yellowList.append(i)
        if i.normal("yellow")[1] == 1 and len(i.colors)!=3:
            upwards.append(i)

    if(len(upwards) == 2):
        # L or Line is formed
        # find the missing 2 nodes, and move to the cross
        lateralFacing = [x for x in yellowList if x.normal("yellow")[1] != 1]
        firstNodePosition = Vector(lateralFacing[0].normal("yellow"))
        secondNodePosition = Vector(lateralFacing[1].normal("yellow"))

        # if normals of the 2 are directly opposing adding them will result in [0,0,0]
        if (1 in abs(firstNodePosition + secondNodePosition)):
            # L shape formed
            # set the machine facing one lateral node, with the second on the right
            # interestingly, maya always draws a triangle with points [0,0,0], [0,1,0], [any] with its facing normal to the right
            # This can be used to find a node to screen right reguardless of world orientation
            # assign the first as the driver
            driver = lateralFacing[0]
            # draw traingle with the drivers position as the third vertex
            plane = pmc.polyCreateFacet(ch=1, p=[firstNodePosition, [0,0,0], [0, 1, 0]], n="temp")
            info = pmc.polyInfo(plane[0] + ".f[0]", fn=1)[0]
            null, null, x, y, z = info.split()
            planeNormal = Vector([float(x),float(y),float(z)])
            
            # # if the traingles normals do not face the same direction as the secondary node, secondary node is to screen left, and should be the driver
            if(planeNormal != secondNodePosition):
                driver = lateralFacing[1]

            # set machine facing now driver is selected
            facing = facingFunction(driver, "yellow")
            machine = Handler(facing)
            _L_to_cross(machine)
        else:
            # line
            # line must be horizontal, either lateralFacing will give the face for the machine
            facing = facingFunction(lateralFacing[0], "yellow")
            machine = Handler(facing)
            furf(machine)

    if(len(upwards) == 0):
        print("Dot formed")
        machine = Handler("zPos")
        furf(machine)
        machine = Handler("zNeg")
        furf(machine)
        machine = Handler("zPos")
        furf(machine)

        
    # print([x.normal("yellow") for x in yellowList])
    # print([node.name() for node in upwards])
    # if len(upwards) == 0:
    #     print("standing")
    #     current = yellowList[0]
    #     facing1 = facingFunction(current, "yellow")
    #     machine1 = Handler(facing1)
    #     furf(i, machine1)
    #     facing2 = facing1[0] + "Neg" if "Pos" in facing1 else "Neg"
    #     machine2 = Handler(facing2)
    #     furf(i, machine2)
    #     furf(i, machine1)
    #     print(facing1)

def Step5__swapYellowEdges():
    # this stage looks for 2 pairs of nodes that need to be switched
    # nodes can be switched if they are adjacent, or if they are opposing
    edges = [x for x in yellowList if len(x.colors) == 2 ]
    # print("Step 5 : Swapping yellow edges")

    def __swapAlgorithm(machine):
        machine.right("ccw")
        machine.top("ccw")
        machine.right("cw")
        machine.top("ccw")
        machine.right("ccw")
        machine.top("ccw")
        machine.top("ccw")
        machine.right("cw")
        machine.top("ccw")
        return

    def __swapEdges(node1, node2):
        # set the machine facing one lateral node, with the second on the left
        # again, we can leverage mayas face normal to detect which node needs to be the driver
        driver = node1
        node1Color = [x for x in node1.colors if x != "yellow"][0]
        node2Color = [x for x in node2.colors if x != "yellow"][0]
        firstNodePosition = Vector(node1.normal(node1Color))
        secondNodePosition = Vector(node2.normal(node2Color))
        # # assign the first as the driver
        # # draw traingle with the drivers position as the third vertex
        plane = pmc.polyCreateFacet(ch=1, p=[firstNodePosition, [0,0,0], [0, 1, 0]], n="temp")
        
        info = pmc.polyInfo(plane[0] + ".f[0]", fn=1)[0]
        null, null, x, y, z = info.split()
        planeNormal = Vector([float(x),float(y),float(z)])
        pmc.delete(plane)
        # # # if the traingles normals do not face the same direction as the secondary node, secondary node is to screen right, primary node should be the driver
        if(planeNormal == secondNodePosition):
            driver = node2
        # # set machine facing now driver is selected
        facing = facingFunction(driver, [x for x in driver.colors if x != "yellow"][0])
        machine = Handler(facing)
        __swapAlgorithm(machine)
        # _L_to_cross(machine)

    def __checkEdges():
        for edge in edges:
            facingColor = [color for color in edge.colors if color != "yellow"][0]
            facingNormal = edge.normal(facingColor)

            # # get closest kernel
            nearKernel = [x for x in kernelList if x.normal(x.colors[0]) == facingNormal][0]
            if(facingColor != nearKernel.colors[0]):
                return False
        return True
        

    def _edge_recursion(node, counter):
        if(counter <= 0 or __checkEdges()):
            return
        # check if edges are correct

        # check if swap should be opposite
        # find normal of color
        facingColor = [color for color in node.colors if color != "yellow"][0]
        facingNormal = node.normal(facingColor)


        # find opposing node
        opposingNode = [x for x in edges if Vector(x.normal([color for color in x.colors if color != "yellow"][0])) == Vector(facingNormal) * -1][0]
        opposingNodeColor = [color for color in opposingNode.colors if color != "yellow"][0]

        # get closest kernel
        nearKernel = [x for x in kernelList if x.normal(x.colors[0]) == facingNormal][0]
        nearKernelColor = nearKernel.colors[0]
        # get opposing kernel
        opposingKernel = [x for x in kernelList if Vector(x.normal(x.colors[0])) == Vector(facingNormal) * -1 ][0]
        opposingKernelColor = opposingKernel.colors[0]

        # if color of opposite kernel matches node color, and near kernel matches opposing node, switch 
        if(opposingNodeColor == nearKernelColor and opposingKernelColor == facingColor):
            # machine set to have both nodes horizontally, so either of the other 2 nodes will do
            print("swapping ", node.name(), " and ", opposingNode.name())
            drivers = [x for x in edges if (x != node and x != opposingNode)]
            driver = drivers[0]
            facing = facingFunction(driver, [x for x in driver.colors if x!= "yellow"][0])
            facing2 = facingFunction(drivers[1], [x for x in drivers[1].colors if x!= "yellow"][0])
            machine = Handler(facing)
            machine.top("ccw")
            __swapAlgorithm(machine)
            machine = Handler(facing2)
            __swapAlgorithm(machine)
            filtered = [x for x in edges if (x != node and x != opposingNode)]
            _edge_recursion(filtered[0], counter-1)
        # check if either of the neighbors are colored appropriately
        neighbors = [x for x in edges if (x != node and x != opposingNode)]
        for n in neighbors:
            # get neighbpors color
            neighborColor = [color for color in n.colors if color != "yellow"][0]
            # get neighbor kernel
            neighborKernel = [x for x in kernelList if x.normal(x.colors[0]) == n.normal(neighborColor)][0]
            # check if neighbor kernel matches facing color and closest kernel matches neighbor colro
            if (facingColor == neighborKernel.colors[0] and  nearKernel.colors[0] == neighborColor):
                __swapEdges(node, n)
                # recurse
                break
        
        # if neither check is passed, rotate the top and try again
        else:
            machine = Handler("xPos")
            machine.top("cw")
            _edge_recursion(node, counter-1)

    for edge in edges:
        if(not __checkEdges()):
            _edge_recursion(edge,4)
        else:
            break

def Step6__positionYellowCorners():
    # first, check if any of the corners are in the right position
    def __swapAlgorithm(machine):
        machine.top("ccw")
        machine.right("ccw")
        machine.top("cw")
        machine.left("ccw")
        machine.top("ccw")
        machine.right("cw")
        machine.top("cw")
        machine.left("cw")

    def __step6Recursion(counter):
        if(counter <= 0):
            return
            
        corners = [x for x in yellowList if len(x.colors) == 3]
        matched = False

        for corner in corners:
            # get all adjacent kernels
            kernelColors = [x.colors[0] for x in kernelList if x.normals()[0] in corner.normals()]
            if(sorted(kernelColors) == sorted(corner.colors)):
                matched = corner
                break

        if(matched):
            print("Matched ", matched.name())
            # set the machine facing the node with it top right of the cube
            # # again, we can leverage mayas face normal to detect which node needs to be the driver
            # driver = node1
            node1Color = [x for x in matched.colors if x != "yellow"][0]
            node2Color = [x for x in matched.colors if x != "yellow"][1]
            firstNodePosition = Vector(matched.normal(node1Color))
            secondNodePosition = Vector(matched.normal(node2Color))
            driver = node1Color
            # # draw traingle with the drivers position as the third vertex
            plane = pmc.polyCreateFacet(ch=1, p=[firstNodePosition, [0,0,0], [0, 1, 0]], n="temp")
            
            info = pmc.polyInfo(plane[0] + ".f[0]", fn=1)[0]
            null, null, x, y, z = info.split()
            planeNormal = Vector([float(x),float(y),float(z)])
            pmc.delete(plane)
            # # # # if the traingles normals do not face the same direction as the secondary node, secondary node is to screen right, primary node should be the driver
            if(planeNormal != secondNodePosition):
                driver = node2Color
            facing = facingFunction(matched, driver)
            print(facing)
            machine = Handler(facing)
            __swapAlgorithm(machine)
            
        else:
            print("No match found")
            __step6Recursion(counter -1)

    __step6Recursion(4)
    # if not, rotate and check again
    # at the end of 4 rotations, select a random corner to operate on, and then recurse

def Step7__orientYellowCorners():
    print("Step 7 : Orienting Yellow Corners")

    def __swapAlgorithm(machine):
        machine.right("cw")
        machine.bottom("cw")
        machine.right("ccw")
        machine.bottom("ccw")


    def __orient2Corners(corners):  
        # if yellows are adjacent
        node1 = corners[0]
        node2 = corners[1]
        # im pretty sure that if nodes are on the same side, adding them up will total 4, but if theyre on opposite sides, it will be 2. This needs further testing
        total = sum(list(Vector(node1.height())+ Vector(node2.height())))

        # same side
        # if yellows are facing the same direction, order changes
        # again position the node to the top right
        firstNodePosition = Vector(node1.normal("yellow"))
        secondNodePosition = Vector(node2.normal("yellow"))
        driver = node1
        # # draw traingle with the drivers position as the third vertex
        plane = pmc.polyCreateFacet(ch=1, p=[firstNodePosition, [0,0,0], [0, 1, 0]], n="temp")
        
        info = pmc.polyInfo(plane[0] + ".f[0]", fn=1)[0]
        null, null, x, y, z = info.split()
        planeNormal = Vector([float(x),float(y),float(z)])
        pmc.delete(plane)
        # # # # if the traingles normals do not face the same direction as the secondary node, secondary node is to screen right, primary node should be the driver
        if(planeNormal != secondNodePosition):
            driver = node2
        if(total == 4):
            if(node1.normal("yellow") == node2.normal("yellow")):

                facing = facingFunction(driver, "yellow")
                machine = Handler(facing)
                __swapAlgorithm(machine)
                __swapAlgorithm(machine)
                __swapAlgorithm(machine)
                __swapAlgorithm(machine)
                machine.top("cw")
                __swapAlgorithm(machine)
                __swapAlgorithm(machine)
                machine.top("ccw")
            else:
                
                facing = facingFunction(driver, [x for x in driver.colors if x != "yellow" and driver.normal(x) != [0,1,0]][0])
                machine = Handler(facing)
                __swapAlgorithm(machine)
                __swapAlgorithm(machine)
                machine.top("cw")
                __swapAlgorithm(machine)
                __swapAlgorithm(machine)
                __swapAlgorithm(machine)
                __swapAlgorithm(machine)
                machine.top("ccw")
                
            # __swapAlgorithm(machine)
        elif(total == 2):
            # facing = facingFunction(driver, [color for color in driver.colors if (color != "yellow" and driver.normal(color) != [0,1,0])][0])
            machine = Handler(facingFunction(driver, "yellow"))
            machine.top("cw")
            __swapAlgorithm(machine)
            __swapAlgorithm(machine)
            machine.top("cw")
            machine.top("cw")
            __swapAlgorithm(machine)
            __swapAlgorithm(machine)
            __swapAlgorithm(machine)
            __swapAlgorithm(machine)
            machine.top("cw")
        else:
            print("Should not be possible")

    def __orient3Corners(corners):
        # with 3 edges needing to be rotated, find which node is on the same "side" as 2 others
        temp =[]
        driverNode = None
        for corner in corners:
            temp = [corn for corn in corners if corn is not corner ]
            first = sum(abs(Vector(corner.height())+ Vector(temp[0].height())))
            second = sum(abs(Vector(corner.height())+ Vector(temp[1].height())))
            if(first == 4 and second == 4):
                driverNode = corner

        if(not driverNode):
            print("error step 7")
            return
        
        # once weve found the "center" node
        # face machine with center node top right
        node1Color = [x for x in driverNode.colors if driverNode.normal(x) != [0,1,0]][0]
        node2Color = [x for x in driverNode.colors if driverNode.normal(x) != [0,1,0]][1]
        firstNodePosition = Vector(driverNode.normal(node1Color))
        secondNodePosition = Vector(driverNode.normal(node2Color))
        driver = node1Color
        # # draw traingle with the drivers position as the third vertex
        plane = pmc.polyCreateFacet(ch=1, p=[firstNodePosition, [0,0,0], [0, 1, 0]], n="temp")
        
        info = pmc.polyInfo(plane[0] + ".f[0]", fn=1)[0]
        null, null, x, y, z = info.split()
        planeNormal = Vector([float(x),float(y),float(z)])
        pmc.delete(plane)
        # # # # if the traingles normals do not face the same direction as the secondary node, secondary node is to screen right, primary node should be the driver
        if(planeNormal != secondNodePosition):
            driver = node2Color

        facing = driverNode.position(driver)[1]

        # find the kernel that matches the upwards facing color
        lateralColor = [color for color in driverNode.colors if color != "yellow" and driverNode.normal(color) != [0,1,0]][0]

        if(driverNode.position(lateralColor) == "left"):
        # else algo is applied 2x per corner
            print("left")
        else:
        # if upward face (not yellow) needs to rotate left, 4x algo per corner
            print("right")
            machine = Handler(facing)
            __swapAlgorithm(machine)
            __swapAlgorithm(machine)
            __swapAlgorithm(machine)
            __swapAlgorithm(machine)
            machine.top("cw")
            __swapAlgorithm(machine)
            __swapAlgorithm(machine)
            __swapAlgorithm(machine)
            __swapAlgorithm(machine)
            machine.top("cw")
            machine.top("cw")
            __swapAlgorithm(machine)
            __swapAlgorithm(machine)
            __swapAlgorithm(machine)
            __swapAlgorithm(machine)
            machine.top("cw")


        pass

    def __orient4Corners(corners):
        print(corners)

    # figure out how many corners are wrong
    incorrectOrientation = []
    corners = [x for x in yellowList if len(x.colors) == 3]
    for corner in corners:
        if(corner.normal("yellow") != [0,1,0]):
            incorrectOrientation.append(corner)
    
    if(len(incorrectOrientation) == 2):
        __orient2Corners(incorrectOrientation)
    
    if(len(incorrectOrientation) == 3):
        __orient3Corners(incorrectOrientation)
    
    if(len(incorrectOrientation) == 4):
        __orient4Corners(incorrectOrientation)
        
# generateCleanCube()
#endregion

scrambleCounter = 10
maxIterations = 5

class Tester():
    def __init__(self):
        self.file =  open("G:\My Drive\Maya\MyScripts\Rubix\Testing\RubixTestingLog.txt", "a")

    def close(self):
        self.file.close()

    def writeTestSuccess(self, testNumber):
        string = "================================= Test #" + str(testNumber) + " Cleared ============================================= \n"
        print(string)
        self.file.writelines(string)
    
    def writeTestFailure(self, testNumber, testName):
        string = "================================= Test #"+str(testNumber)+" Failed at "+ testName+" ============================================= \n"
        print(string)
        self.file.writelines(string)

    def testStep0(self):
        # test daisy
        assertion = [x.normal("white") == [0,1,0] for x in whiteList if len(x.colors) == 2]
        return all(assertion)

    def testStep1(self):
        # test white cross
        assertion = [x.normal("white") == [0,-1,0] for x in whiteList if (len(x.colors) == 2 or len(x.colors) == 1)]
        return all(assertion)
    
    def testStep2(self):
        # test white corners
        # test all white corners faces are no bottom row
        assertion = [x.normal("white") == [0,-1,0] for x in whiteList if (len(x.colors) == 3)]
        # check that all corners are matching kernel orientation
        assertion2 = all([all([all([x.normal(color) == [kernel for kernel in kernelList if color in kernel.colors][0].normal(color)]) for color in x.colors if color != "white"]) for x in whiteList if len(x.colors) == 3])
        return all([assertion, assertion2])
    
    def testStep3(self):
        # test edges to middle
        lateralEdges = [x for x in edgesList if x.height()[1] == 0]
        return(all([all([x.normal(color) == [kernel for kernel in kernelList if color in kernel.colors][0].normal(color) for color in x.colors]) for x in lateralEdges]))
    
    def testStep4(self):
        # test yellow cross
        assertion = [x.normal("yellow") == [0,1,0] for x in yellowList if (len(x.colors) == 2 or len(x.colors) == 1)]
        return all(assertion)

    def testStep5(self):
        # test yellow edges
        assertion = [[x.normal(color) == [kernel for kernel in kernelList if kernel.colors[0] == color][0].normal(color) for color in x.colors if color != "yellow"][0] for x in yellowList if len(x.colors) == 2]
        return all(assertion)
    
    def testStep6(self):
        # test yellow corners are placed
        assertion = [[x.normal(color) == [kernel for kernel in kernelList if kernel.colors[0] == color][0].normal(color) for color in x.colors if color != "yellow"][0] for x in yellowList if len(x.colors) == 3]
        assertion = [
            [
                [Vector([kernel for kernel in kernelList if color in kernel.colors][0].height())for color in x.colors if color!= "yellow"][0]
                + [Vector([kernel for kernel in kernelList if color in kernel.colors][0].height())for color in x.colors if color!= "yellow"][1]
                + Vector(0,1,0) == Vector(x.height())][0]
            for x in yellowList if len(x.colors) == 3]
        return all(assertion)
    
    def testStep7(self):
        # test yellow corners are placed
        assertion = [[x.normal(color) == [kernel for kernel in kernelList if kernel.colors[0] == color][0].normal(color) for color in x.colors if color != "yellow"][0] for x in yellowList if len(x.colors) == 3]
        return all(assertion)

tester  = Tester()

tempPath = 'G:\My Drive\Maya\MyScripts\Rubix\Testing\Temp'
errorPath = 'G:\My Drive\Maya\MyScripts\Rubix\Testing\Errors'
fileNames = [
    "step0",
    "step1",
    "step2",
    "step3",
    "step4",
    "step5",
    "step6",
    "step7",
]

def testSuite(iterations):
    def testingRecursion(counter):
        if(counter >= maxIterations):
            return
        prevFile = "step0"

        global scrambleCounter
        # ----------------------------------------------------Steps
        # no test for scramble
        Step__Scramble(scrambleCounter) 

        for [step, test, fileName] in zip(
            [
                Step0__Daisy,
                Step1_WhiteCross,
                Step2_WhiteCorners,
                Step3_EdgesToMiddle,
                Step4__YellowCross,
                Step5__swapYellowEdges,
                Step6__positionYellowCorners,
                Step7__orientYellowCorners
            ],
            [
                tester.testStep0,
                tester.testStep1,
                tester.testStep2,
                tester.testStep3,
                tester.testStep4,
                tester.testStep5,
                tester.testStep6,
                tester.testStep7
            ],fileNames):
            

            # print("Testing step ", step.__name__)
            # print("filename = ", fileName)
            # print("prev = ", prevFile)
            step()
            
            if(not test()):
                print("test failed", step.__name__)
                opening = tempPath + '/'+ prevFile + ".mb"
                print("opening previous", opening)
                pmc.openFile(opening, force=1)

                pmc.saveAs(errorPath + "/" + fileName + "/" + fileName +"_"+ str(uuid.uuid4())+ ".mb")
                tester.writeTestFailure(counter, step.__name__)
                testingRecursion(counter + 1)   
                return
            # if successful, save the file
            pmc.saveAs(tempPath + '/'+ fileName + ".mb", force=1)
            prevFile = fileName
        tester.writeTestSuccess(counter)

        scrambleCounter += 1
        testingRecursion(counter +1)

    testingRecursion(iterations)    
testSuite(1)
    
tester.close()

# Step__Scramble(5) 
# Step0__Daisy() 
# Step1_WhiteCross() 
# Step2_WhiteCorners()
# Step3_EdgesToMiddle()
# Step4__YellowCross()
# Step5__swapYellowEdges()
# Step6__positionYellowCorners()
# print(tester.testStep6())
Step7__orientYellowCorners()





