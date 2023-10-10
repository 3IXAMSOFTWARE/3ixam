/* SPDX-License-Identifier: GPL-2.0-or-later */


#include <string>

#include "COLLADASWColor.h"
#include "COLLADASWLight.h"

#include "BLI_math.h"

#include "LightExporter.h"
#include "collada_internal.h"

template<class Functor>
void forEachLightObjectInExportSet(Scene *sce, Functor &f, LinkNode *export_set)
{
  LinkNode *node;
  for (node = export_set; node; node = node->next) {
    Object *ob = (Object *)node->link;

    if (ob->type == OB_LAMP && ob->data) {
      f(ob);
    }
  }
}

LightsExporter::LightsExporter(COLLADASW::StreamWriter *sw, BCExportSettings &export_settings)
    : COLLADASW::LibraryLights(sw), export_settings(export_settings)
{
}

void LightsExporter::exportLights(Scene *sce)
{
  openLibrary();

  forEachLightObjectInExportSet(sce, *this, this->export_settings.get_export_set());

  closeLibrary();
}

void LightsExporter::operator()(Object *ob)
{
  Light *la = (Light *)ob->data;
  std::string la_id(get_light_id(ob));
  std::string la_name(id_name(la));
  COLLADASW::Color col(la->r * la->energy, la->g * la->energy, la->b * la->energy);
  float d, constatt, linatt, quadatt;

  d = la->dist;

  constatt = 1.0f;

  if (la->falloff_type == LA_FALLOFF_INVLINEAR) {
    linatt = 1.0f / d;
    quadatt = 0.0f;
  }
  else {
    linatt = 0.0f;
    quadatt = 1.0f / (d * d);
  }

  /* sun */
  if (la->type == LA_SUN) {
    COLLADASW::DirectionalLight cla(mSW, la_id, la_name);
    cla.setColor(col, false, "color");
    cla.setConstantAttenuation(constatt);
    exportIxamProfile(cla, la);
    addLight(cla);
  }

  /* spot */
  else if (la->type == LA_SPOT) {
    COLLADASW::SpotLight cla(mSW, la_id, la_name);
    cla.setColor(col, false, "color");
    cla.setFallOffAngle(RAD2DEGF(la->spotsize), false, "fall_off_angle");
    cla.setFallOffExponent(la->spotblend, false, "fall_off_exponent");
    cla.setConstantAttenuation(constatt);
    cla.setLinearAttenuation(linatt);
    cla.setQuadraticAttenuation(quadatt);
    exportIxamProfile(cla, la);
    addLight(cla);
  }
  /* lamp */
  else if (la->type == LA_LOCAL) {
    COLLADASW::PointLight cla(mSW, la_id, la_name);
    cla.setColor(col, false, "color");
    cla.setConstantAttenuation(constatt);
    cla.setLinearAttenuation(linatt);
    cla.setQuadraticAttenuation(quadatt);
    exportIxamProfile(cla, la);
    addLight(cla);
  }
  /* area light is not supported
   * it will be exported as a local lamp */
  else {
    COLLADASW::PointLight cla(mSW, la_id, la_name);
    cla.setColor(col, false, "color");
    cla.setConstantAttenuation(constatt);
    cla.setLinearAttenuation(linatt);
    cla.setQuadraticAttenuation(quadatt);
    exportIxamProfile(cla, la);
    addLight(cla);
  }
}

bool LightsExporter::exportIxamProfile(COLLADASW::Light &cla, Light *la)
{
  cla.addExtraTechniqueParameter("ixam", "type", la->type);
  cla.addExtraTechniqueParameter("ixam", "flag", la->flag);
  cla.addExtraTechniqueParameter("ixam", "mode", la->mode);
  cla.addExtraTechniqueParameter("ixam", "gamma", la->k, "ixam_gamma");
  cla.addExtraTechniqueParameter("ixam", "red", la->r);
  cla.addExtraTechniqueParameter("ixam", "green", la->g);
  cla.addExtraTechniqueParameter("ixam", "blue", la->b);
  cla.addExtraTechniqueParameter("ixam", "shadow_r", la->shdwr, "ixam_shadow_r");
  cla.addExtraTechniqueParameter("ixam", "shadow_g", la->shdwg, "ixam_shadow_g");
  cla.addExtraTechniqueParameter("ixam", "shadow_b", la->shdwb, "ixam_shadow_b");
  cla.addExtraTechniqueParameter("ixam", "energy", la->energy, "ixam_energy");
  cla.addExtraTechniqueParameter("ixam", "dist", la->dist, "ixam_dist");
  cla.addExtraTechniqueParameter("ixam", "spotsize", RAD2DEGF(la->spotsize));
  cla.addExtraTechniqueParameter("ixam", "spotblend", la->spotblend);
  cla.addExtraTechniqueParameter("ixam", "att1", la->att1);
  cla.addExtraTechniqueParameter("ixam", "att2", la->att2);
  /* \todo figure out how we can have falloff curve supported here */
  cla.addExtraTechniqueParameter("ixam", "falloff_type", la->falloff_type);
  cla.addExtraTechniqueParameter("ixam", "clipsta", la->clipsta);
  cla.addExtraTechniqueParameter("ixam", "clipend", la->clipend);
  cla.addExtraTechniqueParameter("ixam", "bias", la->bias);
  cla.addExtraTechniqueParameter("ixam", "soft", la->soft);
  cla.addExtraTechniqueParameter("ixam", "bufsize", la->bufsize);
  cla.addExtraTechniqueParameter("ixam", "samp", la->samp);
  cla.addExtraTechniqueParameter("ixam", "buffers", la->buffers);
  cla.addExtraTechniqueParameter("ixam", "area_shape", la->area_shape);
  cla.addExtraTechniqueParameter("ixam", "area_size", la->area_size);
  cla.addExtraTechniqueParameter("ixam", "area_sizey", la->area_sizey);
  cla.addExtraTechniqueParameter("ixam", "area_sizez", la->area_sizez);

  return true;
}
