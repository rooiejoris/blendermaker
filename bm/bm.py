# *** Notes ***
# mirar space_view3d_align_tools.py
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
###### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    'name': 'Blender maker',
    'author': 'Miguel Jimenez <miguel.jgz@gmail.com>',
    'version': (0, 1),
    "blender": (2, 5, 8),
    "api": 35622,
    'location': '',
    'description': 'Extension of blender for Open hardware 3D printing.',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'CNC'}

'''
-------------------------------------------------------------------------
Rev 0.1 Blender 2.5 support.
-------------------------------------------------------------------------
'''

import bpy
from bpy import* 
import os,sys
import struct
import mmap
import contextlib
import itertools
import mathutils
from bpy.props import StringProperty, BoolProperty, CollectionProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.props import IntProperty, BoolProperty, FloatVectorProperty
import random

######
# UI #
######

class BMUI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Blender Maker"
    bl_context = "objectmode"

    scaleXval=0
    scaleYval=0
    scaleZval=0
    randomMag=0
    def draw(self, context):
        global scaleXval
        global scaleYval
        global scaleZval
        global randomMag
        #capture
        layout = self.layout
        obj = context.object
        scene = context.scene

        #save file.
        col = layout.column(align=True)
        row = col.row()
        row = layout.row()
        
        col.label(text="STL file", icon='FILE')
        col = layout.column()
        col = layout.column_flow(columns=5,align=True)
        row.operator("export_mesh.stl", text="Save")
        row.operator("import_mesh.stl", text="Load")
        
        box = layout.separator()        
        
        #select view from.
        col = layout.column()
        col.label(text="View from:", icon='MANIPUL')
        col = layout.column_flow(columns=5,align=True)
        col.operator("view3d.viewnumpad",text="X").type='LEFT'
        col.operator("view3d.viewnumpad",text="Y").type='FRONT'
        col.operator("view3d.viewnumpad",text="Z").type='TOP'
                
        #Scale
        col = layout.column(align=True)
        col.label(text="Scale object:", icon='MAN_SCALE')

        row = col.row()
        row.prop( scene, "scaleX" )
        row = col.row()
        row.prop( scene, "scaleY" )
        row = col.row()
        row.prop( scene, "scaleZ" )
        
        box = layout.separator()        
        
        col = layout.column(align=True)
        row = col.row()
        row.label(text="Randomize:", icon='FORCE_TURBULENCE')
        row = col.row()
        row.prop( scene, "randomMagnitude" )
        row = col.row()
        row.operator("object.randomize", text="Randomize")

        scaleXval = bpy.context.scene.scaleX
        scaleYval = bpy.context.scene.scaleY
        scaleZval = bpy.context.scene.scaleZ

        randomMag = bpy.context.scene.randomMagnitude


#############
# Operators #
#############

class AlignOperator(bpy.types.Operator):
    ''''''
    bl_idname = "object.align"
    bl_label = "Align Selected To Active"

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        print("in Align Operator")
        return {'FINISHED'}


class randomizeObject(bpy.types.Operator):
    ''''''
    bl_idname = "object.randomize"
    bl_label = "Randomize selected object"


    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        print("in randomize operator")
        randomize()
        return {'FINISHED'}

# class saveFile(bpy.types.Operator):
#     ''''''
#     bl_idname = "file.save"
#     bl_label = "Save the object in stl file"

#     @classmethod
#     def poll(cls, context):
        
#         return context.active_object != None

#     def execute(self, context):
#         print("In save file operator")    
#         layout = self.layout
#         obj = context.object
#         mesh=bpy.data.scenes[0].objects[obj.name].data
        
#         print()
#         #write_stl("ficherosalva.stl",mesh.faces)
        
#         return {'FINISHED'}


## file exporter ##
class ExportSTL(bpy.types.Operator, ExportHelper):
    '''
    Save STL triangle mesh data from the active object
    '''
    bl_idname = "export_mesh.stl"
    bl_label = "Export STL"

    filename_ext = ".stl"

    ascii = BoolProperty(name="Ascii",
                         description="Save the file in ASCII file format",
                         default=False)
    apply_modifiers = BoolProperty(name="Apply Modifiers",
                                   description="Apply the modifiers "
                                               "before saving",
                                   default=True)

    def execute(self, context):
        from . import stl_utils
        from . import blender_utils
        import itertools

        faces = itertools.chain.from_iterable(
            blender_utils.faces_from_mesh(ob, self.apply_modifiers)
            for ob in context.selected_objects)

        stl_utils.write_stl(self.filepath, faces, self.ascii)

        return {'FINISHED'}


##########
# Events #
##########
def scale_x(self, context):
    print("** in scale x")
    obj = context.object
    obj.scale[0] = scaleXval
    
