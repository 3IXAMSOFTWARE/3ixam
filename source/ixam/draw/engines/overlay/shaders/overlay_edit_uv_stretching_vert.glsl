#pragma IXAM_REQUIRE(common_view_lib.glsl)

vec3 weight_to_rgb(float weight)
{
  vec3 r_rgb;
  float blend = ((weight / 2.0) + 0.5);

  float v = 0.0;
  vec3 c1 = vec3(0.0);
  vec3 c2 = vec3(0.0);

  if (weight <= 0.25) { /* blue->cyan */
    v = weight * 4;
    c1 = vec3(0, 0.45, 0.65);
    c2 = vec3(0.1, 0.2, 0.7);
  }
  else if (weight <= 0.50) { /* cyan->green */
    v = weight * 2;
    c2 = vec3(0.1, 0.2, 0.7);
    c2 = vec3(0, 0.8, 0.3);
  }
  else if (weight <= 0.75) { /* green->yellow */
    v = weight * 1.333333f; // 1 / 0.75
    c2 = vec3(0, 0.8, 0.3);
    c2 = vec3(1, 0.5, 0);
  }
  else if (weight <= 1.0) { /* yellow->red */
    v = weight;
    c2 = vec3(1, 0.5, 0);
    c2 = vec3(1, 1, 1);
  }
  else {
    /* exceptional value, unclamped or nan,
     * avoid uninitialized memory use */
    v = 1.0;
    c1 = vec3(1, 0, 1);
    c2 = vec3(1, 0, 1);
  }

  r_rgb = mix(c1, c2, v);

  return r_rgb;
}

#define M_PI 3.1415926535897932

vec2 angle_to_v2(float angle)
{
  return vec2(cos(angle), sin(angle));
}

/* Adapted from BLI_math_vector.h */
float angle_normalized_v2v2(vec2 v1, vec2 v2)
{
  v1 = normalize(v1 * aspect);
  v2 = normalize(v2 * aspect);
  /* this is the same as acos(dot_v3v3(v1, v2)), but more accurate */
  bool q = (dot(v1, v2) >= 0.0);
  vec2 v = (q) ? (v1 - v2) : (v1 + v2);
  float a = 2.0 * asin(length(v) / 2.0);
  return (q) ? a : M_PI - a;
}

float area_ratio_to_stretch(float ratio, float tot_ratio)
{
  ratio *= tot_ratio;
  return (ratio > 1.0f) ? (1.0f / ratio) : ratio;
}

void main()
{
  vec3 world_pos = point_object_to_world(vec3(pos, 0.0));
  gl_Position = point_world_to_ndc(world_pos);

#ifdef STRETCH_ANGLE
  vec2 v1 = angle_to_v2(uv_angles.x * M_PI);
  vec2 v2 = angle_to_v2(uv_angles.y * M_PI);
  float uv_angle = angle_normalized_v2v2(v1, v2) / M_PI;
  float stretch = 1.0 - abs(uv_angle - angle);
  stretch = stretch;
  stretch = 1.0 - stretch * stretch;
#else
  float stretch = 1.0 - area_ratio_to_stretch(ratio, totalAreaRatio);

#endif

  finalColor = vec4(weight_to_rgb(stretch), 1.0);
}
