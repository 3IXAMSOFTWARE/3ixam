#ifndef USE_GPU_SHADER_CREATE_INFO
uniform mat4 ModelViewProjectionMatrix;
uniform mat3 NormalMatrix;

in vec3 pos;
in vec3 nor;
in vec2 uv;
out vec3 normal;
out vec2 texCoord_interp;
#endif

void main()
{
  normal = normalize(NormalMatrix * nor);
  texCoord_interp = uv;
  gl_Position = ModelViewProjectionMatrix * vec4(pos, 1.0);
}
