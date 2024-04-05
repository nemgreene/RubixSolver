import maya.cmds as m
import math

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


dictionary = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

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

        self.normals()
        

    def name(self):
        return([self.id, self.colors])

    def normals(self) :
        m.select(self.id)
        m.hyperShade(smn=1) # that will select the shader
        for i in range(len(self.colors)):
            s = m.ls(sl=1)[i + 1] # remember the selected shader
            sg = m.listConnections(s+".oc", s=0, d=1)[0] # figure out the shading group
            # select the faces of the same object with same shader attached
            l = []
            for o in m.sets(sg, q=1):
                if self.id not in o: continue
                l.append(o)
            ns = m.polyInfo(l[0], fn=1)[0]
            null, null, x, y, z = ns.split()
            self.normalList.append([x, y, z, s])
            return(self.normalList)
 

        # edgeList = m.polyListComponentConversion(l[0], ff = 1, te = 1)
        # vertList = m.polyListComponentConversion(edgeList[0], fe = 1, tv = 1)
        # vertList = vertList + m.polyListComponentConversion(edgeList[2], fe = 1, tv = 1)
        # print vertList
        # p0, p1, p2, p3 = vertList
        # p0 =  m.xform(p0, q=True, ws=True, t=True)
        # p1 =  m.xform(p1, q=True, ws=True, t=True)
        # p2 =  m.xform(p2, q=True, ws=True, t=True)
        # p3 =  m.xform(p3, q=True, ws=True, t=True)

        # normal = Normal(p0, p1, p2)
        # print normal
        # m.select(vertList)

        # print m.xform(test[0], q=True, ws=True, t=True)

cube = []

for i in range(26):
    new = Node(dictionary[i])
    print new.name()
    cube.append(new)
    
