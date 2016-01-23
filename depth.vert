#version 130
uniform mat4 projection;
attribute vec3 position;

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
  mat4 view = look_at(vec3(0.5, 2, 2), vec3(0, 0, 0), vec3(0, 0, 1));
  gl_Position = projection * view * vec4(position,1.0);
}
