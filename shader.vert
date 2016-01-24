uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 o_projection;
uniform vec4 u_color;
uniform vec3 u_scale;
uniform int draw_shadow;
uniform sampler2D shadow_map;
attribute vec3 position;
varying vec4 v_color;

mat4 translate(float x, float y, float z)
{
    return mat4(
        vec4(1.0, 0.0, 0.0, 0.0),
        vec4(0.0, 1.0, 0.0, 0.0),
        vec4(0.0, 0.0, 1.0, 0.0),
        vec4(x,   y,   z,   1.0)
    );
}

mat4 look_at(vec3 eye, vec3 center, vec3 up)
{
    vec3 F = center - eye;
    vec3 f = normalize(F);   // front vector
    vec3 UP = normalize(up);
    vec3 S = cross(f,UP);    // side vector
    vec3 s = normalize(S);
    vec3 u = cross(s,f);     // orthonormal up vector

    mat4 M = mat4(
        vec4(s.x, u.x, -f.x, 0.0),
        vec4(s.y, u.y, -f.y, 0.0),
        vec4(s.z, u.z, -f.z, 0.0),
        vec4(0.0, 0.0,  0.0, 1.0)
    );

    return M * translate(-eye.x, -eye.y, -eye.z);
}

void main()
{
    v_color = u_color * vec4(1,0,0,1);
    vec4 pos = vec4(u_scale * position,1.0);
    float visibility = 1.0;
    if (draw_shadow == 1) {
      mat4 s_view = look_at(vec3(0.5, 2, 2), vec3(0, 0, 0), vec3(0, 0, 1));
      mat4 bias =
        mat4(
             vec4(0.5, 0.0, 0.0, 0.0),
             vec4(0.0, 0.5, 0.0, 0.0),
             vec4(0.0, 0.0, 0.5, 0.0),
             vec4(0.5, 0.5, 0.5, 1.0)
             );
      mat4 shadow_mvp = bias * o_projection * s_view;
      vec4 shadow_coord = shadow_mvp * pos;
      if (texture(shadow_map, shadow_coord.xy).z < shadow_coord.z) {
        visibility = 0.5;
      }
    }
    v_color *= visibility;
    gl_Position = projection * view * model * pos;
}
