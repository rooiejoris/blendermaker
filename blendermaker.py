#region-begin - a little script to generate a simple pyramid
import random
import Blender
import bpy
import datetime
import commands
import os
import sys
import socket

import Blender
from Blender import Scene
from Blender import BGL
from Blender import Window
from Blender.Draw import *
from Blender import NMesh
from Blender import Mesh

import struct
import mmap
import contextlib
import itertools



nMenu = "Bracelet|Pot|Gun"
vMenu = Blender.Draw.Create(0)
vaas = "/home/miguel/objects/vaas4.stl"
bracelet = "/home/miguel/objects/bracelet25.stl"

height = 0
actheight = 0
length = 0
actlength = 0
PORT=4444
HOST="127.0.0.1"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cntbuttom = 0
cntstatus = "Connect"


def my_callback(filename):                # callback for the FileSelector
            print "You chose the file:", filename   # do something with the chosen file


def draw():

    global nMenu
    global vMenu
    global height
    global actheight
    global length
    global actlength
    global cntbuttom
    global cntstatus

    Blender.BGL.glClear(Blender.BGL.GL_COLOR_BUFFER_BIT) 
	
    BGL.glColor3f(0.2,0.3,0.4)
    BGL.glRectf(0, 0, 1000, 900)
    
    BGL.glColor3f(0,0,0)
    BGL.glRasterPos2i(0,450)
    Blender.Draw.Text("     ++ Blender Maker ++ ", "small")
            
    BGL.glColor3f(1 , 1, 1)
    BGL.glRectf(400, 0, 800, 400)
	
    BGL.glColor3f(0.5,0.5,0.5)
    BGL.glRectf(400,390,800,120)
	
    BGL.glColor3f(0,0,0)
	
    BGL.glRasterPos2i(410, 130)

    #GUI Elements: name,event,x,y,width,height,default,tooltip,callback
    Blender.Draw.Toggle("new tetrahedron",1,10,20,100,20,0,"tooltip")
    Blender.Draw.Toggle("delete object",2,120,20,100,20,0,"tooltip")
    Blender.Draw.Toggle("randomize",3,10,300,80,20,0,"tooltip")
    Blender.Draw.Toggle("Send to ReplicatorG",4,10,335,180,20,0,"tooltip")
    cntbuttom = Blender.Draw.Toggle(cntstatus,10,210,335,80,20,0,"tooltip")
    Blender.Draw.Toggle("view",5,10,210,100,20,0,"tooltip")
    Blender.Draw.Toggle("load obj",6,10,370,100,20,0,"tooltip")
    vMenu = Blender.Draw.Menu(nMenu, 7, 120, 370, 100, 20,vMenu.val)  
    height = Slider("Height  ", 8, 10,270, 150,20 , actheight, 1, 110, 0, "tooltip")
    length = Slider("Length ", 9, 10,239, 150,20 , actlength, 1, 110, 0, "tooltip")
    

#length = Slider("Send to replicatorG ", 9, 10,259, 150,20 , actlength, 1, 110, 0, "tooltip")

#event keyboard	
def event(evt,val):  # define mouse and keyboard press events
    global object

    if evt == Blender.Draw.ESCKEY: # example if esc key pressed
        Blender.Draw.exit()    # then exit script
        return                 # return from the function


def write(filename):
    out = open(filename, "w")
    sce= bpy.data.scenes.active
    for ob in sce.objects:
        out.write(ob.type + ": " + ob.name + "\n")
    out.close()
    
