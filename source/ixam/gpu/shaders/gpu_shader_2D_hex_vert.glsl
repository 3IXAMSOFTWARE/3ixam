#ifndef USE_GPU_SHADER_CREATE_INFO
uniform mat4 ModelViewProjectionMatrix;

#  define MAX_PARAM 12
#  ifdef USE_INSTANCE
#    define MAX_INSTANCE 6
uniform vec4 parameters[MAX_PARAM * MAX_INSTANCE];
#  else
uniform vec4 parameters[MAX_PARAM];
#  endif
#endif

/* gl_InstanceID is supposed to be 0 if not drawing instances, but this seems
 * to be violated in some drivers. For example, macOS 10.15.4 and Intel Iris
 * causes T78307 when using gl_InstanceID outside of instance. */
#ifdef USE_INSTANCE
#  define widgetID gl_InstanceID
#else
#  define widgetID 0
#endif

#define recti parameters[widgetID * MAX_PARAM + 0]
#define rect parameters[widgetID * MAX_PARAM + 1]
#define radsi parameters[widgetID * MAX_PARAM + 2].x
#define rads parameters[widgetID * MAX_PARAM + 2].y
#define faci parameters[widgetID * MAX_PARAM + 2].zw
#define roundCorners parameters[widgetID * MAX_PARAM + 3]
#define colorInner1 parameters[widgetID * MAX_PARAM + 4]
#define colorInner2 parameters[widgetID * MAX_PARAM + 5]
#define colorEdge parameters[widgetID * MAX_PARAM + 6]
#define colorEmboss parameters[widgetID * MAX_PARAM + 7]
#define colorTria parameters[widgetID * MAX_PARAM + 8]
#define tria1Center parameters[widgetID * MAX_PARAM + 9].xy
#define tria2Center parameters[widgetID * MAX_PARAM + 9].zw
#define tria1Size parameters[widgetID * MAX_PARAM + 10].x
#define tria2Size parameters[widgetID * MAX_PARAM + 10].y
#define shadeDir parameters[widgetID * MAX_PARAM + 10].z
#define alphaDiscard parameters[widgetID * MAX_PARAM + 10].w
#define triaType parameters[widgetID * MAX_PARAM + 11].x
#define widgetType parameters[widgetID * MAX_PARAM + 11].y
#define selectedTria parameters[widgetID * MAX_PARAM + 11].zw

#ifndef USE_GPU_SHADER_CREATE_INFO
noperspective out vec4 innerColor;
noperspective out vec2 uvInterp;
flat out vec4 borderColor;
flat out vec2 lineWidth;
flat out float radius;
flat out float type;
flat out float thickness;
#  ifdef OS_MAC
in float dummy;
#  endif
#endif


