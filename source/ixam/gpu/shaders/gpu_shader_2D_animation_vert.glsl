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
/* We encode alpha check and discard factor together. */
#define doAlphaCheck (alphaDiscard < 0.0)
#define discardFactor abs(alphaDiscard)

#ifndef USE_GPU_SHADER_CREATE_INFO
noperspective out vec2 uvInterp;
flat out vec2 outRectSize;
noperspective out vec4 innerColor;
flat out float radius;
#  ifdef OS_MAC
in float dummy;
#  endif
#endif

vec2 do_widget(void)
{
  outRectSize = rect.yw - rect.xz;
  float mul = widgetType == 1.0f ? 0.3f : 0.2f;
  radius = outRectSize.y * mul;
  float trapezoidOffset = outRectSize.x * 0.17f * (2.0f - widgetType);
  vec2 vertices[8] = vec2[8](
    rect.xz + vec2(trapezoidOffset, 0.0f),
    rect.xw,
    rect.yz + vec2(-trapezoidOffset, 0.0f),
    rect.yw,
    
    vec2(0.0f, 0.0f),
    vec2(0.0f, outRectSize.y),
    vec2(outRectSize.x, 0.0f),
    outRectSize
  );
  
  vec2 pos = vec2(0.0);

  switch(gl_VertexID) {
    case 0: {
      pos = rect.xz + vec2(trapezoidOffset, 0.0f);
      innerColor = colorInner1;
      break;
    }
    case 1: {
      pos = rect.xw;
      innerColor = colorInner2;
      break;
    }
    case 2: {
      pos = rect.yz + vec2(-trapezoidOffset, 0.0f);
      innerColor = colorInner1;
      break;
    }
    case 3: {
      pos = rect.yw;
      innerColor = colorInner2;
      break;
    }
  }

  uvInterp = vertices[gl_VertexID + 4];
  return pos;
}

void main()
{
  vec2 pos = do_widget();
  gl_Position = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);
}