uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec4 u_color;
uniform vec3 u_scale;
attribute vec3 position;
varying vec4 v_color;
void main()
{
    v_color = u_color * vec4(1,0,0,1);
    gl_Position = projection * view * model * vec4(u_scale * position,1.0);
}