vec2 do_hold_arrow() {

  if(tria1Size == 0.f)
    return vec2(0, 0);
  
  if(widgetType == 1.f) {

    int vidx = max(0, gl_VertexID - 4);

    if(vidx > 2)
      return vec2(0, 0);
  
    vec2 pts[3] = vec2[3](
      vec2(-1, -1),
      vec2(-1, 1),
      vec2(0, 1)
    );

    vec2 rect_size = -vec2(tria1Size);
    vec2 midpoint = tria1Center;
    vec2 pos = midpoint + pts[vidx].xy * rect_size;

    //innerColor = colorInner1;
    lineWidth = .5 / rect_size.yy;
    borderColor = vec4(0);
    innerColor = colorTria * vec4(colorTria.aaa, 1.0);
    thickness = 0.0;

    uvInterp = (pts[vidx] + 1) * .5;
    // (Pos - mins)
    // ------------  = uv[0; 1]
    //  dimensions
    radius = 0.5 * 0.867;
    type = 1.f;

    return pos;
  } else if(widgetType == 4.f || widgetType == 5.f || widgetType == 8.f) {
    int vidx = max(0, gl_VertexID - 4);

    bool tria2 = vidx > 2;

    vec2 rect_size = vec2(-tria1Size);
    vec2 midpoint = tria2 ? tria2Center : tria1Center;

    vec2 pts[6] = vec2[6] (
      vec2(-.75, .5),
      vec2(.75, .5),
      vec2(0, -.5),

      vec2(-.75, -.5),
      vec2(.75, -.5),
      vec2(0, .5)
    );

    float selected = tria2 ? selectedTria.y : selectedTria.x;

    vec2 pos = midpoint + pts[vidx] * rect_size;
    borderColor = vec4(0);
    innerColor = colorTria * vec4(colorTria.aaa, 1.0) + (selected * vec4(0.1, 0.1, 0.1, 0.0));
    uvInterp = vec2(0.f);
    type = 0.f;
    
    // Sometimes, some cringy triangles appears when .x positions dont match together, so just hide them
    int ncor = int(tria2) * int(tria2Center.x != tria1Center.x);
    ncor = 1 - ncor;
    innerColor.a *= ncor;

    return pos; 
  } else if(triaType == 3.f) {
    int vidx = max(0, gl_VertexID - 4);

    bool tria2 = vidx > 2;

    vec2 rect_size = vec2(-tria1Size);
    vec2 midpoint = tria2 ? tria2Center : tria1Center;

    vec2 pts[6] = vec2[6] (
      vec2(-.75, .5),
      vec2(.75, .5),
      vec2(0, -.5),
      vec2(-.75, .5),
      vec2(.75, .5),
      vec2(0, -.5)
    );

    float selected = tria2 ? selectedTria.y : selectedTria.x;

    vec2 pos = midpoint + pts[vidx] * rect_size;
    borderColor = vec4(0);
    innerColor = colorTria * vec4(colorTria.aaa, 1.0) + (selected * vec4(0.1, 0.1, 0.1, 0.0));
    uvInterp = vec2(0.f);
    type = 0.f;

    return pos; 
  }

  return vec2(0);
}

vec2 do_rhomboid(float invert, float scale) {

  if(gl_VertexID > 3)
    return do_hold_arrow();

  vec2 rect_size = (rect.yw - rect.xz) / 2.0;
  vec2 midpoint = rect.xz + rect_size;
  float inversion = invert == 0.f ? 1.f : -1.f;
  vec2 top_scale = vec2(scale, inversion);

  radius = fract(top_scale.x);

  vec2 pts[8] = vec2[8](
    vec2(-1,  -inversion),
    vec2(-1, 1) * top_scale,
    vec2( 1,  inversion),
    vec2( 1, -1) * top_scale,

    vec2(0.0, 0.0),
    vec2(0.0, 1.0),
    vec2(1.0, 1.0),
    vec2(1.0, 0.0)
  );

  innerColor = colorInner1;
  lineWidth = 0.5 / rect_size.xy;
  // thickness = rads;
  thickness = abs(rect.x - recti.x);
  borderColor = colorEdge;

  vec2 pos = midpoint + pts[gl_VertexID].xy * rect_size.xy;

  uvInterp = pts[gl_VertexID + 4];
  type = scale == 1.f ? 4.f : 2.f;

  return pos;
}


vec2 do_triangle(float invert) {

  if(gl_VertexID > 3)
    return vec2(0, 0);

  vec2 rect_size = (rect.yw - rect.xz) / 2.0f;
  vec2 midpoint = rect.xz + rect_size;
  float inversion = invert == 0.f ? 1.f : -1.f;
  float new_scale_x = (1 + 18.6f / 20.0f) * rect_size.y / rect_size.x;
  vec2 top_scale = vec2(new_scale_x, inversion);

  radius = fract(top_scale.x);

  vec2 pts[8] = vec2[8](
    vec2( 0, -1) * top_scale,
    vec2(-1, 1) * top_scale,
    vec2(0, 1) * top_scale,
    vec2( 1, 1) * top_scale,

    vec2(0.5, 1.0),
    vec2(0.0, 0.0),
    vec2(0.5, 0.0),
    vec2(1.0, 0.0)
  );

  innerColor = colorInner1;
  lineWidth = 0.5 / rect_size.yy;
  // thickness = rads;
  thickness = abs(rect.x - recti.x);
  borderColor = colorEdge;

  vec2 pos = midpoint + pts[gl_VertexID].xy * rect_size.xy;

  uvInterp = pts[gl_VertexID + 4];
  type = 3.f;

  return pos;
}

