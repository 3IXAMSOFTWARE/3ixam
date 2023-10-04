

#include "StrokeShader.h"

#include "../python/Director.h"

namespace Freestyle {

int StrokeShader::shade(Stroke &ioStroke) const
{
  return Director_BPy_StrokeShader_shade(const_cast<StrokeShader *>(this), ioStroke);
}

} /* namespace Freestyle */