#event buttom
def button(evt):     # define what to do if a button is pressed, for example:
    global vMenu,nMenu
    global actheight
    global height
    global length
    global actlength
    global obj
    global object
    global PORT
    global HOST
    global s
    global cntbuttom
    global cntstatus

    view1=[0.0, -1.0000001192092896, 3.422854888412985e-08]
    view3=[1.0, 1.7938124943772671e-16, 2.4524626637321336e-32]
    view7=[0.0, 0.0, 1.0]

    if evt == 1: # event make tetrahedron.
        mk_tetrahedron()
        Redraw()
        
    if evt == 2: # delete.
        result = Blender.Draw.PupMenu("Really?|Yes|No")        
        if result == 2: 
            unlink()
            Redraw()
            if result == 3:
                set_size()
                
    if evt == 3: # buttom 3 randomize
        #load object, mesh, copymesh.
        obj = Blender.Object.GetSelected() 
        objectname=obj[0].name    
        object = Blender.Object.Get(objectname)
        
        meshname = obj[0].data.name
        mesh = Blender.Mesh.Get(meshname)
        
        copyverts=mesh.verts[:]
        covertices=[]

        topz=copyverts[0].co[2]
        bottomz=copyverts[0].co[2]
        
        #find topz and bottomz
        for vertice in copyverts:
            if(vertice.co[2]>topz):
                topz=vertice.co[2]
            elif(vertice.co[2]<bottomz):
                bottomz=vertice.co[2]
                
        print "** The vertices:"
        print "top="+str(topz)+",bottom="+str(bottomz)

        #pass to all the vertices.
        for vertice in copyverts:
            #top and bottom layers.
            if(vertice.co[2]>bottomz and vertice.co[2]<topz):
                verticeact=vertice
                if not(verticeact in covertices):
                    covertices.append(vertice)
                    randx=random.uniform(-5,5)
                    randy=random.uniform(-5,5)
                    index=0;
                    for index,verticeref in enumerate(copyverts):
                        if verticeref.co[0]==verticeact.co[0]:
                            mesh.verts[index].co[0]= verticeref.co[0]+randx
                            mesh.verts[index].co[1]= verticeref.co[1]+randy
                            #print str(mesh.verts[index].co[2])+"/n"
                else:
                    print "was already"
	print "redraw"
	scene  = Scene.GetCurrent()
	Window.RedrawAll() 
    #export stl and send path+filename to replicator g.
    if evt == 4:

        obj = Blender.Object.GetSelected() 
        objectname=obj[0].name    
        object = Blender.Object.Get(objectname)

        meshname1 = object.getData(name_only = True)
        nmesh=NMesh.GetRaw(meshname1)
        nmesh.transform(object.matrixWorld)
        file = open("/home/miguel/objects/temporal.stl","w")
        file.write("solid "+"poo.stl"+"\n")
        
        n_tri=0 # number of tris in STL                                                                 
        n_face=len(nmesh.faces)                                                                          
        for i in range(0,n_face):                                                                       	
            face=nmesh.faces[i]                                                            
            nx=face.no[0]                                                                         
            ny=face.no[1]                                                                         
            nz=face.no[2]                                                                         
            n_vert=len(face.v)                                                                    
            if n_vert>2:                                                                          
		file.write("facet normal "+str(nx)+" "+str(ny)+" "+str(nz)+"\n")              
		file.write("  outer loop")                                                    
		for j in range(0,3):                                                          
			vert=face.v[j]                                                        
			file.write("\n    vertex")                                            
			for k in range(0,3):                                                  
				file.write(" "+str(vert[k]))                                  
		file.write("\n  endloop\n")                                                   
		file.write("endfacet\n")                                                      
		n_tri=n_tri+1                                                                   
		if n_vert>3:                                                                    
			file.write("facet normal "+str(nx)+" "+str(ny)+" "+str(nz)+"\n")        
			file.write("  outer loop")                                              
			for j in [0,2,3]:                                                       
				vert=face.v[j]                                                  
				file.write("\n    vertex")                                      
				for k in range(0,3):                                            
					file.write(" "+str(vert[k]))                            
			file.write("\n  endloop\n")                                             
			file.write("endfacet\n")                                                
			n_tri=n_tri+1                                                          
        file.write("endsolid\n")                                                                       
        file.close()                                                                                   

        
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.send('BM\n')


        Window.RedrawAll() 
    
    if evt == 5: # if button '1' is pressed, set active object to centre:
        
        #print os.path
        currentscene = Scene.GetCurrent()
        viewWindow = Blender.Window.GetScreenInfo(Window.Types. VIEW3D, rect='total')
        #viewWindow = Blender.Window.GetScreenInfo(-1,VIEW3D, rect='total')
        view = Blender.Window.GetViewVector()
        print view
        if view==view1:
              Blender.Window.QAdd(viewWindow[0].get('id'), Blender.Draw.PAD3 , 7) 
              #print "view3"
        if view==view3:
              Blender.Window.QAdd(viewWindow[0].get('id'), Blender.Draw.PAD7 , 7) 
              #print "view7"
        if view!=view1 and view!=view3:
              Blender.Window.QAdd(viewWindow[0].get('id'), Blender.Draw.PAD1 , 7) 
              #print "view1"
    
        Window.RedrawAll() 

    if evt == 6:
        #object load selector
        if(vMenu.val==1):
            Blender.Load(bracelet)
        elif(vMenu.val==2):
            Blender.Load(vaas)
        elif(vMenu.val==3):
            print("not object found")
        
        obj = Blender.Object.GetSelected() 
        objectname=obj[0].name    
        object = Blender.Object.Get(objectname)

	print "redraw"
	scene  = Scene.GetCurrent()
	Window.RedrawAll() 

    if evt == 7:
        print "Inside object"
        print vMenu.val

    if evt == 8:
        actheight=height.val
        object.size=[float(height.val),float(height.val),float(object.size[2])]
        #object.size=[1.0,1.0,1.0]
        Window.RedrawAll() 
        
			
    if evt == 9:
        print "prueba"
        actlength=length.val
        object.size=[float(object.size[0]),float(object.size[1]),float(length.val)]
        Window.RedrawAll() 

    if evt == 10:
        #toggle conect buttom
        if (cntstatus=="Disconnect"):
            cntstatus="Connect"
            s.close()
            print "Connection closed"
        elif(cntstatus=="Connect"):
            print "Connecting to address: "+HOST+" port:"+str(PORT)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            print "Connection accepted"
            cntstatus="Disconnect"
        Window.RedrawAll() 
            