vec2 do_trapezoid(float invert, float scale) {

  if(gl_VertexID > 3)
    return do_hold_arrow();

  vec2 rect_size = (rect.yw - rect.xz) / 2.0;
  vec2 midpoint = rect.xz + rect_size;
  float inversion = invert == 0.f ? 1.f : -1.f;
  // Magic constant 15.6 was calculated from XD metrics
  vec2 top_scale = vec2(1.f + 20.f / rect_size.x, inversion);

  radius = fract(top_scale.x);

  vec2 pts[8] = vec2[8](
    vec2(-1,  -inversion),
    vec2(-1, 1) * top_scale,
    vec2( 1, 1) * top_scale,
    vec2( 1,  -inversion),

    vec2(0.0, 0.0),
    vec2(0.0, 1.0),
    vec2(1.0, 1.0),
    vec2(1.0, 0.0)
  );

  innerColor = colorInner1;
  lineWidth = 0.5 / rect_size.yy;
  // thickness = rads;
  thickness = abs(rect.x - recti.x);
  borderColor = colorEdge;

  vec2 pos = midpoint + pts[gl_VertexID].xy * rect_size.xy;

  uvInterp = pts[gl_VertexID + 4];
  type = 2.f;

  return pos;
}

vec2 do_pro_hex(void) {
  if(gl_VertexID > 9)
    return do_hold_arrow();

  vec2 pts[10] = vec2[10](
    vec2(-1, -1),
    vec2(-1, 1),
    vec2(0, 1),
    vec2(0, -1),

    vec2(0, -1),
    vec2(0, 1),
    vec2(1, 1),

    vec2(0, -1),
    vec2(1, 1),
    vec2(1, -1)
  );

  vec2 rect_size = (rect.yw - rect.xz) / 2.0;
  vec2 midpoint = rect.xz + rect_size;
  vec2 pos = midpoint + pts[gl_VertexID].xy * rect_size.y;

  innerColor = colorInner1;
  lineWidth = .5 / rect_size.yy;
  borderColor = colorEdge;
  // thickness = 0.0;
  thickness = abs(rect.x - recti.x);
  uvInterp = (pts[gl_VertexID] + 1) * .5;
  // (Pos - mins)
  // ------------  = uv[0; 1]
  //  dimensions
  radius = 0.5 * 0.867;
  type = 1.f;

  return pos;
}

vec2 do_hex(void) {

  if(gl_VertexID > 3)
    return do_hold_arrow();

  vec2 pts[4] = vec2[4](
    vec2(-1, -1),
    vec2(-1, 1),
    vec2(1, 1),
    vec2(1, -1)
  );

  vec2 rect_size = (rect.yw - rect.xz) / 2.0;
  vec2 midpoint = rect.xz + rect_size;
  vec2 pos = midpoint + pts[gl_VertexID].xy * rect_size.y;

  innerColor = colorInner1;
  lineWidth = .5 / rect_size.yy;
  borderColor = colorEdge;
  // thickness = 0.0;
  thickness = abs(rect.x - recti.x);
  uvInterp = (pts[gl_VertexID] + 1) * .5;
  // (Pos - mins)
  // ------------  = uv[0; 1]
  //  dimensions
  radius = 0.5 * 0.867;
  type = 1.f;

  return pos;
}


void main()
{
  vec2 pos = vec2(0, 0);
  lineWidth = vec2(0, 0);

  if(widgetType == 1.f) 
    pos = do_hex();
  else if (widgetType == 2.f || widgetType == 3.f)  
    pos = do_trapezoid(widgetType - 2.f, 1.38f);
  else if (widgetType == 4.f || widgetType == 5.f)
    pos = do_rhomboid(widgetType - 4.f, 1.54f);
  else if (widgetType == 6.f || widgetType == 7.f)
    pos = do_triangle(widgetType - 6.f);
  else if (widgetType == 8.f)
    pos = do_rhomboid(0.f, 1.f);
  else if(widgetType == 9.f) {
    pos = do_pro_hex();
    lineWidth *= 2.f;
    type = 5.f;
  }

  gl_Position = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);
}