def scale_y(self, context):
    print("** in scale y")
    obj = context.object
    obj.scale[1] = scaleYval

def scale_z(self, context):
    print("** in scale z")
    obj = context.object
    obj.scale[2] = scaleZval


##############
# Registring #
##############

def register():

    bpy.utils.register_class(AlignOperator)
    bpy.utils.register_class(randomizeObject)
    bpy.utils.register_class(BMUI)
    bpy.utils.register_class(ExportSTL)
    
    scnType = bpy.types.Scene
    scnType.scaleX = bpy.props.FloatProperty( name = "X", 
                                                     default = 0, min = -20, max = 20, 
                                                     description = "Scale object in X axys" ,update=scale_x)
    
    scnType = bpy.types.Scene
    scnType.scaleY = bpy.props.FloatProperty( name = "Y", 
                                                     default = 0, min = -20, max = 20, 
                                                     description = "Scale object in Y axys",update=scale_y)
    
    scnType = bpy.types.Scene
    scnType.scaleZ = bpy.props.FloatProperty( name = "Z", 
                                                     default = 0, min = -20, max = 20, 
                                                     description = "Scale object in Z axys",update=scale_z)
    
    scnType = bpy.types.Scene
    scnType.randomMagnitude = bpy.props.IntProperty( name = "Jump Vertices", 
                                                     default = 0, min = -20, max = 20, 
                                                     description = "Randomize object")


    scale = FloatVectorProperty(name="Scale",
        description="Maximum scale randomization over each axis",
        default=(0.0, 0.0, 0.0), min=-100.0, max=100.0, subtype='TRANSLATION')
    
    pass


def unregister():
    bpy.utils.register_class(AlignOperator)
    bpy.utils.register_class(randomizeObject)
    bpy.utils.register_class(BMUI)
    bpy.utils.register_class(ExportSTL)
    pass


if __name__ == "__main__":
    register()

    
#############
# Functions #
#############

# Writing stl#
def write_stl(filename, faces, ascii=False):
    '''
    Write a stl file from faces,

    filename
       output filename

    faces
       iterable of tuple of 3 vertex, vertex is tuple of 3 coordinates as float

    ascii
       save the file in ascii format (very huge)
    '''
    print("** In write_stl")
    (_ascii_write if ascii else _binary_write)(filename, faces)


def _ascii_write(filename, faces):
    with open(filename, 'w') as data:
        data.write('solid Exported from blender\n')

        for face in faces:
            data.write('''facet normal 0 0 0\nouter loop\n''')
            for vert in face:
                data.write('vertex %f %f %f\n' % vert)
            data.write('endloop\nendfacet\n')

        data.write('endsolid Exported from blender\n')


def _binary_write(filename, faces):
    with open(filename, 'wb') as data:
        # header
        # we write padding at header begginning to avoid to
        # call len(list(faces)) which may be expensive
        data.write(struct.calcsize('<80sI') * b'\0')

        # 3 vertex == 9f
        pack = struct.Struct('<9f').pack
        # pad is to remove normal, we do use them
        pad = b'\0' * struct.calcsize('<3f')

        nb = 0
        for verts in faces:
            # write pad as normal + vertexes + pad as attributes
            data.write(pad + pack(*itertools.chain.from_iterable(verts)))
            data.write(b'\0\0')
            nb += 1

        # header, with correct value now
        data.seek(0)
        data.write(struct.pack('<80sI', b"Exported from blender", nb))


def randomize():
    obj = context.object
    
    mesh = obj.data

    copyverts=mesh.vertices[:]
    covertices=[]

    topz=copyverts[0].co[2]
    bottomz=copyverts[0].co[2]
        
    #find topz and bottomz
    for vertice in copyverts:
            if(vertice.co[2]>topz):
                topz=vertice.co[2]
            elif(vertice.co[2]<bottomz):
                bottomz=vertice.co[2]
                
    print("** The vertices:")
    print("top="+str(topz)+",bottom="+str(bottomz))

        #pass to all the vertices.
    for vertice in copyverts:
            #top and bottom layers.
        if(vertice.co[2]>bottomz and vertice.co[2]<topz):
            verticeact=vertice
            if not(verticeact in covertices):
                covertices.append(vertice)
                randx=random.uniform(-5,5)
                randy=random.uniform(-5,5)
                index=0
                step=randomMag
                for index,verticeref in enumerate(copyverts):
                    if(step == 0):
                        if verticeref.co[0]==verticeact.co[0]:
                            mesh.vertices[index].co[0]= verticeref.co[0]+randx
                            mesh.vertices[index].co[1]= verticeref.co[1]+randy
                        else:
                            print("was already")
                        step=step=randomMag
                    else:
                        print("step salta")
                    step=step-1