#delete selected object		
def unlink():
    scns = Scene.Get()
    scn = scns[0] 
    obs = list(scn.objects) 
    scn.objects.unlink(obs[0]) 
    Window.RedrawAll() 
	

#set size of the selected object.
def set_size():
	selection = Blender.Object.GetSelected() 
	print "** Object selected"+str(selection[0]) 
	print "** Actual size"+str(selection[0].getSize())
	
	size=get_data()
	selection[0].setSize(size,size,size)
	
	Blender.Redraw(-1)


#make tetrahedron
def mk_tetrahedron():
	print "somehitng"
	d1 = random.randint(1, 10)
	d2 = random.randint(1, 10)
	d3 = random.randint(1, 10)
		
	vertexes = [[1+d1,1+d1,1+d1,], [-1-d2,-1-d2,1+d2], [-1-d2, 1+d2, -1-d2], [1+d3, -1-d3, -1-d3]]
	faces    = [[2, 1, 0], [0, 1, 3], [1, 2, 3], [0, 2, 3]]

	mesh = Blender.Mesh.New('mesh')
	mesh.verts.extend(vertexes)
	mesh.faces.extend(faces)

	scene  = Scene.GetCurrent()
	object = scene.objects.new(mesh, 'object')
	Redraw()

#cam
def getCamDatablocks( scn ):
	camList = []
	for ob in scn.objects:
		if ob.type == 'Camera':
			camList.append( ob )
	return camList

#main
Blender.Draw.Register(draw,event,button)

thisFrame = Blender.Get( 'curframe' )
scn =  Blender.Scene.GetCurrent()
camList = getCamDatablocks( scn )

scn.objects.camera = camList[0]



