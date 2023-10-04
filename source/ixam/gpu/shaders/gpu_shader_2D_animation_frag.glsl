#ifndef USE_GPU_SHADER_CREATE_INFO

noperspective in vec2 uvInterp;
flat in vec2 outRectSize;
noperspective in vec4 innerColor;
flat in float radius;

out vec4 fragColor;
#endif

float roundBox(vec2 pos, vec2 size) 
{
  float r = (pos.y >= 0.0f) ? 0.0f : radius;
  // float r = min(size.x, size.y) * 4.0f;
  return length(max(abs(pos) - size + r, 0.0f)) - r;
}

void main()
{
  vec2 smoothedge = vec2(4.0f, 2.0f);
  vec2 size = outRectSize - smoothedge;
  vec2 pos = uvInterp - size * 0.5f;
  float distance = roundBox(pos - smoothedge * 0.5f, size * 0.5f);
  float alpha = 1.0f - smoothstep(0.0f, 4.0f, distance);
  fragColor = mix(vec4(0.0f, 0.0f, 0.0f, 0.0f), innerColor, alpha);
}
