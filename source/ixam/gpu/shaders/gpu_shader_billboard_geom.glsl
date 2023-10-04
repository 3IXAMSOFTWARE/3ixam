
/* Clips point to near clip plane before perspective divide. */
vec4 clip_line_point_homogeneous_space(vec4 p, vec4 q)
{
  if (p.z < -p.w) {
    /* Just solves p + (q - p) * A; for A when p.z / p.w = -1.0. */
    float denom = q.z - p.z + q.w - p.w;
    if (denom == 0.0) {
      /* No solution. */
      return p;
    }
    float A = (-p.z - p.w) / denom;
    p = p + (q - p) * A;
  }
  return p;
}

void do_vertex(const int i, vec4 pos, vec2 ofs)
{
  interp.smoothline = (lineWidth + SMOOTH_WIDTH * float(lineSmooth)) * 0.5;
  gl_Position = pos;
  gl_Position.xy += ofs * pos.w;
  EmitVertex();

  interp.smoothline = -(lineWidth + SMOOTH_WIDTH * float(lineSmooth)) * 0.5;
  gl_Position = pos;
  gl_Position.xy -= ofs * pos.w;
  EmitVertex();
}

void main(void)
{
  vec4 p0 = clip_line_point_homogeneous_space(gl_in[0].gl_Position, gl_in[1].gl_Position);
  vec4 p1 = clip_line_point_homogeneous_space(gl_in[1].gl_Position, gl_in[0].gl_Position);
  vec2 e = normalize(((p1.xy / p1.w) - (p0.xy / p0.w)) * viewportSize.xy);

  vec2 ofs = vec2(-e.y, e.x);
  
  ofs /= viewportSize.xy;
  ofs *= lineWidth;

  do_vertex(0, p0, ofs);
  do_vertex(1, p1, ofs);

  EndPrimitive();
}
