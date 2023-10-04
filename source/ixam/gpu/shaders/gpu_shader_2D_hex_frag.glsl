#ifndef USE_GPU_SHADER_CREATE_INFO
noperspective in vec2 uvInterp;
noperspective in vec4 innerColor;
flat in vec4 borderColor;
flat in vec2 lineWidth;
flat in float radius;
flat in float type;
flat in float thickness;
out vec4 fragColor;
#endif

vec2 compute_trapezoid(vec2 p) {
  vec2 mask;

  float line_width = max(lineWidth.y, 0.0);
  float aa_radius = 0.5 * line_width;

  vec2 translated = p - vec2(0.5, 0.5);
  vec2 dist = (0.5 - abs(translated)) - line_width;

  // Because of lazy rendering, left side of trapezoid is thicker than another.
  // So we need to correct it. Division of fract part by 4 is absolutely magical
  // Like the reason of only 1 side thickening
  float sdf = min(dist.x / (radius - fract(radius) * .25 * float(p.x < .5)), dist.y);

  mask.x = smoothstep(-aa_radius, aa_radius, sdf);
  mask.y = smoothstep(-aa_radius, aa_radius, sdf - thickness * line_width);

  return mask;
}

vec2 compute_pro_hex(vec2 p, float r) {

    vec2 mask;
    float modifier = 1.f;
    
    if(p.y < -0.24f)
      modifier = min(1.0, max(0, 0.6 - p.x) / 0.5);
    else if(p.x > 0)
      modifier = min(1.0, max(0, p.y + 0.5) / 0.6);

    float line_width = max(lineWidth.y * modifier, 0.0);

    const vec2 s = vec2(.5, 0.86602540378);
    float hexHalfWidth= r;

    p = abs(p);

    float sdf = 
      -(max(
        dot(p, s), p.x) - hexHalfWidth);
    float aa_radius = 0.25 * line_width;

    mask.x = smoothstep(-aa_radius, aa_radius, sdf);
    mask.y = smoothstep(-aa_radius, aa_radius, sdf - line_width * thickness);

    return mask;
}

vec2 compute_hex(vec2 p, float r) {

    vec2 mask;
    float line_width = max(lineWidth.y, 0.0);

    const vec2 s = vec2(.5, 0.86602540378);
    float hexHalfWidth= r;

    p = abs(p);

    float sdf = 
      -(max(
        dot(p, s), p.x) - hexHalfWidth);
    float aa_radius = 0.5 * line_width;

    mask.x = smoothstep(-aa_radius, aa_radius, sdf);
    mask.y = smoothstep(-aa_radius, aa_radius, sdf - line_width * thickness);

    return mask;
}

vec2 compute_triangle(vec2 p) {

  vec2 mask;

  p.x += 0.5 * p.y * sign(p.x - 0.5);

  float line_width = max(lineWidth.y, 0.0);
  float aa_radius = 0.5 * line_width;

  vec2 translated = p - vec2(0.5, 0.5);
  vec2 dist = (0.5 - abs(translated)) - line_width;

  float sdf = min(dist.x, dist.y);

  mask.x = smoothstep(-aa_radius, aa_radius, sdf);
  mask.y = smoothstep(-aa_radius, aa_radius, sdf - thickness * line_width);

  return mask;
}

vec2 compute_rect(vec2 p) {
  vec2 mask;
  vec2 line_width = max(lineWidth, 0.0);

  vec2 translated = p - vec2(0.5, 0.5);
  vec2 dist = (0.5 - abs(translated)) - line_width;
  vec2 fill_dist = dist - line_width * thickness;

  float aa_radius = 0.f;

  if(dist.x < dist.y)
    aa_radius = 0.5 * line_width.x;
  else
    aa_radius = 0.5 * line_width.y;

  mask.x = smoothstep(-aa_radius, aa_radius, min(dist.x, dist.y));
  mask.y = smoothstep(-aa_radius, aa_radius, min(fill_dist.x, fill_dist.y));
  return mask;
}

void main() {

  fragColor = borderColor * vec4(borderColor.aaa, 1.0);

  vec2 masks = vec2(0.0, 1.0);
  switch(int(type)) {

    case 1:
      masks = compute_hex(uvInterp - .5, radius);
      break;
    case 2:
      masks = compute_trapezoid(uvInterp);
      break;
    case 3:
      masks = compute_triangle(uvInterp);
      break;
    case 4:
      masks = compute_rect(uvInterp);
      break;
    case 5:
      masks = compute_pro_hex(uvInterp - .5, radius);
      break;
  }

  fragColor *= masks.x;
  fragColor = mix(fragColor, innerColor, masks.y);

  if (fragColor.a > 0.0)
    fragColor.rgb /= fragColor.a;

  fragColor = ixam_srgb_to_framebuffer_space(fragColor);
}
