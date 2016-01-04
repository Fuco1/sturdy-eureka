#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
from vispy.gloo import Program, VertexBuffer, IndexBuffer
from vispy.gloo.context import FakeCanvas
from transforms import perspective, translate, rotate
import ilio

c = FakeCanvas()
vertex = ilio.read('shader.vert')
fragment = ilio.read('shader.frag')


def display():
    gl.glStencilMask(255)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT |
               gl.GL_STENCIL_BUFFER_BIT)

    # Filled cube
    # gl.glDisable(gl.GL_BLEND)
    # gl.glEnable(gl.GL_DEPTH_TEST)
    # gl.glEnable(gl.GL_POLYGON_OFFSET_FILL)
    program['u_color'] = 1,1,1,1
    program['u_scale'] = 1,1,1
    program.draw(gl.GL_TRIANGLES, indices)

    gl.glEnable(gl.GL_STENCIL_TEST)
    gl.glStencilFunc(gl.GL_ALWAYS, 1, 255)
    gl.glStencilOp(gl.GL_KEEP, gl.GL_KEEP, gl.GL_REPLACE)
    gl.glStencilMask(255)
    gl.glDepthMask(gl.GL_FALSE)
    program2['u_color'] = 1,1,1,1
    program2['u_scale'] = 1,1,1
    program2.draw(gl.GL_TRIANGLE_STRIP)

    gl.glStencilFunc(gl.GL_EQUAL, 1, 255);
    gl.glStencilMask(0)
    gl.glDepthMask(gl.GL_TRUE)

    model = np.eye(4, dtype=np.float32)
    translate(model, 0, -2, 0)
    rotate(model, phi, 0,1,0)
    program['model'] = model
    program['u_color'] = 0.5, 0.5, 0.5, 1
    program['u_scale'] = 1,-1,1
    program.draw(gl.GL_TRIANGLES, indices)
    gl.glDisable(gl.GL_STENCIL_TEST)

    # Outlined cube
    # gl.glDisable(gl.GL_POLYGON_OFFSET_FILL)
    # gl.glEnable(gl.GL_BLEND)
    # gl.glDepthMask(gl.GL_FALSE)
    # program['u_color'] = 0,0,0,1
    # program.draw(gl.GL_LINES, outline)
    # gl.glDepthMask(gl.GL_TRUE)

    glut.glutSwapBuffers()

def reshape(width,height):
    gl.glViewport(0, 0, width, height)
    projection = perspective( 45.0, width/float(height), 2.0, 25.0 )
    program2['projection'] = projection
    program['projection'] = projection

def keyboard(key, x, y):
    if key == '\033': sys.exit( )

def timer(fps):
    global theta, phi
    theta += .5
    phi += .5
    model = np.eye(4, dtype=np.float32)
    #rotate(model, theta, 0,0,1)
    rotate(model, phi, 0,1,0)
    program['model'] = model
    program2['model'] = model
    glut.glutTimerFunc(1000/fps, timer, fps)
    glut.glutPostRedisplay()


# Glut init
# --------------------------------------
glut.glutInit(sys.argv)
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
glut.glutCreateWindow('Rotating Cube')
glut.glutReshapeWindow(1280,1024)
glut.glutReshapeFunc(reshape)
glut.glutKeyboardFunc(keyboard )
glut.glutDisplayFunc(display)
glut.glutTimerFunc(1000/60, timer, 60)

# Build cube data
# --------------------------------------
V = np.zeros(8, [("position", np.float32, 3)])
V["position"] = [[ 1, 1, 1], [-1, 1, 1], [-1,-1, 1], [ 1,-1, 1],
                 [ 1,-1,-1], [ 1, 1,-1], [-1, 1,-1], [-1,-1,-1]]

vertices = VertexBuffer(V)

I = [0,1,2, 0,2,3,  0,3,4, 0,4,5,  0,5,6, 0,6,1,
     1,6,7, 1,7,2,  7,4,3, 7,3,2,  4,7,6, 4,6,5]
indices = IndexBuffer(I)

O = [0,1, 1,2, 2,3, 3,0,
     4,7, 7,6, 6,5, 5,4,
     0,5, 1,6, 2,7, 3,4 ]
outline = IndexBuffer(O)

# Build program
# --------------------------------------
program = Program(vertex, fragment)
program.bind(vertices)

# Build view, model, projection & normal
# --------------------------------------
view = np.eye(4,dtype=np.float32)
rotate(view, 20, 1, 0, 0)
translate(view, 0,1 ,-8)
model = np.eye(4,dtype=np.float32)
projection = np.eye(4,dtype=np.float32)
program['model'] = model
program['view'] = view
phi, theta = 0,0

program2 = Program(vertex, ilio.read('black.frag'), count=4)
program2['model'] = model
program2['view'] = view
program2["position"] = [[-2,-1, 2],[-2, -1, -2], [2, -1, 2], [2,-1, -2]]

# OpenGL initalization
# --------------------------------------
gl.glClearColor(1,1,1,1)
gl.glEnable(gl.GL_DEPTH_TEST)

# Start
# --------------------------------------
glut.glutMainLoop()
