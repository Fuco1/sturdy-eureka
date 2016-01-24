#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
from vispy.gloo import Program, VertexBuffer, IndexBuffer
from vispy.gloo.context import FakeCanvas
from transforms import perspective, translate, rotate, ortho
import ilio

c = FakeCanvas()
vertex = ilio.read('shader.vert')
fragment = ilio.read('shader.frag')


def display():
    gl.glStencilMask(255)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT |
               gl.GL_STENCIL_BUFFER_BIT)

    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo)
    shadowProgram.draw(gl.GL_TRIANGLES, indices)
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    # Filled cube
    # gl.glDisable(gl.GL_BLEND)
    # gl.glEnable(gl.GL_DEPTH_TEST)
    # gl.glEnable(gl.GL_POLYGON_OFFSET_FILL)
    program['u_color'] = 1,1,1,1
    program['u_scale'] = 1,1,1
    program['draw_shadow'] = 1
    program.draw(gl.GL_TRIANGLES, indices)

    gl.glEnable(gl.GL_STENCIL_TEST)
    gl.glStencilFunc(gl.GL_ALWAYS, 1, 255)
    gl.glStencilOp(gl.GL_KEEP, gl.GL_KEEP, gl.GL_REPLACE)
    # gl.glStencilFunc(gl.GL_NEVER, 1, 255)
    # gl.glStencilOp(gl.GL_REPLACE, gl.GL_REPLACE, gl.GL_REPLACE)
    gl.glStencilMask(255)
    gl.glDepthMask(gl.GL_FALSE)
    program2['u_color'] = 1,1,1,1
    program2['u_scale'] = 1,1,1
    program2.draw(gl.GL_TRIANGLE_STRIP)

    gl.glStencilFunc(gl.GL_EQUAL, 1, 255);
    #gl.glStencilOp(gl.GL_KEEP, gl.GL_KEEP, gl.GL_REPLACE)
    gl.glStencilMask(0)
    gl.glDepthMask(gl.GL_TRUE)

    model = np.eye(4, dtype=np.float32)
    translate(model, 0, -2, 0)
    rotate(model, phi, 0,1,0)
    program['model'] = model
    program['u_color'] = 0.5, 0.5, 0.5, 1
    program['u_scale'] = 1,-1,1
    program['draw_shadow'] = 0
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
program['o_projection'] = ortho(-10, 10, -10, 10, -10, 20)
phi, theta = 0,0

program2 = Program(vertex, ilio.read('black.frag'), count=4)
program2['model'] = model
program2['view'] = view
program2["position"] = [[-2,-1, 2],[-2, -1, -2], [2, -1, 2], [2,-1, -2]]

depthv = ilio.read('depth.vert')
depthf = ilio.read('depth.frag')
shadowProgram = Program(depthv, depthf)
# shadowProgram.set_shaders(ilio.read('depth.vert'), ilio.read('depth.frag'))
shadowProgram['projection'] = ortho(-10, 10, -10, 10, -10, 20)
#shadowProgram["position"] = [[-2,-1, 2],[-2, -1, -2], [2, -1, 2], [2,-1, -2]]
shadowProgram.bind(vertices)

fbo = gl.glGenFramebuffers(1)
gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo)
fbt = gl.glGenTextures(1)
gl.glActiveTexture(gl.GL_TEXTURE0)
gl.glBindTexture(gl.GL_TEXTURE_2D, fbt)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_DEPTH_COMPONENT16, 1024, 1024, 0, gl.GL_DEPTH_COMPONENT, gl.GL_FLOAT, None)
gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT, gl.GL_TEXTURE_2D, fbt, 0)
program['shadow_map'] = 0;
gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
#gl.glDrawBuffer(gl.GL_NONE)

# OpenGL initalization
# --------------------------------------
gl.glClearColor(1,1,1,1)
gl.glEnable(gl.GL_DEPTH_TEST)

# Start
# --------------------------------------
glut.glutMainLoop()
