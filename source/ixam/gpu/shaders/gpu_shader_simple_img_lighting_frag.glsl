#ifndef USE_GPU_SHADER_CREATE_INFO
#  ifndef USE_INSTANCE_COLOR
uniform vec4 color;
#  endif
uniform vec3 light;
uniform float intensity;

in vec3 normal;
#  ifdef USE_INSTANCE_COLOR
flat in vec4 finalColor;
#    define color finalColor
#  endif
out vec4 fragColor;
#endif

// uniform sampler2D image;

void main()
{
  vec2 dx = dFdx(texCoord_interp);
  vec2 dy = dFdy(texCoord_interp);
  vec2 du = vec2(dx.x, dy.x);
  du -= vec2(float(abs(du.x) > 0.5f), 
    float(abs(du.y) > 0.5f)) * sign(du);
  dx.x = du.x;
  dy.x = du.y;

  fragColor = textureGrad(image, texCoord_interp, dx, dy);

  fragColor.xyz *= clamp(dot(normalize(normal), simple_lighting_data.light)
   + simple_lighting_data.intensity,
  simple_lighting_data.intensity, 1.0);
  fragColor.w *= 0.8f;
}
